"""Fixed native UI Dark Mind selection/cancel/execution and cold save replay."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ctypes as C,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
meta=_load_job_candidate(ROOT/'build/expansion/probes/dark-knight/current.json')
ROM=pathlib.Path(meta['path']);LAB=ROM.parent;FIX=LAB/'fixture';image=ROM.read_bytes()
assert hashlib.sha1(image).hexdigest()==meta['romSha1'] and (FIX/'frozen.gba').read_bytes()==image
Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
from native_battle_wrappers import fixed_giza_formation
half=lambda r,p:struct.unpack_from('<H',r,p)[0]
checks=0;outcomes=[];guard=bytes(8)+b'\xd7'*0xb4
blood='--blood' in sys.argv;action=356 if blood else 359;tag='blood-edge' if blood else 'dark-mind'
if blood:
 control=bytearray(image);addr=meta['symbols']['ffta_physical_final']-0x08000000;control[addr:addr+2]=bytes.fromhex('7047')
 CONTROL=LAB/'blood-native-P.gba';CONTROL.write_bytes(control)
def check(ok,detail):
 global checks
 checks+=1;assert ok,detail
def tap(e,key,wait=180):e.run(8,key);e.run(wait)
def active(e):
 r=e.memory();manager=struct.unpack_from('<I',r,0xf438)[0]-0x02000000
 return struct.unpack_from('<I',r,manager+0x18)[0] if 0<=manager<0x3f7e0 else 0
def ready(e,previous=None):
 for elapsed in range(0,9001,10):
  if observe['menu_visible'](e) and (previous is None or active(e)!=previous):return
  if elapsed<9000:e.run(10)
 raise AssertionError(('menu timeout',previous,active(e)))
def capture(e,label):
 r=e.memory();e.save(OUT/f'{label}.state');e.screenshot(OUT/f'{label}.png');(OUT/f'{label}.ram').write_bytes(r)
 check(r[0x3ff44:]==guard,('transient guard',label));return r
for job,race,actor,index in ((119,2,0x398,80),(117,1,0x80,161)):
 if blood:index-=3
 OUT=LAB/f'{tag}-game-{job}';OUT.mkdir(exist_ok=True);e=Emulator(ROM)
 try:
  e.load(FIX/'battle-ready.state');e.set_memory(0x3ff44,guard);ready(e);fixed_giza_formation(image,e)
  check(e.memory()[actor+6]==race,('fixture race',job))
  for offset in (5,7,0x35):e.set_memory(actor+offset,bytes((job,)))
  e.set_memory(actor+0x2a,struct.pack('<5H',384 if blood else 0,0,0,0,0))
  ap=actor+0x40+index if race==2 else 0x1b40+index-144
  e.set_memory(ap,b'\xff')
  if actor==0x80:
   for turn in range(4):
    previous=active(e)
    for key in (32,32,256,256):tap(e,key)
    ready(e,previous)
  check(active(e)==0x02000000+actor,('wrong actor',job,active(e)))
  e.set_memory(actor+0x18,struct.pack('<HHHH',100 if blood else 50,200,50,50));e.set_memory(actor+0xe8,bytes(8))
  if blood:
   e.set_memory(0x33e4+0x18,struct.pack('<HHHH',999,999,49,49));e.set_memory(0x33e4+0xe8,bytes(8))
  before=capture(e,'ready');stable=before[0x1940:0x1e70]
  for key in ((256,128,128,128) if actor==0x398 else (256,128,128,32)):tap(e,key)
  tap(e,256,600)
  # Native Act -> Dark Arts -> only learned active -> self preview.
  for key in (256,32,256):tap(e,key)
  capture(e,'ability-menu')
  tap(e,256)
  if blood:tap(e,128)
  tap(e,256);preview=capture(e,'preview')
  check(half(preview,0xf3fc)==action,('selected wrong action',job,half(preview,0xf3fc)))
  check(preview[actor+0x18:actor+0x20]==before[actor+0x18:actor+0x20],'preview spent resources')
  tap(e,1);cancel=capture(e,'cancelled')
  check(cancel[actor+0x18:actor+0x20]==before[actor+0x18:actor+0x20],'cancel spent resources')
  tap(e,256);tap(e,256);capture(e,'confirmation')
  if blood:C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',3),4)
  tap(e,256,1500)
  result=capture(e,'executed')
  expected_resources=(80,50) if blood else (90,42)
  check((half(result,actor+0x18),half(result,actor+0x1c))==expected_resources,('actual recovery/payment',job,half(result,actor+0x18),half(result,actor+0x1c)))
  if not blood:check((result[actor+0xeb]&1,result[actor+0xdd])==(1,3),'native Shell')
  check(result[0x1940:0x1e70]==stable,'AP/inventory mutation')
  previous=active(e);tap(e,256,900);ready(e,previous);expected=capture(e,'save-ready')
  for key in (1,8,16,256,256):tap(e,key)
  old=e.memory(0);tap(e,256,300);saved=e.memory(0);check(saved!=old,'native Save Now failed')
  (OUT/'suspended.sav').write_bytes(saved)
 finally:e.close()
 if blood:
  seen=set()
  for seed in range(8):
   values=[]
   for kind,path in (('reference',CONTROL),('candidate',ROM)):
    e=Emulator(path)
    try:
     e.load(OUT/'confirmation.state');C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4)
     tap(e,256,1500);r=capture(e,f'{kind}-{seed}');values.append(999-half(r,0x33e4+0x18))
     check((half(r,actor+0x18),half(r,actor+0x1c))==(80,50),'hit and miss pay exactly once')
    finally:e.close()
   check(values[1]==min(999,values[0]*150//100),('independent actual native P',job,seed,values))
   seen.add(values[1]>0)
  check(True in seen,('no fixed hit coverage',job))
 e=Emulator(ROM)
 try:
  e.set_memory(0,saved,0);e.run(3600);e.set_memory(0x3ff44,guard)
  for key,wait in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):tap(e,key,wait)
  ready(e);r=capture(e,'cold-resumed')
  check(r[actor+0x18:actor+0x20]==expected[actor+0x18:actor+0x20],'cold resources')
  check((r[actor+0xeb]&1,r[actor+0xdd])==(expected[actor+0xeb]&1,expected[actor+0xdd]),'cold native Shell')
  check(r[0x1940:0x1e70]==stable,'cold AP/inventory')
 finally:e.close()
 outcomes.append(dict(job=job,race=race,action=action,HP=expected_resources[0],MP=expected_resources[1],coldSave=True))
report=dict(passed=True,romSha1=meta['romSha1'],checks=checks,outcomes=outcomes)
(LAB/f'{tag}-in-game.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
