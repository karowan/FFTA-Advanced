"""Actual full-clan recruitment refusal, vacancy acceptance and cold save.

Declared results fixture: native Herb Picking ending with enemy HP initially
zero, then native-generated Mythril Rush reward record and a full24-unit clan.
Native RNG produces Quin; player buttons drive the offer and acceptance.
The second declared scenario has one empty slot; no dismissal is claimed.
This does not claim campaign acquisition or a Mythril Rush battle victory.
"""
import ast,ctypes,datetime,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes();sha=lambda x:hashlib.sha1(x).hexdigest()
assert sha(rom)==meta['romSha1']
FIX=ROM.parent/'fixture';proof=json.loads((FIX/'prepare-cache.json').read_text())
assert (FIX/'frozen.gba').read_bytes()==rom
for name,digest in proof['outputs'].items():assert sha((FIX/name).read_bytes())==digest
fm=json.loads((FIX/'report.json').read_text())
OUT=ROM.parent/('full-clan-recruitment-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));OUT.mkdir()
latest=ROM.parent/'full-clan-recruitment-latest.json'
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
checks=[];inputs=[];captures=[];completed=[];values={};retained={};e=None;failure=None

def check(ok,label):
    assert ok,label
    checks.append(label)

def tap(key,wait=300):
    inputs.append([8,key,wait]);e.run(8,key);e.run(wait)

def capture(label):
    e.save(OUT/(label+'.state'));r=e.memory();(OUT/(label+'.ram')).write_bytes(r)
    s=e.memory(0);(OUT/(label+'.sav')).write_bytes(s)
    if e.frame is not None:e.screenshot(OUT/(label+'.png'))
    captures.append(dict(label=label,directory=str(OUT),stateSha1=sha((OUT/(label+'.state')).read_bytes()),ramSha1=sha(r),saveSha1=sha(s)))

def report(passed=False):
    result=dict(passed=passed,romSha1=meta['romSha1'],checks=checks,assertions=len(checks),inputs=inputs,
                captures=captures,completed=completed,values=values,retained=retained,failure=failure,scope=__doc__)
    (OUT/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    latest.write_text(json.dumps(dict(report=str(OUT/'report.json'))),encoding='utf-8')
    return result

def quin(r):
    return [i for i in range(24) if r[0x84+i*264] and r[0x80+i*264:0x84+i*264]==bytes.fromhex('5f165508')]

def prepare():
    e.load(FIX/'battle-ready.state')
    check(e.memory()[0x1e79]==2,'Tracked history starts before the offer')
    for p in fm['otherUnitPointers']:e.set_memory(p-0x02000000+0x18,bytes(2))
    for key in (32,32,256,256):tap(key,180)
    e.run(6000)
    for _ in range(13):tap(256)
    capture('native-ending')
    m=ARM(rom,ctypes.string_at(*e.maps[0x03000000]));m.put(0x02000000,e.memory())
    for reg,val in ((UC_ARM_REG_R5,0x0855ae4c+70*111),(UC_ARM_REG_R8,111<<16),(UC_ARM_REG_R10,3),(UC_ARM_REG_SP,STACK)):
        m.u.reg_write(reg,val)
    m.u.hook_add(UC_HOOK_CODE,lambda u,a,s,d:u.emu_stop() if a==0x080d0162 else None)
    m.u.emu_start(0x080cff41,0,count=100000)
    check(m.u.reg_read(UC_ARM_REG_PC)==0x080d0162,'Native accepted reward record generated')
    record=bytearray(m.read(0x03002850,16));record[2]&=~0x1c;record[4:6]=bytes(2)
    check(struct.unpack_from('<HH',record,8)==(400,0),'Original Mythril Rush Silvril reward retained')
    e.set_memory(0x21c8,bytes(record));e.set_memory(0x2c30,struct.pack('<H',111));e.set_memory(0x2b08,bytes(256))
    e.set_memory(0x1fd8,bytes((e.memory()[0x1fd8]|2,)))
    r=e.memory()
    for slot in range(6,24):e.set_memory(0x80+264*slot,r[0x290:0x398])
    e.set_memory(0x1b40,bytes((i*11+7)%101 for i in range(816)))
    e.set_memory(0x1e80,bytes(i%3 for i in range(24)))
    tap(256);tap(256)
    check(sum(bool(e.memory()[0x84+i*264]) for i in range(24))==24,'Declared full clan before offer')
    values['beforeRoster']=e.memory()[0x80:0x1940].hex()
    values['beforeAP']=e.memory()[0x1b40:0x1e70].hex();values['beforePrefs']=e.memory()[0x1e80:0x1e98].hex()

def full_capacity():
    m=ARM(rom,ctypes.string_at(*e.maps[0x03000000]));m.put(0x02000000,e.memory())
    check(m.call(0x0803600c)==0,'Native vacancy scan reports full clan')
    m.put(0x030034b0,bytes(4))
    check(m.call(0x080d241c,111,0x02002fc4)==1,'Candidate eligibility independently succeeds for full clan')
    before=e.memory()
    pointer,_=e.maps[0x03000000];ctypes.memmove(pointer+0x34b0,bytes(4),4)
    tap(256);capture('full-capacity-result')
    check(not quin(e.memory()) and e.memory()[0x1e79]==2,'Native full-clan result grants no unit or accepted receipt')
    after=e.memory()
    # Closing the result awards native equipment AP. Isolate ownership from
    # that separately tested reward; compare every non-AP byte of every unit.
    for slot in range(24):
        p=0x80+slot*264
        check(after[p:p+0x40]+after[p+0xd0:p+264]==before[p:p+0x40]+before[p+0xd0:p+264],
              'Full capacity preserves non-AP unit bytes '+str(slot))
    values['afterFullRoster']=after[0x80:0x1940].hex()
    for label,lo,hi in [('extra AP',0x1b40,0x1e70),('preferences',0x1e80,0x1e98)]:
        check(e.memory()[lo:hi]==before[lo:hi],'Full capacity preserves '+label)
    check(any(e.memory()[0x2b08+i*4]==25 for i in range(64)),'Full clan retains original quest reward')

def vacancy():
    # Compare the exact same result with one declared empty slot. This is a
    # fixture boundary, not a claim that a player dismissal was performed.
    anchor=next(c for c in captures if c['label']=='prepared');directory=pathlib.Path(anchor['directory'])
    check(sha((directory/'prepared.state').read_bytes())==anchor['stateSha1'],'Original prepared checkpoint authenticated')
    e.load(directory/'prepared.state');e.run(1)
    e.set_memory(0x290,bytes(264));e.set_memory(0x1b84,bytes(34));e.set_memory(0x1e82,bytes(1))
    values['beforeRoster']=e.memory()[0x80:0x1940].hex()
    values['beforeAP']=e.memory()[0x1b40:0x1e70].hex();values['beforePrefs']=e.memory()[0x1e80:0x1e98].hex()
    m=ARM(rom,ctypes.string_at(*e.maps[0x03000000]));m.put(0x02000000,e.memory())
    check(m.call(0x0803600c)==0x02000290,'Native vacancy scan finds exact empty slot2')

def offer():
    pointer,_=e.maps[0x03000000];ctypes.memmove(pointer+0x34b0,struct.pack('<I',2),4)
    tap(256);capture('native-offer')
    check(e.memory()[0x2fc4:0x2fc8]==bytes.fromhex('5f165508'),'Native RNG generated Quin')
    check(not quin(e.memory()) and e.memory()[0x1e79]==2,'Offer alone changes no ownership/history')
    tap(256);tap(256)
    capture('vacant-clan-confirmed')

def accept():
    for _ in range(4):tap(256)
    capture('accepted-inputs')
    check(quin(e.memory())==[2],'Actual acceptance UI assigns Quin to vacant slot2')
    check(e.memory()[0x1e79]==3,'Actual UI acceptance commits history')
    after=e.memory();before=bytes.fromhex(values['afterFullRoster'])
    for slot in range(24):
        if slot==2:continue
        check(after[0x80+264*slot:0x188+264*slot]==before[264*slot:264*(slot+1)],'Other native roster record preserved '+str(slot))
    ap=bytearray.fromhex(values['beforeAP']);ap[68:102]=bytes(34)
    prefs=bytearray.fromhex(values['beforePrefs']);prefs[2]=0
    check(after[0x1b40:0x1e70]==ap,'Acceptance preserves all other extra AP')
    check(after[0x1e80:0x1e98]==prefs,'Acceptance preserves all other potion preferences')
    for _ in range(4):tap(256)
    check(any(e.memory()[0x2b08+i*4]==25 for i in range(64)),'Original Silvril reward survives full-clan offer')

def cold():
    global e
    before=e.memory()
    for key,wait in ((8,60),(16,60),(256,60),(256,60),(256,60),(64,20),(256,300)):tap(key,wait)
    sram=e.memory(0);values['finalSramSha1']=sha(sram);(OUT/'accepted.sav').write_bytes(sram)
    e.close();e=E(ROM);e.set_memory(0,sram,0);e.run(3600)
    for key in (8,256,256,256):tap(key)
    check(quin(e.memory())==[2] and e.memory()[0x1e79]==3,'Fresh cold load restores accepted Quin and receipt')
    for name,lo,hi in (('all24 unit records',0x80,0x1940),('extra AP',0x1b40,0x1e70),('preferences',0x1e80,0x1e98)):
        check(e.memory()[lo:hi]==before[lo:hi],'Cold load preserves '+name)

try:
    e=E(ROM)
    if '--resume' in sys.argv:
        path=pathlib.Path(json.loads(latest.read_text())['report']);prior=json.loads(path.read_text())
        assert prior['romSha1']==meta['romSha1'];checks.extend(prior['checks']);completed.extend(prior['completed']);values.update(prior['values'])
        retained.update(report=str(path),sha1=sha(path.read_bytes()),completed=list(completed))
        anchor=next(c for c in reversed(prior['captures']) if c['label']==completed[-1])
        # Keep every completed checkpoint's provenance. The vacancy comparison
        # may need the earlier prepared state after a later-stage failure.
        captures.extend(c for c in prior['captures'] if c['label'] in completed)
        directory=pathlib.Path(anchor['directory'])
        for ext,key in (('state','stateSha1'),('ram','ramSha1'),('sav','saveSha1')):
            assert sha((directory/(anchor['label']+'.'+ext)).read_bytes())==anchor[key]
        e.set_memory(0,(directory/(anchor['label']+'.sav')).read_bytes(),0)
        e.load(directory/(anchor['label']+'.state'));e.run(1)
    for label,fn in [('prepared',prepare),('full-capacity',full_capacity),('vacancy',vacancy),('offered',offer),('accepted',accept),('cold',cold)]:
        if label in completed:continue
        fn();capture(label);completed.append(label);report(False)
except BaseException as error:
    failure=repr(error)
    if e is not None:capture('failure')
finally:
    if e is not None:e.close();e=None
result=report(failure is None)
print(json.dumps(dict(passed=result['passed'],assertions=len(checks),failure=failure,report=str(OUT/'report.json'))))
assert failure is None,failure
