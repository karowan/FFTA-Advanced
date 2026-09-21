"""Four Samurai strikes through fixed UI inputs, native P and cold save oracles."""
import sys
import ctypes as C,hashlib,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1];meta=json.loads((ROOT/('build/expansion/probes/job-state/current.json' if '--job-state' in sys.argv else 'build/expansion/probes/samurai/current.json')).read_text())
ROM=pathlib.Path(meta['path']);LAB=ROM.parent;FIX=LAB/'fixture';image=ROM.read_bytes()
assert hashlib.sha1(image).hexdigest()==meta['romSha1'] and (FIX/'frozen.gba').read_bytes()==image
control=bytearray(image);control[0x1300e2:0x1300f2]=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()[0x1300e2:0x1300f2]
CONTROL=LAB/'native-P-control.gba';CONTROL.write_bytes(control)
Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
from native_battle_wrappers import fixed_giza_formation
ACTOR,TARGET,AS,TS=0x80,0x33e4,0x1e98,0x1eb4;guard=bytes(8)+b'\xd7'*0xb4;checks=0;outcomes=[]
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
 check(r[0x3ff44:]==guard,('guard',label));return r
for action,item,ap,mp,num in [(347,376,144,4,110),(349,378,146,6,85),(352,381,149,6,100),(353,382,150,10,145)]:
 OUT=LAB/f'game-{action}';OUT.mkdir(exist_ok=True);initial=1 if action==347 else 5
 e=Emulator(ROM)
 try:
  e.load(FIX/'battle-ready.state');e.set_memory(0x3ff44,guard);ready_menu(e);fixed_giza_formation(image,e)
  for offset in (5,7,0x35):e.set_memory(ACTOR+offset,b'\x74')
  check(e.memory()[ACTOR+6]==1,'Samurai fixture must remain Human')
  e.set_memory(ACTOR+0x2a,struct.pack('<5H',item,0,0,0,0));e.set_memory(0x1b40+ap-144,b'\xff')
  for turn in range(4):
   previous=active(e)
   for key in (32,32,256,256):tap(e,key)
   ready_menu(e,previous)
  check(active(e)==0x02000000+ACTOR,('Marche not ready',hex(active(e))))
  e.set_memory(ACTOR+0x18,struct.pack('<HHHH',100,100,50,50));e.set_memory(ACTOR+0xe8,bytes(8));e.set_memory(AS,bytes([initial]))
  e.set_memory(TARGET+0x18,struct.pack('<HHHH',250,250,49,49));e.set_memory(TARGET+0xe8,bytes(8));e.set_memory(TS,b'\x01')
  ready=capture(e,'ready');stable=ready[0x1940:0x1e70]
  for key in (256,128,128,32):tap(e,key)
  tap(e,256,600)
  for key in (256,32,256):tap(e,key)
  capture(e,'ability-menu')
  for key in (256,128,256):tap(e,key)
  preview=capture(e,'preview');check(half(preview,0xf3fc)==action,('wrong action',action,half(preview,0xf3fc)))
  check(preview[AS]==initial and half(preview,ACTOR+0x1c)==50,'Preview consumed stance/MP')
  tap(e,1);cancel=capture(e,'cancelled');check(cancel[AS]==initial and cancel[TARGET:TARGET+264]==ready[TARGET:TARGET+264],'Cancel mutation')
  tap(e,256);tap(e,256);capture(e,'confirmation')
 finally:e.close()
 seen=set();success=None
 for seed in range(16):
  damages=[]
  for kind,path in [('native-P',CONTROL),('samurai',ROM)]:
   e=Emulator(path)
   try:
    e.load(OUT/'confirmation.state');C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4)
    tap(e,256,1500);r=capture(e,f'{kind}-{seed}');damage=250-half(r,TARGET+0x18);damages.append(damage)
    check(half(r,ACTOR+0x1c)==50-mp,('MP',action,seed))
    check(r[AS]==(13 if action==347 and damage else 1),('Centered grant/consume',action,seed,r[AS]))
    check(half(r,TARGET+0x1c)==(39 if action==349 and damage else 49),('Osafune MP',action,seed))
    if action==352:check((r[ACTOR+0xeb]&2,r[ACTOR+0xde])==(2,3),('Guarding Protect',seed))
    check(r[0x1940:0x1e70]==stable,'AP/inventory changed')
    if kind=='samurai':
     previous=active(e);tap(e,256,900);ready_menu(e,previous);turn=capture(e,f'next-turn-{seed}')
     check(turn[AS]==(5 if action==347 and damage else 1),('End-turn Centered',action,seed,turn[AS]))
     if damage:success=OUT/f'next-turn-{seed}.state'
   finally:e.close()
  factor=4 if action==347 else 5
  check(damages[1]==damages[0]*num*factor*6//2000,('One-round composition',action,seed,damages))
  outcomes.append(dict(action=action,seed=seed,P=damages[0],damage=damages[1]));seen.add(damages[1]>0)
  if seen=={False,True}:break
 check(seen=={False,True},('No bounded hit/miss coverage',action))
 e=Emulator(ROM)
 try:
  e.load(success);e.run(1);expected=capture(e,'save-ready')
  for key in (1,8,16,256,256):tap(e,key)
  before=e.memory(0);tap(e,256,300);saved=e.memory(0);check(saved!=before,'Save Now failed');(OUT/'suspended.sav').write_bytes(saved)
 finally:e.close()
 e=Emulator(ROM)
 try:
  e.set_memory(0,saved,0);e.run(3600);e.set_memory(0x3ff44,guard)
  for key,wait in [(8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)]:tap(e,key,wait)
  ready_menu(e);r=capture(e,'cold-resumed');check(r[AS]==expected[AS],'Cold Centered/Exposed')
  for unit in (ACTOR,TARGET):check(r[unit+0x18:unit+0x20]==expected[unit+0x18:unit+0x20],'Cold resources')
  check(r[0x1940:0x1e70]==stable,'Cold AP/inventory')
 finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],controlSha1=hashlib.sha1(control).hexdigest(),checks=checks,outcomes=outcomes,scope='Four Human Samurai actions, fixed menu/cancel/execute, bounded normal-RNG hit/miss, Centered plus Exposed one-round nativeP, turn completion and cold native SRAM resume')
(LAB/'game-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
