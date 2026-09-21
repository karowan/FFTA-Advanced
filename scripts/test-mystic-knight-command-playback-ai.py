"""Fixed complete native Mystic command AI turns, without supplied decisions."""
import pathlib
from datetime import datetime,timezone
RUN_NAME="mystic-knight-command-playback-ai-"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/test-passing-step-ai.py').read_text(encoding='utf-8').split("exec(compile(preparation,")[0]
source=source.replace("'DNC-A9'","'MYK-A12'").replace("'passing-step-ai'",repr(RUN_NAME))
exec(compile(source,'<fixed native AI preparation>','exec'))
preparation=preparation.replace("b'\\x7c'","b'\\x7d'")
preparation=preparation.replace("e.set_memory(ACTOR+0x2a,bytes(10))", "e.set_memory(ACTOR+0x2a,struct.pack('<5H',88,0,0,0,0))")
preparation=preparation.replace('exec(compile(support,',
 "support=support.replace('unsigned result=playback_original', 'log[35]=h(*(const uint8_t *const *)actor+0x1c); unsigned result=playback_original')\nexec(compile(support,")
exec(compile(preparation,'<fixed native Mystic AI formation>','exec'))

inputs=[];outcomes=[];STATE=0x3f410+5*22
costs=dict(zip(range(410,424),(6,6,6,6,10,8,12,20,12,8,12,10,14,24)))
cases=[(a,'attack',s) for a in list(range(410,421))+[423] for s in (0,3,18)]
cases += [(a,'bare',3) for a in range(410,421)]+[(410,'prepared',3)]
cases += [(422,c,3) for c in ('fire','flare','no-fuel','bad-fuel','allies')]
if '--tactical' in sys.argv:cases=[(422,c,seed) for c in ('release-fire','release-flare','release-mixed') for seed in (0,3)]+[(423,c,3) for c in ('break-favorable','break-immune')]
if '--utility' in sys.argv:cases=[(a,'utility',3) for a in range(410,421)]+[(416,'recover-hp',3),(419,'recover-mp',3)]
if '--recovery-only' in sys.argv:cases=[(416,'recover-hp',3),(419,'recover-mp',3)]
if '--break-only' in sys.argv:cases=[(423,c,3) for c in ('break-favorable','break-immune')]
if '--allied-control' in sys.argv:cases=[(422,'allies',3)]
if '--remaining' in sys.argv:cases=[c for c in cases if c[1]!='attack']
(OUT/'report.json').write_text(json.dumps(dict(passed=False,romSha1=meta['romSha1'])),encoding='utf-8')
for action,condition,seed in cases:
 case=(action,condition,seed);folder=OUT/('-'.join(map(str,case)));folder.mkdir(exist_ok=True);e=E(TEST_ROM)
 try:
  e.load(OUT/'start.state');e.set_memory(LOG+148,struct.pack('<II',1,seed))
  e.set_memory(ACTOR+0x40,bytes(0x90))
  lesson=next(l for l in registry['lessons'] if l['id']=='MYK-A'+str(action-409))
  index=next(o['abilityIndex'] for o in lesson['owners'] if o['race']==4)
  e.set_memory(ACTOR+0x40+index,b'\xff')
  kind=8 if condition in ('flare','release-flare') else 5 if condition=='bad-fuel' else 1 if condition in ('fire','prepared','allies','release-fire','release-mixed') else 0
  e.set_memory(STATE+20,struct.pack('<H',(88<<4)|kind if kind else 0))
  if condition in ('utility','recover-hp','recover-mp'):
   # Keep all five opponents healthy. The inherited fifth unit otherwise has
   # native story HP and offers a guaranteed free Fight knockout.
   for unit in (0x80,0x188,0x290,0x398,0x4a0):
    e.set_memory(unit+0x18,struct.pack('<4H',999,999,99,100))
  if condition in ('recover-hp','recover-mp'):
   e.set_memory(ACTOR+0x18,struct.pack('<4H',700 if condition=='recover-hp' else 999,999,30,100))
  if condition in ('bare','prepared'):
   e.set_memory(ACTOR+0xeb,b'\x40') # Immobilize prevents approaching; self Act remains legal.
   e.set_memory(0x398+0xf6,bytes((3,12)));e.set_memory(wrappers[0x398]+8,struct.pack('<3H',112,32,400))
  if condition=='allies':
   # Preserve native faction membership. Move opponents beyond Release range
   # and native allies nearby; Immobilize makes the range boundary decisive.
   e.set_memory(ACTOR+0xeb,b'\x40')
   for unit,x,y,height in ((0x80,4,12,32),(0x188,5,12,32),(0x290,6,12,32),(0x398,7,12,32),(0x4a0,8,12,32),(TARGET,1,13,32),(SECOND,1,14,16)):
    e.set_memory(unit+0xf6,bytes((x,y)));e.set_memory(wrappers[unit]+8,struct.pack('<3H',x*32+16,height,y*32+16))
  if condition.startswith(('release-','break-')):
   # Declared anti-armor matchups: physical Fight is poor, magic/Petrify useful.
   e.set_memory(ACTOR+0x20,struct.pack('<4H',40,40,240,40))
   for unit in (0x80,0x188,0x290,0x398,0x4a0):
    e.set_memory(unit+0x20,struct.pack('<4H',40,999,40,10))
    e.set_memory(unit+0x0c,bytes([1]*9))
    if condition=='break-immune':
     e.set_memory(unit+0xe8,b'\x10') # Astra; actual native status prevention.
   if condition.startswith('break-'):e.set_memory(ACTOR+0xe9,b'\x04') # Blind lowers physical accuracy, not S Petrify.
   if condition=='release-mixed':
    e.set_memory(TARGET+0xf6,bytes((2,12)));e.set_memory(wrappers[TARGET]+8,struct.pack('<3H',80,32,400))
  saw_actor=False;last_log=0;casts=[];rendered=set();before=None;result=None;decisions=[]
  for frame in range(30000):
   r=e.memory();w=word(r,0xf4ec);live=word(r,w-0x02000000) if 0x02000000<=w<0x02040000 else 0
   n=0x15488
   d=dict(owner=word(r,n),target=word(r,n+4),action=half(r,n+8),phase=half(r,n+0x1b8),benefit=r[n+0x28],score=word(r,n+0x1c),success=r[n+0x1b1],aiPhase=half(r,0x156ec))
   if not decisions or decisions[-1]!=d:decisions.append(d)
   count=word(r,LOG+4)
   if count!=last_log:
    check('one-execution-per-frame',count==last_log+1);last_log=count
    if word(r,LOG+24)==0x02000000+ACTOR:
     casts.append(dict(action=word(r,LOG+8),choice=word(r,LOG+132),beforeMP=word(r,LOG+140)))
     result=checkpoint(e,'native-result',folder)
   if live==0x02000000+ACTOR:
    if not saw_actor:before=checkpoint(e,'AI-turn-start',folder)
    saw_actor=True;rendered.add(hashlib.sha1(e.frame[0]).hexdigest())
   elif saw_actor and live:
    final=checkpoint(e,'native-handoff',folder);break
   if observe['menu_visible'](e):
    check('AI-never-needs-player-input',active(e)!=0x02000000+ACTOR)
    for key in (32,32,256):inputs.append((case,frame,key));tap(e,key)
    inputs.append((case,frame,256));e.run(8,256)
   e.run(1)
  else:raise AssertionError(('AI turn timeout',case))
  allowed=(0,) if condition in ('no-fuel','bad-fuel','allies','prepared','break-immune') else (0,action)
  check('one-action-or-wait',len(casts)<=1)
  check('only-learned-valid-actions',all(c['action'] in allowed for c in casts))
  if casts and casts[0]['action']==action:
   selected=casts[0];delta=selected['beforeMP']-half(final,ACTOR+0x1c)
   check('single-MP-payment',costs[action]-10<=delta<=costs[action] if action==419 else delta==costs[action])
   if action<=420:check('actual-prepared-enchantment',half(final,STATE+20)&15==action-409)
   if action==422:check('Release-consumes-fuel',half(final,STATE+20)&15==0)
  if condition.startswith('release-'):
   check('chooses-Release-over-ineffective-Fight',len(casts)==1 and casts[0]['action']==422)
   check('Release-real-enemy-damage',any(half(result,u+0x18)<half(before,u+0x18) for u in (0x80,0x188,0x290,0x398,0x4a0)))
   if condition=='release-mixed':check('mixed-area-avoids-nearby-ally',half(result,TARGET+0x18)==half(before,TARGET+0x18))
  if condition in ('utility','recover-hp','recover-mp'):
   check('chooses-useful-command-'+str(action),len(casts)==1 and casts[0]['action']==action)
   check('command-real-enemy-damage',any(half(result,u+0x18)<half(before,u+0x18) for u in (0x80,0x188,0x290,0x398,0x4a0)))
   if condition=='recover-hp':check('Drain-real-recovery',half(result,ACTOR+0x18)>half(before,ACTOR+0x18))
   if condition=='recover-mp':check('Osmose-real-recovery',half(result,ACTOR+0x1c)>casts[0]['beforeMP']-costs[action])
  if condition=='break-favorable':check('chooses-useful-Petrify',len(casts)==1 and casts[0]['action']==423)
  if condition=='bare':
   check('autonomous-self-preparation',len(casts)==1 and casts[0]['action']==action)
   check('self-preparation-no-HP-loss',half(result,ACTOR+0x18)==half(before,ACTOR+0x18))
   check('immobilized-stays-at-input-tile',final[ACTOR+0xf6:ACTOR+0xf8]==bytes((0,14)))
  if condition=='allies':check('no-allied-only-Release',not casts)
  if condition=='prepared':check('does-not-refresh-prepared-blade',not casts)
  check('scoped-choice-retired',final[0x3f728:0x3f72c]==bytes(4))
  check('actual-rendering',len(rendered)>3)
  outcomes.append(dict(action=action,condition=condition,seed=seed,casts=casts,frames=frame,
   actorStart=list(before[ACTOR+0xf6:ACTOR+0xf8]),actorEnd=list(final[ACTOR+0xf6:ACTOR+0xf8]),
   losses={hex(u):half(before,u+0x18)-half(result,u+0x18) for u in wrappers} if result else {}))
  (folder/'outcome.json').write_text(json.dumps(outcomes[-1],indent=2),encoding='utf-8')
  (OUT/'partial.json').write_text(json.dumps(dict(outcomes=outcomes,checks=dict(checks)),indent=2),encoding='utf-8')
 except Exception:
  print(json.dumps(dict(passed=False,romSha1=meta['romSha1'],completedOutcomes=outcomes,checks=dict(checks),failedCase=case),indent=2))
  (folder/'decisions.json').write_text(json.dumps(decisions,indent=2),encoding='utf-8')
  checkpoint(e,'failure',folder);raise
 finally:e.close()
for action in ([] if '--allied-control' in sys.argv else [423] if '--break-only' in sys.argv else [422,423] if '--tactical' in sys.argv else [416,419] if '--recovery-only' in sys.argv else list(range(410,421)) if '--utility' in sys.argv else list(range(410,421))+[422]):
 check('nonvacuous-full-command-'+str(action),any(o['action']==action and o['casts'] and o['casts'][0]['action']==action for o in outcomes))
report=dict(passed=True,romSha1=meta['romSha1'],instrumentedSha1=hashlib.sha1(instrumented).hexdigest(),checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,fixedInputs=inputs,caseSelection=sys.argv[1:])
(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
