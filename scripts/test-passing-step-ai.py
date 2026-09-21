"""Actual native AI selection, preselected retreat, payment and turn completion.

The fixed Viera keeps her native sprite. Job, mastery, allegiance, level and
formation are declared fixture inputs. No AI command, route, score or result
is supplied by the test; other player units use a fixed Wait sequence.
"""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
preparation=(ROOT/'scripts/test-dancer-choice-playback.py').read_text().split('# Actual selected player casts')[0]
preparation=preparation.replace('dancer-choice-playback','passing-step-ai').replace("'DNC-A6'","'DNC-A9'")
preparation=preparation.split('    for turn in range(12):')[0]+'''
    e.set_memory(ACTOR+0x29,b'\\x80');e.set_memory(ACTOR+9,b'\\x32')
    for unit,x,y,height in ((0x290,1,13,32),(0x398,1,14,16),(TARGET,6,12,32),(SECOND,7,12,32)):
        e.set_memory(unit+0xf6,bytes((x,y)));e.set_memory(wrappers[unit]+8,struct.pack('<3H',x*32+16,height,y*32+16))
    for unit in (0x80,0x188,0x290,0x398,ACTOR,TARGET,SECOND):
        e.set_memory(unit+0x18,struct.pack('<4H',999,999,99,100));e.set_memory(unit+0xe8,bytes(8))
    e.set_memory(0x3ff44,bytes(8)+b'\\xd7'*0xb4);e.set_memory(LOG,bytes(160))
    checkpoint(e,'start',OUT)
finally:e.close()
'''
exec(compile(preparation,'<fixed native AI fixture>','exec'))
samples=[];inputs=[];outcomes=[]
(OUT/'report.json').write_text(json.dumps(dict(passed=False,romSha1=meta['romSha1'])))

def snapshot(e,label,folder):
 r=checkpoint(e,label,folder);(folder/(label+'.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
 row=dict(label=label,phase=word(r,0x3f004),state=list(struct.unpack_from('<13I',r,0x3f000)),
          battlePhase=half(r,0xf5c4),aiCommands=list(r[0x156dc:0x156e1]),
          actorXY=list(r[ACTOR+0xf6:ACTOR+0xf8]),actorMP=half(r,ACTOR+0x1c),
          loggedCasts=word(r,LOG+4),action=word(r,LOG+8))
 samples.append(row);(OUT/'partial.json').write_text(json.dumps(samples,indent=2));return r

for condition,seed in [('route',0),('route',3),('route',18),('immobilized',3),('unlearned',3)]:
 case=(condition,seed);folder=OUT/(condition+'-'+str(seed));folder.mkdir(exist_ok=True);e=E(TEST_ROM)
 try:
  e.load(OUT/'start.state');e.set_memory(LOG+148,struct.pack('<II',1,seed))
  if condition=='immobilized':e.set_memory(ACTOR+0xeb,b'\x40')
  if condition=='unlearned':e.set_memory(ACTOR+0x40+index,b'\x00')
  saw_actor=False;armed=None;retired=None;last_log=0;actor_casts=[]
  for frame in range(30000):
   r=e.memory();w=word(r,0xf4ec);live=word(r,w-0x02000000) if 0x02000000<=w<0x02040000 else 0
   count=word(r,LOG+4)
   if count!=last_log:
    check('one-execution-per-observed-frame',count==last_log+1);last_log=count
    if word(r,LOG+24)==0x02000000+ACTOR:actor_casts.append(word(r,LOG+8))
   if live==0x02000000+ACTOR:
    saw_actor=True
    if word(r,0x3f000)==0x50535450 and word(r,0x3f004)==4 and armed is None:
     armed=snapshot(e,'preselected-before-strike',folder)
     check('AI-route-precedes-payment',word(armed,0x3f030)==0 and word(armed,0x3f02c)==0)
     check('AI-route-has-no-player-controller',word(armed,0x3f008)==0)
     check('AI-positive-retreat',2<=word(armed,0x3f01c)<=32)
     check('AI-budget-cap',1<=word(armed,0x3f014)<=2)
    if word(r,0x3f000)==0x50535450 and word(r,0x3f004)==7 and retired is None:
     retired=snapshot(e,'completed-native-step',folder)
   elif saw_actor and live:
    final=snapshot(e,'turn-handoff',folder);break
   if observe['menu_visible'](e):
    check('AI-unit-never-needs-player-input',active(e)!=0x02000000+ACTOR)
    for k in (32,32,256):inputs.append((seed,frame,k));tap(e,k)
    inputs.append((seed,frame,256));e.run(8,256)
   e.run(1)
  else:raise AssertionError(('AI turn timeout',seed))
  # Both Fight and Passing Step are legal attacks while immobilized. Preserve
  # the native choice, require exactly one, and verify its actual payment.
  allowed=(0,409) if condition in ('route','immobilized') else (0,)
  check('actual-native-AI-selected-action',len(actor_casts)==1 and actor_casts[0] in allowed)
  if condition=='route' and actor_casts==[0]:
   # Ordinary Fight remains a legal native choice. Encounter setup and prior
   # enemy turns affect AI forecasts; require real Passing Step coverage across
   # the fixed seed set below, rather than forcing it on every native turn.
   check('AI-Fight-does-not-create-retreat',armed is None and retired is None)
   check('AI-Fight-keeps-MP',half(final,ACTOR+0x1c)==100)
   check('AI-Fight-route-state-empty',final[0x3f000:0x3f008]==bytes(8))
   outcomes.append(dict(condition=condition,seed=seed,casts=actor_casts));continue
  if condition!='route':
   check('ineligible-AI-route-never-created',armed is None and retired is None)
   check('ineligible-AI-route-state-empty',final[0x3f000:0x3f008]==bytes(8))
   if condition=='immobilized':
    check('Immobilize-stops-Move-not-strike',final[ACTOR+0xf6:ACTOR+0xf8]==bytes((0,14)))
    check('immobilized-AI-pays-selected-attack-once',half(final,ACTOR+0x1c)==(94 if actor_casts[0]==409 else 100))
   outcomes.append(dict(condition=condition,seed=seed,casts=actor_casts));continue
  check('preselection-and-completion-observed',armed is not None and retired is not None)
  count=word(armed,0x3f01c);endpoint=armed[0x3f058+4*(count-1):0x3f05a+4*(count-1)]
  check('AI-commits-exact-preselected-endpoint',retired[ACTOR+0xf6:ACTOR+0xf8]==endpoint)
  check('AI-turn-does-not-add-second-Move',final[ACTOR+0xf6:ACTOR+0xf8]==endpoint)
  check('AI-pays-six-MP-once',half(armed,ACTOR+0x1c)-half(retired,ACTOR+0x1c)==6)
  check('AI-turn-cleans-transient-route',final[0x3f000:0x3f008]==bytes(8))
  outcomes.append(dict(condition=condition,seed=seed,endpoint=list(endpoint),casts=actor_casts))
 except Exception:
  snapshot(e,'failure',folder);raise
 finally:e.close()
check('nonvacuous-native-AI-Passing-Step',any(o['condition']=='route' and o['casts']==[409] and 'endpoint' in o for o in outcomes))
report=dict(passed=True,romSha1=meta['romSha1'],instrumentedSha1=hashlib.sha1(instrumented).hexdigest(),
            checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,fixedInputs=inputs,samples=samples)
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
