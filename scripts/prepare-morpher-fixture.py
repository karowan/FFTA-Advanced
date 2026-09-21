"""One native Morpher battle fixture, with pre-battle bank/mastery inputs.

The original Capture application produces the declared captured-monster bank
on an isolated clone. This is setup, not a claim of capture gameplay. Native
deployment constructs Morpher sprites, battle wrappers and turn order.
"""
import ast,ctypes,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
sha=lambda b:hashlib.sha1(b).hexdigest()
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes();assert sha(rom)==meta['romSha1']
base=ROM.parent;source=base/'fixture';OUT=base/'fixture-morpher';OUT.mkdir(exist_ok=True)
assert (source/'frozen.gba').read_bytes()==rom
inputs=dict(romSha1=meta['romSha1'],files={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in
    [pathlib.Path(__file__),ROOT/'scripts/emulator-test.py',ROOT/'scripts/battle-menu-observation.py',
     ROOT/'scripts/test-equipment-legality.py',source/'accepted-world.state']})
cache=OUT/'prepare-cache.json'
if cache.exists():
    prior=json.loads(cache.read_text())
    if prior['inputs']==inputs and all((OUT/n).is_file() and sha((OUT/n).read_bytes())==v for n,v in prior['outputs'].items()):
        print(json.dumps(dict(passed=True,reused=True,cache=str(cache))));sys.exit(0)
Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
RETURN,STACK=0x08000100,0x03006800
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
ACTOR=0x4a0;BANK=0x02002e78;T,C=0x02028000,0x02029000
jobs=[0x2c,0x2e,0x31,0x33,0x36,0x38,0x3e,0x40,0x42]
checks=[];route=[];captures=[];bank_rows=[];failure=None;e=Emulator(ROM)
def tap(key,wait=180):e.run(8,key);e.run(wait)
def check(ok,label):assert ok,label;checks.append(label)
def native():
    m=ARM(rom,ctypes.string_at(*e.maps[0x03000000]));m.put(0x02000000,e.memory());return m
def capture(label):
    e.save(OUT/(label+'.state'));e.screenshot(OUT/(label+'.png'))
    (OUT/(label+'.ram')).write_bytes(e.memory());(OUT/(label+'.iwram')).write_bytes(ctypes.string_at(*e.maps[0x03000000]));captures.append(label)
try:
    e.load(source/'accepted-world.state');e.run(1);before=e.memory()
    unit=bytearray(before[ACTOR:ACTOR+264]);check(unit[6]==3,'Original Nu Mou identity retained')
    unit[5]=unit[7]=26;unit[8]=21;unit[0x35:0x38]=bytes((30,10,0))
    unit[0x3a:0x3d]=bytes(3);unit[0x40:0xd0]=bytes(144);unit[0xe6:0xf0]=bytes(10)
    struct.pack_into('<5H',unit,0x2a,0,0,0,0,0);struct.pack_into('<4H',unit,0x18,500,500,99,99)
    for i in range(72,81):unit[0x40+i]=255
    unit[0x40+12]=255 # Native Nu Mou Fire, secondary Black Magic.
    e.set_memory(ACTOR,bytes(unit))
    # Native effect produces nine valid bank records/Souls as declared inputs.
    m=native();m.put(BANK,bytes(320));m.put(0x02001940+229,bytes(9))
    clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    for family,job in enumerate(jobs):
        monster=bytearray(unit);monster[4]=1;monster[5]=monster[7]=job;monster[6]=clean[0x521a14+52*job+4]
        monster[9]=30;monster[0x28:0x2a]=b'\0\x80';monster[0x2a:0x34]=bytes(10)
        struct.pack_into('<4H',monster,0x18,1,300,60,60);m.put(T,monster)
        context=bytearray(52);struct.pack_into('<IIIH',context,0,0x02000000+ACTOR,T,T,188);context[0x24]=30;m.put(C,context)
        slot=m.call(0x080c9428,T);check(slot<20,'Original species has valid bank slot')
        soul=m.call(0x0812edf0,T);check(soul==229+family,'Original Soul family mapping')
        m.call(0x0813347c,C)
        check(m.read(BANK+slot*16,4)==monster[:4] and m.read(0x02001940+soul,1)==b'\x01','Native setup stores captured record and Soul')
        bank_rows.append(dict(family=family,monsterJob=job,slot=slot,soul=soul,record=m.read(BANK+slot*16,16).hex()))
    check(m.call(0x080ccbc4)==9,'Exactly nine captured records declared')
    m.call(0x080caf78,0x02000000+ACTOR,229,0)
    check(m.read(0x02000000+ACTOR+0x2a,2)==struct.pack('<H',229),'Native setup equips the captured Goblin Soul')
    e.set_memory(ACTOR,m.read(0x02000000+ACTOR,264))
    e.set_memory(0x2e78,m.read(BANK,320));e.set_memory(0x1940+229,m.read(0x02001940+229,9));capture('declared-world')
    m=native();tile=m.call(0x08036330,8);check(tile==20,'Original Giza placement')
    target=(m.call(0x08035a20,tile-1)+6,m.call(0x08035a44,tile-1)+4)
    for _ in range(600):
        x,y=struct.unpack_from('<HH',e.memory(),0x2c16)
        if abs(x-target[0])<=2 and abs(y-target[1])<=2:break
        key=(128 if x<target[0] else 64) if abs(x-target[0])>2 else (32 if y<target[1] else 16)
        e.run(1,key);route.append([x,y,key])
    else:raise AssertionError('World route exceeded bound')
    e.run(30);tap(256,1200)
    for _ in range(7):tap(256,600)
    for _ in range(3):tap(256)
    for _ in range(3):
        for key in (128,256,256,256):tap(key)
    tap(8,600);tap(256,600);tap(256,600);observe['wait_for_menu'](e);capture('battle-ready')
    after=e.memory();check(after[ACTOR+5:ACTOR+8]==bytes((26,3,26)),'Native battle constructs original Morpher')
    check(after[ACTOR+0x35:ACTOR+0x37]==bytes((30,10)),'Morph and secondary Black Magic commands retained')
    check(after[0x2e78:0x2fb8]==m.read(BANK,320),'Captured bank survives battle construction')
except Exception as exc:
    import traceback;traceback.print_exc()
    failure=repr(exc);capture('failure')
finally:e.close()
report=dict(passed=failure is None,romSha1=meta['romSha1'],scope=__doc__,inputs=inputs,bank=bank_rows,checks=checks,route=route,failure=failure)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=report['passed'],checks=len(checks),failure=failure,report=str(OUT/'report.json'))))
assert failure is None,failure
(OUT/'frozen.gba').write_bytes(rom)
cache.write_text(json.dumps(dict(inputs=inputs,outputs={n:sha((OUT/n).read_bytes()) for n in
    ('frozen.gba','battle-ready.state','battle-ready.ram','battle-ready.iwram','report.json')}),indent=2)+'\n')
