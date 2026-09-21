"""Native resource execution, pure forecasts and actual AI row/score consumers."""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-mystic-knight-commands.py'
ns={'__file__':str(source),'__name__':'mystic_resource_fixture'}
exec(compile(source.read_text(encoding='utf-8').split('# Native casts cover')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,STACK,fixture,call,record=(ns[x] for x in ('m','S','meta','OUT','A','T','STACK','fixture','call','record'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3
checks=collections.Counter();failures=[];samples=[];case=None;events=[]
rom=pathlib.Path(meta['path']).read_bytes();table=m.word(0x080cbc74)
item_data=rom[table-0x08000000:table-0x08000000+461*32]
def check(k,a,b):
 checks[k]+=1
 if a!=b:failures.append(dict(check=k,case=case,actual=repr(a),expected=repr(b)))
def half(p):return int.from_bytes(m.read(p,2),'little')
def signed(v):return v if v<0x80000000 else v-0x100000000
def protected():return m.read(A,264)+m.read(T,264)+m.read(record(A),22)+m.read(record(T),22)+m.read(0x030034b0,4)+m.read(0x03005e80,64)+m.read(0x0203ff44,8)
def observe(u,pc,size,data):
 a,t,k,n=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
 # Only actual actor/target pointers; forecast copies are deliberately separate.
 if a==A and t==T:events.append(dict(kind=k,removed=n,hp=half(a+0x18),maxhp=half(a+0x1a),mp=half(a+0x1c),maxmp=half(a+0x1e),targetmp=half(t+0x1c)))
m.u.hook_add(UC_HOOK_CODE,observe,begin=S['ffta_myk_resource_plan'],end=S['ffta_myk_resource_plan'])
def native_lesson(unit,native_id,typ):
 race=m.read(unit+6,1)[0];bank=m.word(m.word(0x080cd538)+race*4)
 index=next(i for i in range(142) if m.read(bank+8*i+4,3)==bytes((native_id,0,typ)))
 m.put(unit+(0x3a if typ==2 else 0x3b),bytes((index,)));m.put(unit+0x40+index,b'\xff')
def setup(kind,condition,pair,seed=0):
 m.put(table,item_data);fixture(0,seed);ns['job'](A,1,7)
 m.put(A+0x2a,struct.pack('<5H',*pair,0,0,0));ns['hp'](A,100,500,20)
 if condition=='full':ns['hp'](A,500,500,100)
 if condition=='nearly-full':ns['hp'](A,499,500,99)
 if condition=='starved':ns['hp'](T,500,500,0)
 if condition=='overkill':ns['hp'](T,1,500,5)
 if condition=='undead':m.put(T+0x29,bytes((m.read(T+0x29,1)[0]|8,)))
 if condition=='ally':m.put(T+0x29,b'\0')
 if condition=='zero':ns['grant'](T,33)
 if condition=='damage-mp':
  ns['job'](T,1,2);native_lesson(T,13,2);m.put(T+0x1c,struct.pack('<HH',999,999))
 if condition=='parry':ns['equip'](T,'MYK-R2');call('ffta_myk_grant',T,1)
 if condition=='restorative':m.put(table+pair[0]*32+26,b'\x3f\0\0')
 if condition=='offhand-drain':m.put(table+pair[1]*32+26,b'\x3d\0\0')
 if condition=='offhand-removal':
  ns['grant'](T,20);m.put(table+pair[1]*32+26,b'\x3e\0\0')
 call('ffta_myk_grant',A,kind)

def expected(e,condition):
 # Independent rules use observed actual HP loss, not formula damage or the
 # production plan's output. Caps and reversal are checked after native writes.
 undead=condition=='undead';n=e['removed']
 if e['kind']==7:
  amount=min(n*35//100,e['maxhp']*15//100)
  if not undead:amount=min(amount,e['maxhp']-e['hp'])
  return 0,amount if undead else -amount
 loss=min(n//4,10,e['targetmp'])
 gain=min(loss,e['mp'] if undead else e['maxmp']-e['mp'])
 return loss,gain if undead else -gain

conditions=('normal','full','nearly-full','starved','overkill','undead','ally','zero','damage-mp','parry','restorative')
cases=list(itertools.product((7,10),conditions,((88,0),(88,89),(89,88),(88,88))))
cases += list(itertools.product((7,10),('offhand-drain','offhand-removal'),((88,89),(89,88))))
for kind,condition,pair in cases:
 case=(kind,condition,pair);setup(kind,condition,pair)
 before=protected();context=m.read(0x0200f3f0,0x34)
 plan=call('ffta_myk_fight_resource_forecast',A,T)
 loss=plan&65535;delta=struct.unpack('<h',struct.pack('<H',plan>>16))[0]
 check('forecast-live-state-RNG',protected(),before);check('forecast-context',m.read(0x0200f3f0,0x34),context)
 check('bounded-target-MP',loss<=min(10,half(T+0x1c)),True)
 check('bounded-actor-resource',abs(delta)<= (75 if kind==7 else 10),True)
 if condition in ('ally','zero','damage-mp','restorative') or (condition=='full' and kind==7) or (condition=='starved' and kind==10):check('no-invented-recovery',plan,0)
 if condition=='nearly-full' and condition!='undead':check('missing-resource-cap',-delta<=1,True)
 if condition=='undead':check('undead-reverses-recovery',delta>=0,True)
 # Existing native functions supply the unchanged baseline. Public native
 # entrypoints must actually include the new resource value in both consumers.
 wa,wt=ns['wrappers'][A],ns['wrappers'][T]
 before=protected();baseline=signed(call('ffta_ai_original_score',wa,wt,0,0))
 actual=signed(m.call(0x080bdecc,wa,wt,0,0,stack=STACK))
 admitted=m.call(0x080c48a4,A,T,0,stack=STACK)
 bonus=loss-delta if baseline and admitted else 0
 check('native-AI-score-resource-value',actual-baseline,bonus)
 check('AI-score-live-state-RNG',protected(),before)
 rows=[]
 for entry in (S['ffta_ai_original_row'],0x080c2618):
  row=0x02028000;m.put(row,bytes(20));m.put(STACK,struct.pack('<II',pair[0],0))
  m.call(entry,row,wa,wt,0,stack=STACK);rows.append(m.read(row,20))
 old,new=rows;oldvalue=struct.unpack_from('<h',old,12)[0];newvalue=struct.unpack_from('<h',new,12)[0]
 rowbonus=loss-delta if int.from_bytes(old[10:12],'little') and oldvalue and admitted else 0
 check('native-AI-row-resource-value',newvalue-oldvalue,rowbonus)
 check('AI-row-preserves-other-fields',new[:12]+new[14:],old[:12]+old[14:])
 check('AI-row-live-state-RNG',protected(),before)
 # Actual Fight and immediate Drain/Osmose commands share the same plan;
 # original payment and post-action application remain native.
 for action,seed in itertools.product((0,409+kind),(0,3,5,7)):
  setup(kind,condition,pair,seed);beforehp,beforemp=half(A+0x18),half(A+0x1c);events.clear()
  ns['execute'](action)
  check('one-resource-claim',len(events)<=1,True)
  if events:
   e=events[0];debit,change=expected(e,condition)
   if kind==7:
    # Ordinary secondary drain can also heal. Its distinct native header
    # contribution is checked separately below through the exact primary plan.
    if condition!='offhand-drain':check('native-actor-HP-after-rider',half(A+0x18),max(0,min(500,e['hp']-change)))
    else:check('native-primary-drain-capped',abs(change)<=75,True)
   else:
    check('native-actor-MP-after-rider',half(A+0x1c),e['mp']-change)
    check('native-target-MP-after-rider',half(T+0x1c),e['targetmp']-debit)
  # Original HP-threshold laws read the signed recipient HP result. Actor
  # drain recovery and target MP loss must not masquerade as target HP healing.
  # Preserve native semantics for both new resource commands and Fight.
  gate=not m.call(0x080c8280,A,stack=STACK) and not m.call(0x080cd92c,A,stack=STACK)
  for i in range(14):
   obj=ns['regs'][0]+i*0x2c4
   if m.word(obj)!=ns['wrappers'][A] or half(obj+16)!=action:continue
   for j in range(m.read(obj+0x2c0,1)[0]):
    row=obj+0x20+j*0x2c;w=m.word(row)
    if not w or m.word(w)!=T or not half(row+12)&0x80 or half(row+12)&0x40:continue
    damage=struct.unpack('<h',m.read(row+0x1e,2))[0]
    for typ,threshold in itertools.product((11,12,13,14),(1,50,255)):
     want=(0<damage<threshold if typ==11 else damage>threshold if typ==12 else 0>damage> -threshold if typ==13 else damage< -threshold)
     law=0x0203e000;m.put(law,bytes(4)+bytes((typ,threshold))+bytes(10));m.put(STACK,struct.pack('<4I',0,damage&65535,row+0x14,law))
     check('native-HP-law-keeps-resource-domains',m.call(0x081343c8,A,T,action,0,stack=STACK),int(gate and want))
  samples.append(dict(kind=kind,condition=condition,pair=pair,action=action,seed=seed,forecast=plan,events=list(events)))
for kind in (7,10):check('nonvacuous-native-resource-'+str(kind),any(s['kind']==kind and s['events'] for s in samples),True)
report=dict(passed=not failures,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),failures=failures,samples=samples,
 limits=['Full AI turn selection and mixed stochastic outcomes remain assembled Mystic AI acceptance.'])
(OUT/'mystic-knight-resources.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2));assert not failures,len(failures)
