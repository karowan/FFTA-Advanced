"""Paid Springboard and Tripwire casts through native menus and animation.

Only initial loadout, formation and HP/status are scenario inputs. Native
targeting, payment, route generation and completed movement are observed.
No player save, injected result, or replacement battle controller is used.
"""
import collections,ctypes as C,hashlib,json,runpy,struct
from pathlib import Path
from native_battle_wrappers import from_emulator
ROOT=Path(__file__).resolve().parents[1]
from chemist_candidate import candidate
meta=candidate()
ROM=Path(meta['path']);image=ROM.read_bytes();assert hashlib.sha1(image).hexdigest()==meta['romSha1']
FIX=ROM.parent/'fixture';OUT=ROM.parent/'movement';OUT.mkdir(exist_ok=True)
assert json.loads((FIX/'report.json').read_text())['romSha1']==meta['romSha1']
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
menus=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
half=lambda b,p:struct.unpack_from('<H',b,p)[0]
word=lambda b,p:struct.unpack_from('<I',b,p)[0]
checks=collections.Counter();samples=[];inputs=[];case='prepare';e=None
ACTOR,TARGET=0x188,0x290
def check(n,a,b=True):checks[n]+=1;assert a==b,(case,n,a,b)
def active(e):
 r=e.memory();return word(r,word(r,0xf438)-0x02000000+24)-0x02000000
