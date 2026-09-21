"""Native undead flags/Zombie versus Auto-Life across custom recovery and drain.

Uses fixed native executor inputs and independent expected resource equations.
No action result, hit or recovery is injected.
"""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-dancer.py'
ns={'__file__':str(source),'__name__':'undead_policy_fixture'}
exec(compile(source.read_text().split('# The two separate native formula terms')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,C,STACK,regs,call,equip,half,job,hp=(ns[x] for x in
 ('m','S','meta','OUT','A','T','C','STACK','regs','call','equip','half','job','hp'))
checks=collections.Counter();failures=[];samples=[];case=None

def check(name,actual,expected):
 checks[name]+=1
 if actual!=expected:failures.append(dict(case=case,check=name,actual=repr(actual),expected=repr(expected)))

def mark(u,kind):
 flags=m.read(u+0x29,1)[0]&~8
 m.put(u+0x29,bytes((flags|(8 if kind in ('undead','both') else 0),)))
 m.put(u+0xe8,struct.pack('<Q',(1<<2 if kind=='auto-life' else 0)|(1<<11 if kind in ('zombie','both') else 0)))

def fixture(action,kind,seed=0):
 ns['fixture'](action,weapon=88,seed=seed)
 if action in (357,358):job(A,1,117);m.put(A+0x2a,struct.pack('<H',389))
 elif action in (416,419):job(A,4,125)
 else:job(A,4,124)
 mark(T,kind)

# The oracle is the documented native flag/status mapping, not a custom helper.
# Copies have separate addresses; native queries preserve them and RNG.
for flags,status in itertools.product((0,1,8,16,128,136,255),range(-1,44)):
 case=('native-predicate',flags,status);fixture(416,'living')
 m.put(T+0x29,bytes((flags,)));m.put(T+0xe8,struct.pack('<Q',0 if status<0 else 1<<status))
 copy=0x03007500;m.put(copy,m.read(T,264));before=m.read(T,264)+m.read(copy,264);rng=m.read(0x030034b0,4)
 expected=int(bool(flags&8) or status==11)
 for u in (T,copy):check('native-original-and-copy',m.call(0x081308f4,u,stack=STACK),expected)
 check('predicate-purity',m.read(T,264)+m.read(copy,264),before);check('predicate-RNG-purity',m.read(0x030034b0,4),rng)

case='native-Auto-Life-setter';fixture(416,'living')
m.call(0x08132498,C,stack=STACK)
check('Auto-Life-native-status2',bool(m.read(T+0xe8,1)[0]&4),True)
check('Auto-Life-not-undead',m.call(0x081308f4,T,stack=STACK),0)

# Independent actual-loss equations cover every custom HP/MP drain family.
for action,kind,seed in itertools.product((357,358,407,416,419),('living','auto-life','undead','zombie','both'),(0,3)):
 case=('native-drain',action,kind,seed);fixture(action,kind,seed)
 before=(half(A+0x18),half(A+0x1c),half(T+0x18),half(T+0x1c))
 ns['execute'](action)
 loss=max(0,before[2]-half(T+0x18));reverse=kind in ('undead','zombie','both')
 cost={357:6,358:4,407:10,416:12,419:8}[action]
 if action in (357,407,416):
  amount=min(loss*35//100,75) if action==416 else min(loss//2,100 if action==357 else 125)
  wanted=max(0,before[0]-amount) if reverse else min(500,before[0]+amount)
  check('HP-drain-native-direction',half(A+0x18),wanted)
  check('HP-drain-exact-cost',half(A+0x1c),before[1]-cost)
 else:
  amount=min(loss//(4 if action==419 else 5),10 if action==419 else 16,before[3])
  wanted=max(0,before[1]-cost-amount) if reverse else min(100,before[1]-cost+amount)
  check('MP-drain-native-direction',half(A+0x1c),wanted)
  check('MP-drain-target-loss',before[3]-half(T+0x1c),amount)
 check('native-action-roots-retired',m.read(0x0203ff44,8),bytes(8))
 samples.append(dict(action=action,kind=kind,seed=seed,loss=loss))
for action in (357,358,407,416,419):
 for kind in ('living','auto-life','undead','zombie','both'):
  check('nonvacuous-drain-pair',any(s['action']==action and s['kind']==kind and s['loss']>0 for s in samples),True)

# Actual friendly command execution: Auto-Life allows healing, while undead
# and Zombie exclude that recipient. Area casts may still heal the caster.
for action,kind in itertools.product((350,383,393),('living','auto-life','undead','zombie','both')):
 case=('native-healing',action,kind);fixture(action,kind)
 job(A,1 if action==350 else 5,116 if action==350 else 122 if action==383 else 123)
 m.put(A+0x2a,struct.pack('<H',379 if action==350 else 0));m.put(T+0x29,bytes((m.read(T+0x29,1)[0]&127,)))
 hp(T,100,500,50);m.put(0x02001940+362,b'\x03')
 before=half(A+0x1c);ns['execute'](action);eligible=kind in ('living','auto-life')
 check('healing-accepted-only-for-living',half(T+0x18)>100,eligible)
 if action==383 and not eligible:check('rejected-single-target-no-payment',half(A+0x1c),before)
 if action in (350,393):check('area-cast-still-pays-for-valid-caster',half(A+0x1c),before-8)
 if action==383:check('medicine-stock-once-only',m.read(0x02001940+362,1)[0],2 if eligible else 3)

# Every single-target recipe revalidates its exact target before inventory is
# debited. Keep Healing Mist's area admission separate from this contract.
for action,choice,kind in itertools.product((383,384,385,386,388,389,390,391,392),(0,367,363),('undead','zombie','both')):
 case=('single-recipe-invalidated',action,choice,kind);fixture(action,kind)
 m.put(T+0x29,bytes((m.read(T+0x29,1)[0]&127,)));m.put(0x02001940+362,b'\x05'*14)
 frame=0x02027000;m.put(frame,bytes(0xb8));m.put(frame+0x44,struct.pack('<II',5,14))
 before=m.read(0x02001940,0x530)
 check('all-single-recipes-revalidate',call('ffta_chemist_payment_gate',A,action,choice,frame),0)
 check('invalid-target-preserves-all-stock',m.read(0x02001940,0x530),before)

for kind in ('living','auto-life','undead','zombie','both'):
 case=('Recuperation-and-Requiem',kind);fixture(393,kind);job(T,1,2);equip(T,'SLD-AX-S1')
 m.put(T+0x29,bytes((m.read(T+0x29,1)[0]&127,)))
 check('Recuperation-native-policy',call('ffta_recuperation_numerator',A,T),3 if kind in ('living','auto-life') else 2)
 m.put(T+0x29,bytes((m.read(T+0x29,1)[0]|128,)));m.put(C+12,struct.pack('<H',396))
 check('Requiem-native-policy',call('ffta_bard_eligibility',C),int(kind not in ('living','auto-life')))

report=dict(passed=not failures,romSha1=meta['romSha1'],assertions=sum(checks.values()),checks=dict(checks),nativeCasts=65,failures=failures,samples=samples)
(OUT/'native-undead-policy.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
assert not failures,('Native undead policy failures',len(failures))
