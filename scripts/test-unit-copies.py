"""Native memcpy/free dispatch with owned AP snapshots and rollback.

Fixtures allocate real native heap blocks. Registration helpers establish the
same tails as constructors; constructor call sites are tested independently.
"""
import ast,ctypes as C,hashlib,importlib.util,itertools,json,pathlib,random,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')],type_ignores=[]),'<harness>','exec'))
OUT=ROOT/'build/expansion/probes';image=(OUT/'ability-core.gba').read_bytes()
manifest=json.loads((OUT/'ability-core.json').read_text())
assert hashlib.sha1(image).hexdigest()==manifest['romSha1']
symbols={p[2]:int(p[0],16) for line in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=line.split())==3}
arm=ARM(image,iwram_from_boot());checks={};alignments=[]
def check(ok,label):
    assert ok,label
    checks[label]=checks.get(label,0)+1
for name in ('ffta_on_unit_copy','ffta_copy_owner_free','ffta_snapshot_register','ffta_manager_register','ffta_selection_register'):
    def aligned(u,address,size,data):alignments.append(u.reg_read(UC_ARM_REG_SP)%8)
    arm.u.hook_add(UC_HOOK_CODE,aligned,begin=symbols[name],end=symbols[name])
def call(name,*args,**kwargs):return arm.call(symbols[name],*args,**kwargs)
def word(address,value):arm.put(address,struct.pack('<I',value))
heap=0x02018000
def initialize():
    arm.put(0x02000000,bytes(0x40000));arm.put(0x02001e70,b'FFTAEXP1\x01')
    arm.call(0x080070c8,heap,0x27000)
    return [allocate(0x1014),allocate(0x1014),allocate(0x400),allocate(0x3828),allocate(0x7268)]
def allocate(size):
    p=arm.call(0x08007138,heap,size);assert p
    return p
copy_entries=[struct.unpack_from('<I',image,0x36d4bc)[0],0x081443fc]
clear_entry=struct.unpack_from('<I',image,0x36d4b8)[0]
def extra(unit):return call('ffta_owned_extra_ap',unit,144)
def exposed(unit):return call('ffta_owned_exposed',unit)
def wound(unit):return call('ffta_owned_wound',unit)

def pref(unit):
    if UNIT<=unit<UNIT+24*264:return 0x02001e80+(unit-UNIT)//264
    return extra(unit)+34
def populate(unit,seed):
    rng=random.Random(seed);native=bytearray(rng.randbytes(264));native[6]=1
    arm.put(unit,native)
    if extra(unit):arm.put(extra(unit),rng.randbytes(34));arm.put(pref(unit),bytes([seed%3]))
    if exposed(unit):arm.put(exposed(unit),bytes([seed%2]))
    if wound(unit):arm.put(wound(unit),struct.pack('<H',(seed*193)&65535))
