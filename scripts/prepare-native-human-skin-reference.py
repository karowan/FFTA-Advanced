"""Export original human sprites with their actual class palette selectors.

Reference extraction only: no replacement artwork, palette editing, or ROM writes.
"""
import hashlib, json, struct
from PIL import Image, ImageDraw
from native_art import ROOT, palette, compose, sha


def main():
    rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    assert hashlib.sha1(rom).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
    table=struct.unpack_from('<I',rom,0xc8598)[0]-0x08000000
    out=ROOT/'build/art/native-color-study-2026-09-20/native-human-skin';out.mkdir(exist_ok=True)
    board=Image.new('RGBA',(1280,384),'#e4e2dc');draw=ImageDraw.Draw(board);records=[]
    for col,job in enumerate(range(2,12)):
        rec=table+job*52;actor=struct.unpack_from('<H',rom,rec+7)[0];selector=rom[rec+11]&15
        path=ROOT/f'build/art/native-reference/actor-{actor:03}/native.json'
        library=json.loads(path.read_text());frame=library['slots'][0]['frames'][1];pose=library['poses'][frame['pose']]
        raw=rom[pose['tileOffset']:pose['tileOffset']+pose['tileCount']*32]
        assert sha(raw)==pose['tileSha256']
        for row,base in enumerate((0x419d60,0x41a860)):
            _,rgb=palette(rom,base+selector*32)
            image=compose(raw,pose['objects'],rgb).crop((32,28,64,60));dest=out/f'job-{job}-bank-{row}.png'
            image.save(dest,bits=4)
            board.alpha_composite(image.convert('RGBA').resize((128,128),Image.Resampling.NEAREST),(col*128,row*192+30))
            draw.text((col*128+4,row*192+4),f'Job{job} pal{selector} bank{row}',fill='black')
            records.append(dict(job=job,resource=actor,selector=selector,paletteOffset=base+selector*32,
                                path=str(dest.relative_to(ROOT)),sha256=sha(dest.read_bytes()),nativePose=frame['pose']))
    board.save(out/'original-humans.png')
    reference=Image.new('RGBA',(768,320),'#e4e2dc');draw=ImageDraw.Draw(reference)
    for i,job in enumerate((2,3,7)):
        im=Image.open(out/f'job-{job}-bank-0.png').convert('RGBA')
        reference.alpha_composite(im.resize((256,256),Image.Resampling.NEAREST),(i*256,24))
        draw.text((i*256+12,286),'Original FFTA human skin',fill='black')
    reference.save(out/'skin-reference.png')
    report=dict(sourceRomSha1=hashlib.sha1(rom).hexdigest(),classTable=table,records=records,
                generationReference=dict(path=str((out/'skin-reference.png').relative_to(ROOT)),sha256=sha((out/'skin-reference.png').read_bytes())),
                scope=__doc__)
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['generationReference']))


if __name__=='__main__':main()
