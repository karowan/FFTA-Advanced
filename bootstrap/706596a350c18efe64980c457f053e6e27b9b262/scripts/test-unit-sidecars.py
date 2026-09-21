"""Native clear dispatch plus real party sorting/save sidecar integration."""
import ast,ctypes as C,hashlib,importlib.util,json,pathlib,random,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
OUT=ROOT/'build/expansion/probes';ROM=OUT/'content-inventory.gba'
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
source=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
definitions=[n for n in source.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')]
exec(compile(ast.Module(body=definitions,type_ignores=[]),'<native harness>','exec'))
image=ROM.read_bytes();iwram=iwram_from_boot();arm=ARM(image,iwram)
entry=struct.unpack_from('<I',image,0x36d4b8)[0]
cases=0
for active_format in (False,True):
    for address in [UNIT+i*264 for i in range(24)]+[0x02002fc4+i*264 for i in range(12)]+[UNIT+1,UNIT-1,0x02024000]:
        for count in (0,4,263,264,265,528):
            data=bytearray(random.Random(address+count).randbytes(0x25000))
            data[0x1e70:0x1e79]=b'FFTAEXP1\x01' if active_format else bytes(9)
            arm.put(0x02000000,data)
            expected=bytearray(data);offset=address-0x02000000
            expected[offset:offset+count]=bytes(count)
            relative=address-UNIT
            if active_format and count==264 and 0<=relative<24*264 and relative%264==0:
                slot=relative//264
                expected[0x1b40+slot*34:0x1b40+(slot+1)*34]=bytes(34)
                expected[0x1e80+slot]=0
            if active_format:
                for slot,pointer in enumerate([UNIT+264*i for i in range(24)]+[0x02002fc4+264*i for i in range(12)]):
                    if address<=pointer and address+count>=pointer+264:
                        expected[0x1e98+slot]=0
                        expected[0x1ebc+2*slot:0x1ebe+2*slot]=bytes(2)
            arm.call(entry,address,count)
            assert arm.read(0x02000000,len(data))==expected,('clear isolation',active_format,hex(address),count)
            cases+=1

spec=importlib.util.spec_from_file_location('h',ROOT/'scripts/emulator-test.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
seedpath=ROOT/'build/test-lab/early-town.sav';seed=seedpath.read_bytes()
def tap(e,k,w=40):e.run(8,k);e.run(w)
def cold(s):
    e=h.Emulator(ROM);e.set_memory(0,s,0);e.run(3600)
    tap(e,8,180);tap(e,256,60);tap(e,256,60);tap(e,256,180)
    return e
e=cold(seed)
try:
    extras=random.Random(343424).randbytes(816)
    preferences=bytes([0,1])*12
    e.set_memory(0x1b40,extras);e.set_memory(0x1e80,preferences)
    original=e.memory();roster=bytearray(original[0x80:0x1940])
    tap(e,8);tap(e,256,120)
    tap(e,128);tap(e,128);tap(e,4);tap(e,128);tap(e,4,100)
    expected=bytearray(extras);expected[68:102],expected[102:136]=extras[102:136],extras[68:102]
    expected_preferences=bytearray(preferences);expected_preferences[2],expected_preferences[3]=preferences[3],preferences[2]
    roster[528:792],roster[792:1056]=roster[792:1056],roster[528:792]
    ram=e.memory()
    assert ram[0x80:0x1940]==roster,'Native roster swap changed another record'
    assert ram[0x1b40:0x1e70]==expected,'Sidecars did not follow sorted units'
    assert ram[0x1e80:0x1e98]==expected_preferences,'Potion preferences did not follow units'
    assert ram[0x1940:0x1b40]==original[0x1940:0x1b40]
    e.screenshot(OUT/'sidecars-sorted.png')
    tap(e,1,60);tap(e,8);tap(e,16);tap(e,256);tap(e,256,60);tap(e,256,60);tap(e,64,20);tap(e,256,300)
    saved=e.memory(0);assert saved!=seed
finally:e.close()
e=cold(saved)
try:
    ram=e.memory()
    assert ram[0x80:0x1940]==roster
    assert ram[0x1b40:0x1e70]==expected
    assert ram[0x1e80:0x1e98]==expected_preferences
finally:e.close()
assert seedpath.read_bytes()==seed
report={'passed':True,'romSha1':hashlib.sha1(image).hexdigest(),'nativeClearCases':cases,
        'checks':['Exact native whole-roster clear resets only that slots AP and preference','Other clears preserve sidecars',
                  'Actual party menu swaps two generic units with all AP and potion preferences','Native save and cold load preserve sorted roster and sidecars'],
        'remaining':['Recruit replacement by unit copy','Temporary unit AP ownership and battle rollback']}
(OUT/'unit-sidecars-tests.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
