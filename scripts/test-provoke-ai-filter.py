"""Real native candidate filtering and narrow effect94 switch extension.

Native rows, full C32C0 willingness/compatibility, fixed seeds and exact original
fallback. No fabricated native return values or altered AI probabilities.
"""
import collections,itertools,json,struct
from ai_review_fixture import *
from unicorn import UC_HOOK_CODE
ROW,ENTRY=0x0202f000,0x080c3608
old=bytes.fromhex('308801385b2801d901f0b3f8');patched=m.read(ENTRY,12)
checks=collections.Counter();cases=[];failures=[];positive=collections.Counter()
def check(name,actual,expected=True):
 checks[name]+=1
 if actual!=expected:failures.append(dict(case=case,check=name,actual=actual,expected=expected))

for action,condition,seed,sp in itertools.product((0,26,120,347,360,366,367,369,373,403),
 ('useful','same-challenger','KO','Petrify','Silence','law-block','Immunity'),range(8),(STACK,STACK+4)):
 if condition=='Immunity' and action!=373:continue
 case=(action,condition,seed,sp);reset();m.put(A+5,bytes((118,2,118)));m.put(A+0x2a,struct.pack('<H',399));m.put(T+0x29,b'\x80')
 m.put(A+0xf6,bytes((4,14)));m.put(T+0xf6,bytes((5,14)))
 if condition=='same-challenger':call('ffta_viking_grant_challenge',T,A)
 if condition=='KO':m.put(T+0x18,bytes(2))
 if condition=='Petrify':m.put(T+0xe8,b'\x40')
 if condition=='Silence':m.put(A+0xeb,b'\x08')
 if condition=='Immunity':
  indices=[i for i in range(142) if (p:=m.call(0x080cd480,1,i,stack=sp)) and m.read(p+4,3)==bytes((11,0,3))]
  assert indices;index=indices[0];m.put(T+0x3b,bytes((index,)));m.put(T+0x40+index,b'\xff')
  check('real-native-Immunity-equipped',m.call(0x080cd50c,T,stack=sp),11)
 m.put(ROW,bytes(20));m.put(sp,bytes(8));m.call(0x080c2618,ROW,wrappers[A],wrappers[T],action,stack=sp)
 # Native early law-block bit, independent of the later application switch.
 if condition=='law-block':m.put(ROW+17,b'\x01')
 before=m.read(0x02000000,0x40000);row=m.read(ROW,20);outcomes=[];seen=[]
 def observe(u,pc,size,data):seen.append(pc)
 hook=m.u.hook_add(UC_HOOK_CODE,observe,begin=ENTRY,end=ENTRY)
 try:
  for original in (False,True):
   m.put(0x02000000,before);m.put(0x030034b0,struct.pack('<I',seed));m.put(ENTRY,old if original else patched)
   # This switch lies inside a previously translated basic block. Invalidate
   # that block when comparing original bytes; memory writes alone can leave
   # its cached literal-load instructions paired with the restored data.
   m.u.ctl_remove_cache(0x080c3200,0x080c4800)
   seen.clear()
   try:result=m.call(0x080c32c0,A,T,ROW,0,stack=sp)
   except Exception:
    print(dict(case=case,original=original,pc=hex(m.u.reg_read(UC_ARM_REG_PC)),sp=hex(m.u.reg_read(UC_ARM_REG_SP)),lr=hex(m.u.reg_read(UC_ARM_REG_LR)),row=row.hex()),flush=True)
    raise
   outcomes.append(dict(accepted=result,rng=m.word(0x030034b0),switchVisits=len(seen)))
   check('native-filter-keeps-inputs',m.read(0x02000000,0x40000)==before)
 finally:m.u.hook_del(hook);m.put(ENTRY,patched)
 actual,control=outcomes
 if action!=373:check('all-other-actions-exact-native-filter',actual,control)
 else:
  check('original-unknown-effect-rejected',control['accepted'],0)
  check('native-willingness-RNG-preserved',actual['rng'],control['rng'])
  if condition in ('same-challenger','KO','Petrify','law-block','Immunity'):check('no-bypass-of-native-gates',actual['accepted'],0)
  elif actual['switchVisits']:
   check('compatible-Provoke-accepted',actual['accepted'],1);positive[condition]+=1
 cases.append(dict(action=action,condition=condition,seed=seed,stack=sp,row=list(struct.unpack('<10h',row)),actual=actual,control=control))
for condition in ('useful','Silence'):case=('nonvacuous',condition);check('actual-native-Provoke-admission',positive[condition]>0)
# Every switch boundary retains its old branch and evaluated effect index,
# except the single authorized action/effect pair. Both caller alignments.
for action,effect,sp in itertools.product((373,360),(0,1,21,59,82,92,93,94,95,255),(STACK,STACK+4)):
 case=('switch',action,effect,sp);reset();m.put(ROW,struct.pack('<3H',action,0,effect))
 results=[]
 for original in (False,True):
  stops=[]
  def stop(u,pc,size,data):
   if pc in (0x080c3614,0x080c477a,0x080c37b4):stops.append(pc);u.emu_stop()
  hook=m.u.hook_add(UC_HOOK_CODE,stop,begin=0x080c3600,end=0x080c478c)
  values={UC_ARM_REG_R4:41,UC_ARM_REG_R5:43,UC_ARM_REG_R6:ROW+4,UC_ARM_REG_R7:ROW+4,UC_ARM_REG_R8:T,UC_ARM_REG_R9:0,UC_ARM_REG_R10:A,UC_ARM_REG_R11:53,UC_ARM_REG_SP:sp}
  m.put(sp,bytes(32));m.put(sp+12,struct.pack('<I',ROW))
  for reg,value in values.items():m.u.reg_write(reg,value)
  m.put(ENTRY,old if original else patched)
  m.u.ctl_remove_cache(0x080c3200,0x080c4800)
  try:m.u.emu_start(ENTRY|1,RETURN,count=10000)
  finally:m.u.hook_del(hook);m.put(ENTRY,patched)
  check('one-real-continuation',len(stops),1)
  for reg,value in values.items():check('switch-preserves-live-registers',m.u.reg_read(reg),value)
  results.append((stops[0],m.u.reg_read(UC_ARM_REG_R0)))
 if action==373 and effect==94:check('only-Provoke-effect94-extension',results[0][0],0x080c37b4)
 else:check('switch-exact-original-fallback',results[0],results[1])
report=dict(passed=not failures,romSha1=meta['romSha1'],capture=capture,total=sum(checks.values()),checks=dict(checks),cases=cases,failures=failures,scope=__doc__)
(OUT/'provoke-ai-filter.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ('cases','capture')},indent=2));assert not failures,failures[:20]
