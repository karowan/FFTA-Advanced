"""Native animated-source ordering and independent published-pixel checks.

The graphics producer is the unchanged native tick/pump on a second machine.
The field display must publish the source snapshot available to its preceding
main update, including partial DMA. No native controller/result is fabricated.
This tests bounded native execution, not real-device frame-rate acceptance.
"""
import ast,collections,hashlib,importlib.util,json,pathlib,struct

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('renderer_harness',ROOT/'scripts/test-geomancer-renderer.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
tree=ast.parse((ROOT/'scripts/test-geomancer-compositor.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='oracle'],type_ignores=[]),'<independent pixel oracle>','exec'))
checks=collections.Counter();samples=[];case=None

def check(label,got,want=True):
 checks[label]+=1
 if got!=want:
  small=lambda b:(len(b),hashlib.sha1(b).hexdigest()) if isinstance(b,bytes) else b
  raise AssertionError((case,label,small(got),small(want)))

def pixels(raw):
 return [bytes(n for b in raw[i:i+32] for n in (b&15,b>>4)) for i in range(0,len(raw),32)]

def expected(m,reference):
 owner=m.owner();asset=m.word(owner+40);tiles=int.from_bytes(m.read(asset+8,2),'little')
 atlas=pixels(reference.read(0x06000000,tiles*32))
 arrangement=[list(struct.unpack('<4096H',m.read(0x020091a0+p*8192,8192))) for p in range(2)]
 palette=list(struct.unpack('<128H',m.read(m.word(asset+4),256)))
 projection=list(struct.iter_unpack('<hh4B',m.read(owner+604,2048)))
 board=m.read(owner+348,256);cx,cy=struct.unpack('<ii',m.read(owner+32,8))
 retained={576:pixels(reference.read(0x06004800,32))[0]}
 result=oracle(atlas,arrangement,palette,projection,board,cx,cy,retained)
 # The compositor may omit a lower tile only behind a completely opaque
 # front tile. Match that documented representation, not its hashing logic.
 for y in range(21):
  for x in range(31):
   offsets=[(y*8+dy)*248+x*8 for dy in range(8)]
   if all(all(result[0][o:o+8]) for o in offsets):
    for o in offsets:result[1][o:o+8]=bytes(8)
 return result,cx,cy

def published(m,cx,cy):
 raw=m.read(0x06000000,0x7800);result=[]
 for base in (0x7000,0x6000):
  plane=bytearray(248*168)
  for y in range(21):
   for x in range(31):
    pos=((cy//8+y)&31)*32+((cx//8+x)&31)
    word=struct.unpack_from('<H',raw,base+2*pos)[0]
    check('cache-has-no-native-flip-bits',word&0xc00,0)
    tile=pixels(raw[(word&1023)*32:(word&1023)*32+32])[0]
    for dy in range(8):plane[(8*y+dy)*248+8*x:(8*y+dy)*248+8*x+8]=tile[dy*8:dy*8+8]
  result.append(bytes(plane))
 return result

try:
 for index in (4,27,67,155):
  h.case=case=('animated-source',index)
  m=h.Machine().setup(index);reference=h.Machine().setup(index)
  # Select a reproducible viewport containing original animated tile references.
  # Camera changes alone must not be enough to satisfy the animation assertion.
  arrangements=[struct.unpack('<4096H',m.read(0x020091a0+p*8192,8192)) for p in range(2)]
  animated={t for stream in m.streams for t in range(stream.destination//32,(stream.destination+stream.length)//32)}
  def visibility(cx,cy):
   return len({arr[y*64+x]&1023 for arr in arrangements for y in range(cy//8,min(cy//8+21,64)) for x in range(cx//8,min(cx//8+31,64))}&animated)
  cx,cy=max(((x,y) for y in range(0,345,32) for x in range(0,265,32)),key=lambda xy:visibility(*xy))
  check('selected-viewport-has-animated-sources',visibility(cx,cy)>0)
  for machine in (m,reference):
   machine.h(0x02007f64,cx);machine.h(0x02007f66,cy);machine.h(0x02007f6c,1)
  m.fields(1)
  in_pump=[False];pump_compositions=[0];compositions=[0];refreshes=[0];shifts=[0];update_samples=[]
  def compose_entry(u,a,n,data):
   compositions[0]+=1
   if in_pump[0]:pump_compositions[0]+=1
  address=h.S['ffta_geo_compose']&~1
  m.u.hook_add(h.UC_HOOK_CODE,compose_entry,begin=address,end=address)
  def refresh_entry(u,a,n,data):refreshes[0]+=1
  address=h.S['ffta_geo_refresh_animation']&~1
  m.u.hook_add(h.UC_HOOK_CODE,refresh_entry,begin=address,end=address)
  def shift_entry(u,a,n,data):
   shifts[0]+=1
   if in_pump[0]:pump_compositions[0]+=1
  address=h.S['ffta_geo_shift']&~1
  m.u.hook_add(h.UC_HOOK_CODE,shift_entry,begin=address,end=address)
  m.update();owner=m.owner();assert owner
  check('initial-composition-entry-observed',compositions[0],1)
  prefix_bytes=int.from_bytes(m.read(m.word(owner+40)+10,2),'little')*32
  initial=m.read(owner+2708+80,prefix_bytes);m.pump();reference.pump()
  changed=0;max_update=0;observed=set();deferred=0;stationary_changes=0;previous=None
  # Covers multiple real frame boundaries and multi-transfer primary frames.
  for step in range(40):
   h.case=case=('animated-source',index,step)
   check('pristine-prefix-follows-native-producer',m.read(owner+2708+80,len(initial)),reference.read(0x06000000,len(initial)))
   before=m.read(owner+2708+80,4096)
   m.call(0x08020a68);reference.call(0x08020a68)
   if step in (5,6):
    for machine in (m,reference):
     machine.h(0x02007f64,cx+(8 if step==5 else -8))
     machine.h(0x02007f66,cy+8)
   # Native camera/terrain dirty frames take priority over graphics DMA.
   # Include a sub-tile move, a ring wrap and simultaneous two-axis shake.
   if step in (9,17,25):
    for machine in (m,reference):
     machine.h(0x02007f64,{9:123,17:257,25:120}[step])
     machine.h(0x02007f66,{9:259,17:249,25:256}[step])
     machine.h(0x02007f6c,1)
    deferred+=1
   if step==29:
    for machine in (m,reference):
     machine.h(0x02007f6c,0x400);machine.put(0x02008158,b'\x01');machine.put(0x0200815c,b'\x01')
     machine.h(0x02008164,-9);machine.h(0x02008166,11)
   cost=m.instruction_bound;old_compositions=compositions[0];old_refreshes=refreshes[0]
   m.update();work=m.instruction_bound-cost;max_update=max(max_update,work)
   if refreshes[0]!=old_refreshes:update_samples.append(dict(step=step,instructions=work,fallback=compositions[0]!=old_compositions))
   want,cx,cy=expected(m,reference)
   in_pump[0]=True;m.pump();in_pump[0]=False;reference.pump()
   actual=published(m,cx,cy)
   if previous and previous[0]==(cx,cy) and previous[1]!=actual:stationary_changes+=1
   previous=((cx,cy),actual)
   for p in range(2):check('published-pixels-use-completed-source-snapshot',actual[p],bytes(want[p]))
   changed+=m.read(owner+2708+80,4096)!=before
   observed.add(hashlib.sha1(b''.join(actual)).hexdigest())
   check('no-composition-inside-native-pump',pump_compositions[0],0)
   check('pump-leaves-only-source-rebuild-bit',m.word(owner+28) in (0,2))
  check('native-animation-produced-new-pixels',changed>2)
  check('camera-fringe-reuse-actually-executed',shifts[0]>=2)
  check('visible-output-changes',len(observed)>3)
  check('visible-animation-changes-with-stationary-camera',stationary_changes>0)
  # Stop ticking, drain native partial transfers, then require the final pixels
  # to settle too; a producer event must never get swallowed before its DMA.
  for _ in range(6):m.update();m.pump();reference.pump()
  want,cx,cy=expected(m,reference);actual=published(m,cx,cy)
  for p in range(2):check('final-animation-frame-does-not-freeze-stale',actual[p],bytes(want[p]))
  check('settled-source-does-not-stay-dirty',m.word(owner+28),0)
  samples.append(dict(map=index,steps=40,nativePixelChanges=changed,publishedStates=len(observed),stationaryPixelChanges=stationary_changes,terrainPriorityFrames=deferred,maxUpdateInstructionBound=max_update,animationUpdates=update_samples))
 report=dict(passed=True,romSha1=h.meta['romSha1'],checks=dict(checks),samples=samples,
  limitations=['Native instruction counts are not hardware cycle or frame-rate measurements.','Animation display intentionally uses the last completed source snapshot.'])
except BaseException as error:
 report=dict(passed=False,romSha1=h.meta['romSha1'],case=case,error=repr(error),checks=dict(checks),samples=samples)
 raise
finally:
 (h.OUT/'geomancer-render-timing-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 print(json.dumps(report,indent=2))
