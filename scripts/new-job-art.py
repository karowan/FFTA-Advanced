"""Receipt-driven native base studies. No image generation, ROM writes or approvals.

See NEW-JOB-ART-RUNBOOK.md. This deliberately does not invoke a provider or
guess image geometry. A manifest fixes references, grid, crop and native bank.
"""
import argparse
import hashlib
import html
import json
import runpy
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path):
    return {'path': path.resolve().relative_to(ROOT).as_posix(), 'sha256': sha(path)}


def checked(ref):
    path = (ROOT / ref['path']).resolve()
    if not path.is_relative_to(ROOT) or sha(path) != ref['sha256']:
        raise ValueError(f'Input missing, outside checkout or changed: {ref["path"]}')
    return path


def register(plan_path, request_path, image_path, asset_id):
    if not asset_id or not all(c.isalnum() or c=='-' for c in asset_id):
        raise ValueError('Use an alphanumeric/hyphen asset ID')
    out=plan_path.parent.resolve()
    if not out.is_relative_to(ROOT/'build/art'):
        raise ValueError('Plan must be under build/art')
    request=json.loads(request_path.read_text(encoding='utf-8-sig'))
    checked(request['paletteROM'])
    for ref in request['references']:
        checked(ref)
    plan=json.loads(plan_path.read_text()) if plan_path.exists() else dict(schema=1,
        status='base-study-awaiting-review',outputDirectory=out.relative_to(ROOT).as_posix(),
        paletteROM=request['paletteROM'],palette=request['palette'],assets=[])
    if plan['status']!='base-study-awaiting-review' or plan['palette']!=request['palette'] or plan['paletteROM']!=request['paletteROM']:
        raise ValueError('Do not mix approved plans, native palettes or reference ROMs')
    if any(a['id']==asset_id for a in plan['assets']):
        raise ValueError('Asset ID exists; use a new revision ID')
    out.mkdir(parents=True,exist_ok=True)
    dest=out/(asset_id+'-generated.png')
    if dest.exists():
        raise ValueError('Source destination exists; preserve it')
    with Image.open(image_path) as image:
        image.verify()
    shutil.copy2(image_path,dest)
    plan['assets'].append(dict(id=asset_id,source=record(dest),request=record(request_path),
        references=request['references'],logicalGrid=request['logicalGrid'],crop=request['crop'],strip=request['strip']))
    plan_path.write_text(json.dumps(plan,indent=2)+'\n')
    print(f'Registered {asset_id}; conversion and visual review still required')


