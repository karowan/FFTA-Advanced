"""Pack original, explicitly drawn portrait pixels; never sample a donor sprite."""
import json
from PIL import Image,ImageDraw
from native_art import ROOT,pack_tiles,palette,sha

def compile_portraits(out):
    spec=json.loads((ROOT/'src/art/job-portraits.json').read_text())
    assert spec['schema']==1
    portraits=spec['portraits'];assert [p['job'] for p in portraits]==list(range(116,126))
    rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    # Native frame only, drawn explicitly; character region starts blank.
    frame=['0'+'1'*30+'0','1'+'3'*28+'bc1','1'+'b'*29+'b1']
    frame+=['1'+'c'*30+'1']*10
    frame+=['1'+'b'*29+'31','1'+'c'*29+'21','0'+'1'*30+'0']
    assert len(frame)==16 and all(len(row)==32 for row in frame)
    blobs=[];records=[]
    sheet=Image.new('RGB',(384,560),'#233038');draw=ImageDraw.Draw(sheet)
    for n,p in enumerate(portraits):
        rows=p['rows'];assert len(rows)==16 and all(len(row)<=18 for row in rows),(p['job'],[len(r) for r in rows])
        pixels=[int(c,16) for row in frame for c in row]
        for y,row in enumerate(rows):
            for x,c in enumerate(row.ljust(18,'.')):
                # The entire character canvas is authored, including background.
                pixels[y*32+x]=int(c,16) if c!='.' else (int(frame[y][x],16) if x==0 or y in (0,15) else 3)
        im=Image.new('P',(32,16));im.putdata(pixels)
        _,rgb=palette(rom,0x419d60+32*(p['paletteBank']-13))
        im.putpalette(rgb+[0]*(768-len(rgb)));im.info['transparency']=0
        raw=pack_tiles(im,8);blobs.append(raw)
        imagepath=out/f"portrait-{p['job']}.png";im.save(imagepath,bits=4)
        with Image.open(imagepath) as reopened:assert pack_tiles(reopened,8)==raw
        x=(n%2)*192;y=(n//2)*112
        draw.text((x+4,y+3),p['name'],fill='white')
        sheet.paste(im.convert('RGB').resize((160,80),Image.Resampling.NEAREST).crop((0,0,90,80)),(x+4,y+17))
        records.append(dict(job=p['job'],tileSha256=sha(raw),authorship=spec['authorship'],status=spec['status']))
    header='/* Original portrait pixels; generated from source JSON, no donor character data. */\n'
    header+='static const unsigned char original_job_icons[10][256]={\n'
    header+=',\n'.join('{'+','.join(str(b) for b in raw)+'}' for raw in blobs)+'\n};\n'
    (out/'job-icons.h').write_text(header)
    (out/'portrait-records.json').write_text(json.dumps(records,indent=2)+'\n')
    sheet.save(out/'portrait-review.png')
    return records

if __name__=='__main__':
    out=ROOT/'build/art/authored/menu-portraits';out.mkdir(parents=True,exist_ok=True)
    compile_portraits(out)
    print(out/'portrait-review.png')
