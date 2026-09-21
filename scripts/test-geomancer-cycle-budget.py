"""GBA timer measurements of the production compositor in headless mGBA.

An isolated test boot copies declared native-generated RAM inputs, sets the
observed battle WAITCNT, disables interrupts and measures with cascaded timers.
It calls the exact installed production functions. This is emulated CPU cost,
not whole-game FPS or physical hardware acceptance. No gameplay outcome is
injected. Inputs, driver, hashes, cycle counts and outputs remain private.
"""
import hashlib,importlib.util,json,pathlib,runpy,struct,subprocess

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('renderer_harness',ROOT/'scripts/test-geomancer-renderer.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
OUT=h.OUT/'geomancer-cycle-budget';OUT.mkdir(exist_ok=True)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
prefix=ROOT/'tools/arm-gnu/bin/arm-none-eabi-'
# Format documented by mGBA include/mgba/internal/gba/serialize.h: IO at400h.
# Retained successful player state is only an input for the native WAITCNT.
state=ROOT/'build/expansion/probes/integrated-jobs/b26778520203359c3b129bcc025b92dd0e4c01f1/cf5d3a4be46e585fef697ff0e23a4cbfa342a3bd/geomancer-playback/380/0/occupied/0/next-turn.state'
raw=state.read_bytes();assert hashlib.sha1(raw).hexdigest()=='a9a5f851c7aeb852044b4e3c7866edca9adb76d6'
assert struct.unpack_from('<I',raw)[0]==0x0100000b
waitcnt=struct.unpack_from('<H',raw,0x604)[0];assert waitcnt==0x45b7
driver=OUT/'driver.c';entry=OUT/'entry.s';elf=OUT/'driver.elf';binary=OUT/'driver.bin'
driver.write_text('''#include <stdint.h>
typedef unsigned (*Compose)(const void *,void *,const void *);
typedef unsigned (*Refresh)(const void *,void *);
#define H(a) (*(volatile uint16_t *)(a))
#define W(a) (*(volatile uint32_t *)(a))
void bench(void){
 const uint32_t *config=(const uint32_t *)0x09c00000;
 const uint32_t *source=(const uint32_t *)0x09c00100;
 volatile uint32_t *ram=(volatile uint32_t *)0x02000000;
 for(unsigned i=0;i<65536;i++)ram[i]=source[i];
 H(0x04000208)=0;H(0x04000204)=(uint16_t)config[3];
 H(0x0400010a)=0;H(0x0400010e)=0;
 W(0x0400010c)=0x00840000;W(0x04000108)=0x00800000;
 const void *scene=(const void *)config[0];void *frame=(void *)config[1];
 unsigned refreshed=0,result;
 if(config[2]==1)refreshed=((Refresh)config[4])(scene,frame);
 if(config[2]==2)refreshed=((Compose)config[7])(scene,frame,(const void *)config[6]);
 result=refreshed?1:((Compose)config[5])(scene,frame,(const void *)config[6]);
 H(0x0400010a)=0;
 unsigned cycles=H(0x04000108)|((unsigned)H(0x0400010c)<<16);
 H(0x0400010e)=0;
 W(0x0203fff4)=cycles;W(0x0203fff8)=result;W(0x0203fffc)=refreshed;
 W(0x0203fff0)=0x47435943;
 for(;;){}
}
''',encoding='utf-8')
entry.write_text('''.syntax unified
.cpu arm7tdmi
.arm
.global _start
_start:
 mov r0,#0xdf
 msr cpsr_c,r0
 ldr sp,=0x03007000
 ldr r0,=bench
 bx r0
.ltorg
''',encoding='utf-8')
def tool(name,*args):return subprocess.check_output([str(prefix)+name,*map(str,args)],text=True)
tool('gcc','-mcpu=arm7tdmi','-mthumb','-Os','-ffreestanding','-fno-builtin','-nostdlib',
 '-Wall','-Wextra','-Werror','-Wl,-Ttext=0x093ef000','-Wl,--entry=_start',entry,driver,'-lgcc','-o',elf)
tool('objcopy','-O','binary',elf,binary);code=binary.read_bytes();assert len(code)<4096
rows=[]

def decoded(ram,owner):
 frame=owner-0x02000000+6884
 cache=struct.unpack_from('<I',ram,frame+4100)[0]-0x02000000
 result=[]
 # Compare all ring entries as their exact tile bytes and palette, independent
 # of cache index assignment/reinterning in the full-composition control.
 for p in range(2):
  cells=[]
  for word in struct.unpack_from('<1024H',ram,frame+4+p*2048):
   physical=word&1023;index=physical if physical<640 else physical-192
   assert 0<=index<672 and not word&0xc00
   cells.append(struct.pack('<H',word&0xf000)+ram[cache+index*32:cache+(index+1)*32])
  result.append(b''.join(cells))
 return b''.join(result)

try:
 for index in (4,27,67,155):
  h.case=('cycle-input',index);m=h.Machine().setup(index)
  arrangements=[struct.unpack('<4096H',m.read(0x020091a0+p*8192,8192)) for p in range(2)]
  animated={t for a in m.streams for t in range(a.destination//32,(a.destination+a.length)//32)}
  def score(cx,cy):return len({a[y*64+x]&1023 for a in arrangements for y in range(cy//8,min(cy//8+21,64)) for x in range(cx//8,min(cx//8+31,64))}&animated)
  cx,cy=max(((x,y) for y in range(0,345,32) for x in range(0,265,32)),key=lambda xy:score(*xy))
  m.h(0x02007f64,cx);m.h(0x02007f66,cy);m.h(0x02007f6c,1)
  m.fields(1);m.update();owner=m.owner();assert owner;m.pump()
  camera_fixture=bytearray(m.read(0x02000000,0x40000))
  struct.pack_into('<2i',camera_fixture,owner-0x02000000+2652+28,cx+8,cy+8)
  (OUT/f'map-{index}-camera.ram').write_bytes(camera_fixture)
  before=m.read(owner+2788,4096)
  for step in range(60):
   m.call(0x08020a68);m.pump()
   if m.read(owner+2788,4096)!=before and m.word(owner+28)&2:break
  else:raise AssertionError(('No native visible animation input',index))
  fixture=m.read(0x02000000,0x40000);(OUT/f'map-{index}.ram').write_bytes(fixture)
  results=[];pixel_results=[]
  for mode in (0,1,2,3):
   rom=bytearray(h.rom[:0x1c40100])
   assert rom[0x13ef000:0x13ef000+len(code)]==bytes([255])*len(code)
   assert rom[0x1c00000:0x1c40100]==bytes([255])*0x40100
   rom[0x13ef000:0x13ef000+len(code)]=code
   struct.pack_into('<I',rom,0,0xea000000|((0x093ef000-0x08000008)//4))
   algorithm=0 if mode%2==0 else 1 if mode==1 else 2
   struct.pack_into('<8I',rom,0x1c00000,owner+2652,owner+6884,algorithm,waitcnt,
     h.S['ffta_geo_refresh_animation']|1,h.S['ffta_geo_compose']|1,m.word(m.word(owner+40)+20),h.S['ffta_geo_shift']|1)
   rom[0x1c00100:0x1c40100]=fixture if mode<2 else camera_fixture
   path=OUT/'benchmark.gba';path.write_bytes(rom);e=E(path)
   e.run(1) # libretro publishes memory-map descriptors on its first frame.
   try:
    for frame in range(121):
     memory=e.memory()
     if struct.unpack_from('<I',memory,0x3fff0)[0]==0x47435943:break
     if frame<120:e.run(1)
    else:raise AssertionError(('Benchmark did not finish',index,mode))
    cycles,result,refreshed=struct.unpack_from('<3I',memory,0x3fff4)
    assert result==1 and cycles>1000,(index,mode,cycles,result)
    (OUT/f'map-{index}-{mode}-output.ram').write_bytes(memory)
    e.save(OUT/f'map-{index}-{mode}.state')
    if mode==3:assert refreshed==1,('Camera input did not reuse intersection',index)
    results.append(dict(mode=mode,path='animation' if mode<2 else 'camera',cycles=cycles,frameBudgets=cycles/280896,reused=refreshed,
      privateRomSha1=hashlib.sha1(rom).hexdigest(),outputSha1=hashlib.sha1(memory).hexdigest()))
    pixel_results.append(decoded(memory,owner))
   finally:e.close()
  assert pixel_results[0]==pixel_results[1],('mGBA full/refresh pixel mismatch',index)
  assert pixel_results[2]==pixel_results[3],('mGBA full/shift pixel mismatch',index)
  rows.append(dict(map=index,camera=[cx,cy],nativeSteps=step+1,inputSha1=hashlib.sha1(fixture).hexdigest(),
   cameraInputSha1=hashlib.sha1(camera_fixture).hexdigest(),results=results,
   cycleRatio=results[1]['cycles']/results[0]['cycles'],cameraCycleRatio=results[3]['cycles']/results[2]['cycles']))
 report=dict(passed=True,romSha1=h.meta['romSha1'],waitcnt=hex(waitcnt),waitcntInputSha1=hashlib.sha1(raw).hexdigest(),
  driverSha1=hashlib.sha1(code).hexdigest(),rows=rows,
  limits=['Isolated production function CPU cost on emulated GBA timers, not whole-game FPS.','Interrupt/audio work is disabled; native battle WAITCNT is preserved.','benchmark.gba is the final case; earlier images reproduce from retained RAM/configuration and this script.'])
except BaseException as error:
 report=dict(passed=False,romSha1=h.meta['romSha1'],rows=rows,error=repr(error));raise
finally:
 (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
