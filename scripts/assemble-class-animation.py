"""Native-reference, one-pose-at-a-time imagegen animation workbench.

Only reference extraction, image layout, technical conversion and previews are
performed here. All new character artwork is authored by imagegen.
"""
import argparse
import hashlib
import html
import json
import runpy
import shutil
from collections import Counter
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/art/approved-class-animation-2026-09-19'
BASE=ROOT/'build/art/approved-class-sprites-2026-09-19'
MANIFEST=ROOT/'src/art/race-study/animation-generation-v1.json'
H=runpy.run_path(str(ROOT/'scripts/assemble-other-race-studies.py'))
RACES={'human':[0,2,5,7],**H['RACES']}
BG=H['BG']

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(m): MANIFEST.write_text(json.dumps(m,indent=2)+'\n')
def read(): return json.loads(MANIFEST.read_text())

def reference(actor,slot,phase):
    folder=ROOT/f'build/art/native-reference/actor-{actor:03}'
    p=folder/'native.json';native=json.loads(p.read_text())
    frame=native['slots'][slot]['frames'][phase]
    source=folder/(frame['pose']+'-pose.png')
    im=Image.open(source).convert('RGBA').crop((32,28,64,60))
    return im,dict(actor=actor,slot=slot,frame=phase,record=frame,source=str(source.relative_to(ROOT)),sha256=sha(source),manifestSha256=sha(p))

def prepare():
    if MANIFEST.exists(): raise SystemExit('Manifest already exists; use templates to resume without resetting provenance.')
    OUT.mkdir(parents=True,exist_ok=True)
    approved=json.loads((ROOT/'src/art/race-study/approved-class-sprites-v1.json').read_text())
    records=[];inventory=[]
    for c in approved['concepts']:
        slug=c['slug'];folder=OUT/slug;folder.mkdir(exist_ok=True)
        source=BASE/(slug+'-grid.png')
        if c.get('selectedRevision'):
            revision=json.loads((ROOT/c['selectedRevision']).read_text());source=ROOT/revision['output']
        target=folder/'front-neutral.png';shutil.copy2(source,target)
        actor=RACES[c['race']][0];native=json.loads((ROOT/f'build/art/native-reference/actor-{actor:03}/native.json').read_text())
        inventory.append(dict(job=c['job'],slug=slug,referenceActor=actor,referenceManifestSha256=sha(ROOT/f'build/art/native-reference/actor-{actor:03}/native.json'),
            scope='Original reference actor slot inventory, not final expansion consumer coverage.',
            slots=[dict(slot=s['slot'],frames=s.get('frames',[]),status='movement-study' if s['slot'] in (0,1) else 'not-authored') for s in native['slots']]))
        unit=dict(job=c['job'],slug=slug,race=c['race'],label=c['label'],baseSource=str(source.relative_to(ROOT)),baseSha256=sha(source),base=str(target.relative_to(ROOT)),poses=[])
        for facing,slot in [('front',0),('back',1)]:
            for phase,name in [(0,'step-a'),(1,'neutral'),(2,'step-b')]:
                if facing=='front' and phase==1:continue
                poseid=f'{facing}-{name}'
                description=('rear three-quarter standing pose, face hidden' if facing=='back' and phase==1 else f'{facing} three-quarter walking step '+('A' if phase==0 else 'B'))
                unit['poses'].append(dict(id=poseid,slot=slot,phase=phase,meaning=description,status='pending',
                    output=str((folder/(poseid+'.png')).relative_to(ROOT)),source=str((folder/(poseid+'-generated.png')).relative_to(ROOT)),
                    template=str((folder/(poseid+'-template.png')).relative_to(ROOT))))
        records.append(unit)
    m=dict(tool='built-in image_gen',model='Tool default; version not exposed',settings='Prompt, native-pose worksheet and isolated costume reference per pose; other settings tool-managed.',
        scope='Front and rear neutral/walk cycles for all ten approved designs. Subsequent actions and native integration remain unfinished.',
        authoring='Individual poses; native command order and durations retained in metadata. Generated source colors kept for design review.',
        units=records,referenceInventory=inventory)
    # Reuse the two prior Samurai pose generations, authenticated against their base.
    pilot=json.loads((ROOT/'src/art/race-study/samurai-pose-pilot.json').read_text())
    samurai=records[0];assert samurai['slug']=='human-samurai' and pilot['baseSha256']==samurai['baseSha256']
    for pose in samurai['poses']:
        if pose['slot']==0:
            old=next(x for x in pilot['poses'] if x['frame']==pose['phase'])
            source=ROOT/old['output']['source'];assert sha(source)==old['output']['sha256']
            shutil.copy2(source,ROOT/pose['source'])
            shutil.copy2(BASE/(old['slug']+'-grid.png'),ROOT/pose['output'])
            pose.update(status='generated',reusedFrom='src/art/race-study/samurai-pose-pilot.json',prompt=old['prompt'],references=old['references'],sourceSha256=sha(source),outputSha256=sha(ROOT/pose['output']))
    save(m);templates()

