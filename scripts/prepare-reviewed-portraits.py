"""Lay out decoded native portrait references for separate imagegen artwork.

Only archive decoding and reference placement happen here; no character drawing.
"""
import json,struct
from PIL import Image
from native_art import ROOT,sha
from native_portraits import PIXELS,LAYOUTS,PALETTES,entry,decode,layout,compose
from native_miniatures import decode as palette_decode


def main():
    rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    catalog=json.loads((ROOT/'src/art/race-study/full-animation-v1.json').read_text())
    table=struct.unpack_from('<I',rom,0xc8598)[0]-0x08000000
    out=ROOT/'build/art/reviewed-integration/portraits';out.mkdir(parents=True,exist_ok=True)
    jobs=[]
    def record(p):return dict(path=str(p.relative_to(ROOT)).replace('\\','/'),sha256=sha(p.read_bytes()))
    for u in catalog['units']:
        refs=[];worksheet=Image.new('RGBA',(192,128),(228,226,220,255))
        actors=list(dict.fromkeys(v['actor'] for v in u['poses'][6]['generation']['nativeReferences']))[:4]
        for n,actor in enumerate(actors):
            matches=[j for j in range(116) if rom[table+j*52+7]==actor]
            assert matches,(u['slug'],actor)
            j=matches[0];pid,palid=rom[table+j*52+13:table+j*52+15]
            raw,_=decode(rom,entry(rom,PIXELS,pid));objects,_=layout(rom,entry(rom,LAYOUTS,pid))
            words=struct.unpack('<48H',palette_decode(rom,PALETTES[0],palid))
            colors=[0]*768;colors[96*3:144*3]=[((w>>s)&31)*255//31 for w in words for s in (0,5,10)]
            im=compose(raw,objects,colors).convert('RGBA');box=im.getbbox();assert box
            part=im.crop(box);part.thumbnail((64,64),Image.Resampling.NEAREST)
            cell=Image.new('RGBA',(64,64));cell.alpha_composite(part,((64-part.width)//2,64-part.height))
            path=out/f"native-job-{j:03}.png";cell.save(path)
            worksheet.alpha_composite(cell,(n%2*64,n//2*64))
            refs.append(dict(job=j,portrait=pid,palette=palid,image=record(path),nativeBounds=list(box)))
        design=ROOT/'build/art/approved-class-animation-2026-09-19'/u['slug']/'front-neutral.png'
        worksheet.alpha_composite(Image.open(design).convert('RGBA'),(144,16))
        template=out/(u['slug']+'-template.png');worksheet.resize((1152,768),Image.Resampling.NEAREST).save(template)
        jobs.append(dict(job=u['job'],slug=u['slug'],label=u['label'],nativeReferences=refs,template=record(template),design=record(design),concept=u['originalConcept'],logicalSize=[192,128],crop=[128,64,192,128],status='pending',prompt=f"Draw a 64x64 pixel-art menu portrait of the {u['label']} in the empty bottom-right square of image 1. Match the four native portraits on the left. Use the character design and colors from image 2, including its headgear. Keep the worksheet layout unchanged."))
    path=out/'generation-plan.json';assert not path.exists(),'Preserve existing generation provenance'
    path.write_text(json.dumps(dict(schema=1,tool='built-in image_gen',jobs=jobs),indent=2)+'\n')
    print(path)


if __name__=='__main__':main()
