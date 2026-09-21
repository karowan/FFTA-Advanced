"""Fixed racial menus deliver weapon elements and independent theft to Judge."""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/test-custom-status-law-playback.py').read_text().split('\nfor action,lesson,jid,race,ACTOR,weapon in ')[0]
source=source.replace("LAB/'custom-status-law-playback'","LAB/'carrier-weapon-law-playback'")
exec(compile(source,'<fixed weapon-law playback setup>','exec'))
cases=[(360,True,0,0,3),(360,False,13,0,3),(361,False,13,0,3),(362,False,60,0,3),
       (408,False,91,0,3),(366,False,399,0,3),(367,False,399,354,2),(370,False,399,288,2)]
cases=[(*c,1 if c[0]<365 else 2 if c[0]<374 else 4) for c in cases]
if '--last-resort-only' in sys.argv:
 cases=[(360,own,weapon,0,3,race) for race in (1,2) for own,weapon in ((True,0),(True,13 if race==1 else 68),(False,13 if race==1 else 68))]
cases=[(*c,0) for c in cases]
if '--spellbreak-only' in sys.argv:cases=[(421,False,weapon,0,3,4,choice) for weapon in (88,91) for choice in (7,8)]
for action,own,weapon,loot,seed,race,choice in cases:
 if '--skip-self' in sys.argv and own:continue
 if '--self-only' in sys.argv and not own:continue
 case=('setup',action,own,race,weapon,choice);ACTOR,jid=(0x290,117) if action<365 and race==1 else (0x398,119) if action<365 else (0x398,118) if action<374 else (0x5a8,125 if action==421 else 124)
 kind=1 if action in (366,367,370) else 2;value=23 if kind==1 else 1 if action in (408,421) else 6 if weapon==68 else 5
 folder=OUT/f'{action}-{own}-{race}-{weapon}-{choice}';folder.mkdir();e=E(TEST_ROM)
 try:
  e.load(FIX/'battle-ready.state');e.run(1);menu(e);fixed_giza_formation(image,e)
  check('actual-racial-sprite',e.memory()[ACTOR+6]==race)
  for offset in (5,7,0x35):e.set_memory(ACTOR+offset,bytes((jid,)))
  e.set_memory(ACTOR+8,b'\0');e.set_memory(ACTOR+0x36,bytes(2));e.set_memory(ACTOR+0x40,bytes(144))
  row=next(l for l in registry['lessons'] if l['type']=='Action' and l['globalAbilityId']==action)
  index=next(o['abilityIndex'] for o in row['owners'] if o['race']==race)
  extra=0x1b40+34*((ACTOR-0x80)//264)
  if race==1:e.set_memory(extra,bytes(34))
  e.set_memory(extra+index-144 if race==1 and index>=144 else ACTOR+0x40+index,b'\xff')
  e.set_memory(ACTOR+0x2a,struct.pack('<5H',weapon,0,0,0,0));formation(e)
  for turn in range(16):
   if active(e)==0x02000000+ACTOR:break
   previous=active(e)
   for key in (32,32,256,256):tap(e,key)
   menu(e,previous)
  check('native-actor-turn',active(e)==0x02000000+ACTOR);formation(e)
  e.set_memory(TARGET+0x2a,struct.pack('<5H',loot,0,0,0,0))
  if action==421:
   e.set_memory(TARGET+0xeb,b'\x03')
   e.set_memory(0x3f410+5*22+20,struct.pack('<H',(weapon<<4)|2))
  e.set_memory(0x3ff44,bytes(8)+b'\xd7'*0xb4);e.set_memory(LOG,bytes(160))
  for key in (256,16,256):tap(e,key)
  menu(e)
  for key in (256,32,256):tap(e,key)
  if choice:
   # Native menu starts at the first usable row (Shell7), not row1.
   for _ in range(choice-7):tap(e,32,30)
  tap(e,256)
  if not own:tap(e,128)
  for _ in range(3):
   if mode(e)==11:break
   tap(e,256)
  before=checkpoint(e,'confirmation',folder)
  check('real-carrier-confirmation',mode(e)==11 and half(before,0xf3fc)==action)
  if choice:check('real-selected-buff',half(before,0xf3fe)==choice)
 finally:e.close()
 for banned in (value,8):
  case=(action,own,kind,banned,seed);trial=bytearray(instrumented);trial[0x529348:0x52934a]=bytes((kind,banned))
  for pc in (0x134e68,0x135076):
   check('native-Judge-return',trial[pc:pc+2]==bytes.fromhex('0006'));trial[pc:pc+2]=bytes.fromhex('fee7')
  sub=folder/str(banned);sub.mkdir();path=sub/'law.gba';path.write_bytes(trial);e=E(path)
  try:
   e.load(folder/'confirmation.state');e.set_memory(LOG+148,struct.pack('<II',1,seed));e.run(8,256)
   for frame in range(2401):
    if word(e.memory(),LOG)==0x504c4159:break
    e.run(1)
   r=checkpoint(e,'transaction',sub);e.run(3600);checkpoint(e,'Judge',sub)
   cpu=struct.unpack_from('<17I',(sub/'Judge.state').read_bytes(),0x20)
   check('native-command-once',word(r,LOG)==0x504c4159 and word(r,LOG+4)==1 and word(r,LOG+8)==action)
   check('real-Judge-reached',cpu[15] in (0x08134e6a,0x08135078))
   check('real-Judge-carrier-rule',cpu[0]==int(not own and banned==value and (action!=421 or weapon==91)))
   if choice:
    check('only-selected-buff-removed',r[TARGET+0xeb]&3==(2 if choice==7 else 1))
    check('Spellbreak-keeps-prepared-blade',half(r,0x3f410+5*22+20)&15==2)
   if own:check('weapon-free-self-no-damage',half(r,ACTOR+0x18)==half(before,ACTOR+0x18))
   if loot:check('actual-theft-before-Judge',half(r,TARGET+0x2a)==0)
   outcomes.append(dict(action=action,self=own,race=race,weapon=weapon,choice=choice,kind=kind,banned=banned,seed=seed,result=cpu[0],damage=half(before,TARGET+0x18)-half(r,TARGET+0x18),stolen=bool(loot and not half(r,TARGET+0x2a)),testSha1=hashlib.sha1(trial).hexdigest()))
   (OUT/'completed.json').write_text(json.dumps(outcomes,indent=2))
  except Exception:checkpoint(e,'failure',sub);raise
  finally:e.close()
if '--self-only' not in sys.argv and '--last-resort-only' not in sys.argv and '--spellbreak-only' not in sys.argv:check('positive-theft-law-despite-damage-miss',any(o['stolen'] and not o['damage'] and o['result']==1 for o in outcomes))
report=dict(passed=True,romSha1=meta['romSha1'],total=sum(checks.values()),checks=dict(checks),outcomes=outcomes,
 limits=['Real late Judge return; campaign cards and persistent penalties remain final acceptance.'])
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
