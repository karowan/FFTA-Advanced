"""Real native Tsunami on flat/downhill terrain; observe writes, never inject results."""
import json, os, pathlib, struct, collections

ROOT=pathlib.Path(__file__).resolve().parents[1]
os.environ['FFTA_TEST_CANDIDATE']=str(ROOT/'build/expansion/probes/integrated-jobs/current.json')
# Reuse only the deterministic terrain/executor fixture definitions. The
# ordinary Tsunami test body is a separate declared check in the same plan.
source=ROOT/'scripts/jobs/viking/test-tsunami.py'
ns={'__file__':str(source),'__name__':'tsunami_fixture'}
exec(compile(source.read_text().split('for center,target,want in ')[0],str(source),'exec'),ns)
m,S,meta,reset,regs,wrappers=(ns[k] for k in ('m','S','meta','reset','regs','wrappers'))
UNIT,TARGET,GRID=(ns[k] for k in ('UNIT','TARGET','GRID'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_SP
checks=collections.Counter();samples=[];writes=[];losses=[];pending=[];next_kind=None;case=None
def half(p):return int.from_bytes(m.read(p,2),'little')
def check(k,a,b):
    checks[k]+=1
    if a!=b:
        (pathlib.Path(meta['path']).parent/'hp-provenance-failure.json').write_text(json.dumps(dict(check=k,actual=a,expected=b,case=case,writes=writes,losses=losses),indent=2))
    assert a==b,(k,a,b,case)
def trace(u,pc,size,data):
    global next_kind
    if pending and pc==pending[-1]['return'] and u.reg_read(UC_ARM_REG_SP)==pending[-1]['sp']:
        event=pending.pop();event['after']=half(event['unit']+0x18);writes.append(event)
    if pc==S['ffta_integrated_native_hp_apply']:
        next_kind=u.reg_read(UC_ARM_REG_R2)
    elif pc==S['ffta_integrated_direct_hp_apply'] and next_kind is None:
        next_kind='descriptor'
    elif pc==S['ffta_original_action_hp_apply']:
        unit=u.reg_read(UC_ARM_REG_R0)
        pending.append(dict(unit=unit,before=half(unit+0x18),kind=next_kind,
            return_=0,sp=u.reg_read(UC_ARM_REG_SP)))
        pending[-1]['return']=u.reg_read(UC_ARM_REG_LR)&~1;next_kind=None
    elif pc==S['ffta_integrated_hp_loss']:
        losses.append(dict(unit=u.reg_read(UC_ARM_REG_R0),before=u.reg_read(UC_ARM_REG_R1),after=u.reg_read(UC_ARM_REG_R2)))
region=json.loads(pathlib.Path(os.environ['FFTA_TEST_CANDIDATE']).read_text())['regions']['integration']
m.u.hook_add(UC_HOOK_CODE,trace,begin=0x08000000+region[0],end=0x08000000+region[1])
direct_kinds={'descriptor',0x080a2607,0x080a2b8b,0x080a3293}
for downhill in (False,True):
    for sea in (False,True):
        for seed in range(16):
            case=(downhill,sea,seed);ns['case']=case
            reset((8,6),(8,6),True,sea)
            if downhill:m.put(GRID+2*(6*16+9),b'\x0c')
            writes.clear();losses.clear();pending.clear();next_kind=None
            m.put(0x030034b0,struct.pack('<I',seed));m.put(regs[13],struct.pack('<4I',372,0,0,255))
            m.call(0x080a433c,regs[0],wrappers[UNIT],8,6,stack=regs[13])
            check('all-native-writes-returned',len(pending),0)
            direct=sum(max(0,w['before']-w['after']) for w in writes if w['unit']==TARGET and w['kind'] in direct_kinds)
            # Fight and descriptor effects have distinct row+1C writers.
            # A3588..A3594 follows the actual descriptor-driven displacement.
            fall=sum(max(0,w['before']-w['after']) for w in writes if w['unit']==TARGET and w['kind'] in (0x080a2ccd,0x080a3595))
            observed=sum(e['before']-e['after'] for e in losses if e['unit']==TARGET)
            check('only-direct-loss-reaches-job-consumers',observed,direct)
            check('actual-total-HP-includes-fall',250-half(TARGET+0x18),direct+fall)
            check('water-MP-rider-once-after-direct-hit',half(TARGET+0x1c),42 if direct else 50)
            if sea:check('Sea-Legs-prevents-fall',fall,0)
            samples.append(dict(case=case,direct=direct,fall=fall,writes=list(writes),events=list(losses)))
check('nonvacuous-direct-native-hits',any(s['direct'] for s in samples),True)
check('nonvacuous-direct-native-misses',any(not s['direct'] for s in samples),True)
check('nonvacuous-native-fall-damage',any(s['fall'] for s in samples),True)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),scope=__doc__,samples=samples,
    limitations=['Does not establish queued Viking reaction presentation or zero-rounded TBN consumption'])
out=pathlib.Path(meta['path']).parent
(out/'hp-provenance.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