def templates():
    m=read()
    for u in m['units']:
        for p in u['poses']:
            if p['status'] in ('generated','ready'):continue
            front=ROOT/u['base'];back=OUT/u['slug']/'back-neutral.png'
            if p['slot']==1 and p['phase']!=1 and not back.exists():continue
            anchor=back if p['slot']==1 and p['phase']!=1 else front
            anchor_slot=1 if anchor==back else 0
            board=Image.new('RGBA',(160,96),BG);refs=[]
            for i,actor in enumerate(RACES[u['race']]):
                for y,slot,phase in [(16,anchor_slot,1),(56,p['slot'],p['phase'])]:
                    im,evidence=reference(actor,slot,phase);board.alpha_composite(im,(i*32,y));refs.append(evidence)
            im=Image.open(anchor).convert('RGBA')
            design=anchor.with_name(anchor.stem+'-design-reference-16x.png')
            im.resize((512,512),Image.Resampling.NEAREST).save(design)
            board.alpha_composite(im,(128,16));board.alpha_composite(im,(128,56))
            path=ROOT/p['template'];board.resize((1280,768),Image.Resampling.NEAREST).save(path)
            p.update(templateSha256=sha(path),anchor=str(anchor.relative_to(ROOT)),anchorSha256=sha(anchor),references=refs,
                designReference=str(design.relative_to(ROOT)),designReferenceSha256=sha(design),
                prompt=f"Put the character from image 2 into the bottom-right cell of image 1, in the {p['meaning']} demonstrated by the four bottom-row references. Image 2 is the ONLY costume design. Match the native pose and screen-left facing exactly. Keep the full worksheet layout.",status='ready')
    save(m)
    print(json.dumps([dict(slug=u['slug'],id=p['id'],template=p['template'],prompt=p['prompt']) for u in m['units'] for p in u['poses'] if p['status']=='ready']))

def assemble(slug,poseid):
    m=read();u=next(u for u in m['units'] if u['slug']==slug);p=next(p for p in u['poses'] if p['id']==poseid)
    assert sha(ROOT/p['template'])==p['templateSha256'] and sha(ROOT/p['anchor'])==p['anchorSha256']
    if p.get('designReferenceSha256'):
        assert sha(ROOT/p['designReference'])==p['designReferenceSha256']
    spec=p.get('workbenchSpec',dict(grid=[160,96],crop=[128,56,160,88],strip=[128,48,160,96]))
    source=ROOT/p['source'];full=H['clear_background'](Image.open(source).convert('RGBA').resize(tuple(spec['grid']),Image.Resampling.NEAREST))
    # Check the whole target strip before cropping; never silently trim a moved sprite.
    box=full.crop(tuple(spec['strip'])).getbbox()
    top=spec['crop'][1]-spec['strip'][1];bottom=spec['crop'][3]-spec['strip'][1]
    assert box and box[1]>=top and box[3]<=bottom,('Sprite exceeds target body cell',slug,poseid,box)
    im=full.crop(tuple(spec['crop']))
    if p.get('mechanicalCorrection'):
        correction=p['mechanicalCorrection'];reference=ROOT/correction['source']
        assert correction['operation']=='exact-rgba-region-reuse' and sha(reference)==correction['sourceSha256']
        region=Image.open(reference).convert('RGBA').crop(tuple(correction['sourceBox']))
        im.paste(region,tuple(correction['position']))
    im.save(ROOT/p['output'])
    p.update(status='generated',sourceSha256=sha(source),outputSha256=sha(ROOT/p['output']),conversion=dict(logicalGrid=spec['grid'],crop=spec['crop'],resampling='nearest',palette='Generated colors; final native palette conversion not accepted'))
    save(m);print(json.dumps(dict(slug=slug,pose=poseid,bbox=im.getbbox())))

def save_loop(frames,path,exact_colors=()):
    """Use a shared GIF palette with protected colors encoded at exact indices."""
    if exact_colors:
        counts=Counter(pixel for im in frames for pixel in im.convert('RGB').getdata())
        palette=list(dict.fromkeys(exact_colors))
        assert len(palette)<=256,'Protected colors exceed GIF palette capacity'
        palette+= [color for color,_ in counts.most_common() if color not in palette][:256-len(palette)]
        indices={color:i for i,color in enumerate(palette)}
        for color in counts:
            if color not in indices:
                indices[color]=min(range(len(palette)),key=lambda i:sum((color[c]-palette[i][c])**2 for c in range(3)))
        flat=[v for color in palette for v in color]+[0]*(768-3*len(palette));converted=[]
        for frame in frames:
            im=Image.new('P',frame.size);im.putpalette(flat)
            im.putdata([indices[color] for color in frame.convert('RGB').getdata()]);converted.append(im)
        frames=converted
    frames[0].save(path,save_all=True,append_images=frames[1:],duration=[270,130,270,130],loop=0,disposal=2,optimize=False)


