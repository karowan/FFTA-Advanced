"""Sea Legs actual native compatibility and committed movement/status defense."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'tools/arm-python'),str(ROOT/'scripts')]
from unicorn import *
from unicorn.arm_const import *
from native_battle_wrappers import from_memory
P=ROOT/'build/expansion/probes';meta=_load_job_candidate(P/'viking/current.json')
ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes();base=(ROM.parent/'input.gba').read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
parent=json.loads((P/'job-state/current.json').read_text());fix=pathlib.Path(meta['path']).parent/'executor'
ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes()
regs=struct.unpack_from('<17I',(fix/'execute-trap.state').read_bytes(),0x20)
UNIT,TARGET,EQUIPMENT,RETURN,STACK=0x02000080,0x020033e4,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
n,m=ARM(base,iw),ARM(rom,iw);counts=collections.Counter();alignment=[]
pc=meta['symbols']['ffta_viking_compatibility'];m.u.hook_add(UC_HOOK_CODE,lambda u,p,s,d:alignment.append(u.reg_read(UC_ARM_REG_SP)%8),begin=pc,end=pc)
def check(k,a,b):
 counts[k]+=1
 assert a==b,(k,a,b)
def reset(machine,job=118,status=-1,support=True):
 machine.put(0x02000000,ram);machine.put(0x03000000,iw)
 machine.put(UNIT+5,bytes((job,2,job)));machine.put(UNIT+0x3b,bytes([100 if support else 0]));machine.put(UNIT+0xa4,b'\xff')
 machine.put(UNIT+0xe8,bytes(8));machine.put(UNIT+0x18,struct.pack('<4H',250,500,50,50))
 if status>=0:machine.put(UNIT+0xe8+status//8,bytes([1<<(status%8)]))

# Native job IDs are read from their immutable race field, not assumed from
# a name. Exercise every legal original/new Bangaa primary job.
jobs=struct.unpack_from('<I',rom,0xc8598)[0]-0x08000000
bangaa=[j for j in range(126) if rom[jobs+j*52+4]==2 and rom[jobs+j*52+5]==0]
for job in bangaa:
 reset(m,job);check('legal-cross-job-support',m.call(0x080cd50c,UNIT),132)
 for effect in (24,26,51):
  reset(n,job);check('cross-job-immunity',m.call(0x08133a58,UNIT,effect),0 if effect in (24,26) else n.call(0x08133a58,UNIT,effect))
for status,effect,support,residue in itertools.product(range(-1,64),range(93),(False,True),(0,4)):
 reset(n,status=status,support=support);reset(m,status=status,support=support)
 before=m.read(UNIT,264)
 expected=0 if support and effect in (24,26) else n.call(0x08133a58,UNIT,effect,stack=STACK+residue)
 check('native-effect-status-domain',m.call(0x08133a58,UNIT,effect,stack=STACK+residue),expected)
 check('explicit-recipient-unchanged',m.read(UNIT,264),before)
check('aligned-C-callback',set(alignment),{0})
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()}
seen=collections.Counter();outcomes=[]
for action,seed in itertools.product((112,149,173,298,35),range(32)):
 results=[]
 for machine in (n,m):
  machine.put(0x02000000,ram);machine.put(0x03000000,iw)
  actor=bytearray(ram[0x80:0x80+264]);target=bytearray(ram[0x33e4:0x33e4+264])
  actor[5]=actor[7]=actor[0x35]=2;actor[6]=1;actor[0x3a]=actor[0x3b]=0
  target[5]=target[7]=target[0x35]=118;target[6]=2;target[0x3a]=0;target[0x3b]=100;target[0xa4]=255
  actor[0xe8:0xf0]=target[0xe8:0xf0]=bytes(8)
  struct.pack_into('<4H',actor,0x18,100,100,50,50);struct.pack_into('<4H',target,0x18,250,250,49,49)
  struct.pack_into('<5H',actor,0x2a,460,0,0,0,0);actor[0xf6:0xf8]=bytes([4,14]);target[0xf6:0xf8]=bytes([5,14])
  machine.put(UNIT,actor);machine.put(TARGET,target)
  machine.put(wrappers[UNIT]+8,struct.pack('<H',4<<5));machine.put(wrappers[UNIT]+12,struct.pack('<H',14<<5))
  machine.put(0x02001e98,bytes(108));machine.put(0x0203ff44,bytes(8));machine.put(0x030034b0,struct.pack('<I',seed))
  machine.put(regs[13],struct.pack('<4I',action,0,0,255))
  machine.call(0x080a433c,regs[0],wrappers[UNIT],5,14,stack=regs[13])
  results.append(machine.read(TARGET,264))
 ordinary,protected=results
 check('native-HP-stage-retained',protected[0x18:0x20],ordinary[0x18:0x20])
 if action==112:
  check('native-Rush-no-displacement',protected[0xf6:0xf8],bytes([5,14]))
  if ordinary[0xf6:0xf8]!=bytes([5,14]):seen['nativeRushMoved']+=1
 elif action==35:
  check('native-Slow-still-applies',protected[0xe8:0xf0],ordinary[0xe8:0xf0])
  if ordinary[0xea]&64:seen['nativeSlowApplied']+=1
 else:
  check('native-Immobilize-blocked',protected[0xeb]&64,0)
  if ordinary[0xeb]&64:seen['nativeImmobilizeApplied']+=1
 outcomes.append(dict(action=action,seed=seed,originalXY=list(ordinary[0xf6:0xf8]),protectedXY=list(protected[0xf6:0xf8]),originalStatus=ordinary[0xe8:0xf0].hex(),protectedStatus=protected[0xe8:0xf0].hex()))
check('nonvacuous-native-movement-status-controls',all(seen[x]>0 for x in ('nativeRushMoved','nativeSlowApplied','nativeImmobilizeApplied')),True)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(counts),scope=__doc__,
            observed=dict(seen),outcomes=outcomes,gaps=['native menu/save acceptance'])
(ROM.parent/'sea-legs.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
