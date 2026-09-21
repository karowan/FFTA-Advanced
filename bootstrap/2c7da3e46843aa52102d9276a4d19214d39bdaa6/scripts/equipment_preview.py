"""Compile and apply the bounded native equipment-preview pagination module."""
import hashlib,json,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
START,END=0x1d00000,0x1d04000
HOOKS=((0x8e488,8,'ffta_preview_party_init'),(0x8e578,8,'ffta_preview_party_input'),
       (0x6aede,10,'ffta_preview_shop_init'),(0x6afb8,8,'ffta_preview_shop_input'),
       (0x6cf5a,10,'ffta_preview_sell_init'),(0x6d034,8,'ffta_preview_sell_input'))

def apply(rom,out,generated_portraits=False):
    out.mkdir(parents=True,exist_ok=True)
    clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    assert hashlib.sha1(clean).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
    assert rom[START:END]==b'\xff'*(END-START),'Equipment preview reservation occupied'
    for offset,size,name in HOOKS:assert rom[offset:offset+size]==clean[offset:offset+size],('Conflicting hook',name)
    # Keep the existing integrated decoder for every unowned job.
    assert rom[0xcb9e0:0xcb9e4]==bytes.fromhex('004b1847')
    original_icon=struct.unpack_from('<I',rom,0xcb9e4)[0]
    assert original_icon&1 and 0x08000000<=original_icon<0x0a000000
    if generated_portraits:
        from generated_menu_icons import compile_portraits
    else:
        from job_icon_art import compile_portraits
    portraits=compile_portraits(out)
    prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
    linker=out/'preview.ld'
    linker.write_text('SECTIONS { .text 0x09d00000 : { *(.text*) *(.rodata*) } .unexpected : { *(.data*) *(.bss*) *(COMMON) } /DISCARD/ : { *(.comment) *(.note*) *(.ARM.attributes) *(.ARM.exidx*) *(.ARM.extab*) } ASSERT(SIZEOF(.text)<0x4000,"Preview reservation overflow") ASSERT(SIZEOF(.unexpected)==0,"Unexpected persistent state") }\n')
    elf=out/'preview.elf';binary=out/'preview.bin'
    subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib',
                    '-Wl,-T,'+str(linker),'-Wl,-e,ffta_preview_party_init','-I'+str(out),'-DFFTA_ORIGINAL_ICON='+hex(original_icon)+'u',
                    str(ROOT/'src/engine/equipment-preview.c'),str(ROOT/'src/engine/equipment-preview-hooks.s'),'-lgcc','-o',str(elf)],check=True)
    subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True)
    symbols={}
    for line in subprocess.check_output([prefix+'nm.exe','-n',str(elf)],text=True).splitlines():
        parts=line.split()
        if len(parts)==3:symbols[parts[2]]=int(parts[0],16)
    blob=binary.read_bytes();rom[START:START+len(blob)]=blob
    changes=[]
    for offset,size,name in HOOKS:
        expected=bytes(rom[offset:offset+size]).hex()
        jump=offset
        if offset&3:
            struct.pack_into('<H',rom,offset,0xb408);jump+=2
        assert jump%4==0 and jump+8==offset+size
        struct.pack_into('<HHI',rom,jump,0x4b00,0x4718,symbols[name]|1)
        changes.append(dict(offset=offset,bytes=size,name=name,expected=expected))
    expected=rom[0xcb9e4:0xcb9e8].hex()
    struct.pack_into('<I',rom,0xcb9e4,symbols['ffta_icon_decode']|1)
    changes.append(dict(offset=0xcb9e4,bytes=4,name='original portrait dispatcher',expected=expected))
    return dict(reservation=[START,END],bytes=len(blob),symbols=symbols,changes=changes,persistentRAM=0,portraits=portraits,
                originalIconDecoder=original_icon,generatedPortraits=generated_portraits,
                scope='Paged party/buy/sell previews and temporary portraits. Actor animations and production visual acceptance remain open.')

if __name__=='__main__':
    base=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
    original=Path(base['path']).read_bytes();assert hashlib.sha1(original).hexdigest()==base['romSha1']
    out=ROOT/'build/art/equipment-preview';rom=bytearray(original)
    report=apply(rom,out)
    digest=hashlib.sha1(rom).hexdigest();artifact=out/digest;artifact.mkdir(exist_ok=True)
    path=artifact/'preview.gba';path.write_bytes(rom)
    report.update(path=str(path),romSha1=digest,baseRomSha1=base['romSha1'],source=base['path'])
    (artifact/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    (out/'current.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
