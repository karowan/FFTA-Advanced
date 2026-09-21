"""Fixed real Viera inputs for every Mystic command and self-enchantment.

The controlled fixture gives mastery, equipment and declared native buffs.
All choices, hit results, state changes, rendering and turn return are native.
"""
import pathlib,datetime,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
support=(ROOT/'scripts/test-integrated-reaction-playback.py').read_text().split('for lesson,job,race,weapon,hidden in cases:')[0]
lifecycle='--lifecycle' in sys.argv
output_name='mystic-knight-lifecycle-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ') if lifecycle else 'mystic-knight-playback'
support=support.replace("OUT=LAB/'reaction-playback'",f"OUT=LAB/{output_name!r}")
support=support.replace('log[0]=0x504c4159;', 'log[33]=mode;log[34]=(unsigned)out;log[0]=0x504c4159;')
exec(compile(support,'<deterministic Mystic recorder>','exec'))
ACTOR,TARGET,SECOND=0x5a8,0x33e4,0x2fc4
STATE=0x3f410+5*22
costs=[6,6,6,6,10,8,12,20,12,8,12,10,14,24]
failures=[]

def mode(e):
 r=e.memory();return r[word(r,0xf438)-0x02000000+4]

def checkpoint(e,label,folder):
 r=capture(e,label,folder)
 check('native-renderer-intact',C.string_at(*e.maps[0x03000000])[CODE_FIRST:CODE_LAST]==NATIVE_CODE)
 return r

def formation(e,wrappers):
 for unit,x,y,height in ((ACTOR,0,14,16),(TARGET,1,13,32),(SECOND,1,14,16),(0x290,2,12,32),(0x398,3,12,32)):
  e.set_memory(unit+0xf6,bytes((x,y)))
  e.set_memory(wrappers[unit]+8,struct.pack('<3H',x*32+16,height,y*32+16))

e=E(TEST_ROM)
try:
 e.load(FIX/'battle-ready.state');e.run(1);menu(e);fixed_giza_formation(image,e)
 check('real-Viera',e.memory()[ACTOR+6]==4)
 for offset in (5,7,0x35):e.set_memory(ACTOR+offset,bytes((125,)))
 e.set_memory(ACTOR+8,b'\0');e.set_memory(ACTOR+0x36,bytes(2));e.set_memory(ACTOR+0x40,bytes(0x90))
 for lesson in registry['lessons']:
  if lesson['id'].startswith('MYK-'):
   index=next(o['abilityIndex'] for o in lesson['owners'] if o['race']==4)
   e.set_memory(ACTOR+0x40+index,b'\xff')
   if lesson['id']=='MYK-S1':e.set_memory(ACTOR+0x3b,bytes((index,)))
 e.set_memory(ACTOR+0x3a,b'\0');e.set_memory(ACTOR+0x2a,struct.pack('<5H',88,0,0,0,0))
 for unit in (ACTOR,TARGET,SECOND):
  e.set_memory(unit+0x18,struct.pack('<4H',500,500,100,100));e.set_memory(unit+0xe8,bytes(8))
  e.set_memory(unit+0x20,struct.pack('<4H',70,40,40,40))
 wrappers=from_emulator(image,e);formation(e,wrappers)
 for turn in range(16):
  if active(e)==0x02000000+ACTOR:break
  previous=active(e)
  for key in (32,32,256,256):tap(e,key)
  menu(e,previous)
 check('native-Viera-turn',active(e)==0x02000000+ACTOR)
 wrappers=from_emulator(image,e);formation(e,wrappers)
 for unit in (ACTOR,TARGET,SECOND):
  e.set_memory(unit+0x18,struct.pack('<4H',500,500,100,100));e.set_memory(unit+0xe8,bytes(8))
 e.set_memory(STATE+20,bytes(2))
 e.set_memory(0x3ff44,bytes(8)+b'\xd7'*0xb4);e.set_memory(LOG,bytes(160))
 checkpoint(e,'start',OUT)
finally:e.close()

