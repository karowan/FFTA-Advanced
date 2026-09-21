"""Absorb's direct-loss contract across normal and percentage native attacks."""
import collections,datetime,itertools,json,pathlib,struct,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-bard.py';ns={'__file__':str(source),'__name__':'absorb_fixture'}
exec(compile(source.read_text(encoding='utf-8').split('# Native command flags')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,STACK,regs,setup,call,job,hp,half,equip=(ns[k] for k in
 ('m','S','meta','OUT','ACTOR','ENEMY','STACK','regs','setup','call','job','hp','half','equip'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2
checks=collections.Counter();failures=[];cases=[];injuries=[];objects=[];case=None
out=OUT/('absorb-direct-loss-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir()

def check(name,actual,expected=True):
 checks[name]+=1
 if actual!=expected:failures.append(dict(case=case,check=name,actual=actual,expected=expected))

def observe(u,pc,size,data):
 unit,before,after=(u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
 frame=m.word(0x0203ff48)
 injuries.append(dict(unit=unit,before=before,after=after,origin=m.word(frame+792),category=m.word(frame+796)))

def object_entry(u,pc,size,data):
 obj=u.reg_read(UC_ARM_REG_R0);objects.append(half(obj+16))

p=S['ffta_viking_hp_loss'];m.u.hook_add(UC_HOOK_CODE,observe,begin=p,end=p)
m.u.hook_add(UC_HOOK_CODE,object_entry,begin=0x080a23b8,end=0x080a23b8)
positive=collections.Counter()
try:
 for action,condition,seed in itertools.product((0,23,40,278,287),('ordinary','ally','KO','blocked'),range(4)):
  case=(action,condition,seed);setup(action,seed);job(A,1,5);job(T,2,118)
  hp(A,1 if action==287 else 500,999,99);hp(T,1 if condition=='KO' else 800,999,99)
  m.put(A+0x2a,struct.pack('<H',1));m.put(T+0x29,b'\0' if condition=='ally' else b'\x80')
  equip(T,'VIK-R1')
  if condition=='blocked':m.put(T+0xe8,b'\x01') # Native disabling reaction-mask bit0.
  ready=bool(m.call(0x08133adc,T+0xe8,5,stack=STACK)) and not m.call(0x080c8280,T,stack=STACK)
  before=half(T+0x18);injuries.clear();objects.clear()
  m.put(regs[13],struct.pack('<4I',action,0,0,255))
  m.call(0x080a433c,regs[0],ns['wrappers'][A],5,14,stack=regs[13])
  rows=[e for e in injuries if e['unit']==T and e['origin']==1 and e['before']>e['after']]
  lost=sum(e['before']-e['after'] for e in rows);remaining=before-lost
  expected=min(lost*3//10,999*15//100,999-remaining) if ready and remaining>0 and condition!='ally' else 0
  check('native-actual-loss-restoration',half(T+0x18),remaining+expected)
  check('one-queued-reaction-after-action',objects.count(436),int(expected>0))
  check('reaction-roots-retired',m.read(0x0203ff44,8)==bytes(8))
  if condition=='ordinary' and expected:positive[action]+=1
  cases.append(dict(case=case,lost=lost,healed=half(T+0x18)-remaining,category=[e['category'] for e in rows],objects=list(objects)))
 # Limit Glove is a lethal fixed-damage control at these declared HP inputs.
 for action in (0,23,40,278):check('nonvacuous-native-recovery-'+str(action),positive[action]>0)
 check('fixed-lethal-control',any(c['case'][0]==287 and c['lost'] and not c['healed'] for c in cases))
except Exception as exc:
 failures.append(dict(case=case,exception=repr(exc)))
report=dict(passed=not failures,romSha1=meta['romSha1'],capture={p.name:hashlib.sha1(p.read_bytes()).hexdigest() for p in (OUT/'executor').glob('execute-trap.*')},
 total=sum(checks.values()),checks=dict(checks),cases=cases,failures=failures,
 limits=['Controlled native execution, not command learning or full campaign; prior dual-hit/reaction-scope evidence retained.'])
(out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(dict(passed=report['passed'],total=report['total'],report=str(out/'report.json'),failures=failures),indent=2))
assert not failures
