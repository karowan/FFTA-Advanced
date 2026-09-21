"""Native animation controllers and DMA, redirected into the original prefix.

Unicorn executes original20F34/20DA0/20A68/20BA0. A deterministic DMA peripheral
copies exactly the requested bytes; no controller timing or output is faked.
Compare ordinary VRAM playback with redirected source memory, including partial
transfers, simultaneous streams, restoration and invalid/stale admission.
"""
import collections,hashlib,json,pathlib,struct
from ffta_maps import Maps,COUNT,CLEAN_SHA1
from ffta_geo_assets import static_tiles,graphics_animations
ROOT=pathlib.Path(__file__).resolve().parents[1]
fixture=ROOT/'scripts/test-geomancer-compositor.py';ns={'__file__':str(fixture),'__name__':'animation_fixture'}
exec(compile(fixture.read_text(encoding='utf-8').split('for kind,camera in ')[0],str(fixture),'exec'),ns)
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
OUT,code,symbols=(ns[k] for k in ('OUT','code','symbols'))
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();assert hashlib.sha1(clean).hexdigest()==CLEAN_SHA1
maps=Maps(clean)
frozen=ROOT/'build/expansion/probes/integrated-jobs/b26778520203359c3b129bcc025b92dd0e4c01f1/ecfa1755355cc1e5e512e2ec825dc5be8c0782ea/executor/execute-trap.iwram'
iw=frozen.read_bytes();assert hashlib.sha1(iw).hexdigest()=='761ee39d19804c61525588f0df390bc2803f41fc'
POOL,SOURCE,SOURCE_BYTES=0x02008000,0x02018000,4176
PREFIX=SOURCE+80
checks=collections.Counter();samples=[];case=None
def check(label,got,want=True):
 checks[label]+=1
 if got!=want:raise AssertionError((case,label,got if not isinstance(got,bytes) else hashlib.sha1(got).hexdigest(),want if not isinstance(want,bytes) else hashlib.sha1(want).hexdigest()))
class Machine:
 def __init__(self):
  self.u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);self.dma=[];self.pending=False
  for a,n in ((0x02000000,0x40000),(0x03000000,0x8000),(0x04000000,0x1000),(0x06000000,0x18000),(0x08000000,0x2000000)):self.u.mem_map(a,n)
  self.put(0x08000000,clean);self.put(0x09e00000,code);self.put(0x03000000,iw)
  self.u.hook_add(UC_HOOK_MEM_WRITE,self.write_dma,begin=0x040000dc,end=0x040000df)
  self.u.hook_add(UC_HOOK_MEM_READ,self.read_dma,begin=0x040000dc,end=0x040000df)
 def put(self,a,b):self.u.mem_write(a,bytes(b))
 def read(self,a,n):return bytes(self.u.mem_read(a,n))
 def word(self,a):return int.from_bytes(self.read(a,4),'little')
 def write_dma(self,u,access,a,n,v,data):
  if not v&0x80000000:return
  assert a==0x040000dc and n==4 and v&0xffff0000==0x84000000,('unexpected DMA mode',hex(v))
  source=self.word(0x040000d4);dest=self.word(0x040000d8);size=(v&65535)*4
  assert size and source%4==dest%4==0
  self.put(dest,self.read(source,size));self.dma.append((source,dest,size));self.pending=True
 def read_dma(self,u,access,a,n,v,data):
  if self.pending:self.put(0x040000dc,bytes(4));self.pending=False
 def call(self,address,*args):
  if isinstance(address,str):address=symbols[address]
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for i,r in enumerate(saved):self.u.reg_write(r,0x55000000+i)
  for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):self.u.reg_write(r,v)
  self.u.reg_write(UC_ARM_REG_SP,0x03007000);self.u.reg_write(UC_ARM_REG_LR,0x08000101)
  self.u.emu_start(address|1,0x08000100,count=1000000)
  check('native-return-and-stack',(self.u.reg_read(UC_ARM_REG_PC),self.u.reg_read(UC_ARM_REG_SP)),(0x08000100,0x03007000))
  check('native-preserved-registers',[self.u.reg_read(r) for r in saved],[0x55000000+i for i in range(8)])
  return self.u.reg_read(UC_ARM_REG_R0)
 def tick(self):self.call(0x08020a68);self.call(0x08020ba0,0)
 def setup(self,index):
  image=static_tiles(maps,index);self.put(0x06000000,image)
  primary=struct.unpack_from('<i',maps.record(index),20)[0]
  if primary>0:
   a=graphics_animations(maps,index)[0];self.put(0x06000000+a.destination,a.frames[0])
  self.call(0x08020f34,POOL)
  for a in graphics_animations(maps,index):self.call(0x08020da0,0x08000000+a.control,0x06000000+a.destination,0x08000000+a.source)
  self.put(SOURCE-4,b'\x9a'*(SOURCE_BYTES+8));self.put(SOURCE,bytes(16))
  return image
 def controllers(self,redirected=False):
  b=bytearray(self.read(POOL,180))
  if redirected:
   for i in range(4):
    for off in (20,28):
     p=4+44*i+off;v=struct.unpack_from('<I',b,p)[0]
     if PREFIX<=v<PREFIX+4096:struct.pack_into('<I',b,p,v-PREFIX+0x06000000)
  return bytes(b)