def tap(k,wait=180):inputs.append((k,8,wait));e.run(8,k);e.run(wait)
def xy(r,w):return half(r,w+8)//32,half(r,w+12)//32
def phase(r):return word(r,0x3f004) if word(r,0x3f000)==0x50535450 else 0
def snap(label):
 r=e.memory();p=OUT/case;p.mkdir(exist_ok=True)
 e.save(p/(label+'.state'));e.screenshot(p/(label+'.png'))
 (p/(label+'.ram')).write_bytes(r);(p/(label+'.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
 menu=word(r,0xf438)-0x02000000
 samples.append(dict(case=case,label=label,passing=phase(r),battle=half(r,0xf5c4),
  mode=r[menu+4],action=word(r,menu+20),active=active(e),
  cursor=(half(r,0xf3b8),half(r,0xf3bc)),actor=xy(r,wrappers[ACTOR]),target=xy(r,wrappers[TARGET]),
  mp=half(r,ACTOR+0x1c),passingWords=list(struct.unpack_from('<14I',r,0x3f000))))
 (OUT/'partial.json').write_text(json.dumps(samples,indent=2));return r
try:
 e=E(ROM);e.load(FIX/'battle-ready.state');e.run(1);menus['wait_for_menu'](e)
 wrappers=from_emulator(image,e)
 for unit in wrappers:e.set_memory(unit+0x18,struct.pack('<4H',500,500,100,100));e.set_memory(unit+0xe8,bytes(8))
 # Establish the formation before the Sapper's native turn-start snapshot.
 for unit,x,y,height in ((ACTOR,0,14,16),(TARGET,1,13,32),(0x398,3,12,32),(0x5a8,2,12,32)):
  e.set_memory(unit+0xf6,bytes((x,y)));e.set_memory(wrappers[unit]+8,struct.pack('<3H',x*32+16,height,y*32+16))
 e.set_memory(ACTOR+0x40,bytes(0x90));e.set_memory(ACTOR+0x40+121,b'\xff')
 e.set_memory(ACTOR+0x2a,bytes(10));e.set_memory(ACTOR+0x3a,bytes(2))
 for turn in range(16):
  menus['wait_for_menu'](e)
  if active(e)==ACTOR:break
  prior=active(e)
  for k in (32,32,256,256):tap(k)
  for frame in range(9000):
   if menus['menu_visible'](e) and active(e)!=prior:break
   e.run(1)
  else:raise AssertionError('next native turn timed out')
 else:raise AssertionError('Sapper did not receive a turn')
 check('native-Sapper-job',e.memory()[ACTOR+5],127)
 snap('start');e.save(OUT/'start.state')
 for flow in ('spring-route','spring-unspent-Move','spring-cancel','spring-occupied','spring-immobilized','tripwire-place'):
  case=flow;e.load(OUT/'start.state');e.run(1)
  trap=flow=='tripwire-place';unspent=flow=='spring-unspent-Move'
  if trap:
   e.set_memory(ACTOR+0x40,bytes(0x90));e.set_memory(ACTOR+0x40+119,b'\xff')
  # Spend one ordinary Move, then choose the only learned primary action.
  if unspent:tap(32)
  else:
   for k in (256,16,256):tap(k)
  origin=(0,14 if unspent else 13)
  r=snap('approach');check('native-approach',xy(r,wrappers[ACTOR]),origin)
  for k in (256,32,256,256):tap(k)
  r=snap('targeting');check('selected-job-action',word(r,word(r,0xf438)-0x02000000+20),456 if trap else 458)
  if trap:
   initial=half(r,ACTOR+0x1c)
   for k in (16,256,256,256):tap(k)
   e.run(2400);r=snap('placed')
   check('Tripwire-once-eight-MP',half(r,ACTOR+0x1c),initial-8)
   # Canonical live bank is stable and authenticated by cp-state-codec.
   s=0x3f410+27*(ACTOR-0x80)//264
   check('Tripwire-record-tile',r[s+25],0|(12<<4))
   check('Tripwire-live-timer',(r[s+23]>>3)&7,6)
   markers=[i for i in range(0,len(r)-18332,4) if word(r,i)==0x31524746 and word(r,i+4)==0x02000000+i]
   check('Tripwire-owned-renderer',len(markers),1)
   marker=markers[0]
   check('Tripwire-renderer-published',word(r,marker+20),1)
   check('Tripwire-single-tile-outline',r[marker+348:marker+604],bytes(192)+b'\x01'+bytes(63))
   continue
  cursor=(half(r,0xf3b8),half(r,0xf3bc))
  check('target-cursor-domain',cursor in (origin,(1,13)))
  if cursor==origin:
   if unspent:tap(16)
   tap(128)
  tap(256)
  if phase(e.memory())!=2:tap(256)
  r=snap('route-selection');check('ally-route-selection',phase(r),2)
  initial=half(r,ACTOR+0x1c)
  for k in (16,16,256):tap(k)
  r=snap('confirmation');check('route-confirmation',phase(r),3)
  if flow=='spring-cancel':
   tap(1,600);r=snap('cancelled')
   check('cancel-no-MP',half(r,ACTOR+0x1c),initial)
   check('cancel-no-movement',xy(r,wrappers[TARGET]),(1,13))
   check('cancel-retired',phase(r),7)
   continue
  if flow=='spring-occupied':
   e.set_memory(0x398+0xf6,bytes((1,11)));e.set_memory(wrappers[0x398]+8,struct.pack('<3H',48,32,11*32+16))
  if flow=='spring-immobilized':e.set_memory(TARGET+0xeb,bytes((e.memory()[TARGET+0xeb]|64,)))
  tap(256,2400);r=snap('after')
  check('one-eight-MP-payment',half(r,ACTOR+0x1c),initial-8)
  destination=(1,13) if flow in ('spring-occupied','spring-immobilized') else (1,11)
  check('ally-only-valid-two-tile-route',xy(r,wrappers[TARGET]),destination)
  check('caster-stays-put',xy(r,wrappers[ACTOR]),origin)
  check('ally-position-committed',tuple(r[TARGET+0xf6:TARGET+0xf8]),destination)
  check('native-caster-restored',word(r,0xf4ec),0x02000000+wrappers[ACTOR])
  check('route-retired',phase(r),7)
  check('native-caster-Move-budget-preserved',half(r,0xf5c4),37 if unspent else 47)
 report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),inputs=inputs,samples=samples)
except BaseException as error:
 if e:snap('failure')
 report=dict(passed=False,romSha1=meta['romSha1'],checks=dict(checks),case=case,error=repr(error),inputs=inputs,samples=samples)
 raise
finally:
 if e:e.close()
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
