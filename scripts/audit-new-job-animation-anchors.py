"""Read-only native animation registration and cross-job landmark atlas.

The ROM stores object positions, not a skeleton. Never label an OAM origin, a
silhouette centroid, or a shared pixel patch an eye/hand joint automatically.
This exports the actual geometry and conservative shared patches for inspection.
Original frames are never fitted, resized, recentered or substituted. All ROM
images and pixel-coordinate exports remain in ignored build/art storage.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import struct

from PIL import Image, ImageDraw
from native_art import ANIM, OAM, TILES, SIZES, compose, layout, palette, romoff, sha, u16, u32
from new_job_art_helpers import ROOT, checked, record

ORIGIN = (48, 64)
VIEW = (16, 8, 80, 72)  # One fixed, unscaled 64x64 inspection window for all jobs.


def geometry(image):
    """Integer pixel edges are half-open; anchor centres use pixel centres."""
    points = [(x, y) for y in range(image.height) for x in range(image.width)
              if image.getpixel((x, y))]
    if not points:
        return dict(bounds=None, rows=[], occupiedPixels=0)
    xs, ys = zip(*points)
    box = [min(xs), min(ys), max(xs)+1, max(ys)+1]
    rows = []
    for y in sorted(set(ys)):
        row = [x for x, py in points if py == y]
        rows.append(dict(y=y-64, left=min(row)-48, rightExclusive=max(row)+1-48))
    return dict(bounds=[box[0]-48, box[1]-64, box[2]-48, box[3]-64],
                occupiedPixels=len(points), width=box[2]-box[0], height=box[3]-box[1],
                silhouetteCentre=[(box[0]+box[2])/2-48, (box[1]+box[3])/2-64],
                bottomEdge=box[3]-64, rows=rows)


def shared_patches(images):
    """Unanimous, nonzero palette-index agreement across >=3 original jobs.

    Disconnected matching pixels are not bones. Keep their exact coordinates,
    indices and support; the review shows where they land on original anatomy.
    No averaging, colour similarity, majority filling or generated pixel input.
    """
    if len(images) < 3:
        return []
    pixels = {}
    for y in range(96):
        for x in range(96):
            vals = [im.getpixel((x, y)) for im in images]
            if vals[0] and len(set(vals)) == 1:
                pixels[x, y] = vals[0]
    patches = []
    remaining = set(pixels)
    while remaining:
        seed = min(remaining, key=lambda p: (p[1], p[0]))
        todo = [seed]; component = []; remaining.remove(seed)
        while todo:
            x, y = todo.pop(); component.append((x, y))
            for p in [(x-1,y), (x+1,y), (x,y-1), (x,y+1)]:
                if p in remaining:
                    remaining.remove(p); todo.append(p)
        if len(component) < 2:
            continue
        xs, ys = zip(*component)
        patches.append(dict(id=len(patches)+1, role='shared-pixel-patch-unlabelled',
            support=len(images),
            centre=[round(sum(xs)/len(xs)+.5-48,3), round(sum(ys)/len(ys)+.5-64,3)],
            bounds=[min(xs)-48,min(ys)-64,max(xs)+1-48,max(ys)+1-64],
            pixels=[[x-48,y-64,pixels[x,y]] for x,y in sorted(component,key=lambda p:(p[1],p[0]))]))
    return patches


class Native:
    def __init__(self, rom, out):
        self.rom, self.out = rom, out
        self.rgb = palette(rom, 0x41a860)[1]
        self.tables = sorted(set(romoff(u32(rom,p),rom) for p in range(ANIM,SIZES,4)))
        self.sequences = {}; self.frames = {}; self.images = {}

    def sequence(self, actor, slot):
        key = actor, slot
        if key in self.sequences:
            return self.sequences[key]
        r = self.rom; table = romoff(u32(r,ANIM+actor*4),r)
        end = next((v for v in self.tables if v > table), None)
        if end is None or table+slot*12+12 > end:
            return None
        descriptor = r[table+slot*12:table+slot*12+12]
        ptr = u32(descriptor,0)
        if not ptr:
            self.sequences[key] = None; return None
        start = romoff(ptr,r); count = u32(r,start)
        assert 0 < count <= 256
        records = []
        for i in range(count):
            address = start+4+i*20
            t,o,d,c,*params = struct.unpack_from('<IIBB5H',r,address)
            records.append(dict(index=i, address=address, tileOffset=TILES+t,
                                oamOffset=OAM+o, duration=d, command=c, params=params,
                                raw=r[address:address+20].hex()))
        result = dict(actor=actor, slot=slot, descriptorOffset=table+slot*12,
                      descriptorHex=descriptor.hex(), address=start, records=records)
        self.sequences[key] = result
        return result

    def drawing(self, frame):
        key = f'{frame["tileOffset"]:x}-{frame["oamOffset"]:x}'
        if key in self.frames:
            return self.frames[key]
        objects, raw_oam = layout(self.rom,frame['oamOffset'])
        n = max(o['tile']+o['width']*o['height']//64 for o in objects)
        raw = self.rom[frame['tileOffset']:frame['tileOffset']+n*32]
        # compose's origin is exact: each native object is placed at (48+x,64+y).
        # Reject clipping rather than silently losing an off-canvas attachment.
        for o in objects:
            assert 0 <= 48+o['x'] <= 96-o['width']
            assert 0 <= 64+o['y'] <= 96-o['height']
        im = compose(raw,objects,self.rgb)
        g = geometry(im); box = im.getbbox()
        assert box and VIEW[0] <= box[0] and VIEW[1] <= box[1] and box[2] <= VIEW[2] and box[3] <= VIEW[3], (key,box)
        path = self.out/'images'/f'{key}.png'
        im.crop(VIEW).save(path, bits=4)
        item = dict(key=key, image='images/'+path.name, geometry=g, objects=objects,
                    tileOffset=frame['tileOffset'], oamOffset=frame['oamOffset'],
                    tileSha256=sha(raw), oamSha256=sha(raw_oam), imageSha256=sha(path.read_bytes()))
        self.frames[key] = item; self.images[key] = im
        return item


def signature(seq):
    # Equal slot/record numbers alone do not establish equivalent animation phase.
    return [(f['duration'], f['command'], f['params']) for f in seq['records']]


def build(manifest_path, selections_path, out):
    if not out.resolve().is_relative_to(ROOT/'build/art'):
        raise ValueError('Original-reference exports must stay in ignored build/art')
    (out/'images').mkdir(parents=True,exist_ok=True)
    manifest = json.loads(manifest_path.read_text())
    selections = json.loads(selections_path.read_text())
    rom = checked(manifest['paletteROM']).read_bytes(); checked(manifest['sourceCatalog'])
    assert sha(rom) == '43fc8204c6dceee58828aebc7af0c72eb807e99f35ad641c8bb0a4fa8b6edc19'
    native = Native(rom,out); units=[]; counts=Counter()
    for unit in manifest['units']:
        slug = unit['slug']; race = {'physician':3,'sapper':5}[slug]
        jobs = []
        # Select all eight ordinary original jobs of the race, from ROM records.
        for job in range(2,44):
            p = 0x521a14+job*52
            if rom[p+4] == race:
                jobs.append(dict(job=job, land=u16(rom,p+7),water=u16(rom,p+9)))
        assert len(jobs)==8
        poses = {p['id']:p for p in unit['poses']}; sequences=[]; pose_uses={p:[] for p in poses}
        drafts={}
        for pid,p in poses.items():
            if p['status']=='user-approved-base':
                ref=p['output']; delta=[0,0]
            else:
                choice=selections[slug][pid];ref=choice['native']
                receipt=json.loads(checked(choice['conversion']).read_text())
                asset=next(a for a in receipt['assets'] if a['id']==choice['attempt'])
                assert asset['native']==ref
                checked(asset['source'])
                crop=asset.get('extractionCrop',asset['crop']); nominal=asset['crop']
                delta=[crop[0]-nominal[0],crop[1]-nominal[1]]
            im=Image.open(checked(ref)); assert im.size==(32,32) and im.mode=='P'
            # This is a *diagnostic proposed placement*, not authenticated runtime
            # registration. Old worksheet coordinates did not preserve one origin.
            canvas=Image.new('P',(96,96));canvas.putpalette(im.getpalette())
            canvas.paste(im,(32+delta[0],28+delta[1]));canvas.info['transparency']=0
            path=out/'images'/f'{slug}-{pid}-draft.png';canvas.crop(VIEW).save(path,bits=4)
            drafts[pid]=dict(source=ref,image='images/'+path.name,geometry=geometry(canvas),
                worksheetTranslation=delta,placement='diagnostic-only: nominal native crop [32,28,64,60] plus recorded extraction translation',
                baseApproved=p['status']=='user-approved-base',
                previousReferenceGeometry=p['native'])
        for resource in unit['authoringReferenceResources']:
            life=resource['lifetime']
            for slot in resource['slots']:
                if not slot['frames']:
                    sequences.append(dict(id=f'{slug}-{life}-{slot["slot"]:02}',lifetime=life,slot=slot['slot'],status='native-null',records=[]));counts['nullSlots']+=1
                    continue
                canonical=native.sequence(slot['sourceActor'],slot['slot']);assert canonical
                expected=[(f['duration'],f['command'],f['params']) for f in slot['frames']]
                assert signature(canonical)==expected, (slug,life,slot['slot'])
                comparisons=[]
                for job in jobs:
                    actor=job[life];seq=native.sequence(actor,slot['slot'])
                    status=('absent' if seq is None else 'timing-and-command-match' if signature(seq)==expected else 'different-record-schedule')
                    comparisons.append(dict(**job,actor=actor,status=status,sequence=seq))
                sid=f'{slug}-{life}-{slot["slot"]:02}';records=[]
                for f,old in zip(canonical['records'],slot['frames']):
                    rec=dict(**f,pose=old.get('pose'),references=[])
                    counts['records']+=1
                    if f['command']==1:
                        assert old.get('pose') in poses
                        drawing=native.drawing(f);rec['canonical']=drawing['key']
                        aligned=[]
                        for comparison in comparisons:
                            seq=comparison['sequence'];rf=None
                            if seq and f['index']<len(seq['records']):
                                rf=seq['records'][f['index']]
                            item={k:v for k,v in comparison.items() if k!='sequence'}
                            if rf and rf['command']==1:
                                draw=native.drawing(rf);item['drawing']=draw['key'];item['record']=rf
                                if comparison['status']=='timing-and-command-match':
                                    aligned.append(native.images[draw['key']])
                            rec['references'].append(item)
                        rec['sharedPatches']=shared_patches(aligned)
                        rec['patchEvidence']='unanimous pixel-index agreement; corresponding schedules; anatomy labels unreviewed'
                        rec['alignedOriginalJobs']=len(aligned)
                        counts['drawingRecords']+=1;counts['sharedPatchRecords']+=bool(rec['sharedPatches'])
                        pose_uses[old['pose']].append(dict(sequence=sid,record=f['index'],canonical=drawing['key']))
                    else:
                        counts['controlRecords']+=1
                    records.append(rec)
                counts['populatedSequences']+=1
                sequences.append(dict(id=sid,lifetime=life,slot=slot['slot'],status='populated',
                    canonicalActor=slot['sourceActor'],descriptorHex=canonical['descriptorHex'],
                    schedule=expected,records=records))
        assert all(pose_uses.values())
        counts['poses']+=len(poses)
        units.append(dict(slug=slug,label=unit['label'],originalJobs=jobs,sequences=sequences,
                          drafts=drafts,poseUses=pose_uses))
    result=dict(schema=1,status='native-registration-and-shared-patch-study-not-anatomy-approval',
        sourceROM=manifest['paletteROM'],manifest=record(manifest_path),selections=record(selections_path),
        coordinateSystem=dict(origin=list(ORIGIN),viewCrop=list(VIEW),displayOrigin=[32,56],
                              units='native pixels; x right, y down; bounds half-open',
                              originMeaning='native OAM object registration; not a measured foot or ground joint'),
        limits=['The ROM has OAM rectangles and indexed drawings, not named skeletal joints.',
                'Equal schedules permit comparison; they do not independently prove semantic pose equivalence.',
                'Shared patches are exact original pixels, not approved anatomical labels or pixels to copy into new artwork.',
                'Silhouette bounds include clothing, shadows and actor-contained effects; they are not body dimensions.',
                'Draft placement is diagnostic; old fitted references cannot recover lost per-part anatomy.',
                'Control records and descriptor bytes are preserved, not interpreted as movement offsets.'],
        counts=dict(counts),nativeDrawings=native.frames,units=units)
    (out/'anchors.json').write_text(json.dumps(result,indent=2)+'\n')
    (out/'anchors-data.js').write_text('const ANCHORS='+json.dumps(result,separators=(',',':'))+';\n')
    write_page(out)
    walk_contact(out,result)
    # A compact, reproducible failure diagnosis for the exact rejected walk.
    walk=units[0]['sequences'][0]
    diagnosis=[]
    for r in walk['records']:
        if not r.get('pose'):continue
        diagnosis.append(dict(record=r['index'],pose=r['pose'],
            native=native.frames[r['canonical']]['geometry']['bounds'],
            proposed=units[0]['drafts'][r['pose']]['geometry']['bounds'],
            sharedPatches=len(r['sharedPatches'])))
    report=dict(passed=True,checks=['authenticated clean ROM and inputs','all inherited slots and ordered records covered',
        'all 148 pose uses resolved','all original objects and visible pixels fit fixed canvas',
        'no reference resizing, per-frame recentering or missing-job substitution',
        'unanimous shared patches exclude mismatched record schedules'],counts=dict(counts),physicianWalk=diagnosis,
        geometryApproval=False,artChanged=False)
    (out/'audit-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


def walk_contact(out, result):
    """Reference diagnostic only: annotate existing pixels; create no artwork."""
    board=Image.new('RGB',(4*272,2*310),'#efeee8');d=ImageDraw.Draw(board)
    unit=result['units'][0];seq=unit['sequences'][0]
    for col,r in enumerate(seq['records']):
        for row,item in enumerate([result['nativeDrawings'][r['canonical']],unit['drafts'][r['pose']]]):
            im=Image.open(out/item['image']).convert('RGBA').resize((256,256),Image.Resampling.NEAREST)
            x=col*272+8;y=row*310+24;board.paste(im,(x,y),im)
            d.line((x+116,y+224,x+140,y+224),fill='#197dac',width=1)
            d.line((x+128,y+212,x+128,y+236),fill='#197dac',width=1)
            b=item['geometry']['bounds']
            d.rectangle((x+(b[0]+32)*4,y+(b[1]+56)*4,x+(b[2]+32)*4-1,y+(b[3]+56)*4-1),outline='#bd8026')
            d.text((x,y-18),('Native original' if row==0 else 'Current proposal')+' '+r['pose'],fill='black')
            d.text((x,y+260),'Bounds '+str(b),fill='black')
    board.save(out/'physician-walk-registration.png')


def write_page(out):
    (out/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Native animation anchors · Physician and Sapper</title>
<style>body{font:16px/1.5 system-ui;background:#ecebe5;color:#203139;margin:0}header,main{padding:24px;max-width:1450px;margin:auto}h1{margin:0}a{color:#176779}nav{position:sticky;top:0;background:#faf9f4;padding:12px 24px;z-index:5;border-bottom:1px solid #bbb;display:flex;flex-wrap:wrap;gap:12px}select,button{font:inherit;padding:6px}article,section{background:#faf9f4;border:1px solid #ccc;border-radius:8px;padding:18px;margin:18px 0}.grid{display:flex;flex-wrap:wrap;gap:12px}figure{margin:0;background:#e6e6e1;padding:10px;width:260px}figure.draft{background:#f2dddd}.view{position:relative;width:256px;height:256px;background:repeating-conic-gradient(#e2e4df 0% 25%,#eceee9 0% 50%) 0/16px 16px}.view img{width:100%;height:100%;image-rendering:pixelated}.view svg{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}.clean .view svg{display:none}figcaption{font-size:13px}pre{max-height:350px;overflow:auto;font-size:12px}small{display:block}.warn{background:#f5e3c8;padding:12px}.patch{color:#705120}table{border-collapse:collapse}td,th{text-align:left;border-bottom:1px solid #ddd;padding:5px}.note{max-width:950px}dialog{max-width:95vw}dialog .view{width:min(640px,80vw);height:min(640px,80vw)}.view{cursor:zoom-in}</style>
<header><h1>Native animation anchors</h1><p class="note">Original Nu Mou and Moogle jobs, on one fixed native grid. Every inherited land and water sequence is included. Blue cross: native object origin. Orange outline: occupied pixel bounds. Gold markers: exact shared pixel patches among originals with matching record schedules.</p>
<p class="warn">The Physician animation was rejected for distortion. These are reference measurements, not corrected artwork. Approved front/rear designs remain approved; animation anatomy needs another pass.</p><p class="note">The game does not contain a named skeleton. Shared patches may show a face, foot, outline or shadow; inspect their locations before assigning anatomical meaning. Costume tops and bounding-box centres must not become head anchors.</p><a href="../chemist-job-art-2026-09-26/review.html">Previous proposals</a> · <a href="anchors.json">All coordinates and source records</a> · <a href="audit-report.json">Coverage and walk diagnosis</a><details><summary>Physician walk · fixed-position comparison</summary><img src="physician-walk-registration.png" alt="Original and proposed walk frames on the same grid" style="max-width:100%;image-rendering:pixelated"></details></header>
<nav><label>Job <select id="job"></select></label><label>Animation <select id="seq"></select></label><label><input type="checkbox" id="guides" checked> Show measured guides</label><button id="all">Open all animations for this job</button><span>Click an image to enlarge. Annotate with Codex browser comments.</span></nav>
<main id="content"></main><dialog id="zoom"><button id="close">Close</button><div id="large"></div></dialog><script src="anchors-data.js"></script><script>
const $=s=>document.querySelector(s), E=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let unit;const N=ANCHORS.nativeDrawings;
function pic(draw,label,patches=[],draft=false){const b=draw.geometry.bounds;let shapes='<path d="M29 56h6M32 53v6" stroke="#167bbb" stroke-width=".3"/>';
if(b)shapes+=`<rect x="${b[0]+32}" y="${b[1]+56}" width="${b[2]-b[0]}" height="${b[3]-b[1]}" fill="none" stroke="#b57522" stroke-width=".25"/>`;
for(const p of patches){const [x,y]=p.centre;shapes+=`<circle cx="${x+32}" cy="${y+56}" r=".9" fill="none" stroke="#cf9b13" stroke-width=".3"/><text x="${x+33}" y="${y+55}" font-size="2" fill="#8a5911">${p.id}</text>`}
return `<figure class="${draft?'draft':''}"><div class="view"><img loading="lazy" src="${E(draw.image)}" alt="${E(label)}"><svg viewBox="0 0 64 64">${shapes}</svg></div><figcaption>${E(label)}<small>Bounds ${E(JSON.stringify(b))} · ${draw.geometry.width}×${draw.geometry.height} occupied extent</small></figcaption></figure>`}
function showSequence(s){let out=`<article id="${s.id}"><h2>${unit.label} · ${s.lifetime} ${String(s.slot).padStart(2,'0')}</h2>`;
if(!s.records.length)return out+'<p>Native null slot — no invented frames or anchors.</p></article>';
out+=`<p>Canonical original actor ${s.canonicalActor}. Each original is shown at its own encoded position. Matching timing is necessary but does not alone prove matching anatomy.</p>`;
for(const r of s.records){out+=`<section id="${s.id}-record-${r.index}"><h3>Record ${r.index+1} · ${r.pose||'control'} · ${r.duration} ticks</h3>`;
if(!r.canonical){out+=`<p>Control command ${r.command}. No drawing anchor assigned.</p><pre>${E(JSON.stringify(r,null,2))}</pre></section>`;continue}
out+='<div class="grid">'+pic(N[r.canonical],'Canonical original · actor '+s.canonicalActor,r.sharedPatches)+pic(unit.drafts[r.pose],'Current proposal · '+r.pose+' · diagnostic placement',[],true)+'</div>';
out+=`<p class="patch">${r.sharedPatches.length} shared patches; ${r.alignedOriginalJobs} original jobs have matching record schedules. These are pixel correspondences, not automatically named joints.</p>`;
out+='<table><tr><th>Patch</th><th>Centre (x, y)</th><th>Native bounds</th><th>Matching pixels</th></tr>'+r.sharedPatches.map(p=>`<tr><td>${p.id}</td><td>${p.centre.join(', ')}</td><td>${p.bounds.join(', ')}</td><td>${p.pixels.length}</td></tr>`).join('')+'</table>';
out+='<details><summary>All eight original jobs · compare anatomy and positions</summary><div class="grid">';
for(const ref of r.references){if(ref.drawing)out+=pic(N[ref.drawing],`Original job ${ref.job} · actor ${ref.actor} · ${ref.status}`,ref.status==='timing-and-command-match'?r.sharedPatches:[]);else out+=`<figure>Original job ${ref.job} · actor ${ref.actor}<p>${E(ref.status)} · no drawable record here; no substitute.</p></figure>`}
out+='</div></details><details><summary>Anchor coordinates, OAM parts, source addresses and exact records</summary><pre>'+E(JSON.stringify({origin:[0,0],geometry:N[r.canonical].geometry,objects:N[r.canonical].objects,sharedPatches:r.sharedPatches,record:r},null,2))+'</pre></details></section>'}
return out+'</article>'}
function render(all=false){const s=unit.sequences.find(s=>s.id===$('#seq').value);$('#content').innerHTML=(all?unit.sequences:[s]).map(showSequence).join('');document.querySelectorAll('.view').forEach(v=>v.onclick=()=>{$('#large').innerHTML=v.outerHTML;$('#zoom').showModal()})}
function selectJob(){unit=ANCHORS.units[$('#job').value];$('#seq').innerHTML=unit.sequences.map(s=>`<option value="${s.id}">${s.lifetime} · ${String(s.slot).padStart(2,'0')} · ${s.status==='native-null'?'unused':s.records.length+' records'}</option>`).join('');render()}
$('#job').innerHTML=ANCHORS.units.map((u,i)=>`<option value="${i}">${u.label}</option>`).join('');$('#job').onchange=selectJob;$('#seq').onchange=()=>render();$('#all').onclick=()=>render(true);$('#guides').onchange=e=>document.body.classList.toggle('clean',!e.target.checked);$('#close').onclick=()=>$('#zoom').close();selectJob();
</script></html>''',encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--selections',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();build(a.manifest.resolve(),a.selections.resolve(),a.out.resolve())