catalog=[graphics_animations(maps,i) for i in range(COUNT)]
extra=[i for i,a in enumerate(catalog) if any(struct.unpack_from('<i',maps.record(i),f)[0] for f in range(32,48,4))]
largest=max(range(COUNT),key=lambda i:max((a.length for a in catalog[i]),default=0))
check('all-six-independent-stream-maps',extra,[4,5,62,63,67,155])
for index in extra+[largest]:
 case=('native-streams',index);reference,redirected=Machine(),Machine()
 image=reference.setup(index);redirected.setup(index)
 tiles=max(a.destination+a.length for a in catalog[index])//32
 # Enter after the first native upload, including the large stream's first
 #1024 bytes. Its next upload must continue at the redirected partial offset.
 reference.tick();redirected.tick();before=redirected.read(0x06000000,0x5000)
 check('source-begin',redirected.call('ffta_geo_animation_begin',SOURCE,POOL,tiles),1)
 check('initial-pristine-prefix',redirected.read(PREFIX,tiles*32),reference.read(0x06000000,tiles*32))
 check('begin-preserves-visible-graphics',redirected.read(0x06000000,0x5000),before)
 check('begin-keeps-native-controller-state',redirected.controllers(True),reference.controllers())
 snapshot=redirected.read(0x02000000,0x40000)
 check('cannot-rebind-live-source',redirected.call('ffta_geo_animation_begin',SOURCE,POOL,tiles),0)
 check('rejected-rebind-is-pure',redirected.read(0x02000000,0x40000),snapshot)
 frames=max(sum(a.durations) for a in catalog[index])*2+8
 for frame in range(frames):
  reference.tick();redirected.tick()
  check('exact-native-animation-progress',redirected.controllers(True),reference.controllers())
  check('all-partial-DMA-prefix-pixels',redirected.read(PREFIX,tiles*32),reference.read(0x06000000,tiles*32))
  check('animation-never-overwrites-composed-VRAM',redirected.read(0x06000000,0x5000),before)
  check('map-transfer-lock-restored',redirected.read(0x02009198,1),b'\0')
 check('source-allocation-guards',redirected.read(SOURCE-4,4)+redirected.read(SOURCE+SOURCE_BYTES,4),b'\x9a'*8)
 # The later ring owner restores the pristine pixels before releasing source
 # ownership. This explicit copy is setup, not a claimed renderer callback.
 redirected.put(0x06000000,redirected.read(PREFIX,tiles*32))
 redirected.call('ffta_geo_animation_end',SOURCE)
 check('native-destinations-restored',redirected.controllers(),reference.controllers())
 for frame in range(10):reference.tick();redirected.tick()
 check('restored-native-animation-pixels',redirected.read(0x06000000,len(image)),reference.read(0x06000000,len(image)))
 snapshot=redirected.read(0x02000000,0x40000);redirected.call('ffta_geo_animation_end',SOURCE)
 check('repeat-retirement-is-pure',redirected.read(0x02000000,0x40000),snapshot)
 samples.append(dict(map=index,streams=len(catalog[index]),frames=frames,prefixTiles=tiles,transfers=len(reference.dma)))

for failure in ('prefix-too-small','misaligned-chunk','foreign-source','foreign-control','bad-pool-budget','untouched-controller','new-frame-not-transferred'):
 case=('atomic-admission',failure);m=Machine();m.setup(largest);m.tick();tiles=128
 if failure=='prefix-too-small':tiles=1
 if failure=='misaligned-chunk':m.put(POOL+4+10,struct.pack('<H',1000))
 if failure=='foreign-source':m.put(POOL+4+24,struct.pack('<I',0x02009000))
 if failure=='foreign-control':m.put(POOL+4+16,struct.pack('<I',0x02009000))
 if failure=='bad-pool-budget':m.put(POOL,struct.pack('<H',1000))
 if failure=='untouched-controller':m.put(POOL+4+4,b'\xff')
 if failure=='new-frame-not-transferred':m.put(POOL+4+12,bytes(2))
 before=m.read(0x02000000,0x40000)
 check('invalid-animation-input-refused',m.call('ffta_geo_animation_begin',SOURCE,POOL,tiles),0)
 check('refusal-is-atomic',m.read(0x02000000,0x40000),before)
case='retire-after-controller-reuse';m=Machine();m.setup(largest);m.tick();m.call('ffta_geo_animation_begin',SOURCE,POOL,128)
m.put(POOL+4+16,struct.pack('<I',0x08001234));before=m.read(POOL,180)
m.call('ffta_geo_animation_end',SOURCE);check('foreign-controller-not-restored',m.read(POOL,180),before)
report=dict(passed=True,sourceSha1=ns['digest'],cleanRomSha1=CLEAN_SHA1,checks=dict(checks),samples=samples,
 animationDecoderSha1=hashlib.sha1((ROOT/'scripts/ffta_geo_assets.py').read_bytes()).hexdigest(),
 limits=['Direct original native animation controllers with deterministic DMA peripheral, not full emulator rendering',
 'Map owner allocation, original graphics restoration and live callback installation remain separate integration work'])
(OUT/'native-animation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
