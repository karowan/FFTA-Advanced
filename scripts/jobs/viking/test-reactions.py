"""Actual native injury, critical flag provenance and once-after-action Viking reactions."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT/'tools/arm-python'),str(ROOT/'scripts')]
from unicorn import *
from unicorn.arm_const import *
from native_battle_wrappers import from_memory
meta=_load_job_candidate(ROOT/'build/expansion/probes/viking/current.json');ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes();S=meta['symbols'];fix=ROM.parent/'executor'
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes();regs=struct.unpack_from('<17I',(fix/'execute-trap.state').read_bytes(),0x20)
UNIT,TARGET,EQUIPMENT,RETURN,STACK=0x02000080,0x02000398,0x02002000,0x08000100,0x03007000
node=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'));exec(compile(ast.Module(body=[n for n in node.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m=ARM(rom,iw);wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()};checks=collections.Counter();samples=[];events=[];criticals=[];objects=[]
def check(k,a,b):checks[k]+=1;assert a==b,(k,a,b,globals().get('case'))
def half(p):return struct.unpack('<H',m.read(p,2))[0]
def word(p):return struct.unpack('<I',m.read(p,4))[0]
def record(unit):return m.call(S['ffta_job_state'],unit)
def observe(u,pc,size,data):
 if pc==0x080a29e8:
  base=u.reg_read(UC_ARM_REG_R2);wrapper=word(base+0x20);criticals.append(word(wrapper))
 else:
  unit=u.reg_read(UC_ARM_REG_R0);before=u.reg_read(UC_ARM_REG_R1);after=u.reg_read(UC_ARM_REG_R2);frame=word(0x0203ff48);obj=word(frame+816)
  flags=[]
  if obj:
   for i in range(m.read(obj+0x2c0,1)[0]):
    row=obj+0x20+44*i;wrapper=word(row)
    if wrapper and word(wrapper)==unit:flags.append(half(row+12))
  events.append(dict(unit=unit,before=before,after=after,flags=flags,origin=word(frame+792),category=word(frame+796),permission=word(frame+16)))
def object_entry(u,pc,size,data):
 obj=u.reg_read(UC_ARM_REG_R0);objects.append((half(obj+0x10),obj))
m.u.hook_add(UC_HOOK_CODE,object_entry,begin=0x080a23b8,end=0x080a23b8)
m.u.hook_add(UC_HOOK_CODE,observe,begin=0x080a29e8,end=0x080a29e8)
pc=S['ffta_viking_hp_loss'];m.u.hook_add(UC_HOOK_CODE,observe,begin=pc,end=pc)
def setup(reaction,ally=False,hp=500,maximum=500,dual=False,status=-1,reset_state=True):
 # Each A433C fixture owns fresh output/allocator handles. Carry only observed
 # persistent state across independent native actions, never stale heap handles.
 carried=(m.read(record(TARGET),16),m.read(0x02001f64,4)) if not reset_state else None
 m.put(0x02000000,ram);m.put(0x03000000,iw);m.put(0x0203ff44,bytes(8));m.call(S['ffta_job_reset'])
 if carried:m.put(record(TARGET),carried[0]);m.put(0x02001f64,carried[1])
 for unit in wrappers:
  xy=(4,14) if unit==UNIT else ((5,14) if unit==TARGET else (0,0))
  m.put(unit+0xf6,bytes(xy));m.put(wrappers[unit]+8,struct.pack('<H',xy[0]<<5));m.put(wrappers[unit]+12,struct.pack('<H',xy[1]<<5))
 for unit in (UNIT,TARGET):
  m.put(unit+0xe8,bytes(8));m.put(unit+0x3a,bytes(2));m.put(unit+0x18,struct.pack('<4H',hp,maximum,999,999))
  m.put(unit+5,bytes([118,2,118]));m.put(unit+0x35,b'\x76');m.put(unit+0x2a,struct.pack('<5H',383 if dual and unit==UNIT else 399,383 if dual and unit==UNIT else 0,0,0,0))
 m.put(UNIT+0x29,bytes([0 if ally else 128]));m.put(TARGET+0x29,b'\0');m.put(TARGET+0x3a,bytes([reaction]))
 if status>=0:m.put(TARGET+0xe8+status//8,bytes([1<<(status%8)]))
 if reset_state:m.put(0x02001f64,struct.pack('<I',1000))
def execute(action,seed):
 global events,criticals,objects
 events=[];criticals=[];objects=[];m.put(0x030034b0,struct.pack('<I',seed));m.put(regs[13],struct.pack('<4I',action,0,0,255))
 m.call(0x080a433c,regs[0],wrappers[UNIT],5,14,stack=regs[13])
 losses=[e for e in events if e['unit']==TARGET and e['before']>e['after'] and e['origin']==1]
 return sum(e['before']-e['after'] for e in losses),losses
for action,reaction,ally,dual,seed in itertools.product((0,365,370),(102,103),(False,True),(False,True),range(32)):
 case=(action,reaction,ally,dual,seed);setup(reaction,ally,dual=dual)
 check('native-reaction-lesson',m.call(0x080cd4d4,TARGET),132 if reaction==102 else 133)
 loss,rows=execute(action,seed);remaining=max(0,500-loss)
 expected_heal=min(loss*3//10,500*15//100) if reaction==102 and not ally and remaining else 0
 check('once-after-all-hits-recovery',half(TARGET+0x18),remaining+expected_heal)
 crit_loss=sum(e['before']-e['after'] for e in rows if e['flags'] and e['flags'][0]&0x20)
 if crit_loss:check('actual-critical-setter-observed',TARGET in criticals,True)
 gil=min(50,crit_loss//2) if reaction==103 and not ally and remaining else 0
 check('critical-only-native-gil',word(0x02001f64),1000+gil)
 check('battle-gil-cap-record',m.read(record(TARGET)+6,1),bytes([gil]))
 reactions=[(a,p) for a,p in objects if a in (436,437)]
 check('one_named_reaction_result',[a for a,p in reactions],[436 if reaction==102 else 437] if expected_heal or gil else [])
 if reactions:
  a,obj=reactions[0];check('self_reaction_wrapper',word(word(obj)),TARGET)
  check('single_native_recipient',m.read(obj+0x2c0,1),b'\x01')
  row=obj+0x20
  if a==436:
   check('native_healing_result',int.from_bytes(m.read(row+0x1e,2),'little',signed=True),-expected_heal)
   check('native_HP_display_flag',bool(half(row+0xc)&1),True)
  else:
   check('native_gil_display_flag',bool(half(row+0xc)&0x1000),True)
   check('native_gil_display_value',half(row+0x28),gil+1)

 check('transient-cleared-on-completion',m.read(record(TARGET)+7,1),b'\0')
 samples.append(dict(case=case,loss=loss,heal=expected_heal,gil=gil,criticalLoss=crit_loss,events=rows))
 (ROM.parent/'reactions-observed.json').write_text(json.dumps(samples,indent=2))
check('nonvacuous-healing',any(x['heal'] for x in samples),True)
check('nonvacuous-critical-gil',any(x['gil'] for x in samples),True)
check('multiple-native-hit-losses',any(len(x['events'])>1 for x in samples),True)
for reaction,seed in itertools.product((102,103),range(16)):
 case=('KO',reaction,seed);setup(reaction,hp=1,maximum=500);loss,rows=execute(0,seed)
 if loss:check('KO-never-revives',half(TARGET+0x18),0)
 check('KO-no-gil',word(0x02001f64),1000)
# Repeated real native critical opportunities cannot farm more than50 per unit.
setup(103)
for seed in range(128):
 case=('battle-cap',seed);setup(103,reset_state=False);execute(0,seed)
 check('finite-battle-gil',word(0x02001f64)<=1050,True)
check('battle-cap-reached',word(0x02001f64),1050)
m.call(S['ffta_viking_lifecycle_event'],TARGET,4);check('battle-end-resets-cap',m.read(record(TARGET)+6,2),bytes(2))
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),samples=samples,scope=__doc__)
(ROM.parent/'reactions.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
