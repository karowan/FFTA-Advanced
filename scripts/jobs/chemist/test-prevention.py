"""Actual native ailment callbacks, partial Bad Breath prevention and ABI controls."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
P=ROOT/'build/expansion/probes';meta=_load_job_candidate(P/'chemist/current.json');OUT=pathlib.Path(meta['path']).parent
rom=pathlib.Path(meta['path']).read_bytes();base=(OUT/'input.gba').read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
fix=OUT/'executor';ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes()
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m,n=ARM(rom,iw),ARM(base,iw);TARGET=0x020033e4;CTX=0x0200f3f0;counts=collections.Counter()

def check(k,a,b):counts[k]+=1;assert a==b,(k,a,b)
def setup(a,active=0,query=0,side=1,seed=0):
 a.put(0x02000000,ram);a.put(0x03000000,iw);a.put(UNIT+0xe8,bytes(8));a.put(TARGET+0xe8,bytes(8));a.put(UNIT+0x28,b'\0\0');a.put(TARGET+0x28,bytes([0,128*side]));a.put(0x030034b0,struct.pack('<I',seed));a.put(CTX,struct.pack('<IIIHH',UNIT,TARGET,TARGET,5,0)+bytes(36));a.put(CTX+0x26,bytes([query]));a.put(0x0203f410,bytes(792));a.put(0x0203f410+28*22+8,bytes([active]))
for status,residue in itertools.product(range(44),(0,4)):
 for a in (m,n):setup(a);a.call(0x08131dd4,CTX,status,stack=STACK+residue)
 check('unrecognized-caller-registers',[m.u.reg_read(x) for x in range(UC_ARM_REG_R0,UC_ARM_REG_R12+1)],[n.u.reg_read(x) for x in range(UC_ARM_REG_R0,UC_ARM_REG_R12+1)])
 check('unrecognized-caller-NZCV',m.u.reg_read(UC_ARM_REG_CPSR)&0xf0000000,n.u.reg_read(UC_ARM_REG_CPSR)&0xf0000000)
 check('unrecognized-caller-context',m.read(CTX,52),n.read(CTX,52))
callbacks=[(12,8),(35,10),(41,28),(45,26),(46,6),(56,27),(61,9)]
for effect,status in callbacks:
 fn=struct.unpack_from('<I',base,0x3a87b0+effect*12)[0]
 for active,query,side,residue in itertools.product((0,2),(0,16),(0,1),(0,4)):
  for a in (m,n):setup(a,active,query,side);a.call(fn,CTX,stack=STACK+residue)
  blocked=active and side
  mask=bytearray(n.read(CTX+16,8))
  if blocked:mask[status//8]&=~(1<<(status%8))
  check('native-single-ailment-reported-mask',m.read(CTX+16,8),bytes(mask))
  expected=bytearray(n.read(TARGET,264))
  if blocked:expected=bytearray(ram[0x33e4:0x33e4+264]);expected[0xe8:0xf0]=bytes(8);expected[0x28:0x2a]=bytes([0,128*side])
  check('native-single-ailment-setter-and-timers',m.read(TARGET,264),bytes(expected))
  check('native-single-ailment-RNG',m.read(0x030034b0,4),n.read(0x030034b0,4))
# Native Bad Breath independently rolls seven sub-effects; only six are curable.
for seed,query,residue in itertools.product(range(32),(0,16),(0,4)):
 for a in (m,n):setup(a,2,query,1,seed);a.call(0x081326ac,CTX,stack=STACK+residue)
 original=n.read(CTX+16,8);expected=bytearray(original)
 for s in (6,8,9,10,26,27,28):expected[s//8]&=~(1<<(s%8))
 check('BadBreath-retains-Slow-only',m.read(CTX+16,8),bytes(expected))
 check('BadBreath-same-RNG',m.read(0x030034b0,4),n.read(0x030034b0,4))
 check('BadBreath-no-curable-status-write',int.from_bytes(m.read(TARGET+0xe8,8),'little')&sum(1<<s for s in (6,8,9,10,26,27,28)),0)
 check('BadBreath-retains-native-Slow',m.read(TARGET+0xea,1)[0]&64,n.read(TARGET+0xea,1)[0]&64)
# Beneficial Conceal application and native Cureall reveal are explicit negatives.
for query,residue in itertools.product((0,16),(0,4)):
 for a in (m,n):setup(a,2,query);a.call(0x08133180,CTX,stack=STACK+residue)
 check('Conceal-application-unchanged',m.read(TARGET,264)+m.read(CTX,52),n.read(TARGET,264)+n.read(CTX,52))
 check('Conceal-positive-control',m.read(CTX+17,1)[0]&16,16)
 for a in (m,n):
  setup(a,2,query);a.put(TARGET+0xe9,b'\x10');a.put(CTX+0x30,struct.pack('<I',0x08553e70+139*4));a.call(0x0813388c,stack=STACK+residue)
 check('Cureall-reveal-unchanged',m.read(TARGET,264)+m.read(CTX,52),n.read(TARGET,264)+n.read(CTX,52))
 if not query:check('Cureall-actually-reveals',m.read(TARGET+0xe9,1)[0]&16,0)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(counts),total=sum(counts.values()),scope='Installed native prevention hook with explicit owned fixture state; separate native game script covers action391/lifecycle')
(OUT/'prevention-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
