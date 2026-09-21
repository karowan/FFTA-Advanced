"""Nine real Soul transformations and native appearance/gameplay separation.

Uses one preconstructed Morpher fixture and fixed menu inputs. The recorder
supplies only a native RNG seed and records completed executions. It never
writes a morph flag, family, hit, result or sprite. Further playback phases
have separate acceptance; this script first establishes all nine real casts.
"""
import datetime,pathlib
SCOPE=__doc__
ROOT=pathlib.Path(__file__).resolve().parents[1]
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
helper=ROOT/'scripts/test-integrated-reaction-playback.py'
support=helper.read_text(encoding='utf-8').split('cases=[')[0]
support=support.replace("FIX=LAB/'fixture'","FIX=LAB/'fixture-morpher'")
support=support.replace("OUT=LAB/'reaction-playback'","OUT=LAB/"+repr('morpher-player-'+stamp))
exec(compile(support,str(helper),'exec'));__doc__=SCOPE
# Morphed units add Unmorph: the same native Wait/Status text is 8px left and 16px higher.
# Keep both exact text/outline anchors, without relaxing pixel thresholds.
import types,copy
normal_visible=observe['menu_visible'];anchor=copy.deepcopy(observe['ANCHOR'])
for key in ('points','darkPoints'):anchor[key]=[[x-8,y-16] for x,y in anchor[key]]
morph_visible=types.FunctionType(normal_visible.__code__,dict(normal_visible.__globals__,ANCHOR=anchor))
observe['menu_visible']=lambda e:normal_visible(e) or morph_visible(e)
proof=json.loads((FIX/'prepare-cache.json').read_text())
assert proof['inputs']['romSha1']==meta['romSha1']
for n,digest in proof['outputs'].items():assert hashlib.sha1((FIX/n).read_bytes()).hexdigest()==digest,n
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
RETURN,STACK=0x08000100,0x03006800
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
ACTOR=0x4a0;clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
jobs=[0x2c,0x2e,0x31,0x33,0x36,0x38,0x3e,0x40,0x42]
names=['Goblin','Flan','Bomb','Dragon','Lamia','Bug','Panther','Malboro','Floateye']
sha=lambda b:hashlib.sha1(b).hexdigest()
latest=LAB/'morpher-player-latest.json';rows=[];retained=[];failure=None;e=None
def checkpoint(passed=False):
    report=dict(passed=passed,romSha1=meta['romSha1'],instrumentedSha1=sha(instrumented),fixture=proof,
                checks=dict(checks),total=sum(checks.values()),cases=rows,retained=retained,failure=failure,scope=SCOPE)
    path=OUT/'report.json';path.write_text(json.dumps(report,indent=2)+'\n')
    latest.write_text(json.dumps(dict(report=str(path),sha1=sha(path.read_bytes()),passed=passed))+'\n');return report
if '--resume' in sys.argv:
    pointer=json.loads(latest.read_text());priorpath=pathlib.Path(pointer['report']);priorbytes=priorpath.read_bytes();assert sha(priorbytes)==pointer['sha1']
    prior=json.loads(priorbytes);assert prior['romSha1']==meta['romSha1'] and prior['instrumentedSha1']==sha(instrumented) and prior['fixture']==proof
    for row in prior['cases']:
        for file,digest in row['files'].items():assert sha((pathlib.Path(row['directory'])/file).read_bytes())==digest
    rows.extend(prior['cases']);checks.update(prior['checks']);retained.append(dict(report=str(priorpath),sha1=sha(priorbytes)))
