"""Fixed player choices deliver original command elements to the late Judge."""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/test-custom-status-law-playback.py').read_text().split('\nfor action,lesson,jid,race,ACTOR,weapon in ')[0]
source=source.replace("LAB/'custom-status-law-playback'","LAB/'carrier-element-law-playback'")
exec(compile(source,'<fixed law-playback setup>','exec'))
# Same declared all-material tile as the accepted Geomancy playback. Move
# brings it into the actor's neighborhood before actual menu construction.
instrumented[0x11f0000+70*256:0x11f0000+71*256]=bytes(256)
instrumented[0x11f0000+70*256+12*16]=31
TEST_ROM.write_bytes(instrumented)
cases=[(410,0,0,True),(410,0,0,False),(422,0,1,False),(422,0,8,False),
       (381,1,0,False),(381,5,0,False)]
for action,choice,fuel,own in cases:
 case=('setup',action,choice,fuel,own)
 ACTOR,race,jid,weapon=(0x4a0,3,121,0) if action==381 else (0x5a8,4,125,88)
 expected=choice if action==381 else 1 if action==410 or fuel==1 else 0
 lesson='GEO-A8' if action==381 else 'MYK-A1' if action==410 else 'MYK-A13'
 state=0x3f410+22*((ACTOR-0x80)//264)
 folder=OUT/('-'.join(map(str,(action,choice,fuel,own))));folder.mkdir();e=E(TEST_ROM)
 try:
  e.load(FIX/'battle-ready.state');e.run(1);menu(e);fixed_giza_formation(image,e)
  check('actual-racial-sprite',e.memory()[ACTOR+6]==race)
  for offset in (5,7,0x35):e.set_memory(ACTOR+offset,bytes((jid,)))
  e.set_memory(ACTOR+8,b'\0');e.set_memory(ACTOR+0x36,bytes(2));e.set_memory(ACTOR+0x40,bytes(144))
  row=next(l for l in registry['lessons'] if l['id']==lesson)
  index=next(o['abilityIndex'] for o in row['owners'] if o['race']==race)
  e.set_memory(ACTOR+0x40+index,b'\xff');e.set_memory(ACTOR+0x2a,struct.pack('<5H',weapon,0,0,0,0));formation(e)
  for turn in range(16):
   if active(e)==0x02000000+ACTOR:break
   previous=active(e)
   for key in (32,32,256,256):tap(e,key)
   menu(e,previous)
  check('native-actor-turn',active(e)==0x02000000+ACTOR);formation(e)
  e.set_memory(state+20,struct.pack('<H',(weapon<<4)|fuel if fuel else 0))
  e.set_memory(0x3ff44,bytes(8)+b'\xd7'*0xb4);e.set_memory(LOG,bytes(160))
  for key in (256,16,256):tap(e,key)
  menu(e)
  for key in (256,32,256):tap(e,key)
  if choice:
   for _ in range((2,3,4,1,5).index(choice)):tap(e,32,30)
  tap(e,256)
  if not own:tap(e,128)
  for _ in range(3):
   if mode(e)==11:break
   tap(e,256)
  r=checkpoint(e,'confirmation',folder)
  check('real-command-confirmation',mode(e)==11 and half(r,0xf3fc)==action)
  if choice:check('actual-menu-element-choice',half(r,0xf3fe)==choice)
 finally:e.close()
 for banned in (expected or 1,8):
  case=(action,choice,fuel,own,banned);trial=bytearray(instrumented)
  trial[0x529348:0x52934a]=bytes((2,banned))
  for pc in (0x134e68,0x135076):
   check('native-Judge-return',trial[pc:pc+2]==bytes.fromhex('0006'));trial[pc:pc+2]=bytes.fromhex('fee7')
  sub=folder/str(banned);sub.mkdir();path=sub/'law.gba';path.write_bytes(trial);e=E(path)
  try:
   e.load(folder/'confirmation.state');e.set_memory(LOG+148,struct.pack('<II',1,3));e.run(8,256)
   for frame in range(2401):
    if word(e.memory(),LOG)==0x504c4159:break
    e.run(1)
   r=checkpoint(e,'transaction',sub);e.run(3600);final=checkpoint(e,'Judge',sub)
   cpu=struct.unpack_from('<17I',(sub/'Judge.state').read_bytes(),0x20)
   check('native-command-once',word(r,LOG)==0x504c4159 and word(r,LOG+4)==1 and word(r,LOG+8)==action)
   if action==422:check('actual-fuel-consumed',half(r,state+20)&15==0)
   check('native-Judge-reached',cpu[15] in (0x08134e6a,0x08135078))
   check('native-Judge-original-element',cpu[0]==int(bool(expected) and banned==expected))
   outcomes.append(dict(action=action,choice=choice,fuel=fuel,self=own,banned=banned,element=expected,result=cpu[0],testSha1=hashlib.sha1(trial).hexdigest()))
  except Exception:checkpoint(e,'failure',sub);raise
  finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,
 limits=['Stops at actual late Judge query. Campaign card animation and persistent penalties remain final acceptance.'])
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
