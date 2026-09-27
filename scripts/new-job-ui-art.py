"""Prepare and convert separate native UI drawings, without touching a ROM.

Portraits and heads get their own fixed grids and authenticated original race
references. Generated sources are immutable. Quantization chooses among existing
native banks; its score is not approval. See NEW-JOB-ART-RUNBOOK.md.
"""
import argparse
import json
import runpy
import shutil
import struct
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from new_job_art_helpers import ROOT, checked, record
from native_portraits import PALETTES
from native_miniatures import decode

BG=(228,226,220,255)


def save_json(path, value):
    path.write_text(json.dumps(value,indent=2)+'\n')


def prepare(base_path, out):
    base=json.loads(base_path.read_text()); rom=checked(base['paletteROM']).read_bytes()
    approval=json.loads(checked(base['approval']).read_text())
    approved={r['path']:r['sha256'] for r in approval['images']}
    if not approval['approved'] or approval['scope']!='native-front-rear-designs-and-colors':
        raise ValueError('Native bases must be explicitly approved')
    if not out.is_relative_to(ROOT/'build/art') or out.exists():
        raise ValueError('Use a fresh build/art UI folder')
    old_path=ROOT/'build/art/native-ui-regeneration-v2-2026-09-20/plan.json'
    old=json.loads(old_path.read_text())
    anchor_path=ROOT/'src/art/native-ui-review/round4/plan.json'
    anchors=json.loads(anchor_path.read_text())
    badge_path=ROOT/'build/art/native-reference/ui/report.json'
    badges=json.loads(badge_path.read_text())
    out.mkdir(parents=True);requests=[]
    for job in base['jobs']:
        slug=job['slug']; source={'physician':'nu-mou-chemist','sapper':'moogle-chemist'}[slug]
        original=next(j for j in old['jobs'] if j['slug']==source)
        contract=next(a for a in anchors['assets'] if a['slug']==source and a['kind']=='icon')['anchors']
        front=record(ROOT/base['outputDirectory']/(job['front']+'-native.png'))
        if approved.get(front['path'])!=front['sha256']:raise ValueError('Changed base')
        folder=out/slug;folder.mkdir()
        design=folder/'approved-native-design.png'
        Image.open(checked(front)).convert('RGBA').resize((512,512),Image.Resampling.NEAREST).save(design)
        for kind in ('portrait','icon'):
            refs=[];palette_options=[]
            if kind=='portrait':
                size=(48,56);grid=(144,112);crop=(96,56,144,112);scale=8
                board=Image.new('RGBA',grid,BG)
                asset=next(a for a in original['assets'] if a['kind']=='portrait')
                for n,ref in enumerate(asset['refs']):
                    picture=Image.open(checked(ref)).convert('RGBA')
                    if picture.size!=size:raise ValueError('Wrong native portrait reference size')
                    board.alpha_composite(picture,((n%2)*48,(n//2)*56));refs.append(ref)
                board.alpha_composite(Image.open(checked(front)).convert('RGBA'),(104,12))
                for choice in original['portraitPalettes']:
                    words=list(struct.unpack('<48H',decode(rom,PALETTES[0],choice['index'])))
                    if words!=choice['words']:raise ValueError('Portrait bank differs from clean ROM')
                    palette_options.append(dict(archive=PALETTES[0],index=choice['index'],words=words))
                prompt=(f'Draw a NEW {job["label"]} menu BUST portrait in ONLY the empty bottom-right 48x56 cell of image 1. '
                    'The four portraits on the left are original FFTA jobs of this race: match their anatomy, coarse pixel clusters, close framing, eye and mouth readability. '
                    'Image 2 is the approved new costume concept, image 3 is its approved native sprite identity, image 4 is an existing native portrait palette guide. '
                    'Design directly for 48x56 logical pixels, full headgear inside the cell and shoulders at its bottom edge. '
                    'Keep the entire 144x112 logical worksheet unchanged, no labels. Use the guide colors with bright highlights and clear dark outlines. '
                    'Do not shrink a full-body illustration. No extra equipment or effects. ')
            else:
                size=(16,14);grid=(80,14);crop=(64,0,80,14);scale=20
                board=Image.new('RGBA',grid,BG)
                for n,ref in enumerate(contract['references']):
                    head=Image.open(checked(ref)).convert('RGBA').crop(tuple(contract['crop']))
                    board.alpha_composite(head,(n*16,0));refs.append(ref)
                # A sparse authenticated face layer fixes facial landmarks;
                # there is no old costume in the new character's target cell.
                layer=Image.open(checked(contract['layer'])).convert('RGBA').resize(size,Image.Resampling.NEAREST)
                board.alpha_composite(layer,(64,0))
                # Native badge banks are class/side choices, not race-wide.
                # Reuse the accepted teal bank and authenticate its location
                # against the original UI inventory, not the first race job.
                badge=next(b for b in badges['records'] if list(struct.unpack_from('<16H',rom,b['paletteOffset']))==original['iconPaletteWords'])
                words=list(struct.unpack_from('<16H',rom,badge['paletteOffset']))
                if words!=original['iconPaletteWords']:raise ValueError('Icon bank differs from clean ROM')
                palette_options=[dict(offset=badge['paletteOffset'],words=words)]
                prompt=(f'Draw a NEW {job["label"]} HEAD icon in ONLY the FIFTH cell of image 1. '
                    'All heads face STRAIGHT TOWARD CAMERA. Keep the exact 16x14 logical pixel layout, common facial pixels, eye row, eye spacing and chin baseline shown in that cell. '
                    'The first four heads are original race anatomy/style references, not costumes to copy. '
                    'Image 2 is the original new costume concept, image 3 is its approved sprite identity, image 4 supplies the ONLY native icon colors. '
                    'Build clear recognizable headgear around the existing face anchors. Coarse simple pixel clusters; no tiny details. '
                    'Keep the full 80x14 logical worksheet and all four original heads unchanged. No body, shoulders, letters or border. ')
            prompt+=('Ivory field-physician cap with dark teal band, long Nu Mou drooping ears and broad gentle muzzle; no pointy wizard hat. '
                     if slug=='physician' else 'Ochre utility cap with dark goggles ABOVE the exposed eyes, cream Moogle face and ears, orange-gold pom-pom; no gun. ')
            template=folder/(kind+'-worksheet.png');board.resize((grid[0]*scale,grid[1]*scale),Image.Resampling.NEAREST).save(template)
            guide=folder/(kind+'-palette-guide.png')
            # All displayed colors come from a single existing bank. Other
            # authenticated choices may be compared after generation.
            choice=palette_options[2 if kind=='portrait' else 0]
            swatches=Image.new('RGB',(480,((len(choice['words'])+15)//16)*30));draw=ImageDraw.Draw(swatches)
            for n,w in enumerate(choice['words']):
                x=(n%16)*30;y=(n//16)*30
                draw.rectangle((x,y,x+29,y+29),fill=tuple(((w>>s)&31)*255//31 for s in (0,5,10)))
            swatches.save(guide)
            request=dict(schema=1,slug=slug,label=job['label'],kind=kind,tool='image_gen.imagegen',model='Tool managed; version not exposed',
                prompt=prompt,references=[record(template),job['concept'],record(design),record(guide)],
                originalReferences=refs,sourcePlans=[record(old_path),record(anchor_path),record(badge_path)],
                paletteROM=base['paletteROM'],paletteChoices=palette_options,nativeSize=size,logicalGrid=grid,crop=crop,
                anchors=contract if kind=='icon' else None,status='prepared-not-generated')
            path=folder/(kind+'-request.json');save_json(path,request);requests.append(record(path))
    save_json(out/'requests.json',dict(baseApproval=base['approval'],requests=requests))
    print(out/'requests.json')


def ingest(request_path, image_path, revision, worksheet_box=None, registration_note=None):
    req=json.loads(request_path.read_text());folder=request_path.parent
    if not folder.is_relative_to(ROOT/'build/art') or not revision.replace('-','').isalnum():raise ValueError('Invalid output')
    for ref in req['references']+req['originalReferences']+req['sourcePlans']:checked(ref)
    rom=checked(req['paletteROM']).read_bytes()
    for choice in req['paletteChoices']:
        words=(list(struct.unpack('<48H',decode(rom,choice['archive'],choice['index']))) if 'archive' in choice
               else list(struct.unpack_from('<16H',rom,choice['offset'])))
        if words!=choice['words']:raise ValueError('Changed native palette')
    stem=folder/(req['kind']+'-'+revision)
    raw=stem.with_name(stem.name+'-generated.png')
    if raw.exists():raise ValueError('Revision exists; preserve it and use a new ID')
    source=Image.open(image_path).convert('RGBA');grid=req['logicalGrid']
    if worksheet_box:
        if not registration_note:raise ValueError('Declared worksheet crop requires inspection explanation')
        left,top,right,bottom=worksheet_box
        if not (0<=left<right<=source.width and 0<=top<bottom<=source.height):raise ValueError('Invalid worksheet crop')
        source=source.crop(tuple(worksheet_box))
    if abs(source.width/source.height-grid[0]/grid[1])>0.02:raise ValueError('Worksheet aspect changed')
    shutil.copy2(image_path,raw)
    clear=runpy.run_path(str(ROOT/'scripts/assemble-other-race-studies.py'))['clear_background']
    sampled=source.resize(tuple(grid),Image.Resampling.NEAREST).crop(tuple(req['crop']))
    # Badge head slots include their native cream background. Flood-clearing
    # that color can also erase a connected ivory ear or muzzle. Portraits
    # need transparency; opaque equipment-head cells deliberately do not.
    if req['kind']=='portrait':sampled=clear(sampled)
    else:sampled.putalpha(sampled.getchannel('A').point(lambda a:255 if a>=128 else 0))
    if sampled.size!=tuple(req['nativeSize']) or not sampled.getbbox():raise ValueError('Empty/wrong native cell')
    sampled_path=stem.with_name(stem.name+'-sampled.png');sampled.save(sampled_path)
    pix=np.array(sampled);mask=pix[:,:,3]>0;options=[]
    for choice in req['paletteChoices']:
        colors=np.array([[((w>>s)&31)*255//31 for s in (0,5,10)] for w in choice['words']])
        distance=((pix[:,:,:3].astype(float)[:,:,None,:]-colors[None,None,1:,:])**2).sum(3)
        indices=(distance.argmin(2)+1).astype('uint8');indices[~mask]=0
        options.append((float(distance.min(2)[mask].mean()),indices,colors,choice))
    error,indices,colors,choice=min(options,key=lambda a:a[0]);anchor_changes=[]
    if req['anchors']:
        contract=req['anchors'];originals=[np.array(Image.open(checked(r)).crop(tuple(contract['crop']))) for r in contract['references']]
        for x,y,index in contract['coordinates']:
            if not all(int(a[y,x])==index for a in originals):raise ValueError('Unauthenticated face anchor')
            if not mask[y,x]:raise ValueError('Face anchor outside generated silhouette; regenerate')
            anchor_changes.append([x,y,int(indices[y,x]),index]);indices[y,x]=index
    native=Image.fromarray(indices);native.putpalette(colors.ravel().tolist()+[0]*(768-colors.size));native.info['transparency']=0
    path=stem.with_name(stem.name+'-native.png');native.save(path)
    native.resize((native.width*8,native.height*8),Image.Resampling.NEAREST).save(stem.with_name(stem.name+'-8x.png'))
    result=dict(request=record(request_path),source=record(raw),sampled=record(sampled_path),native=record(path),palette=choice,
        colorError=error,anchorChanges=anchor_changes,worksheetBox=worksheet_box,registrationNote=registration_note,
        status='proposal-awaiting-visual-review',ROMWritten=False)
    save_json(stem.with_name(stem.name+'-receipt.json'),result);print(path)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare');p.add_argument('--base-plan',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p=sub.add_parser('ingest');p.add_argument('--request',type=Path,required=True);p.add_argument('--image',type=Path,required=True);p.add_argument('--revision',required=True)
    p.add_argument('--worksheet-box',nargs=4,type=int);p.add_argument('--registration-note')
    args=parser.parse_args()
    if args.command=='prepare':prepare(args.base_plan.resolve(),args.out.resolve())
    else:ingest(args.request.resolve(),args.image.resolve(),args.revision,args.worksheet_box,args.registration_note)
