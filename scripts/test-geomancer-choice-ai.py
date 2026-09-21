"""Deterministic whole native AI turns for Torrent and Gaia's Wrath.

Inputs declare job, mastery, material masks, formation and seeds. No action,
option, destination, score or combat outcome is supplied to the AI.
"""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/test-passing-step-ai.py').read_text().split("exec(compile(preparation,")[0]
source=source.replace("'DNC-A9'","'GEO-A3'").replace("'passing-step-ai'","'geomancer-choice-ai'")
exec(compile(source,'<fixed native AI preparation>','exec'))
preparation=preparation.replace('0x5a8,0x33e4,0x2fc4','0x4a0,0x33e4,0x2fc4')
preparation=preparation.replace("o['race']==4","o['race']==3").replace("[ACTOR+6]==4","[ACTOR+6]==3").replace('real-Viera','real-Nu-Mou').replace("b'\\x7c'","b'\\x79'")
preparation=preparation.replace('((0x290,1,13,32)', '((0x5a8,1,15,16),(0x290,1,13,32)')
preparation=preparation.replace('exec(compile(support,',
 "support=support.replace('unsigned result=playback_original', 'log[35]=h(*(const uint8_t *const *)actor+0x1c); unsigned result=playback_original')\nexec(compile(support,")
exec(compile(preparation,'<fixed native Geomancer AI formation>','exec'))
# All-affinity ground is an explicit private-ROM input for full-turn coverage;
# the separate search matrix proves movement-dependent option availability.
instrumented[0x11f0000+70*256:0x11f0000+71*256]=bytes([31])*256
TEST_ROM.write_bytes(instrumented)
inputs=[];outcomes=[];variants={}
(OUT/'report.json').write_text(json.dumps(dict(passed=False,romSha1=meta['romSha1'])))
for action,seed,learned in ((376,0,True),(376,3,True),(381,0,True),(381,3,True),(381,18,True),(381,3,False)):
 case=(action,seed,learned);folder=OUT/(str(action)+'-'+str(seed)+'-'+str(learned));folder.mkdir(exist_ok=True)
 moved=action==381 and seed==18
 instrumented[0x11f0000+70*256:0x11f0000+71*256]=bytes([0 if moved else 31])*256
 if moved:instrumented[0x11f0000+70*256+12*16]=8
 fixture_sha=hashlib.sha1(instrumented).hexdigest()
 frozen=OUT/'roms'/(fixture_sha+'.gba');frozen.parent.mkdir(exist_ok=True)
 if not frozen.exists():frozen.write_bytes(instrumented)
 variants[fixture_sha]=str(frozen)
 TEST_ROM.write_bytes(instrumented);e=E(TEST_ROM)
 try:
  e.load(OUT/'start.state');e.set_memory(LOG+148,struct.pack('<II',1,seed))
  e.set_memory(ACTOR+0x40,bytes(0x90))
  if moved:
   for unit in wrappers:
    if unit!=ACTOR:
     e.set_memory(unit+0x0e,b'\x03');e.set_memory(unit+0x0d,b'\x00')
  lesson=next(l for l in registry['lessons'] if l['id']==('GEO-A3' if action==376 else 'GEO-A8'))
  index=next(o['abilityIndex'] for o in lesson['owners'] if o['race']==3)
  if learned:e.set_memory(ACTOR+0x40+index,b'\xff')
  saw_actor=False;last_log=0;casts=[];rendered=set();before=None;damage=0
  for frame in range(30000):
   r=e.memory();w=word(r,0xf4ec);live=word(r,w-0x02000000) if 0x02000000<=w<0x02040000 else 0
   count=word(r,LOG+4)
   if count!=last_log:
    check('one-execution-per-frame',count==last_log+1);last_log=count
    if word(r,LOG+24)==0x02000000+ACTOR:
     casts.append(dict(action=word(r,LOG+8),choice=word(r,LOG+132),beforeMP=word(r,LOG+140)))
     result=checkpoint(e,'native-result',folder)
     damage=sum(max(0,half(before,u+0x18)-half(result,u+0x18)) for u in wrappers if not (before[u+0x29]&128))
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
  selected=casts[0];actual=selected['action']
  check('only-learned-actions',actual in ((0,action) if learned else (0,)))
  if actual==action:
   check('native-choice-carried',1<=selected['choice']<=(4 if action==376 else 5))
   check('single-MP-payment',selected['beforeMP']-half(final,ACTOR+0x1c)==(8 if action==376 else 18))
  if moved:
   check('native-moved-Fire-choice',actual==381 and selected['choice']==1)
  check('scoped-choice-retired',final[0x3f728:0x3f72c]==bytes(4))
  check('actual-rendering',len(rendered)>3)
  outcomes.append(dict(action=action,seed=seed,learned=learned,casts=casts,frames=frame,enemyHPLost=damage,
   fixtureSha1=fixture_sha,terrain='heat-after-move' if moved else 'all-affinities'))
 except Exception:
  checkpoint(e,'failure',folder);raise
 finally:e.close()
for action in (376,381):
 check('nonvacuous-full-AI-'+str(action),any(o['casts'][0]['action']==action for o in outcomes))
 check('actual-damaging-cast-'+str(action),any(o['casts'][0]['action']==action and o['enemyHPLost']>0 for o in outcomes))
report=dict(passed=True,romSha1=meta['romSha1'],instrumentedVariants=variants,
 checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,fixedInputs=inputs)
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
