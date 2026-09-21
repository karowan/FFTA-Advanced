"""Fixed-input Fell Cleave UI, hit/miss costs, Exposed and cold SRAM resume."""
import ctypes as C, hashlib, json, pathlib, runpy, struct, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
from fell_test_context import load_context
meta=load_context('--current' in sys.argv)
ROM=pathlib.Path(meta['path']);LAB=ROM.parent;FIX=LAB/'fixture';OUT=LAB/'actual';OUT.mkdir(exist_ok=True)
rom=ROM.read_bytes();sha=lambda b:hashlib.sha1(b).hexdigest()
assert sha(rom)==meta['romSha1'] and sha((FIX/'frozen.gba').read_bytes())==sha(rom)
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
control=bytearray(rom);control[0x1300e2:0x1300f2]=clean[0x1300e2:0x1300f2]
CONTROL=OUT/'native-P-control.gba';CONTROL.write_bytes(control)
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
heap=runpy.run_path(str(ROOT/'scripts/probe-ap-copy-heap.py'))['heap']
menu=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
ACTOR,TARGET,AS,TS=0x398,0x33e4,0x1e9b,0x1eb4
guard=bytes([0xd7])*0xbc;checks=0;samples=[];outcomes=[]
half=lambda r,p:struct.unpack_from('<H',r,p)[0]
word=lambda r,p:struct.unpack_from('<I',r,p)[0]
def tap(e,key,wait=180):e.run(8,key);e.run(wait)
def check(value,detail):
 global checks
 checks+=1
 assert value,detail
def capture(e,label):
 r=e.memory();e.save(OUT/(label+'.state'));e.screenshot(OUT/(label+'.png'))
 (OUT/(label+'.ram')).write_bytes(r);(OUT/(label+'.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
 check(r[0x3ff44:]==guard,(label,'guard'));check(heap(r)['end']==0x0203f800,(label,'heap'))
 samples.append(dict(label=label,actorMP=half(r,ACTOR+0x1c),targetHP=half(r,TARGET+0x18),actorState=r[AS],targetState=r[TS]))
 return r
e=h['Emulator'](ROM)
try:
 e.load(FIX/'battle-ready.state');e.run(1);menu['wait_for_menu'](e)
 for offset in (5,7,0x35):e.set_memory(ACTOR+offset,b'\x10')
 e.set_memory(ACTOR+0x2a,struct.pack('<5H',460,0,0,0,0));e.set_memory(ACTOR+0x40+108,b'\xff')
 e.set_memory(ACTOR+0x1c,struct.pack('<HH',50,50));e.set_memory(TARGET+0x18,struct.pack('<HHHH',250,250,49,49))
 ready=capture(e,'ready');stable=[(0x1940,ready[0x1940:0x1e70]),(ACTOR+0x2a,ready[ACTOR+0x2a:ACTOR+0x34])]
 for key in [256,128,128,128]:tap(e,key)
 tap(e,256,600)
 for key in [256,32,256,32]:tap(e,key)
 capture(e,'ability-menu')
 for key in [256,128,256]:tap(e,key)
 preview=capture(e,'preview');check(half(preview,0xf3fc)==431,('wrong action',half(preview,0xf3fc)))
 check(half(preview,ACTOR+0x1c)==50 and preview[AS]==0,'Preview charged MP or applied Exposed')
 tap(e,1);cancel=capture(e,'cancelled')
 check(cancel[TARGET:TARGET+264]==ready[TARGET:TARGET+264] and cancel[AS]==0,'Cancel changed gameplay')
 tap(e,256);again=capture(e,'repreview')
 check(heap(again)['freePayload']==heap(preview)['freePayload'],'Repreview leaked heap')
 tap(e,256);capture(e,'confirmation')
finally:e.close()
seen=set();successful=None
for seed in range(16):
 pair=[]
 for kind,path in [('native-P',CONTROL),('fell',ROM)]:
  e=h['Emulator'](path)
  try:
   e.load(OUT/'confirmation.state');C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4)
   tap(e,256,1500);result=capture(e,f'{kind}-seed-{seed}')
   damage=250-half(result,TARGET+0x18);pair.append(damage)
   check(half(result,ACTOR+0x1c)==34,(kind,seed,'Expected exactly16 MP'))
   check(result[AS]==1,(kind,seed,'Exposed must apply on hit AND miss'))
   for off,data in stable:check(result[off:off+len(data)]==data,'AP/inventory/gear changed')
   check(result[ACTOR+0xf6:ACTOR+0xf8]==bytes([4,14]),'Move did not commit')
   if kind=='fell':
    tap(e,256,900);menu['wait_for_menu'](e);turn=capture(e,f'seed-{seed}-next-turn')
    manager=word(turn,0xf438)-0x02000000
    check(word(turn,manager+0x18)!=0x02000000+ACTOR,'Next unit did not receive turn')
    check(turn[AS]==1,'Exposed expired before next own turn')
    if damage:successful=OUT/f'seed-{seed}-next-turn.state'
  finally:e.close()
 check(pair[1]==pair[0]*18//10,('Wrong native P factor',seed,pair))
 outcomes.append(dict(seed=seed,reference=pair[0],damage=pair[1]));seen.add(pair[1]>0)
 if len(seen)==2:break
check(seen=={False,True},'Fixed seeds did not exercise both hit and miss')
e=h['Emulator'](ROM)
try:
 e.load(successful);e.run(1);expected=capture(e,'before-suspend')
 for key in [1,8,16,256,256]:tap(e,key)
 before=e.memory(0);tap(e,256,300);saved=e.memory(0);check(before!=saved,'Save Now failed')
 (OUT/'suspended.sav').write_bytes(saved)
finally:e.close()
e=h['Emulator'](ROM)
try:
 e.set_memory(0,saved,0);e.run(3600);e.set_memory(0x3ff44,guard)
 for key,wait in [(8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)]:tap(e,key,wait)
 menu['wait_for_menu'](e);resumed=capture(e,'cold-resumed')
 check(resumed[AS]==1,'Cold resume lost Exposed')
 for unit,offset,length in [(ACTOR,0x1c,2),(ACTOR,0xf6,2),(TARGET,0x18,8),(TARGET,0xf6,2)]:
  check(resumed[unit+offset:unit+offset+length]==expected[unit+offset:unit+offset+length],'Cold outcome changed')
 for off,data in stable:check(resumed[off:off+len(data)]==data,'Cold AP/inventory/gear changed')
finally:e.close()
report=dict(passed=True,romSha1=sha(rom),controlSha1=sha(control),checks=checks,outcomes=outcomes,samples=samples,
 scope='Fresh matching private-ROM fixture, native Fell menu/preview/cancel, nativeP coefficient oracle, hit/miss16MP and selfExposed, next-unit turn, cold SRAM suspend/resume. Target Exposed incoming/expiry and law checks are separate.')
(LAB/'actual-report.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
