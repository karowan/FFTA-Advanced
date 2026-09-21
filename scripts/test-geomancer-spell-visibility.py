"""Native Fire/Fira/Firaga playback with real fields and a display-only control.

Reuse accepted two-caster results. The declared next-turn inputs grant original
spells/HP/MP and position the caster/recipient; fields and graphics are untouched.
The private test ROM fixes RNG at the shared executor boundary on both sides.
Original execution, allocation, damage formulas and animations remain intact.
"""
import collections,ctypes as C,hashlib,json,pathlib,runpy,struct,subprocess
from native_battle_wrappers import from_emulator
from geomancer_render_observation import observe
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
ROM=pathlib.Path(meta['path']);image=ROM.read_bytes();LAB=ROM.parent
PLAY=LAB/'geomancer-overlap';OUT=LAB/'geomancer-spell-visibility';OUT.mkdir(exist_ok=True)
proof=json.loads((PLAY/'report.json').read_text())
assert proof['passed'] and proof['romSha1']==meta['romSha1']==hashlib.sha1(image).hexdigest()
source=PLAY/'first-1/second-2-3/after-cast.state'
source_ram=(source.with_suffix('.ram')).read_bytes()
accepted=next(o for o in proof['outcomes'] if o['first']==1 and o['second']==2 and o['center']==[3,12])
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
menus=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
heap=runpy.run_path(str(ROOT/'scripts/probe-ap-copy-heap.py'))['heap']
word=lambda r,p:struct.unpack_from('<I',r,p)[0]
half=lambda r,p:struct.unpack_from('<H',r,p)[0]
ACTOR,TARGET=0x188,0x398
checks=collections.Counter();outcomes=[];failures=[];case='preparation'
# Ordinary menu rendering consumes RNG at timing-dependent points. Freeze only
# the declared combat seed immediately before the real shared executor, with
# the original pushed-r3 stack contract unchanged. No outcome is manufactured.
assert image[0xa433c:0xa4344]==bytes.fromhex('08b4c046004b1847')
original=word(image,0xa4344)
assert original==meta['priorSymbols']['ffta_samurai_execute_entry']|1
asm=OUT/'fixed-seed.s'
asm.write_text(f'''.syntax unified
.cpu arm7tdmi
.thumb
.global fixed_seed
.thumb_func
fixed_seed:
 push {{r0,r1}}
 ldr r0,=0x030034b0
 movs r1,#3
 str r1,[r0]
 pop {{r0,r1}}
 ldr r3,={original}
 bx r3
.ltorg
''',encoding='utf-8')
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
subprocess.run([prefix+'gcc','-mcpu=arm7tdmi','-mthumb','-nostdlib','-Wl,-Ttext=0x093f0000',
 '-Wl,--entry=fixed_seed',str(asm),'-o',str(OUT/'fixed-seed.elf')],check=True)
subprocess.run([prefix+'objcopy','-O','binary',str(OUT/'fixed-seed.elf'),str(OUT/'fixed-seed.bin')],check=True)
stub=(OUT/'fixed-seed.bin').read_bytes();assert len(stub)<=64 and image[0x13f0000:0x13f0000+len(stub)]==b'\xff'*len(stub)
instrumented=bytearray(image);instrumented[0x13f0000:0x13f0000+len(stub)]=stub
struct.pack_into('<I',instrumented,0xa4344,0x093f0001)
TEST_ROM=OUT/'fixed-seed.gba';TEST_ROM.write_bytes(instrumented)
control=bytearray(instrumented);offset=(meta['symbols']['ffta_geo_renderer_update']&~1)-0x08000000
patch=(bytes.fromhex('c046') if offset&3 else b'')+bytes.fromhex('004b1847')+struct.pack('<I',meta['symbols']['ffta_geo_renderer_retire']|1)
control[offset:offset+len(patch)]=patch
CONTROL=OUT/'display-disabled.gba';CONTROL.write_bytes(control)

def check(label,value):
 checks[label]+=1
 assert value,(case,label)

