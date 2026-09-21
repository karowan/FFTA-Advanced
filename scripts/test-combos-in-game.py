"""Actual headless battle Combo UI fixtures; never touches user play files."""
import ctypes as C,datetime,hashlib,json,pathlib,runpy,struct,sys
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1];integrated='--integrated' in sys.argv;resume='--resume' in sys.argv
sha=lambda b:hashlib.sha1(b).hexdigest()
if integrated:
 meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text());FIX=pathlib.Path(meta['path']).parent/'fixture'
 rom=pathlib.Path(meta['path']).read_bytes();assert (FIX/'frozen.gba').read_bytes()==rom
 cache=json.loads((FIX/'prepare-cache.json').read_text());assert cache['inputs']['romSha1']==meta['romSha1']
 for name in ('battle-ready.state','battle-ready.ram','battle-ready.iwram'):assert sha((FIX/name).read_bytes())==cache['outputs'][name],name
 FAMILY=pathlib.Path(meta['path']).parent/'combo-ui';FAMILY.mkdir(exist_ok=True)
 previous=json.loads((FAMILY/'latest.json').read_text()) if resume else None
 OUT=pathlib.Path(previous['directory']) if previous else FAMILY/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
else:
 assert not resume,'Resume requires the integrated mode'
 FIX=ROOT/'build/expansion/probes/battle-fixture';meta=json.loads((FIX/'report.json').read_text());rom=(FIX/'frozen.gba').read_bytes()
 assert meta['romSha1']==json.loads((ROOT/'build/expansion/probes/combat.json').read_text())['romSha1'], 'Stale battle fixture'
 OUT=ROOT/'build/expansion/probes/combos-in-game'/meta['romSha1'];previous=None
assert sha(rom)==meta['romSha1']
OUT.mkdir(parents=True,exist_ok=True);ROM=OUT/'frozen.gba';ROM.write_bytes(rom);START=OUT/'battle-ready.state';START.write_bytes((FIX/'battle-ready.state').read_bytes());registry=json.loads((ROOT/'build/expansion/registry.json').read_text());Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
ROWS={1:(0x290,3,32),2:(0x398,0,128),3:(0x4a0,2,16),4:(0x5a8,1,128),5:(0x188,5,64)}
WEAPONS={'SAM-C1':106,'DRK-C1':1,'VIK-C1':453,'GEO-C1':135,'CHM-C1':74,'BRD-C1':201,'DNC-C1':88,'MYK-C1':88}
checks={};results=[]
completed={};provenance=[]
if previous:
 prior_path=pathlib.Path(previous['report']);prior_bytes=prior_path.read_bytes();assert sha(prior_bytes)==previous['reportSha1']
 prior=json.loads(prior_bytes);assert prior['romSha1']==meta['romSha1'] and prior['fixtureSha1']==sha(START.read_bytes())
 for entry in prior['completed'].values():
  for file,digest in entry.items():assert sha((OUT/file).read_bytes())==digest,('Changed accepted artifact',file)
 checks.update(prior['groups']);results.extend(prior['owners']);completed.update(prior['completed']);provenance=prior.get('provenance',[])+[{'report':str(prior_path),'sha1':sha(prior_bytes)}]
def check(g,a,b):
 assert a==b,(g,a,b)
 checks[g]=checks.get(g,0)+1

def tap(e,k,wait=120):e.run(8,k);e.run(wait)
observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
def active_actor(e):
 b=e.memory();manager=struct.unpack_from('<I',b,0xf438)[0]-0x02000000
 return struct.unpack_from('<I',b,manager+0x18)[0] if 0<=manager<0x3f7e0 else 0

def wait_menu(e,previous=None,expected=None,limit=9000):
 for elapsed in range(0,limit+1,10):
  actor=active_actor(e)
  if observe['menu_visible'](e) and (previous is None or actor!=previous) and (expected is None or actor==expected):return
  if elapsed<limit:e.run(10)
 raise AssertionError(('Native actor/menu not ready',previous,expected,hex(active_actor(e))))

