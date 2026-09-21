"""Imagegen class-concept workbenches and exact native-layer assembly.

All character design pixels come from imagegen or unchanged native references.
Code performs only extraction, palette conversion, compositing and validation.
"""
import argparse
import json
import runpy
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'build/art/race-study-2026-09-19'
OUT = ROOT / 'build/art/class-concepts-2026-09-19'
MANIFEST = ROOT / 'src/art/race-study/class-concepts-v1.json'
HELPERS = runpy.run_path(str(ROOT / 'scripts/assemble-other-race-studies.py'))
RACES = {'human': [0,2,5,7], **HELPERS['RACES']}
BG = HELPERS['BG']
sha = HELPERS['sha']
CLASSES = [
    (116, 'human-samurai', 'human', 'Human Samurai',
     'red lacquered segmented armor, compact crescent-crested kabuto with the face exposed, dark divided trousers'),
    (117, 'human-dark-knight', 'human', 'Human Dark Knight',
     'dark steel angular armor, an open-faced black brow guard, high collar and a short burgundy tabard'),
    (118, 'bangaa-viking', 'bangaa', 'Bangaa Viking',
     'a cream fur shoulder mantle, broad brown leather belt, teal short cloak and bronze arm guards; exposed head and muzzle'),
    (119, 'bangaa-dark-knight', 'bangaa', 'Bangaa Dark Knight',
     'heavy dark steel segmented armor, low violet head crest, armored neck and burgundy waist cloth; exposed muzzle'),
    (120, 'nu-mou-chemist', 'nu-mou', 'Nu Mou Chemist',
     'a cream apothecary coat, teal work apron, small brass goggles above the eyes and a medicine belt; long ears exposed'),
    (121, 'nu-mou-geomancer', 'nu-mou', 'Nu Mou Geomancer',
     'a moss-green shoulder mantle, ochre earth-patterned robe and a large stone clasp; head and long ears exposed'),
    (122, 'moogle-chemist', 'moogle', 'Moogle Chemist',
     'a short cream work coat, amber leather utility apron, brass goggles on the forehead and a teal medicine satchel; ears and pom-pom exposed'),
    (123, 'moogle-bard', 'moogle', 'Moogle Bard',
     'a small green feathered beret, blue short performance cape, gold clasp and red cravat; ears and pom-pom exposed'),
    (124, 'viera-dancer', 'viera', 'Viera Dancer',
     'a jeweled headband, blue and cream layered dance dress, gold waist chain and flowing short sash; tall ears exposed'),
    (125, 'viera-mystic-knight', 'viera', 'Viera Mystic Knight',
     'silver fitted armor over a violet split tunic, a slim runic brow guard and teal shoulder mantle; face and tall ears exposed'),
]

def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    for job,slug,race,label,design in CLASSES:
        cells,evidence = HELPERS['references'](RACES[race])
        base = BASE / ('shared-base-v1-locked.png' if race == 'human' else f'other-races/{race}-locked.png')
        board = Image.new('RGBA',(160,64),BG)
        for i,cell in enumerate(cells + [Image.open(base).convert('RGBA')]):
            board.alpha_composite(cell,(i*32,16))
        template = OUT / f'{slug}-template.png'
        board.resize((1280,512),Image.Resampling.NEAREST).save(template)
        prompt = (f'Turn the fifth sprite into a {label}: {design}. '
                  'Use the SAME underlying racial pixel base. Keep the shared face, eyes, anatomy, '
                  'pose, camera angle and pixel positions unchanged. Replace the cook costume completely. '
                  'Match the simple pixel art of the other four sprites. No held weapon. Keep the entire row and its layout.')
        records.append(dict(job=job,slug=slug,race=race,label=label,prompt=prompt,
            references=evidence,approvedBase=str(base.relative_to(ROOT)),approvedBaseSha256=sha(base),
            template=str(template.relative_to(ROOT)),templateSha256=sha(template)))
    MANIFEST.write_text(json.dumps(dict(tool='built-in image_gen',model='Tool default; model version not exposed',
        settings='Only prompt and referenced_image_paths supplied. Other settings tool-managed.',
        scope='Ten single-pose class concept studies using user-approved racial bases; not production art or animation.',
        concepts=records),indent=2)+'\n')
    print(json.dumps([dict(slug=r['slug'],prompt=r['prompt']) for r in records]))