def active(e):
 r=e.memory();return word(r,word(r,0xf438)-0x02000000+24)-0x02000000

def mode(e):
 r=e.memory();return r[word(r,0xf438)-0x02000000+4]

def tap(e,key,release=180):e.run(8,key);e.run(release)

def menu(e,previous=None):
 for frame in range(0,9001,10):
  if menus['menu_visible'](e) and (previous is None or active(e)!=previous):return
  if frame<9000:e.run(10)
 raise AssertionError(('Native menu timeout',case,hex(active(e)),mode(e)))

def fields(r):return bytes(r[0x3f410+i*22+j] for i in range(36) for j in (15,16,17))

def owner(r):
 manager=word(r,0xf4b0)-0x02000000
 if not 0<=manager<=len(r)-0x440:return 0
 pool=word(r,manager+0x438)-0x02000000
 return word(r,pool+12) if 0<=pool<=len(r)-0x2660 else 0

def capture(e,folder,label):
 e.save(folder/(label+'.state'));e.screenshot(folder/(label+'.png'))
 r=e.memory();(folder/(label+'.ram')).write_bytes(r)
 check('native-render-code-intact',C.string_at(*e.maps[0x03000000])[0x6170:0x6d68]==image[0xa38d24:0xa3991c])
 return r

def prepare():
 e=E(ROM)
 try:
  e.load(source);e.run(1);menu(e)
  for caster,value in zip((0x290,0x4a0),accepted['fields']):
   p=0x3f410+((caster-0x80)//264)*22+15
   check('accepted-source-field-record',e.memory()[p:p+3].hex()==value==source_ram[p:p+3].hex())
  for _ in range(24):
   if active(e)==ACTOR:break
   previous=active(e)
   for key in (32,32,256,256):tap(e,key)
   menu(e,previous)
  check('native-Montblanc-turn',active(e)==ACTOR)
  check('field-survives-to-spell-turn',any(fields(e.memory())[2::3]))
  bank=word(image,word(image,0xcd538)-0x08000000+5*4)-0x08000000
  for index,action in ((66,23),(67,24),(68,25)):
   check('original-Moogle-spell-identity',half(image,bank+index*8+4)==action and image[bank+index*8+6]==1)
   e.set_memory(ACTOR+0x40+index,b'\xff')
  wrappers=from_emulator(image,e)
  for unit,(x,y) in {ACTOR:(2,14),TARGET:(2,12)}.items():
   r=e.memory();grid=word(r,0x7f14)-0x02000000;height=r[grid+2*(y*16+x)]
   check('valid-declared-spell-tile',height>0)
   e.set_memory(unit+0xf6,bytes((x,y)))
   e.set_memory(wrappers[unit]+8,struct.pack('<3H',x*32+16,height*16,y*32+16))
   e.set_memory(unit+0x18,struct.pack('<4H',500,500,100,100))
  observe(e);capture(e,OUT,'spell-ready')
 except BaseException:
  capture(e,OUT,'preparation-failure');raise
 finally:e.close()

def run(action,variant,rom):
 folder=OUT/str(action)/variant;folder.mkdir(parents=True,exist_ok=True);e=E(rom)
 try:
  e.load(OUT/'spell-ready.state');e.run(120);menu(e)
  observe(e,expected=variant=='field-display')
  before=capture(e,folder,'before');check('spell-starts-with-live-field',any(fields(before)[2::3]))
  for key in (32,256,32,256):tap(e,key)
  for _ in range(action-23):tap(e,32)
  tap(e,256)
  r=e.memory();check('selected-original-spell',word(r,word(r,0xf438)-0x02000000+20)==action)
  for _ in range(2):tap(e,16)
  for _ in range(3):
   if mode(e)==11:break
   tap(e,256)
  check('native-final-confirmation',mode(e)==11)
  confirmed=capture(e,folder,'confirmation');observations=[];pictures=set()
  e.run(8,256)
  for frames in range(8,1801,8):
   r=e.memory();observations.append((frames,owner(r),r[0x9198],half(r,0xf5c4)))
   pictures.add(hashlib.sha1(e.frame[0]).hexdigest())
   check('animation-preserves-native-code',C.string_at(*e.maps[0x03000000])[0x6170:0x6d68]==image[0xa38d24:0xa3991c])
   if frames in (64,184,360,720,1200):e.screenshot(folder/f'frame-{frames:04}.png')
   if frames<1800:e.run(8)
  menu(e);display=observe(e,expected=variant=='field-display');after=capture(e,folder,'after')
  check('spell-executed-and-rendered',half(after,ACTOR+0x1c)<half(confirmed,ACTOR+0x1c) and len(pictures)>3)
  check('native-spell-damages-recipient',half(after,TARGET+0x18)<half(confirmed,TARGET+0x18))
  check('spell-preserves-fields',fields(before)==fields(after))
  check('spell-preserves-AP-inventory',before[0x1940:0x1e70]==after[0x1940:0x1e70])
  check('spell-returns-to-caster-menu',active(e)==ACTOR and mode(e)==4)
  current_heap=heap(after);check('native-heap-bound',current_heap['end']==meta['heapEnd'])
  # Hide the command list through the original Wait-facing screen, without
  # confirming the turn. These screenshots are separate readability evidence.
  for key in (32,32,256):tap(e,key)
  capture(e,folder,'facing-view')
  result=dict(action=action,variant=variant,display=display,fields=fields(after).hex(),
   stats=[after[u+0x18:u+0x20].hex() for u in (ACTOR,TARGET)],
   inventoryAP=hashlib.sha1(after[0x1940:0x1e70]).hexdigest(),
   mpSpent=half(confirmed,ACTOR+0x1c)-half(after,ACTOR+0x1c),
   hpLost=half(confirmed,TARGET+0x18)-half(after,TARGET+0x18),
   nativeHeap={k:v for k,v in current_heap.items() if k!='allocationBlocks'},
   observedOwners=sorted(set(o[1] for o in observations)),samples=observations,renderedFrames=len(pictures))
  (folder/'report.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
  return result
 except BaseException:
  capture(e,folder,'failure');raise
 finally:e.close()

try:
 prepare()
 for action in (23,24,25):
  pair=[]
  for variant,rom in (('native-control',CONTROL),('field-display',TEST_ROM)):
   case=(action,variant)
   try:pair.append(run(action,variant,rom))
   except BaseException as error:failures.append(dict(case=case,error=repr(error)))
  if len(pair)==2:
   case=(action,'comparison')
   try:
    check('display-preserves-native-spell-results',all(pair[0][key]==pair[1][key] for key in ('fields','stats','inventoryAP','mpSpent','hpLost')))
   except BaseException as error:failures.append(dict(case=case,error=repr(error)))
  outcomes.extend(pair)
except BaseException as error:failures.append(dict(case=case,error=repr(error)))
report=dict(passed=not failures,romSha1=meta['romSha1'],checks=dict(checks),outcomes=outcomes,failures=failures,
 inputs=dict(source=str(source),sourceSha1=hashlib.sha1(source.read_bytes()).hexdigest(),
 overlapReportSha1=hashlib.sha1((PLAY/'report.json').read_bytes()).hexdigest(),
 declaredSpells=[23,24,25],formation={ACTOR:[2,14],TARGET:[2,12]},hp=500,mp=100,executorSeed=3,
 instrumentedSha1=hashlib.sha1(instrumented).hexdigest(),seedStubSha1=hashlib.sha1(stub).hexdigest()),
 control=dict(sha1=hashlib.sha1(control).hexdigest(),offset=hex(offset),original=image[offset:offset+len(patch)].hex(),replacement=patch.hex()),
 limits=['Owner samples occur every eight frames and are not exact allocation traces.',
 'Three original spell animations are bounded coexistence evidence, not every mixed job or campaign scene.'])
(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(dict(passed=report['passed'],checks=dict(checks),outcomes=[{k:v for k,v in o.items() if k!='samples'} for o in outcomes],failures=failures),indent=2))
assert not failures,('Field spell visibility failures',len(failures))
