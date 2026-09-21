"""Diagnostic private native text-call trace while opening battle Status."""
import pathlib,runpy,struct,subprocess,json,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'build/expansion/probes';F=P/'status-display';OUT=F/'text-trace';OUT.mkdir(exist_ok=True)
source=P/'grace/f7eb5f98b32d1c3d4c61b49782b9f5ade598e87a/grace.gba'
rom=bytearray(source.read_bytes())
asm='''.syntax unified
.cpu arm7tdmi
.thumb
.global entry
.thumb_func
entry:
 push {r0-r4}
 ldr r0,=0x0203ff20
 ldr r1,[r0]
 cmp r1,#64
 bhs done
 adds r2,r1,#1
 str r2,[r0]
 movs r0,#20
 muls r1,r0
 ldr r0,=0x0203f800
 adds r1,r1,r0
 mov r2,lr
 str r2,[r1]
 ldr r2,[sp]
 str r2,[r1,#4]
 ldr r2,[sp,#4]
 str r2,[r1,#8]
 ldr r2,[sp,#8]
 str r2,[r1,#12]
 ldr r2,[sp,#12]
 str r2,[r1,#16]
done:
 pop {r0-r4}
 push {r4-r7,lr}
 mov r7,r10
 mov r6,r9
 mov r5,r8
 ldr r3,=0x08015119
 bx r3
.ltorg
'''
# r3 is live on entry: route the replay jump through LR, preserving it.
asm=asm.replace(' ldr r3,=0x08015119\n bx r3',' push {r0}\n ldr r0,=0x08015119\n mov lr,r0\n pop {r0}\n bx lr')
(OUT/'trace.s').write_text(asm);prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-nostdlib','-Wl,-Ttext=0x09180000,-e,entry',str(OUT/'trace.s'),'-o',str(OUT/'trace.elf')],check=True)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(OUT/'trace.elf'),str(OUT/'trace.bin')],check=True)
code=(OUT/'trace.bin').read_bytes();assert rom[0x1180000:0x1180000+len(code)]==b'\xff'*len(code);rom[0x1180000:0x1180000+len(code)]=code
assert rom[0x15110:0x15118].hex()=='f0b557464e464546';struct.pack_into('<HHI',rom,0x15110,0x4b00,0x4718,0x09180001)
# Entry veneer clobbers r3. Preserve original r3 in r12 across the jump.
# Instead use a12-byte push veneer, replay additionally push/sub instructions.
asm=asm.replace('entry:\n push', 'entry:\n pop {r3}\n push').replace(' push {r0}\n ldr r0,=0x08015119', ' push {r5-r7}\n sub sp,#0x30\n push {r0}\n ldr r0,=0x0801511d')
(OUT/'trace.s').write_text(asm)
subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-nostdlib','-Wl,-Ttext=0x09180000,-e,entry',str(OUT/'trace.s'),'-o',str(OUT/'trace.elf')],check=True)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(OUT/'trace.elf'),str(OUT/'trace.bin')],check=True)
code=(OUT/'trace.bin').read_bytes();rom[0x1180000:0x1180000+len(code)]=code;struct.pack_into('<HHHHI',rom,0x15110,0xb408,0x46c0,0x4b00,0x4718,0x09180001)
if '--equipment' in sys.argv:
 rom[0x15110:0x1511c]=source.read_bytes()[0x15110:0x1511c]
 asm=asm.replace('0x0801511d','0x08074915').replace('sub sp,#0x30','sub sp,#0x10')
 (OUT/'trace.s').write_text(asm)
 subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-nostdlib','-Wl,-Ttext=0x09180000,-e,entry',str(OUT/'trace.s'),'-o',str(OUT/'trace.elf')],check=True)
 subprocess.run([prefix+'objcopy.exe','-O','binary',str(OUT/'trace.elf'),str(OUT/'trace.bin')],check=True)
 code=(OUT/'trace.bin').read_bytes();rom[0x1180000:0x1180000+len(code)]=code
 struct.pack_into('<HHHHI',rom,0x74908,0xb408,0x46c0,0x4b00,0x4718,0x09180001)
(OUT/'trace.gba').write_bytes(rom);h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'));e=h['Emulator'](OUT/'trace.gba')
try:
 e.load(F/'key-256.state');e.set_memory(0x3f800,bytes(0x730));e.run(8,256);e.run(180);e.screenshot(OUT/'status.png');ram=e.memory()
 rows=[struct.unpack_from('<5I',ram,0x3f800+20*i) for i in range(min(64,struct.unpack_from('<I',ram,0x3ff20)[0]))]
 (OUT/'calls.json').write_text(json.dumps([[hex(v) for v in row] for row in rows],indent=2));print((OUT/'calls.json').read_text())
finally:e.close()
