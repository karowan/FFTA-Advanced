"""Read-only native traces for the explicit-choice execution blocker."""
import pathlib,json,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-dancer.py';ns={'__file__':str(source),'__name__':'choice_diagnostic'}
exec(compile(source.read_text().split('# The two separate native formula terms')[0],str(source),'exec'),ns)
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3
m,S,meta,OUT,A,T,C,STACK,regs=(ns[k] for k in ('m','S','meta','OUT','A','T','C','STACK','regs'))
trace=[];samples=[]
points={S['ffta_dancer_context']:'constructor',S['ffta_dancer_eligibility']:'eligibility',0x0812f328:'stage',0x081324cc:'blind-apply'}
def observer(u,address,size,data):
    values=[u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
    trace.append(dict(at=points[address],args=values,context=m.read(0x0200f3f0,52).hex()))
for p in points:m.u.hook_add(UC_HOOK_CODE,observer,begin=p,end=p)
for action,choice in ((403,0),(406,1),(406,2),(406,3),(406,4)):
    trace.clear();ns['fixture'](action);m.put(regs[13]+4,struct.pack('<I',choice));ns['run'](action)
    samples.append(dict(action=action,choice=choice,trace=list(trace),statuses=m.read(T+0xe8,8).hex(),object=m.read(regs[0],96).hex()))
report=dict(romSha1=meta['romSha1'],samples=samples)
(OUT/'dancer-choice-diagnostic.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
