"""Real party sorting, native deployment and battle construction preserve identity.

Reuse the exact candidate's accepted Herb Picking checkpoint. Distinctive
extra AP/preferences are declared before sorting; all later changes are inputs.
"""
import ast,ctypes,datetime,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
sha=lambda b:hashlib.sha1(b).hexdigest()
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
rom=pathlib.Path(meta['path']).read_bytes();assert sha(rom)==meta['romSha1']
base=pathlib.Path(meta['path']).parent;fix=base/'fixture'
assert (fix/'frozen.gba').read_bytes()==rom
cache=json.loads((fix/'prepare-cache.json').read_text());assert cache['inputs']['romSha1']==meta['romSha1']
assert sha((fix/'report.json').read_bytes())==cache['outputs']['report.json']
OUT=base/('sorted-deployment-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));OUT.mkdir()
ROM=OUT/'fixture.gba';ROM.write_bytes(rom)
Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
RETURN,STACK=0x08000100,0x03006800
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
checks=[];inputs=[];captures=[];e=Emulator(ROM);failure=None
def check(ok,label):assert ok,label;checks.append(label)
def tap(k,wait=180):inputs.append([8,k,wait]);e.run(8,k);e.run(wait)
def word(b,p):return struct.unpack_from('<I',b,p)[0]
def capture(label):
    b=e.memory();e.screenshot(OUT/(label+'.png'));e.save(OUT/(label+'.state'));(OUT/(label+'.ram')).write_bytes(b)
    captures.append(dict(label=label,ramSha1=sha(b),stateSha1=sha((OUT/(label+'.state')).read_bytes())))
def native():
    m=ARM(rom,ctypes.string_at(*e.maps[0x03000000]));m.put(0x02000000,e.memory());return m
try:
    e.load(fix/'accepted-world.state');e.run(1)
    e.set_memory(0x1b40,bytes((i*7+13)%101 for i in range(816)))
    e.set_memory(0x1e80,bytes(i%3 for i in range(24)))
    before=e.memory();capture('before-sort')
    tap(8);tap(256);tap(4);tap(128);tap(4)
    check(e.memory()[0x80:0x1940]==before[0x80:0x1940],'Story characters reject manual relocation')
    tap(128);tap(4);tap(128);tap(4)
    after=e.memory();capture('sorted-party')
    expected=bytearray(before[0x80:0x1940]);expected[528:792],expected[792:1056]=expected[792:1056],expected[528:792]
    check(after[0x80:0x1940]==expected,'Generic identities and full native records swap exactly')
    ap=bytearray(before[0x1b40:0x1e70]);ap[68:102],ap[102:136]=ap[102:136],ap[68:102]
    prefs=bytearray(before[0x1e80:0x1e98]);prefs[2],prefs[3]=prefs[3],prefs[2]
    check(after[0x1b40:0x1e70]==ap,'Extra AP follows identity during sorting')
    check(after[0x1e80:0x1e98]==prefs,'Potion preference follows identity during sorting')
    check(after[0x21c8:0x28cc]==before[0x21c8:0x28cc],'Accepted mission queue stays intact')
    for _ in range(4):tap(1)
    m=native();tile=m.call(0x08036330,8);check(tile==20,'Original Giza placement remains')
    target=(m.call(0x08035a20,tile-1)+6,m.call(0x08035a44,tile-1)+4);route=[]
    for _ in range(600):
        x,y=struct.unpack_from('<HH',e.memory(),0x2c16)
        if abs(x-target[0])<=2 and abs(y-target[1])<=2:break
        key=(128 if x<target[0] else 64) if abs(x-target[0])>2 else (32 if y<target[1] else 16)
        e.run(1,key);route.append([x,y,key])
    else:raise AssertionError('Native world cursor exceeded bound')
    inputs.append(dict(destination=8,route=route));e.run(30);tap(256,1200)
    for i in range(7):tap(256,600)
    capture('deployment-story-members')
    for _ in range(3):tap(256)
    capture('deployment-first-sorted-member')
    for i in range(3):
        for key in (128,256,256,256):tap(key)
        capture('deployment-'+str(i+4)+'-members')
    tap(8,600);tap(256,600);tap(256,600);observe['wait_for_menu'](e);capture('battle-ready')
    b=e.memory();m=native();manager=word(b,0xf4b0)
    count=m.call(0x08099cdc,manager,0x02008000)
    pointers=[m.word(m.word(0x02008000+4*i)) for i in range(count)]
    party=[p for p in pointers if 0x02000080<=p<0x02001940 and (p-0x02000080)%264==0]
    check(count==12 and sorted(party)==[0x02000080+264*i for i in range(6)],'Exactly six original party members deploy once')
    for slot in range(6):
        at=0x80+264*slot;unit=expected[264*slot:264*(slot+1)];race=unit[6]
        check(b[at:at+7]==unit[:7],f'Slot{slot}: native battle retains name, identity, job and race')
        check(b[at+0x2a:at+0x34]==unit[0x2a:0x34],f'Slot{slot}: equipment follows the deployed identity')
        count=142 if race==1 else next(r['totalCount'] for r in json.loads((ROOT/'build/expansion/registry.json').read_text())['races'] if r['id']==race)
        check(b[at+0x40:at+0x40+count]==unit[0x40:0x40+count],f'Slot{slot}: native racial AP preserved')
    check(b[0x1b40:0x1e70]==ap and b[0x1e80:0x1e98]==prefs,'All extra AP and preferences survive deployment')
    check(b[0x1940:0x1b40]==before[0x1940:0x1b40],'Deployment does not transfer equipment inventory')
except Exception as exc:
    failure=repr(exc);capture('failure')
finally:e.close()
report=dict(passed=failure is None,romSha1=meta['romSha1'],acceptedStateSha1=sha((fix/'accepted-world.state').read_bytes()),
            assertions=len(checks),checks=checks,inputs=inputs,captures=captures,failure=failure,scope=__doc__)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=report['passed'],assertions=len(checks),failure=failure,report=str(OUT/'report.json'))))
assert failure is None,failure