def captured(unit):return arm.read(unit,264),arm.read(extra(unit),34) if extra(unit) else bytes(34),arm.read(pref(unit),1) if extra(unit) else bytes(1),arm.read(exposed(unit),1) if exposed(unit) else bytes(1),arm.read(wound(unit),2) if wound(unit) else bytes(2)
for residue,copy_entry in itertools.product((0,4),copy_entries):
    s1,s2,manager,selection,party=initialize()
    call('ffta_snapshot_register',s1);call('ffta_snapshot_register',s2)
    call('ffta_manager_register',manager);word(0x0200f4b0,manager)
    call('ffta_selection_register',selection);word(0x0200f454,selection)
    word(0x03002818,party);call('ffta_party_copy_register')
    roster=[UNIT+i*264 for i in range(24)]
    backups=[s+4+i*264 for s in (s1,s2) for i in range(13)]
    temps=[manager+0x40,manager+0x148,selection+0xa4c,party+0x1be4]
    unknown=0x02006000
    allunits=roster+[0x02002fc4+264*i for i in range(12)]+backups+temps+[unknown]
    for i,unit in enumerate(allunits):populate(unit,100+i)
    for source in allunits:
        for destination in allunits:
            before=arm.read(0x02000000,0x40000);expected=bytearray(before)
            original,ap,potion,status,wound_record=captured(source)
            offset=destination-0x02000000
            expected[offset:offset+264]=original
            target=extra(destination)
            if target:
                offset=target-0x02000000;expected[offset:offset+34]=ap
                expected[pref(destination)-0x02000000]=potion[0]
            if exposed(destination):expected[exposed(destination)-0x02000000]=status[0]
            if wound(destination):
                at=wound(destination)-0x02000000;expected[at:at+2]=wound_record
            arm.call(copy_entry,destination,source,264,stack=STACK+residue)
            check(arm.read(0x02000000,0x40000)==expected,'whole-copy exact isolation')
    for destination in allunits:
        for length in (0,4,16,260,264,268):
            before=arm.read(0x02000000,0x40000);expected=bytearray(before)
            source=unknown;offset=destination-0x02000000
            expected[offset:offset+length]=before[source-0x02000000:source-0x02000000+length]
            if length==264 and extra(destination):
                at=extra(destination)-0x02000000;expected[at:at+34]=bytes(34);expected[pref(destination)-0x02000000]=0
            if length==264 and exposed(destination):expected[exposed(destination)-0x02000000]=0
            if length==264 and wound(destination):
                at=wound(destination)-0x02000000;expected[at:at+2]=bytes(2)
            arm.call(copy_entry,destination,source,length,stack=STACK+residue)
            check(arm.read(0x02000000,0x40000)==expected,'partial copies preserve AP')
    for unit in backups+temps:
        populate(unit,194)
        before=arm.read(0x02000000,0x40000);expected=bytearray(before)
        offset=unit-0x02000000;expected[offset:offset+264]=bytes(264)
        offset=extra(unit)-0x02000000;expected[offset:offset+38]=bytes(38)
        arm.call(clear_entry,unit,264,stack=STACK+residue)
        check(arm.read(0x02000000,0x40000)==expected,'temporary clear exact isolation')
    # Nested simulations must recover the distinct state at each capture.
    for i in range(13):
        live=roster[i];a=s1+4+264*i;b=s2+4+264*i
        populate(live,1000+i);first=captured(live)
        arm.call(copy_entry,a,live,264)
        populate(live,2000+i);second=captured(live)
        arm.call(copy_entry,b,live,264)
        populate(live,3000+i)
        arm.call(copy_entry,live,b,264);check(captured(live)==second,'inner rollback')
        arm.call(copy_entry,live,a,264);check(captured(live)==first,'outer rollback')
    # Free an interior snapshot node while the newer node remains live.
    arm.call(0x08007170,heap,s1,stack=STACK+residue)
    check(extra(s1+4)==0 and extra(s2+4)!=0,'non-LIFO snapshot retirement')
    recycled=allocate(0x1014);call('ffta_snapshot_register',recycled)
    check(arm.read(extra(recycled+4),34)==bytes(34),'reused snapshot starts empty')
    check(arm.read(wound(recycled+4),2)==bytes(2),'reused snapshot wound empty')
    for owner,unit in ((manager,temps[0]),(selection,temps[2]),(party,temps[3]),(s2,s2+4),(recycled,recycled+4)):
        arm.call(0x08007170,heap,owner,stack=STACK+residue)
        check(extra(unit)==0,'freed owner rejected')
        check(wound(unit)==0,'freed wound owner rejected')
    for offset in (-1,1,4,263,265):
        check(extra(UNIT+offset)==0,'inexact owner rejected')
        check(wound(UNIT+offset)==0,'inexact wound owner rejected')
check(not any(alignments),'all observed C hook entries aligned')
report={'passed':True,'romSha1':manifest['romSha1'],'checks':checks,'total':sum(checks.values()),'alignedEntries':len(alignments),
        'limitations':['Owner constructor wiring has a separate test','Populated battle rollback rendering still requires integration']}
(OUT/'unit-copies-tests.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
