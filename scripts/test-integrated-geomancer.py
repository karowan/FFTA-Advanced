"""Native Geomancer support/reaction transactions and cross-job contracts.

Fixed ROM-derived executor, deterministic seeds, no interactive test driver.
This accepts the four passive lessons only; terrain arts remain separate work.
"""
import collections,itertools,json,pathlib,struct
from fractions import Fraction
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-bard.py';ns={'__file__':str(source),'__name__':'geomancer_fixture'}
exec(compile(source.read_text().split('# Native command flags')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,C,STACK,regs=(ns[x] for x in ('m','S','meta','OUT','ACTOR','ENEMY','CTX','STACK','regs'))
setup,execute,call,job,hp,half,status=(ns[x] for x in ('setup','execute','call','job','hp','half','status'))
equip=ns['ns']['equip'];checks=collections.Counter();case=None;samples=[];executions=0
def check(k,a,b):
 checks[k]+=1
 assert a==b,(k,a,b,case)
def fixture(action,seed=0):
 setup(action,seed);job(A,3,21);job(T,3,121);hp(A,500,500,100);hp(T,500,500,100)
 m.put(T+0x29,b'\x80')
 for u in (A,T):m.put(u+0x2a,bytes(10));m.put(u+0x3a,bytes(2));m.put(u+0xe8,bytes(8))
 # Runtime units expand ROM's packed racial affinities to nine bytes.
 m.put(T+0x0c,bytes([1]*9))
def affinity(u,element,value):
 m.put(u+0x0c+element,bytes((value,)))
def run(action):
 global executions
 executions+=1;execute(action)
 count=m.read(regs[0]+0x26bd,1)[0]
 return [half(regs[0]+i*0x2c4+0x10) for i in range(count)]
def report():
 p=OUT/'geomancer-passives.json'
 p.write_text(json.dumps(dict(romSha1=meta['romSha1'],checks=dict(checks),nativeExecutions=executions,samples=samples),indent=2))

# Native transferability and mobility rebuild: every Nu Mou original/new job,
# native movement equipment and independent native movement modes retained.
for j,equipment,move_type in itertools.product((19,20,21,22,23,24,25,26,27,120,121),(0,191),(0,1,2,3,4,5,6)):
 case=('Surefoot',j,equipment,move_type);fixture(23);job(A,3,j)
 m.put(A+0x2a,struct.pack('<H',equipment));m.put(A+0x3d,bytes((move_type,)))
 m.call(0x080ca2e8,A,stack=STACK);base=m.read(A+0xfc,4);move=m.call(0x080ca394,A,stack=STACK)
 equip(A,'GEO-S2');m.call(0x080ca2e8,A,stack=STACK);got=m.read(A+0xfc,4)
 check('Surefoot-native-Jump',got[2],base[2]+1 if base[2]<127 else base[2])
 check('Surefoot-negative-Jump-bound',got[3],255-got[2])
 check('Surefoot-modes-preserved',got[:2],base[:2])
 check('Surefoot-no-extra-Move',m.call(0x080ca394,A,stack=STACK),move)

# Native tile callback: legal tiles, water, impassability, occupancy and
# height use the original callback. Surefoot may change only a cost nibble.
for enabled in (False,True):
 fixture(23)
 if enabled:equip(A,'GEO-S2')
 m.call(0x080ca2e8,A,stack=STACK)
 grid=0x0202d000;wrapper=ns['wrappers'][A]
 m.put(grid,bytes(0x98a))
 for y,x in itertools.product(range(16),range(16)):
  m.call(0x08097814,grid,x,y,wrapper,stack=STACK)
 actual=m.read(grid,0x700)
 if not enabled:plain=actual
 else:check('Surefoot-native-map-legality-and-height',actual,plain)

# One support per actor: Attunement works with native Black Magic on another
# Nu Mou job. Actual payment/refund is checked independently of hit RNG.
for action,value,seed in itertools.product((23,24,25,26,29),range(5),range(4)):
 outcomes=[]
 for enabled in (False,True):
  case=('Attunement native',action,value,seed,enabled);fixture(action,seed)
  element=m.call(0x0812f8a4,A,action,0,stack=STACK);affinity(T,element,value)
  if enabled:equip(A,'GEO-S1')
  cost=m.call(0x0812ed98,A,action,stack=STACK)
  weak=call('ffta_geo_weakness',A,T,action)
  check('explicit-native-elemental-affinity',weak,int(value==0))
  before=half(A+0x1c);ids=run(action);loss=500-half(T+0x18)
  expected_refund=cost//4 if enabled and weak and loss>0 else 0
  check('actual-debit-minus-one-refund',before-half(A+0x1c),cost-expected_refund)
  check('no-extra-Attunement-action',ids,[action])
  check('native-roots-retired',m.read(0x0203ff44,8),bytes(8))
  outcomes.append(dict(enabled=enabled,cost=cost,loss=loss,weak=weak,mp=half(A+0x1c)))
 # Final damage may cap or include prior integer steps. Direct rational
 # stage controls below establish exact1.25 without assuming early rounding.
 if outcomes[0]['loss']>0 and outcomes[0]['weak']:
  check('weakness-damage-improves',outcomes[1]['loss']>=outcomes[0]['loss'],True)
 samples.append(dict(case=case,outcomes=outcomes))

# Final rational stage with native Fire, low odd magnitudes, Attunement,
# Inspired Magic and Stone Skin. No extra rounding between new/old factors.
for physical,attuned,stone,inspired,raw in itertools.product((False,True),(False,True),(False,True),(False,True),(1,3,17,99,511)):
 action=0 if physical else 23;case=('rational',physical,attuned,stone,inspired,raw);fixture(action)
 affinity(T,1,0)
 if attuned:equip(A,'GEO-S1')
 if stone:equip(T,'GEO-R1')
 if inspired:m.put(call('ffta_job_state',A)+10,bytes((2 if physical else 16,)))
 f=Fraction(1)
 if attuned and not physical:f*=Fraction(5,4)
 if stone and physical:f*=Fraction(3,4)
 if inspired:f*=Fraction(6,5)
 before=m.read(0x02000000,0x40000);rng=m.read(0x030034b0,4)
 check('one-rational-damage-product',call('ffta_integrated_exposed_native_stage',raw,C),min(999,raw*f.numerator//f.denominator) if physical else raw*f.numerator//f.denominator)
 check('preview-read-only',m.read(0x02000000,0x40000),before)
 check('preview-does-not-roll',m.read(0x030034b0,4),rng)

# Real queued reactions, including misses, KO and incapacity. Native result
# objects must carry the new hidden action and ordinary Protect must persist.
reaction_samples=[]
for lesson,action,blocked,lethal,seed in itertools.product(('GEO-R1','GEO-R2'),(0,23),(False,True),(False,True),range(4)):
 case=('native reaction',lesson,action,blocked,lethal,seed);fixture(action,seed)
 equip(T,lesson)
 if blocked:m.put(T+0xe8,b'\x40') # native Petrify
 if lethal:hp(T,1,500,100)
 before=half(T+0x18);ids=run(action);loss=before-half(T+0x18)
 expected=bool(loss and half(T+0x18)>0 and not blocked and (lesson=='GEO-R2' or action==0))
 hidden=443 if lesson=='GEO-R1' else 444
 check('native-reaction-admission',hidden in ids,expected)
 if lesson=='GEO-R1':check('ordinary-Protect-after-survival',status(T,25),expected)
 check('native-reaction-no-MP-charge',half(T+0x1c),100)
 check('no-recursive-native-reaction',ids.count(hidden),int(expected))
 check('native-roots-retired',m.read(0x0203ff44,8),bytes(8))
 reaction_samples.append(dict(lesson=lesson,action=action,blocked=blocked,lethal=lethal,seed=seed,ids=ids,loss=loss,actorHP=half(A+0x18)))
for hidden in (443,444):check('nonvacuous-native-reaction',any(hidden in x['ids'] for x in reaction_samples),True)
check('Wrath-positive-retaliation',any(444 in x['ids'] and x['actorHP']<500 for x in reaction_samples),True)
samples.extend(reaction_samples)

# Every native Nu Mou support is a legal cross-job control. Outgoing support
# damage cannot strengthen Nature's Wrath; incoming damage may still vary.
fixture(0);bank=m.word(m.word(0x080cd538)+3*4)
native_count=next(r['nativeCount'] for r in ns['ns']['registry']['races'] if r['id']==3)
native_supports=[i for i in range(native_count) if m.read(bank+8*i+6,1)[0]==1 and 0<half(bank+8*i+4)<128]
check('native-support-controls-present',bool(native_supports),True)
wrath_controls=[]
for index,seed in itertools.product([0]+native_supports,range(8)):
 case=('Wrath outgoing support',index,seed);fixture(0,seed);equip(T,'GEO-R2')
 m.put(T+0x24,struct.pack('<H',200));m.put(A+0x26,struct.pack('<H',20))
 if index:m.put(T+0x3b,bytes((index,)));m.put(T+0x40+index,b'\xff')
 ids=run(0)
 if 444 in ids:
  at=ids.index(444);obj=regs[0]+at*0x2c4
  amount=struct.unpack('<h',m.read(obj+0x20+0x1e,2))[0]
  wrath_controls.append(dict(index=index,seed=seed,amount=amount,actorHP=half(A+0x18)))
for seed in range(8):
 baseline=next((x for x in wrath_controls if x['index']==0 and x['seed']==seed),None)
 if baseline and baseline['amount']>0:
  for x in wrath_controls:
   if x['seed']==seed and x['amount']>0:
    case=('Wrath outgoing support',x['index'],seed)
    check('Wrath-native-support-damage-invariant',x['amount'],baseline['amount'])
for index in [0]+native_supports:
 check('nonvacuous-native-support-retaliation',any(x['index']==index and x['amount']>0 for x in wrath_controls),True)
samples.extend(wrath_controls)

# Authenticated API contracts complement the native transactions above:
# repeated successful recipients, forced actions, zero payment, rounding,
# refund clamping and repeated completion cannot create extra MP.
FRAME=0x03007400
for debit,forced,repeats,restored in itertools.product((0,1,3,4,6,24,100),(0,16,32),(1,3),(False,True)):
 case=('refund contract',debit,forced,repeats,restored);fixture(23)
 equip(A,'GEO-S1');affinity(T,1,0);m.put(A+0xeb,bytes((forced,)))
 check('snapshot-opens',call('ffta_snapshot_begin',FRAME,A,T,1),1)
 call('ffta_action_started',A,23,1,2)
 check('unpaid-query-has-no-spend',call('ffta_action_mp_spent'),0)
 m.put(A+0x1c,struct.pack('<H',100-debit));call('ffta_action_paid',A,23)
 check('actual-MP-debit-accounted',call('ffta_action_mp_spent'),debit)
 check('payment-count-ABI-preserved',call('ffta_action_paid_count'),1)
 m.put(FRAME+800,struct.pack('<I',2))
 for _ in range(repeats):call('ffta_geo_hp_loss',T,500,490)
 if restored:m.put(A+0x1c,struct.pack('<H',99))
 before=half(A+0x1c);m.put(FRAME+800,struct.pack('<I',1))
 expected=before+min(100-before,debit//4) if not forced else before
 call('ffta_action_completed',A);check('one-refund-for-all-recipients',half(A+0x1c),expected)
 call('ffta_action_completed',A);check('completion-cannot-refund-twice',half(A+0x1c),expected)
 call('ffta_snapshot_end',FRAME);check('payment-state-retired',m.read(FRAME,820),bytes(820))
report();print(json.dumps(dict(romSha1=meta['romSha1'],checks=sum(checks.values()),nativeExecutions=executions)))
