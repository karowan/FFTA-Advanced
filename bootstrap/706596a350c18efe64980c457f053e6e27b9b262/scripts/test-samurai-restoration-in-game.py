"""Fixed UI/cross/ally/Silence/save tests for Murasame and Kiyomori."""
import ctypes as C,hashlib,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1];meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text())
ROM=pathlib.Path(meta['path']);LAB=ROM.parent;FIX=LAB/'fixture';image=ROM.read_bytes()
assert hashlib.sha1(image).hexdigest()==meta['romSha1'] and (FIX/'frozen.gba').read_bytes()==image
Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
from native_battle_wrappers import fixed_giza_formation
ACTOR,ALLY,ENEMY,AS=0x80,0x188,0x33e4,0x1e98;guard=bytes(4)+b'\xd7'*0xb8;checks=0;outcomes=[]
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

def selected_center(out,expected):
 # Pause a diagnostic copy at the real executor entry. The production image
 # separately executes this same saved confirmation without instrumentation.
 trial=bytearray(image);trial[0xa433c:0xa433e]=b'\xfe\xe7';path=out/'center-trap.gba';path.write_bytes(trial)
 e=Emulator(path)
 try:
  e.load(out/'confirmation.state');tap(e,256,300);state=out/'center-trap.state';e.save(state)
  regs=struct.unpack_from('<17I',state.read_bytes(),0x20)
  check(regs[15]==0x080a433e,('center breakpoint',hex(regs[15])))
  check(tuple(regs[2:4])==expected,('selected center',expected,tuple(regs[2:4])))
 finally:e.close()
for action,center in [(350,'between-allies'),(350,'self-with-enemy'),(351,'self')]:
 OUT=LAB/f'game-{action}-{center}';OUT.mkdir(exist_ok=True);e=Emulator(ROM)
 try:
  e.load(FIX/'battle-ready.state');e.set_memory(0x3ff44,guard);e.run(1);ready_menu(e);fixed_giza_formation(image,e)
  for offset in (5,7,0x35):e.set_memory(ACTOR+offset,b'\x74')
  e.set_memory(ACTOR+0x2a,struct.pack('<5H',379 if action==350 else 380,0,0,0,0));e.set_memory(0x1b40+(147 if action==350 else 148)-144,b'\xff')
  for turn in range(4):
   previous=active(e)
   for key in (32,32,256,256):tap(e,key)
   ready_menu(e,previous)
  check(active(e)==0x02000000+ACTOR,('Marche not ready',hex(active(e))))
  for unit,hp,maximum in [(ACTOR,50,100),(ALLY,100,250),(ENEMY,100,250)]:
   e.set_memory(unit+0x18,struct.pack('<HHHH',hp,maximum,50,50));e.set_memory(unit+0xe8,bytes(8))
  e.set_memory(AS,b'\x05');e.set_memory(ACTOR+0xeb,b'\x08') # Actual Silence, not just a metadata assertion.
  e.set_memory(ALLY+0xeb,b'\x04') # Reflect must not redirect either technique.
  ready=capture(e,'ready');stable=ready[0x1940:0x1e70]
  moves=(256,128,128,32) if action==350 else (256,128,32)
  for key in moves:tap(e,key)
  tap(e,256,600)
  for key in (256,32,256):tap(e,key)
  capture(e,'ability-menu');tap(e,256)
  if center=='between-allies':tap(e,64)
  capture(e,'target-area')
  if action==350:tap(e,256)
  preview=capture(e,'preview')
  check(half(preview,0xf3fc)==action,('wrong action',action,half(preview,0xf3fc)))
  for unit in (ACTOR,ALLY,ENEMY):check(preview[unit+0x18:unit+0x20]==ready[unit+0x18:unit+0x20],'Preview resources')
  check(preview[AS]==5,'Preview consumed Centered');tap(e,1);cancel=capture(e,'cancelled')
  check(cancel[AS]==5 and half(cancel,ACTOR+0x1c)==50,'Cancel consumed state/MP')
  # Native cancellation recenters on a recipient. Restore the observed
  # pre-cancel preview so execution tests the originally selected area.
  e.load(OUT/'preview.state');e.run(1);tap(e,256);capture(e,'confirmation')
 finally:e.close()
 selected_center(OUT,(4,14) if center=='self-with-enemy' else (3,14))
 for seed in (0,1):
  e=Emulator(ROM)
  try:
   e.load(OUT/'confirmation.state');C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4)
   tap(e,256,1500);r=capture(e,f'executed-{seed}')
   check(half(r,ACTOR+0x1c)==(42 if action==350 else 40),('single MP cost',action,seed))
   check(half(r,ENEMY+0x18)==100 and r[ENEMY+0xeb]&3==0,'Enemy affected by allied cross')
   if action==350:
    check(half(r,ACTOR+0x18)==93,('self heal',center,seed,half(r,ACTOR+0x18)))
    check(half(r,ALLY+0x18)==(209 if center=='between-allies' else 100),('ally cross heal',center,seed,half(r,ALLY+0x18)))
    check(r[AS]==1,'Murasame must consume Centered once')
   else:
    for unit in (ACTOR,ALLY):check((r[unit+0xeb]&3,r[unit+0xdd],r[unit+0xde])==(3,3,3),('Protect/Shell cross',unit,seed))
    check(r[AS]==5,'Kiyomori consumed Centered')
   check(r[0x1940:0x1e70]==stable,'AP/inventory changed')
   previous=active(e);tap(e,256,900);ready_menu(e,previous);turn=capture(e,f'next-turn-{seed}')
   check(turn[AS]==(1 if action==350 else 3),'Centered retirement/end-turn count')
   outcomes.append(dict(action=action,center=center,seed=seed,actorHP=half(r,ACTOR+0x18),allyHP=half(r,ALLY+0x18),actorMP=half(r,ACTOR+0x1c)))
  finally:e.close()
 e=Emulator(ROM)
 try:
  e.load(OUT/'next-turn-1.state');e.run(1);expected=capture(e,'save-ready')
  for key in (1,8,16,256,256):tap(e,key)
  before=e.memory(0);tap(e,256,300);saved=e.memory(0);check(saved!=before,'Save Now failed');(OUT/'suspended.sav').write_bytes(saved)
 finally:e.close()
 e=Emulator(ROM)
 try:
  e.set_memory(0,saved,0);e.run(3600);e.set_memory(0x3ff44,guard)
  for key,wait in [(8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)]:tap(e,key,wait)
  ready_menu(e);r=capture(e,'cold-resumed');check(r[AS]==expected[AS],'Cold Centered/Exposed')
  for unit in (ACTOR,ALLY,ENEMY):
   check(r[unit+0x18:unit+0x20]==expected[unit+0x18:unit+0x20],'Cold resources')
   check(r[unit+0xdc:unit+0xf0]==expected[unit+0xdc:unit+0xf0],'Cold status/timers')
  check(r[0x1940:0x1e70]==stable,'Cold AP/inventory')
 finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],checks=checks,outcomes=outcomes,scope='Actual Silence/Reflect, empty-center ally cross, self-center enemy exclusion, Murasame percentage healing, Kiyomori native buffs, preview/cancel, one payment/Centered, native turns and cold SRAM resume')
(LAB/'restoration-game-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
