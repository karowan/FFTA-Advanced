"""Five real racial job menus deliver custom effects to the native Judge.

Fixed learning/formation and executor RNG are inputs. Only the test rule and
post-query breakpoints differ; selection, application and reporting are native.
"""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
support=(ROOT/'scripts/test-integrated-reaction-playback.py').read_text().split('for lesson,job,race,weapon,hidden in cases:')[0]
support=support.replace("OUT=LAB/'reaction-playback'","OUT=LAB/'custom-status-law-playback'")
support=support.replace('log[0]=0x504c4159;', 'log[33]=mode;log[34]=(unsigned)out;log[0]=0x504c4159;')
exec(compile(support,'<deterministic custom-law recorder>','exec'))
TARGET,SECOND=0x33e4,0x2fc4
from datetime import datetime,timezone
OUT=OUT/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');OUT.mkdir()
selected={int(a.split('=',1)[1]) for a in sys.argv if a.startswith('--action=')}

def mode(e):
 r=e.memory();return r[word(r,0xf438)-0x02000000+4]

def checkpoint(e,label,folder):
 r=capture(e,label,folder)
 check('native-renderer-intact',C.string_at(*e.maps[0x03000000])[CODE_FIRST:CODE_LAST]==NATIVE_CODE)
 return r

def formation(e):
 wrappers=from_emulator(image,e)
 placements={0x80:(5,14,16),0x188:(4,13,32),0x290:(2,12,32),0x398:(3,12,32),0x4a0:(1,15,16),0x5a8:(0,15,16),
             TARGET:(1,13,32),SECOND:(1,14,16)}
 placements[ACTOR]=(0,14,16)
 for unit,(x,y,z) in placements.items():
  e.set_memory(unit+0xf6,bytes((x,y)));e.set_memory(wrappers[unit]+8,struct.pack('<3H',x*32+16,z,y*32+16))
 for unit in (ACTOR,TARGET,SECOND):
  e.set_memory(unit+0x18,struct.pack('<4H',500,500,100,100));e.set_memory(unit+0xe8,bytes(8))
  e.set_memory(unit+0x20,struct.pack('<4H',70,40,40,40));e.set_memory(unit+0x3a,bytes(2))
 e.set_memory(TARGET+0x0c,bytes([1]*9));e.set_memory(SECOND+0x0c,bytes([1]*9))

for action,lesson,jid,race,ACTOR,weapon in ((355,'SAM-A9',116,1,0x290,383),(373,'VIK-A9',118,2,0x398,399),
 (379,'GEO-A6',121,3,0x4a0,0),(404,'DNC-A4',124,4,0x5a8,0),(405,'DNC-A5',124,4,0x5a8,0)):
 if selected and action not in selected:continue
 case=('setup',action);folder=OUT/str(action);folder.mkdir(exist_ok=True);e=E(TEST_ROM)
 try:
  e.load(FIX/'battle-ready.state');e.run(1);menu(e);fixed_giza_formation(image,e)
  check('actual-racial-sprite',e.memory()[ACTOR+6]==race)
  for offset in (5,7,0x35):e.set_memory(ACTOR+offset,bytes((jid,)))
  e.set_memory(ACTOR+8,b'\0');e.set_memory(ACTOR+0x36,bytes(2));e.set_memory(ACTOR+0x40,bytes(144))
  extra_ap=0x1b40+34*((ACTOR-0x80)//264)
  if race==1:e.set_memory(extra_ap,bytes(34))
  lesson_row=next(l for l in registry['lessons'] if l['id']==lesson)
  index=next(o['abilityIndex'] for o in lesson_row['owners'] if o['race']==race)
  e.set_memory(extra_ap+index-144 if race==1 and index>=144 else ACTOR+0x40+index,b'\xff')
  e.set_memory(ACTOR+0x2a,struct.pack('<5H',weapon,0,0,0,0));formation(e)
  for turn in range(16):
   if active(e)==0x02000000+ACTOR:break
   previous=active(e)
   for key in (32,32,256,256):tap(e,key)
   menu(e,previous)
  check('native-actor-turn',active(e)==0x02000000+ACTOR);formation(e)
  e.set_memory(0x3ff44,bytes(8)+b'\xd7'*0xb4);e.set_memory(LOG,bytes(160))
  for key in (256,16,256):tap(e,key)
  menu(e)
  for key in (256,32,256,256,128,256,256):tap(e,key)
  checkpoint(e,'confirmation',folder)
  check('native-custom-command-confirmation',mode(e)==11 and half(e.memory(),0xf3fc)==action)
 finally:e.close()
 for typ,value,seed in [(16,0,s) for s in (0,3,18)]+[(15,9,3)]:
  case=(action,typ,value,seed);trial=bytearray(instrumented)
  check('known-law-record',trial[0x529348:0x52934a]==bytes((15,28)))
  trial[0x529348:0x52934a]=bytes((typ,value))
  for pc in (0x134e68,0x135076):
   check('native-Judge-return',trial[pc:pc+2]==bytes.fromhex('0006'));trial[pc:pc+2]=bytes.fromhex('fee7')
  case_folder=folder/f'{typ}-{seed}';case_folder.mkdir(exist_ok=True);path=case_folder/'law.gba';path.write_bytes(trial);e=E(path)
  try:
   e.load(folder/'confirmation.state');e.set_memory(LOG+148,struct.pack('<II',1,seed));e.run(8,256)
   for frame in range(2401):
    if word(e.memory(),LOG)==0x504c4159:break
    e.run(1)
   result=checkpoint(e,'transaction',case_folder);e.run(3600)
   final=checkpoint(e,'Judge',case_folder);cpu=struct.unpack_from('<17I',(case_folder/'Judge.state').read_bytes(),0x20)
   check('single-native-command',word(result,LOG+4)==1 and word(result,LOG+8)==action)
   state=0x3f410+(24+(TARGET-0x2fc4)//264)*22
   applied=(half(result,0x1ef4)>>14 in (1,2)) if action==355 else bool(result[state+5]) if action==373 else bool(result[state+17]&0x60) if action==379 else bool(result[state+3]&(7 if action==404 else 56))
   expected=int(typ==16 and applied);trapped=cpu[15] in (0x08134e6a,0x08135078)
   check('application-reaches-Judge',not applied or trapped)
   if trapped:check('native-Judge-reports-custom-effect',cpu[0]==expected)
   else:check('miss-completes-without-violation',not expected and half(final,0xf4e8+0xdc)==47)
   outcomes.append(dict(action=action,law=typ,seed=seed,applied=applied,trapped=trapped,result=cpu[0] if trapped else None,testSha1=hashlib.sha1(trial).hexdigest()))
  except Exception:checkpoint(e,'failure',case_folder);raise
  finally:e.close()
 for item in (action,):check('positive-real-Judge-'+str(item),any(o['action']==item and o['result']==1 for o in outcomes))
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,
 limits=['Stops at native late-law return; final campaign acceptance owns card animation and persistent penalties.'])
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
