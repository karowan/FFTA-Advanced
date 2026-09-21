"""Calibrate offline color conversion against an approved native base.

This changes color indices only, never draws pixels, changes pose geometry, or
creates palette colors. The source and approved base must share a pixel grid.
The output is an isolated review, not an import or approval of other frames.
"""
import argparse
import html
import importlib.util
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from native_art import ROOT, sha

spec = importlib.util.spec_from_file_location('colorstudy', ROOT/'scripts/study-reviewed-native-color.py')
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)


def fit(source, target):
    rgba = np.asarray(source.convert('RGBA'))
    indices = np.asarray(target)
    overlap = (rgba[:, :, 3] > 0) & (indices > 0)
    # Retain repeated color samples: their native-index frequency is evidence.
    return study.oklab(rgba[:, :, :3][overlap]), indices[overlap]


def convert(source, training, labels, colors, neighbors):
    rgba = np.asarray(source.convert('RGBA'))
    opaque = rgba[:, :, 3] > 0
    queries = study.oklab(rgba[:, :, :3][opaque])
    distances = ((queries[:, None, :] - training[None, :, :])**2).sum(2)
    nearest = np.argsort(distances, axis=1, kind='stable')[:, :neighbors]
    costs = np.take_along_axis(distances, nearest, axis=1)
    weights = 1 / (costs + .0001)
    votes = np.zeros((len(queries), 16))
    for n in range(neighbors):
        votes[np.arange(len(queries)), labels[nearest[:, n]]] += weights[:, n]
    result = np.zeros(opaque.shape, dtype=np.uint8)
    result[opaque] = votes[:, 1:].argmax(1) + 1
    out = Image.fromarray(result).convert('P')
    out.putpalette([v for color in colors for v in color] + [0]*(768-48))
    out.info['transparency'] = 0
    assert np.array_equal(np.asarray(out) != 0, opaque)
    return out, dict(meanReferenceDistance=float(np.sqrt(costs[:, 0]).mean()),
                     maxReferenceDistance=float(np.sqrt(costs[:, 0]).max()))


def board(images, path):
    columns = 11
    canvas = Image.new('RGBA', (columns*128, ((len(images)+columns-1)//columns)*152), '#e4e2dc')
    draw = ImageDraw.Draw(canvas)
    for i, (label, im) in enumerate(images):
        x, y = i % columns * 128, i // columns * 152
        draw.text((x+4, y+2), label, fill='black')
        canvas.alpha_composite(im.convert('RGBA').resize((128,128),Image.Resampling.NEAREST), (x,y+20))
    canvas.save(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--job', type=int, default=117)
    parser.add_argument('--select', type=int, choices=(1,5,9), help='Write selected conversion files for an isolated native import')
    args = parser.parse_args()
    catalog = json.loads((ROOT/'src/art/race-study/full-animation-v1.json').read_text())
    unit = next(u for u in catalog['units'] if u['job']==args.job)
    receipts = json.loads((ROOT/'src/art/race-study/native-color-study-v1.json').read_text())
    approved = [g for g in receipts['generations'] if g.get('status','').startswith('native-base-user-approved')
                and unit['slug'] in g.get('converted','')]
    assert len(approved)==1, 'Requires one explicitly user-approved native base'
    approved = approved[0]
    sourcepath, targetpath = ROOT/unit['front']['path'], ROOT/approved['converted']
    assert sha(sourcepath.read_bytes())==unit['front']['sha256']
    assert sha(targetpath.read_bytes())==approved['convertedSha256']
    source, target = Image.open(sourcepath).convert('RGBA'), Image.open(targetpath)
    assert source.size==target.size==(32,32) and target.mode=='P'
    colors = np.array(target.getpalette()[:48]).reshape(16,3).tolist()
    words = receipts['nativePalettes'][approved['nativePalette']]['words']
    assert colors==[[((w>>s)&31)*255//31 for s in (0,5,10)] for w in words]
    training, labels = fit(source,target)
    out = ROOT/'build/art/native-color-transfer-2026-09-20'/unit['slug']
    out.mkdir(parents=True,exist_ok=True)
    sources, baseline, variants, records = [], [], {k:[] for k in (1,5,9)}, []
    for pose in unit['poses']:
        path = ROOT/pose['output']
        assert sha(path.read_bytes())==pose['outputSha256']
        im = Image.open(path).convert('RGBA')
        sources.append((pose['id'],im))
        rejected,_ = study.convert(im,colors,'rgb555')
        baseline.append((pose['id'],rejected))
        row = dict(pose=pose['id'], source=pose['output'], sourceSha256=pose['outputSha256'], variants={})
        for k in variants:
            folder = out/f'k{k}';folder.mkdir(exist_ok=True)
            converted, metrics = convert(im, training, labels, colors,k)
            dest = folder/(pose['id']+'.png');converted.save(dest,bits=4)
            variants[k].append((pose['id'],converted))
            row['variants'][str(k)] = dict(path=str(dest.relative_to(ROOT)),sha256=sha(dest.read_bytes()),**metrics)
        records.append(row)
    board(sources,out/'source-poses.png');board(baseline,out/'rejected-poses.png')
    for k, images in variants.items():board(images,out/f'transferred-k{k}.png')
    report = dict(status='review-only; not imported',job=args.job,poseCount=len(records),
                  sourceBase=unit['front'], approvedNativeBase=approved['converted'],
                  approvedNativeBaseSha256=approved['convertedSha256'],
                  nativePalette=approved['nativePalette'],nativePaletteWords=words,
                  method='Inverse-distance nearest reference-color voting in Oklab; no spatial rules or new colors',
                  alphaIntersectionPixels=len(training),
                  alphaGridAgreement=float(np.mean((np.array(source)[:,:,3]>0)==(np.array(target)>0))),
                  limitations='Aligned reference colors are not semantic material labels; inspect all poses before import.',
                  records=records)
    if args.select:
        selected=out/'selected';selected.mkdir(exist_ok=True)
        for row in records:
            exact_base=row['sourceSha256']==unit['front']['sha256']
            chosen=targetpath if exact_base else ROOT/row['variants'][str(args.select)]['path']
            dest=selected/(row['pose']+'.png');shutil.copy2(chosen,dest)
            row['selected']=dict(path=str(dest.relative_to(ROOT)),sha256=sha(dest.read_bytes()),
                                 exactApprovedBase=exact_base)
        report['selectedNeighbors']=args.select
        report['importScope']='Isolated Dark Knight conversion pilot, not production acceptance'
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    sections=[]
    for label,name in [('Original approved poses','source-poses.png'),('Rejected direct conversion','rejected-poses.png'),
                       *[(f'Approved-base color transfer, {k} neighbors',f'transferred-k{k}.png') for k in variants]]:
        sections.append(f'<h2>{html.escape(label)}</h2><img src="{name}">')
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Dark Knight animation color study</title>'
        '<style>body{font:16px system-ui;background:#e4e2dc;margin:24px}img{max-width:100%;image-rendering:pixelated}</style>'
        '<h1>Dark Knight animation colors</h1><p>All existing poses, identical silhouettes. Offline conversion into unchanged native colors. Review only.</p>'
        +''.join(sections),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))


if __name__=='__main__':main()
