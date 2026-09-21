"""Native racial buff menus and occupied/empty field Judge boundaries."""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/test-custom-status-law-playback.py').read_text().split('\nfor action,lesson,jid,race,ACTOR,weapon in ')[0]
source=source.replace("LAB/'custom-status-law-playback'","LAB/'buff-field-law-playback'")
exec(compile(source,'<fixed buff and field recorder>','exec'))
cases=[(359,1,117,0x290,True,False,24),(359,2,119,0x398,True,False,24),
 (398,5,123,0x188,True,False,12),(378,3,121,0x4a0,False,False,25),
 (392,3,120,0x4a0,False,False,25),(392,5,122,0x188,False,False,24),
 (400,5,123,0x188,False,False,24)]
fields=[(action,3,121,0x4a0,False,empty,5 if action==380 else 25) for action in (380,382) for empty in (False,True)]
cases=fields if '--fields-only' in sys.argv else cases
for action,race,jid,ACTOR,own,empty,status in cases:
 case=('setup',action,race,empty);folder=OUT/f'{action}-{race}-{empty}';folder.mkdir();e=E(TEST_ROM)
 try:
  e.load(FIX/'battle-ready.state');e.run(1);menu(e);fixed_giza_formation(image,e)
  check('real-racial-sprite',e.memory()[ACTOR+6]==race)
  for offset in (5,7,0x35):e.set_memory(ACTOR+offset,bytes((jid,)))
  e.set_memory(ACTOR+8,b'\0');e.set_memory(ACTOR+0x36,bytes(2));e.set_memory(ACTOR+0x40,bytes(144))
  row=next(l for l in registry['lessons'] if l['type']=='Action' and l['globalAbilityId']==action)
  index=next(o['abilityIndex'] for o in row['owners'] if o['race']==race)
  extra=0x1b40+34*((ACTOR-0x80)//264)
  if race==1:e.set_memory(extra,bytes(34))
  e.set_memory(extra+index-144 if race==1 and index>=144 else ACTOR+0x40+index,b'\xff')
  e.set_memory(ACTOR+0x2a,bytes(10));formation(e)
  for turn in range(16):
   if active(e)==0x02000000+ACTOR:break
   previous=active(e)
   for key in (32,32,256,256):tap(e,key)
   menu(e,previous)
  check('native-racial-turn',active(e)==0x02000000+ACTOR);formation(e)
  for u in (ACTOR,TARGET,SECOND):e.set_memory(u+0x18,struct.pack('<4H',300,500,100,100))
  if action not in (380,382):
   for u in (TARGET,SECOND):e.set_memory(u+0x29,b'\0')
  if action==392:e.set_memory(0x1940+362,bytes([5])*14)
  if empty:
   ws=from_emulator(image,e)
   for u,x,y in ((0x290,4,14),(0x398,4,13),(0x80,5,14)):
    e.set_memory(u+0xf6,bytes((x,y)));e.set_memory(ws[u]+8,struct.pack('<3H',x*32+16,32,y*32+16))
   r=e.memory();check('empty-center-is-empty',all(abs(r[u+0xf6]-2)+abs(r[u+0xf7]-12)>1 for u in ws))
  e.set_memory(0x3ff44,bytes(8)+b'\xd7'*0xb4);e.set_memory(LOG,bytes(160))
  for key in (256,16,256):tap(e,key)
  menu(e)
  for key in (256,32,256,256):tap(e,key)
  if not own:tap(e,128)
  if empty:tap(e,128);tap(e,16)
  for _ in range(3):
   if mode(e)==11:break
   tap(e,256)
  before=checkpoint(e,'confirmation',folder)
  check('real-buff-field-confirmation',mode(e)==11)
  if not empty:check('selected-action',half(before,0xf3fc)==action)
 finally:e.close()
 rules=((2,5),(2,1)) if action==380 else ((15,25),(16,0)) if action==382 else ((15,status),(15,9))
 for kind,value in rules:
  case=(action,race,empty,kind,value);trial=bytearray(instrumented);trial[0x529348:0x52934a]=bytes((kind,value))
  for pc in (0x134e68,0x135076):
   check('native-Judge-return-opcode',trial[pc:pc+2]==bytes.fromhex('0006'));trial[pc:pc+2]=bytes.fromhex('fee7')
  sub=folder/f'{kind}-{value}';sub.mkdir();path=sub/'law.gba';path.write_bytes(trial);e=E(path)
  try:
   e.load(folder/'confirmation.state');e.set_memory(LOG+148,struct.pack('<II',1,3));e.run(8,256)
   for frame in range(2401):
    if word(e.memory(),LOG)==0x504c4159:break
    e.run(1)
   r=checkpoint(e,'transaction',sub);e.run(3600);final=checkpoint(e,'Judge',sub)
   cpu=struct.unpack_from('<17I',(sub/'Judge.state').read_bytes(),0x20)
   check('one-native-cast',word(r,LOG)==0x504c4159 and word(r,LOG+4)==1 and word(r,LOG+8)==action)
   out=word(r,LOG+136)-0x02000000;check('native-result-range',0<=out<0x40000-0x2c4)
   trapped=cpu[15] in (0x08134e6a,0x08135078)
   if action in (380,382):
    state=0x3f410+((ACTOR-0x80)//264)*22
    check('actual-field-created',r[state+17]&3==(1 if action==380 else 2))
    check('field-payment-once',half(before,ACTOR+0x1c)-half(r,ACTOR+0x1c)==12)
    check('field-center',r[state+15:state+17]==bytes((2,12) if empty else (1,13)))
    if empty:
     check('empty-no-recipient',r[out+0x2c0]==0)
     check('empty-no-invented-Judge-recipient',not trapped and half(final,0xf4e8+0xdc)==47)
    elif action==380:check('occupied-ice-Judge',trapped and cpu[0]==int(value==5))
    else:
     check('Refuge-not-status-law',not trapped or cpu[0]==0)
     if not trapped:check('Refuge-returns-to-control',half(final,0xf4e8+0xdc)==47)
   else:
    check('actual-buff-Judge',trapped and cpu[0]==int(value==status))
    target=ACTOR if own else TARGET
    check('native-buff-exists',bool(r[target+0xe8+status//8]&(1<<(status%8))))
   outcomes.append(dict(action=action,race=race,empty=empty,kind=kind,value=value,trapped=trapped,result=cpu[0] if trapped else None,recipients=r[out+0x2c0],testSha1=hashlib.sha1(trial).hexdigest()))
   (OUT/'completed.json').write_text(json.dumps(outcomes,indent=2))
  except Exception:checkpoint(e,'failure',sub);raise
  finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],total=sum(checks.values()),checks=dict(checks),outcomes=outcomes,
 limits=['Native Judge evaluation/empty-result skip only; campaign card penalties remain separate.'])
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
