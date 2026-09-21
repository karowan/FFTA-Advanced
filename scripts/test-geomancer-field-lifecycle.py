"""Native field casts -> cartridge suspend -> cold boot -> two caster turns.

Consumes the fixed player playback's actual results. No field record, result,
save payload, turn timer or renderer output is written by this test. Unicorn
accessors run only on detached copies; all live transitions use fixed buttons.
"""
import ast,collections,ctypes as C,hashlib,json,pathlib,runpy,struct,sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
ROM=pathlib.Path(meta['path']);image=ROM.read_bytes();LAB=ROM.parent
PLAY=LAB/'geomancer-playback';OUT=LAB/'geomancer-field-lifecycle';OUT.mkdir(exist_ok=True)
play=json.loads((PLAY/'report.json').read_text());TEST_ROM=PLAY/'playback.gba'
assert play['passed'] and play['romSha1']==meta['romSha1']==hashlib.sha1(image).hexdigest()
assert hashlib.sha1(TEST_ROM.read_bytes()).hexdigest()==play['instrumentedSha1']
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
STACK,RETURN=0x03007000,0x08000100
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<detached field accessors>','exec'))
ACTOR=0x4a0
checks=collections.Counter();outcomes=[];case=None
display_checks='--display-checks' in sys.argv
if display_checks:
 from geomancer_render_observation import observe as observe_field_display
word=lambda r,p:struct.unpack_from('<I',r,p)[0]
half=lambda r,p:struct.unpack_from('<H',r,p)[0]

def check(label,value):
 checks[label]+=1
 assert value,(label,case)

def active(e):
 r=e.memory();p=word(r,0xf438)-0x02000000
 return word(r,p+24) if 0<=p<len(r)-28 else 0

def tap(e,key,wait=180):e.run(8,key);e.run(wait)

def menu(e,previous=None):
 for frames in range(0,9001,10):
  if observe['menu_visible'](e) and (previous is None or active(e)!=previous):return
  if frames<9000:e.run(10)
 raise AssertionError(('menu timeout',case,hex(active(e))))

def capture(e,label,folder):
 e.save(folder/(label+'.state'));e.screenshot(folder/(label+'.png'))
 r=e.memory();(folder/(label+'.ram')).write_bytes(r)
 check('native-render-code-intact',C.string_at(*e.maps[0x03000000])[0x6170:0x6d68]==image[0xa38d24:0xa3991c])
 return r

def field(e):
 """Observe actual field geometry and the native caster's saved owner record."""
 before=e.memory();iwram=C.string_at(*e.maps[0x03000000])
 m=ARM(image,iwram);m.put(0x02000000,before)
 call=lambda name,*args:m.call(meta['symbols'][name],*args)
 unit=0x02000000+ACTOR;s=call('ffta_job_state',unit)
 check('owned-live-caster',bool(s))
 record=m.read(s,22);kind=call('ffta_geo_field_kind',unit)
 x,y=record[15:17];coverage=[];expected=[]
 if kind:
  height=m.call(0x0801cc18,x,y)
  # Inspect all adjacent candidates and a two-tile negative control. The
  # exact cross/height rule has a separate exhaustive board matrix.
  for dx,dy in ((0,0),(-1,0),(1,0),(0,-1),(0,1),(2,0)):
   tx,ty=x+dx,y+dy
   present=call('ffta_geo_field_at',unit,tx&0xffffffff,ty&0xffffffff,kind)
   if present:coverage.append([tx,ty])
   valid=0<=tx<16 and 0<=ty<16 and m.call(0x0801cc7c,tx,ty)
   if valid and abs(dx)+abs(dy)<=1 and abs(m.call(0x0801cc18,tx,ty)-height)<=2:expected.append([tx,ty])
  check('native-field-geometry',coverage==expected)
 check('detached-observation-read-only',e.memory()==before and C.string_at(*e.maps[0x03000000])==iwram)
 return dict(record=record.hex(),kind=kind,center=[x,y],timer=(record[17]>>2)&7,coverage=coverage)

