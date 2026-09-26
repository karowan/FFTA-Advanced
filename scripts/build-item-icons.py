"""Install the approved equipment icons for the 85 expansion weapons.

Bounded patch on the memory-fixes candidate:
- the 85 approved 16x16 native-palette icons (src/art/imagegen/
  new-item-icons-approved.json, published under artwork/items) are packed
  into one native icon container, decoded by the game's own 05318 decoder;
- the equipment icon draw pointer (literal 0CB984, previously the art stage's
  generated-axe dispatcher) goes to src/engine/item-icons.c, which draws item
  N's own icon at the established equipment-only callers and delegates every
  other caller and ID to that previous dispatcher.
Palette selection is unchanged; every icon uses its donor's native bank, and
the build checks that bank against the game's palette selector data.
Code and data go into blank ROM 0x1FE0000..0x1FEFFFF.
"""
import datetime, hashlib, json, struct, subprocess, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from PIL import Image
from native_art import pack_tiles
from native_miniatures import decode, encode

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/expansion/item-icons'
START,END=0x1fe0000,0x1ff0000
HOOK=0xcb984                      # equipment icon draw pointer (entry at 0CB980: ldr r3,[pc]; bx r3)
RECEIPT=ROOT/'src/art/imagegen/new-item-icons-approved.json'
SOURCES=['src/engine/item-icons.c','src/engine/item-icons.s']
sha=lambda raw:hashlib.sha256(raw).hexdigest()
u32=lambda b,p:struct.unpack_from('<I',b,p)[0]

def main():
    parent=Path(json.loads((ROOT/'build/expansion/memory-fixes/current.json').read_text())['manifest'])
    meta=json.loads(parent.read_text());original=Path(meta['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==meta['romSha1']
    assert original[START:END]==b'\xff'*(END-START),'Item icon reservation occupied'
    clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    art=meta['components']['equipment']['symbols']
    assert original[0xcb980:0xcb984]==bytes.fromhex('004b1847') and u32(original,HOOK)==art['ffta_art_equipment_entry']|1,'Equipment draw pointer changed'
    previous=art['ffta_art_equipment_draw']
    receipt=json.loads(RECEIPT.read_text(encoding='utf-8'));assert receipt['status']=='approved-for-release'
    drafts=ROOT/'src/art/imagegen/new-item-icon-drafts.json';assert sha(drafts.read_bytes())==receipt['draftRecordSha256']
    profiles={p['id']:p for p in json.loads((ROOT/'build/expansion/probes/content-data.json').read_text())['itemProfiles']}
    icons=[]
    assert [row['id'] for row in receipt['items']]==list(range(376,461))
    for row in receipt['items']:
        raw=(ROOT/row['path']).read_bytes();assert sha(raw)==row['sha256'],row['path']
        pixels=pack_tiles(Image.open(ROOT/row['path']),4);assert len(pixels)==128 and sha(pixels)==row['nativePixelsSha256'],row['id']
        donor=profiles[row['id']]['donor'];assert donor==row['donorIcon'],row['id']
        # The palette selector reads the donor's bank for these IDs (equipment.c).
        assert original[0x3c7fe4+donor*2+4]>>4==clean[0x3c7fe4+donor*2+4]>>4==row['paletteBank'],row['id']
        icons.append(pixels)
    assert len(set(icons))==85
    blob=encode(icons,size=128)
    out=OUT/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    (out/'item-icons-payload.h').write_text('static const unsigned char ffta_item_icon_container[]={'+','.join(str(v) for v in blob)+'};\n')
    linker=out/'item-icons.ld'
    linker.write_text('SECTIONS { .text 0x%08x : { *(.text*) *(.rodata*) } .unexpected : { *(.data*) *(.bss*) *(COMMON) } '
                      '/DISCARD/ : { *(.comment) *(.note*) *(.ARM.attributes) *(.ARM.exidx*) *(.ARM.extab*) } '
                      'ASSERT(SIZEOF(.text)<0x%x,"Item icon reservation overflow") ASSERT(SIZEOF(.unexpected)==0,"Unexpected persistent state") }\n'%(0x08000000+START,END-START))
    prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=out/'item-icons.elf';binary=out/'item-icons.bin'
    command=[prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib',
             '-Wl,-T,'+str(linker),'-Wl,-e,ffta_item_icon_entry','-I'+str(out),'-DFFTA_PREVIOUS_EQUIPMENT_DRAW='+hex(previous|1)+'u',
             *[str(ROOT/s) for s in SOURCES],'-o',str(elf)]
    subprocess.run(command,check=True)
    subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True)
    symbols={s[2]:int(s[0],16) for line in subprocess.check_output([prefix+'nm.exe','-n',str(elf)],text=True).splitlines() if len(s:=line.split())==3}
    code=binary.read_bytes();assert len(code)<END-START
    rom=bytearray(original);rom[START:START+len(code)]=code
    struct.pack_into('<I',rom,HOOK,symbols['ffta_item_icon_entry']|1)
    allowed=set(range(START,START+len(code)))|set(range(HOOK,HOOK+4))
    assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
    container=symbols['ffta_item_icon_container']-0x08000000
    assert all(decode(rom,container,i)==icons[i] for i in range(85))
    target=out/'FFTA_Reviewed_All_Classes.gba';target.write_bytes(rom)
    meta.update(path=str(target),romSha1=hashlib.sha1(rom).hexdigest(),romSha256=sha(rom))
    meta['itemIcons']=dict(parent=str(parent),baseSha1=hashlib.sha1(original).hexdigest(),reservation=[START,END],used=[START,START+len(code)],
        hook=dict(offset=HOOK,before=original[HOOK:HOOK+4].hex(),after=rom[HOOK:HOOK+4].hex()),previousDraw=previous,symbols=symbols,
        items=list(range(376,461)),containerSha256=sha(blob),receiptSha256=sha(RECEIPT.read_bytes()),
        sourceSha256={s:sha((ROOT/s).read_bytes()) for s in SOURCES},compileCommand=command)
    manifest=out/'candidate.json';manifest.write_text(json.dumps(meta,indent=2)+'\n')
    (OUT/'current.json').write_text(json.dumps(dict(manifest=str(manifest)))+'\n')
    print(json.dumps(dict(status='passed',manifest=str(manifest),romSha1=meta['romSha1'],codeBytes=len(code),icons=85)))

if __name__=='__main__':main()
