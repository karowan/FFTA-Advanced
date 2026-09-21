"""Fresh native Executioner UI, live HP threshold and independent P control."""
import ctypes as C,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
FIX=ROOT/'build/expansion/probes/battle-fixture'
if '--fixture' in sys.argv:FIX=pathlib.Path(sys.argv[sys.argv.index('--fixture')+1]).resolve()
rom=(FIX/'frozen.gba').read_bytes();sha=hashlib.sha1(rom).hexdigest()
if '--fixture' not in sys.argv:
 assert sha==json.loads((ROOT/'build/expansion/probes/combat.json').read_text())['romSha1'],'Stale battle fixture: generate it from current combat ROM'
OUT=ROOT/'build/expansion/probes/executioner-in-game'/sha;OUT.mkdir(parents=True,exist_ok=True)
STATE=OUT/'battle-ready.state';STATE.write_bytes((FIX/'battle-ready.state').read_bytes())
ROM=OUT/'frozen.gba';ROM.write_bytes(rom);clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
plain=bytearray(rom);plain[0x1300e2:0x1300f2]=clean[0x1300e2:0x1300f2]
CONTROL=OUT/'native-P-control.gba';CONTROL.write_bytes(plain)
chance=bytearray(rom)
for offset,size in ((0x131378,12),(0xa3004,12),(0xb5816,10)):chance[offset:offset+size]=clean[offset:offset+size]
(OUT/'native-chance-control.gba').write_bytes(chance)
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'));hp=runpy.run_path(str(ROOT/'scripts/probe-ap-copy-heap.py'))
ACTOR,TARGET=0x398,0x33e4;guard=bytes([0xd7])*0xbc;checks=0;samples=[];outcomes=[];displayed_chances=[]
def half(r,p):return struct.unpack_from('<H',r,p)[0]
def word(r,p):return struct.unpack_from('<I',r,p)[0]
def tap(e,k,wait=180):e.run(8,k);e.run(wait)
def check(ok,detail):
 global checks
 checks+=1
 assert ok,detail
