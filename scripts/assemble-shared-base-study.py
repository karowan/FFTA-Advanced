"""Preserve an extracted native shared layer over imagegen costume pixels.

No new pixel patterns are authored: resample/quantize generated art and composite
only unmodified original pixels common to all four supplied reference sprites.
This is a private study, not an import or a universal all-job/race base.
"""
import hashlib,json
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/art/race-study-2026-09-19'
reference=OUT/'user-face-reference.png'
source=OUT/'shared-base-v1-generated.png'
ref=Image.open(reference).convert('RGBA').resize((128,40),Image.Resampling.NEAREST)
cells=[ref.crop((i*32,4,i*32+32,36)) for i in range(4)]
background=ref.getpixel((0,0))
palette=sorted({c.getpixel((x,y))[:3] for c in cells for y in range(32) for x in range(32) if c.getpixel((x,y))!=background})
assert len(palette)<=15,len(palette)
fixed=[(x,y,cells[0].getpixel((x,y))) for y in range(32) for x in range(32)
       if cells[0].getpixel((x,y))!=background and len({c.getpixel((x,y)) for c in cells})==1]
assert len(fixed)==68
full=Image.open(source).convert('RGBA').resize((160,64),Image.Resampling.NEAREST)
generated=full.crop((128,16,160,48))
generated.putalpha(generated.getchannel('A').point(lambda a:255 if a>=128 else 0))
generated.save(OUT/'shared-base-v1-grid.png')
converted=Image.new('RGBA',(32,32))
for y in range(32):
    for x in range(32):
        rgb=generated.getpixel((x,y))
        if rgb[3]:
            nearest=min(palette,key=lambda c:sum((c[i]-rgb[i])**2 for i in range(3)))
            converted.putpixel((x,y),(*nearest,255))
before=sum(converted.getpixel((x,y))==value for x,y,value in fixed)
layer=Image.new('RGBA',(32,32))
for x,y,value in fixed:layer.putpixel((x,y),value)
layer.save(OUT/'shared-base-immutable-layer.png')
converted.alpha_composite(layer)
assert all(converted.getpixel((x,y))==v for x,y,v in fixed)
assert len(converted.getcolors(1024))<=16
converted.save(OUT/'shared-base-v1-locked.png')
converted.resize((512,512),Image.Resampling.NEAREST).save(OUT/'shared-base-v1-locked-16x.png')
board=Image.new('RGBA',(160,40),background);board.alpha_composite(ref);board.alpha_composite(converted,(128,4))
board.save(OUT/'shared-base-v1-comparison-1x.png')
board.resize((1280,320),Image.Resampling.NEAREST).save(OUT/'shared-base-v1-comparison-8x.png')
report=dict(scope='Only exact common foreground of four supplied native same-pose references; not every job or animation.',
 sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),referenceSha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
 generatedGrid={'size':[160,64],'crop':[128,16,160,48],'resampling':'nearest','alphaThreshold':128},
 referenceGrid={'size':[128,40],'cellCropY':[4,36]},palette=palette,
 commonForegroundPixels=len(fixed),matchingBeforeProtection=before,matchingAfterProtection=len(fixed),
 sharedPixels=fixed,method='Copy exact unchanged shared native layer; all remaining artwork comes from imagegen with nearest original-palette conversion.',
 productionAccepted=False)
(OUT/'shared-base-v1-proof.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['commonForegroundPixels','matchingBeforeProtection','matchingAfterProtection']}))
