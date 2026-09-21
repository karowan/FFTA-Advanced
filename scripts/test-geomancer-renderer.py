"""Bounded live renderer consumers using native heap, map streams and animation.

The historical map-state RAM is a hashed INPUT, not current-candidate acceptance.
Its older workspace is freed and rebuilt through native allocation before use.
No synthetic allocation header or successful display result is injected. The
DMA peripheral implements requested transfers; native controller code executes.
Actual player-input display/lifetime playback remains a separate gate.
"""
import ast,collections,hashlib,json,pathlib,struct,sys
from ffta_maps import Maps,CLEAN_SHA1
from ffta_geo_assets import static_tiles,graphics_animations
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
OUT=pathlib.Path(meta['path']).parent;rom=pathlib.Path(meta['path']).read_bytes();S=meta['symbols']
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();assert hashlib.sha1(clean).hexdigest()==CLEAN_SHA1
maps=Maps(clean);native=ROOT/'build/expansion/terrain'/CLEAN_SHA1/'native-loader'
loader=json.loads((native/'report.json').read_text());assert loader['passed']
frozen=ROOT/'build/expansion/probes/integrated-jobs/b26778520203359c3b129bcc025b92dd0e4c01f1/ecfa1755355cc1e5e512e2ec825dc5be8c0782ea/executor'
captures={}
for suffix,want in [('ram','a8e6c2ef237bac2b2774c281e94a7323bf0033ac'),('iwram','761ee39d19804c61525588f0df390bc2803f41fc')]:
 data=(frozen/f'execute-trap.{suffix}').read_bytes();assert hashlib.sha1(data).hexdigest()==want
 captures[suffix]=data
STACK,RETURN=0x03007000,0x08000100
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
checks=collections.Counter();samples=[];case=None
def check(label,got,want=True):
 checks[label]+=1
 if got!=want:
  small=lambda x:(len(x),hashlib.sha1(x).hexdigest()) if isinstance(x,bytes) else x
  raise AssertionError((case,label,small(got),small(want)))
