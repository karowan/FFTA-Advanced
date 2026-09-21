"""Paired native Spell Parry preview, hit/miss playback and cold-state retention.

Two legal weapon families, fixed native seeds and declared pre-input mastery,
stats, allegiance and an initial Fire enchantment. No damage, reaction claim,
result, preview or serialized output is supplied by the test.
"""
import pathlib,datetime
PARRY_SCOPE=__doc__;ROOT=pathlib.Path(__file__).resolve().parents[1]
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
support=(ROOT/'scripts/test-integrated-reaction-playback.py').read_text().split('cases=[')[0]
support=support.replace("OUT=LAB/'reaction-playback'","OUT=LAB/"+repr('spell-parry-player-'+stamp))
exec(compile(support,'<shared playback recorder>','exec'));SCOPE=PARRY_SCOPE;__doc__=SCOPE
sha=lambda b:hashlib.sha1(b).hexdigest()
proof=json.loads((FIX/'prepare-cache.json').read_text());assert proof['inputs']['romSha1']==meta['romSha1']
for n,digest in proof['outputs'].items():assert sha((FIX/n).read_bytes())==digest
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
STACK,RETURN=0x03007000,0x08000100
nodes=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000')).body
exec(compile(ast.Module(body=[n for n in nodes if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native accessors>','exec'))
TARGET=0x5a8;rows=[];cold=[];retained=[];failure=None;e=None;latest=LAB/'spell-parry-player-latest.json'

def native(e):
 m=ARM(image,C.string_at(*e.maps[0x03000000]));m.put(0x02000000,e.memory());return m

def blade(e):
 m=native(e);return m.call(meta['symbols']['ffta_myk_enchantment'],0x02000000+TARGET)

def snapshot(e,label,folder):
 r=capture(e,label,folder);check('native-renderer-intact',C.string_at(*e.maps[0x03000000])[CODE_FIRST:CODE_LAST]==NATIVE_CODE);return r

def report(passed=False):
 data=dict(passed=passed,romSha1=meta['romSha1'],instrumentedSha1=sha(instrumented),fixture=proof,scope=SCOPE,
           checks=dict(checks),cases=rows,cold=cold,retained=retained,failure=failure)
 p=OUT/'report.json';p.write_text(json.dumps(data,indent=2)+'\n');latest.write_text(json.dumps(dict(report=str(p),sha1=sha(p.read_bytes()),passed=passed)));return data

if '--resume' in sys.argv:
 pointer=json.loads(latest.read_text());p=pathlib.Path(pointer['report']);assert sha(p.read_bytes())==pointer['sha1'];old=json.loads(p.read_bytes())
 assert old['romSha1']==meta['romSha1'] and old['instrumentedSha1']==sha(instrumented) and old['fixture']==proof
 for row in old['cases']+old['cold']:
  for f,digest in row['files'].items():assert sha((pathlib.Path(row['directory'])/f).read_bytes())==digest
 rows.extend(old['cases']);cold.extend(old['cold']);checks.update(old['checks']);retained.append(pointer)
try:
 # One shared current-candidate battle; no new campaign fixture is created.
 e=E(TEST_ROM);e.load(FIX/'battle-ready.state');e.run(1);menu(e);fixed_giza_formation(image,e)
 for turn in range(16):
  if active(e)==0x02000000+ACTOR:break
  previous=active(e)
  for key in (32,32,256,256):tap(e,key)
  menu(e,previous)
 check('native-Marche-turn',active(e)==0x02000000+ACTOR)
 e.set_memory(0x3ff44,bytes(8)+b'\xd7'*0xb4);e.set_memory(LOG,bytes(160));snapshot(e,'start',OUT);e.close();e=None
 for weapon in (35,88):
  for seed in (0,3):
   for enabled in (False,True):
    if any(r['weapon']==weapon and r['seed']==seed and r['enabled']==enabled for r in rows):continue
    case=(weapon,seed,enabled);folder=OUT/f'{weapon}-{seed}-{int(enabled)}';folder.mkdir();e=E(TEST_ROM);e.load(OUT/'start.state');e.run(1)
    wrappers=from_emulator(image,e)
    for u in (ACTOR,TARGET):
     e.set_memory(u+0x18,struct.pack('<4H',500,500,99,99));e.set_memory(u+0x20,struct.pack('<4H',70,40,70,40))
     e.set_memory(u+0xe8,bytes(8));e.set_memory(u+0x3a,bytes(3))
    e.set_memory(ACTOR+0x29,b'\x80');e.set_memory(TARGET+0x29,b'\0')
    e.set_memory(TARGET+0xf6,bytes((3,12)));e.set_memory(wrappers[TARGET]+8,struct.pack('<3H',112,32,400))
    e.set_memory(TARGET+5,bytes((125,4,125)));e.set_memory(TARGET+0x35,bytes((125,0,0)))
    e.set_memory(TARGET+0x2a,struct.pack('<5H',weapon,0,0,0,0));equip(e,TARGET,'MYK-R2',4,enabled)
    e.set_memory(ACTOR+5,bytes((2,1,2)));e.set_memory(ACTOR+0x35,bytes((2,0,0)));e.set_memory(ACTOR+0x2a,struct.pack('<5H',1,0,0,0,0))
    # Native grant on the initial clone; publish only its owned blade word.
    m=native(e);owned=m.call(meta['symbols']['ffta_job_state'],0x02000000+TARGET)
    check('owned-state-located',0x02000000<=owned<0x02040000)
    m.call(meta['symbols']['ffta_myk_grant'],0x02000000+TARGET,1);e.set_memory(owned-0x02000000+20,m.read(owned+20,2))
    check('declared-Fire-enchantment',blade(e)==1)
    initial=snapshot(e,'declared',folder)
    for key in (256,16,256,256,256,128,256):tap(e,key)
    preview=snapshot(e,'preview',folder);check('preview-keeps-live-fuel',blade(e)==1)
    check('preview-keeps-live-HP',half(preview,TARGET+0x18)==500)
    tap(e,256);before=snapshot(e,'confirmation',folder)
    check('native-final-confirmation',before[word(before,0xf438)-0x02000000+4]==11)
    e.set_memory(LOG+148,struct.pack('<II',1,seed));tap(e,256,1)
    rendered=set();executed=None;result=None
    for frame in range(2401):
     r=e.memory();rendered.add(sha(e.frame[0]))
     if word(r,LOG)==0x504c4159 and executed is None:
      executed=snapshot(e,'native-result',folder);result=list(struct.unpack_from('<7I',r,LOG+20))
     if frame%120==0:e.screenshot(folder/f'frame-{frame:04}.png')
     if executed is not None and frame>300 and half(r,0xf4e8+0xdc)==47:break
     if frame<2400:e.run(1)
    check('native-Fight-completed',executed is not None and result[:3]==[0,0x02000000+ACTOR,0x02000000+TARGET])
    after=snapshot(e,'after',folder);loss=500-half(after,TARGET+0x18);fuel=blade(e)
    check('one-native-executor',word(after,LOG+4)==1)
    check('playback-does-not-repeat-HP',after[TARGET+0x18:TARGET+0x20]==executed[TARGET+0x18:TARGET+0x20])
    check('AP-and-inventory-preserved',after[0x1940:0x1e70]==before[0x1940:0x1e70])
    check('lesson-and-equipment-preserved',after[TARGET+0x2a:TARGET+0xd0]==before[TARGET+0x2a:TARGET+0xd0])
    check('rendered-motion',len(rendered)>3)
    previous=active(e);tap(e,256,900);menu(e,previous);snapshot(e,'next-turn',folder)
    check('turn-return-keeps-Parry-result',blade(e)==fuel)
    rows.append(dict(weapon=weapon,seed=seed,enabled=enabled,loss=loss,blade=fuel,result=result,frames=frame,uniqueFrames=len(rendered),directory=str(folder),files={p.name:sha(p.read_bytes()) for p in folder.iterdir() if p.is_file()}))
    e.close();e=None;report()
 for weapon in (35,88):
  pairs=[]
  for seed in (0,3):
   base,on=[next(r for r in rows if r['weapon']==weapon and r['seed']==seed and r['enabled']==enabled) for enabled in (False,True)]
   check('paired-half-damage',on['loss']==base['loss']//2)
   check('control-retains-fuel',base['blade']==1)
   check('actual-hit-spends-miss-preserves',on['blade']==(0 if base['loss'] else 1));pairs.append(base['loss'])
  check('positive-hit-and-miss',any(pairs) and 0 in pairs)
 # One positive and one miss cold-resume: spent and preserved fuel.
 for seed in (0,3):
  if any(r['seed']==seed for r in cold):continue
  case=('cold',seed);row=next(r for r in rows if r['weapon']==35 and r['seed']==seed and r['enabled'])
  folder=OUT/f'cold-{seed}';folder.mkdir();e=E(TEST_ROM);e.load(pathlib.Path(row['directory'])/'next-turn.state');e.run(1)
  expected=e.memory();expected_blade=blade(e)
  for key in (1,8,16,256,256):tap(e,key)
  old_save=e.memory(0);tap(e,256,300);saved=e.memory(0);check('native-suspend-written',saved!=old_save);(folder/'suspended.sav').write_bytes(saved)
  e.close();e=E(ROM);e.set_memory(0,saved,0);e.run(3600)
  for key,wait in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):tap(e,key,wait)
  menu(e);actual=e.memory();check('cold-fuel-spent-or-retained',blade(e)==expected_blade)
  check('cold-HP-MP',actual[TARGET+0x18:TARGET+0x20]==expected[TARGET+0x18:TARGET+0x20])
  check('cold-equipment-lessons',actual[TARGET+0x2a:TARGET+0xd0]==expected[TARGET+0x2a:TARGET+0xd0])
  check('cold-inventory-extra-AP',actual[0x1940:0x1e70]==expected[0x1940:0x1e70])
  check('cold-renderer-intact',C.string_at(*e.maps[0x03000000])[CODE_FIRST:CODE_LAST]==NATIVE_CODE)
  e.save(folder/'cold.state');e.screenshot(folder/'cold.png');(folder/'cold.ram').write_bytes(actual)
  cold.append(dict(seed=seed,blade=expected_blade,directory=str(folder),files={p.name:sha(p.read_bytes()) for p in folder.iterdir() if p.is_file()}));e.close();e=None;report()
except Exception as exc:
 import traceback;traceback.print_exc();failure=repr(exc)
 if e is not None:
  e.save(OUT/'failure.state');e.screenshot(OUT/'failure.png');(OUT/'failure.ram').write_bytes(e.memory())
finally:
 if e is not None:e.close()
result=report(failure is None and len(rows)==8 and len(cold)==2)
print(json.dumps(dict(passed=result['passed'],checks=sum(checks.values()),cases=len(rows),cold=len(cold),failure=failure,report=str(OUT/'report.json'))))
assert result['passed'],failure