def protected_preview_colors(unit,facing):
    colors=[]
    for pose in unit['poses']:
        if not pose['id'].startswith(facing+'-') or not pose.get('mechanicalCorrection'):continue
        correction=pose['mechanicalCorrection']
        face=Image.open(ROOT/correction['source']).convert('RGBA').crop(tuple(correction['sourceBox']))
        bg=Image.new('RGBA',face.size,BG);bg.alpha_composite(face)
        colors.extend(bg.convert('RGB').getdata())
    return list(dict.fromkeys(colors))


def gallery():
    m=read();font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
    board=Image.new('RGBA',(1152,10*180),BG);draw=ImageDraw.Draw(board);cards=[]
    overview=[Image.new('RGBA',(680,900),BG) for _ in range(4)];overview_colors=[]
    for row,u in enumerate(m['units']):
        folder=OUT/u['slug'];draw.text((8,row*180+4),u['label'],font=font,fill='#252630')
        complete=True
        for col,name in enumerate(['front-step-a','front-neutral','front-step-b','back-step-a','back-neutral','back-step-b']):
            p=folder/(name+'.png')
            if p.exists():board.alpha_composite(Image.open(p).convert('RGBA').resize((128,128),Image.Resampling.NEAREST),(col*192+32,row*180+30))
            else:complete=False
        if not complete:continue
        previews=[]
        for facing in ['front','back']:
            frames=[]
            for name in ['step-a','neutral','step-b','neutral']:
                im=Image.open(folder/(facing+'-'+name+'.png')).convert('RGBA').resize((192,192),Image.Resampling.NEAREST)
                bg=Image.new('RGBA',(192,192),BG);bg.alpha_composite(im);frames.append(bg.convert('RGB'))
            exact_colors=protected_preview_colors(u,facing);overview_colors.extend(exact_colors)
            save_loop(frames,folder/(facing+'-walk.gif'),exact_colors)
            preview=facing+'-walk.gif'
            revisions=[p.get('consistencyRevision',0) for p in u['poses'] if p['id'].startswith(facing+'-')]
            if max(revisions,default=0):
                preview=f'{facing}-walk-consistency-v{max(revisions)}.gif'
                shutil.copy2(folder/(facing+'-walk.gif'),folder/preview)
            previews.append(f'<img src="{u["slug"]}/{preview}" alt="{facing} walking preview">')
            for i,name in enumerate(['step-a','neutral','step-b','neutral']):
                im=Image.open(folder/(facing+'-'+name+'.png')).convert('RGBA').resize((128,128),Image.Resampling.NEAREST)
                x=(row%2)*340+(12 if facing=='front' else 170);y=(row//2)*180+35
                overview[i].alpha_composite(im,(x,y))
        for im in overview:
            ImageDraw.Draw(im).text(((row%2)*340+12,(row//2)*180+4),u['label'],font=font,fill='#252630')
        # One combined atlas with stable front and rear rows.
        sheet=Image.new('RGBA',(96,64))
        for y,facing in enumerate(['front','back']):
            for x,name in enumerate(['step-a','neutral','step-b']):sheet.alpha_composite(Image.open(folder/(facing+'-'+name+'.png')).convert('RGBA'),(x*32,y*32))
        sheet.save(folder/'movement-sheet.png')
        cards.append('<article><h2>'+html.escape(u['label'])+'</h2>'+''.join(previews)+f'<p><a href="{u["slug"]}/movement-sheet.png">Native-size movement sheet</a></p></article>')
    board.save(OUT/'all-unit-movement.png')
    rgb=[im.convert('RGB') for im in overview]
    save_loop(rgb,OUT/'all-unit-walk.gif',overview_colors)
    (OUT/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FFTA movement animation review</title><style>body{background:#e4e2dc;color:#252630;font:17px system-ui;margin:30px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:24px}article{background:#f3f1eb;padding:18px;border-radius:12px}h2{font-size:21px}img{image-rendering:pixelated}a{color:#35556b}</style><h1>Movement animation review</h1><p>Front and rear cycles from individually generated poses. Offline previews use native 16/8/16/8 durations at an assumed 60 ticks per second. These are design reviews, not final palette or in-game acceptance. Other actions remain unfinished.</p><main>'+''.join(cards)+'</main></html>',encoding='utf-8')
    m['coverage']=dict(generatedPoses=sum(p['status']=='generated' for u in m['units'] for p in u['poses']),requiredMovementPoses=50,retainedFrontBases=10,otherActions='not-authored',nativeIntegration=False)
    save(m);print(json.dumps(m['coverage']))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','templates','assemble','gallery']);p.add_argument('--slug');p.add_argument('--pose');a=p.parse_args()
    if a.action=='prepare':prepare()
    elif a.action=='templates':templates()
    elif a.action=='assemble':assemble(a.slug,a.pose)
    else:gallery()
