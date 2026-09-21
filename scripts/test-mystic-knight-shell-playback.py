"""Fixed Doublecast inputs with two Viera loaded before deployment.

The second Viera is a declared pre-battle roster fixture. Native deployment
loads her graphics. Actual menu inputs, forecasts, casts and renderer run normally.
"""
import pathlib,datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/test-doublecast-playback.py').read_text(encoding='utf-8').split('for placement in ')[0]
source=source.replace("(ROOT/'scripts/test-equipment-legality.py').read_text()","(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000')")
source=source.replace("OUT=LAB/'doublecast-playback'","OUT=LAB/('shell-playback-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))")
# Keep all recorder/helpers, then run the unchanged Doublecast navigation on
# a freshly deployed matching fixture with two native Viera sprites.
header,prepare=source.split('e=E(TEST_ROM)',1)
exec(compile(header,'<Shell deterministic recorder>','exec'))
e=E(TEST_ROM)
try:
 e.load(FIX/'giza-cursor.state')
 check('prebattle-native-Bangaa-record',e.memory()[TARGET+6]==2)
 for offset,value in ((5,125),(6,4),(7,125),(8,0),(0x35,125)):
  e.set_memory(TARGET+offset,bytes((value,)))
 e.set_memory(TARGET+0x36,bytes(8));e.set_memory(TARGET+0x40,bytes(0x90))
 e.set_memory(TARGET+0x2a,struct.pack('<5H',88,0,0,0,0))
 tap(e,256,1200)
 for _ in range(7):tap(e,256,600)
 for _ in range(3):tap(e,256)
 for _ in range(3):
  for key in (128,256,256,256):tap(e,key)
 tap(e,8,600);tap(e,256,600);tap(e,256,600);menu(e)
 check('deployed-second-Viera',e.memory()[TARGET+6]==4)
 e.save(OUT/'two-viera-battle.state');e.screenshot(OUT/'two-viera-battle.png')
finally:e.close()
prepare='e=E(TEST_ROM)'+prepare
prepare=prepare.replace('if active(e)==0x02000000+ACTOR:break','if turn and active(e)==0x02000000+ACTOR:break')
prepare=prepare.replace("FIX/'battle-ready.state'","OUT/'two-viera-battle.state'")
prepare=prepare.replace("check('real-Bangaa-recipient',e.memory()[TARGET+6]==2)","check('real-Viera-recipient',e.memory()[TARGET+6]==4)")
prepare=prepare.replace('for key in (256,16,256,256,32,256,32,256):tap(e,key)', 'for key in (256,16,256):tap(e,key)\n menu(e)\n for key in (256,32,256,32,256):tap(e,key)')
exec(compile(prepare,'<fixed Doublecast selection preparation>','exec'))