def assemble(slugs=None):
    manifest = json.loads(MANIFEST.read_text())
    reports = []
    for record in manifest['concepts']:
        slug,race = record['slug'],record['race']
        if slugs and slug not in slugs:
            continue
        cells,_ = HELPERS['references'](RACES[race])
        fixed = HELPERS['shared'](cells)
        palette = sorted({c.getpixel((x,y))[:3] for c in cells for y in range(32) for x in range(32)
                          if c.getpixel((x,y))[3] == 255})
        assert len(palette) <= 15
        source = OUT / f'{slug}-generated.png'
        full = HELPERS['clear_background'](Image.open(source).convert('RGBA').resize((160,64),Image.Resampling.NEAREST))
        fifth = full.crop((128,0,160,64))
        bbox = fifth.getbbox()
        assert bbox and bbox[1] >= 16 and bbox[3] <= 48, (slug,'Generated sprite moved outside the 32x32 body cell',bbox)
        generated = full.crop((128,16,160,48))
        generated.save(OUT / f'{slug}-grid.png')
        converted = Image.new('RGBA',(32,32))
        for y in range(32):
            for x in range(32):
                p = generated.getpixel((x,y))
                if p[3]:
                    nearest = min(palette,key=lambda c:sum((c[i]-p[i])**2 for i in range(3)))
                    converted.putpixel((x,y),(*nearest,255))
        before = sum(converted.getpixel((x,y))==value for x,y,value in fixed)
        for x,y,value in fixed:
            converted.putpixel((x,y),value)
        assert all(converted.getpixel((x,y))==value for x,y,value in fixed)
        assert len(converted.getcolors(1024)) <= 16
        converted.save(OUT / f'{slug}-locked.png')
        converted.resize((512,512),Image.Resampling.NEAREST).save(OUT/f'{slug}-locked-16x.png')
        board = Image.new('RGBA',(160,40),BG)
        for i,cell in enumerate(cells+[converted]):
            board.alpha_composite(cell,(i*32,4))
        board.resize((1280,320),Image.Resampling.NEAREST).save(OUT/f'{slug}-comparison-8x.png')
        report = dict(slug=slug,sourceSha256=sha(source),assembledSha256=sha(OUT/f'{slug}-locked.png'),
            source=str(source.relative_to(ROOT)),sharedPixels=fixed,commonForegroundPixels=len(fixed),
            matchingBeforeProtection=before,matchingAfterProtection=len(fixed),generatedGrid=[160,64],
            crop=[128,16,160,48],palette=palette,productionAccepted=False)
        (OUT/f'{slug}-proof.json').write_text(json.dumps(report,indent=2)+'\n')
        record['result'] = {k:report[k] for k in ['source','sourceSha256','assembledSha256','commonForegroundPixels','matchingBeforeProtection','matchingAfterProtection']}
        reports.append(dict(slug=slug,shared=len(fixed),before=before,after=len(fixed)))
    MANIFEST.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(reports))
    if all((OUT/f'{c[1]}-locked.png').exists() for c in CLASSES):
        gallery()

def gallery():
    font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
    for suffix in ['locked','grid']:
        board = Image.new('RGBA',(1280,640),BG)
        draw = ImageDraw.Draw(board)
        for i,(_,slug,_,label,_) in enumerate(CLASSES):
            x,y = (i//2)*256,(i%2)*320
            sprite = Image.open(OUT/f'{slug}-{suffix}.png').convert('RGBA')
            board.alpha_composite(sprite.resize((256,256),Image.Resampling.NEAREST),(x,y+24))
            draw.text((x+128,y+298),label,font=font,fill='#242833',anchor='mm')
        board.save(OUT/f'all-ten-{suffix}-concepts.png')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action',choices=['prepare','assemble'])
    parser.add_argument('--slugs',nargs='*')
    args = parser.parse_args()
    prepare() if args.action == 'prepare' else assemble(args.slugs)