def convert(plan_path):
    plan = json.loads(plan_path.read_text(encoding='utf-8-sig'))
    if plan['status'] != 'base-study-awaiting-review':
        raise ValueError('This converter accepts draft base studies only')
    out = (ROOT / plan['outputDirectory']).resolve()
    if not out.is_relative_to(ROOT / 'build/art'):
        raise ValueError('Study output must stay under build/art')
    out.mkdir(parents=True, exist_ok=True)
    clear = runpy.run_path(str(ROOT/'scripts/assemble-other-race-studies.py'))['clear_background']
    rom = checked(plan['paletteROM']).read_bytes()
    palette = plan['palette']
    raw = rom[palette['offset']:palette['offset']+32]
    words = [int.from_bytes(raw[i:i+2], 'little') for i in range(0,32,2)]
    if words != palette['words']:
        raise ValueError('Native palette words changed')
    colors = np.array([[((w >> s) & 31)*255//31 for s in (0,5,10)] for w in words])
    results = []
    for asset in plan['assets']:
        if asset.get('request'):
            checked(asset['request'])
        for ref in asset['references']:
            checked(ref)
        source = checked(asset['source'])
        im = Image.open(source).convert('RGBA')
        grid = asset['logicalGrid']
        if abs(im.width/im.height - grid[0]/grid[1]) > 0.02:
            raise ValueError(f'{asset["id"]}: wrong worksheet aspect; regenerate, do not fit')
        sheet = clear(im.resize(tuple(grid), Image.Resampling.NEAREST))
        # Check the whole target column before cropping: a successful crop
        # cannot establish that no ear/hat/pompom was silently cut off.
        crop=asset.get('extractionCrop',asset['crop'])
        if crop!=asset['crop']:
            registration=asset.get('registration',{})
            if registration.get('sourceSha256')!=asset['source']['sha256'] or not registration.get('reason'):
                raise ValueError('Extraction translation needs source-bound inspection evidence')
            if crop[2]-crop[0]!=32 or crop[3]-crop[1]!=32 or crop[0]!=asset['crop'][0]:
                raise ValueError('Only whole 32px-cell vertical translation is supported')
        x1,y1,x2,y2 = crop
        strip_box = asset.get('strip',[x1,0,x2,grid[1]])
        strip = sheet.crop(tuple(strip_box))
        box = strip.getbbox()
        if not box or box[1]+strip_box[1] < y1 or box[3]+strip_box[1] > y2:
            raise ValueError(f'{asset["id"]}: target crosses crop, bbox={box}')
        cell = sheet.crop(tuple(crop))
        if cell.size != (32,32):
            raise ValueError('Base cell must be exactly 32x32')
        pixels = np.array(cell)
        mask = pixels[:,:,3] > 0
        distances = ((pixels[:,:,:3].astype(float)[:,:,None,:]-colors[None,None,1:,:])**2).sum(3)
        indices = (distances.argmin(2)+1).astype('uint8')
        indices[~mask] = 0
        anchor_proof = None
        if asset.get('sharedFace'):
            # Same bounded technical operation as the accepted class workflow:
            # restore only native facial pixels agreed by ALL recorded race
            # references. Never synthesize an eye pattern or copy a costume.
            contract = asset['sharedFace']
            refs = [np.array(Image.open(checked(ref)).convert('RGBA').crop(tuple(ref['crop']))) for ref in contract['references']]
            if len(refs)<2 or any(ref.shape!=(32,32,4) for ref in refs):
                raise ValueError('Shared face requires multiple authenticated 32x32 reference crops')
            common = (refs[0][:,:,3] == 255)
            for reference in refs[1:]:
                common &= (reference == refs[0]).all(2)
            left,top,right,bottom = contract['region']
            if not (0<=left<right<=32 and 0<=top<bottom<=32):
                raise ValueError('Shared-face region is outside native cell')
            region = np.zeros((32,32),dtype=bool)
            region[top:bottom,left:right] = True
            common &= region
            if not common.any():
                raise ValueError('Shared-face region contains no agreed opaque native pixels')
            coordinates = []
            for y,x in zip(*np.where(common)):
                if not mask[y,x]:
                    raise ValueError(f'{asset["id"]}: face anchor outside generated silhouette; regenerate')
                value = int(((colors[1:]-refs[0][y,x,:3])**2).sum(1).argmin()+1)
                coordinates.append([int(x),int(y),int(indices[y,x]),value])
                indices[y,x] = value
            anchor_proof = {'region':contract['region'],'references':contract['references'],
                'coordinatesBeforeAfter':coordinates,'changedPixels':sum(a!=b for x,y,a,b in coordinates),
                'scope':'Native shared facial pixels only; mapped to the selected original palette. No costume or new painted pixels.'}
        native = Image.fromarray(indices)
        native.putpalette(colors.flatten().tolist()+[0]*(768-48))
        native.info['transparency'] = 0
        sampled_path = out/(asset['id']+'-sampled.png')
        native_path = out/(asset['id']+'-native.png')
        # Fail closed on differing existing results; revisions get new IDs.
        for path, picture in [(sampled_path,cell),(native_path,native)]:
            if path.exists():
                previous = Image.open(path)
                if previous.mode != picture.mode or previous.tobytes() != picture.tobytes() or previous.getpalette() != picture.getpalette():
                    raise ValueError(f'Refusing to overwrite a different study: {path.name}')
            else:
                picture.save(path)
        native.resize((384,384),Image.Resampling.NEAREST).save(out/(asset['id']+'-12x.png'))
        results.append({'id':asset['id'],'source':asset['source'],'sampled':record(sampled_path),
            'native':record(native_path),'logicalGrid':grid,'crop':asset['crop'],
            'extractionCrop':crop,'registration':asset.get('registration'),
            'opaqueBounds':native.convert('RGBA').getbbox(),'opaquePixels':int(mask.sum()),
            'indicesUsed':sorted(int(v) for v in np.unique(indices)),
            'alphaPreserved':bool(np.array_equal(indices!=0,mask)),
            'paletteOffset':palette['offset'],'paletteWords':words,
            'colorErrorMeanSquared':float(distances.min(2)[mask].mean()),
            'sharedFace':anchor_proof,
            'method':'Fixed whole-grid nearest sampling; connected neutral background removal; exact cell extraction; original native palette quantization; optional authenticated common native face preservation. No new drawn pixels or bbox fitting.',
            'status':'converted-awaiting-human-review'})
    report = {'plan':record(plan_path),'assets':results,'ROMWritten':False,'productionApproved':False}
    (out/'conversion.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':'converted-awaiting-human-review','assets':len(results),'report':str(out/'conversion.json')}))


def review(plan_path):
    plan = json.loads(plan_path.read_text(encoding='utf-8-sig'))
    out = (ROOT/plan['outputDirectory']).resolve()
    if not out.is_relative_to(ROOT/'build/art'):
        raise ValueError('Review must stay under build/art')
    report = json.loads((out/'conversion.json').read_text())
    if report['plan'] != record(plan_path):
        raise ValueError('Plan changed; reconvert before building review')
    by_id = {a['id']:a for a in report['assets']}
    base_approved=False
    if plan.get('approval'):
        approval=json.loads(checked(plan['approval']).read_text())
        approved={r['path']:r['sha256'] for r in approval['images']}
        base_approved=approval['approved'] and approval['scope']=='native-front-rear-designs-and-colors'
        for job in plan['jobs']:
            for key in ('front','rear'):
                ref=by_id[job[key]]['native']
                base_approved &= approved.get(ref['path'])==ref['sha256']
        if not base_approved:
            raise ValueError('Approval does not cover the selected native bases')
    def figure(ref, caption, cls='pixel', width=256):
        path = checked(ref)
        if path.parent != out:
            raise ValueError('Review assets must be alongside page')
        return f'<figure><img class="{cls}" src="{html.escape(path.name)}" width="{width}" alt="{html.escape(caption)}"><figcaption>{html.escape(caption)}</figcaption></figure>'
    sections = []
    for job in plan['jobs']:
        front, rear = by_id[job['front']], by_id[job['rear']]
        views = figure(job['concept'],'Concept direction approved; native bases '+('approved' if base_approved else 'awaiting review'),'concept',320)
        for label,asset in [('Front',front),('Rear',rear)]:
            views += figure(asset['native'],label+' · exact native palette 0')
            views += figure(asset['native'],label+' · actual 32×32 size','pixel actual',32)
        stage = ''.join(figure(by_id[k]['native'],k) for k in job['comparisonIDs'])
        stage += figure(front['sampled'],'Sampled front before palette conversion')
        stage += figure(rear['sampled'],'Sampled rear before palette conversion')
        refs = figure(job['frontWorksheet'],'Original race references and anatomy anchor','worksheet',800)
        refs += figure(job['rearWorksheet'],'Front/rear reference worksheet','worksheet',800)
        sections.append(f'<section id="{html.escape(job["slug"])}"><h2>{html.escape(job["label"])}</h2><div class="grid">{views}</div><p>{html.escape(job["note"])}</p><details><summary>Conversion stages and previous attempts</summary><div class="grid">{stage}</div></details><details><summary>Exact reference worksheets</summary>{refs}</details></section>')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Physician and Sapper · native base review</title>
<style>body{font:17px system-ui;color:#20303a;background:#e5e3dd;margin:0}header,main{max-width:1320px;margin:auto;padding:24px}section{background:#faf9f4;padding:24px;margin-bottom:24px;border-radius:12px}.grid{display:flex;flex-wrap:wrap;gap:20px;align-items:center}figure{margin:0;padding:12px;background:#eae9e3;border-radius:8px}figcaption{font-size:14px;max-width:300px;margin-top:8px}.pixel,.worksheet{image-rendering:pixelated;max-width:100%;height:auto}.pixel:not(.actual){cursor:zoom-in}.concept{max-height:360px;object-fit:contain;max-width:100%}details{padding-top:18px}summary{cursor:pointer}.notice{padding:16px;background:#dce8df}dialog{max-width:90vw;border:1px solid #63746c;border-radius:12px}dialog img{image-rendering:pixelated;max-width:80vw;max-height:75vh;object-fit:contain}button{padding:10px;font:inherit}a{color:#215d72}</style>
<header><h1>Physician &amp; Sapper</h1><p>New native-size base studies, using the same reference-row and shared-face approach as the earlier classes.</p><p class="notice">Concept directions approved. Front/rear sprite designs and native colors await your review. These are draft images, not in-game captures. Animations, portraits and badges follow after this base checkpoint.</p><p>Click a sprite to enlarge it. Annotate using Codex browser comments.</p></header><main>'''+''.join(sections)+'''<section><h2>Color and provenance</h2><p>Original battle palette 0, unchanged. In this bank the Sapper's pom-pom and leather use orange/gold; the concept's red is unavailable. Face shading uses the existing pale teal ramp. No new palette or runtime remapping.</p><img class="worksheet" src="palette-0.png" width="800" alt="Native palette 0 swatches"><p><a href="base-plan.json">Input hashes and exact crops</a> · <a href="conversion.json">Conversion and shared-face proof</a> · <a href="generation-receipt.json">Prompts and generation records</a></p></section></main><dialog id="zoom"><button id="close">Close</button><p id="caption"></p><img id="large" alt=""></dialog><script>
const d=document.querySelector('#zoom'),big=document.querySelector('#large');document.querySelectorAll('img.pixel').forEach(im=>{im.tabIndex=0;im.setAttribute('role','button');im.setAttribute('aria-label',im.alt+' — enlarge');const show=()=>{big.src=im.src;big.alt=im.alt;big.width=512;document.querySelector('#caption').textContent=im.alt;d.showModal()};im.onclick=show;im.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();show()}}});document.querySelector('#close').onclick=()=>d.close();</script></html>'''
    if base_approved:
        page=page.replace('Concept directions approved. Front/rear sprite designs and native colors await your review. These are draft images, not in-game captures. Animations, portraits and badges follow after this base checkpoint.',
            'Concept directions and exact front/rear native bases approved. Animation and UI artwork are being developed from these frozen bases. These are artwork previews, not in-game captures.')
    (out/'index.html').write_text(page,encoding='utf-8')
    print(out/'index.html')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['register','convert','review'])
    parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--request',type=Path)
    parser.add_argument('--image',type=Path)
    parser.add_argument('--id')
    args = parser.parse_args()
    if args.action=='register':
        if not all([args.request,args.image,args.id]):
            parser.error('register requires --request, --image and --id')
        register(args.plan.resolve(),args.request.resolve(),args.image.resolve(),args.id)
    else:
        {'convert':convert,'review':review}[args.action](args.plan.resolve())
