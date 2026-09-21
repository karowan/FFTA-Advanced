"""Prepare fixed native portrait/icon cells and preserved imagegen instructions."""
import json,struct
from pathlib import Path
from PIL import Image,ImageDraw
from native_art import ROOT,sha
from native_portraits import PIXELS,LAYOUTS,PALETTES,entry,decode,layout,compose
from native_miniatures import decode as decode_palette

OUT=ROOT/'build/art/native-ui-regeneration-v2-2026-09-20'
def record(p):return dict(path=str(p.relative_to(ROOT)),sha256=sha(p.read_bytes()))
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    old=json.loads((ROOT/'build/art/reviewed-integration/portraits/generation-plan.json').read_text())
    rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    final=json.loads((ROOT/'build/art/native-final-integration-2026-09-20/candidate.json').read_text())
    evidence=json.loads((ROOT/'build/art/native-final-integration-2026-09-20/evidence.json').read_text())
    inv=Path(next(r['path'] for r in evidence['reports'] if r['test']=='test-final-native-inventory-ui')).parent
    original=Image.open(inv/'party-original-jobs.png').resize((240,160),Image.Resampling.NEAREST)
    jobs=[]
    for j in old['jobs']:
        folder=OUT/j['slug'];folder.mkdir(exist_ok=True)
        portraits=[];icons=[];palettes=[]
        for ref in j['nativeReferences']:
            raw,_=decode(rom,entry(rom,PIXELS,ref['portrait']));objects,_=layout(rom,entry(rom,LAYOUTS,ref['portrait']))
            words=struct.unpack('<48H',decode_palette(rom,PALETTES[0],ref['palette']))
            rgb=[0]*768;rgb[288:432]=[((w>>s)&31)*255//31 for w in words for s in (0,5,10)]
            # Decode the entire original, including tall ears above the 64px
            # primary object. Scaling here is for references, never new art.
            full=Image.new('RGBA',(128,160))
            for obj in reversed(objects):
                w,h=obj['width'],obj['height'];part=Image.new('P',(w,h));part.putpalette(rgb)
                for ty in range(h//8):
                    for tx in range(w//8):
                        at=obj['tile']*32+(ty*(w//8)+tx)*64
                        tile=Image.frombytes('P',(8,8),raw[at:at+64]);tile.putpalette(rgb);part.paste(tile,(tx*8,ty*8))
                part.info['transparency']=0;part=part.convert('RGBA')
                if obj['flipH']:part=part.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                if obj['flipV']:part=part.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                full.alpha_composite(part,(64+obj['x'],128+obj['y']))
            part=full.crop(full.getbbox());part.thumbnail((48,56),Image.Resampling.NEAREST)
            cell=Image.new('RGBA',(48,56));cell.alpha_composite(part,((48-part.width)//2,56-part.height))
            path=folder/f"original-{ref['job']}-portrait.png";cell.save(path);portraits.append(record(path))
            n=ref['job']-2;x=8+(n%7)*32;y=16+(n//7)*24
            badge=original.crop((x,y,x+32,y+16));icon=badge.crop((1,1,17,15))
            path=folder/f"original-{ref['job']}-icon.png";icon.save(path);icons.append(record(path))
            palettes.append(dict(job=ref['job'],index=ref['palette'],words=list(words)))
        sources=[]
        for kind,refs,size,scale in [('portrait',portraits,(48,56),8),('icon',icons,(16,14),24)]:
            w,h=size;board=Image.new('RGBA',(w*3,h*2),(228,226,220,255))
            for n,ref in enumerate(refs):board.alpha_composite(Image.open(ROOT/ref['path']).convert('RGBA'),(n%2*w,n//2*h))
            # The approved sprite explicitly anchors the third column.
            anchor=Image.open(ROOT/j['design']['path']).convert('RGBA');anchor.thumbnail((w,h),Image.Resampling.NEAREST)
            board.alpha_composite(anchor,(2*w+(w-anchor.width)//2,(h-anchor.height)//2))
            path=folder/(kind+'-template.png');board.resize((w*3*scale,h*2*scale),Image.Resampling.NEAREST).save(path)
            prompt=(f'Draw a new {j["label"]} {"menu portrait" if kind=="portrait" else "tiny job-head icon"} in the blank BOTTOM-RIGHT cell of image 1, directly below the small character in the THIRD column. Keep all four references in the LEFT TWO columns. '
                    f'The four other images in that sheet are original jobs of the same race: match their face anatomy, pixel size, framing and style. '
                    f'Use the new character design in image 2. The target is exactly {w} by {h} logical pixels; '
                    'design directly for that coarse pixel grid, with clear eyes and a readable silhouette. '
                    'Keep the entire worksheet and cell boundaries unchanged. Transparent background in the new cell. No text, border or extra characters. ')
            if kind=='portrait':prompt+='Bust portrait, same close framing as the references; full headgear inside the cell, shoulders meet its bottom edge. '
            else:prompt+='Only the head, no shoulders or body. Use only colors from image 3, with dark outlines and bright contrast. '
            if j['job'] in (117,119):prompt+='Wear the closed helmet. '
            if j['job']==119:prompt+='The blue cloth comes out BEHIND the helmet, tucked behind the rear metal edge; it must not cross the face or front of the helmet. '
            if j['job']==116:prompt+='Preserve the gold crescent and red helmet. '
            sources.append(dict(kind=kind,logicalSize=[w*3,h*2],crop=[w*2,h,w*3,h*2],nativeSize=list(size),template=record(path),prompt=prompt,refs=refs))
        badge=next(x for x in final['components']['reviewedMenuBadges']['jobs'] if x['job']==j['job'])
        words=struct.unpack_from('<16H',rom,badge['badge']['paletteOffset']);swatches=Image.new('RGB',(480,64));draw=ImageDraw.Draw(swatches)
        for n,w in enumerate(words):draw.rectangle((n*30,0,n*30+29,63),fill=tuple(((w>>s)&31)*255//31 for s in (0,5,10)))
        palpath=folder/'native-icon-palette.png';swatches.save(palpath)
        jobs.append(dict(job=j['job'],slug=j['slug'],label=j['label'],concept=j['concept'],assets=sources,
            iconPalette=record(palpath),iconPaletteWords=list(words),portraitPalettes=palettes))
    plan=OUT/'plan.json'
    if plan.exists():
        assert not list(OUT.glob('*/generated-*.png')),'Preserve generation inputs after first generation'
    plan.write_text(json.dumps(dict(schema=1,tool='image_gen.imagegen',model='Built-in tool managed',jobs=jobs),indent=2)+'\n')
    print(plan)
if __name__=='__main__':main()
