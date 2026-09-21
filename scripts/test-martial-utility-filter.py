"""Inline custom-ward filter ABI and exact native fallback, after willingness.

Actual native rows feed the hook. The test stops at either real continuation;
it does not fabricate a native function return or claim common-gate coverage.
"""
import collections,itertools,json,struct
from ai_review_fixture import *
from unicorn import UC_HOOK_CODE
ROW=0x0202f000;ENTRY=0x080c35d6;NATIVE=0x080c35e2;ACCEPT=0x080c37b4
original=bytes.fromhex('40460af090f9051c2d062d0e');patched=m.read(ENTRY,12)
checks=collections.Counter();cases=[]

def check(name,actual,expected=True):
 checks[name]+=1;assert actual==expected,(case,name,actual,expected)

def execute(sp,control):
 stopped=[]
 def stop(u,pc,size,data):
  if pc in (NATIVE,ACCEPT):stopped.append(pc);u.emu_stop()
 hook=m.u.hook_add(UC_HOOK_CODE,stop,begin=0x080c3500,end=0x080c3800)
 values={UC_ARM_REG_R0:17,UC_ARM_REG_R1:23,UC_ARM_REG_R2:29,UC_ARM_REG_R3:31,
  UC_ARM_REG_R4:41,UC_ARM_REG_R5:43,UC_ARM_REG_R6:ROW+4,UC_ARM_REG_R7:ROW+4,
  UC_ARM_REG_R8:target,UC_ARM_REG_R9:0,UC_ARM_REG_R10:A,UC_ARM_REG_R11:53,
  UC_ARM_REG_SP:sp,UC_ARM_REG_LR:RETURN|1}
 m.put(sp,bytes(32));m.put(sp+12,struct.pack('<I',ROW));before=protected()
 for reg,value in values.items():m.u.reg_write(reg,value)
 m.put(ENTRY,original if control else patched)
 try:m.u.emu_start(ENTRY|1,RETURN,count=100000)
 finally:m.u.hook_del(hook);m.put(ENTRY,patched)
 observed={reg:m.u.reg_read(reg) for reg in values};frame=m.read(sp,32)
 check('reaches-real-continuation',len(stopped),1)
 check('preserves-query-inputs',protected(),before)
 for reg in (UC_ARM_REG_R4,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_SP):
  check('preserves-live-native-registers',observed[reg],values[reg])
 return stopped[0],observed[UC_ARM_REG_R5],frame

for action,condition,sp in itertools.product((351,359,360,364,368,394,403,410),
 ('useful','Protect','complete','KO','enemy','empty'),(STACK,STACK+4)):
 case=(action,condition,sp);reset();target=A if action in (359,360) else T
 m.put(A+5,bytes((117,1,117)));m.put(A+0x2a,b'\x01\0')
 if condition=='Protect':m.put(target+0xeb,b'\x02')
 if condition=='complete':
  m.put(state(A),b'\x02');m.put(state(target)+1,bytes((call('ffta_job_origin',A),1)));m.put(state(target)+4,b'\x02')
 if condition=='KO':m.put(target+0x18,bytes(2))
 if condition=='enemy':target=T;m.put(T+0x29,b'\x80')
 m.put(ROW,bytes(20));m.put(STACK,bytes(8));m.call(0x080c2618,ROW,wrappers[A],wrappers[target],action,stack=STACK)
 if condition=='empty':m.put(ROW+10,bytes(2))
 before=protected();result=execute(sp,False)
 expected=action in (360,364,368) and condition in ('useful','Protect')
 check('only-useful-custom-buffs-accepted',result[0],ACCEPT if expected else NATIVE)
 if not expected:check('exact-original-fallback',result,execute(sp,True))
 check('no-test-ROM-patch-retained',m.read(ENTRY,12),patched)
 cases.append(dict(action=action,condition=condition,stack=sp,accepted=expected))
report=dict(passed=True,romSha1=meta['romSha1'],capture=capture,total=sum(checks.values()),checks=dict(checks),cases=cases,scope=__doc__)
(OUT/'martial-utility-filter.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
