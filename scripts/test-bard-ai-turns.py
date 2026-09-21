"""Fixed autonomous song turns using the retained exact-ROM battle capture.

Only initial job/mastery, formation, resources and RNG seeds are supplied.
Native AI selects its command and target; real execution/rendering follow.
"""
import pathlib
from datetime import datetime,timezone
ROOT=pathlib.Path(__file__).resolve().parents[1]
name='bard-ai-turns-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
support=(ROOT/'scripts/test-integrated-reaction-playback.py').read_text().split('for lesson,job,race,weapon,hidden in cases:')[0]
support=support.replace("FIX=LAB/'fixture'","FIX=LAB/'fixture-two-geomancers'")
support=support.replace("OUT=LAB/'reaction-playback'",'OUT=LAB/'+repr(name))
support=support.replace('unsigned result=playback_original','log[35]=h(*(const uint8_t *const *)actor+0x1c); unsigned result=playback_original')
exec(compile(support,'<native playback recorder>','exec'))
ACTOR,TARGET,SECOND=0x188,0x33e4,0x2fc4
STATE=0x3f410+((ACTOR-0x80)//264)*22
inputs=[];outcomes=[];tests=[(394,'useful',5)]+[(399,'useful',s) for s in (0,3,18)]+[(394,'no-MP',3),(399,'full',3)]
if '--chants-only' in sys.argv:tests=[(394,'useful',5)]
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
 case=(action,condition,seed);folder=OUT/('-'.join(map(str,case)));folder.mkdir(exist_ok=True);e=E(TEST_ROM)
 try:
  e.load(FIX/'battle-ready.state');e.run(1);menu(e);fixed_giza_formation(image,e)
  check('actual-Moogle-sprite',e.memory()[ACTOR+6]==5)
  for offset in (5,7,0x35):e.set_memory(ACTOR+offset,b'\x7b')
  e.set_memory(ACTOR+8,b'\0');e.set_memory(ACTOR+0x36,bytes(2));e.set_memory(ACTOR+0x40,bytes(0x90))
  lesson=next(l for l in registry['lessons'] if l['globalAbilityId']==action and l['type'][0]=='A')
  index=next(o['abilityIndex'] for o in lesson['owners'] if o['race']==5)
  e.set_memory(ACTOR+0x40+index,b'\xff');e.set_memory(ACTOR+0x29,b'\x80');e.set_memory(ACTOR+9,b'\x32')
  e.set_memory(ACTOR+0x2a,bytes(10));e.set_memory(ACTOR+0x3a,bytes(2))
  wrappers=from_emulator(image,e)
  for u in wrappers:
   e.set_memory(u+0x18,struct.pack('<4H',999,999,100 if condition=='full' else 1,100));e.set_memory(u+0xe8,bytes(8))
   e.set_memory(u+0x20,struct.pack('<4H',1 if u==ACTOR else 70,220,80,40))
  for u,x,y,h in ((ACTOR,0,14,16),(TARGET,1,13,32),(SECOND,1,14,16),
   (0x80,7,3,80),(0x290,8,3,80),(0x398,9,3,80),(0x4a0,10,3,80),(0x5a8,11,3,80)):
   e.set_memory(u+0xf6,bytes((x,y)));e.set_memory(wrappers[u]+8,struct.pack('<3H',x*32+16,h,y*32+16))
  if action==394 and condition=='useful':
   # Support scenario: the six native allies cluster around the singer.
   # Original Giza clan tiles supply known native elevations. Seed5 naturally
   # admits this 20%-considered command; no AI result or probability is patched.
   for u,x,y,h in ((0x32dc,2,14,16),(0x30cc,2,13,32),(0x31d4,1,15,16),(0x34ec,3,14,16)):
    e.set_memory(u+0xf6,bytes((x,y)));e.set_memory(wrappers[u]+8,struct.pack('<3H',x*32+16,h,y*32+16))
  e.set_memory(ACTOR+0x1c,struct.pack('<H',0 if condition=='no-MP' else 100))
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
   check('exact-song-cost',casts[0]['beforeMP']-half(result,ACTOR+0x1c)==(12 if action==394 else 0))
   if action==394:
    check('actual-owned-March-granted',any(result[0x3f410+i*22+10]&3 for i in range(36)))
    check('actual-Protect-granted',any(result[u+0xeb]&2 for u in wrappers))
   else:
    check('actual-ally-MP-restored',any(half(result,u+0x1c)>half(before,u+0x1c) for u in wrappers if u!=ACTOR and before[u+0x29]&128))
    check('Ballad-does-not-restore-caster',half(result,ACTOR+0x1c)==casts[0]['beforeMP'])
  check('choice-root-retired',final[0x3f728:0x3f72c]==bytes(4))
  check('native-rendering-advances',len(rendered)>3)
  outcomes.append(dict(action=action,condition=condition,seed=seed,casts=casts,frames=frame));save_report(False)
 except Exception:
  checkpoint(e,'failure',folder);save_report(False);raise
 finally:e.close()
for action in {a for a,c,s in tests if c=='useful'}:check('nonvacuous-autonomous-song-'+str(action),any(o['casts'] and o['casts'][0]['action']==action for o in outcomes))
print(json.dumps(save_report(True),indent=2))
