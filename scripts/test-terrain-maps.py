"""Decode the complete USA map table and retain reproducible review images.

This validates component bounds and stream decoding. Production material
annotations and native pixel/height differentials require additional evidence.
"""
import json,pathlib,hashlib,collections
from PIL import Image,ImageDraw
from ffta_maps import Maps,COUNT,MapError
ROOT=pathlib.Path(__file__).resolve().parents[1]
rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();maps=Maps(rom)
OUT=ROOT/'build/expansion/terrain'/hashlib.sha1(rom).hexdigest();OUT.mkdir(parents=True,exist_ok=True)
entries=[];failures=[]
for index in range(COUNT):
 try:
  graphics=maps.graphics(index);palette=maps.palette(index);heights=maps.heights(index);arrange=maps.planar(index);clipping=maps.clipping(index)
  picture,grid,layers=maps.render(index)
  picture.save(OUT/f'map-{index:03}.png');grid.save(OUT/f'map-{index:03}-grid.png')
  entries.append(dict(map=index,heightSha1=hashlib.sha1(heights).hexdigest(),graphicsSha1=hashlib.sha1(graphics.data).hexdigest(),paletteSha1=hashlib.sha1(palette.data).hexdigest(),arrangementSha1=hashlib.sha1(arrange).hexdigest(),clippingSha1=hashlib.sha1(clipping).hexdigest(),cells=sum(heights[i]!=0 for i in range(0,512,2)),graphicsAddress=graphics.address,paletteAddress=palette.address,paletteCodec=palette.codec))
 except Exception as e:failures.append(dict(map=index,error=f'{type(e).__name__}: {e}'))
for start in range(0,COUNT,24):
 sheet=Image.new('RGB',(6*260,4*282),(25,28,35));draw=ImageDraw.Draw(sheet)
 for i in range(start,min(COUNT,start+24)):
  if i not in {entry['map'] for entry in entries}:continue
  im=Image.open(OUT/f'map-{i:03}.png').convert('RGBA');im.thumbnail((256,256))
  x=(i-start)%6*260;y=(i-start)//6*282;sheet.paste(im,(x,y+22),im);draw.text((x+8,y+5),f'Map {i} / {i:02X}',fill='white')
 sheet.save(OUT/f'contact-{start:03}.png')
report=dict(passed=not failures,romSha1=hashlib.sha1(rom).hexdigest(),maps=entries,failures=failures,limits=['Rendering and geometry alignment need independent native comparison.','No material annotation is implied by successful decoding.'])
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(passed=report['passed'],decoded=len(entries),failures=failures,output=str(OUT)),indent=2))
assert not failures,('Map decoding failures',len(failures))
