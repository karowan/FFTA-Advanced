"""Independent Tomahawk impact atlas using generated temporary effect frames."""
import hashlib,json,struct,subprocess
from pathlib import Path
from PIL import Image
from native_art import ROOT,sha,pack_tiles
from native_effect_art import reference,literal_lz
START,END=0x1f88000,0x1f8c000
TABLE,HOOK=0x39d844,0xfe358
def build(base_manifest=None, *, publish_current=True):
    parent=json.loads((Path(base_manifest) if base_manifest else ROOT/'build/art/generated-weapon/current.json').read_text());original=Path(parent['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==parent['romSha1']
    clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();assert hashlib.sha1(clean).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
    assert original[START:END]==b'\xff'*(END-START)
    assert original[HOOK:HOOK+10]==clean[HOOK:HOOK+10]==bytes.fromhex('0449009350460190201c')
    assert original[TABLE:TABLE+48]==clean[TABLE:TABLE+48]
    r=reference(clean);root=ROOT/'build/art/generated-effect';work=root/'compile';work.mkdir(parents=True,exist_ok=True)
    specpath=ROOT/'src/art/imagegen/impact-transport-prompts.json';spec=json.loads(specpath.read_text());source=ROOT/spec['source']
    assert sha(source.read_bytes())==spec['sourceSha256'];im=Image.open(source).convert('RGBA')
    assert im.width==3*im.height and im.getextrema()[3][0]==0
    cells=[im.crop((i*im.height,0,(i+1)*im.height,im.height)) for i in range(3)]
    bounds=[c.getchannel('A').point(lambda v:255 if v>=128 else 0).getbbox() for c in cells];assert all(bounds)
    scale=24/max(max(b[2]-b[0],b[3]-b[1]) for b in bounds);rgb=r['palettes'][0]['rgb'];pixels=bytearray();converted=[]
    for index,(cell,box,frame) in enumerate(zip(cells,bounds,r['frames'])):
        crop=cell.crop(box);size=tuple(max(1,round(n*scale)) for n in crop.size);crop=crop.resize(size,Image.Resampling.NEAREST)
        indexed=Image.new('P',(24,24));indexed.putpalette(rgb+[0]*(768-len(rgb)));indexed.info['transparency']=0
        dx=(24-size[0])//2;dy=(24-size[1])//2
        for y in range(size[1]):
            for x in range(size[0]):
                v=crop.getpixel((x,y))
                if v[3]>=128:indexed.putpixel((dx+x,dy+y),min(range(1,4),key=lambda c:sum((v[k]-rgb[c*3+k])**2 for k in range(3))))
        indexed.save(work/f'impact-{index}.png',bits=4)
        for obj in frame['objects']:
            assert obj['tile']*32==len(pixels) and not obj['flipH'] and not obj['flipV']
            x,y=obj['x']+12,obj['y']+24;w,h=obj['width'],obj['height']
            assert 0<=x and 0<=y and x+w<=24 and y+h<=24
            pixels.extend(pack_tiles(indexed.crop((x,y,x+w,y+h)),w*h//64))
        converted.append(dict(bounds=list(box),scaled=list(size),pixelSha256=sha(indexed.tobytes())))
    assert len(pixels)==864 and bytes(pixels)!=r['pixels']
    rom=bytearray(original);cursor=START;segments=[]
    def add(data,kind):
        nonlocal cursor
        cursor=(cursor+3)&~3;p=cursor;cursor+=len(data);assert cursor<=END
        rom[p:cursor]=data;segments.append(dict(offset=p,bytes=len(data),sha256=sha(data),kind=kind));return p
    blob=bytes.fromhex('0402fd7f')+literal_lz(pixels);payload=add(blob,'generated impact4bpp LZ container')
    ref=add(struct.pack('<2I',payload+0x08000000,0),'private graphic reference')
    table=bytearray(original[TABLE:TABLE+48]);struct.pack_into('<I',table,16,ref+0x08000000)
    table_address=add(table,'Tomahawk-specific effect resource list')
    cursor=(cursor+3)&~3;entry=cursor
    asm=work/'effect.s';asm.write_text(f'''.syntax unified
.cpu arm7tdmi
.thumb
.global ffta_art_impact_entry
.thumb_func
ffta_art_impact_entry:
 ldrh r1,[r4,#16]
 ldr r0,=425
 cmp r1,r0
 ldr r1,=0x0839d844
 bne 1f
 ldr r1,={table_address+0x08000000}
1:
 str r3,[sp]
 mov r0,r10
 str r0,[sp,#4]
 ldr r0,=0x080fe361
 bx r0
.ltorg
''')
    prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=work/'effect.elf';binary=work/'effect.bin'
    subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-nostdlib','-Wl,-Ttext='+hex(entry+0x08000000),'-Wl,-e,ffta_art_impact_entry',str(asm),'-o',str(elf)],check=True)
    subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True)
    add(binary.read_bytes(),'action-specific native resource selector')
    rom[HOOK:HOOK+8]=struct.pack('<HHI',0x4800,0x4700,entry+0x08000001)
    assert all(a==b or START<=i<cursor or HOOK<=i<HOOK+8 for i,(a,b) in enumerate(zip(original,rom)))
    digest=hashlib.sha1(rom).hexdigest();out=root/digest;out.mkdir(parents=True,exist_ok=True);path=out/'FFTA_Generated_Impact.gba';path.write_bytes(rom)
    meta=dict(path=str(path),romSha1=digest,source=parent['path'],baseRomSha1=parent['romSha1'],releaseSource=parent['releaseSource'],
        reservation=[START,END],used=[START,cursor],hook=HOOK,entry=entry,payload=payload,reference=ref,table=table_address,originalTable=TABLE,
        pixelsSha256=sha(pixels),pixelsBytes=len(pixels),frames=converted,sourceArt=spec['source'],sourceArtSha256=spec['sourceSha256'],promptSha256=sha(specpath.read_bytes()),segments=segments,
        scope='Temporary generated Tomahawk425 primary impact atlas only; original Throw and every other action keep native resource list. Three24x24 images packed into original OAM27tile atlas; original timings/palette phases/native metadata preserved. Runtime/native acceptance and final art separate.')
    for p in ((out/'manifest.json',root/'current.json') if publish_current else (out/'manifest.json',)):p.write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps(dict(romSha1=digest,bytes=cursor-START,path=str(path))));return meta
if __name__=='__main__':build()
