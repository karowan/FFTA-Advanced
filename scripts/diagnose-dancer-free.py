"""Trap invalid native frees during the fixed Counter Rhythm preview."""
import pathlib,json,struct,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-reaction-playback.py';code=source.read_text();ns={'__file__':str(source),'__name__':'dancer_free_diagnostic'}
exec(compile(code.split('for lesson,job,race,weapon,hidden in ')[0],str(source),'exec'),ns)
out=ns['OUT']/'free-diagnostic';out.mkdir(exist_ok=True)
original=struct.unpack_from('<I',ns['image'],0x7174)[0]
assert ns['image'][0x7170:0x7174]==bytes.fromhex('004b1847')
(out/'watch.c').write_text('''#include <stdint.h>
extern void original_free(unsigned,unsigned);
void watched_free(unsigned heap,unsigned pointer,unsigned caller){
 if(!pointer || ((pointer&0xff000000u)==0x02000000u && (pointer&0x3ffffu)>=0x3ea00u)){
  volatile unsigned *log=(volatile unsigned *)0x0203f220u;
  log[0]=0x46524545;log[1]=heap;log[2]=pointer;log[3]=caller;
  unsigned sp;__asm__ volatile("mov %0, sp":"=r"(sp));log[4]=sp;
  for(unsigned i=0;i<32;i++)log[5+i]=((const unsigned *)sp)[i];
  for(;;)__asm__ volatile("nop");
 }
 original_free(heap,pointer);
}
''')
(out/'watch.s').write_text('''.syntax unified
.cpu arm7tdmi
.thumb
.section .text.entry,"ax"
.global watched_entry
.thumb_func
watched_entry:
 mov r2,lr
 b watched_free
.text
.global original_free
.thumb_func
original_free:
 ldr r3,=ORIGINAL
 bx r3
.ltorg
'''.replace('ORIGINAL',hex(original)))
(out/'watch.ld').write_text('SECTIONS { . = 0x093ef000; .text : { *(.text.entry) *(.text*) *(.rodata*) } /DISCARD/ : { *(.comment) *(.ARM.attributes) } }')
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-ffreestanding','-nostdlib','-Wl,-T,'+str(out/'watch.ld'),str(out/'watch.c'),str(out/'watch.s'),'-o',str(out/'watch.elf')],check=True,capture_output=True)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(out/'watch.elf'),str(out/'watch.bin')],check=True)
image=bytearray(ns['TEST_ROM'].read_bytes());blob=(out/'watch.bin').read_bytes()
assert image[0x7170:0x7174]==bytes.fromhex('004b1847')
assert image[0x13ef000:0x13ef000+len(blob)]==b'\xff'*len(blob)
image[0x13ef000:0x13ef000+len(blob)]=blob;struct.pack_into('<HHI',image,0x7170,0x4b00,0x4718,0x093ef001)
compact='--compact-name' in ns['sys'].argv
if compact:
 registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
 content=json.loads((ROOT/'build/expansion/probes/content-data.json').read_text())
 lesson=next(l for l in registry['lessons'] if l['id']=='DNC-R2')
 at=struct.unpack_from('<I',image,content['addresses']['others']-0x08000000+4*lesson['nameId'])[0]-0x08000000
 label=bytes(x for c in 'Rhythm' for x in (0x80,0xb0+ord(c)-65 if c.isupper() else 0xca+ord(c)-97))+b'\0'
 image[at:at+len(label)]=label
trial=out/'watch.gba';trial.write_bytes(image);ns['TEST_ROM']=trial;ns['cases']=[('DNC-R2',124,4,416,442)]
body=code[code.index('for lesson,job,race,weapon,hidden in '):code.index('        for seed in ')]
body=body.replace('for enabled in (False,True):','for enabled in (True,):')
if compact:body=body.replace("if lesson=='DNC-R2' and enabled:tap(e,256)","if False:tap(e,256)")
error=None
try:exec(compile(body,str(source),'exec'),ns)
except AssertionError as ex:error=str(ex)
ram=(ns['OUT']/('menu-failure.ram' if error and 'menu timeout' in error else 'DNC-R2-on/confirmation.ram')).read_bytes()
log=struct.unpack_from('<37I',ram,0x3f220)
report=dict(compactName=compact,error=error,trap=hex(log[0]),heap=hex(log[1]),pointer=hex(log[2]),caller=hex(log[3]),sp=hex(log[4]),stack=[hex(x) for x in log[5:]])
(out/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
