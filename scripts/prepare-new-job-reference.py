"""Prepare the proven same-race worksheet for one NEW class design.

No model calls or drawn art. Local originals remain private references. Read
NEW-JOB-ART-RUNBOOK.md before using the printed generation request.
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw
from new_job_art_helpers import ROOT, record, checked


def prepare(args):
    out = args.out.resolve()
    if not out.is_relative_to(ROOT/'build/art') or (out/'request.json').exists():
        raise ValueError('Use a fresh output under build/art; preserve previous requests')
    catalog = json.loads((ROOT/'src/art/race-study/approved-class-sprites-v1.json').read_text())
    old = next(c for c in catalog['concepts'] if c['slug']==args.source_class)
    concept = args.concept.resolve()
    if not concept.is_relative_to(ROOT):
        raise ValueError('Copy the concept into this workspace first')
    out.mkdir(parents=True,exist_ok=True)
    board = Image.new('RGBA',(160,96 if args.front else 64),(228,226,220,255))
    references = []
    for col,ref in enumerate(old['references']):
        source = checked({'path':ref['source'],'sha256':ref['sourceSha256']})
        folder = source.parent
        manifest = checked({'path':(folder/'native.json').relative_to(ROOT).as_posix(),'sha256':ref['manifestSha256']})
        native = json.loads(manifest.read_text())
        for row,slot in enumerate([0,1] if args.front else [0]):
            frame = native['slots'][slot]['frames'][1]
            path = folder/(frame['pose']+'-pose.png')
            im = Image.open(path).convert('RGBA')
            bounds = im.getbbox()
            if not bounds or bounds[0]<32 or bounds[1]<28 or bounds[2]>64 or bounds[3]>60:
                raise ValueError('Native reference exceeds fixed crop; use a separately reviewed layout')
            board.alpha_composite(im.crop((32,28,64,60)),(col*32,8+row*48 if args.front else 16))
            references.append({**record(path),'crop':[32,28,64,60],'slot':slot,'manifest':record(manifest)})
    anchor = args.front.resolve() if args.front else checked({'path':old['approvedBase'],'sha256':old['approvedBaseSha256']})
    im = Image.open(anchor).convert('RGBA')
    if im.size != (32,32):
        raise ValueError('Anatomy/front anchor must be an exact 32x32 image')
    board.alpha_composite(im,(128,8 if args.front else 16))
    worksheet = out/'worksheet.png'
    board.resize((1600,960) if args.front else (1280,512),Image.Resampling.NEAREST).save(worksheet)
    rom = ROOT/'roms/clean/FFTA_US_clean.gba'
    offset = 0x419d60+args.palette*32
    data = rom.read_bytes()
    # Same supported USA reference ROM as the existing native extraction tools.
    import hashlib
    if hashlib.sha1(data).hexdigest()!='4ac05441f4de70a4ec3dd932116346c61b8783d9':
        raise ValueError('Wrong clean reference ROM')
    words = [int.from_bytes(data[i:i+2],'little') for i in range(offset,offset+32,2)]
    colors = [tuple(((w>>s)&31)*255//31 for s in (0,5,10)) for w in words]
    swatch = Image.new('RGB',(750,80),(228,226,220));draw=ImageDraw.Draw(swatch)
    for i,color in enumerate(colors[1:]):
        draw.rectangle((i*50,0,i*50+49,55),fill=color);draw.text((i*50+4,62),str(i+1),fill='black')
    palette_path=out/'palette.png';swatch.save(palette_path)
    prompt = (f'Create the NEW {args.label} costume from image 2 in '+
        ('ONLY the empty bottom-right cell of image 1, showing the exact top-right character from the rear. Match the pose and anatomy of the four lower-row references. ' if args.front else
         'ONLY the fifth/rightmost cell of image 1. The fifth character is a previously generated anatomy anchor: preserve facial landmarks and scale, replace its costume completely. ')+
        'Image 1 supplies native race anatomy, face positions, scale, baseline and coarse pixel clusters; its original jobs are references, not costume bases. '+
        'Image 2 supplies the new costume ONLY. Image 3 supplies the ONLY allowed colors. Keep the whole worksheet layout, original reference cells and neutral background. '+
        'Use the exact same logical pixel size as the neighbors, not a detailed illustration. No text, held weapons, effects or tiny subpixel detail. '+
        ('Target 32x32 cell [128,56,160,88] of logical160x96. Keep front/rear equipment on the same anatomical side; no face or front accessories painted on the back.' if args.front else
         'Target 32x32 cell [128,16,160,48] of logical160x64. Keep the eye clear and costume recognizable at native size.'))
    request=dict(schema=1,label=args.label,sourceClass=args.source_class,tool='image_gen.imagegen',model='Tool managed; version not exposed',
        prompt=prompt,references=[record(worksheet),record(concept),record(palette_path)],nativeReferences=references,anatomyAnchor=record(anchor),
        logicalGrid=[160,96] if args.front else [160,64],crop=[128,56,160,88] if args.front else [128,16,160,48],strip=[128,48,160,96] if args.front else [128,0,160,64],
        paletteROM=record(rom),palette=dict(selector=args.palette,offset=offset,words=words),status='prepared-not-generated')
    (out/'request.json').write_text(json.dumps(request,indent=2)+'\n')
    print(out/'request.json')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-class',required=True)
    parser.add_argument('--label',required=True)
    parser.add_argument('--concept',type=Path,required=True)
    parser.add_argument('--front',type=Path)
    parser.add_argument('--palette',type=int,choices=[0,1,2],default=0)
    parser.add_argument('--out',type=Path,required=True)
    prepare(parser.parse_args())
