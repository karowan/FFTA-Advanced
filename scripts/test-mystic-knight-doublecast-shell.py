"""Whole-pair Shell threshold with native targeting/cost/damage controls.

Fixed inputs execute the native controller call sites and full constructors.
Ordinary Shell is the mitigation oracle; observations never inject outcomes.
"""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-mystic-knight-doublecast.py'
ns={'__file__':str(source),'__name__':'doublecast_shell_fixture'}
exec(compile(source.read_text().split('# Compare every register')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,C,STACK,SP,B,call,half,setup,cast,finish,dispose,h,w=(ns[x] for x in
 ('m','S','meta','OUT','A','T','C','STACK','SP','B','call','half','setup','cast','finish','dispose','h','w'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0
checks=collections.Counter();failures=[];samples=[];case=None;pending=None;hits=[]

def check(k,a,b):
 checks[k]+=1
 if a!=b:failures.append(dict(case=case,check=k,actual=repr(a),expected=repr(b)))

def observe_hit(u,pc,size,data):
 global pending
 c=u.reg_read(UC_ARM_REG_R0)
 if m.word(c+8)==T:
  hits.append(m.read(B+0xaf,1)[0])
  pending=(m.read(0x0200f390,0x94),m.read(0x030034b0,4),m.read(A,264),m.read(T,264))

def observe_magnitude(u,pc,size,data):
 global pending
 if pending:
  check('forecast-preserves-native-query-bank-and-RNG',(m.read(0x0200f390,0x94),m.read(0x030034b0,4)),pending[:2])
  check('forecast-never-mutates-caster',m.read(A,264),pending[2])
  # Only the approved Shell status and its timer may change the defender.
  before=bytearray(pending[3]);after=bytearray(m.read(T,264))
  before[0xdd]=after[0xdd];before[0xeb]=after[0xeb]
  check('forecast-no-unrelated-recipient-writes',after,before)
  pending=None

p=S['ffta_myk_shell_hit'];m.u.hook_add(UC_HOOK_CODE,observe_hit,begin=p,end=p)
p=S['ffta_samurai_magnitude'];m.u.hook_add(UC_HOOK_CODE,observe_magnitude,begin=p,end=p)

def configure(next,center,mp,hp,reaction,existing,seed,condition):
 global pending
 setup((23,next),previous=1,seed=seed,shell=reaction)
 h(T+0x18,hp);h(A+0x1c,mp);m.put(B+0xcc,bytes((center,)))
 if condition=='immune':m.put(T+0x0d,b'\x02')
 if condition=='absorb':m.put(T+0x0d,b'\x03')
 if existing:
  m.call(0x080ce070,T,1,stack=STACK);m.call(0x080ce440,T,3,stack=STACK)
 ns['grants'].clear();hits.clear();pending=None

def preview(action):
 m.put(STACK,struct.pack('<2I',0,2))
 v=m.call(0x08130200,A,T,action,0,stack=STACK)
 return v if v<0x80000000 else v-0x100000000

def run(residue):
 native_code=m.read(0x03005d00,0x300)
 outputs=[];states=[]
 for i in (0,1):
  outputs.append(cast(i,residue))
  states.append((half(T+0x18),bool(m.read(T+0xeb,1)[0]&1),half(A+0x1c)))
 finish(residue);dispose(outputs)
 check('native-roots-retired',m.read(0x0203ff44,8),bytes(8))
 check('native-IWRAM-code-preserved',m.read(0x03005d00,0x300),native_code)
 bank=call('ffta_battle_workspace',0x10)
 check('borrowed-query-bank-retired',m.read(bank,824*8),bytes(824*8))
 return dict(states=states,hits=list(hits),grants=len(ns['grants']),rng=m.read(0x030034b0,4).hex())

# Each pair alone is below threshold on its first spell. Center6 includes T
# on the native cross edge; center7 excludes it. Cure cannot contribute HP
# damage, and a missing second MP payment cannot contribute a hypothetical hit.
cases=((23,5,99,'normal'),(23,6,99,'normal'),(23,7,99,'normal'),
       (1,5,99,'normal'),(23,5,6,'normal'),(23,5,11,'normal'),
       (23,5,12,'normal'),(23,5,99,'immune'),(23,5,99,'absorb'))
for (next,center,mp,condition),seed,residue in itertools.product(cases,(0,1,2),(0,4)):
 case=(next,center,mp,condition,seed,residue)
 configure(next,center,mp,500,False,False,seed,condition);raw=preview(23)
 hp=min(500,250+max(raw,0)+1)
 configure(next,center,mp,hp,False,False,seed,condition);base=run(residue)
 expected=raw>0 and next==23 and center in (5,6) and mp>=12 and 0 in base['hits']
 configure(next,center,mp,hp,False,expected,seed,condition);control=run(residue)
 configure(next,center,mp,hp,True,False,seed,condition);actual=run(residue)
 check('pair-threshold-first-cast-Shell',actual['states'][0][1],expected)
 check('ordinary-Shell-damage-and-cost-oracle',actual['states'],control['states'])
 check('one-decision-for-pair',actual['grants'],int(expected))
 check('forecast-keeps-native-RNG',actual['rng'],base['rng'])
 samples.append(dict(case=case,raw=raw,hp=hp,expected=expected,base=base,control=control,actual=actual))

# Adjacent total thresholds and mixed elements use independent native damage
# queries. A nullified/absorbed first element does not remove the second
# spell's damage from the one decision. Include stronger original magic.
for next,condition,offset,residue in itertools.product((23,24,26),('normal','immune','absorb'),(-1,0,1),(0,4)):
 case=('total-boundary',next,condition,offset,residue)
 configure(next,5,99,500,False,False,1,condition)
 first_raw=preview(23);second_raw=preview(next)
 check('original-spell-native-Doublecast-eligibility',bool(m.call(0x080ccd50,next,19,stack=STACK)),True)
 total=max(0,first_raw)+max(0,second_raw);hp=min(500,250+total+offset)
 configure(next,5,99,hp,False,False,1,condition);base=run(residue)
 expected=0 in base['hits'] and total>0 and hp-total<=250
 configure(next,5,99,hp,False,expected,1,condition);control=run(residue)
 configure(next,5,99,hp,True,False,1,condition);actual=run(residue)
 check('exact-total-threshold',actual['states'][0][1],expected)
 check('mixed-elements-native-Shell-damage',actual['states'],control['states'])
 check('mixed-elements-RNG-unchanged',actual['rng'],base['rng'])
 samples.append(dict(case=case,firstRaw=first_raw,secondRaw=second_raw,total=total,hp=hp,expected=expected,base=base,control=control,actual=actual))

check('nonvacuous-whole-pair-activation',any(x['expected'] for x in samples),True)
check('nonvacuous-cross-edge-activation',any(x['expected'] and x['case'][1]==6 for x in samples),True)
check('nonvacuous-different-target-exclusion',any(x['case'][1]==7 and not x['expected'] and 0 in x['base']['hits'] for x in samples),True)
check('nonvacuous-no-second-payment',any(x['case'][2]==6 and 0 in x['base']['hits'] for x in samples),True)
check('nonvacuous-nullified-first-element',any(x.get('firstRaw')==0 and x.get('secondRaw',0)>0 and x['expected'] for x in samples),True)
report=dict(passed=not failures,romSha1=meta['romSha1'],assertions=sum(checks.values()),checks=dict(checks),failures=failures,samples=samples)
(OUT/'mystic-knight-doublecast-shell.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
assert not failures,('Doublecast Shell failures',len(failures))
