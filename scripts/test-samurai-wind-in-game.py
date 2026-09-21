"""Deterministic Wind Draw menu, recipient, hit/miss and Centered execution."""
import ctypes as C,hashlib,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1];meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text());ROM=pathlib.Path(meta['path']);LAB=ROM.parent;FIX=LAB/'fixture';image=ROM.read_bytes()
assert hashlib.sha1(image).hexdigest()==meta['romSha1'] and (FIX/'frozen.gba').read_bytes()==image
Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
from native_battle_wrappers import fixed_giza_formation
ACTOR,AS=0x80,0x1e98;targets=(0x33e4,0x32dc,0x31d4);checks=0;outcomes=[];guard=bytes(4)+b'\xd7'*0xb8
half=lambda r,p:struct.unpack_from('<H',r,p)[0]
word=lambda r,p:struct.unpack_from('<I',r,p)[0]
def check(ok,detail):
 global checks
 checks+=1;assert ok,detail
def tap(e,k,wait=180):e.run(8,k);e.run(wait)
def active(e):
 r=e.memory();p=word(r,0xf438)-0x02000000
 return word(r,p+0x18) if 0<=p<0x3f7e0 else 0
def menu(e,previous=None):
 for t in range(901):
  if observe['menu_visible'](e) and (previous is None or active(e)!=previous):return
  e.run(10)
 raise AssertionError(('menu timeout',hex(active(e))))
def capture(e,d,label):
 r=e.memory();e.save(d/f'{label}.state');e.screenshot(d/f'{label}.png');(d/f'{label}.ram').write_bytes(r);check(r[0x3ff44:]==guard,('guard',label));return r
from native_battle_wrappers import from_emulator

def place(e,unit,wrapper,x,y):
 check(word(e.memory(),wrapper)==0x02000000+unit,('wrapper',hex(unit),hex(wrapper)))
 e.set_memory(unit+0xf6,bytes((x,y)));e.set_memory(wrapper+8,struct.pack('<3H',x*32+16,32,y*32+16))
