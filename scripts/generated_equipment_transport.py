"""Generated axe inventory/projectile icon dispatcher; held weapon art separate."""
import hashlib,json,struct,subprocess
from pathlib import Path
from PIL import Image
from native_art import ROOT,sha,palette,pack_tiles
from native_miniatures import decode,encode
START,END=0x1f80000,0x1f84000

def build(base_manifest=None, *, publish_current=True):
    parentpath=Path(base_manifest) if base_manifest else ROOT/'build/art/generated-status/current.json'
    parent=json.loads(parentpath.read_text());original=Path(parent['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==parent['romSha1']
    assert original[START:END]==b'\xff'*(END-START),'Equipment art reservation occupied'
    assert original[0xcb980:0xcb984]==bytes.fromhex('004b1847')
    entry=struct.unpack_from('<I',original,0xcb984)[0]&~1;p=entry-0x08000000
    assert original[p:p+16]==bytes.fromhex('72462b0070b56c466d46ed08ed00ad46'),'Established equipment ABI changed'
    lo,hi=struct.unpack_from('<HH',original,p+16);assert lo&0xf800==0xf000 and hi&0xf800==0xf800
    distance=((lo&2047)<<12)|((hi&2047)<<1)
    if distance&(1<<22):distance-=1<<23
    helper=entry+20+distance
    assert 0x08000000<=helper<0x0a000000
    root=ROOT/'build/art/generated-equipment';work=root/'compile';work.mkdir(parents=True,exist_ok=True)
    specpath=ROOT/'src/art/imagegen/axe-transport-prompts.json';spec=json.loads(specpath.read_text());source=ROOT/spec['source']
    assert sha(source.read_bytes())==spec['sourceSha256']
    im=Image.open(source).convert('RGBA');bounds=im.getchannel('A').point(lambda v:255 if v>=128 else 0).getbbox();assert bounds
    im=im.crop(bounds);im.thumbnail((16,16),Image.Resampling.NEAREST)
    bank=original[0x3c7fe4+52*2+4]>>4;assert bank==0
    pal,rgb=palette(original,0x419d60+bank*32)
    indexed=Image.new('P',(16,16));indexed.putpalette(rgb+[0]*(768-len(rgb)));indexed.info['transparency']=0
    dx=(16-im.width)//2;dy=(16-im.height)//2
    for y in range(im.height):
        for x in range(im.width):
            pixel=im.getpixel((x,y))
            if pixel[3]>=128:indexed.putpixel((dx+x,dy+y),min(range(1,16),key=lambda c:sum((pixel[k]-rgb[c*3+k])**2 for k in range(3))))
    raw=pack_tiles(indexed,4);assert raw!=decode(original,0x3c83fc,52) and any(raw)
    indexed.save(work/'axe-16.png',bits=4);blob=encode([raw],size=128)
    (work/'art-equipment-payload.h').write_text('static const unsigned char ffta_art_axe_container[]={'+','.join(str(v) for v in blob)+'};\n')
    linker=work/'equipment.ld';linker.write_text('SECTIONS { .text 0x09f80000 : { *(.text*) *(.rodata*) } .unexpected : { *(.data*) *(.bss*) *(COMMON) } /DISCARD/ : { *(.comment) *(.note*) *(.ARM.attributes) *(.ARM.exidx*) *(.ARM.extab*) } ASSERT(SIZEOF(.text)<0x4000,"Equipment art reservation overflow") ASSERT(SIZEOF(.unexpected)==0,"Unexpected persistent state") }\n')
    prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=work/'equipment.elf';binary=work/'equipment.bin'
    subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib',
        '-Wl,-T,'+str(linker),'-Wl,-e,ffta_art_equipment_entry','-I'+str(work),'-DFFTA_ORIGINAL_EQUIPMENT_DRAW='+hex(helper|1)+'u',
        str(ROOT/'src/engine/art-equipment-icons.c'),str(ROOT/'src/engine/art-equipment-icons.s'),'-o',str(elf)],check=True)
    subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True)
    symbols={s[2]:int(s[0],16) for line in subprocess.check_output([prefix+'nm.exe','-n',str(elf)],text=True).splitlines() if len(s:=line.split())==3}
    code=binary.read_bytes();assert len(code)<END-START
    rom=bytearray(original);rom[START:START+len(code)]=code;struct.pack_into('<I',rom,0xcb984,symbols['ffta_art_equipment_entry']|1)
    allowed=set(range(START,START+len(code)))|set(range(0xcb984,0xcb988));assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
    digest=hashlib.sha1(rom).hexdigest();out=root/digest;out.mkdir(parents=True,exist_ok=True);path=out/'FFTA_Generated_Equipment.gba';path.write_bytes(rom)
    result=dict(path=str(path),romSha1=digest,source=parent['path'],baseRomSha1=parent['romSha1'],releaseSource=parent['releaseSource'],reservation=[START,END],used=[START,START+len(code)],
        symbols=symbols,originalEntry=entry,originalHelper=helper,originalHelperSha256=sha(original[helper-0x08000000:helper-0x08000000+44]),
        sourceArt=spec['source'],sourceArtSha256=spec['sourceSha256'],promptSha256=sha(specpath.read_bytes()),paletteOffset=0x419d60,paletteBank=bank,paletteSha256=sha(pal),
        pixelsSha256=sha(raw),containerSha256=sha(blob),items=[*range(392,400),448,*range(453,461)],sourceBounds=list(bounds),scaled=list(im.size),persistentRAM=0,
        scope='Temporary generated axe16x16 icon at established equipment-only callers; generic quest IDs and all other equipment delegate unchanged. Native compressed decode. Actual held weapon/effect art and visual acceptance separate.')
    for p in ((out/'manifest.json',root/'current.json') if publish_current else (out/'manifest.json',)):p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(romSha1=digest,bytes=len(code),items=result['items'])));return result
if __name__=='__main__':build()
