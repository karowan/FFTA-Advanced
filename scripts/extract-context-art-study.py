"""Extract last cell and key its neutral background; never paint sprite pixels."""
import argparse,json
from collections import deque
from pathlib import Path
from PIL import Image

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('source',type=Path);p.add_argument('output',type=Path)
a=p.parse_args()
im=Image.open(a.source).convert('RGBA')
crop=(im.width*4//5,0,im.width,im.height)
im=im.crop(crop);px=im.load();key=px[0,0][:3]
todo=deque([(x,y) for x in range(im.width) for y in (0,im.height-1)]+[(x,y) for y in range(im.height) for x in (0,im.width-1)])
seen=set();removed=0
while todo:
    x,y=todo.popleft()
    if (x,y) in seen or not(0<=x<im.width and 0<=y<im.height):continue
    seen.add((x,y));c=px[x,y]
    if max(abs(c[i]-key[i]) for i in range(3))>20 or max(c[:3])-min(c[:3])>22:continue
    px[x,y]=(*c[:3],0);removed+=1
    todo.extend(((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
im.save(a.output)
a.output.with_suffix('.extraction.json').write_text(json.dumps(dict(source=str(a.source),crop=crop,key=key,tolerance=20,maxChroma=22,method='Border-connected color key; RGB unchanged; no painted pixels',removed=removed),indent=2)+'\n')