try:
    e=E(TEST_ROM);e.load(FIX/'battle-ready.state');e.run(1);fixed_giza_formation(image,e)
    e.set_memory(0x3ff44,bytes(8)+b'\xd7'*0xb4);e.set_memory(LOG,bytes(160))
    for u in (0x80,0x188,0x290,0x398,0x5a8):e.set_memory(u+0x18,struct.pack('<HH',999,999))
    menu(e)
    for turn in range(24):
        if active(e)==0x02000000+ACTOR:break
        previous=active(e)
        for key in (32,32,256,256):tap(e,key)
        menu(e,previous)
    check('native-Morpher-turn-ready',active(e)==0x02000000+ACTOR)
    capture(e,'turn-ready',OUT);e.close();e=None
    for family,(job,name) in enumerate(zip(jobs,names)):
        if any(r['family']==family for r in rows):continue
        case=(family,name);folder=OUT/f'{family}-{name}';folder.mkdir();e=E(TEST_ROM)
        e.load(OUT/'turn-ready.state');e.run(1)
        # Legal Soul choice is a scenario input on an already-native Morpher.
        # Use the complete equipment setter on a clone, then publish setup.
        m=ARM(image,C.string_at(*e.maps[0x03000000]));m.put(0x02000000,e.memory())
        m.call(0x080caf78,0x02000000+ACTOR,229+family,0)
        e.set_memory(ACTOR,m.read(0x02000000+ACTOR,264));e.set_memory(0x1940,m.read(0x02001940,512))
        e.set_memory(LOG,bytes(160));e.set_memory(LOG+148,struct.pack('<II',1,6))
        before=capture(e,'before',folder)
        check('starts-unmorphed',not before[ACTOR+0xea]&4)
        for key in (32,256,32,256):tap(e,key)
        capture(e,'morph-list',folder)
        for _ in range(family):tap(e,32,60)
        capture(e,'family-selected',folder)
        for step in range(10):
            tap(e,256,180);capture(e,'confirm-'+str(step),folder)
            if word(e.memory(),LOG)==0x504c4159:break
        check('native-Morph-action-executed',word(e.memory(),LOG)==0x504c4159 and word(e.memory(),LOG+8)==202+family)
        menu(e);after=capture(e,'morphed',folder)
        check('actual-morph-status',bool(after[ACTOR+0xea]&4))
        check('actual-morph-family',after[ACTOR+0xe6]==family)
        check('identity-job-race-retained',after[ACTOR:ACTOR+8]==before[ACTOR:ACTOR+8])
        check('Soul-and-mastered-AP-retained',after[ACTOR+0x2a:ACTOR+0x34]==before[ACTOR+0x2a:ACTOR+0x34] and after[ACTOR+0x40:ACTOR+0xc0]==before[ACTOR+0x40:ACTOR+0xc0])
        check('captured-bank-and-inventory-retained',after[0x2e78:0x2fb8]==before[0x2e78:0x2fb8] and after[0x1940:0x1e70]==before[0x1940:0x1e70])
        check('native-renderer-intact',C.string_at(*e.maps[0x03000000])[CODE_FIRST:CODE_LAST]==NATIVE_CODE)
        iw=C.string_at(*e.maps[0x03000000]);original=ARM(clean,iw);expanded=ARM(image,iw)
        for machine in (original,expanded):machine.put(0x02000000,after)
        for selector in range(48):
            baseline=original.call(0x080c92f0,0x02000000+ACTOR,selector)
            actual=expanded.call(0x080c92f0,0x02000000+ACTOR,selector)
            expected=baseline
            if selector in (4,5,0x22,0x23):
                expected=original.call(0x080c8570,job,job,selector)
                if selector==5 and expected==0xffff:expected=original.call(0x080c8570,job,job,4)
            check('native-appearance-only-selector-'+str(selector),actual==expected)
        check('native-observation-does-not-mutate-unit',expanded.read(0x02000000+ACTOR,264)==after[ACTOR:ACTOR+264])
        rows.append(dict(family=family,name=name,monsterJob=job,action=202+family,directory=str(folder),
                         files={p.name:sha(p.read_bytes()) for p in folder.iterdir() if p.is_file()}))
        e.close();e=None;checkpoint(False);print(name,'native transformation passed',flush=True)
except Exception as exc:
    import traceback;traceback.print_exc()
    failure=repr(exc)
    if e is not None:
        e.save(OUT/'failure.state');e.screenshot(OUT/'failure.png');(OUT/'failure.ram').write_bytes(e.memory())
finally:
    if e is not None:e.close()
report=checkpoint(failure is None and len(rows)==9)
print(json.dumps(dict(passed=report['passed'],checks=report['total'],completed=[r['name'] for r in rows],failure=failure,report=str(OUT/'report.json'))))
assert report['passed'],failure
