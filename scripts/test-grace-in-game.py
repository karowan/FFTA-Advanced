"""Grace real battle A preview/commit, with explicit hostile Archer fixture."""
import ctypes as C,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'build/expansion/probes'
meta=json.loads((P/'grace/current.json').read_text());ROM=pathlib.Path(meta['path']);LAB=ROM.parent;FIX=LAB/'fixture'
if '--current' in sys.argv:
 FIX=P/'battle-fixture';assert hashlib.sha1((P/'combat.gba').read_bytes()).hexdigest()==meta['romSha1'],'Run test-grace-native.py --current first'
if '--fixture' in sys.argv:FIX=pathlib.Path(sys.argv[sys.argv.index('--fixture')+1]).resolve()
assert hashlib.sha1((FIX/'frozen.gba').read_bytes()).hexdigest()==meta['romSha1']
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'));ACTOR,TARGET=0x398,0x33e4;guard=b'\xd7'*0xbc;checks=0;outcomes=[];previews=[]
observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
rom=ROM.read_bytes();control=(LAB/'control.gba').read_bytes();oracle=bytearray(control);oracle[0x3a8444:0x3a8448]=bytes([1]*4);(LAB/'frontal-oracle.gba').write_bytes(oracle)
def half(r,p):return struct.unpack_from('<H',r,p)[0]
def check(ok,detail):
 global checks
 checks+=1;assert ok,detail
def tap(e,k,w=180):e.run(8,k);e.run(w)
def face(e,facing):
 # Native preview B56A8 reads wrapper+1F and temporarily replaces unit+F8.
 r=e.memory();wrapper=WRAPPER;check(struct.unpack_from('<I',r,wrapper)[0]==0x02000000+TARGET,'Target wrapper changed')
 e.set_memory(wrapper+0x1f,bytes([facing]));e.set_memory(TARGET+0xf8,bytes([facing]))
def capture(e,label):
 r=e.memory();e.save(OUT/(label+'.state'));e.screenshot(OUT/(label+'.png'));(OUT/(label+'.ram')).write_bytes(r);check(r[0x3ff44:]==guard,('guard',label));return r
