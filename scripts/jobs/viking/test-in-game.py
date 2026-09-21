"""Fixed native Bangaa menus, cancel, execution, turn completion and cold resume."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ctypes as C,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
from native_battle_wrappers import fixed_giza_formation
meta=_load_job_candidate(ROOT/'build/expansion/probes/viking/current.json');ROM=pathlib.Path(meta['path']);LAB=ROM.parent;FIX=LAB/'fixture';image=ROM.read_bytes()
assert hashlib.sha1(image).hexdigest()==meta['romSha1'] and (FIX/'frozen.gba').read_bytes()==image
Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
ACTOR,TARGET=0x398,0x33e4;guard=bytes(8)+b'\xd7'*0xb4;checks=0;outcomes=[]
half=lambda r,p:struct.unpack_from('<H',r,p)[0]
def check(ok,detail):
 global checks
 checks+=1;assert ok,detail
def tap(e,key,wait=180):e.run(8,key);e.run(wait)
def active(e):
 r=e.memory();manager=struct.unpack_from('<I',r,0xf438)[0]-0x02000000
 return struct.unpack_from('<I',r,manager+0x18)[0] if 0<=manager<0x3f7e0 else 0
def ready_menu(e,previous=None):
 for elapsed in range(0,9001,10):
  if observe['menu_visible'](e) and (previous is None or active(e)!=previous):return
  if elapsed<9000:e.run(10)
 raise AssertionError(('Actor/menu not ready',previous,hex(active(e))))
def capture(e,label):
 r=e.memory();e.save(OUT/f'{label}.state');e.screenshot(OUT/f'{label}.png');(OUT/f'{label}.ram').write_bytes(r)
 check(r[0x3ff44:]==guard,('guard',label));check(all(r[0x3f410+22*i+7]==0 for i in range(36)),('Transient accumulator at native UI boundary',label));return r
for action,item,ap,mp in [(365,392,91,6),(366,393,92,0),(367,394,93,6),(368,395,94,8),(369,396,95,12),(370,397,96,10),(371,398,97,20),(372,399,98,18),(373,448,99,6)]:
 OUT=LAB/f'game-{action}';OUT.mkdir(exist_ok=True)
 e=Emulator(ROM)
 try:
  e.load(FIX/'battle-ready.state');e.set_memory(0x3ff44,guard);ready_menu(e);fixed_giza_formation(image,e)
  check(active(e)==0x02000000+ACTOR,('Initial Bangaa not ready',hex(active(e))))
  check(e.memory()[ACTOR+6]==2,'Fixture actor must actually be Bangaa')
  for offset in (5,7,0x35):e.set_memory(ACTOR+offset,b'\x76')
  e.set_memory(ACTOR+0x2a,struct.pack('<5H',item,0,0,0,0));e.set_memory(ACTOR+0x40+91,bytes(14));e.set_memory(ACTOR+0x40+ap,b'\xff')
  e.set_memory(ACTOR+0x18,struct.pack('<4H',100,100,50,50));e.set_memory(ACTOR+0xe8,bytes(8))
  e.set_memory(TARGET+0x18,struct.pack('<4H',250,250,49,49));e.set_memory(TARGET+0xe8,bytes(8))
  if action in (367,370):e.set_memory(TARGET+0x2a,struct.pack('<5H',354 if action==367 else 288,0,0,0,0))
  initial=capture(e,'initial')
  for key in (256,128,128,128):tap(e,key)
  tap(e,256,600)
  for key in (256,32,256):tap(e,key)
  capture(e,'ability-menu')
  for key in ((256,256) if action==368 else (256,128,256)):tap(e,key)
  preview=capture(e,'preview');check(half(preview,0xf3fc)==action,('Wrong selected Reaving action',action,half(preview,0xf3fc)))
  check(half(preview,ACTOR+0x1c)==50,'Preview charged MP')
  tap(e,1);cancel=capture(e,'cancelled');check(cancel[TARGET:TARGET+264]==initial[TARGET:TARGET+264],'Cancel changed target')
  tap(e,256);tap(e,256);capture(e,'confirmation')
 finally:e.close()
 for seed in (0,3):
  e=Emulator(ROM)
  try:
   e.load(OUT/'confirmation.state');C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4)
   tap(e,256,1800);r=capture(e,f'executed-{seed}')
   check(half(r,ACTOR+0x1c)==50-mp,('One native payment',action,seed,half(r,ACTOR+0x1c)))
   check(r[ACTOR+0x40:ACTOR+0xce]==initial[ACTOR+0x40:ACTOR+0xce],('No AP per use',action))
   previous=active(e);tap(e,256,900);ready_menu(e,previous);capture(e,f'next-turn-{seed}')
   outcomes.append(dict(action=action,seed=seed,damage=250-half(r,TARGET+0x18),actorMP=half(r,ACTOR+0x1c),targetEquipment=list(struct.unpack_from('<5H',r,TARGET+0x2a))))
   if action==368 and seed==0:save_source=OUT/f'next-turn-{seed}.state'
  finally:e.close()
check(any(x['damage']>0 for x in outcomes),'Native damage must execute')
OUT=LAB/'cold-save';OUT.mkdir(exist_ok=True);e=Emulator(ROM)
try:
 e.load(save_source);e.run(1);expected=capture(e,'before-save')
 for key in (1,8,16,256,256):tap(e,key)
 before=e.memory(0);tap(e,256,300);saved=e.memory(0);check(saved!=before,'Native Save Now failed');(OUT/'suspended.sav').write_bytes(saved)
finally:e.close()
e=Emulator(ROM)
try:
 e.set_memory(0,saved,0);e.run(3600);e.set_memory(0x3ff44,guard)
 for key,wait in [(8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)]:tap(e,key,wait)
 ready_menu(e);r=capture(e,'cold-resumed')
 for unit in (ACTOR,TARGET):
  check(r[unit+0x18:unit+0x20]==expected[unit+0x18:unit+0x20],'Cold resources')
 check(r[ACTOR+0x2a:ACTOR+0xce]==expected[ACTOR+0x2a:ACTOR+0xce],'Cold equipment, commands and AP')
 check(r[0x3f410:0x3f728]==expected[0x3f410:0x3f728],'Cold owned job state')
 check(all(r[0x3f410+22*i+7]==0 for i in range(36)),'No in-flight critical accumulator in suspend')
finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],checks=checks,outcomes=outcomes,scope=__doc__)
(LAB/'game-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
