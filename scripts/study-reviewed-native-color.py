"""Technical color-conversion study. Does not publish or modify game assets.

Compare source RGB555 distance with perceptual Oklab distance and a neutral
chroma penalty, across all three existing native shared palettes. Same color
always maps to the same index. No dithering, geometry changes or authored pixels.
"""
import html,json,struct
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from native_art import ROOT,sha

OUT=ROOT/'build/art/native-color-study-2026-09-20'

def oklab(rgb):
    v=np.asarray(rgb,dtype=float)/255
    v=np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
    lms=v@np.array([[.4122214708,.2119034982,.0883024619],[.5363325363,.6806995451,.2817188376],[.0514459929,.1073969566,.6299787005]])
    return np.cbrt(lms)@np.array([[.2104542553,1.9779984951,.0259040371],[.7936177850,-2.4285922050,.7827717662],[-.0040720468,.4505937099,-.8086757660]])

def convert(im,colors,method):
    rgba=np.asarray(im.convert('RGBA'));rgb=rgba[:,:,:3];a=rgba[:,:,3]
    source=rgb.reshape(-1,3)
    if method=='rgb555':
        p=np.round(source.astype(float)*31/255);q=np.round(np.array(colors,dtype=float)*31/255)
        cost=((p[:,None,:]-q[None,1:,:])**2).sum(2)
    else:
        p=oklab(source);q=oklab(colors)[1:]
        cost=((p[:,None,:]-q[None,:,:])**2).sum(2)
        if method=='neutral':
            cp=np.linalg.norm(p[:,1:],axis=1)[:,None];cq=np.linalg.norm(q[:,1:],axis=1)[None,:]
            # Discourage adding saturated color to dark neutral material.
            weight=np.clip((.06-cp)/.06,0,1)*4
            cost+=weight*np.maximum(cq-cp-.015,0)**2
    indices=cost.argmin(1)+1;indices[a.reshape(-1)==0]=0
    result=Image.new('P',im.size);result.putdata(indices.tolist())
    result.putpalette([v for c in colors for v in c]+[0]*(768-48));result.info['transparency']=0
    assert np.array_equal(np.asarray(result)==0,a==0)
    return result,float(cost.min(1)[a.reshape(-1)>0].mean())

def main():
    OUT.mkdir(parents=True,exist_ok=True);rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    colors=[[[((w>>s)&31)*255//31 for s in (0,5,10)] for w in struct.unpack_from('<16H',rom,0x419d60+n*32)] for n in range(3)]
    for n,rgb in enumerate(colors):
        chart=Image.new('RGB',(800,360),'#e4e2dc');draw=ImageDraw.Draw(chart)
        draw.text((15,10),f'Original FFTA battle palette {n}. Opaque colors 1-15. Index 0 is transparent.',fill='black')
        for i,c in enumerate(rgb[1:],1):
            x=(i-1)%5*160;y=(i-1)//5*104+38
            draw.rectangle((x+10,y,x+150,y+70),fill=tuple(c));draw.text((x+12,y+76),f'{i}: #'+''.join(f'{v:02X}' for v in c),fill='black')
        chart.save(OUT/f'palette-{n}.png')
    catalog=json.loads((ROOT/'src/art/race-study/full-animation-v1.json').read_text());records=[];cards=[]
    for unit in catalog['units']:
        source=ROOT/unit['front']['path'];assert sha(source.read_bytes())==unit['front']['sha256']
        im=Image.open(source).convert('RGBA');folder=OUT/unit['slug'];folder.mkdir(exist_ok=True)
        im.save(folder/'source.png');im.resize((512,512),Image.Resampling.NEAREST).save(folder/'source-reference.png')
        variants=[];figures=[]
        for n,rgb in enumerate(colors):
            for method in ('rgb555','oklab','neutral'):
                converted,error=convert(im,rgb,method);name=f'palette-{n}-{method}.png';converted.save(folder/name,bits=4)
                variants.append(dict(palette=n,method=method,error=error,path=str((folder/name).relative_to(ROOT)),sha256=sha((folder/name).read_bytes())))
                figures.append(f'<figure><img src="{unit["slug"]}/{name}"><figcaption>Palette {n} · {method}</figcaption></figure>')
        board=Image.new('RGBA',(1024,720),(228,226,220,255));draw=ImageDraw.Draw(board)
        draw.text((6,4),unit['label']+' - SOURCE | RGB555 | OKLAB | NEUTRAL-PROTECTED',fill='black')
        for n in range(3):
            y=24+n*232;board.alpha_composite(im.resize((192,192),Image.Resampling.NEAREST),(16,y))
            for k,method in enumerate(('rgb555','oklab','neutral'),1):
                v=Image.open(folder/f'palette-{n}-{method}.png').convert('RGBA')
                board.alpha_composite(v.resize((192,192),Image.Resampling.NEAREST),(16+k*256,y))
            draw.text((10,y+198),f'Native palette {n}',fill='black')
        board.save(folder/'comparison.png')
        cards.append(f'<article><h2>{unit["label"]}</h2><figure><img src="{unit["slug"]}/source.png"><figcaption>Approved source</figcaption></figure><div class="grid">'+''.join(figures)+'</div></article>')
        records.append(dict(job=unit['job'],slug=unit['slug'],source=str(source),sourceSha256=sha(source.read_bytes()),variants=variants))
    (OUT/'manifest.json').write_text(json.dumps(dict(scope=__doc__,nativeRomSha256=sha(rom),palettes=colors,records=records),indent=2)+'\n')
    (OUT/'index.html').write_text('''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Native palette conversion study</title><style>body{font:16px system-ui;background:#e4e2dc;color:#202431;margin:24px}article{background:#f5f3ed;border-radius:12px;padding:20px;margin:24px 0}.grid{display:grid;grid-template-columns:repeat(3,1fr)}figure{margin:12px}img{width:160px;image-rendering:pixelated}figcaption{font-size:14px}p{max-width:950px}</style><h1>Native color conversion study</h1><p>Each row uses one of the game's three existing palettes. Columns compare the rejected RGB-distance conversion, perceptual mapping, and perceptual mapping that protects neutral materials from unwanted color. Sprite shape and animation sources are unchanged. No palette bytes or game code have been edited. These are experiments, not installed artwork.</p>'''+''.join(cards),encoding='utf-8')
    print(OUT)

if __name__=='__main__':main()
