"""Localized face consistency and helmet width model revisions."""
import json,sys,importlib.util
from PIL import Image
from native_art import ROOT,sha

OUT=ROOT/'build/art/ui-detail-v6-2026-09-20'
PREVIOUS=ROOT/'build/art/ui-detail-v5-2026-09-20'

def rec(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p.read_bytes()))

def prepare():
    OUT.mkdir(exist_ok=True);assert not (OUT/'plan.json').exists()
    source=json.loads((PREVIOUS/'results.json').read_text());assets=[]
    for a in source['assets']:
        if a['kind']!='icon' or a['slug'] not in ('human-samurai','human-dark-knight'):continue
        a={k:v for k,v in a.items() if k not in ('raw','native','sampled','palette','paletteError','anchorProof','tool','model','conversion','registration','worksheetBox','layoutDeviation')}
        f=OUT/a['slug'];f.mkdir(exist_ok=True)
        row=Image.new('RGBA',(80,14));row.alpha_composite(Image.open(ROOT/a['anchors']['referenceStrip']['path']).convert('RGBA').resize((64,14),Image.Resampling.NEAREST),(0,0))
        row.alpha_composite(Image.open(PREVIOUS/a['slug']/'icon-native.png').convert('RGBA'),(64,0))
        target=f/'edit-row.png';row.resize((1600,280),Image.Resampling.NEAREST).save(target)
        refs=[rec(target)]
        if a['slug']=='human-samurai':
            p=f/'previous-face-reference.png';Image.open(ROOT/'build/art/anchor-ui-v4-2026-09-20'/a['slug']/'icon-native.png').convert('RGBA').resize((320,280),Image.Resampling.NEAREST).save(p);refs.append(rec(p))
            prompt='Edit ONLY the fifth red Samurai head in image 1. The right side of his face became a large solid black patch and one eye merges into it. Restore the same clean frontal face as image 2, while retaining the smaller helmet of image 1. Two separate equally shaped black eyes, light cream around both eyes, yellow cheeks and chin evenly balanced left and right. No black patch swallowing the right eye. Keep both eyes in columns 7 and 10, rows 7 and 8 of the 16x14 head cell, counting from zero. Keep the current compact red helmet, gold crest, side guards and costume unchanged. Image 2 is FACE ONLY reference; do not enlarge the helmet to match it.'
        else:
            prompt='Edit ONLY the fifth dark knight head in this row. Widen the HELMET slightly by extending each side outward ONE logical pixel, so its width matches the neighboring original human head icons. Keep the same head height, central alignment, and two gold eyes at columns 7 and 10, rows 7 and 8 of the 16x14 head cell, counting from zero. Do not widen the eye spacing or move the eyes. Front-facing symmetric helmet outline, equal cheek plates and level visor, dark teal-black armor and native gold trim. Blue cloth stays BEHIND the right side of the helmet. Do not compress or horizontally scale the whole head. Keep the gold crest readable.'
        a.update(prompt=prompt+' Preserve the first FOUR reference heads and the full row canvas exactly. Use the same coarse pixel grid and only colors already in the reference icons. Return the entire five-icon row at the same proportions, no text, no border, no extra details.',references=refs,logicalSize=[80,14],crop=[64,0,80,14])
        assets.append(a)
    (OUT/'plan.json').write_text(json.dumps(dict(assets=assets,contracts=source['contracts']),indent=2)+'\n');print('Prepared two focused edits.')

def ingest():
    spec=importlib.util.spec_from_file_location('converter',ROOT/'scripts/revise-ui-art-round4.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.OUT=OUT;m.ingest()

if __name__=='__main__':prepare() if sys.argv[1]=='prepare' else ingest()
