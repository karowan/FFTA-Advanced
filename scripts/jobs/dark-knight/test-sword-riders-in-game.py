"""Fixed native Crushing Blow/Unholy Sacrifice menu, damage, status and cold-save replay."""
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
blood=True;unholy='--unholy' in sys.argv;action=363 if unholy else 361;tag='unholy-sacrifice' if unholy else 'crushing-blow'
weapon=391 if unholy else 389;coefficient=175 if unholy else 115;status_bit=22 if unholy else 23
expected_resources=(60,36) if unholy else (100,40)
if blood:
 control=bytearray(image);addr=meta['symbols']['ffta_physical_final']-0x08000000;control[addr:addr+2]=bytes.fromhex('7047')
 CONTROL=LAB/'blood-native-P.gba';CONTROL.write_bytes(control)
instrumented=[]
def fixed_entry(base,kind,seed):
 image=bytearray(base);entry=0xa433c;stub=0x122e000;done=0xa822e
 assert image[entry:entry+8]==bytes.fromhex('08b4c046004b1847')
 original=struct.unpack_from('<I',image,entry+8)[0]
 assert original==meta['priorSymbols']['ffta_samurai_execute_entry']|1
 code=bytes.fromhex('03b403480349086003bc034b1847c046')+struct.pack('<3I',seed,0x030034b0,original)
 assert image[stub:stub+len(code)]==b'\xff'*len(code)
 image[stub:stub+len(code)]=code;struct.pack_into('<I',image,entry+8,0x08000000+stub+1)
 image[done:done+2]=bytes.fromhex('fee7')
 path=OUT/f'entry-{kind}-{seed}.gba';path.write_bytes(image)
 instrumented.append(dict(kind=kind,seed=seed,sha1=hashlib.sha1(image).hexdigest()))
 return path

def finish_at_return(e,label):
 e.run(8,256)
 for frames in range(0,2101,30):
  e.save(OUT/f'{label}.state');pc=struct.unpack_from('<I',(OUT/f'{label}.state').read_bytes(),0x5c)[0]
  if pc==0x080a8230:break
  if frames<2100:e.run(30)
 check(pc==0x080a8230,('native transaction return',label,hex(pc)))
 return capture(e,label)

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
for job,race,actor,index in ((119,2,0x398,84 if unholy else 82),(117,1,0x80,165 if unholy else 163)):
 OUT=LAB/f'{tag}-game-{job}';OUT.mkdir(exist_ok=True);e=Emulator(ROM)
 try:
  e.load(FIX/'battle-ready.state');e.set_memory(0x3ff44,guard);ready(e);fixed_giza_formation(image,e)
  check(e.memory()[actor+6]==race,('fixture race',job))
  for offset in (5,7,0x35):e.set_memory(actor+offset,bytes((job,)))
  e.set_memory(actor+0x2a,struct.pack('<5H',weapon,0,0,0,0))
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
  if not unholy:tap(e,128)
  tap(e,256);preview=capture(e,'preview')
  check(half(preview,0xf3fc)==action,('selected wrong action',job,half(preview,0xf3fc)))
  check(preview[actor+0x18:actor+0x20]==before[actor+0x18:actor+0x20],'preview spent resources')
  tap(e,1);cancel=capture(e,'cancelled')
  check(cancel[actor+0x18:actor+0x20]==before[actor+0x18:actor+0x20],'cancel spent resources')
  tap(e,256)
  if not unholy:tap(e,256)
  confirmation=capture(e,'confirmation')
  check(confirmation[actor+0x18:actor+0x20]==before[actor+0x18:actor+0x20],'confirmation already committed')
  if blood:C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',3),4)
  tap(e,256,1500)
  result=capture(e,'executed')
  check((half(result,actor+0x18),half(result,actor+0x1c))==expected_resources,('actual recovery/payment',job,half(result,actor+0x18),half(result,actor+0x1c)))
  if not blood:check((result[actor+0xeb]&1,result[actor+0xdd])==(1,3),'native Shell')
  check(result[0x1940:0x1e70]==stable,'AP/inventory mutation')
  previous=active(e);tap(e,256,900);ready(e,previous);expected=capture(e,'save-ready')
  for key in (1,8,16,256,256):tap(e,key)
  old=e.memory(0);tap(e,256,300);saved=e.memory(0);check(saved!=old,'native Save Now failed')
  (OUT/'suspended.sav').write_bytes(saved)
 finally:e.close()
 if blood:
  seen=set();status_seen=set()
  for seed in range(64):
   values=[]
   for kind,path in (('reference',CONTROL),('candidate',ROM)):
    e=Emulator(fixed_entry(control if kind=='reference' else image,kind,seed))
    try:
     e.load(OUT/'confirmation.state')
     r=finish_at_return(e,f'{kind}-{seed}');values.append(999-half(r,0x33e4+0x18))
     if kind=='candidate':
      applied=bool(int.from_bytes(r[0x33e4+0xe8:0x33e4+0xf0],'little')&(1<<status_bit));status_seen.add(applied)
      if not values[-1]:check(not applied,'miss applied rider')
     check((half(r,actor+0x18),half(r,actor+0x1c))==expected_resources,'hit and miss pay exactly once')
    finally:e.close()
   check(values[1]==min(999,values[0]*coefficient//100),('independent actual native P',job,seed,values))
   seen.add(values[1]>0)
  check(True in seen,('no fixed hit coverage',job));check(True in status_seen,('no fixed native status coverage',job))
 e=Emulator(ROM)
 try:
  e.set_memory(0,saved,0);e.run(3600);e.set_memory(0x3ff44,guard)
  for key,wait in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):tap(e,key,wait)
  ready(e);r=capture(e,'cold-resumed')
  check(r[actor+0x18:actor+0x20]==expected[actor+0x18:actor+0x20],'cold resources')
  check((r[actor+0xeb]&1,r[actor+0xdd])==(expected[actor+0xeb]&1,expected[actor+0xdd]),'cold native Shell')
  check(r[0x1940:0x1e70]==stable,'cold AP/inventory')
  check(r[0x33e4+0xe8:0x33e4+0xf0]==expected[0x33e4+0xe8:0x33e4+0xf0],'cold target statuses')
 finally:e.close()
 outcomes.append(dict(job=job,race=race,action=action,HP=expected_resources[0],MP=expected_resources[1],coldSave=True))
report=dict(passed=True,romSha1=meta['romSha1'],checks=checks,outcomes=outcomes,instrumented=instrumented)
(LAB/f'{tag}-in-game.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
