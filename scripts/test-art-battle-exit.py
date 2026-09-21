"""Finish the retained all-ten demanding battle through native results/world UI.

Reuse the exact post-cast/post-Status own-ROM state. Zero only enumerated hostile
HP as a declared result-boundary input, then use native Wait/dialog inputs. No
victory, receipt, scene, roster or saved result is injected. This tests teardown
and campaign consumers, not naturally winning formation324 or a full playthrough.
"""
import argparse, ast, ctypes as C, datetime, hashlib, json, runpy, struct, sys
from pathlib import Path
from native_art import ROOT, sha
from native_battle_wrappers import from_emulator

index_path=ROOT/'notes/native-art-capacity-followup-evidence.json'
index=json.loads(index_path.read_text());pins={r['path']:r['sha256'] for r in index['files']}
base=ROOT/'build/art/capacity-action/20260919T092806.315981Z'
def pinned(path):
    data=path.read_bytes();assert sha(data)==pins[path.relative_to(ROOT).as_posix()];return data
previous=json.loads(pinned(base/'report.json'));assert previous['status']=='passed'
state=pinned(base/'returned-1.state');ram=pinned(base/'returned-1.ram');iw=pinned(base/'returned-1.iwram')
inputs_index=json.loads((ROOT/'notes/native-art-capacity-action-inputs.json').read_text())
rompath=ROOT/inputs_index['files']['fixture.gba']['path'];rom=rompath.read_bytes()
assert sha(rom)==inputs_index['files']['fixture.gba']['sha256'] and hashlib.sha1(rom).hexdigest()==previous['romSha1']
meta=json.loads((ROOT/'build/art/connected'/previous['candidateSha1']/'manifest.json').read_text())
out=ROOT/'build/art/battle-exit'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--resume-result',action='store_true');args=parser.parse_args()
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
RETURN,STACK=0x08000100,0x03006800
source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000').replace('self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)','self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(source);exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native world functions>','exec'))
menus=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
for filename,name in [('probe-ap-copy-heap.py','heap'),('test-art-capacity-action.py','select_menu'),('test-independent-save-slots.py','owned')]:
    tree=ast.parse((ROOT/'scripts'/filename).read_text())
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name],type_ignores=[]),filename,'exec'))
word=lambda b,p:struct.unpack_from('<I',b,p)[0]
half=lambda b,p:struct.unpack_from('<H',b,p)[0]
flag=lambda b,i:bool(b[0x1f70+i//8]&(1<<(i%8)))
checks=[];inputs=[];captures={};observations=[];tick=0;phase='setup';e=None

def check(ok,label):
    assert ok,phase+'/'+label
    checks.append(phase+'/'+label)

def run(frames,key=0):
    global tick
    e.run(frames,key);tick+=frames

def tap(key,wait=180):
    inputs.append(dict(phase=phase,frame=tick,key=key,press=8,wait=wait));run(8,key);run(wait)

def capture(label):
    e.save(out/(label+'.state'));e.screenshot(out/(label+'.png'))
    for ext,address in [('ram',0x02000000),('iwram',0x03000000),('vram',0x06000000),('palette',0x05000000),('oam',0x07000000)]:
        (out/(label+'.'+ext)).write_bytes(C.string_at(*e.maps[address]))
    r=e.memory();captures[label]=dict(frame=tick,story=r[0x2190],scene=half(r,0x2192),receipt=flag(r,770),flashSha256=sha(e.memory(0)))

def native():
    m=ARM(rom,C.string_at(*e.maps[0x03000000]));m.put(0x02000000,e.memory());return m

def place_lutia():
    global phase
    phase='placement';m=native()
    tiles=[t for t in range(1,31) if not m.call(0x08036350,t)];check(bool(tiles),'Native map has empty placement slot')
    giza=m.call(0x08036330,8);gx=m.call(0x08035a20,giza-1)+6;gy=m.call(0x08035a44,giza-1)+4
    points=[(t,m.call(0x08035a20,t-1)+6,m.call(0x08035a44,t-1)+4) for t in tiles]
    tile,x,y=min(points,key=lambda p:(p[1]-gx)**2+(p[2]-gy)**2)
    tap(256,180);route=[]
    for _ in range(600):
        cx,cy=struct.unpack_from('<HH',e.memory(),0x2c16)
        if abs(cx-x)<=2 and abs(cy-y)<=2:break
        key=(128 if cx<x else 64) if abs(cx-x)>2 else (32 if cy<y else 16)
        route.append([cx,cy,key]);run(1,key)
    else:raise AssertionError('Native placement cursor route exceeded bound')
    inputs.append(dict(emptyTile=tile,cursorRoute=route));run(30);tap(256,300);tap(256,600);capture('placed-lutia')
    m=native();location=m.call(0x08036350,tile)
    check(location!=0 and m.call(0x08036330,location)==tile,'Original result and map inputs place awarded territory')
    check(sum(m.call(0x08036350,t)==0 for t in range(1,31))==len(tiles)-1,'Exactly one formerly empty map slot filled')
    captures['placed-lutia']['placedLocation']=location;captures['placed-lutia']['placedTile']=tile

try:
    e=E(rompath);e.load(base/'returned-1.state')
    check(e.memory()==ram and C.string_at(*e.maps[0x03000000])==iw,'Exact retained own-ROM state')
    retained_result=None
    if args.resume_result:
        resume_path=ROOT/'notes/native-art-battle-exit-inputs.json';resume=json.loads(resume_path.read_text())['files']
        data={k:(ROOT/v['path']).read_bytes() for k,v in resume.items()}
        check(all(sha(data[k])==v['sha256'] for k,v in resume.items()),'Authenticated result resume evidence')
        failed=json.loads(data['failed.json'])
        check(failed['error']=='world-party/Actual world heap owns complete context' and failed['romSha1']==previous['romSha1'],'Exact retained missing-placement failure')
        e.load(ROOT/resume['earned-world.state']['path'])
        check(e.memory()==data['earned-world.ram'] and C.string_at(*e.maps[0x03000000])==data['earned-world.iwram'],'Exact own-ROM earned result state')
        retained_result=dict(indexSha256=sha(resume_path.read_bytes()),checks=failed['checks'],observations=failed['observations'],scope='Original result assertions reused; the premature party-menu assertion remains failed.')
        root=meta['components']['livePalette']['partyHeapRoot']-0x02000000
        run(1)
    else:
        run(1);before=e.memory();wrappers=from_emulator(rom,e)
        check(len(wrappers)==13 and before[0x2190]==3 and not flag(before,770),'Original Giza stage with13 actors before result')
        enemies=[u for u in wrappers if 0x2fc4<=u<0x3c24 and (u-0x2fc4)%264==0 and before[u+0x29]&128]
        check(len(enemies)==6,'Exactly six native hostile units')
        for unit in enemies:e.set_memory(unit+0x18,bytes(2))
        after=e.memory();allowed={u+offset for u in enemies for offset in (0x18,0x19)}
        check(all(a==b or i in allowed for i,(a,b) in enumerate(zip(before,after))),'Only declared hostile HP changed')
        inputs.append(dict(hostileHPZeroed=enemies));capture('result-input');phase='result'
        select_menu(2);tap(256);tap(256,900)
        for step in range(180):
            r=e.memory();observations.append(dict(frame=tick,story=r[0x2190],scene=half(r,0x2192),receipt=flag(r,770),heapPointer=word(r,0xf434)))
            if r[0x2190]==4 and flag(r,770):break
            tap(256,180)
        else:raise AssertionError('Native Giza result did not earn story4/receipt770 within bound')
        run(600);capture('earned-world');r=e.memory()
        check(r[0x2190]==4 and flag(r,770),'Native result earns next story stage and mission receipt')
        check(all(r[0x80+264*s+7]==before[0x80+264*s+7] for s in range(24)),'All24 party job identities retained through battle exit')
        root=meta['components']['livePalette']['partyHeapRoot']-0x02000000
        check(word(r,root)==0 and word(r,0x3ff40)==0 and word(r,0x3ff48)==0,'Borrowed party/copy/action owners retired')
    place_lutia()
    # Dismiss any final result prompt before opening the actual full world UI.
    for _ in range(3):tap(1,120)
    phase='world-party';tap(8);tap(256,600);capture('world-party')
    r=e.memory();ctx=word(C.string_at(*e.maps[0x03000000]),0x2818)
    check(0x02000000<=ctx<ctx+0x9980<=0x0203c000,'Full world context fits after demanding battle')
    owner=word(r,ctx-0x02000000);clone=bytearray(r);struct.pack_into('<I',clone,0xf434,owner);h=heap(clone)
    check(h.get('end',0)<=0x0203c000 and any(b['marker']=='la' and b['address']+12==ctx and b['payloadBytes']>=0x9980 for b in h.get('allocationBlocks',[])),'Actual world heap owns complete context')
    check(word(r,ctx-0x02000000+0x2d50)==ctx+0x7280,'Full world item list restored')
    captures['world-party']['ownedHeap']=h
    tap(1,300);tap(1,300);capture('returned-world')
    check(e.memory()[0x2190]==4 and flag(e.memory(),770) and word(e.memory(),root)==0,'World menu closes with earned progression and no borrowed owner')
    phase='native-save';saved_profile=owned(e.memory());old_flash=e.memory(0)
    for key,wait in ((8,180),(16,180),(256,180),(256,180),(256,180),(64,60),(256,300)):tap(key,wait)
    capture('native-save');flash=e.memory(0)
    check(flash!=old_flash,'Original normal save controller writes private flash')
    (out/'normal.sav').write_bytes(flash)
    e.close();e=E(Path(meta['path']));e.set_memory(0,flash,0);run(3600);phase='cold-current'
    for key,wait in ((8,180),(256,60),(256,60),(256,180)):tap(key,wait)
    capture('cold-current')
    check(owned(e.memory())==saved_profile,'Current unmodified candidate restores complete saved roster/AP/inventory/preferences/history/gil')
    check(e.memory()[0x2190]==4 and flag(e.memory(),770),'Current cold load restores earned original campaign progression')
    check(word(e.memory(),root)==0 and e.memory()[0x3f410:0x3f728]==bytes(792),'Cold load retires temporary battle state')
    check(e.memory(0)==flash,'Current Continue preserves newly written flash')
    for filename in ('report.json','returned-1.state','returned-1.ram','returned-1.iwram'):pinned(base/filename)
    report=dict(status='passed',scope=__doc__,romSha1=previous['romSha1'],coldRomSha1=meta['romSha1'],candidateSha1=previous['candidateSha1'],inputIndexSha256=sha(index_path.read_bytes()),retainedResult=retained_result,checks=checks,inputs=inputs,captures=captures,observations=observations,savedProfile=saved_profile)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    if e and e.frame:capture('failed')
    (out/'failed.json').write_text(json.dumps(dict(status='failed',scope=__doc__,romSha1=previous['romSha1'],candidateSha1=previous['candidateSha1'],checks=checks,inputs=inputs,captures=captures,observations=observations,error=str(error)),indent=2)+'\n',encoding='utf-8');print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
