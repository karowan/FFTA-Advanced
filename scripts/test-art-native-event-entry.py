"""Enter original event203 through a disposable world-location substitution.

Preserve event203's scene, formation pair, setup flags and all original scene
bytes. Only event3's record is replaced, retaining its placed location8. This
does not establish event203 campaign eligibility or multiplayer reachability.
Fixed confirmation inputs stop at the first native battle command menu.
"""
import argparse, ast, ctypes as C, datetime, hashlib, json, runpy, struct
from pathlib import Path
from native_art import ROOT, sha
from native_battle_wrappers import from_emulator

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--resume-deployment',action='store_true',help='Use pinned original failed deployment; supply the missing Start and confirm inputs.')
args=parser.parse_args()

meta=json.loads((ROOT/'build/art/connected/a28b624bb13c8f2f2597a4d4bd3999b17c234b99/manifest.json').read_text())
rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
source,target=0x563a70+203*12,0x563a70+3*12
assert rom[source:source+12]==clean[source:source+12]==bytes.fromhex('00a817000000000100000000')
assert rom[target:target+12]==clean[target:target+12]==bytes.fromhex('080e20000000000104000000')
assert rom[0x54cd54+23*40:0x54cd54+24*40]==clean[0x54cd54+23*40:0x54cd54+24*40]
fixture=bytearray(rom);fixture[target+1:target+12]=rom[source+1:source+12]
assert fixture[:target+1]==rom[:target+1] and fixture[target+12:]==rom[target+12:]
fixture=bytes(fixture)
out=ROOT/'build/art/native-event-entry'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
path=out/'event203.gba';path.write_bytes(fixture)
world=Path(meta['fixtureSource']).parent/'fixture';seed=world/'accepted-world.state';seedbytes=seed.read_bytes()
route=json.loads((world/'route.json').read_text());proof=json.loads((world/'report.json').read_text())
assert proof['passed'] and proof['romSha1']==route['romSha1']==hashlib.sha1(Path(meta['fixtureSource']).read_bytes()).hexdigest()
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];menus=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
tree=ast.parse((ROOT/'scripts/probe-ap-copy-heap.py').read_text())
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='heap'],type_ignores=[]),'<native heap walk>','exec'))
checks=[];samples=[];inputs=[];e=None
def check(ok,label):
    assert ok,label
    checks.append(label)
def capture(label):
    e.save(out/(label+'.state'));e.screenshot(out/(label+'.png'))
    for ext,address in [('ram',0x02000000),('iwram',0x03000000),('vram',0x06000000),('palette',0x05000000),('oam',0x07000000)]:
        (out/(label+'.'+ext)).write_bytes(C.string_at(*e.maps[address]))
try:
    e=E(path)
    if args.resume_deployment:
        resume=ROOT/'build/art/native-event-entry/20260919T083826.629102Z'
        pins=json.loads((ROOT/'notes/native-art-sort-capacity-evidence.json').read_text())['sha256']
        for name in ('event203.gba','failed.json','failed.state','failed.ram','failed.iwram'):
            f=resume/name;check(sha(f.read_bytes())==pins[f.relative_to(ROOT).as_posix()],'Pinned deployment input '+name)
        check((resume/'event203.gba').read_bytes()==fixture,'Exact original event fixture retained')
        e.load(resume/'failed.state')
        check(e.memory()==(resume/'failed.ram').read_bytes() and C.string_at(*e.maps[0x03000000])==(resume/'failed.iwram').read_bytes(),'Exact own-ROM retained deployment RAM/IWRAM')
        inputs.append(dict(kind='resume unchanged failed deployment',state=str(resume/'failed.state'),sha256=sha((resume/'failed.state').read_bytes())))
        for key in (8,256):
            e.run(8,key);e.run(600);inputs.append([8,key,600]);capture('resume-'+str(key))
    else:
        e.load(seed)
        for slot,job,race in [(2,117,1),(3,118,2)]:
            p=0x80+264*slot;check(e.memory()[p+6]==race,'Same-race preallocation profile '+str(job))
            e.set_memory(p+4,bytes((1,job,race,job)));e.set_memory(p+0x35,bytes((job,)))
        inputs.append(dict(kind='preallocation profiles',slots=[dict(slot=2,job=117,race=1),dict(slot=3,job=118,race=2)]))
        for x,y,key in route['path']:e.run(1,key)
        e.run(30);e.run(8,256);e.run(1200);capture('entered')
    ready=False
    for step in range(80 if args.resume_deployment else 50):
        if args.resume_deployment:e.run(30);inputs.append([30,0])
        else:e.run(8,256);e.run(120);inputs.append([8,256,120])
        r=e.memory()
        state=heap(r)
        samples.append(dict(step=step,event=r[0x3c2a],formation=struct.unpack_from('<HH',r,0x2170),heap={k:v for k,v in state.items() if k!='allocationBlocks'},menu=menus['menu_visible'](e)))
        if samples[-1]['menu']:
            ready=True;capture('ready');break
        if step%10==0:capture('step-'+str(step))
    check(ready,'Original event scene reaches a native command menu within '+('2400 no-input frames after Start/confirm' if args.resume_deployment else '6400 confirmation frames'))
    wrappers=from_emulator(fixture,e);r=e.memory()
    check(struct.unpack_from('<HH',r,0x2170)==(23,0),'Original event203 primary and secondary selectors')
    check(seed.read_bytes()==seedbytes,'Original world state preserved')
    roster=[dict(unit=u,wrapper=w,identity=list(r[u+4:u+8]),flags=struct.unpack_from('<H',r,u+40)[0]) for u,w in wrappers.items()]
    report=dict(status='passed',checks=checks,candidateSha1=meta['romSha1'],romSha1=hashlib.sha1(fixture).hexdigest(),scope=__doc__,roster=roster,actorCount=len(roster),samples=samples,inputs=inputs,source=dict(state=str(seed),stateSha256=sha(seedbytes),routeSha256=sha((world/'route.json').read_bytes())))
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),actorCount=len(roster),report=str(out/'report.json'))))
except Exception as error:
    if e and e.frame:capture('failed')
    (out/'failed.json').write_text(json.dumps(dict(status='failed',candidateSha1=meta['romSha1'],romSha1=hashlib.sha1(fixture).hexdigest(),scope=__doc__,checks=checks,error=str(error),samples=samples,inputs=inputs),indent=2)+'\n',encoding='utf-8');print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
