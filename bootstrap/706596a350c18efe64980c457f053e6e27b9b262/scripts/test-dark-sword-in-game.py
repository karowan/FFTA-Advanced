"""Private fresh Dark Knight sword-art UI, resource, turn and suspend regression."""
import ctypes as C,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'build/expansion/probes'
meta,LAB,_,_=runpy.run_path(str(ROOT/'scripts/dark-sword-test-input.py'))['load_input']('--current' in sys.argv)
FIX=P/'battle-fixture' if '--current' in sys.argv else LAB/'fixture'
if '--fixture' in sys.argv:FIX=pathlib.Path(sys.argv[sys.argv.index('--fixture')+1]).resolve()
ROM=FIX/'frozen.gba'
assert hashlib.sha1(ROM.read_bytes()).hexdigest()==meta['romSha1']
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'));checks=0;outcomes=[];guard=b'\xd7'*0xbc;TARGET=0x33e4
def half(r,p):return struct.unpack_from('<H',r,p)[0]
def tap(e,k,w=180):e.run(8,k);e.run(w)
def check(ok,detail):
 global checks
 checks+=1;assert ok,detail
def capture(e,label):
 r=e.memory();e.screenshot(OUT/(label+'.png'));e.save(OUT/(label+'.state'));(OUT/(label+'.ram')).write_bytes(r)
 check(r[0x3ff44:]==guard,('guard',label));return r
for job,actor in ((119,0x398),(117,0x80)):
 for action,item,mp,index in ((357,385,6,78 if job==119 else 159),(358,386,4,79 if job==119 else 160)):
  if '--case' in sys.argv and f'{job}-{action}'!=sys.argv[sys.argv.index('--case')+1]:continue
  OUT=LAB/f'game-{job}-{action}';OUT.mkdir(exist_ok=True);e=h['Emulator'](ROM)
  try:
   e.load(FIX/'battle-ready.state');e.run(1)
   for off in (5,7,0x35):e.set_memory(actor+off,bytes([job]))
   e.set_memory(actor+0x2a,struct.pack('<5H',item,0,0,0,0))
   ap=actor+0x40+index if job==119 else 0x1b40+index-144;e.set_memory(ap,b'\xff')
   if actor==0x80:
    for turn in range(4):
     for k in (32,32,256):tap(e,k)
     tap(e,256,4500 if turn==3 else 900)
   e.set_memory(actor+0x18,struct.pack('<HHHH',20,100,20,50));e.set_memory(TARGET+0x18,struct.pack('<HHHH',250,250,49,49))
   ready=capture(e,'ready');stable=ready[0x1940:0x1e70]
   for k in ([256,128,128,128] if actor==0x398 else [256,128,128,32]):tap(e,k)
   tap(e,256,600)
   for k in (256,32,256):tap(e,k)
   capture(e,'ability-menu')
   tap(e,256);tap(e,128);capture(e,'target-selected');tap(e,256);preview=capture(e,'preview')
   check(half(preview,0xf3fc)==action,('Wrong action',job,action,half(preview,0xf3fc)))
   check(preview[actor+0x18:actor+0x20]==ready[actor+0x18:actor+0x20] and preview[TARGET+0x18:TARGET+0x20]==ready[TARGET+0x18:TARGET+0x20],'Preview resource mutation')
   tap(e,1);cancel=capture(e,'cancelled');check(cancel[TARGET:TARGET+264]==ready[TARGET:TARGET+264],'Cancel mutation')
   tap(e,256);tap(e,256);capture(e,'confirmation');seen=set();success=None
   for seed in range(16):
    e.load(OUT/'confirmation.state');C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4);tap(e,256,1500)
    result=capture(e,f'seed-{seed}');damage=250-half(result,TARGET+0x18);hit=damage>0
    if action==357:
     expected_hp=20+min(damage//2,20);expected_mp=20-mp;target_mp=49
    else:
     loss=min(damage//5,16,49);expected_hp=20;expected_mp=20-mp+min(loss,50-(20-mp));target_mp=49-loss
    check(half(result,actor+0x18)==expected_hp,('HP rider',job,action,seed,damage,half(result,actor+0x18),expected_hp))
    check(half(result,actor+0x1c)==expected_mp,('MP rider',job,action,seed,damage,half(result,actor+0x1c),expected_mp))
    check(half(result,TARGET+0x1c)==target_mp,'Target MP rider');check(result[0x1940:0x1e70]==stable,'AP/inventory mutation')
    check(result[TARGET+0xf6:TARGET+0xf8]==bytes([5,14]),'Displacement')
    tap(e,256,900);turn=capture(e,f'seed-{seed}-next-turn')
    if hit:success=OUT/f'seed-{seed}-next-turn.state'
    outcomes.append(dict(job=job,action=action,seed=seed,damage=damage,HP=expected_hp,MP=expected_mp,targetMP=target_mp));seen.add(hit)
    if len(seen)==2:break
   check(len(seen)==2,'No hit/miss controls');e.load(success);e.run(1);expected=capture(e,'save-ready')
   for k in (1,8,16,256,256):tap(e,k)
   before=e.memory(0);tap(e,256,300);saved=e.memory(0);check(saved!=before,'Native Save Now');(OUT/'suspended.sav').write_bytes(saved)
  finally:e.close()
  e=h['Emulator'](ROM)
  try:
   e.set_memory(0,saved,0);e.run(3600);e.set_memory(0x3ff44,guard)
   for k,w in [(8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)]:tap(e,k,w)
   resumed=capture(e,'cold-resumed')
   for unit in (actor,TARGET):check(resumed[unit+0x18:unit+0x20]==expected[unit+0x18:unit+0x20],'Cold resources')
   check(resumed[0x1940:0x1e70]==stable,'Cold AP/inventory');tap(e,32);tap(e,256);capture(e,'cold-action-menu')
  finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],checks=checks,outcomes=outcomes)
(LAB/'game-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
