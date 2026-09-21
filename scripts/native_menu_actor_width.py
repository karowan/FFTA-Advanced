"""Extend the two animated menu figure components to16-bit actor IDs.

Own the final16 bytes of the widget's existing4096-byte private arena by
reducing its native allocator extent to4080. The full ID lives at widget+1080;
neighboring native byte fields1084..108b retain their original layout.
The separate racial header extends only its manager allocation from16 to20
bytes; native list ownership and size-aware allocator teardown are retained.
"""
import struct,subprocess
from native_art import ROOT,sha

NARROW_PAIRS=((0x57496,0),(0x5752e,2),(0x60ecc,0),(0x60fc6,4),
              (0x65d94,0),(0x65e96,4),(0x2989c,0))

def apply(rom,arena,out):
    out.mkdir(parents=True,exist_ok=True);changes=[]
    def patch(offset,old,new,label):
        assert bytes(rom[offset:offset+len(old)])==old,('Menu width source drift',hex(offset),label)
        assert len(old)==len(new)
        rom[offset:offset+len(new)]=new
        changes.append(dict(offset=offset,bytes=len(new),before=old.hex(),after=new.hex(),purpose=label))
    for offset,reg in NARROW_PAIRS:
        bits=reg*9
        patch(offset,struct.pack('<2H',0x0600+bits,0x0e00+bits),struct.pack('<2H',0x0400+bits,0x0c00+bits),'preserve16-bit resource argument')
    patch(0x299aa,struct.pack('<2H',0x2180,0x0149),struct.pack('<2H',0x21ff,0x0109),'native private arena4096 to4080 bytes')
    for literal in (0x29a24,0x29b4c,0x29bcc,0x29cc8,0x29d1c):
        patch(literal,struct.pack('<I',0x1085),struct.pack('<I',0x1080),'owned full-width resource field')
    for offset,old in ((0x299f0,0x7809),(0x29b20,0x7800),(0x29bb0,0x7800),(0x29c9e,0x781a),(0x29cf8,0x7812)):
        patch(offset,struct.pack('<H',old),struct.pack('<H',old+0x1000),'load complete resource ID')
    # The racial header uses a different component. Give only its manager a
    # 20-byte allocation (native size16), and own the new halfword at+16.
    # All three state-driven rebuilds and the direct unit update read it.
    for offset,old in ((0x71826,'49190978'),(0x88984,'0c4bd1180978'),
                       (0x889de,'304bd1180978'),(0x88ae8,'364bd1180978')):
        before=bytes.fromhex(old)
        patch(offset,before,struct.pack('<H',0x8a01)+bytes.fromhex('c046')*((len(before)-2)//2),'header manager full ID read')
    assembly='''.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.global menu_create_id
.thumb_func
menu_create_id:
    adds r0,r4,r3
    mov r2,r8
    strb r2,[r0]
    push {r1}
    ldr r1,=0x1080
    adds r1,r4,r1
    strh r2,[r1]
    pop {r1}
    adds r3,#1
    ldr r0,=0x08029909
    bx r0
.ltorg
.align 2
.global menu_update_id
.thumb_func
menu_update_id:
    strh r2,[r1]
    adds r0,r1,#5
    strb r2,[r0]
    ldr r2,=0x1086
    adds r7,r4,r2
    strb r3,[r7]
    ldr r0,=0x08029c61
    bx r0
.ltorg
.align 2
.global header_create_manager
.thumb_func
header_create_manager:
    ldr r0,[r6]
    adds r0,r0,r4
    ldr r0,[r0]
    bl header_manager_allocate
    ldr r3,=0x0808895b
    bx r3
.ltorg
.align 2
.thumb_func
header_manager_allocate:
    push {r4,r5,lr}
    movs r5,r0
    ldr r0,[r5]
    movs r1,#20
    bl native_alloc
    movs r4,r0
    ldr r0,=0x0836d4b8
    ldr r2,[r0]
    movs r0,r4
    movs r1,#20
    bl native_fill
    ldr r0,[r5]
    bl native_list_create
    str r0,[r4,#4]
    str r5,[r4,#8]
    ldr r0,[r5,#4]
    movs r1,r4
    bl native_list_add
    ldr r0,=0x03002818
    ldr r0,[r0]
    ldr r1,=0x434
    adds r0,r0,r1
    ldrb r0,[r0]
    strh r0,[r4,#16]
    movs r0,r4
    pop {r4,r5}
    pop {r1}
    bx r1
.ltorg
.align 2
.global header_store_id
.thumb_func
header_store_id:
    ldr r1,[r7]
    ldr r5,=0x434
    adds r1,r1,r5
    strb r0,[r1]
    ldr r3,[r1,#16]
    strh r0,[r3,#16]
    ldr r3,=0x0807180d
    bx r3
.ltorg
.align 2
.thumb_func
native_alloc:
    ldr r3,=0x08007139
    bx r3
.thumb_func
native_fill:
    ldr r3,=0x0814224d
    bx r3
.thumb_func
native_list_create:
    ldr r3,=0x080c799d
    bx r3
.thumb_func
native_list_add:
    ldr r3,=0x080c7a75
    bx r3
.ltorg
'''
    (out/'width.s').write_text(assembly)
    base=(arena.cursor+3)&~3;prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
    subprocess.run([prefix+'as.exe','-mcpu=arm7tdmi','-mthumb',str(out/'width.s'),'-o',str(out/'width.o')],check=True)
    subprocess.run([prefix+'ld.exe','-Ttext',hex(0x08000000+base),'-e','menu_create_id',str(out/'width.o'),'-o',str(out/'width.elf')],check=True)
    subprocess.run([prefix+'objcopy.exe','-O','binary',str(out/'width.elf'),str(out/'width.bin')],check=True)
    symbols={}
    for line in subprocess.check_output([prefix+'nm.exe','-n',str(out/'width.elf')],text=True).splitlines():
        values=line.split()
        if len(values)==3:symbols[values[2]]=int(values[0],16)
    blob=(out/'width.bin').read_bytes();assert arena.add(blob,'menu-width-hooks')==base
    for offset,expected,name in [(0x29900,bytes.fromhex('e018424602700133'),'menu_create_id'),
                                 (0x29c58,bytes.fromhex('0a701c4aa7183b70'),'menu_update_id')]:
        patch(offset,expected,struct.pack('<HHI',0x4800,0x4700,symbols[name]|1),name)
    patch(0x88950,bytes.fromhex('30680019006899f7e1f8'),
          struct.pack('<HHI',0x4800,0x4700,symbols['header_create_manager']|1)+bytes.fromhex('c046'),'header-only extended manager allocation')
    patch(0x71804,bytes.fromhex('39681e4d49190870'),
          struct.pack('<HHI',0x4b00,0x4718,symbols['header_store_id']|1),'header full ID store with legacy byte mirror')
    return dict(changes=changes,symbols=symbols,codeSha256=sha(blob),field=0x1080,
        arenaStart=0x84,arenaBytes=0xff0,reserved=[0x1074,0x1084],
        headerManagerBytes=20,headerResourceField=16,
        scope='Generic figure arena-owned ID; racial header owns an extended manager and retains ID through direct update and state rebuilds. Runtime acceptance required.')
