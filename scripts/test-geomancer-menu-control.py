"""Fixed cold-resume menu inputs; observation only, no supplied game result."""
import pathlib,json,hashlib,runpy,struct,ctypes as C,sys,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
rom=pathlib.Path(meta['path']);assert hashlib.sha1(rom.read_bytes()).hexdigest()==meta['romSha1']
source=rom.parent/'geomancer-field-lifecycle/380/occupied/cold-resumed.state'
OUT=rom.parent/'geomancer-menu-control';OUT.mkdir(exist_ok=True)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
menu=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))['menu_visible']
w=lambda b,p:struct.unpack_from('<I',b,p)[0]
if '--free-control' in sys.argv:
 data=bytearray(rom.read_bytes());assert data[0x7170:0x7174]==bytes.fromhex('004b1847')
 original=w(data,0x7174)
 (OUT/'free.c').write_text('''#include <stdint.h>
 void watched(unsigned heap,unsigned pointer,unsigned caller){
  unsigned end=heap+8+4u*(*(uint16_t *)(heap+6));
  if(!pointer || pointer<heap+20 || pointer>end-4 || *(uint16_t *)(pointer-8)!=0x616c){
   volatile unsigned *log=(volatile unsigned *)0x0203ff50u;
   log[1]=heap;log[2]=pointer;log[3]=caller;
   unsigned sp;__asm__ volatile("mov %0, sp":"=r"(sp));log[4]=sp;
   for(unsigned i=0;i<32;i++)log[5+i]=((const unsigned *)sp)[i];
   log[0]=0x46524545;for(;;)__asm__ volatile("nop");
  }
  ((void (*)(unsigned,unsigned))ORIGINAL)(heap,pointer);
 }
 '''.replace('ORIGINAL',hex(original)+'u'),encoding='utf-8')
 (OUT/'free.s').write_text('''.syntax unified
 .cpu arm7tdmi
 .thumb
 .section .text.entry,"ax"
 .global entry
 .thumb_func
 entry:
  mov r2,lr
  b watched
 ''',encoding='utf-8')
 (OUT/'free.ld').write_text('SECTIONS { . = 0x093ef000; .text : { *(.text.entry) *(.text*) *(.rodata*) } }')
 prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
 subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-ffreestanding','-nostdlib','-Wl,-T,'+str(OUT/'free.ld'),str(OUT/'free.c'),str(OUT/'free.s'),'-o',str(OUT/'free.elf')],check=True,capture_output=True)
 subprocess.run([prefix+'objcopy.exe','-O','binary',str(OUT/'free.elf'),str(OUT/'free.bin')],check=True)
 blob=(OUT/'free.bin').read_bytes();assert data[0x13ef000:0x13ef000+len(blob)]==b'\xff'*len(blob)
 data[0x13ef000:0x13ef000+len(blob)]=blob;struct.pack_into('<I',data,0x7174,0x093ef001)
 trial=OUT/'free.gba';trial.write_bytes(data);e=E(trial)
 try:
  e.load(source);e.set_memory(0x3ff50,bytes(160));turns=0
  for turns in range(12):
   r=e.memory();previous=w(r,w(r,0xf438)-0x02000000+24)
   for key in (32,32,256,256):e.run(8,key);e.run(180)
   for elapsed in range(0,9001,10):
    r=e.memory()
    if w(r,0x3ff50)==0x46524545:break
    if menu(e) and w(r,w(r,0xf438)-0x02000000+24)!=previous:break
    if elapsed<9000:e.run(10)
   if w(r,0x3ff50)==0x46524545 or elapsed==9000:break
  log=struct.unpack_from('<37I',r,0x3ff50);e.save(OUT/'free-trap.state')
  report=dict(romSha1=meta['romSha1'],instrumentedSha1=hashlib.sha1(data).hexdigest(),inputSha1=hashlib.sha1(source.read_bytes()).hexdigest(),turns=turns,
    trap=hex(log[0]),heap=hex(log[1]),pointer=hex(log[2]),caller=hex(log[3]),sp=hex(log[4]),stack=[hex(v) for v in log[5:]])
  (OUT/'free-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
 finally:e.close()
 sys.exit(0)
if '--allocation-control' in sys.argv:
 (OUT/'allocation.c').write_text('''#include <stdint.h>
 unsigned watched(unsigned bytes,unsigned caller){
  unsigned result=((unsigned (*)(unsigned,unsigned))0x08007139u)(*(unsigned *)0x0200f434u,bytes);
  if(!result && (caller<0x09360000u || caller>=0x09380000u)){volatile unsigned *log=(volatile unsigned *)0x0203ff50u;
   unsigned n=log[0]++;if(n<12){log[1+3*n]=bytes;log[2+3*n]=caller;log[3+3*n]=*(volatile uint8_t *)0x02009198u;}
   unsigned manager=*(unsigned *)0x0200f4b0u,pool=*(unsigned *)(manager+0x438);
   log[38]=pool?*(unsigned *)(pool+12):0;
   for(;;)__asm__ volatile("nop");}
  return result;
 }
 ''',encoding='utf-8')
 (OUT/'allocation.s').write_text('''.syntax unified
 .cpu arm7tdmi
 .thumb
 .section .text.entry,"ax"
 .global entry
 .thumb_func
 entry:
  mov r1,lr
  b watched
 ''',encoding='utf-8')
 (OUT/'allocation.ld').write_text('SECTIONS { . = 0x093ef000; .text : { *(.text.entry) *(.text*) *(.rodata*) } }')
 prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
 subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-ffreestanding','-nostdlib','-Wl,-T,'+str(OUT/'allocation.ld'),str(OUT/'allocation.c'),str(OUT/'allocation.s'),'-o',str(OUT/'allocation.elf')],check=True,capture_output=True)
 subprocess.run([prefix+'objcopy.exe','-O','binary',str(OUT/'allocation.elf'),str(OUT/'allocation.bin')],check=True)
 data=bytearray(rom.read_bytes());blob=(OUT/'allocation.bin').read_bytes()
 assert data[0x22840:0x22848]==bytes.fromhex('00b5011c02480068')
 assert data[0x13ef000:0x13ef000+len(blob)]==b'\xff'*len(blob)
 data[0x13ef000:0x13ef000+len(blob)]=blob;struct.pack_into('<HHI',data,0x22840,0x4b00,0x4718,0x093ef001)
 trial=OUT/'allocation.gba';trial.write_bytes(data);e=E(trial)
 try:
  e.load(source);e.set_memory(0x3ff50,bytes(160))
  for turn in range(12):
   r=e.memory();previous=w(r,w(r,0xf438)-0x02000000+24)
   for key in (32,32,256,256):e.run(8,key);e.run(180)
   for elapsed in range(0,9001,10):
    r=e.memory()
    if w(r,0x3ff50):break
    if menu(e) and w(r,w(r,0xf438)-0x02000000+24)!=previous:break
    if elapsed<9000:e.run(10)
   if w(r,0x3ff50) or elapsed==9000:break
  log=struct.unpack_from('<40I',e.memory(),0x3ff50)
  report=dict(romSha1=meta['romSha1'],instrumentedSha1=hashlib.sha1(data).hexdigest(),inputSha1=hashlib.sha1(source.read_bytes()).hexdigest(),failedAllocations=log[0],owner=hex(log[38]),
    failures=[dict(bytes=log[1+3*i],caller=hex(log[2+3*i]),mapLock=log[3+3*i]) for i in range(min(log[0],12))])
  (OUT/'allocation-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
 finally:e.close()
 sys.exit(0)
if '--trace-exception' in sys.argv:
 e=E(rom)
 try:
  source=OUT/'key-3.state';e.load(source)
  n=e.core.retro_serialize_size();buffer=C.create_string_buffer(n)
  def state():
   assert e.core.retro_serialize(buffer,n)
   return buffer.raw
  before=state();found=False
  for elapsed in range(0,9000,16):
   e.run(16);after=state()
   if w(after,0x60)&31==27:
    previous=OUT/'pre-exception.state';previous.write_bytes(before);e.load(previous)
    for frame in range(16):
     before=state();e.run(1);after=state()
     if w(after,0x60)&31==27:break
    previous.write_bytes(before);(OUT/'exception.state').write_bytes(after)
    (OUT/'exception.ram').write_bytes(e.memory());(OUT/'exception.iwram').write_bytes(C.string_at(*e.maps[0x03000000]))
    report=dict(romSha1=meta['romSha1'],sourceSha1=hashlib.sha1(source.read_bytes()).hexdigest(),frames=elapsed+frame+1,
      beforeWords=[hex(x) for x in struct.unpack_from('<68I',before,0x20)],afterWords=[hex(x) for x in struct.unpack_from('<68I',after,0x20)],
      schema='https://raw.githubusercontent.com/mgba-emu/mgba/master/include/mgba/internal/gba/serialize.h')
    (OUT/'exception.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2));found=True;break
   before=after
  assert found,'No undefined-instruction exception within diagnostic bound'
 finally:e.close()
 sys.exit(0)
e=E(rom);events=[]
def capture(label):
 r=e.memory();manager=w(r,0xf438)-0x02000000
 e.screenshot(OUT/(label+'.png'));e.save(OUT/(label+'.state'))
 events.append(dict(label=label,visible=menu(e),active=hex(w(r,manager+24)),mode=r[manager+4],
   camera=struct.unpack_from('<4h',r,0x7f64),manager=r[manager:manager+128].hex()))
try:
 e.load(source);e.run(1);capture('start')
 for n,key in enumerate((32,32,256,256)):
  e.run(8,key);e.run(180);capture('key-'+str(n))
 e.run(1800);capture('settled')
finally:e.close()
if '--ai-control' in sys.argv:
 # The sole control change disables future field-display preparation. No
 # action, field mechanics, AI, native heap consumer or menu is replaced.
 image=bytearray(rom.read_bytes());offset=meta['symbols']['ffta_geo_renderer_update']-0x08000000
 image[offset:offset+2]=bytes.fromhex('7047')
 control=OUT/'display-disabled.gba';control.write_bytes(image)
 saved=source.parent/'suspended.sav';results=[]
 for label,path in (('production',rom),('display-disabled-control',control)):
  e=E(path)
  try:
   e.set_memory(0,saved.read_bytes(),0);e.run(3600)
   for key,wait in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):
    e.run(8,key);e.run(wait)
   for _ in range(900):
    if menu(e):break
    e.run(10)
   assert menu(e),'Control never reached cold menu'
   initial=w(e.memory(),w(e.memory(),0xf438)-0x02000000+24)
   for key in (32,32,256,256):e.run(8,key);e.run(180)
   for elapsed in range(0,9001,10):
    r=e.memory();active=w(r,w(r,0xf438)-0x02000000+24)
    if active!=initial and menu(e):break
    if elapsed<9000:e.run(10)
   capture(label);results.append(dict(label=label,elapsed=elapsed,active=hex(active),visible=menu(e),
     romSha1=hashlib.sha1(path.read_bytes()).hexdigest()))
  finally:e.close()
 events.append(dict(controlResults=results,coldSaveSha1=hashlib.sha1(saved.read_bytes()).hexdigest()))
report=dict(romSha1=meta['romSha1'],inputSha1=hashlib.sha1(source.read_bytes()).hexdigest(),
 keys=[32,32,256,256],pressFrames=8,releaseFrames=180,events=events,
 scope='Menu diagnosis from retained cold resume; not new cold-save acceptance')
(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