for action,item,index in ((357,385,78),(358,386,79)):
 OUT=LAB/f'game-{action}';OUT.mkdir(exist_ok=True);e=h['Emulator'](ROM)
 try:
  e.load(FIX/'battle-ready.state');e.run(1)
  for off in (5,7,0x35):e.set_memory(ACTOR+off,b'\x77')
  e.set_memory(ACTOR+0x2a,struct.pack('<5H',item,0,0,0,0));e.set_memory(ACTOR+0x40+index,b'\xff')
  r=e.memory();target=bytearray(r[0x5a8:0x5a8+264]);target[0x28:0x2a]=r[TARGET+0x28:TARGET+0x2a];target[0xf6:0xf9]=bytes([5,14,0]);target[0x3b]=94;target[0x40+94]=0xff;target[0xe8:0xf0]=bytes(8)
  struct.pack_into('<HHHH',target,0x18,250,250,49,49);e.set_memory(TARGET,bytes(target));e.set_memory(ACTOR+0x18,struct.pack('<HHHH',20,100,20,50))
  for k in (256,128,128,128):tap(e,k)
  tap(e,256,600)
  for k in (256,32,256,256,128):tap(e,k)
  capture(e,'target-selected')
 finally:e.close()
 # Resolve the actual wrapper through the native UI caller, rather than a
 # heap address tied to this frozen build. This preflight does not commit.
 trap=bytearray(control);trap[0x2b8cc:0x2b8ce]=b'\xfe\xe7';path=OUT/'wrapper-trap.gba';path.write_bytes(trap);e=h['Emulator'](path)
 try:
  e.load(OUT/'target-selected.state');tap(e,256,60);p=OUT/'wrapper-trap.state';e.save(p);regs=struct.unpack_from('<17I',p.read_bytes(),0x20)
  check(regs[15]==0x0802b8ce,'Wrapper preflight missed native display');WRAPPER=regs[6]-0x02000000
  check(struct.unpack_from('<I',e.memory(),WRAPPER)[0]==0x02000000+TARGET,'Wrong defender wrapper')
 finally:e.close()
 for facing in range(4):
  displayed={};damage={}
  for kind,data in (('ordinary',control),('oracle',oracle),('grace',rom)):
   trap=bytearray(data);trap[0x2b8cc:0x2b8ce]=b'\xfe\xe7';path=OUT/f'{kind}-trap.gba';path.write_bytes(trap);e=h['Emulator'](path)
   try:
    e.load(OUT/'target-selected.state');face(e,facing);tap(e,256,60);p=OUT/f'{kind}-{facing}-display.state';e.save(p);regs=struct.unpack_from('<17I',p.read_bytes(),0x20)
    check(regs[15]==0x0802b8ce,('display path',action,kind,facing,hex(regs[15])));displayed[kind]=regs[1];damage[kind]=regs[2]
   finally:e.close()
  check(displayed['grace']==displayed['oracle'],('Frontal preview',displayed));check(len(set(damage.values()))==1,('Grace changed damage',damage));previews.append(dict(action=action,facing=facing,chance=displayed,damage=damage))
  pair=[]
  for kind,path in (('oracle',LAB/'frontal-oracle.gba'),('grace',ROM)):
   e=h['Emulator'](path)
   try:
    e.load(OUT/'target-selected.state');face(e,facing);before=e.memory();tap(e,256);r=capture(e,f'{kind}-{facing}-preview')
    check(half(r,0xf3fc)==action,'Wrong action');check(r[TARGET:TARGET+264]==before[TARGET:TARGET+264],'Preview mutation');tap(e,1);r=capture(e,f'{kind}-{facing}-cancel');check(r[TARGET:TARGET+264]==before[TARGET:TARGET+264],'Cancel mutation')
    tap(e,256);tap(e,256);capture(e,f'{kind}-{facing}-confirm');results=[]
    for seed in (0,1):
     e.load(OUT/f'{kind}-{facing}-confirm.state');C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4);tap(e,256,1500);r=capture(e,f'{kind}-{facing}-seed{seed}');results.append((r[ACTOR+0x18:ACTOR+0x20].hex(),r[TARGET+0x18:TARGET+0x20].hex()))
     check(r[TARGET+0x3b]==94 and r[TARGET+0x40+94]==0xff,'Support/mastery changed');check(r[TARGET+0xf6:TARGET+0xf8]==bytes([5,14]),'Target displaced');check(r[0x1940:0x1e70]==before[0x1940:0x1e70],'Inventory/AP changed')
     outcomes.append(dict(action=action,kind=kind,facing=facing,seed=seed,damage=250-half(r,TARGET+0x18),actorHP=half(r,ACTOR+0x18),actorMP=half(r,ACTOR+0x1c)));tap(e,256,900)
    pair.append(results)
    if kind=='grace' and facing==3:
     capture(e,'before-save-wait');observe['wait_for_menu'](e,limit=9000)
     expected=capture(e,'save-menu-ready');old=e.memory(0)
     for k in (1,8,16,256,256):tap(e,k)
     tap(e,256,300);saved=e.memory(0);capture(e,'save-complete');check(saved!=old,'Native Save Now did not write');(OUT/'suspended.sav').write_bytes(saved)
   finally:e.close()
  check(pair[0]==pair[1],('Native frontal commit differs',action,facing,pair))
 e=h['Emulator'](ROM)
 try:
  e.set_memory(0,saved,0);e.run(3600);e.set_memory(0x3ff44,guard)
  for k,w in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):tap(e,k,w)
  resumed=capture(e,'cold-resumed')
  for unit in (ACTOR,TARGET):check(resumed[unit+0x18:unit+0x20]==expected[unit+0x18:unit+0x20],'Cold resource persistence')
  check(resumed[TARGET+0x3b]==94 and resumed[TARGET+0x40+94]==0xff,'Cold Grace mastery/equipment')
  check(resumed[0x1940:0x1e70]==expected[0x1940:0x1e70],'Cold AP/inventory')
 finally:e.close()
check(any(p['chance']['ordinary']!=p['chance']['grace'] for p in previews),'Vacuous facing changes')
check(any(x['damage']>0 for x in outcomes) and any(x['damage']==0 for x in outcomes),'No hit/miss coverage')
report=dict(passed=True,romSha1=meta['romSha1'],checks=checks,previews=previews,outcomes=outcomes,fixture='Fresh battle; hostile target explicitly replaced by native Viera Archer record, Grace lesson94 mastered. Native movement/target/preview/cancel/commit inputs; independent native frontal table control.')
(LAB/'game-report.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='outcomes'},indent=2))
