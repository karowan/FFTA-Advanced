"""Continue authenticated native transformations through movement/monster abilities/unmorph.

One fixed formation/seed per family. No post-input outcome or sprite injection.
Passed phases are retained so a late failure does not replay the native prefix.
"""
import pathlib,datetime
LIFECYCLE_SCOPE=__doc__;ROOT=pathlib.Path(__file__).resolve().parents[1]
helper=ROOT/'scripts/test-morpher-player.py'
head=helper.read_text().split("latest=LAB/'morpher-player-latest.json'")[0]
head=head.replace("'morpher-player-'+stamp","'morpher-lifecycle-'+stamp")
exec(compile(head,str(helper),'exec'));SCOPE=LIFECYCLE_SCOPE;__doc__=SCOPE
pointer=json.loads((LAB/'morpher-player-latest.json').read_text());producer=pathlib.Path(pointer['report'])
assert sha(producer.read_bytes())==pointer['sha1'];accepted=json.loads(producer.read_bytes())
assert accepted['passed'] and accepted['romSha1']==meta['romSha1'] and accepted['instrumentedSha1']==sha(instrumented)
for row in accepted['cases']:
 for file,digest in row['files'].items():assert sha((pathlib.Path(row['directory'])/file).read_bytes())==digest
latest=LAB/'morpher-lifecycle-latest.json';rows=[];retained=[];failure=None;e=None

def report(passed=False):
 data=dict(passed=passed,romSha1=meta['romSha1'],instrumentedSha1=sha(instrumented),producer=pointer,scope=SCOPE,
           checks=dict(checks),cases=rows,retained=retained,failure=failure)
 path=OUT/'report.json';path.write_text(json.dumps(data,indent=2)+'\n')
 latest.write_text(json.dumps(dict(report=str(path),sha1=sha(path.read_bytes()),passed=passed))+'\n');return data

def save_phase(label,details=None):
 r=capture(e,label,folder)
 check('native-renderer-intact',C.string_at(*e.maps[0x03000000])[CODE_FIRST:CODE_LAST]==NATIVE_CODE)
 paths=[folder/(label+ext) for ext in ('.state','.ram','.png')]
 rows.append(dict(family=family,name=name,phase=label,directory=str(folder),details=details,
                  files={p.name:sha(p.read_bytes()) for p in paths}));report();return r

def own_turn():
 for turn in range(24):
  menu(e)
  if active(e)==0x02000000+ACTOR:return
  previous=active(e)
  for key in (32,32,256,256):tap(e,key)
  menu(e,previous)
 raise AssertionError('Morpher did not receive native next turn')

def action_finish(action):
 check('recorded-native-action',word(e.memory(),LOG)==0x504c4159 and word(e.memory(),LOG+8)==action)
 # With movement already spent, native facing mode is the action endpoint.
 for frame in range(2401):
  r=e.memory()
  if frame>120 and half(r,ACTOR+0x18)==0 and active(e)!=0x02000000+ACTOR and observe['menu_visible'](e):
   check('native-Selfdestruct-KO-clears-morph',family==2 and action==271 and not r[ACTOR+0xea]&4);return
  if frame>120 and half(r,0xf4e8+0xdc)==47:break
  if frame<2400:e.run(1)
 else:raise AssertionError('Native action did not reach facing')
 tap(e,256,900);menu(e)

if '--resume' in sys.argv:
 priorpointer=json.loads(latest.read_text());priorpath=pathlib.Path(priorpointer['report']);assert sha(priorpath.read_bytes())==priorpointer['sha1']
 prior=json.loads(priorpath.read_bytes());assert prior['producer']==pointer and prior['instrumentedSha1']==sha(instrumented)
 for row in prior['cases']:
  for file,digest in row['files'].items():assert sha((pathlib.Path(row['directory'])/file).read_bytes())==digest
 rows.extend(prior['cases']);checks.update(prior['checks']);retained.append(priorpointer)
