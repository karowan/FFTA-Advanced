"""Stormcall native HP-dependent Slow, interception and ordinary S chances."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT/'tools/arm-python'),str(ROOT/'scripts')]
from unicorn import *
from unicorn.arm_const import *
from native_battle_wrappers import from_memory
P=ROOT/'build/expansion/probes';meta=_load_job_candidate(P/'viking/current.json');ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
parent=json.loads((P/'job-state/current.json').read_text());fix=pathlib.Path(meta['path']).parent/'executor'
ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes();regs=struct.unpack_from('<17I',(fix/'execute-trap.state').read_bytes(),0x20)
UNIT,TARGET,EQUIPMENT,RETURN,STACK=0x02000080,0x020033e4,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m=ARM(rom,iw);wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()}
bank=m.word(m.word(0x080cd538)+4)
reaction=next(i for i in range(142) if struct.unpack_from('<H',m.read(bank+8*i,8),4)[0]==13 and m.read(bank+8*i+6,1)[0]==2)
trace=[];counts=collections.Counter();samples=[];violations=[]
def hook(u,pc,size,data):
 ctx=bytes(u.mem_read(u.reg_read(UC_ARM_REG_R0),0x34));trace.append(dict(mpRedirect=mp_redirect,seed=seed,context=ctx.hex()))
pc=meta['symbols']['ffta_viking_physical_eligibility'];m.u.hook_add(UC_HOOK_CODE,hook,begin=pc,end=pc)
def check(k,a,b):
 counts[k]+=1;assert a==b,(k,a,b)
for mp_redirect,seed in itertools.product((False,True),range(64)):
 m.put(0x02000000,ram);m.put(0x03000000,iw)
 actor=bytearray(ram[0x80:0x80+264]);target=bytearray(ram[0x33e4:0x33e4+264])
 actor[5]=actor[7]=actor[0x35]=118;actor[6]=2;actor[0x3a]=actor[0x3b]=0
 target[5]=target[7]=2;target[6]=1;target[0x3a]=reaction if mp_redirect else 0;target[0x3b]=0
 actor[0xe8:0xf0]=target[0xe8:0xf0]=bytes(8)
 struct.pack_into('<4H',actor,0x18,100,100,50,50);struct.pack_into('<4H',target,0x18,250,250,49,49)
 struct.pack_into('<5H',actor,0x2a,399,0,0,0,0);actor[0xf6:0xf8]=bytes([4,14]);target[0xf6:0xf8]=bytes([5,14])
 m.put(UNIT,actor);m.put(TARGET,target);m.put(wrappers[UNIT]+8,struct.pack('<H',4<<5));m.put(wrappers[UNIT]+12,struct.pack('<H',14<<5))
 m.put(0x02001e98,bytes(108));m.put(0x0203ff44,bytes(8));m.put(0x030034b0,struct.pack('<I',seed));m.put(regs[13],struct.pack('<4I',369,0,0,255))
 m.call(0x080a433c,regs[0],wrappers[UNIT],5,14,stack=regs[13]);r=m.read(TARGET,264);damage=250-struct.unpack_from('<H',r,0x18)[0];slow=bool(r[0xea]&64)
 samples.append(dict(mpRedirect=mp_redirect,seed=seed,damage=damage,slow=slow,MP=struct.unpack_from('<H',r,0x1c)[0]))
 (ROM.parent/'stormcall-observed.json').write_text(json.dumps(dict(samples=samples,trace=trace),indent=2))
 if damage<=0 and slow:violations.append(samples[-1])
 check('one-native-MP-charge',struct.unpack('<H',m.read(UNIT+0x1c,2))[0],38)
check('no-Slow-without-positive-HP',violations,[])
check('nonvacuous-damage-plus-Slow',any(x['damage']>0 and x['slow'] for x in samples),True)
check('nonvacuous-ordinary-status-miss',any(x['damage']>0 and not x['slow'] for x in samples),True)
check('nonvacuous-MP-interception',any(x['mpRedirect'] and x['MP']<49 and x['damage']==0 for x in samples),True)
# Query the installed rider admission with real native state. Read-only query
# must not replace the original Slow descriptor or alter native RNG/units.
ctx=0x0200f3f0
for mp_redirect,seed in itertools.product((False,True),range(32)):
 m.put(0x02000000,ram);m.put(0x03000000,iw);m.put(0x0203ff44,bytes(8))
 m.put(UNIT,actor);m.put(TARGET,target)
 m.put(TARGET+0x3a,bytes([reaction if mp_redirect else 0]));m.put(TARGET+0xe8,bytes(8))
 m.put(0x030034b0,struct.pack('<I',seed))
 query=bytearray(0x34);struct.pack_into('<IIIH',query,0,UNIT,TARGET,TARGET,369);query[0x26]=0x10;query[0x28]=1
 struct.pack_into('<I',query,0x30,0x09260000+104*4);m.put(ctx,query)
 before=m.read(0x02000000,0x40000);rng=m.read(0x030034b0,4)
 eligible=m.call(meta['symbols']['ffta_viking_rider_eligible'],ctx)
 check('query-global-state-preserved',m.read(0x02000000,0x40000),before)
 check('query-RNG-preserved',m.read(0x030034b0,4),rng)
 if mp_redirect:check('query-MP-only-no-Slow',eligible,0)
 else:check('query-positive-magic-admitted',eligible,1)

report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(counts),samples=samples,scope=__doc__)
(ROM.parent/'stormcall.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
