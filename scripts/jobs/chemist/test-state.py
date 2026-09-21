"""Owned Inoculated state and literal Cureall whitelist; no gameplay-hook claim."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
P=ROOT/'build/expansion/probes';meta=_load_job_candidate(P/'chemist/current.json');OUT=pathlib.Path(meta['path']).parent
rom=pathlib.Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
fix=OUT/'executor';ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes()
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m=ARM(rom,iw);sy={**meta['upstream']['symbols'],**meta['symbols']};counts=collections.Counter();C=0x02026000;TARGET=0x020033e4

def check(k,a,b):counts[k]+=1;assert a==b,(k,a,b)
def call(n,*args,sp=STACK):return m.call(sy[n],*args,stack=sp)
def reset():m.put(0x02000000,ram);m.put(0x03000000,iw);call('ffta_job_reset')
def slot(u):return call('ffta_job_state',u)+8
units=[UNIT+264*i for i in range(24)]+[0x02002fc4+264*i for i in range(12)]
for u,residue in itertools.product(units,(0,4)):
 reset();a=slot(u);m.put(a,b'\xf8');before=m.read(0x02000000,0x40000)
 check('first-grant',call('ffta_inoculated_grant',u,1,sp=STACK+residue),1)
 check('refresh-not-first',call('ffta_inoculated_grant',u,1,sp=STACK+residue),0)
 check('preserved-neighbor-bits',m.read(a,1),b'\xfe')
 for expected in (0xfa,0xf9,0xf8):call('ffta_chemist_turn_end',u,sp=STACK+residue);check('T2-skip-own-application',m.read(a,1),bytes([expected]))
 after=bytearray(m.read(0x02000000,0x40000));after[a-0x02000000]=before[a-0x02000000];check('only-owned-byte',bytes(after),before)
 for event,expected in ((1,0xf2),(2,0xf0),(3,0xf0),(4,0xf0),(5,0xf0),(6,0xfa),(7,0xf8),(8,0xfa)):
  m.put(a,b'\xfa');call('ffta_chemist_event',u,event,sp=STACK+residue);check('typed-event-mask',m.read(a,1),bytes([expected]))
for status in range(256):
 reset();check('verified-harmful-native-whitelist',call('ffta_chemist_native_curable',status),int(status in (6,8,9,10,26,27,28)))
for value,side,charm,query,status,residue in itertools.product((0,1,2,3,6),(0,1),(0,1),(0,16),range(44),(0,4)):
 reset();m.put(UNIT+0x28,b'\0\0');m.put(UNIT+0xeb,bytes([charm*32]));m.put(TARGET+0x28,bytes([0,side*128]));m.put(slot(TARGET),bytes([value]));m.put(C,struct.pack('<IIIHH',UNIT,UNIT,TARGET,5,0)+bytes(36));m.put(C+0x26,bytes([query]));before=m.read(0x02000000,0x40000);rng=m.read(0x030034b0,4)
 check('prevention-explicit-recipient',call('ffta_chemist_prevent_native',C,status,sp=STACK+residue),int(value in (1,2,6) and side!=charm and status in (6,8,9,10,26,27,28)))
 check('prevention-no-writes',m.read(0x02000000,0x40000),before);check('prevention-no-RNG',m.read(0x030034b0,4),rng)
# Explicit native evaluated owners have independent 16-byte records.
for residue in (0,4):
 reset();m.put(UNIT+0x18,struct.pack('<H',100));m.put(UNIT+0xe8,bytes(8));m.put(slot(UNIT),b'\xf8');copy=0x03007500
 check('actual-evaluated-constructor',call('ffta_evaluated_init',copy,UNIT,sp=STACK+residue),1)
 m.put(C,struct.pack('<IIIHH',UNIT,UNIT,copy,391,0)+bytes(36));m.put(C+0x26,b'\x10');before=m.read(0x02000000,0x40000)
 call('ffta_chemist_inoculation',C,sp=STACK+residue);check('query-copy-state',m.read(slot(copy),1),b'\xfe');check('query-live-independent',m.read(slot(UNIT),1),b'\xf8');check('query-no-EWRAM-writes',m.read(0x02000000,0x40000),before)
 m.put(C+8,struct.pack('<I',UNIT));call('ffta_chemist_inoculation',C,sp=STACK+residue);check('live-query-rejected',m.read(slot(UNIT),1),b'\xf8')
 call('ffta_evaluated_close',copy,sp=STACK+residue);check('retired-owner-rejected',call('ffta_inoculated_grant',copy,1,sp=STACK+residue),0)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(counts),total=sum(counts.values()),scope='Callable owned primitives; separate installed/native game scripts cover application/prevention/lifecycle')
(OUT/'state-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