class Machine(ARM):
 def __init__(self):
  super().__init__(rom,captures['iwram']);self.put(0x02000000,captures['ram'])
  for a,n in [(0x04000000,4096),(0x05000000,4096),(0x06000000,0x18000),(0x07000000,4096)]:self.u.mem_map(a,n)
  self.pending=set();self.dmas=[];self.blocks=collections.deque(maxlen=24);self.instruction_bound=0
  self.u.hook_add(UC_HOOK_BLOCK,self.block)
  self.u.hook_add(UC_HOOK_MEM_WRITE,self.write_dma,begin=0x040000b0,end=0x040000df)
  self.u.hook_add(UC_HOOK_MEM_READ,self.read_dma,begin=0x040000b0,end=0x040000df)
 def block(self,u,a,n,d):
  self.blocks.append(hex(a));self.instruction_bound+=n//2
 def write_dma(self,u,access,a,n,v,data):
  if a not in (0x040000b8,0x040000c4,0x040000d0,0x040000dc) or not v&0x80000000:return
  assert n==4 and not v&0x78000000,('unsupported non-immediate DMA',hex(v))
  width=4 if v&0x04000000 else 2;count=v&65535
  source,dest=self.word(a-8),self.word(a-4);size=count*width
  sm,dm=(v>>23)&3,(v>>21)&3
  assert count and sm<3 and dm<3 and source%width==dest%width==0
  if sm==dm==0:self.put(dest,self.read(source,size))
  else:
   delta=lambda mode:width if mode==0 else -width if mode==1 else 0
   for i in range(count):self.put(dest+delta(dm)*i,self.read(source+delta(sm)*i,width))
  self.dmas.append((source,dest,size));self.pending.add(a)
 def read_dma(self,u,access,a,n,v,data):
  if a in self.pending:self.put(a,bytes(4));self.pending.remove(a)
 def call(self,address,*args,**kw):
  try:return super().call(S[address] if isinstance(address,str) else address,*args,**kw)
  except BaseException:
   print(json.dumps(dict(address=address,pc=hex(self.u.reg_read(UC_ARM_REG_PC)),sp=hex(self.u.reg_read(UC_ARM_REG_SP)),registers=[hex(self.u.reg_read(r)) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)],blocks=list(self.blocks))))
   raise
 def w(self,a,v):self.put(a,struct.pack('<I',v))
 def h(self,a,v):self.put(a,struct.pack('<H',v&65535))
 def owner(self):return self.word(self.call('ffta_battle_workspace',12))
 def fields(self,kind=2):
  for i in range(36):
   unit=0x02000080+i*264 if i<24 else 0x02002fc4+(i-24)*264
   state=self.call('ffta_job_state',unit);assert state
   self.put(state+15,bytes(3))
  if kind:
   self.h(0x02000098,500);self.put(0x02000168,bytes(8))
   state=self.call('ffta_job_state',0x02000080)
   self.put(state+15,bytes((*self.center,24|kind)))
 def setup(self,index):
  # Replace only the retained capture's old0x2640 payload via original heap
  # free and the current production allocation path. Do not fabricate a pool.
  self.manager=self.word(0x0200f4b0);self.heap=self.word(0x0200f434)
  old=self.word(self.manager+0x438)
  self.call(0x08007170,self.heap,old);self.w(self.manager+0x438,0);self.w(self.manager+0x43c,0)
  check('native-workspace-created',self.call('ffta_additional_workspace_prepare'),1)
  self.pool=self.word(self.manager+0x438);check('native-renderer-slot-empty',self.owner(),0)
  # Declared player-menu phase. The historical executor capture is phase57;
  # production now defers absent-cache creation until a command/facing boundary.
  self.h(0x0200f5c4,37)
  entry=loader['maps'][index]
  for name,address in [('height',0x02007cb0),('arrangement',0x020091a0),('clipping',0x0200d1a0)]:
   part=(native/f'map-{index:03d}-{name}.bin').read_bytes();assert hashlib.sha1(part).hexdigest()==entry[name+'Sha1']
   self.put(address,part)
  self.h(0x02007f10,index);self.w(0x02007f14,0x02007cb0);self.put(0x02007f18,bytes((16,16,0,0,0,16,0,16)))
  self.put(0x02007f40,bytes.fromhex('01000203010000100002000188003000000000060070000600600006'))
  self.put(0x02007f64,struct.pack('<4h',120,256,-64,208));self.h(0x02007f6c,1)
  self.put(0x02008158,bytes(32));self.put(0x02009198,b'\0');self.h(0x03000e10,0)
  self.put(0x03000942,struct.pack('<4H',0x4c03,0x4e02,0x0800,0x0a00))
  self.put(0x06000000,bytes((i*13+1)&255 for i in range(0x18000)))
  atlas=static_tiles(maps,index);self.put(0x06000000,atlas)
  streams=graphics_animations(maps,index)
  if struct.unpack_from('<i',maps.record(index),20)[0]>0:self.put(0x06000000+streams[0].destination,streams[0].frames[0])
  self.call(0x08020f34,0x02007fe4)
  for a in streams:self.call(0x08020da0,0x08000000+a.control,0x06000000+a.destination,0x08000000+a.source)
  if streams:self.call(0x08020a68);self.call(0x08020ba0,0)
  heights=self.read(0x02007cb0,512)
  self.center=next((x,y) for y in range(6,15) for x in range(3,13) if heights[2*(16*y+x)])
  self.fields(0);self.streams=streams
  self.call(0x0801ac78)
  self.original=self.read(0x06000000,0x18000);self.shadow=self.read(0x03000940,26)
  self.heap_before=self.read(self.heap,20)
  return self
 def update(self):self.call('ffta_geo_renderer_update',8)
 def pump(self):self.call(0x0801ac78)
 def cache(self,owner):return self.word(owner+6884+4100)
 def owns(self,owner,src):return owner<=src<owner+18332 or self.cache(owner)<=src<self.cache(owner)+672*32

