"""Export coordinate-labelled surface crops for terrain content review.

Read-only authoring aid; it neither assigns materials nor creates game fixtures.
All rendered art stays in the ignored build directory.
"""
import argparse,pathlib,json
from PIL import Image,ImageDraw
from ffta_maps import Maps,CLEAN_SHA1,tile_center
ROOT=pathlib.Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('maps',nargs='+',type=int)
parser.add_argument('--materials',action='store_true',help='Label reviewed symbols and export a full material overlay')
args=parser.parse_args();maps=Maps((ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes())
catalog={e['map']:e for e in json.loads((ROOT/'notes/terrain-materials.json').read_text())['maps']}
out=ROOT/'build/expansion/terrain'/CLEAN_SHA1
for index in args.maps:
 picture,_,_=maps.render(index);h=maps.heights(index)
 entry=catalog.get(index);overlay=picture.copy();mark=ImageDraw.Draw(overlay)
 sheet=Image.new('RGB',(16*96,16*70),(30,30,35));draw=ImageDraw.Draw(sheet)
 for y in range(16):
  for x in range(16):
   z=h[(y*16+x)*2]
   if not z:continue
   cx,cy=tile_center(x,y,z)
   patch=picture.crop((cx-16,cy-8,cx+16,cy+8)).resize((96,48),Image.Resampling.NEAREST)
   dx,dy=x*96,y*70;sheet.paste(patch,(dx,dy+18),patch)
   symbol=entry['rows'][y][x] if entry else '?'
   draw.text((dx+2,dy+2),f'{x},{y} h{z}'+(' '+symbol if args.materials else ''),fill='white')
   if args.materials and symbol not in '.?':
    mark.text((cx-3,cy-4),symbol,fill='white',stroke_width=1,stroke_fill='black')
   draw.line((dx+45,dy+42,dx+51,dy+42),fill='red',width=1)
   draw.line((dx+48,dy+39,dx+48,dy+45),fill='red',width=1)
 suffix='review' if args.materials else 'cells'
 sheet.save(out/f'map-{index:03}-{suffix}.png')
 if args.materials:overlay.save(out/f'map-{index:03}-review-overlay.png')
 print(out/f'map-{index:03}-{suffix}.png')