try:
 for source in accepted['cases']:
  family,name=source['family'],source['name'];case=(family,name);folder=OUT/f'{family}-{name}';folder.mkdir()
  completed=[r for r in rows if r['family']==family]
  if any(r['phase'] in ('unmorphed','defeated') for r in completed):continue
  last=completed[-1] if completed else None
  state=pathlib.Path(last['directory'])/(last['phase']+'.state') if last else pathlib.Path(source['directory'])/'morphed.state'
  e=E(TEST_ROM);e.load(state);e.run(1);phases={r['phase'] for r in completed}
  if 'moved' not in phases:
   before=e.memory();check('starts-native-morphed',bool(before[ACTOR+0xea]&4))
   for key in (256,128,256):tap(e,key)
   for _ in range(240):
    if half(e.memory(),0xf4e8+0xdc)==47:break
    e.run(10)
   check('movement-reaches-native-facing',half(e.memory(),0xf4e8+0xdc)==47)
   r=e.memory();w=from_emulator(image,e)[ACTOR]
   check('native-moving-wrapper-position',half(r,w+8)//32==2 and half(r,w+12)//32==15)
   check('movement-keeps-family',r[ACTOR+0xea]&4 and r[ACTOR+0xe6]==family)
   previous=active(e);tap(e,256,900);menu(e,previous)
   check('native-movement-committed',e.memory()[ACTOR+0xf6:ACTOR+0xf8]==bytes((2,15)))
   save_phase('moved')
  if 'attacked' not in phases:
   own_turn()
   if 'attack-ready' not in phases:save_phase('attack-ready')
   check('next-turn-retains-morph',bool(e.memory()[ACTOR+0xea]&4))
   # Move back to1,15, then target adjacent Jona with the monster ability.
   for i,key in enumerate((256,64,256)):
    tap(e,key);capture(e,'fight-move-'+str(i),folder)
   menu(e)
   e.set_memory(LOG,bytes(148));e.set_memory(LOG+148,struct.pack('<II',1,6))
   # Native morphed command replaces Fight/secondary. Select its first ability.
   for i,key in enumerate((256,256,256)):
    tap(e,key);capture(e,'monster-command-'+str(i),folder)
   r=e.memory();manager=word(r,0xf438)-0x02000000;action=word(r,manager+20)
   check('original-monster-action-selected',0<action<360 and action not in range(202,211))
   tap(e,16)
   for _ in range(5):
    tap(e,256)
    if word(e.memory(),LOG)==0x504c4159:break
   action_finish(action)
   save_phase('attacked',dict(action=action,targetHP=half(e.memory(),0x398+0x18)))
  if half(e.memory(),ACTOR+0x18)==0:
   check('native-death-ending',family==2 and not e.memory()[ACTOR+0xea]&4)
   save_phase('defeated');e.close();e=None;print(name,'native selfdestruct/KO passed',flush=True);continue
  if 'unmorphed' not in phases:
   own_turn()
   for key in (16,256):tap(e,key)
   menu(e);r=e.memory();check('native-Unmorph-clears-form',not r[ACTOR+0xea]&4)
   check('original-Morpher-identity',r[ACTOR+5:ACTOR+8]==bytes((26,3,26)))
   save_phase('unmorphed')
  e.close();e=None;print(name,'movement/monster abilities/unmorph passed',flush=True)
except Exception as exc:
 import traceback;traceback.print_exc();failure=repr(exc)
 if e is not None:
  e.save(OUT/'failure.state');e.screenshot(OUT/'failure.png');(OUT/'failure.ram').write_bytes(e.memory())
finally:
 if e is not None:e.close()
result=report(failure is None and sum(r['phase'] in ('unmorphed','defeated') for r in rows)==9)
print(json.dumps(dict(passed=result['passed'],phases=len(rows),checks=sum(checks.values()),failure=failure,report=str(OUT/'report.json'))))
assert result['passed'],failure
