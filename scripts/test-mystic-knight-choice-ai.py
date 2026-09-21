"""Fixed complete native Spellbreak AI turns, without supplied decisions."""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/test-passing-step-ai.py').read_text(encoding='utf-8').split("exec(compile(preparation,")[0]
source=source.replace("'DNC-A9'","'MYK-A12'").replace("'passing-step-ai'","'mystic-knight-choice-ai'")
exec(compile(source,'<fixed native AI preparation>','exec'))
preparation=preparation.replace("b'\\x7c'","b'\\x7d'")
preparation=preparation.replace("e.set_memory(ACTOR+0x2a,bytes(10))", "e.set_memory(ACTOR+0x2a,struct.pack('<5H',88,0,0,0,0))")
preparation=preparation.replace('exec(compile(support,',
 "support=support.replace('unsigned result=playback_original', 'log[35]=h(*(const uint8_t *const *)actor+0x1c); unsigned result=playback_original')\nexec(compile(support,")
exec(compile(preparation,'<fixed native Mystic AI formation>','exec'))
inputs=[];outcomes=[]
(OUT/'report.json').write_text(json.dumps(dict(passed=False,romSha1=meta['romSha1'])),encoding='utf-8')
for condition,seed in [('protect',0),('protect',3),('protect',18),('no-buff',3),('unlearned',3)]:
 case=(condition,seed);folder=OUT/(condition+'-'+str(seed));folder.mkdir(exist_ok=True);e=E(TEST_ROM)
 try:
  e.load(OUT/'start.state');e.set_memory(LOG+148,struct.pack('<II',1,seed))
  if condition=='unlearned':e.set_memory(ACTOR+0x40+index,b'\x00')
  if condition!='no-buff':
   for unit in wrappers:
    if not e.memory()[unit+0x29]&128:
     e.set_memory(unit+0xeb,b'\x02');e.set_memory(unit+0xde,b'\x03')
  saw_actor=False;last_log=0;casts=[];rendered=set();before=None
  for frame in range(30000):
   r=e.memory();w=word(r,0xf4ec);live=word(r,w-0x02000000) if 0x02000000<=w<0x02040000 else 0
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
  check('one-native-AI-cast',len(casts)==1)
  selected=casts[0];action=selected['action']
  check('only-learned-valid-actions',action in ((0,421) if condition=='protect' else (0,)))
  if action==421:
   check('exact-Protect-choice-through-movement',selected['choice']==8)
   check('single-MP-payment',selected['beforeMP']-half(final,ACTOR+0x1c)==10)
  check('scoped-choice-retired',final[0x3f728:0x3f72c]==bytes(4))
  check('actual-rendering',len(rendered)>3)
  outcomes.append(dict(condition=condition,seed=seed,casts=casts,frames=frame,actorStart=list(before[ACTOR+0xf6:ACTOR+0xf8]),actorEnd=list(final[ACTOR+0xf6:ACTOR+0xf8]),removed=[u for u in wrappers if before[u+0xeb]&2 and not final[u+0xeb]&2]))
  (OUT/'partial.json').write_text(json.dumps(dict(outcomes=outcomes,checks=dict(checks)),indent=2),encoding='utf-8')
 except Exception:
  checkpoint(e,'failure',folder);raise
 finally:e.close()
check('nonvacuous-full-Spellbreak-AI',any(o['casts'][0]['action']==421 for o in outcomes))
check('actual-selected-removal',any(o['casts'][0]['action']==421 and o['removed'] for o in outcomes))
report=dict(passed=True,romSha1=meta['romSha1'],instrumentedSha1=hashlib.sha1(instrumented).hexdigest(),checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,fixedInputs=inputs)
(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
