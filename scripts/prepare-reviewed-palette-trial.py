"""Offline, deterministic three-group 4bpp conversion experiment.

Does not modify a ROM or claim safe runtime palette allocation. Image colors
come only from approved artwork; this is technical quantization, not art authoring.
"""
import collections
import json
import math
from PIL import Image
from native_art import ROOT, sha

groups=[[116,123,124],[117,119,121],[118,120,122,125]]
source=ROOT/'src/art/race-study/animation-generation-v1.json';spec=json.loads(source.read_text())
out=ROOT/'build/art/reviewed-integration';out.mkdir(parents=True,exist_ok=True)
palettes=[];sources=[]
for group in groups:
    counts=collections.Counter()
    for unit in spec['units']:
        if unit['job'] not in group:continue
        path=ROOT/unit['base'];image=Image.open(path).convert('RGBA')
        sources.append(dict(job=unit['job'],path=unit['base'],sha256=sha(path.read_bytes())))
        counts.update(tuple(round(v/255*31) for v in p[:3]) for p in image.get_flattened_data() if p[3]>=128)
    # Square-root frequency retains small costume accents without weighting
    # every rare generated shade as heavily as the main clothing colors.
    colors=[]
    for color,n in counts.items():colors.extend([tuple(v*255//31 for v in color)]*max(1,round(math.sqrt(n))))
    strip=Image.new('RGB',(len(colors),1));strip.putdata(colors)
    quantized=strip.quantize(colors=15,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
    raw=quantized.getpalette()[:45]
    palettes.append([tuple(round(v/255*31)*255//31 for v in raw[i:i+3]) for i in range(0,45,3)])
board=Image.new('RGBA',(1280,292),(228,226,220,255))
for i,unit in enumerate(spec['units']):
    im=Image.open(ROOT/unit['base']).convert('RGBA')
    pal=palettes[next(n for n,g in enumerate(groups) if unit['job'] in g)]
    converted=Image.new('RGBA',(32,32))
    converted.putdata([(*min(pal,key=lambda c:sum((c[j]-p[j])**2 for j in range(3))),p[3])
                       if p[3]>=128 else (0,0,0,0) for p in im.get_flattened_data()])
    board.alpha_composite(im.resize((128,128),Image.Resampling.NEAREST),(i*128,16))
    board.alpha_composite(converted.resize((128,128),Image.Resampling.NEAREST),(i*128,160))
board.convert('RGB').save(out/'three-palette-trial.png')
report=dict(scope='Offline experiment only. Requires independent runtime palette engineering, not final artwork acceptance.',
            groups=groups,palettesRGB=palettes,sources=sources,sourceManifestSha256=sha(source.read_bytes()),
            scriptSha256=sha(__import__('pathlib').Path(__file__).read_bytes()))
(out/'three-palette-trial.json').write_text(json.dumps(report,indent=2)+'\n')
print('Wrote the three-palette comparison and authenticated inputs; no ROM was changed.')
