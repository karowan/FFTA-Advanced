"""Package untouched imagegen concept illustrations for visual review.

No character artwork is painted or revised. Only review thumbnails, captions,
an HTML gallery, file hashes and source provenance are assembled.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/art/illustrated-class-concepts-2026-09-19'
MANIFEST = ROOT / 'src/art/race-study/illustrated-class-concepts-v1.json'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    manifest = json.loads(MANIFEST.read_text())
    font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',26)
    heading = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',36)
    board = Image.new('RGB',(2500,1700),'white')
    draw = ImageDraw.Draw(board)
    draw.text((40,20),'FFTA expansion — illustrated class concepts',font=heading,fill='#33343c')
    cards = []
    assert len(manifest['concepts']) == 10
    for i,concept in enumerate(manifest['concepts']):
        path = OUT / concept.get('selectedImage', concept['slug']+'.png')
        with Image.open(path) as opened:
            opened.verify()
        im = Image.open(path).convert('RGBA')
        concept['output'] = dict(path=str(path.relative_to(ROOT)),sha256=sha(path),
                                 dimensions=list(im.size),status=concept.get('reviewStatus','First illustrated concept draft, awaiting user review'))
        for revision in concept.get('revisions',[]):
            for ref in revision['references']:
                assert sha(ROOT/ref['path']) == ref['sha256']
        for ref in concept['references']:
            assert sha(ROOT/ref['path']) == ref['sha256']
        thumb = im.copy()
        thumb.thumbnail((470,730),Image.Resampling.LANCZOS)
        x,y = (i//2)*500,80+(i%2)*800
        board.paste(thumb,(x+(500-thumb.width)//2,y+(730-thumb.height)//2),thumb)
        draw.text((x+250,y+754),concept['label'],font=font,fill='#33343c',anchor='mm')
        name=html.escape(concept['label'])
        references=''
        if 'inspiration' in concept:
            references='<p>Job inspiration: '+html.escape(concept['inspiration'])+'</p><details><summary>View original reference images used</summary>'
            for ref in concept['references']:
                ref_path=Path(ref['path'])
                relative='references/'+ref_path.name
                assert (OUT/relative).exists()
                references+=f'<a href="{relative}"><img style="height:auto" src="{relative}" alt="Original reference panel"></a>'
                for source in ref.get('sources',[]):
                    assert sha(ROOT/source['path'])==source['sha256']
                    references+=f'<a href="{html.escape(source["page"])}">{html.escape(source["id"])}</a><br>'
            references+='</details>'
        cards.append(f'<article><h2>{name}</h2><a href="{path.name}"><img src="{path.name}" alt="{name} concept illustration"></a><p><a href="{path.name}">Open full-size image</a></p>{references}</article>')
    board.save(OUT/'all-ten-concepts.jpg',quality=95,subsampling=0)
    MANIFEST.write_text(json.dumps(manifest,indent=2)+'\n')
    document = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FFTA class concept illustrations</title><style>
    *{box-sizing:border-box}body{margin:0;background:#eeeae2;color:#292a31;font:17px/1.5 system-ui,sans-serif}header,main{max-width:1500px;margin:auto;padding:28px}h1{margin:0}header p{margin:8px 0 0;color:#585b62}main{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px;padding-top:0}article{background:white;padding:20px;border-radius:12px}h2{font-size:21px;margin:0 0 18px}img{display:block;width:100%;height:650px;object-fit:contain}a{color:#35546b}p{margin:14px 0 0}@media(max-width:750px){main{grid-template-columns:1fr}img{height:560px}}
    </style><header><h1>FFTA class concept illustrations</h1><p>Ten original class designs using the original game's concept illustrations as visual references. First drafts for costume and silhouette review.</p></header><main>'''+''.join(cards)+'''</main></html>'''
    (OUT/'index.html').write_text(document,encoding='utf-8')
    print('Verified and packaged all ten full-resolution illustrations and all reference hashes.')

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--version',choices=['v1','v2'],default='v1')
    args=parser.parse_args()
    if args.version=='v2':
        OUT=ROOT/'build/art/illustrated-class-concepts-v2-2026-09-19'
        MANIFEST=ROOT/'src/art/race-study/illustrated-class-concepts-v2.json'
    main()
