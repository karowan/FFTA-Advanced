"""Native8bpp portrait archives, compression, OAM and palette references.

Independent of the4bpp actor and640-byte miniature consumers. Original assets
remain private; this module decodes/re-packs bytes without authoring artwork.
"""
import json,struct
from PIL import Image
from native_art import ROOT,SHAPES,sha

PIXELS,LAYOUTS=0x3e105c,0x417f88
PIXEL_LITERALS=(0xcb828,0xcb864,0xcb88c,0xcb8d0)
LAYOUT_LITERALS=(0xcb948,0xcb97c)
PALETTES=(0x3d5a1c,0x3d965c,0x3dd360)
PALETTE_LITERALS=(0xcb924,0xcb910,0xcb900)

def entry(data,base,index):
    width,count=struct.unpack_from('<HH',data,base)
    assert width in (2,4) and 0<=index<count
    offset=int.from_bytes(data[base+4+width*index:base+4+width*(index+1)],'little')
    p=base+4+offset
    assert 0<=p<len(data)
    return p

def decode(data,start):
    size=int.from_bytes(data[start:start+4],'big');assert 0<size<=0x10000
    p=start+4;out=bytearray()
    while len(out)<size:
        token=data[p];p+=1
        distance=None
        if token&128:
            count=((token>>3)&15)+3;distance=((token&7)<<8|data[p])+1;p+=1
        elif token&64:
            count=(token&63)+1;out.extend(data[p:p+count]);p+=count
        elif token&32:
            count=(token&31)+2;out.extend(bytes(count))
        elif token&16:
            high=data[p];low=data[p+1];p+=2
            count=((token&15)|((high>>2)&48))+4;distance=((high&63)<<8|low)+1
        elif token==0:
            count=data[p]+5;distance=(data[p+1]<<8|data[p+2])+1;p+=3
        elif token in (1,2):
            count=data[p]+3;p+=1;out.extend(bytes([255 if token==1 else 0])*count)
        else:raise ValueError(('Unsupported portrait token',token,hex(p-1)))
        if distance is not None:
            assert 0<distance<=len(out)
            for _ in range(count):out.append(out[-distance])
        assert len(out)<=size and p<=len(data)
    return bytes(out),p

def encode(raw):
    out=bytearray(len(raw).to_bytes(4,'big'))
    for i in range(0,len(raw),64):
        part=raw[i:i+64];out.append(64|len(part)-1);out.extend(part)
    assert decode(out,0)[0]==raw
    return bytes(out)

def archive(records,width):
    assert width in (2,4) and len(records)<=65535
    out=bytearray(struct.pack('<HH',width,len(records))+bytes(width*len(records)))
    for i,raw in enumerate(records):
        while len(out)%4:out.append(0)
        offset=len(out)-4;assert offset<1<<(8*width)
        out[4+width*i:4+width*(i+1)]=offset.to_bytes(width,'little');out.extend(raw)
    return bytes(out)

def layout(data,p):
    count=struct.unpack_from('<H',data,p)[0];assert 0<count<=128
    result=[]
    for i in range(count):
        a,b,c=struct.unpack_from('<3H',data,p+2+i*6)
        assert a&0x2000 and not a&0x100 and a>>14<3,'Expected non-affine8bpp portrait'
        w,h=SHAPES[a>>14][b>>14];x=b&511;y=a&255
        result.append(dict(attributes=[a,b,c],x=x-512 if x>=256 else x,y=y-256 if y>=128 else y,
            width=w,height=h,tile=c&1023,flipH=bool(b&4096),flipV=bool(b&8192)))
    return result,data[p:p+2+count*6]

def pack(image):
    assert image.mode=='P' and image.width%8==image.height%8==0
    out=bytearray()
    for y in range(0,image.height,8):
        for x in range(0,image.width,8):out.extend(image.crop((x,y,x+8,y+8)).tobytes())
    return bytes(out)

def compose(raw,objects,colors):
    image=Image.new('P',(128,96));image.putpalette(colors)
    for obj in reversed(objects):
        w,h=obj['width'],obj['height'];part=Image.new('P',(w,h));part.putpalette(colors)
        for y in range(h//8):
            for x in range(w//8):
                p=obj['tile']*32+(y*(w//8)+x)*64
                block=raw[p:p+64];assert len(block)==64
                tile=Image.frombytes('P',(8,8),block);tile.putpalette(colors);part.paste(tile,(x*8,y*8))
        if obj['flipH']:part=part.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if obj['flipV']:part=part.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        mask=Image.frombytes('L',part.size,part.tobytes()).point(lambda v:255 if v else 0)
        image.paste(part,(64+obj['x'],80+obj['y']),mask)
    image.info['transparency']=0
    return image

def export():
    from native_miniatures import decode as decode_palette
    data=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    import hashlib
    assert hashlib.sha1(data).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
    out=ROOT/'build/art/native-reference/portraits';out.mkdir(parents=True,exist_ok=True);records=[]
    for i in range(103):
        p=entry(data,PIXELS,i);raw,end=decode(data,p);objects,oam=layout(data,entry(data,LAYOUTS,i))
        assert max(v['tile']*32+v['width']*v['height'] for v in objects)<=len(raw)
        (out/f'portrait-{i:03}.8bpp').write_bytes(raw);(out/f'portrait-{i:03}.oam').write_bytes(oam)
        records.append(dict(index=i,source=p,compressedBytes=end-p,decodedBytes=len(raw),sha256=sha(raw),oamSha256=sha(oam),
            indices=sorted(set(raw)),objects=objects))
    palettes=[]
    for mode,base in enumerate(PALETTES):
        for i in range(165):
            raw=decode_palette(data,base,i);assert len(raw)==96
            (out/f'palette-{mode}-{i:03}.bin').write_bytes(raw);palettes.append(dict(mode=mode,index=i,sha256=sha(raw)))
    report=dict(sourceSha256=sha(data),records=records,palettes=palettes,
        scope='Private103-portrait8bpp/OAM export and495 palette variants. Native decode/import/runtime proof remains separate.')
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(portraits=len(records),palettes=len(palettes),indices=sorted(set(v for r in records for v in r['indices'])),out=str(out))))
    return report

if __name__=='__main__':export()
