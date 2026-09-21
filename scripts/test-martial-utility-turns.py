"""Fixed autonomous martial utility turns using the retained exact-ROM battle capture.

Only initial job/mastery, formation, resources and RNG seeds are supplied.
Native AI selects its command and target; real execution/rendering follow.
"""
import pathlib
from datetime import datetime,timezone
ROOT=pathlib.Path(__file__).resolve().parents[1]
name='martial-utility-turns-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
support=(ROOT/'scripts/test-integrated-reaction-playback.py').read_text().split('for lesson,job,race,weapon,hidden in cases:')[0]
support=support.replace("FIX=LAB/'fixture'","FIX=LAB/'fixture-two-geomancers'")
support=support.replace("OUT=LAB/'reaction-playback'",'OUT=LAB/'+repr(name))
support=support.replace('unsigned result=playback_original','log[35]=h(*(const uint8_t *const *)actor+0x1c); unsigned result=playback_original')
exec(compile(support,'<native playback recorder>','exec'))
ACTOR,TARGET,SECOND=0x80,0x33e4,0x2fc4
STATE=0x3f410+((ACTOR-0x80)//264)*22
inputs=[];outcomes=[];tests=[(351,'useful',0x87654321),(359,'useful',5),(360,'useful',5),(364,'useful',0x12345678),(368,'useful',5)]
if '--kiyomori' in sys.argv:tests=[t for t in tests if t[0]==351]
if '--remaining' in sys.argv:tests=[t for t in tests if t[0]!=359]
if '--custom-wards' in sys.argv:tests=[t for t in tests if t[0] in (360,364,368)]
if '--kiyomori-sweep' in sys.argv:
 tests=[(351,'useful',s) for s in (0xdeadbeef,0x87654321,0x80000000,0x01010101,
  0x2468ace0,0x31415926,0xabcdef01,0xfeedface,0x54321abc,0x76543210,0x13579bdf,
  0x98765432,0x19283746,0xfaceb00c,0x12003400,0x11223344)]

def checkpoint(e,label,folder):
 r=capture(e,label,folder)
 check('native-renderer-code-intact',C.string_at(*e.maps[0x03000000])[CODE_FIRST:CODE_LAST]==NATIVE_CODE)
 return r
def save_report(passed):
 result=dict(passed=passed,romSha1=meta['romSha1'],instrumentedSha1=hashlib.sha1(instrumented).hexdigest(),
  checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,fixedInputs=inputs,scope=__doc__)
 (OUT/'report.json').write_text(json.dumps(result,indent=2));return result
save_report(False)
for action,condition,seed in tests:
 ACTOR=0x398 if action==368 else 0x80
 STATE=0x3f410+((ACTOR-0x80)//264)*22
 case=(action,condition,seed);folder=OUT/('-'.join(map(str,case)));folder.mkdir(exist_ok=True);e=E(TEST_ROM)
 try:
  e.load(FIX/'battle-ready.state');e.run(1);menu(e)
  # Finish the initially captured player turn through its real Wait control.
  # The subsequent AI turn is observed from its natural scheduler handoff.
  if active(e)==0x02000000+ACTOR:
   for key in (32,32,256):tap(e,key)
   e.run(8,256);menu(e,0x02000000+ACTOR)
  fixed_giza_formation(image,e)
  race=2 if action==368 else 1;job=118 if action==368 else 116 if action==351 else 117
  check('native-racial-sprite',e.memory()[ACTOR+6]==race)
  for offset in (5,7,0x35):e.set_memory(ACTOR+offset,bytes((job,)))
  e.set_memory(ACTOR+8,b'\0');e.set_memory(ACTOR+0x36,bytes(2));e.set_memory(ACTOR+0x40,bytes(0x90))
  if race==1:e.set_memory(0x1b40,bytes(112))
  lesson=next(l for l in registry['lessons'] if l['globalAbilityId']==action and l['type'][0]=='A')
  index=next(o['abilityIndex'] for o in lesson['owners'] if o['race']==race)
  e.set_memory(0x1b40+index-144 if race==1 and index>=144 else ACTOR+0x40+index,b'\xff')
  e.set_memory(ACTOR+0x29,b'\x80');e.set_memory(ACTOR+9,b'\x32')
  e.set_memory(ACTOR+0x2a,struct.pack('<5H',376 if action==351 else 1,0,0,0,0));e.set_memory(ACTOR+0x3a,bytes(2))
  wrappers=from_emulator(image,e)
  for u in wrappers:
   e.set_memory(u+0x18,struct.pack('<4H',999,999,100 if condition=='full' else 1,100));e.set_memory(u+0xe8,bytes(8))
   e.set_memory(u+0x20,struct.pack('<4H',1 if u==ACTOR else 70,220,80,40))
  # Actual Giza floor elevations; useful allies adjacent, hostile units far.
  for u,x,y,h in ((ACTOR,0,14,16),(TARGET,1,13,32),(SECOND,1,14,16),
    (0x32dc,2,14,16),(0x30cc,2,13,32),(0x31d4,1,15,16)):
   e.set_memory(u+0xf6,bytes((x,y)));e.set_memory(wrappers[u]+8,struct.pack('<3H',x*32+16,h,y*32+16))
  for u,x,y in ((0x80,7,3),(0x188,8,3),(0x290,9,3),(0x398,10,3),(0x4a0,11,3),(0x5a8,12,3)):
   if u==ACTOR:continue
   e.set_memory(u+0xf6,bytes((x,y)));e.set_memory(wrappers[u]+8,struct.pack('<3H',x*32+16,80,y*32+16))
  if action==359:e.set_memory(ACTOR+0x18,struct.pack('<H',100))
  if action==368:
   e.set_memory(ACTOR+0xeb,b'\x08');e.set_memory(SECOND+0xe9,b'\x04')
  e.set_memory(ACTOR+0x1c,struct.pack('<H',100))
  e.set_memory(0x3ff44,bytes(8)+b'\xd7'*0xb4);e.set_memory(LOG,bytes(160));e.set_memory(LOG+148,struct.pack('<II',1,seed))
  checkpoint(e,'declared-input',folder);saw=False;casts=[];last=0;rendered=set();before=None;result=None
  for frame in range(30000):
   r=e.memory();w=word(r,0xf4ec);live=word(r,w-0x02000000) if 0x02000000<=w<0x02040000 else 0
   # Recorder publishes complete result rows only; a frame may end mid-call.
   if word(r,LOG)==0x504c4159 and word(r,LOG+4)!=last:
    last=word(r,LOG+4)
    if word(r,LOG+24)==0x02000000+ACTOR:
     casts.append(dict(action=word(r,LOG+8),beforeMP=word(r,LOG+140)))
     result=checkpoint(e,'native-result',folder)
   if live==0x02000000+ACTOR:
    if not saw:
     C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4)
     before=checkpoint(e,'AI-turn-start',folder)
    saw=True;rendered.add(hashlib.sha1(e.frame[0]).hexdigest())
   elif saw and live:
    final=checkpoint(e,'native-handoff',folder);break
   if observe['menu_visible'](e):
    check('AI-does-not-request-player-input',active(e)!=0x02000000+ACTOR)
    for key in (32,32,256):inputs.append((case,frame,key));tap(e,key)
    inputs.append((case,frame,256));e.run(8,256)
   e.run(1)
  else:raise AssertionError(('native turn timeout',case))
  check('at-most-one-action',len(casts)<=1)
  check('only-learned-useful-affordable-actions',all(c['action'] in ((0,action) if condition=='useful' else (0,)) for c in casts))
  if casts and casts[0]['action']==action:
   check('exact-command-cost',casts[0]['beforeMP']-half(result,ACTOR+0x1c)==(10 if action in (351,364) else 8))
   if action==351:check('caster-gets-Protect-and-Shell',result[ACTOR+0xeb]&3==3)
   if action==359:
    check('caster-gets-Shell',result[ACTOR+0xeb]&1==1)
    check('actual-Dark-Mind-recovery',half(result,ACTOR+0x18)-half(before,ACTOR+0x18)==100)
   if action==360:
    check('actual-owned-Last-Resort',result[STATE]&3>0)
    check('self-mode-has-no-HP-strike',half(result,ACTOR+0x18)==half(before,ACTOR+0x18))
   if action==368:
    check('caster-gets-War-Cry',result[STATE+4]&3>0)
    check('silenced-caster-is-cured',not result[ACTOR+0xeb]&8)
   if action==364:
    check('actual-TBN-source-and-ward',any(result[0x3f410+i*22+1]==1 and result[0x3f410+i*22+2]==1 for i in range(36)))
    check('exact-TBN-sacrifice',half(before,ACTOR+0x18)-half(result,ACTOR+0x18)==100)
  check('choice-root-retired',final[0x3f728:0x3f72c]==bytes(4))
  check('native-rendering-advances',len(rendered)>3)
  outcomes.append(dict(action=action,condition=condition,seed=seed,casts=casts,frames=frame));save_report(False)
 except Exception:
  checkpoint(e,'failure',folder);save_report(False);raise
 finally:e.close()
 if '--kiyomori-sweep' in sys.argv and casts and casts[0]['action']==action:break
for action in {a for a,c,s in tests if c=='useful'}:check('nonvacuous-autonomous-utility-'+str(action),any(o['casts'] and o['casts'][0]['action']==action for o in outcomes))
print(json.dumps(save_report(True),indent=2))
