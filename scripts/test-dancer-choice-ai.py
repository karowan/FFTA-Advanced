"""Fixed full native AI turns, without injecting a chosen action or option."""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/test-passing-step-ai.py').read_text().split("exec(compile(preparation,")[0]
source=source.replace("'DNC-A9'","'DNC-A6'").replace("'passing-step-ai'","'dancer-choice-ai'")
exec(compile(source,'<fixed native AI preparation>','exec'))
preparation=preparation.replace('exec(compile(support,',
 "support=support.replace('unsigned result=playback_original', 'log[35]=h(*(const uint8_t *const *)actor+0x1c); unsigned result=playback_original')\nexec(compile(support,")
exec(compile(preparation,'<fixed native AI formation>','exec'))
inputs=[];outcomes=[]
(OUT/'report.json').write_text(json.dumps(dict(passed=False,romSha1=meta['romSha1'])))
for condition,seed in [('learned',0),('learned',3),('learned',18),('unlearned',3)]:
 case=(condition,seed);folder=OUT/(condition+'-'+str(seed));folder.mkdir(exist_ok=True);e=E(TEST_ROM)
 try:
  e.load(OUT/'start.state');e.set_memory(LOG+148,struct.pack('<II',1,seed))
  if condition=='unlearned':e.set_memory(ACTOR+0x40+index,b'\x00')
  saw_actor=False;last_log=0;casts=[];before=None;rendered=set()
  for frame in range(30000):
   r=e.memory();w=word(r,0xf4ec);live=word(r,w-0x02000000) if 0x02000000<=w<0x02040000 else 0
   count=word(r,LOG+4)
   if count!=last_log:
    check('one-execution-per-frame',count==last_log+1);last_log=count
    if word(r,LOG+24)==0x02000000+ACTOR:
     casts.append(dict(action=word(r,LOG+8),choice=word(r,LOG+132),mp=half(r,ACTOR+0x1c),beforeMP=word(r,LOG+140)))
     checkpoint(e,'native-result',folder)
   if live==0x02000000+ACTOR:
    if not saw_actor:before=checkpoint(e,'AI-turn-start',folder)
    saw_actor=True;rendered.add(hashlib.sha1(e.frame[0]).hexdigest())
   elif saw_actor and live:
    final=checkpoint(e,'native-handoff',folder);break
   if observe['menu_visible'](e):
    check('AI-never-needs-player-input',active(e)!=0x02000000+ACTOR)
    for key in (32,32,256):inputs.append((condition,seed,frame,key));tap(e,key)
    inputs.append((condition,seed,frame,256));e.run(8,256)
   e.run(1)
  else:raise AssertionError(('AI turn timeout',case))
  check('one-native-AI-cast',len(casts)==1)
  selected=casts[0];action=selected['action']
  check('only-learned-actions',action in ((0,406) if condition=='learned' else (0,)))
  if action==406:
   check('native-choice-carried',1<=selected['choice']<=4)
   check('single-14MP-payment',selected['beforeMP']-half(final,ACTOR+0x1c)==14)
  check('scoped-choice-retired',final[0x3f728:0x3f72c]==bytes(4))
  check('actual-rendering',len(rendered)>3)
  outcomes.append(dict(condition=condition,seed=seed,casts=casts,frames=frame))
 except Exception:
  checkpoint(e,'failure',folder);raise
 finally:e.close()
check('nonvacuous-native-Forbidden-Dance',any(o['casts'][0]['action']==406 for o in outcomes))
report=dict(passed=True,romSha1=meta['romSha1'],instrumentedSha1=hashlib.sha1(instrumented).hexdigest(),
 checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,fixedInputs=inputs)
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