for facing,blocked,friendly in [(f,False,False) for f in range(4)]+[(3,True,False),(3,False,True)]:
 dx,dy,key=((0,1,32),(-1,0,64),(0,-1,16),(1,0,128))[facing]
 d=LAB/f'wind-game-{facing}-block{blocked}-ally{friendly}';d.mkdir(exist_ok=True);e=Emulator(ROM)
 try:
  e.load(FIX/'battle-ready.state');e.set_memory(0x3ff44,guard);e.run(1);menu(e);fixed_giza_formation(image,e)
  for offset in (5,7,0x35):e.set_memory(ACTOR+offset,b'\x74')
  e.set_memory(ACTOR+0x2a,struct.pack('<5H',377,0,0,0,0));e.set_memory(0x1b41,b'\xff')
  for turn in range(4):
   previous=active(e)
   for k in (32,32,256,256):tap(e,k)
   menu(e,previous)
  check(active(e)==0x02000080,'Marche ready')
  wrappers=from_emulator(image,e)
  grid=word(e.memory(),0x7f14)-0x02000000
  for y in range(3,11):
   for x in range(3,11):e.set_memory(grid+2*(y*16+x),bytes((2,0)))
  place(e,ACTOR,wrappers[ACTOR],5,5)
  for unit,wrapper,distance in zip(targets,tuple(wrappers[u] for u in targets),(1,2,3)):
   place(e,unit,wrapper,6+dx*distance,6+dy*distance);e.set_memory(unit+0x18,struct.pack('<HHHH',999,999,50,50));e.set_memory(unit+0xe8,bytes(8));e.set_memory(unit+0x3a,bytes(2))
  if friendly:e.set_memory(targets[1]+0x28,struct.pack('<H',half(e.memory(),targets[1]+0x28)&0x7fff))
  if blocked:e.set_memory(grid+2*((6+dy*2)*16+6+dx*2),bytes((5,0)))
  e.set_memory(ACTOR+0x18,struct.pack('<HHHH',100,100,50,50));e.set_memory(ACTOR+0xe8,bytes(8));e.set_memory(ACTOR+0xeb,b'\x08');e.set_memory(AS,b'\x05')
  before=capture(e,d,'ready')
  for k in (256,128,32):tap(e,k)
  tap(e,256,600)
  for k in (256,32,256):tap(e,k)
  capture(e,d,'ability-menu');tap(e,256);tap(e,key);capture(e,d,'target-area');tap(e,256);preview=capture(e,d,'preview')
  check(half(preview,0xf3fc)==348,('action',half(preview,0xf3fc)));check(preview[AS]==5 and half(preview,ACTOR+0x1c)==50,'preview consumes')
  tap(e,1);cancel=capture(e,d,'cancelled');check(cancel[AS]==5 and half(cancel,ACTOR+0x1c)==50,'cancel consumes')
  e.load(d/'preview.state');e.run(1);tap(e,256);capture(e,d,'confirmation')
 finally:e.close()
 trial=bytearray(image);trial[0xa24a8:0xa24aa]=b'\xfe\xe7';trap=d/'member-trap.gba';trap.write_bytes(trial);e=Emulator(trap)
 try:
  e.load(d/'confirmation.state');tap(e,256,300);r=capture(e,d,'member-trap');regs=struct.unpack_from('<17I',(d/'member-trap.state').read_bytes(),0x20)
  check(regs[15]==0x080a24aa,('member breakpoint',hex(regs[15])));obj=regs[9]-0x02000000;count=word(r,obj+0x2c0);check(count<=15,'member bounds')
  members=[word(r,word(r,obj+0x20+i*0x2c)-0x02000000) for i in range(count)]
  allowed={0x02000000+u for u in targets[:1 if blocked else 3]};ally={0x02000000+targets[1]} if friendly else set()
  check(set(members)<=allowed and set(members)-ally==allowed-ally,('recipient set',members))
 finally:e.close()
 raw=bytearray(image);raw[0x1300e2:0x1300f2]=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()[0x1300e2:0x1300f2];p=d/'reference.gba';p.write_bytes(raw)
 for seed in (0,1):
  results=[]
  for rom,label in ((p,'reference'),(ROM,'production')):
   e=Emulator(rom)
   try:
    e.load(d/'confirmation.state');C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4);tap(e,256,2000);r=capture(e,d,f'{label}-{seed}');results.append(r)
   finally:e.close()
  reference,r=results
  for unit in targets:
   damage=999-half(r,unit+0x18);base=999-half(reference,unit+0x18)
   check(damage==base*5//4,('native P with Centered',blocked,seed,unit,damage,base))
   if friendly and unit==targets[1]:check(damage==0,'Wind damaged an ally in the line')
  check(half(r,ACTOR+0x1c)==46 and r[AS]==1,'one MP cost/Centered consumption')
  check(r[0x1940:0x1e70]==before[0x1940:0x1e70],'AP/inventory')
  outcomes.append(dict(facing=facing,blocked=blocked,friendly=friendly,seed=seed,damage=[999-half(r,u+0x18) for u in targets]))
 e=Emulator(ROM)
 try:
  e.load(d/'production-1.state');e.run(1);previous=active(e);tap(e,256,900);menu(e,previous);expected=capture(e,d,'next-turn')
  check(expected[AS]==1,'Wind end-turn state')
  if not friendly:continue
  for k in (1,8,16,256,256):tap(e,k)
  before_save=e.memory(0);tap(e,256,300);saved=e.memory(0);check(saved!=before_save,'native suspend save');(d/'suspended.sav').write_bytes(saved)
 finally:e.close()
 if friendly:
  e=Emulator(ROM)
  try:
   e.set_memory(0,saved,0);e.run(3600);e.set_memory(0x3ff44,guard)
   for k,wait in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):tap(e,k,wait)
   menu(e);r=capture(e,d,'cold-resumed');check(r[AS]==expected[AS],'cold Centered')
   for unit in (ACTOR,*targets):
    check(r[unit+0x18:unit+0x20]==expected[unit+0x18:unit+0x20],'cold resources')
    check(r[unit+0xf6:unit+0xf8]==expected[unit+0xf6:unit+0xf8],'cold positions')
   check(r[0x1940:0x1e70]==before[0x1940:0x1e70],'cold AP/inventory')
  finally:e.close()
check(any(any(v for v in o['damage']) for o in outcomes),'No successful hits exercised')
check(any(not any(o['damage']) for o in outcomes),'No complete miss exercised')
report=dict(passed=True,romSha1=meta['romSha1'],checks=checks,outcomes=outcomes,scope='All four directions after native Move, line obstruction, ally exclusion, actual hit/miss and native P, Centered once, Silence, preview/cancel, turns, MP/AP/inventory and cold native suspend resume')
(LAB/'wind-game-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
