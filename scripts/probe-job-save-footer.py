"""Disposable native flash footer experiment; not production persistence.

Build a private hook that temporarily supplies a known footer during the
native synchronous flash transaction, then restores its source tail. Replay
normal Save Now and check native CRC and footer contents in the actual flash.
"""
import hashlib,json,pathlib,runpy,struct,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text())
source=pathlib.Path(meta['path']);base=source.read_bytes()
assert hashlib.sha1(base).hexdigest()==meta['romSha1']
OUT=ROOT/'build/expansion/probes/job-save-footer'/meta['romSha1']
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'footer.c').write_text('''#include <stdint.h>
extern unsigned original_save(unsigned,uint8_t *);
unsigned footer_save(unsigned slot,uint8_t *source) {
    if(slot!=2 || !source)return original_save(slot,source);
    uint8_t saved[608];
    for(unsigned i=0;i<608;i++)saved[i]=source[0x3ca8+i];
    for(unsigned i=0;i<608;i++)source[0x3ca8+i]=(uint8_t)(i*37+11);
    source[0x3ca8]='F';source[0x3ca9]='F';source[0x3caa]='J';source[0x3cab]='S';
    unsigned result=original_save(slot,source);
    for(unsigned i=0;i<608;i++)source[0x3ca8+i]=saved[i];
    return result;
}
''')
(OUT/'footer.s').write_text('''.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global footer_entry
.thumb_func
footer_entry:
 pop {r3}
 push {r4,lr}
 mov r4,sp
 mov r3,sp
 lsrs r3,r3,#3
 lsls r3,r3,#3
 mov sp,r3
 bl footer_save
 mov sp,r4
 pop {r4}
 pop {r3}
 bx r3
.align 2
.global original_save
.thumb_func
original_save:
 push {r4-r7,lr}
 mov r7,r10
 mov r6,r9
 mov r5,r8
 push {r5-r7}
 sub sp,#0x34
 ldr r3,=0x0813b2b5
 bx r3
.ltorg
''')
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
elf=OUT/'footer.elf';binary=OUT/'footer.bin'
subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11',
 '-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib',
 '-Wl,-Ttext=0x091d0000,-e,footer_entry',str(OUT/'footer.c'),str(OUT/'footer.s'),
 '-lgcc','-o',str(elf)],check=True)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True)
symbols={p[2]:int(p[0],16) for line in subprocess.check_output([prefix+'nm.exe','-n',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
rom=bytearray(base);code=binary.read_bytes();assert rom[0x11d0000:0x11d0000+len(code)]==b'\xff'*len(code)
rom[0x11d0000:0x11d0000+len(code)]=code
assert rom[0x13b2a8:0x13b2b4]==bytes.fromhex('f0b557464e464546e0b48db0')
rom[0x13b2a8:0x13b2b4]=bytes.fromhex('08b4c046004b1847')+struct.pack('<I',symbols['footer_entry']|1)
ROM=OUT/'footer.gba';ROM.write_bytes(rom)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
menu=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
fixture=source.parent/'blade-ward-game/counter-1-ward.state'
assert fixture.is_file()
def tap(e,k,wait=180):e.run(8,k);e.run(wait)
e=E(ROM)
try:
 e.load(fixture);e.run(1);tap(e,256,900);menu['wait_for_menu'](e,limit=9000)
 for k in (1,8,16,256,256):tap(e,k)
 before=e.memory();old=e.memory(0);e.save(OUT/'before.state')
 tap(e,256,300);saved=e.memory(0);after=e.memory()
 assert saved!=old,'Save Now made no flash change'
 (OUT/'saved.sav').write_bytes(saved);e.save(OUT/'saved.state')
 (OUT/'before.ram').write_bytes(before);(OUT/'after.ram').write_bytes(after)
finally:e.close()
expected=bytearray((i*37+11)&255 for i in range(608));expected[:4]=b'FFJS'
hits=[]
for sector in range(16):
 off=sector*4096+0xca8
 if saved[off:off+608]==expected:hits.append(sector)
assert len(hits)==1,('Expected one native flash footer',hits)
# Normal native Resume Battle must still pass its original checksum.
e=E(ROM)
try:
 e.set_memory(0,saved,0);e.run(3600)
 for k,wait in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):tap(e,k,wait)
 menu['wait_for_menu'](e,limit=9000);e.save(OUT/'resumed.state')
 assert e.memory()[0x1b40:0x1e70]==after[0x1b40:0x1e70],'Native AP changed on cold resume'
finally:e.close()
report=dict(passed=True,baseSha1=meta['romSha1'],romSha1=hashlib.sha1(rom).hexdigest(),
 footerSectors=hits,footerBytes=608,sourceFixtureSha256=hashlib.sha256(fixture.read_bytes()).hexdigest(),
 scope='Experiment only: actual native flash footer transport and native checksum cold resume. No status API enabled.')
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