def advance_turns(e,count,expected):
 wait_menu(e)
 for turn in range(count):
  previous=active_actor(e)
  for key in (32,32,256,256):tap(e,key)
  wait_menu(e,previous=previous)
 check('observed_ready_actor',active_actor(e),0x02000000+expected)

def get16(b,p):return struct.unpack_from('<H',b,p)[0]
def state(e):
 b=e.memory();return [{'unit':hex(o),'job':b[o+5],'JP':get16(b,o+0xd6),'HP':get16(b,o+0x18),'combo':b[o+0x3c],'flags':b[o+0xe8:o+0xee].hex()} for o in (0x80,0x188,0x290,0x398,0x4a0,0x5a8)]
def snapshot(e,d,label):
 e.screenshot(d/(label+'.png'));e.save(d/(label+'.state'));(d/(label+'.ram')).write_bytes(e.memory());(d/(label+'.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]));(d/(label+'.json')).write_text(json.dumps(state(e),indent=2))
def completed_menu(e,d,reference):
 # Wait for actual native text/outline pixels; do not create an oracle from
 # an unverified screenshot captured while the preceding actor was finishing.
 try:wait_menu(e,limit=6300)
 except AssertionError:
  e.save(d/'animation-stalled.state');(d/'animation-stalled.ram').write_bytes(e.memory());raise
 check('animation_returns_control',True,True)

def ap_offset(unit,race,index):return 0x1b40+((unit-0x80)//264)*34+index-144 if race==1 and index>=144 else unit+0x40+index

def mastery(b,unit,race):
 count=next(r['totalCount'] for r in registry['races'] if r['id']==race)
 if race==1:
  side=0x1b40+((unit-0x80)//264)*34
  return b[unit+0x40:unit+0x40+142]+b[side:side+34]
 return b[unit+0x40:unit+0x40+count]

def run(lesson,owner):
 d=OUT/(lesson['id']+'-race'+str(owner['race']));d.mkdir(exist_ok=True);unit,turns,key=ROWS[owner['race']];target=0x188 if owner['race']==2 else 0x398;e=Emulator(ROM)
 try:
  e.load(START);e.run(1);before=e.memory();check('original_race',before[unit+6],owner['race'])
  # Legal new-job/gear/mastery/JP setup in disposable RAM. Names, character
  # IDs, race, growth/level and accumulated stats retain the original unit.
  for offset in (5,7,0x35):e.set_memory(unit+offset,bytes((owner['jobId'],)))
  e.set_memory(unit+0x3c,bytes((owner['abilityIndex'],)));ap=ap_offset(unit,owner['race'],owner['abilityIndex']);e.set_memory(ap,b'\x8a');e.set_memory(unit+0x2a,struct.pack('<5H',WEAPONS[lesson['id']],0,0,0,0))
  for o in (0x80,0x188,0x290,0x398,0x4a0,0x5a8):e.set_memory(o+0xd6,struct.pack('<H',3 if o==unit else 0))
  e.set_memory(target+0x18,struct.pack('<HH',999,999))
  advance_turns(e,turns,unit)
  snapshot(e,d,'turn-ready');ready=e.memory();print(lesson['id'],owner['race'],'native turn ready',flush=True)
  # Open Action and select Combo, retaining the original native command path.
  tap(e,32);tap(e,256)
  tap(e,16)  # native wrap selects the final Combo entry
  snapshot(e,d,'combo-menu');tap(e,256);snapshot(e,d,'targeting');tap(e,key);snapshot(e,d,'target-selected')
  tap(e,1);tap(e,1);snapshot(e,d,'cancelled');cancel=e.memory()
  check('cancel_JP',get16(cancel,unit+0xd6),3);check('cancel_target_HP',get16(cancel,target+0x18),999);check('cancel_equipment',cancel[unit+0x2a:unit+0x34],ready[unit+0x2a:unit+0x34]);check('cancel_mastery',cancel[ap],0x8a);check('cancel_all_AP',mastery(cancel,unit,owner['race']),mastery(ready,unit,owner['race']))
  e.load(d/'target-selected.state');e.run(1);tap(e,256,180);snapshot(e,d,'commit-first');tap(e,256,180);snapshot(e,d,'commit-second');tap(e,256,0);snapshot(e,d,'commit-8')
  trace=[]
  for frame in range(0,1800,30):
   e.run(30);trace.append({'frame':frame+38,'party':state(e)})
   if frame in (90,270,570):e.screenshot(d/f'animation-{frame+38}.png')
  completed_menu(e,d,d/'turn-ready.png')
  snapshot(e,d,'executed');after=e.memory();(d/'trace.json').write_text(json.dumps(trace,indent=2));print(lesson['id'],owner['race'],'completed JP',get16(after,unit+0xd6),'target HP',get16(after,target+0x18),flush=True)
  check('spent_JP_once',get16(after,unit+0xd6),0);check('target_survives',get16(after,target+0x18)>0,True);check('combo_remains_assigned',after[unit+0x3c],owner['abilityIndex']);check('execution_mastery',after[ap],0x8a);check('execution_equipment',after[unit+0x2a:unit+0x34],ready[unit+0x2a:unit+0x34]);check('identity_name',after[unit:unit+4],before[unit:unit+4]);check('identity_race',after[unit+6],before[unit+6])
  check('all_AP_unchanged',mastery(after,unit,owner['race']),mastery(ready,unit,owner['race']))
  for o in (0x80,0x188,0x290,0x398,0x4a0,0x5a8):check('no_KO_JP_award',get16(after,o+0xd6),0)
  # Native Save Now from the completed-action unit menu; write only this
  # emulator's SRAM, then recreate the core and resume using SRAM alone.
  # Finish the committed turn before opening System; native prevents free
  # cursor cancellation after spending Action while Move remains available.
  for k in (32,32,256,256):tap(e,k)
  e.run(6000);persist=e.memory();tap(e,1);tap(e,8)
  for _ in range(5):tap(e,32)
  tap(e,256);tap(e,256);snapshot(e,d,'save-complete');tap(e,256)
  sram=e.memory(0);(d/'suspend.srm').write_bytes(sram);e.close();e=None
  e=Emulator(ROM);e.set_memory(0,sram,0);e.run(1200)
  for k in (8,8,256,256,256,256,64,256):tap(e,k,300)
  e.run(600);snapshot(e,d,'cold-resumed');cold=e.memory()
  check('cold_job',cold[unit+5],owner['jobId']);check('cold_assigned',cold[unit+0x3c],owner['abilityIndex']);check('cold_JP',get16(cold,unit+0xd6),0)
  check('cold_equipment',cold[unit+0x2a:unit+0x34],after[unit+0x2a:unit+0x34]);check('cold_all_AP',mastery(cold,unit,owner['race']),mastery(after,unit,owner['race']));check('cold_target_HP',get16(cold,target+0x18),get16(persist,target+0x18));check('cold_identity',cold[unit:unit+4],before[unit:unit+4])
  results.append({'id':lesson['id'],'race':owner['race'],'unit':hex(unit),'target':hex(target),'JP':get16(after,unit+0xd6),'targetHP':get16(after,target+0x18),'screenshots':str(d)})
 finally:
  if e is not None:e.close()
DONORS={'SAM-C1':15,'DRK-C1':2,'VIK-C1':7,'GEO-C1':17,'CHM-C1':23,'BRD-C1':32,'DNC-C1':6,'MYK-C1':11}
chains=prior['chains'][:] if previous else []
def chain(lesson,owner):
 # The new lesson must participate, not merely initiate: profile power/range/
 # chance are participant properties. Use an original native Combo initiator.
 unit,_,_=ROWS[owner['race']]
 if owner['race']==2:init,turns,key,target,race,index=0x80,4,64,0x290,1,11
 elif owner['race']==4:init,turns,key,target,race,index=0x290,3,32,0x398,1,11
 else:init,turns,key,target,race,index=0x5a8,1,128,0x398,4,11
 d=OUT/(lesson['id']+'-race'+str(owner['race']))/'chain';d.mkdir(exist_ok=True)
 e=Emulator(ROM)
 try:
  e.load(START);e.run(1)
  for off in (5,7,0x35):e.set_memory(unit+off,bytes((owner['jobId'],)))
  e.set_memory(unit+0x3c,bytes((owner['abilityIndex'],)));e.set_memory(ap_offset(unit,owner['race'],owner['abilityIndex']),b'\x8a');e.set_memory(unit+0x2a,struct.pack('<5H',WEAPONS[lesson['id']],0,0,0,0))
  # Only the intended participant and initiator are combo-assigned. This is a
  # disposable fixture, with actual legal native same-race units and weapons.
  for o in (0x80,0x188,0x290,0x398,0x4a0,0x5a8):
   if o not in (unit,init):e.set_memory(o+0x3c,b'\0')
   e.set_memory(o+0xd6,struct.pack('<H',3 if o in (unit,init) else 0))
  e.set_memory(init+0x3c,bytes((index,)));e.set_memory(ap_offset(init,race,index),b'\x8a');e.set_memory(init+0x2a,struct.pack('<5H',1 if race==1 else 88,0,0,0,0));e.set_memory(target+0x18,struct.pack('<HH',999,999))
  advance_turns(e,turns,init)
  snapshot(e,d,'turn-ready')
  tap(e,32);tap(e,256)
  tap(e,16)  # native wrap selects the final Combo entry
  tap(e,256);tap(e,key);snapshot(e,d,'selected')
 finally:e.close()
 # Change only the new racial lesson's global profile in the native control.
 # The whole new profile exactly copies that named native donor. No runtime
 # menu, hit handler, JP, geometry, or chain function is replaced.
 pointer_table=struct.unpack_from('<I',rom,0xcd538)[0]-0x08000000
 race_base=struct.unpack_from('<I',rom,pointer_table+owner['race']*4)[0]-0x08000000
 record=race_base+owner['abilityIndex']*8
 check('chain_lesson_type',rom[record+6],5);check('chain_lesson_global',get16(rom,record+4),lesson['globalAbilityId'])
 control=bytearray(rom);struct.pack_into('<H',control,record+4,DONORS[lesson['id']]);variants={'expanded':rom,'native-donor':bytes(control)}
 def execute(label,image,seed,trap=False):
  trial=bytearray(image)
  # Break after native STRB publishes the successful participant count.
  if trap:trial[0xb32e8:0xb32ea]=b'\xfe\xe7'
  path=d/(label+('-trap' if trap else '')+'.gba');path.write_bytes(trial);e=Emulator(path)
  try:
   e.load(d/'selected.state');e.run(1)
   # Controlled native RNG seed, not a replacement random function.
   C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4)
   for _ in range(3):tap(e,256,180)
   e.run(900 if trap else 1800);label=label+('-trap' if trap else '');snapshot(e,d,label);b=e.memory()
   if trap:
    reg=struct.unpack_from('<16I',(d/(label+'.state')).read_bytes(),0x20)
    check('native_sum_breakpoint',reg[15],0x080b32ea)
    context=reg[7]-0x02000000;assert 0<=context<len(b)-0x15c4
    count=b[context+0x1539];assert count<=12
    def unwrap(pointer):
     offset=pointer-0x02000000;assert 0<=offset<len(b)-4
     return struct.unpack_from('<I',b,offset)[0]
    initiator=unwrap(struct.unpack_from('<I',b,context+0x141c)[0]);receiver=unwrap(struct.unpack_from('<I',b,context+0x1420)[0]);members=[unwrap(struct.unpack_from('<I',b,context+0x1458+4*i)[0]) for i in range(count)]
    return {'context':hex(context+0x02000000),'initiator':initiator,'target':receiver,'members':members}
   completed_menu(e,d,d/'turn-ready.png')
   return {'JP':[get16(b,o+0xd6) for o in (init,unit,target)],'targetHP':get16(b,target+0x18),'mastery':mastery(b,unit,owner['race']).hex(),'equipment':b[unit+0x2a:unit+0x34].hex()}
  finally:e.close()
 # Fixed native seeds from accepted participant controls; no repeated search.
 for seed in (1 if lesson['id'] in ('GEO-C1','BRD-C1') else 0,):
  membership=execute('expanded',rom,seed,True)
  if 0x02000000+unit in membership['members']:break
 else:raise AssertionError(('new combo never participates',lesson['id'],owner))
 check('chain_actual_initiator',membership['initiator'],0x02000000+init);check('chain_actual_target',membership['target'],0x02000000+target);check('chain_actual_new_participant',membership['members'],[0x02000000+unit])
 native=execute('native-donor',variants['native-donor'],seed,True)
 check('native_donor_chain_list',(membership['initiator'],membership['target'],membership['members']),(native['initiator'],native['target'],native['members']))
 expanded=execute('expanded',rom,seed);native=execute('native-donor',variants['native-donor'],seed)
 check('native_donor_actual_outcome',expanded,native);check('chain_initiator_spent',expanded['JP'][0],0);check('chain_nonKO',expanded['targetHP']>0,True)
 chains.append({'id':lesson['id'],'race':owner['race'],'seed':seed,'membership':membership,'outcome':expanded});print(lesson['id'],owner['race'],'new participant and native donor match',flush=True)

scope='Actual native Combo UI cancellation/commit for each tested owner; new lesson as an actual participant with exact named-donor control; native Save Now and SRAM-only cold Resume Battle. Disposable legal job/equipment/mastery/JP/targetHP fixtures, no user files.'
def checkpoint(passed,error=None):
 report={'passed':passed,'romSha1':meta['romSha1'],'fixtureSha1':sha(START.read_bytes()),'checks':sum(checks.values()),'groups':checks,'owners':results,'chains':chains,'completed':completed,'provenance':provenance,'scope':scope,'error':error,'directory':str(OUT)}
 path=OUT/('report-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')+'.json')
 path.write_text(json.dumps(report,indent=2))
 if integrated:(FAMILY/'latest.json').write_text(json.dumps(dict(directory=str(OUT),report=str(path),reportSha1=sha(path.read_bytes()),passed=passed,romSha1=meta['romSha1']),indent=2))
 return report
try:
 accepted_checks=checks.copy()
 for lesson in registry['lessons']:
  if lesson['type']!='Combo':continue
  if '--lesson' in sys.argv and lesson['id']!=sys.argv[sys.argv.index('--lesson')+1]:continue
  for owner in lesson['owners']:
   name=lesson['id']+'-race'+str(owner['race']);directory=OUT/name
   for phase,fn in [('owner',run),('chain',chain)]:
    key=name+'-'+phase
    if key in completed:continue
    accepted_checks=checks.copy()
    fn(lesson,owner)
    artifacts=directory.glob('*') if phase=='owner' else (directory/'chain').glob('*')
    completed[key]={str(p.relative_to(OUT)):sha(p.read_bytes()) for p in artifacts if p.is_file()}
    accepted_checks=checks.copy()
    checkpoint(False)
 report=checkpoint(True)
 (OUT/'results.json').write_text(json.dumps(report,indent=2))
 if not integrated and '--lesson' not in sys.argv:(ROOT/'build/expansion/probes/combos-in-game-tests.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({k:v for k,v in report.items() if k not in ('completed','provenance')},indent=2))
except Exception as exc:
 checks=accepted_checks
 checkpoint(False,repr(exc));raise