def main():
 global case,checks,samples
 try:
  for index in (0,4,27,66,67,155):
   case=('activation/restoration',index);m=Machine().setup(index)
   before=m.read(0x02000000,0x40000);cost=m.instruction_bound;m.update();idle=m.instruction_bound-cost
   check('no-field-does-not-allocate-or-mutate',m.read(0x02000000,0x40000),before)
   check('no-field-bounded-instruction-overhead',idle<3000)
   m.fields(2);cost=m.instruction_bound;m.update();composition=m.instruction_bound-cost;owner=m.owner();check('field-allocates-native-owner',bool(owner))
   check('prepare-no-video-writes',m.read(0x06000000,0x18000),m.original)
   check('prepare-publishes-complete-frame',m.read(owner+6884+2,2),b'\x01\0')
   origins=m.read(0x02007f68,4)
   m.pump();check('native-stream-origins-retained',m.read(0x02007f68,4),origins)
   check('published-live-owner',m.word(owner+20),1)
   changed=m.read(0x06000000,0x18000)
   check('terrain-graphics-changed',changed[:0x5000]!=m.original[:0x5000])
   for start,end in [(0x5000,0x6000),(0x7800,0x18000)]:
    check('native-overlay-and-ui-preserved',changed[start:end],m.original[start:end])
   check('ring-background-sizes',tuple(struct.unpack_from('<H',m.read(0x03000940,26),2+2*bg)[0]>>14 for bg in (0,1)),(0,0))
   n=int.from_bytes(m.read(owner+6884,2),'little')
   check('cache-within-proven-bound',n<=672)
   check('exact-front-upload',m.read(0x06007000,2048),m.read(owner+6888,2048))
   check('exact-back-upload',m.read(0x06006000,2048),m.read(owner+8936,2048))
   # Native renderer sees copied source animation, not the composed VRAM. Its
   # already accepted timing/partial-transfer matrix is not repeated here.
   prefix=owner+2708+80
   for a in m.streams:
    check('controller-destinations-owned',any(m.word(0x02007fe4+4+44*i+20)==prefix+a.destination for i in range(4)))
   m.dmas.clear()
   for step in range(4):
    m.call(0x08020a68);m.update();m.pump()
    check('native-animation-never-uploads-over-cache',all(not(0x06000000<=dst<0x06005000) for src,dst,size in m.dmas if src<0x0a000000 and src>=0x08000000))
    m.dmas.clear()
   # The current prepared frame must survive a no-change pump without uploading.
   m.update();m.pump();m.dmas.clear();cost=m.instruction_bound;m.update();steady=m.instruction_bound-cost;m.pump()
   check('stable-field-update-instruction-budget',steady<7000)
   if not m.streams:check('unchanged-static-frame-not-reuploaded',not any(m.owns(owner,src) and dst>=0x06000000 for src,dst,size in m.dmas))
   # Follow the descriptor's currently assigned terrain backgrounds, as native
   # target overlays do. Full native targeting/playback remains separate.
   m.put(0x02007f40,b'\x03\x02');m.h(0x03000946,0x4c03);m.h(0x03000948,0x4e02)
   m.h(0x02007f64,257);m.h(0x02007f66,249);m.h(0x02007f6c,1)
   m.update();m.pump();check('reassigned-background-ring-sizes',m.read(0x03000946,4),bytes.fromhex('030c020e'))
   check('camera-global-ring-scroll',m.read(0x03000952,8),struct.pack('<4H',257,249,257,249))
   pristine_prefix=m.read(prefix,struct.unpack_from('<H',rom,m.word(owner+40)-0x08000000+10)[0]*32)
   m.fields(0);m.update();m.pump();check('expiry-frees-owner',m.owner(),0)
   check('native-heap-budget-restored',m.read(m.heap,20),m.heap_before)
   tiles=len(static_tiles(maps,index))
   expected=bytearray(m.original[:tiles]);expected[:len(pristine_prefix)]=pristine_prefix
   check('restored-native-original-atlas',m.read(0x06000000,tiles),bytes(expected))
   check('inherited-tile576-preserved',m.read(0x06004800,32),m.original[0x4800:0x4820])
   check('native-background-size-restored',m.read(0x03000946,4),bytes.fromhex('034c024e'))
   for a in m.streams:
    check('native-animation-destinations-restored',any(m.word(0x02007fe4+4+44*i+20)==0x06000000+a.destination for i in range(4)))
   samples.append(dict(map=index,owner=owner,cacheTiles=n,streams=len(m.streams),idleInstructionBound=idle,compositionInstructionBound=composition,steadyInstructionBound=steady))
  case=('offscreen-animation',70);m=Machine().setup(70);m.fields(1)
  m.h(0x02007f64,-71);m.h(0x02007f66,265);m.update();m.pump()
  owner=m.owner();stamps=set()
  for step in range(120):
   m.call(0x08020a68);cost=m.instruction_bound;m.update();work=m.instruction_bound-cost
   m.dmas.clear();m.pump()
   check('offscreen-animation-bounded-update',work<7000)
   check('offscreen-animation-no-frame-upload',not any(m.owns(owner,src) and 0x06000000<=dst<0x06007000 for src,dst,size in m.dmas))
   stamps.add(m.read(owner+44,16))
  check('offscreen-control-actually-animated',len(stamps)>2)
  case=('native-allocation-pressure',4);m=Machine().setup(4);m.fields(1);m.update();m.pump()
  owner=m.owner();cache=m.cache(owner);chunks=[]
  m.h(0x0200f5c4,57) # An existing display may survive an active native action.
  # Original allocator supplies deterministic memory pressure; only the actual
  # native global request exercises eviction/retry. No successful result injected.
  while True:
   block=m.call('ffta_geo_native_allocate',m.heap,1024)
   if not block:break
   chunks.append(block)
  check('pressure-control-rejects-request',m.call('ffta_geo_native_allocate',m.heap,22148),0)
  result=m.call(0x08022840,22148)
  check('native-request-retried-after-reclaim',bool(result))
  check('pressure-root-detached',m.owner(),0)
  check('pressure-metadata-retired',m.word(owner),0)
  check('pressure-native-backgrounds-restored',tuple(struct.unpack_from('<H',m.read(0x03000940,26),2+2*bg)[0]>>14 for bg in (0,1)),(1,1))
  m.call(0x08007170,m.heap,result)
  for block in reversed(chunks):m.call(0x08007170,m.heap,block)
  check('pressure-no-heap-leak',m.read(m.heap,20),m.heap_before)
  allocations=[]
  def allocated_during_action(u,address,size,data):allocations.append(address)
  hook=m.u.hook_add(UC_HOOK_CODE,allocated_during_action,begin=S['ffta_geo_native_allocate'],end=S['ffta_geo_native_allocate'])
  for phase in (39,49,57,58):
   m.h(0x0200f5c4,phase)
   for _ in range(8):
    before=m.instruction_bound;m.update()
    check('absent-action-display-update-is-bounded',m.instruction_bound-before<7000)
    check('no-cache-recreation-during-action',m.owner(),0)
  m.u.hook_del(hook)
  check('no-speculative-action-allocations',allocations,[])
  check('deferred-display-does-not-touch-heap',m.read(m.heap,20),m.heap_before)
  m.h(0x0200f5c4,47)
  m.update();m.pump();check('display-recreated-after-pressure',bool(m.owner()))
  m.call('ffta_geo_renderer_retire')
  for boundary in ('native-main-hook','map-reset','scene-reset','manager-free','pool-free','owner-free','cache-free','allocation-failure','cache-allocation-failure','boot-not-ready','enemy-planning','busy','foreign'):
   case=('lifetime',boundary);m=Machine().setup(4);m.fields(1)
   if boundary in ('allocation-failure','cache-allocation-failure'):
    # Exhaust native heap in declared1KiB chunks. A rejected display allocation
    # must preserve the existing native renderer and animation destinations.
    chunks=[]
    while True:
     block=m.call(0x08022840,1024)
     if not block:break
     chunks.append(block)
    if boundary=='cache-allocation-failure':
     for block in reversed(chunks[-18:]):m.call(0x08007170,m.heap,block)
    heap_before=m.read(m.heap,20)
    before=m.read(0x06000000,0x18000);m.update();check('allocation-failure-safe',m.owner(),0)
    check('allocation-failure-no-video-write',m.read(0x06000000,0x18000),before)
    check('partial-allocation-failure-reclaims-metadata',m.read(m.heap,20),heap_before);continue
   if boundary in ('boot-not-ready','enemy-planning'):
    if boundary=='boot-not-ready':m.put(m.word(0x0200f438)+4,b'\0')
    else:
     unit=m.word(m.word(0x0200f4ec));m.put(unit+0x29,bytes((m.read(unit+0x29,1)[0]|128,)))
    before=m.read(m.heap,20);m.update()
    check('native-loading-and-AI-admission-respected',m.owner(),0)
    check('deferred-admission-no-heap-change',m.read(m.heap,20),before);continue
   if boundary=='busy':
    m.put(0x02009198,b'\x01');before=m.read(0x02000000,0x40000);cost=m.instruction_bound;m.update();idle=m.instruction_bound-cost;m.pump()
    check('native-transfer-lock-respected',m.read(0x02000000,0x40000),before);continue
   if boundary=='foreign':
    m.w(m.pool+12,0x02004000);before=m.read(0x02000000,0x40000);cost=m.instruction_bound;m.update();idle=m.instruction_bound-cost
    check('foreign-root-not-repaired',m.read(0x02000000,0x40000),before);continue
   if boundary=='native-main-hook':
    m.put(0x03007e00,b'\x08');m.call(0x0801a518,0,0x03007e00)
    check('actual-native-main-hook-creates-owner',bool(m.owner()));m.pump()
    check('actual-native-main-hook-publishes',m.word(m.owner()+20),1)
    m.call('ffta_geo_renderer_retire');continue
   m.update();owner=m.owner();assert owner;m.pump()
   if boundary=='map-reset':m.call(0x0801a060)
   elif boundary=='scene-reset':m.call('ffta_geo_reset_owners')
   else:m.call(0x08007170,m.heap,{'manager-free':m.manager,'pool-free':m.pool,'owner-free':owner,'cache-free':m.cache(owner)}[boundary])
   check('retired-native-payload-not-allocated',m.read(owner-8,2)!=b'la')
   check('retired-owner-magic-cleared',m.word(owner),0)
  report=dict(passed=True,romSha1=meta['romSha1'],captures={k:hashlib.sha1(v).hexdigest() for k,v in captures.items()},checks=dict(checks),samples=samples)
 except BaseException as error:
  report=dict(passed=False,romSha1=meta['romSha1'],case=case,error=repr(error),checks=dict(checks),samples=samples,pc=hex(m.u.reg_read(UC_ARM_REG_PC)) if 'm' in globals() else None)
  raise
 finally:
  (OUT/'geomancer-renderer-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
  print(json.dumps(report,indent=2))

if __name__=='__main__':main()