for action,kind in ((380,1),(382,2)):
 for empty in (False,True):
  case=(action,empty);folder=OUT/str(action)/('empty' if empty else 'occupied');folder.mkdir(parents=True,exist_ok=True)
  source=PLAY/str(action)/'0'/('empty' if empty else 'occupied')/'0'/'next-turn.state'
  check('actual-successful-cast-input',any(o['action']==action and o['seed']==0 and o['empty']==empty for o in play['outcomes']))
  source_hash=hashlib.sha1(source.read_bytes()).hexdigest()
  e=E(TEST_ROM)
  try:
   e.load(source);e.run(1);menu(e)
   if display_checks:observe_field_display(e)
   expected=capture(e,'suspend-ready',folder);before=field(e);next_actor=active(e)
   check('actual-field-survived-cast-turn',before['kind']==kind and before['timer']==2)
   check('actual-field-selected-center',before['center']==([2,12] if empty else [1,13]))
   for key in (1,8,16,256,256):tap(e,key)
   old=e.memory(0);tap(e,256,300);saved=e.memory(0)
   check('native-cartridge-suspend',saved!=old);(folder/'suspended.sav').write_bytes(saved)
  except BaseException:
   e.save(folder/'failure.state');e.screenshot(folder/'failure.png');raise
  finally:e.close()
  # New emulator, production ROM, SRAM only: no savestate restoration and
  # no instrumentation or private affinity tile survives this cold boot.
  e=E(ROM)
  try:
   e.set_memory(0,saved,0);e.run(3600)
   for key,wait in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):tap(e,key,wait)
   menu(e)
   display=observe_field_display(e) if display_checks else None
   actual=capture(e,'cold-resumed',folder);restored=field(e)
   check('cold-owner-timer-center-and-coverage',restored==before)
   check('cold-current-turn-preserved',active(e)==next_actor)
   check('cold-caster-HP-MP',actual[ACTOR+0x18:ACTOR+0x20]==expected[ACTOR+0x18:ACTOR+0x20])
   check('cold-AP-inventory',actual[0x1940:0x1e70]==expected[0x1940:0x1e70])
   check('cold-native-roots-clear',actual[0x3ff44:0x3ff4c]==bytes(8))
   turns=[];caster_ends=0
   for n in range(36):
    previous=active(e);prior=field(e)
    check('caster-alive-before-expiry',half(e.memory(),ACTOR+0x18)>0 and not e.memory()[ACTOR+0xe8]&64)
    # Unmoved, unacted native turn: Down, Down, A, A chooses Wait/facing.
    for key in (32,32,256,256):tap(e,key)
    menu(e,previous)
    if previous==0x02000000+ACTOR:caster_ends+=1
    after=field(e);turns.append(dict(actor=previous,before=prior,after=after))
    check('only-caster-turns-tick-field',after['timer']==2-caster_ends)
    check('two-subsequent-turns-field-kind',after['kind']==(kind if caster_ends<2 else 0))
    if caster_ends==2:break
   check('two-native-caster-turns-reached',caster_ends==2)
   check('expired-field-coordinates-cleared',after['center']==[0,0])
   if display_checks:observe_field_display(e,False)
   capture(e,'expired',folder)
   outcomes.append(dict(action=action,empty=empty,sourceStateSha1=source_hash,saveSha1=hashlib.sha1(saved).hexdigest(),before=before,restored=restored,turns=turns,display=display))
  except BaseException:
   e.save(folder/'failure.state');e.screenshot(folder/'failure.png');(folder/'failure.ram').write_bytes(e.memory());raise
  finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],sourcePlaybackSha1=play['instrumentedSha1'],checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,
 inputs=dict(actions=[380,382],seed=0,centers=[[1,13],[2,12]],nativeWait=[32,32,256,256],maxMenus=36),
 limits=['Actual field publication/retirement is observed only when --display-checks is selected.','KO, Petrify, job change and battle-end cleanup have separate deterministic native-event coverage.'])
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