cases=[(a,0,own) for a in range(410,421) for own in (True,False)]+[(421,7,False),(421,8,False),(422,0,False),(423,0,False)]
if '--navigation' in sys.argv:cases=[(410,0,True)]
if '--remaining' in sys.argv:cases=[(419,0,False),(421,7,False),(421,8,False)]
if lifecycle:
 cases=[(410,0,True),(419,0,False),(421,8,False)]
 if '--sabers-only' in sys.argv:cases=[c for c in cases if c[0]!=419]
 selected=next((int(a.split('=',1)[1]) for a in sys.argv if a.startswith('--only-action=')),None)
 if selected is not None:cases=[c for c in cases if c[0]==selected];assert cases
for action,choice,own in cases:
 case=(action,choice,own);folder=OUT/str(action)/str(choice)/str(own);folder.mkdir(parents=True,exist_ok=True);e=E(TEST_ROM)
 try:
  e.load(OUT/'start.state');e.run(1)
  weapon={410:35,419:88,421:440}.get(action,88) if lifecycle else 88
  e.set_memory(ACTOR+0x2a,struct.pack('<H',weapon))
  if action in (421,422):e.set_memory(STATE+20,struct.pack('<H',(weapon<<4)|1))
  if action==421:
   e.set_memory(TARGET+0xeb,b'\x03') # Both Shell and Protect; select exactly one.
  # Move to0,13, open Spellblade, scroll the actual 34-row native list.
  for step,key in enumerate((256,16,256)):
   tap(e,key)
   if '--navigation' in sys.argv:checkpoint(e,'navigation-'+str(step),folder)
  menu(e)
  for key in (256,32,256):tap(e,key)
  checkpoint(e,'commands',folder)
  row=action-410 if action<=420 else 10+choice if action==421 else 32+(action==423)
  for _ in range(row):tap(e,32,30)
  tap(e,256);selected=checkpoint(e,'targeting',folder)
  manager=word(selected,0xf438)-0x02000000
  check('selected-real-command',word(selected,manager+20)==action)
  if choice:check('selected-exact-buff',half(selected,manager+16)==choice)
  if not own:tap(e,128)
  tap(e,256);preview=checkpoint(e,'preview',folder)
  check('preview-command',half(preview,0xf3fc)==action)
  if choice:check('preview-exact-buff',half(preview,0xf3fe)==choice)
  tap(e,256);before=checkpoint(e,'confirmation',folder)
  check('native-final-confirmation',mode(e)==11)
  check('no-premature-payment',half(before,ACTOR+0x1c)==100 and word(before,LOG+4)==0)
  e.set_memory(LOG+148,struct.pack('<II',1,3));tap(e,256,1)
  rendered=set();executed=None
  for frames in range(2401):
   r=e.memory();rendered.add(hashlib.sha1(e.frame[0]).hexdigest())
   if choice and executed is not None:
    result=word(r,LOG+136)-0x02000000
    if half(r,result+0x10)==action:check('live-choice-retained-during-rendering',half(r,result+0x12)==choice)
   if word(r,LOG)==0x504c4159 and executed is None:executed=checkpoint(e,'native-result',folder)
   if frames%240==0:e.screenshot(folder/f'frame-{frames:04}.png')
   if executed is not None and frames>300 and half(r,0xf4e8+0xdc)==47:break
   if frames<2400:e.run(1)
  check('native-cast-completed',executed is not None)
  after=checkpoint(e,'after-playback',folder)
  check('one-native-executor',word(after,LOG+4)==1 and word(after,LOG+8)==action)
  recovered=100-half(after,TARGET+0x1c) if action==419 and not own else 0
  check('actual-MP-cost',100-half(after,ACTOR+0x1c)==costs[action-410]-recovered)
  check('rendering-no-repeat',all(after[u+0x18:u+0x20]==executed[u+0x18:u+0x20] for u in (ACTOR,TARGET,SECOND)))
  check('AP-inventory-preserved',after[0x1940:0x1e70]==before[0x1940:0x1e70])
  check('learning-preserved',after[ACTOR+0x40:ACTOR+0xd0]==before[ACTOR+0x40:ACTOR+0xd0])
  value=half(after,STATE+20)
  check('correct-final-sequence',(value>>13)&3== (1 if action==421 else 2))
  if action<=420:
   check('native-enchantment-granted',value&15==action-409 and (value>>4)&511==weapon)
   if own:check('self-enchant-does-not-damage',all(half(after,u+0x18)==500 for u in (ACTOR,TARGET,SECOND)))
   tiles=C.string_at(*e.maps[0x06000000]);offset=0x14080+64*(action-410)
   check('actual-enchantment-glyph-upload',any(tiles[offset:offset+64]))
  if action==421:
   check('exact-selected-buff-removed',after[TARGET+0xeb]&3==(2 if choice==7 else 1))
   check('Spellbreak-keeps-enchantment',value&15==1)
  if action==422:check('Release-spends-enchantment',value&15==0)
  if action==423:check('Break-no-HP-damage',half(after,TARGET+0x18)==500)
  check('rendering-changes',len(rendered)>3)
  tiles=C.string_at(*e.maps[0x06000000]);offset=0x14080+64*(11 if action==421 else 12)
  check('actual-next-category-glyph-upload',any(tiles[offset:offset+64]))
  check('retained-choice-after-rendering',not choice or half(after,word(after,LOG+136)-0x02000000+0x12) in (0,choice))
  previous=active(e);tap(e,256,900);menu(e,previous);checkpoint(e,'next-turn',folder)
  if lifecycle:
   expected=e.memory()
   check('positive-state-before-cold',half(expected,STATE+20)==value and value&15!=0)
   for key in (1,8,16,256,256):tap(e,key)
   old=e.memory(0);tap(e,256,300);saved=e.memory(0)
   check('native-suspend-written',saved!=old);(folder/'suspended.sav').write_bytes(saved)
   e.close();e=E(ROM);e.set_memory(0,saved,0);e.run(3600)
   for key,wait in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):tap(e,key,wait)
   menu(e);actual=e.memory()
   check('cold-enchantment-and-sequence',half(actual,STATE+20)==value)
   check('cold-entire-owned-record',actual[STATE:STATE+22]==expected[STATE:STATE+22])
   check('cold-gear-and-lessons',actual[ACTOR+0x2a:ACTOR+0xd0]==expected[ACTOR+0x2a:ACTOR+0xd0])
   check('cold-AP-inventory',actual[0x1940:0x1e70]==expected[0x1940:0x1e70])
   check('cold-HP-MP',all(actual[u+0x18:u+0x20]==expected[u+0x18:u+0x20] for u in (ACTOR,TARGET,SECOND)))
   check('cold-transient-roots',actual[0x3ff44:0x3ff4c]==bytes(8))
   check('cold-native-renderer',C.string_at(*e.maps[0x03000000])[CODE_FIRST:CODE_LAST]==NATIVE_CODE)
   e.save(folder/'cold-resumed.state');e.screenshot(folder/'cold-resumed.png');(folder/'cold-resumed.ram').write_bytes(actual)
   cold.append(dict(action=action,weapon=weapon,value=value,saveSha1=hashlib.sha1(saved).hexdigest()))
  outcomes.append(dict(action=action,choice=choice,selfTarget=own,frames=frames,loss=500-half(after,TARGET+0x18),value=value))
 except AssertionError as exc:
  failures.append(dict(case=case,error=str(exc)))
  # Preserve the original failure even when cold boot legitimately cleared
  # the test-only logger guards; failure capture must not assert recursively.
  e.save(folder/'failure.state');e.screenshot(folder/'failure.png');(folder/'failure.ram').write_bytes(e.memory())
 finally:e.close()
report=dict(passed=not failures,romSha1=meta['romSha1'],instrumentedSha1=hashlib.sha1(instrumented).hexdigest(),checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,cold=cold,failures=failures,
 limits=['Fixed seed and formation; general AI/laws remain separate.','Native frame changes do not certify all animation artwork or exact text placement.'])
(OUT/('remaining-report.json' if '--remaining' in sys.argv else 'navigation-report.json' if '--navigation' in sys.argv else 'report.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not failures,('Mystic player-flow failures',len(failures))