def capture(e,label):
 r=e.memory();e.screenshot(CASE/(label+'.png'));e.save(CASE/(label+'.state'))
 (CASE/(label+'.ram')).write_bytes(r);(CASE/(label+'.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
 check(r[0x3ff44:]==guard,(label,'guard'));check(hp['heap'](r)['end']==0x0203f800,(label,'heap'))
 samples.append(dict(case=CASE.name,label=label,HP=half(r,TARGET+0x18),maxHP=half(r,TARGET+0x1a),actorMP=half(r,ACTOR+0x1c)))
 return r
for preview_hp,execution_hp in ((125,125),(126,126),(125,126),(126,125)):
 CASE=OUT/f'{preview_hp}-to-{execution_hp}';CASE.mkdir(exist_ok=True)
 e=h['Emulator'](ROM)
 try:
  e.load(STATE);e.run(1)
  for offset in (5,7,0x35):e.set_memory(ACTOR+offset,b'\x10')
  e.set_memory(ACTOR+0x2a,struct.pack('<5H',459,0,0,0,0));e.set_memory(ACTOR+0x40+107,b'\x9e')
  e.set_memory(ACTOR+0x1c,struct.pack('<HH',50,50));e.set_memory(TARGET+0x18,struct.pack('<HHHH',preview_hp,250,49,49))
  ready=capture(e,'ready');stable=[(0x1940,ready[0x1940:0x1e70]),(ACTOR+0x2a,ready[ACTOR+0x2a:ACTOR+0x34])]
  for key in [256,128,128,128]:tap(e,key)
  tap(e,256,600)
  for key in [256,32,256,32]:tap(e,key)
  capture(e,'ability-menu')
  for key in [256,128,256]:tap(e,key)
  preview=capture(e,'preview')
  check(half(preview,0xf3fc)==430,('wrong action',half(preview,0xf3fc)))
  check(half(preview,TARGET+0x18)==preview_hp and half(preview,ACTOR+0x1c)==50,'Preview mutation')
  tap(e,1);cancel=capture(e,'cancelled');check(cancel[TARGET:TARGET+264]==ready[TARGET:TARGET+264],'Cancel mutation')
  check(hp['heap'](cancel)['freePayload']>=hp['heap'](preview)['freePayload'],'Cancel heap')
  tap(e,256);again=capture(e,'repreview');check(hp['heap'](again)['freePayload']==hp['heap'](preview)['freePayload'],'Repreview heap')
  tap(e,256);capture(e,'confirmation')
 finally:e.close()
 e=h['Emulator'](OUT/'native-chance-control.gba')
 try:
  e.load(CASE/'cancelled.state');tap(e,256);chance_preview=capture(e,'native-chance-preview')
  check(half(chance_preview,TARGET+0x18)==preview_hp and half(chance_preview,ACTOR+0x1c)==50,'Chance control preview mutation')
 finally:e.close()
 displayed=[]
 for kind,data in [('ordinary',chance),('executioner',rom)]:
  trap=bytearray(data);trap[0x2b8cc:0x2b8ce]=b'\xfe\xe7';trap_path=CASE/f'{kind}-display-trap.gba';trap_path.write_bytes(trap)
  e=h['Emulator'](trap_path)
  try:
   e.load(CASE/'cancelled.state');tap(e,256,60);state_path=CASE/f'{kind}-display-trap.state';e.save(state_path)
   regs=struct.unpack_from('<17I',state_path.read_bytes(),0x20)
   check(regs[15]==0x0802b8ce,('No native display call',hex(regs[15])))
   displayed.append(regs[1])
  finally:e.close()
 expected_chance=min(95,displayed[0]+20) if displayed[0] and preview_hp*2<=250 else displayed[0]
 check(displayed[1]==expected_chance,('Wrong displayed chance',CASE.name,displayed,expected_chance))
 displayed_chances.append(dict(previewHP=preview_hp,executionHP=execution_hp,ordinary=displayed[0],executioner=displayed[1]))
 # Control changes only the final coefficient hook: same native430 chance,
 # full P formula, damage application, MP payment, targeting and animation.
 seen=set();successful=None
 for seed in range(16):
  pair=[]
  for kind,path in [('native-P',CONTROL),('executioner',ROM)]:
   e=h['Emulator'](path)
   try:
    e.load(CASE/'confirmation.state');e.set_memory(TARGET+0x18,struct.pack('<H',execution_hp))
    C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4)
    tap(e,256,1500);result=capture(e,f'{kind}-seed-{seed}')
    damage=execution_hp-half(result,TARGET+0x18);pair.append(damage)
    check(half(result,ACTOR+0x1c)==40,(kind,seed,'Expected10MP once'))
    check(result[TARGET+0xf6:TARGET+0xf8]==bytes([5,14]),'Target displaced')
    check(result[ACTOR+0xf6:ACTOR+0xf8]==bytes([4,14]),'Move did not commit')
    for off,data in stable:check(result[off:off+len(data)]==data,'AP/inventory/gear')
    if kind=='executioner':
     tap(e,256,900);turn=capture(e,f'seed-{seed}-next-turn')
     check(word(turn,word(turn,0xf438)-0x02000000+0x18)!=0x02000000+ACTOR,'No next turn')
     if damage:successful=CASE/f'seed-{seed}-next-turn.state'
   finally:e.close()
  factor=18 if execution_hp*2<=250 else 11
  check(pair[1]==pair[0]*factor//10,(CASE.name,seed,'Wrong execution-time factor',pair,factor))
  outcomes.append(dict(previewHP=preview_hp,executionHP=execution_hp,seed=seed,reference=pair[0],damage=pair[1],factor=factor))
  seen.add(pair[1]>0)
  if len(seen)==2:break
 check(seen=={False,True},('Missing hit/miss',CASE.name))
 e=h['Emulator'](ROM)
 try:
  e.load(successful);e.run(1);expected=capture(e,'successful-next-turn')
  for key in [1,8,16,256,256]:tap(e,key)
  before=e.memory(0);tap(e,256,300);saved=e.memory(0);check(before!=saved,'Save Now failed');(CASE/'suspended.sav').write_bytes(saved)
 finally:e.close()
 e=h['Emulator'](ROM)
 try:
  e.set_memory(0,saved,0);e.run(3600);e.set_memory(0x3ff44,guard)
  for key,wait in [(8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)]:tap(e,key,wait)
  resumed=capture(e,'cold-resumed')
  for unit,offset,length in [(ACTOR,0x1c,2),(ACTOR,0xf6,2),(TARGET,0x18,8),(TARGET,0xf6,2)]:
   check(resumed[unit+offset:unit+offset+length]==expected[unit+offset:unit+offset+length],('Cold outcome',CASE.name))
  for off,data in stable:check(resumed[off:off+len(data)]==data,'Cold AP/inventory/gear')
  tap(e,32);tap(e,256);capture(e,'resumed-action-menu');tap(e,1);capture(e,'resumed-action-cancel')
 finally:e.close()
report=dict(passed=True,romSha1=sha,controlSha1=hashlib.sha1(plain).hexdigest(),checks=checks,outcomes=outcomes,samples=samples,displayedChances=displayed_chances,
 scope='Fresh native Executioner menu/preview/cancel/commit with same-chance nativeP control; liveHP threshold flips, MP10, turn and native SRAM cold resume. Chance matrices are independently covered by test-gladiator-finishers.py --current.')
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
