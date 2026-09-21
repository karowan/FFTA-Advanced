"""Native dictionary-compressed menu figures; private extraction and rebuild.

Derived from USA05318/051c4. No artwork is authored here.
"""
import hashlib,json,struct
from pathlib import Path
from native_art import ROOT,palette,tile_image,pack_tiles,sha

CONTAINER=0x3b5a5c
LITERALS=(0x87bd8,0x87c58,0x87d90)

def decode(rom,base,index):
    assert rom[base:base+2]==b'A7'
    count=int.from_bytes(rom[base+2:base+4],'big')
    assert 0<=index<count
    dictionary=base+int.from_bytes(rom[base+4:base+8],'big')
    kind,bits=rom[dictionary:dictionary+2]
    assert kind in (0,3) and 0<=bits<=7
    size=int.from_bytes(rom[dictionary+2:dictionary+4],'big') if kind==0 else None
    data=dictionary+(4 if kind==0 else 2)
    cursor=base+int.from_bytes(rom[base+8+index*4:base+12+index*4],'big')
    if kind==3:size=int.from_bytes(rom[cursor:cursor+2],'big');cursor+=2
    assert 0<size<=0x10000
    result=bytearray();mask=0xffff>>(bits+1)
    while len(result)<size:
        token=rom[cursor];cursor+=1
        if token&128:
            n=(token&127)+1
            result.extend(rom[cursor:cursor+n]);cursor+=n
        else:
            n=(token>>(7-bits))+3
            offset=((token<<8)|rom[cursor])&mask;cursor+=1
            assert data+offset+n<=len(rom)
            result.extend(rom[data+offset:data+offset+n])
        assert len(result)<=size
    return bytes(result)

def encode(images,size=640):
    assert 0<len(images)<256 and 0<size<=65535 and all(len(v)==size for v in images)
    blob=bytearray(b'A7'+len(images).to_bytes(2,'big')+bytes(4+4*len(images)))
    for i,raw in enumerate(images):
        blob[8+i*4:12+i*4]=len(blob).to_bytes(4,'big')
        for start in range(0,len(raw),128):
            part=raw[start:start+128];blob.append(0x80|len(part)-1);blob.extend(part)
    blob[4:8]=len(blob).to_bytes(4,'big')
    blob.extend(bytes((0,5))+size.to_bytes(2,'big'))
    for i,raw in enumerate(images):assert decode(blob,0,i)==raw
    return bytes(blob)

def export():
    rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    assert hashlib.sha1(rom).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
    count=int.from_bytes(rom[CONTAINER+2:CONTAINER+4],'big')
    images=[decode(rom,CONTAINER,i) for i in range(count)]
    assert count==54 and all(len(v)==640 for v in images)
    out=ROOT/'build/art/native-reference/miniatures';out.mkdir(parents=True,exist_ok=True)
    _,rgb=palette(rom,0x419d80)
    records=[]
    for i,raw in enumerate(images):
        image=tile_image(raw,rgb,32)
        assert pack_tiles(image,20)==raw
        image.save(out/f'image-{i:02}.png',bits=4)
        raw_path=out/f'image-{i:02}.4bpp';raw_path.write_bytes(raw)
        records.append(dict(index=i,sha256=sha(raw),bytes=len(raw),size=list(image.size)))
    encoded=encode(images);(out/'unchanged-container.bin').write_bytes(encoded)
    report=dict(sourceSha1=hashlib.sha1(rom).hexdigest(),count=count,records=records,encodedSha256=sha(encoded),
                scope='Static54-entry dictionary decode/literal encode/indexed image roundtrip. Native decoder and rendered consumer acceptance pending; preview uses one reference palette only.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(count=count,encodedBytes=len(encoded),out=str(out))))

if __name__=='__main__':export()
