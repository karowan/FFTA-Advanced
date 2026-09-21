"""Adapt approved illustration designs using imagegen and native reference grids.

Code only composes references and technically converts generated art. It does
not draw character pixels. Original and generated sources remain untouched.
"""
import argparse
import json
import runpy
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'build/art/approved-class-sprites-2026-09-19'
MANIFEST = ROOT/'src/art/race-study/approved-class-sprites-v1.json'
H = runpy.run_path(str(ROOT/'scripts/assemble-class-concepts.py'))

def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    approved = json.loads((ROOT/'src/art/race-study/illustrated-class-concepts-v2.json').read_text())
    old = json.loads((ROOT/'src/art/race-study/class-concepts-v1.json').read_text())
    records=[]
    for design,base in zip(approved['concepts'],old['concepts']):
        assert design['slug']==base['slug']
        prompt=(f"Turn the fifth sprite in image 1 into the {design['label']} from image 2. "
                "Image 2 supplies the costume design; image 1 supplies the SAME racial pixel base, "
                "size, pose, slightly elevated camera and simple pixel art. Replace the cook outfit "
                "completely. Keep the entire row and its layout. No held weapon or spell effect.")
        records.append({**{k:base[k] for k in ['job','slug','race','label','references','approvedBase','approvedBaseSha256','template','templateSha256']},
            'prompt':prompt,'illustration':design['output']['path'],
            'illustrationSha256':design['output']['sha256']})
    MANIFEST.write_text(json.dumps(dict(tool='built-in image_gen',model='Tool default; version not exposed',
        settings='Prompt and two local reference image paths; other settings tool-managed.',
        scope='Ten concept-derived neutral base sprite studies. Not an animation set or native integration.',
        concepts=records),indent=2)+'\n')

def assemble(slugs):
    # Reuse the proven grid recovery and exact common-pixel protection unchanged.
    scope=H['assemble'].__globals__
    scope['OUT']=OUT
    scope['MANIFEST']=MANIFEST
    manifest=json.loads(MANIFEST.read_text())
    for record in manifest['concepts']:
        if slugs and record['slug'] not in slugs:
            continue
        for name,hashkey in [('illustration','illustrationSha256'),('template','templateSha256'),('approvedBase','approvedBaseSha256')]:
            assert H['sha'](ROOT/record[name])==record[hashkey]
    H['assemble'](slugs)
    if all((OUT/f"{r['slug']}-locked.png").exists() for r in manifest['concepts']):
        cards=[]
        for r in manifest['concepts']:
            s=r['slug']
            cards.append(f'<article><h2>{r["label"]}</h2><img class="sprite" src="{s}-locked-16x.png"><p>Native 32 × 32: <img width="32" height="32" src="{s}-locked.png"></p><a href="{s}-comparison-8x.png">Compare with original jobs</a> · <a href="{s}-generated.png">Generated source</a> · <a href="{s}-proof.json">Conversion record</a></article>')
        (OUT/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FFTA concept-derived sprites</title><style>body{background:#e4e2dc;color:#252630;font:17px system-ui;margin:30px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px}article{background:#f3f1eb;padding:18px;border-radius:12px}h2{font-size:20px}.sprite{width:256px;height:256px;image-rendering:pixelated}a{color:#35556b}</style><h1>Concept-derived base sprites</h1><p>Ten neutral pose studies, with exact shared native pixels preserved. Animation and in-game integration remain separate stages.</p><main>'+''.join(cards)+'</main></html>',encoding='utf-8')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['prepare','assemble'])
    parser.add_argument('--slugs',nargs='*')
    args=parser.parse_args()
    prepare() if args.action=='prepare' else assemble(args.slugs)
