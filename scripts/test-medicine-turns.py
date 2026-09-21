"""Fixed autonomous medicine turns using the retained exact-ROM battle capture.

Only initial job/mastery, formation, resources and RNG seeds are supplied.
Native AI selects its command and target; real execution/rendering follow.
"""
import pathlib
from datetime import datetime,timezone
ROOT=pathlib.Path(__file__).resolve().parents[1]
name='medicine-turns-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
support=(ROOT/'scripts/test-integrated-reaction-playback.py').read_text().split('for lesson,job,race,weapon,hidden in cases:')[0]
support=support.replace("FIX=LAB/'fixture'","FIX=LAB/'fixture-two-geomancers'")
support=support.replace("OUT=LAB/'reaction-playback'",'OUT=LAB/'+repr(name))
support=support.replace('unsigned result=playback_original','log[34]=mode; log[35]=h(*(const uint8_t *const *)actor+0x1c); unsigned result=playback_original')
exec(compile(support,'<native playback recorder>','exec'))
ACTOR,TARGET,SECOND=0x80,0x33e4,0x2fc4
STATE=0x3f410+((ACTOR-0x80)//264)*22
inputs=[];outcomes=[];tests=[(a,'useful',18 if a==384 else 0x87654321 if a==386 else 0x01010101 if a==392 else 5) for a in range(383,393)]
if '--remaining' in sys.argv:tests=[(a,'useful',seed) for a in (384,386,392) for seed in (0,3,18,0x12345678,0x87654321,0xdeadbeef)]
if '--guarding-sweep' in sys.argv:tests=[(392,'useful',seed) for seed in (0x80000000,0x01010101,0x2468ace0,0x31415926,0xabcdef01,0xfeedface,0x54321abc,0x76543210,0x13579bdf,0x98765432,0x19283746,0xfaceb00c,0x12003400,0x11223344)]
if '--choices' in sys.argv:tests=[t for t in tests if t[0] in (384,386)]
if '--action' in sys.argv:tests=[t for t in tests if t[0]==int(sys.argv[sys.argv.index('--action')+1])]

def checkpoint(e,label,folder):
 r=capture(e,label,folder)
 (folder/(label+'.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
 check('native-renderer-code-intact',C.string_at(*e.maps[0x03000000])[CODE_FIRST:CODE_LAST]==NATIVE_CODE)
 return r
def save_report(passed):
 result=dict(passed=passed,romSha1=meta['romSha1'],instrumentedSha1=hashlib.sha1(instrumented).hexdigest(),
  checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,fixedInputs=inputs,scope=__doc__)
 (OUT/'report.json').write_text(json.dumps(result,indent=2));return result
save_report(False)
for action,condition,seed in tests:
 if ('--remaining' in sys.argv or '--guarding-sweep' in sys.argv) and any(o['action']==action and o['casts'] and o['casts'][0]['action']==action for o in outcomes):continue
 ACTOR=0x188 if action%2 else 0x290
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
  race=5 if action%2 else 3;job=122 if race==5 else 120
  check('native-racial-sprite',e.memory()[ACTOR+6]==race)
  for offset in (5,7,0x35):e.set_memory(ACTOR+offset,bytes((job,)))
  e.set_memory(ACTOR+8,b'\0');e.set_memory(ACTOR+0x36,bytes(2));e.set_memory(ACTOR+0x40,bytes(0x90))
  if race==1:e.set_memory(0x1b40,bytes(112))
  lesson=next(l for l in registry['lessons'] if l['globalAbilityId']==action and l['type'][0]=='A')
  index=next(o['abilityIndex'] for o in lesson['owners'] if o['race']==race)
  e.set_memory(0x1b40+index-144 if race==1 and index>=144 else ACTOR+0x40+index,b'\xff')
  e.set_memory(ACTOR+0x29,b'\x80');e.set_memory(ACTOR+9,b'\x32')
  e.set_memory(ACTOR+0x2a,struct.pack('<5H',0,0,0,0,0));e.set_memory(ACTOR+0x3a,bytes(2))
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
  e.set_memory(ACTOR+0x1c,struct.pack('<H',100))
  # One useful recipient, no competing missing medicine benefits.
  for u in wrappers:
   e.set_memory(u+0x1c,struct.pack('<H',100));e.set_memory(u+0xeb,b'\x03')
   token=(u-0x80)//264 if u<0x2fc4 else 24+(u-0x2fc4)//264
   e.set_memory(0x3f410+token*22+8,b'\x02')
  e.set_memory(TARGET+0x18,struct.pack('<H',0 if action in (385,390) else 200))
  e.set_memory(TARGET+0x1c,struct.pack('<H',1));e.set_memory(TARGET+0xeb,b'\0')
  e.set_memory(0x3f410+(24+(TARGET-0x2fc4)//264)*22+8,b'\0')
  if action in (384,389):e.set_memory(TARGET+0xe9,b'\x02')
  e.set_memory(0x1940+362,bytes((5,))*14)
  e.set_memory(0x3ff44,bytes(8)+b'\xd7'*0xb4);e.set_memory(LOG,bytes(160));e.set_memory(LOG+148,struct.pack('<II',1,seed))
  checkpoint(e,'declared-input',folder);saw=False;casts=[];last=0;rendered=set();before=None;result=None
  for frame in range(30000):
   r=e.memory();w=word(r,0xf4ec);live=word(r,w-0x02000000) if 0x02000000<=w<0x02040000 else 0
   # Recorder publishes complete result rows only; a frame may end mid-call.
   if word(r,LOG)==0x504c4159 and word(r,LOG+4)!=last:
    last=word(r,LOG+4)
    if word(r,LOG+12)==0x02000000+wrappers[ACTOR]:
     casts.append(dict(action=word(r,LOG+8),beforeMP=word(r,LOG+140),selected=word(r,LOG+136),target=word(r,LOG+28),results=word(r,LOG+16)))
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
   check('medicine-has-no-MP-cost',casts[0]['beforeMP']==half(result,ACTOR+0x1c))
   chosen=casts[0]['selected']
   recipe={383:(362,),384:(chosen,),385:(375,),386:(chosen,),387:(362,363),388:(365,),389:(374,),390:(364,375),391:(362,374),392:(362,371)}[action]
   check('exact-recipe-paid-once',result[0x1940+362:0x1940+376]==bytes(4 if i in recipe else 5 for i in range(362,376)))
   if action==384:check('AI-selects-needed-Antidote',chosen==367)
   if action==386:check('AI-selects-useful-X-Potion',chosen==364)
   if action in (383,386,387):check('actual-HP-recovery',half(result,TARGET+0x18)>half(before,TARGET+0x18))
   if action==388:check('actual-MP-recovery',half(result,TARGET+0x1c)>half(before,TARGET+0x1c))
   if action in (384,389):check('actual-Poison-cure',not result[TARGET+0xe9]&2)
   if action in (385,390):check('actual-half-HP-revival',half(result,TARGET+0x18)==half(result,TARGET+0x1a)//2)
   if action==391:check('actual-Inoculated',result[0x3f410+(24+(TARGET-0x2fc4)//264)*22+8]&3>0)
   if action==392:check('actual-Protect-and-Shell',result[TARGET+0xeb]&3==3)
  check('choice-root-retired',final[0x3f728:0x3f72c]==bytes(4))
  check('native-rendering-advances',len(rendered)>3)
  outcomes.append(dict(action=action,condition=condition,seed=seed,casts=casts,frames=frame));save_report(False)
 except Exception:
  capture(e,'failure',folder);save_report(False);raise
 finally:e.close()
for action in {a for a,c,s in tests if c=='useful'}:check('nonvacuous-autonomous-medicine-'+str(action),any(o['casts'] and o['casts'][0]['action']==action for o in outcomes))
print(json.dumps(save_report(True),indent=2))
