"""Whole native replacement/removal transactions for all24 roster slots.

Fixed full-clan input, generated Quin candidate, both stack alignments.
This invokes the native commit routine, not recruitment menu playback.
"""
import ast, collections, datetime, hashlib, json, pathlib, struct, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
path=pathlib.Path(meta['path']);rom=path.read_bytes();fix=path.parent/'fixture'
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
proof=json.loads((fix/'prepare-cache.json').read_text())
assert (fix/'frozen.gba').read_bytes()==rom
for name,value in proof['outputs'].items():
    assert hashlib.sha1((fix/name).read_bytes()).hexdigest()==value
ram=(fix/'battle-ready.ram').read_bytes();iw=(fix/'battle-ready.iwram').read_bytes()
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
m=ARM(rom,iw);counts=collections.Counter();cases=[];case=None;failure=None
OUT=path.parent/('full-roster-replacement-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));OUT.mkdir()

def check(label,a,b):
    assert a==b,(case,label,a.hex() if isinstance(a,bytes) else a,b.hex() if isinstance(b,bytes) else b)
    counts[label]+=1

try:
 for residue in (0,4):
  for slot in range(24):
   for operation in (0,1):
    case=(slot,operation,residue)
    r=bytearray(ram);r[0x1e79]=2
    for index in range(24):
        r[0x80+index*264:0x188+index*264]=ram[0x188:0x290]
    r[0x1b40:0x1e70]=bytes((i*13+7)%101 for i in range(816))
    r[0x1e80:0x1e98]=bytes(i%3 for i in range(24))
    # Battle-only records are empty in a normal recruitment scene. Nonzero
    # destination payload catches stale inheritance without arming peer links.
    r[0x3f410:0x3f728]=bytes(792)
    r[0x3f410+slot*22:0x3f426+slot*22]=bytes(range(1,23))
    m.put(0x02000000,r);m.put(0x03000000,iw);m.put(0x030034b0,bytes(4))
    check('native-candidate',m.call(0x080d241c,111,0x02002fc4),1)
    # Native replacement UI supplies the normalized name index and join flag.
    m.put(0x02002fc4,struct.pack('<I',97));m.put(0x020030ca,b'\1')
    m.put(0x02030000,bytes(0x200));m.put(0x0200f450,struct.pack('<I',0x02030000))
    dest=UNIT+slot*264
    m.put(0x0203005c,struct.pack('<II',0x02002fc4,dest))
    before=m.read(0x02000000,0x40000)
    m.call(0x08061f54,operation,stack=STACK+residue)
    after=m.read(0x02000000,0x40000)
    for index in range(24):
        if index==slot:continue
        p=0x80+index*264
        check('other-native-unit-isolated',after[p:p+264],before[p:p+264])
        p=0x1b40+index*34
        check('other-extended-AP-isolated',after[p:p+34],before[p:p+34])
        check('other-potion-preference-isolated',after[0x1e80+index],before[0x1e80+index])
    check('destination-extended-AP-cleared',after[0x1b40+slot*34:0x1b62+slot*34],bytes(34))
    check('destination-potion-preference-cleared',after[0x1e80+slot],0)
    check('destination-transient-record-cleared',after[0x3f410+slot*22:0x3f426+slot*22],bytes(22))
    p=0x80+slot*264
    if operation:
        check('native-Quin-identity',after[p:p+4],bytes.fromhex('5f165508'))
        check('native-Quin-acceptance-history',after[0x1e79],3)
        check('full-clan-remains-full',sum(bool(after[0x84+i*264]) for i in range(24)),24)
    else:
        check('native-slot-cleared',after[p:p+264],bytes(264))
        check('removal-does-not-accept-candidate',after[0x1e79],2)
        check('only-one-slot-vacated',sum(bool(after[0x84+i*264]) for i in range(24)),23)
    cases.append(dict(slot=slot,operation=operation,stackResidue=residue))
except BaseException as error:
 failure=repr(error);(OUT/'failure.ram').write_bytes(m.read(0x02000000,0x40000))
report=dict(passed=failure is None,romSha1=meta['romSha1'],fixture=proof['outputs'],counts=dict(counts),
            assertions=sum(counts.values()),cases=cases,failure=failure,scope=__doc__)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(passed=report['passed'],assertions=report['assertions'],cases=len(cases),failure=failure,report=str(OUT/'report.json'))))
assert failure is None,failure
