"""Native Mystic AI consumers, legal chosen buffs, and actual chosen casts.

No scores or outcomes are overridden. Each deterministic input declares job,
equipment, statuses and owned choices; native row search selects the option.
"""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-mystic-knight-fight-status.py'
ns={'__file__':str(source),'__name__':'mystic_ai_fixture'}
exec(compile(source.read_text(encoding='utf-8').split('samples = []')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,STACK,fixture,call,record=(ns[x] for x in ('m','S','meta','OUT','A','T','STACK','fixture','call','record'))
base=ns['ns'];wrappers=base['wrappers'];ROW=0x02028000;NODE=0x02015488;AI=0x020101f8
checks=collections.Counter();failures=[];samples=[];case=None
from unicorn import UC_HOOK_MEM_INVALID
from unicorn.arm_const import UC_ARM_REG_PC,UC_ARM_REG_SP,UC_ARM_REG_LR
def invalid(u,access,address,size,value,data):
 detail=dict(case=case,address=hex(address),access=access,regs=[hex(u.reg_read(r)) for r in (UC_ARM_REG_PC,UC_ARM_REG_SP,UC_ARM_REG_LR)],failures=failures)
 print(json.dumps(detail));(OUT/'mystic-knight-ai-fault.json').write_text(json.dumps(detail,indent=2),encoding='utf-8');return False
m.u.hook_add(UC_HOOK_MEM_INVALID,invalid)
def check(k,a,b):
 checks[k]+=1
 if a!=b:failures.append(dict(check=k,case=case,actual=repr(a),expected=repr(b)))
def half(p):return int.from_bytes(m.read(p,2),'little')
def signed(n):return n if n<0x80000000 else n-0x100000000
def protected():return m.read(A,264)+m.read(T,264)+m.read(record(A),22)+m.read(record(T),22)+m.read(0x030034b0,4)+m.read(0x03005e80,64)
def row(action,sp=STACK):
 m.put(ROW-16,b'\xa5'*52);m.put(ROW,bytes(20));m.put(sp,struct.pack('<II',88,0))
 before=protected();m.call(0x080c2618,ROW,wrappers[A],wrappers[T],action,stack=sp)
 check('row-preserves-live-state-RNG-code',protected(),before)
 check('row-memory-guards',m.read(ROW-16,16)+m.read(ROW+20,16),b'\xa5'*32)
 check('choice-query-roots-retired',m.read(0x0203f728,4)+m.read(0x0203ff44,8),bytes(12))
 return m.read(ROW,20)
def score(action,choice=0,sp=STACK):
 m.put(NODE,struct.pack('<I',wrappers[A]));m.put(NODE+8,struct.pack('<HH',action,choice))
 before=protected();n=signed(m.call(0x080bdecc,wrappers[A],wrappers[T],action,0,stack=sp))
 check('score-preserves-live-state-RNG-code',protected(),before)
 check('score-choice-root-retired',m.read(0x0203f728,4),bytes(4));return n
def buff(choice):
 p=record(T)
 if choice<=8:base['grant'](T,(2,3,4,5,12,21,24,25)[choice-1])
 elif choice==9:call('ffta_centered_grant',T,0)
 elif choice==10:call('ffta_drk_grant_last_resort',T,0)
 elif choice==11:call('ffta_drk_grant_tbn',T,T)
 elif choice==12:call('ffta_viking_grant_war_cry',T,0)
 elif choice==13:call('ffta_inoculated_grant',T,0)
 elif choice in (14,15):m.put(p+10,bytes((2 if choice==14 else 16,)))
 elif choice==16:base['job'](T,5,123);base['equip'](T,'BRD-R1');m.put(p+11,b'\x01')
 elif choice==17:base['equip'](T,'DNC-R1');m.put(p+3,b'\x40')
 elif choice in (18,19):m.put(p+18,bytes((4 if choice==18 else 32,)))
 elif choice==20:m.put(p+19,b'\x02')
 else:call('ffta_myk_grant',T,8)
def reset():
 fixture(421);m.put(0x0203f728,bytes(4));m.put(m.word(0x0200f438)+4,b'\0')
for kind,condition,pair,sp in itertools.product((4,5,6,9),('normal','existing','astra','immunity','inoculated','zero','lethal','damage-mp'),((88,0),(88,89)),(STACK,STACK+4)):
 case=('Fight-status-value',kind,condition,pair,sp);reset();base['job'](A,1,7);m.put(A+0x2a,struct.pack('<5H',*pair,0,0,0));call('ffta_myk_grant',A,kind)
 if condition=='existing':base['grant'](T,{4:9,5:26,6:27,9:22}[kind])
 if condition=='astra':base['grant'](T,4)
 if condition=='immunity':base['job'](T,1,2);ns['native_lesson'](T,11,3)
 if condition=='inoculated':call('ffta_inoculated_grant',T,0)
 if condition=='zero':base['grant'](T,33)
 if condition=='lethal':base['hp'](T,1,500,99)
 if condition=='damage-mp':
  base['job'](T,1,2);ns['native_lesson'](T,13,2);m.put(T+0x1c,struct.pack('<HH',999,999))
 original=signed(call('ffta_ai_original_score',wrappers[A],wrappers[T],0,0));actual=score(0,sp=sp)
 result=row(0,sp);bonus=actual-original
 blocked=condition in ('astra','zero','lethal','damage-mp') or (condition in ('immunity','inoculated') and kind!=9) or (condition=='existing' and kind!=5)
 if blocked:check('inapplicable-or-repeat-no-status-bonus',bonus,0)
 else:check('native-status-chance-adds-value',0<bonus<=100,True)
 samples.append(dict(case=case,baseline=original,score=actual,row=result.hex()))
for choice,sp in itertools.product(range(1,22),(STACK,STACK+4)):
 case=('Spellbreak-option',choice,sp);reset();buff(choice)
 check('declared-buff-eligible',call('ffta_myk_dispellable',T,choice),1)
 result=row(421,sp);selected=int.from_bytes(result[2:4],'little')
 check('native-row-selects-only-present-buff',selected,choice);check('selected-row-admitted',int.from_bytes(result[10:12],'little')>0,True)
 check('native-score-carries-exact-choice',score(421,selected,sp)>0,True)
 # Execute the native row's choice with fixed seeds, never a substituted hit.
 removed=[]
 for seed in (0,3):
  reset();buff(choice);m.put(0x030034b0,struct.pack('<I',seed));call('ffta_myk_grant',A,3)
  base['execute'](421,choice=selected);removed.append(not call('ffta_myk_dispellable',T,choice))
  check('chosen-cast-preserves-actor-fuel',call('ffta_myk_enchantment',A),3)
  check('chosen-cast-single-MP-cost',half(A+0x1c),89)
 samples.append(dict(case=case,choice=selected,row=result.hex(),removed=removed))
for condition in ('none','ally','silenced','wrong-weapon','dead-target'):
 case=('Spellbreak-rejected',condition);reset()
 if condition!='none':buff(8)
 if condition=='ally':m.put(T+0x29,b'\0')
 if condition=='silenced':base['grant'](A,27)
 if condition=='wrong-weapon':m.put(A+0x2a,struct.pack('<H',1))
 if condition=='dead-target':m.put(T+0x18,bytes(2))
 result=row(421);check('no-invalid-Spellbreak-row',int.from_bytes(result[10:12],'little'),0)
 check('no-invalid-Spellbreak-score',score(421,8),0)
for invalid in ('none','player','wrapper','owner','phase','success','action','published-action','published-choice','range'):
 case=('Spellbreak-published-choice',invalid);reset();buff(8)
 m.put(A+0x29,b'\x80');m.put(0x0200f4ec,struct.pack('<I',wrappers[A]));m.put(NODE,struct.pack('<I',wrappers[A]));m.put(NODE+8,struct.pack('<HH',421,8));m.put(NODE+0x1b1,b'\1')
 m.put(AI+0x54f4,struct.pack('<H',8));m.put(AI+0x54be,struct.pack('<HH',421,8))
 if invalid=='player':m.put(A+0x29,b'\0')
 if invalid=='wrapper':m.put(0x0200f4ec,struct.pack('<I',wrappers[T]))
 if invalid=='owner':m.put(NODE,struct.pack('<I',wrappers[T]))
 if invalid=='phase':m.put(AI+0x54f4,bytes(2))
 if invalid=='success':m.put(NODE+0x1b1,b'\0')
 if invalid=='action':m.put(NODE+8,bytes(2))
 if invalid=='published-action':m.put(AI+0x54be,bytes(2))
 if invalid=='published-choice':m.put(AI+0x54c0,bytes(2))
 if invalid=='range':m.put(NODE+10,struct.pack('<H',22));m.put(AI+0x54c0,struct.pack('<H',22))
 check('exact-published-decision-admission',call('ffta_ai_preview_choice',A,421),8 if invalid=='none' else 0)
report=dict(passed=not failures,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),samples=samples,failures=failures)
(OUT/'mystic-knight-ai.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2));assert not failures,len(failures)
