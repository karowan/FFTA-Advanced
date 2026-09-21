"""Whole native AI utility turns with fixed inputs and no supplied decisions."""
import pathlib
from datetime import datetime,timezone
ROOT=pathlib.Path(__file__).resolve().parents[1]
RUN_NAME='geomancer-utility-turns-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
preparation=(ROOT/'scripts/test-geomancer-choice-ai.py').read_text(encoding='utf-8').split('# All-affinity ground')[0]
preparation=preparation.replace("'geomancer-choice-ai'",repr(RUN_NAME))
exec(compile(preparation,'<fixed native utility AI formation>','exec'))
STATE=0x3f410+((ACTOR-0x80)//264)*22
inputs=[];outcomes=[];costs={377:8,380:12,382:12}
cases=[(a,'available',seed) for a in (377,380,382) for seed in (0,3,18)]
cases += [(377,'unlearned',3),(382,'no-MP',3)]
if '--benefits-only' in sys.argv:cases=[c for c in cases if c[0] in (377,382) and c[1]=='available']

def save_report(passed):
 report=dict(passed=passed,romSha1=meta['romSha1'],instrumentedSha1=hashlib.sha1(instrumented).hexdigest(),
  checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,fixedInputs=inputs,
  scope='Whole native utility AI turns; explicit planner and combat seeds, native decisions and execution.')
 (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 return report

save_report(False)
for action,condition,seed in cases:
 case=(action,condition,seed);folder=OUT/('-'.join(map(str,case)));folder.mkdir(exist_ok=True);e=E(TEST_ROM)
 try:
  e.load(OUT/'start.state');e.set_memory(LOG+148,struct.pack('<II',1,seed));e.set_memory(ACTOR+0x40,bytes(0x90))
  lesson=next(l for l in registry['lessons'] if l['id']=='GEO-A'+str(action-373))
  index=next(o['abilityIndex'] for o in lesson['owners'] if o['race']==3)
  if condition!='unlearned':e.set_memory(ACTOR+0x40+index,b'\xff')
  # Keep original races, jobs and native faction lists. Master existing enemy
  # commands, including the starting Black Mage, and remove cheap Fight KOs.
  for unit in (0x80,0x188,0x290,0x398,0x5a8):
   e.set_memory(unit+0x18,struct.pack('<4H',999,999,99,100));e.set_memory(unit+0x40,b'\xff'*0x90)
   e.set_memory(unit+0x20,struct.pack('<4H',70,220,100,40))
  e.set_memory(0x188+0xf6,bytes((2,12)));e.set_memory(wrappers[0x188]+8,struct.pack('<3H',80,32,400))
  e.set_memory(ACTOR+0x20,struct.pack('<4H',1,40,80,40))
  if action in (377,382) and condition=='available':
   # Declare a support situation: allies near the caster, hostile melee far
   # away. Refuge alone keeps the real Black Mage within spell-threat reach.
   for unit,x,y,h in ((0x80,7,3,80),(0x188,8,3,80),(0x290,9,3,80),
      (0x398,10,3,80),(0x5a8,11,3,80),(TARGET,1,13,32),(SECOND,1,14,16)):
    e.set_memory(unit+0xf6,bytes((x,y)));e.set_memory(wrappers[unit]+8,struct.pack('<3H',x*32+16,h,y*32+16))
   if action==382:
    e.set_memory(0x188+0xf6,bytes((4,12)));e.set_memory(wrappers[0x188]+8,struct.pack('<3H',144,32,400))
  if condition=='no-MP':e.set_memory(ACTOR+0x1c,bytes(2))
  saw_actor=False;last_log=0;casts=[];rendered=set();before=None
  for frame in range(30000):
   r=e.memory();w=word(r,0xf4ec);live=word(r,w-0x02000000) if 0x02000000<=w<0x02040000 else 0
   count=word(r,LOG+4)
   if count!=last_log:
    check('one-native-execution-per-frame',count==last_log+1);last_log=count
    if word(r,LOG+24)==0x02000000+ACTOR:
     casts.append(dict(action=word(r,LOG+8),choice=word(r,LOG+132),beforeMP=word(r,LOG+140)))
     result=checkpoint(e,'native-result',folder)
   if live==0x02000000+ACTOR:
    if not saw_actor:
     # Execution instrumentation seeds hit rolls only. Seed the planner too,
     # before native setup, so these declared cases exercise distinct native
     # willingness/discovery decisions rather than repeating one AI decision.
     C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4)
     before=checkpoint(e,'AI-turn-start',folder)
    saw_actor=True;rendered.add(hashlib.sha1(e.frame[0]).hexdigest())
   elif saw_actor and live:
    final=checkpoint(e,'native-handoff',folder);break
   if observe['menu_visible'](e):
    check('AI-never-needs-player-input',active(e)!=0x02000000+ACTOR)
    for key in (32,32,256):inputs.append((case,frame,key));tap(e,key)
    inputs.append((case,frame,256));e.run(8,256)
   e.run(1)
  else:raise AssertionError(('AI turn timeout',case))
  allowed=(0,action) if condition=='available' else (0,)
  check('at-most-one-native-AI-command',len(casts)<=1)
  check('only-learned-affordable-actions',all(c['action'] in allowed for c in casts))
  if casts and casts[0]['action']==action:
   selected=casts[0];check('native-zero-extra',selected['choice']==0)
   check('one-MP-payment',selected['beforeMP']-half(final,ACTOR+0x1c)==costs[action])
   if action in (380,382):check('actual-field-owned',final[STATE+17]&3==(1 if action==380 else 2))
   else:
    bank=final[0x3f410:0x3f410+36*22]
    check('actual-Updraft-recipient',any(bank[i*22+18]&14 for i in range(36)))
  check('scope-retired',final[0x3f728:0x3f72c]==bytes(4))
  check('native-rendering-advanced',len(rendered)>3)
  outcomes.append(dict(action=action,condition=condition,seed=seed,casts=casts,frames=frame,
   actorPosition=list(final[ACTOR+0xf6:ACTOR+0xf8]),field=list(final[STATE+15:STATE+19])))
  save_report(False)
 except Exception:
  checkpoint(e,'failure',folder);save_report(False);raise
 finally:e.close()
for action in sorted({c[0] for c in cases if c[1]=='available'}):
 check('nonvacuous-native-utility-'+str(action),any(o['casts'] and o['casts'][0]['action']==action for o in outcomes))
print(json.dumps(save_report(True),indent=2))