original_checkpoint=checkpoint
def checkpoint(e,label,folder):
 (folder/(label+'.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
 return original_checkpoint(e,label,folder)

def predicted(e):
 r=e.memory();root=word(r,0xf440)-0x02000000;panel=word(r,root+8)-0x02000000
 check('native-forecast-panel',0<=panel<len(r)-0x30)
 return struct.unpack_from('<h',r,panel+0x2e)[0],r[panel+0x2d]

def raw_damage(e,shelled=False):
 m=armns['ARM'](image,C.string_at(*e.maps[0x03000000]));m.put(0x02000000,e.memory())
 sp=0x03007800
 if shelled:
  m.call(0x080ce070,0x02000000+TARGET,1,stack=sp)
  m.call(0x080ce440,0x02000000+TARGET,3,stack=sp)
 m.put(sp,struct.pack('<2I',0,2));return m.call(0x08130200,0x02000000+ACTOR,0x02000000+TARGET,23,88,stack=sp)

for placement,kind in (('same','off'),('same','reaction'),('same','ordinary'),('first-only','off'),('first-only','reaction')):
 case=(placement,kind);folder=OUT/(placement+'-'+kind);folder.mkdir()
 e=E(TEST_ROM)
 try:
  e.load(OUT/'doublecast-first-choice.state')
  raw=raw_damage(e);protected=raw_damage(e,True);hp=250+raw+1
  check('pair-only-threshold-input',0<protected<raw and hp<=500)
  e.set_memory(TARGET+0x18,struct.pack('<H',hp))
  equip(e,TARGET,'MYK-R1',4,kind=='reaction')
  if kind=='ordinary':
   e.set_memory(TARGET+0xeb,b'\x01');e.set_memory(TARGET+0xdd,b'\x03')
  # First Fire selection, area highlight, then target confirmation.
  for key in (256,128,256):tap(e,key)
  first=checkpoint(e,'first-forecast',folder);first_value=predicted(e)
  check('first-forecast-is-single-spell',first_value[0]==(protected if kind=='ordinary' else raw))
  check('first-preview-does-not-grant-Shell',bool(first[TARGET+0xeb]&1)==(kind=='ordinary'))
  # Commit first area, select second spell and center. The second native
  # forecast is where the combined threshold can now affect mitigation.
  for key in (256,256)+((128,) if placement=='same' else (128,128,128))+(256,):tap(e,key)
  before=checkpoint(e,'second-forecast',folder);second_value=predicted(e)
  check('second-selection-controller',before[0xf4e8+0xae]==1 and half(before,0xf4e8+0xdc)==0x31)
  check('no-execution-in-preview',word(before,LOG+4)==0)
  if placement=='same':check('combined-damage-reaches-native-panel',second_value[0]==(raw if kind=='off' else protected))
  check('second-preview-does-not-grant-Shell',bool(before[TARGET+0xeb]&1)==(kind=='ordinary'))
  tap(e,256)
  checkpoint(e,'commit-confirmation',folder)
  check('confirmation-before-execution',word(e.memory(),LOG+4)==0)
  e.set_memory(LOG+148,struct.pack('<II',1,3));tap(e,256,1);seen={};rendered=set()
  for frames in range(2401):
   r=e.memory();n=word(r,LOG+4)
   if n and n not in seen:seen[n]=checkpoint(e,'cast-'+str(n),folder)
   rendered.add(hashlib.sha1(e.frame[0]).hexdigest())
   if frames%240==0:e.screenshot(folder/f'frame-{frames:04}.png')
   if n==2 and frames>300 and half(r,0xf4e8+0xdc)==47:break
   if frames<2400:e.run(1)
  after=checkpoint(e,'after-playback',folder)
  check('two-real-native-casts',set(seen)=={1,2} and word(after,LOG+4)==2)
  expected=kind=='ordinary' or (kind=='reaction' and placement=='same')
  check('Shell-before-first-result',bool(seen[1][TARGET+0xeb]&1)==expected)
  check('Shell-survives-rendering',bool(after[TARGET+0xeb]&1)==expected)
  check('ordinary-Shell-three-turn-timer',after[TARGET+0xdd]==(3 if expected else 0))
  check('actual-first-spell-damage',half(seen[1],TARGET+0x18)<hp)
  check('two-native-MP-payments',half(before,ACTOR+0x1c)-half(after,ACTOR+0x1c)==12)
  check('no-rendered-repeat',after[TARGET+0x18:TARGET+0x20]==seen[2][TARGET+0x18:TARGET+0x20])
  check('AP-inventory-unchanged',after[0x1940:0x1e70]==before[0x1940:0x1e70])
  check('native-rendered-frames',len(rendered)>3)
  check('continuation-retired',owned(e)[2]==bytes(16))
  previous=active(e);tap(e,256,900);menu(e,previous);checkpoint(e,'next-turn',folder)
  outcomes.append(dict(placement=placement,kind=kind,raw=raw,protected=protected,hp=hp,firstForecast=first_value,secondForecast=second_value,
   firstHP=half(seen[1],TARGET+0x18),finalHP=half(after,TARGET+0x18),frames=frames,uniqueFrames=len(rendered)))
  (OUT/'completed.json').write_text(json.dumps(outcomes,indent=2),encoding='utf-8')
 finally:e.close()
check('pair-exact-ordinary-Shell-control',[(r['firstHP'],r['finalHP']) for r in outcomes if r['placement']=='same' and r['kind'] in ('reaction','ordinary')][0]==[(r['firstHP'],r['finalHP']) for r in outcomes if r['placement']=='same' and r['kind'] in ('reaction','ordinary')][1])
check('pair-protection-effective',outcomes[1]['finalHP']>outcomes[0]['finalHP'])
check('different-area-no-premature-Shell',outcomes[3]['firstHP']==outcomes[4]['firstHP'] and outcomes[3]['finalHP']==outcomes[4]['finalHP'])
report=dict(passed=True,romSha1=meta['romSha1'],instrumentedSha1=hashlib.sha1(instrumented).hexdigest(),checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,
 limits=['Declared predeployment Viera roster; no recruitment/campaign acceptance.','Native Shell status/timer and changing frames are verified; exhaustive animation art review remains separate.'])
(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
