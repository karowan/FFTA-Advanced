"""Fresh native Light Foot movement on an Archer, cancellation and cold resume."""
import ast,ctypes as C,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'build/expansion/probes/mobility-supports'
CURRENT='--current' in sys.argv
if CURRENT:OUT=OUT/'current'/hashlib.sha1((ROOT/'build/expansion/probes/combat.gba').read_bytes()).hexdigest()
ROM=OUT/'isolated.gba'
report=json.loads((OUT/'report.json').read_text());assert hashlib.sha1(ROM.read_bytes()).hexdigest()==report['romSha1']
FIX=ROOT/'build/expansion/probes/battle-fixture' if CURRENT else OUT/'battle';fixture=json.loads((FIX/'report.json').read_text()) if (FIX/'report.json').exists() else None
assert (FIX/'frozen.gba').read_bytes()==ROM.read_bytes()
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];checks={};results=[]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
RETURN,STACK=0x08000100,0x03007000
rom=ROM.read_bytes()
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native actor harness>','exec'))
# Import only the validated native enumerator, never another test's execution.
tree=ast.parse((ROOT/'scripts/test-arcs-in-game.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='native_wrappers'],type_ignores=[]),'<native actor enumeration>','exec'))
def check(k,a,b):
 assert a==b,(k,a,b)
 checks[k]=checks.get(k,0)+1
def tap(e,k,w=180):e.run(8,k);e.run(w)
def u32(b,p):return struct.unpack_from('<I',b,p)[0]
def shot(e,d,name):
 b=e.memory();e.screenshot(d/(name+'.png'));e.save(d/(name+'.state'));(d/(name+'.ram')).write_bytes(b)
 check('reserved_guard',b[0x3ff44:],b'\xd7'*0xbc);return b
def location(b):
 check('moving_wrapper_identity',u32(b,moving_wrapper),0x020005a8)
 return tuple(struct.unpack_from('<H',b,moving_wrapper+p)[0]//32 for p in (8,12))
for enabled in (False,True):
 d=OUT/('enabled' if enabled else 'control');d.mkdir(exist_ok=True);e=E(ROM)
 try:
  e.load(FIX/'battle-ready.state');e.run(1)
  moving_wrapper=native_wrappers(e)[0x5a8]
  check('external_Archer_job',e.memory()[0x5af],33)
  e.set_memory(0x5a8+0x40+95,b'\xa3');e.set_memory(0x5a8+0x3b,bytes((95 if enabled else 0,)))
  for k in (32,32,256):tap(e,k)
  tap(e,256,900);before=shot(e,d,'turn')
  check('Colette_turn',u32(before,u32(before,0xf438)-0x02000000+24),0x020005a8)
  tap(e,256)
  for _ in range(5):tap(e,16)
  shot(e,d,'fifth_tile');tap(e,256,900);moved=shot(e,d,'move_attempt')
  check('five_tile_destination',location(moved),(0,9) if enabled else (0,14))
  check('movement_no_resource_cost',moved[0x5c0:0x5c8],before[0x5c0:0x5c8])
  check('equipment_AP_preserved',moved[0x5d2:0x6b0],before[0x5d2:0x6b0])
  if not enabled:
   tap(e,1);shot(e,d,'cancelled');continue
  # A completed but uncommitted Move remains cancellable under native rules.
  tap(e,1,600);cancel=shot(e,d,'cancelled');check('cancel_returns_origin',location(cancel),(0,14))
  for _ in range(5):tap(e,16)
  tap(e,256,900);shot(e,d,'removed')
  for k in (32,256):tap(e,k)
  tap(e,256,900);after=shot(e,d,'next_turn')
  check('turn_advances_once',u32(after,u32(after,0xf438)-0x02000000+24),0x020004a0)
  check('committed_unit_position',after[0x69e:0x6a0],bytes((0,9)))
  for k in (1,8,16,256,256):tap(e,k)
  old=e.memory(0);tap(e,256,300);saved=e.memory(0);check('native_suspend_written',saved!=old,True);(d/'suspended.sav').write_bytes(saved)
  expected=after
 finally:e.close()
e=E(ROM);d=OUT/'enabled'
try:
 e.set_memory(0,saved,0);e.run(3600);e.set_memory(0x3ff44,b'\xd7'*0xbc)
 for k,w in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):tap(e,k,w)
 cold=shot(e,d,'cold_resumed')
 check('cold_S_AP_gear',cold[0x5d2:0x69e],expected[0x5d2:0x69e]);check('cold_position',cold[0x69e:0x6a0],bytes((0,9)))
 tap(e,32);tap(e,256);shot(e,d,'cold_interactive')
finally:e.close()
result={'passed':True,'romSha1':report['romSha1'],'checks':sum(checks.values()),'groups':checks,'scope':__doc__}
(OUT/'in-game.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
