"""Deterministic indexed-format checks; no emulator or player files."""
import json
from native_art import ROOT, Image, compose, pack_tiles, tile_image

checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)

# Deliberately black RGB entries: visibility depends on index zero, not color.
rgb=[0]*48
atlas=Image.new('P',(16,8));atlas.putpalette(rgb+[0]*720)
for y in range(8):
    for x in range(8): atlas.putpixel((x,y),1+(x+y*3)%15)
atlas.putpixel((8,0),4)
raw=pack_tiles(atlas,2)
check(tile_image(raw,rgb,16).tobytes()==atlas.tobytes(),'all indexed values roundtrip')
def obj(tile,x=0,y=0,h=False,v=False):
    return dict(tile=tile,x=x,y=y,width=8,height=8,flipH=h,flipV=v)
for h,v in ((False,False),(True,False),(False,True),(True,True)):
    rendered=compose(raw,[obj(0,-4,-8,h,v)],rgb)
    check(all(rendered.getpixel((44+x,56+y))==atlas.getpixel((7-x if h else x,7-y if v else y))
              for y in range(8) for x in range(8)),f'nonzero black pixels and flips {h}/{v}')
rendered=compose(raw,[obj(1),obj(0)],rgb)
check(rendered.getpixel((48,64))==4,'lower OAM index wins opaque overlap')
check(rendered.getpixel((49,64))==atlas.getpixel((1,0)),'index zero reveals lower object')
check(rendered.getpixel((0,0))==0,'outside objects remains transparent')
out=ROOT/'build/art/format';out.mkdir(parents=True,exist_ok=True)
(out/'report.json').write_text(json.dumps(dict(status='passed',checks=checks),indent=2)+'\n')
print(json.dumps(dict(status='passed',checks=len(checks),scope='Static format/compositor only')))
