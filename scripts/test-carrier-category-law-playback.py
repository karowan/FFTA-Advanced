"""Real medicine menus, payment, rendering and the native late Judge consumer."""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/test-custom-status-law-playback.py').read_text().split('\nfor action,lesson,jid,race,ACTOR,weapon in ')[0]
source=source.replace("LAB/'custom-status-law-playback'","LAB/'carrier-category-law-playback'")
exec(compile(source,'<medicine law-playback setup>','exec'))
for action,full,empty in ((383,False,False),(383,True,False),(388,False,False),(388,True,False),(387,False,False),(387,False,True)):
 if '--empty-only' in sys.argv and not empty:continue
 case=('setup',action,full,empty);ACTOR=0x4a0;race=3;jid=120
 folder=OUT/f'{action}-{full}-{empty}';folder.mkdir();e=E(TEST_ROM)
 try:
  e.load(FIX/'battle-ready.state');e.run(1);menu(e);fixed_giza_formation(image,e)
  check('actual-racial-sprite',e.memory()[ACTOR+6]==race)
  for offset in (5,7,0x35):e.set_memory(ACTOR+offset,bytes((jid,)))
  e.set_memory(ACTOR+8,b'\0');e.set_memory(ACTOR+0x36,bytes(2));e.set_memory(ACTOR+0x40,bytes(144))
  row=next(l for l in registry['lessons'] if l['id']==f'CHM-A{action-382}')
  index=next(o['abilityIndex'] for o in row['owners'] if o['race']==race)
  e.set_memory(ACTOR+0x40+index,b'\xff');e.set_memory(ACTOR+0x2a,bytes(10));formation(e)
  for turn in range(16):
   if active(e)==0x02000000+ACTOR:break
   previous=active(e)
   for key in (32,32,256,256):tap(e,key)
   menu(e,previous)
  check('native-actor-turn',active(e)==0x02000000+ACTOR);formation(e)
  e.set_memory(ACTOR+0x18,struct.pack('<4H',500 if full else 100,500,100 if full else 1,100))
  e.set_memory(0x1940+362,bytes([5])*14)
  e.set_memory(0x3ff44,bytes(8)+b'\xd7'*0xb4);e.set_memory(LOG,bytes(160))
  for key in (256,16,256):tap(e,key)
  menu(e)
  for key in (256,32,256,256):tap(e,key)
  if empty:
   for _ in range(2):tap(e,16)
  for _ in range(3):
   if mode(e)==11:break
   tap(e,256)
  before=checkpoint(e,'confirmation',folder)
  if empty:
   check('empty-selection-not-confirmed',mode(e)==6)
   check('unconfirmed-recipe-not-spent',before[0x1940+362:0x1940+376]==bytes([5])*14)
   check('unconfirmed-recipe-not-executed',word(before,LOG+4)==0)
   for _ in range(2):tap(e,32)
   for _ in range(3):
    if mode(e)==11:break
    tap(e,256)
   restored=checkpoint(e,'restored-self-selection',folder)
   check('restored-self-selection-confirms',mode(e)==11 and half(restored,0xf3fc)==action)
   check('restored-selection-no-early-cost',restored[0x1940+362:0x1940+376]==bytes([5])*14 and word(restored,LOG+4)==0)
   outcomes.append(dict(action=action,empty=True,selectionRejected=True,restoredSelfConfirmed=True))
   (OUT/'completed.json').write_text(json.dumps(outcomes,indent=2))
   continue
  check('real-medicine-confirmation',mode(e)==11 and half(before,0xf3fc)==action)
 finally:e.close()
 for kind,value in ((4,0),(14,25)):
  case=(action,full,empty,kind);trial=bytearray(instrumented)
  trial[0x529348:0x52934a]=bytes((kind,value))
  for pc in (0x134e68,0x135076):
   check('native-Judge-return',trial[pc:pc+2]==bytes.fromhex('0006'));trial[pc:pc+2]=bytes.fromhex('fee7')
  sub=folder/str(kind);sub.mkdir();path=sub/'law.gba';path.write_bytes(trial);e=E(path)
  try:
   e.load(folder/'confirmation.state');e.set_memory(LOG+148,struct.pack('<II',1,3));e.run(8,256)
   for frame in range(2401):
    if word(e.memory(),LOG)==0x504c4159:break
    e.run(1)
   r=checkpoint(e,'transaction',sub);e.run(3600);final=checkpoint(e,'Judge',sub)
   cpu=struct.unpack_from('<17I',(sub/'Judge.state').read_bytes(),0x20)
   check('native-command-once',word(r,LOG)==0x504c4159 and word(r,LOG+4)==1 and word(r,LOG+8)==action)
   ingredients=(362,363) if action==387 else (365,) if action==388 else (362,)
   check('native-recipe-paid-once',r[0x1940+362:0x1940+376]==bytes(4 if i in ingredients else 5 for i in range(362,376)))
   trapped=cpu[15] in (0x08134e6a,0x08135078)
   healed=half(r,ACTOR+0x18)-half(before,ACTOR+0x18)
   expected=int(kind==4 or (kind==14 and healed>25))
   outcome=dict(action=action,full=full,empty=empty,law=kind,healed=healed,trapped=trapped,result=cpu[0] if trapped else None,testSha1=hashlib.sha1(trial).hexdigest())
   outcomes.append(outcome);(OUT/'completed.json').write_text(json.dumps(outcomes,indent=2))
   check('medicine-reaches-Judge',trapped or not expected)
   if trapped:check('native-Judge-medicine-category',cpu[0]==expected)
   if empty:check('empty-Mist-no-HP-recovery',healed==0)
  except Exception:checkpoint(e,'failure',sub);raise
  finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,
 limits=['Stops at native late Judge query; campaign cards and persistent penalties remain final acceptance.'])
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
