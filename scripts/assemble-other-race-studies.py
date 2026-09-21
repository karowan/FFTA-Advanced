"""Prepare native reference rows and protect their exact shared pixels.

Imagegen creates costumes. This script only extracts, converts and composites
unchanged reference pixels; it never authors replacement character patterns.
"""
import argparse
import hashlib
import json
from collections import deque
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/art/race-study-2026-09-19/other-races'
CONFIG = ROOT / 'src/art/race-study/other-races-shared-base.json'
RACES = {'bangaa': [11, 13, 14, 16], 'nu-mou': [18, 20, 21, 25],
         'moogle': [35, 34, 37, 39], 'viera': [26, 27, 29, 31]}
BG = (228, 226, 220, 255)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def references(ids):
    cells, evidence = [], []
    for actor in ids:
        folder = ROOT / f'build/art/native-reference/actor-{actor:03}'
        manifest = folder / 'native.json'
        frame = json.loads(manifest.read_text())['slots'][0]['frames'][1]
        path = folder / (frame['pose'] + '-pose.png')
        source = Image.open(path).convert('RGBA')
        box = source.getbbox()
        assert box and box[0] >= 32 and box[1] >= 28 and box[2] <= 64 and box[3] <= 60, (actor, box)
        cells.append(source.crop((32, 28, 64, 60)))
        evidence.append(dict(actor=actor, slot=0, frame=1, pose=frame['pose'],
                             crop=[32, 28, 64, 60], source=str(path.relative_to(ROOT)),
                             sourceSha256=sha(path), manifestSha256=sha(manifest)))
    return cells, evidence

def shared(cells):
    return [(x, y, cells[0].getpixel((x, y))) for y in range(32) for x in range(32)
            if cells[0].getpixel((x, y))[3] == 255
            and len({c.getpixel((x, y)) for c in cells}) == 1]

def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    for race, ids in RACES.items():
        cells, evidence = references(ids)
        board = Image.new('RGBA', (160, 64), BG)
        for i, cell in enumerate(cells + [cells[0]]):
            board.alpha_composite(cell, (i * 32, 16))
        path = OUT / f'{race}-template.png'
        board.resize((1280, 512), Image.Resampling.NEAREST).save(path)
        label = race.replace('-', ' ').title()
        prompt = (f'Turn the fifth sprite into a {label} cook job using the SAME underlying '
                  f'{label} pixel base as the others. Keep the shared face, eyes, anatomy, pose '
                  'and pixel positions unchanged. Change only the job-specific appearance: '
                  'cream rolled sleeves, mustard apron and teal sash, no hat. '
                  'Keep the entire row and its layout.')
        records.append(dict(race=race, references=evidence, commonForegroundPixels=len(shared(cells)),
                            prompt=prompt, template=str(path.relative_to(ROOT)), templateSha256=sha(path)))
    CONFIG.write_text(json.dumps(dict(tool='built-in image_gen', model='tool default; model version not exposed',
        settings='Only prompt and referenced_image_paths supplied; other settings tool-managed.',
        scope='One front-facing neutral pose per race. Shared pixels are exact across the four listed references only.',
        races=records), indent=2) + '\n')
    print(json.dumps([{k: r[k] for k in ['race', 'commonForegroundPixels']} for r in records]))

def clear_background(im):
    """Remove only a connected flat neutral backdrop if output has no alpha."""
    im.putalpha(im.getchannel('A').point(lambda a: 255 if a >= 128 else 0))
    corner = im.getpixel((0, 0))
    if corner[3] == 0:
        return im
    assert max(corner[:3]) - min(corner[:3]) < 30, corner
    todo = deque([(0, 0)])
    seen = set()
    while todo:
        x, y = todo.popleft()
        if not (0 <= x < im.width and 0 <= y < im.height) or (x, y) in seen:
            continue
        seen.add((x, y))
        p = im.getpixel((x, y))
        if max(abs(p[i] - corner[i]) for i in range(3)) > 24:
            continue
        im.putpixel((x, y), (0, 0, 0, 0))
        todo.extend([(x-1,y), (x+1,y), (x,y-1), (x,y+1)])
    return im

def assemble():
    reports = []
    gallery = Image.new('RGBA', (160, 160), BG)
    for row, (race, ids) in enumerate(RACES.items()):
        cells, evidence = references(ids)
        fixed = shared(cells)
        palette = sorted({c.getpixel((x,y))[:3] for c in cells for y in range(32) for x in range(32)
                          if c.getpixel((x,y))[3] == 255})
        assert len(palette) <= 15
        source = OUT / f'{race}-generated.png'
        full = clear_background(Image.open(source).convert('RGBA').resize((160,64),Image.Resampling.NEAREST))
        fifth = full.crop((128,0,160,64))
        bbox = fifth.getbbox()
        assert bbox and bbox[1] >= 16 and bbox[3] <= 48, (race, 'Output moved outside body cell', bbox)
        generated = full.crop((128,16,160,48))
        generated.save(OUT / f'{race}-grid.png')
        converted = Image.new('RGBA',(32,32))
        for y in range(32):
            for x in range(32):
                pixel = generated.getpixel((x,y))
                if pixel[3]:
                    nearest = min(palette,key=lambda c:sum((c[i]-pixel[i])**2 for i in range(3)))
                    converted.putpixel((x,y),(*nearest,255))
        before = sum(converted.getpixel((x,y)) == value for x,y,value in fixed)
        layer = Image.new('RGBA',(32,32))
        for x,y,value in fixed:
            layer.putpixel((x,y),value)
        layer.save(OUT / f'{race}-immutable-layer.png')
        converted.alpha_composite(layer)
        assert all(converted.getpixel((x,y)) == value for x,y,value in fixed)
        assert len(converted.getcolors(1024)) <= 16
        converted.save(OUT / f'{race}-locked.png')
        converted.resize((512,512),Image.Resampling.NEAREST).save(OUT / f'{race}-locked-16x.png')
        board = Image.new('RGBA',(160,40),BG)
        for i,cell in enumerate(cells + [converted]):
            board.alpha_composite(cell,(i*32,4))
        board.save(OUT / f'{race}-comparison-1x.png')
        board.resize((1280,320),Image.Resampling.NEAREST).save(OUT / f'{race}-comparison-8x.png')
        gallery.alpha_composite(board,(0,row*40))
        report = dict(race=race, references=evidence, sourceSha256=sha(source),
                      source=str(source.relative_to(ROOT)), generatedGrid=[160,64], crop=[128,16,160,48],
                      palette=palette, sharedPixels=fixed, commonForegroundPixels=len(fixed),
                      matchingBeforeProtection=before, matchingAfterProtection=len(fixed),
                      scope='Exact common foreground of the four listed native resources, slot 0 frame 1 only.',
                      productionAccepted=False)
        (OUT / f'{race}-proof.json').write_text(json.dumps(report,indent=2)+'\n')
        reports.append({k:report[k] for k in ['race','commonForegroundPixels','matchingBeforeProtection','matchingAfterProtection']})
    gallery.resize((1280,1280),Image.Resampling.NEAREST).save(OUT/'all-races-comparison-8x.png')
    print(json.dumps(reports))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare','assemble'])
    args = parser.parse_args()
    prepare() if args.action == 'prepare' else assemble()
