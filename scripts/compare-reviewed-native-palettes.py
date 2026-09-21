"""Compare technical conversion to original palettes; never author artwork.

This is a visual feasibility study, not an import or palette acceptance.
"""
import json,struct
from PIL import Image,ImageDraw
from native_art import ROOT

rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
catalog=json.loads((ROOT/'src/art/race-study/full-animation-v1.json').read_text())
out=ROOT/'build/art/reviewed-integration/native-palette-comparison-v2';out.mkdir(exist_ok=True)
colors=[]
for bank in range(3):
    # Native menu OBJ banks0..2 are bright;3..5 are their authored dim variants.
    # The earlier sixteen-bank study starting at94EE3C crossed into unrelated
    # UI data. Preserve that rejected output; never treat it as16 job palettes.
    words=struct.unpack_from('<16H',rom,0x94eddc+bank*32)
    colors.append([tuple(((w>>s)&31)*255//31 for s in (0,5,10)) for w in words])
records=[]
for unit in catalog['units']:
    source=ROOT/'build/art/approved-class-animation-2026-09-19'/unit['slug']/'front-neutral.png'
    original=Image.open(source).convert('RGBA');candidates=[]
    for bank,rgb in enumerate(colors):
        converted=Image.new('RGBA',(32,32));error=0;count=0
        for y in range(32):
            for x in range(32):
                pixel=original.getpixel((x,y))
                if pixel[3]<128:continue
                distances=[sum((pixel[k]-rgb[i][k])**2 for k in range(3)) for i in range(1,16)]
                i=min(range(15),key=distances.__getitem__)+1
                converted.putpixel((x,y),rgb[i]+(255,));error+=distances[i-1];count+=1
        candidates.append((error/count,bank,converted))
    candidates.sort(key=lambda v:v[0]);sheet=Image.new('RGBA',(768,214),(228,226,220,255));draw=ImageDraw.Draw(sheet)
    sheet.alpha_composite(original.resize((192,192),Image.Resampling.NEAREST),(0,24));draw.text((4,4),'Approved source',fill='black')
    for n,(error,bank,im) in enumerate(candidates[:7],1):
        x=n%4*192;y=n//4*214;sheet.alpha_composite(im.resize((192,192),Image.Resampling.NEAREST),(x,y+22));draw.text((x+3,y+3),f'Original palette {bank}; error {error:.0f}',fill='black')
    sheet.save(out/(unit['slug']+'.png'));records.append(dict(slug=unit['slug'],ranking=[dict(bank=b,error=e) for e,b,im in candidates]))
(out/'report.json').write_text(json.dumps(dict(scope=__doc__,records=records),indent=2)+'\n')
print(out)
