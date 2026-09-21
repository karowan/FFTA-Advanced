"""Reuse the approved Samurai's face for unchanged front head orientations.

This is the exact-existing-pixel operation the user authorized for face repair,
not authored pixel art. Bowed/turned/defeated faces are deliberately excluded.
"""
import json
from pathlib import Path
from PIL import Image
from native_art import ROOT, sha

path=ROOT/'src/art/race-study/full-animation-v1.json';spec=json.loads(path.read_text())
unit=next(u for u in spec['units'] if u['job']==116)
source=ROOT/unit['front']['path'];approved=Image.open(source).convert('RGBA').crop((10,8,18,14))
for pid,position in [('p006',(8,6)),('p007',(6,6)),('p008',(8,5)),
                     ('p018',(8,7)),('p019',(8,6)),('p022',(7,5)),
                     ('p023',(4,7)),('p026',(7,6)),('p027',(4,6)),('p030',(8,5)),
                     ('p044',(7,8)),('p045',(7,6)),('p046',(6,5)),
                     ('p060',(7,5)),('p062',(8,8)),('p064',(8,7))]:
    pose=next(p for p in unit['poses'] if p['id']==pid)
    out=ROOT/pose['output'];archive=out.with_name(pid+'-before-face-lock.png')
    if not archive.exists():archive.write_bytes(out.read_bytes())
    image=Image.open(archive).convert('RGBA');before=image.copy();image.paste(approved,position)
    changed=[]
    for y in range(32):
        for x in range(32):
            if image.getpixel((x,y))!=before.getpixel((x,y)):
                assert position[0]<=x<position[0]+8 and position[1]<=y<position[1]+6
                changed.append([x,y])
    image.save(out)
    pose['mechanicalCorrection']=dict(operation='exact-rgba-region-reuse',
        authorization='User explicitly authorized exact approved face reuse: yes do whatever you need to',
        source=unit['front']['path'],sourceSha256=sha(source.read_bytes()),sourceBox=[10,8,18,14],position=list(position),
        before=str(archive.relative_to(ROOT)).replace('\\','/'),beforeSha256=sha(archive.read_bytes()),
        changedPixelCount=len(changed),changedPixelsOutsideDestination=0)
    pose['outputSha256']=sha(out.read_bytes())
path.write_text(json.dumps(spec,indent=2)+'\n')
print('Reused the approved face in sixteen front poses; all pixels outside each 8x6 region are unchanged.')
