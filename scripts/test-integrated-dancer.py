"""Deterministic Dancer native execution, owned effects and formula controls.

Not full-job acceptance: choice/route UI and broad law/AI acquisition remain.
"""
import pathlib,json,struct,itertools,collections
from fractions import Fraction
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-bard.py';ns={'__file__':str(source),'__name__':'dancer_fixture'}
exec(compile(source.read_text().split('# Native command flags')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,C,STACK,regs=(ns[x] for x in ('m','S','meta','OUT','ACTOR','ENEMY','CTX','STACK','regs'))
setup,execute,call,job,hp,half,status=(ns[x] for x in ('setup','execute','call','job','hp','half','status'))
equip=ns['ns']['equip'];checks=collections.Counter();case=None;executions=0;outcomes=[]
def check(k,a,b):checks[k]+=1;assert a==b,(k,a,b,case)
def record(u):return call('ffta_job_state',u)
def fixture(action,level=25,weapon=416,seed=0):
 setup(action,seed);job(A,4,124);job(T,1,2);hp(A,100,500,99);hp(T,500,500,99)
 m.put(A+9,bytes((level,)));m.put(A+0x2a,struct.pack('<5H',weapon,0,0,0,0));m.put(T+0x2a,bytes(10))
 m.put(T+0x29,b'\x80');m.put(A+0x20,struct.pack('<4H',90,40,50,40));m.put(T+0x20,struct.pack('<4H',40,25,40,25))
 m.put(A+0x3a,bytes(2));m.put(T+0x3a,bytes(2));m.put(A+0xe8,bytes(8));m.put(T+0xe8,bytes(8))
def run(action):
 global executions
 executions+=1;return execute(action)

# The two separate native formula terms must both use V. Actual primary,
# offhand and restorative/proc weapons cannot change a weapon-free dance.
for level in (1,10,25,40,50):
 for weapon,second in ((0,0),(1,0),(74,0),(88,0),(416,0),(423,0),(1,74)):
  case=('virtual-power',level,weapon,second);fixture(401,level,weapon)
  m.put(A+0x2c,struct.pack('<H',second));v=min(35,12+3*level//5)
  check('independent-virtual-power',call('ffta_dancer_power',A,weapon,10,401),v)
  check('independent-attack-addend',call('ffta_dancer_attack',A,401,weapon,123),123+v)
  before=m.read(A,264)
  for action in (401,404,405,407,409):check('virtual-action-membership',call('ffta_dancer_virtual',action),1)
  for action in (0,402,403,406,408,265):check('ordinary-action-membership',call('ffta_dancer_virtual',action),0)
  check('formula-unit-read-only',m.read(A,264),before)

costs={401:6,402:8,403:12,404:12,405:12,407:10,408:16,409:6}
positives=collections.Counter()
for action,level,seed in itertools.product(costs,(10,25,40),range(4)):
 values=[]
 for weapon in ((416,423) if action==408 else (0,1,74,416)):
  case=('native-dance',action,level,seed,weapon);fixture(action,level,weapon,seed)
  before=(half(A+0x18),half(A+0x1c),half(T+0x18),half(T+0x1c));run(action)
  result=(half(T+0x18),half(T+0x1c),half(A+0x18),m.read(record(T)+3,1)[0],status(T,22))
  check('native-once-MP-payment',before[1]-half(A+0x1c),costs[action])
  check('native-action-roots-retired',m.read(0x0203ff44,8),bytes(8))
  check('unrelated-owned-fields',m.read(record(T),3)+m.read(record(T)+4,6),bytes(9))
  lost=before[2]-result[0]
  if lost>0:positives[action]+=1
  if action==402:
   check('MP-only-no-HP-loss',lost,0)
   # Witch Hunt uses native A accuracy: retain misses rather than requiring
   # every deterministic seed to hit. The matrix must include an actual hit.
   removed=before[3]-result[1]
   check('Witch-Hunt-actual-loss',removed in (0,20),True)
   if removed:positives[action]+=1
  if action in (404,405):check('positive-damage-debuff',bool(result[3]&(7 if action==404 else 56)),lost>0)
  if action==407:check('Jitterbug-actual-HP-recovery',result[2]-before[0],min(125,lost//2))
  values.append(result)
 if action!=408:check('native-dance-independent-of-held-weapon',len(set(values)),1)
 outcomes.append(dict(action=action,level=level,seed=seed,results=values))
for action in (401,402,404,405,407,408,409):check('nonvacuous-damage-'+str(action),positives[action]>0,True)

# Sword Dance really requires one of the two approved primary categories.
for weapon,wanted in ((0,0),(1,0),(74,1),(88,1),(416,1),(423,1),(400,0)):
 case=('Sword-Dance-weapons',weapon);fixture(408,weapon=weapon)
 check('native-primary-eligibility',call('ffta_dancer_eligibility',C),wanted)

# Independent owned timer domains survive copies; remedies clear harmful
# weakening while Dispel clears the beneficial charge, not weakening.
for event in range(1,9):
 case=('lifecycle',event);fixture(401);p=record(A);pattern=bytes(range(22));m.put(p,pattern);m.put(p+3,b'\xdb')
 call('ffta_dancer_event',A,event);actual=m.read(p,22)
 check('lifecycle-other-jobs-preserved',actual[:3]+actual[4:],pattern[:3]+pattern[4:])
 expected=0 if 2<=event<=5 else 192 if event==6 else 27 if event in (7,8) else 219
 check('independent-lifecycle-domains',actual[3],expected)
fixture(401);p=record(A);m.put(p+3,bytes((6|(6<<3)|192,)))
for expected in (2|(2<<3)|64,1|(1<<3),0):
 call('ffta_dancer_turn_end',A);check('application-turn-skip-and-expiry',m.read(p+3,1)[0],expected)

# Cross-class damage includes independent weakening, Fury, Bard buffs and
# incoming Samurai Poise. Assert the whole rational product without rounding
# any intermediate factor, and preserve all RAM/RNG on these native queries.
for magic,polka,frolic,fury,bard,poise in itertools.product((False,True),repeat=6):
 case=('mixed-native-stage',magic,polka,frolic,fury,bard,poise)
 fixture(23 if magic else 0);equip(A,'DNC-R1')
 m.put(record(A)+3,bytes((2*polka+16*frolic+64*fury,)))
 if bard:m.put(record(A)+10,bytes((16 if magic else 2,)))
 if poise:equip(T,'SAM-S2');call('ffta_viking_grant_war_cry',T,0)
 factor=Fraction(1)
 if (frolic if magic else polka):factor*=Fraction(13,20)
 if fury and not magic:factor*=Fraction(27,20)
 if bard:factor*=Fraction(6,5)
 if poise:factor*=Fraction(3,4)
 before=m.read(0x02000000,0x40000);rng=m.read(0x030034b0,4)
 for raw in (0,1,3,17,99,511,997):
  expected=raw*factor.numerator//factor.denominator
  if not magic:expected=min(999,expected)
  check('mixed-one-rational-rounding',call('ffta_integrated_exposed_native_stage',raw,C),expected)
 check('mixed-query-purity',m.read(0x02000000,0x40000)==before and m.read(0x030034b0,4)==rng,True)

# Whole native transactions establish charges and queued Slow attempts. No
# result, accuracy roll or damage is injected. Keep misses in the fixed grid.
reaction_samples=[]
for reaction,action,blocked,seed in itertools.product(('DNC-R1','DNC-R2'),(0,23),(False,True),range(8)):
 case=('native-reaction',reaction,action,blocked,seed);fixture(action,seed=seed)
 job(A,1,2);job(T,4,29 if seed%2 else 124);hp(T,500,500);equip(T,reaction)
 if blocked:m.put(T+0xe8,b'\x40')
 run(action);count=m.read(regs[0]+0x26bd,1)[0]
 ids=[half(regs[0]+i*0x2c4+0x10) for i in range(count)]
 loss=500-half(T+0x18);expected=bool(loss and not blocked and (reaction=='DNC-R1' or action==0))
 hidden=441 if reaction=='DNC-R1' else 442
 check('queued-native-reaction-once',ids.count(hidden),int(expected))
 if reaction=='DNC-R1':check('native-Fury-charge',bool(m.read(record(T)+3,1)[0]&64),expected)
 if not expected:check('no-unearned-Slow',status(A,22),False)
 check('reaction-transient-roots-retired',m.read(0x0203ff44,8),bytes(8))
 reaction_samples.append(dict(reaction=reaction,action=action,blocked=blocked,seed=seed,loss=loss,ids=ids,slow=status(A,22)))
for reaction,hidden in (('DNC-R1',441),('DNC-R2',442)):
 check('nonvacuous-reaction-'+reaction,any(x['reaction']==reaction and hidden in x['ids'] for x in reaction_samples),True)
check('nonvacuous-Counter-Rhythm-Slow',any(x['slow'] for x in reaction_samples),True)

# Fury pays its charge on physical attempts including misses, while ordinary
# magic preserves it; ordinary Fight and both dance damage paths qualify.
for action,seed in itertools.product((0,23,401,408),range(8)):
 case=('Fury-consumption',action,seed);fixture(action,seed=seed);equip(A,'DNC-R1')
 m.put(record(A)+3,b'\x40');run(action)
 check('Fury-physical-attempt-consumes',bool(m.read(record(A)+3,1)[0]&64),action==23)

report=dict(passed=True,romSha1=meta['romSha1'],total=sum(checks.values()),checks=dict(checks),nativeExecutions=executions,outcomes=outcomes,reactions=reaction_samples,
 limits=['Forbidden Dance choice UI and Passing Step route playback are tested separately.',
 'Reactions need native queue playback, cross-class expiry/cold resume and full UI/law/AI acceptance.'])
(OUT/'dancer-native.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ('outcomes','reactions')},indent=2))

# Native help decoding covers every Dancer description and preserves all
# earlier text routes against the image just before the Dancer text patch.
help_source=(ROOT/'scripts/test-samurai-help.py').read_text()
help_source=help_source.replace("P/'samurai/current.json'","P/'integrated-jobs/current.json'")
help_source=help_source.replace("help=meta['help']","help=meta['help']['dancer']")
help_source=help_source.replace("ROM.parent/'input.gba'","ROM.parent.parent/'dancer-help-input.gba'")
help_source=help_source.replace("ROM.parent/'help-tests.json'","ROM.parent/'dancer-help-tests.json'")
exec(compile(help_source,'<native Dancer help>','exec'),{'__file__':__file__,'__name__':'dancer_help'})
from unicorn.arm_const import UC_ARM_REG_R2,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_SP,UC_ARM_REG_PC
others=m.word(0x0802c08c)
widths=[]
for lesson in ns['ns']['registry']['lessons']:
 if lesson['type']!='Reaction':continue
 pointer=m.word(others+lesson['nameId']*4)
 owner=lesson['owners'][0];m.put(A+6,bytes((owner['race'],)));m.put(A+0x3a,bytes((owner['abilityIndex'],)))
 m.put(0x0202800c,struct.pack('<I',A))
 for register,value in ((UC_ARM_REG_R5,0x02028000),(UC_ARM_REG_R6,0x02029000),(UC_ARM_REG_SP,STACK)):
  m.u.reg_write(register,value)
 m.u.emu_start(0x0802c05f,0x0802c09a,count=2000)
 assert m.u.reg_read(UC_ARM_REG_PC)==0x0802c09a
 assert m.u.reg_read(UC_ARM_REG_R2)==pointer,('native-reaction-name-route',lesson['id'])
 width=m.call(0x080161bc,pointer,stack=STACK)
 assert width<=12,('unsafe-native-reaction-label',lesson['id'],width)
 widths.append(dict(id=lesson['id'],tiles=width))
(OUT/'reaction-label-widths.json').write_text(json.dumps(dict(passed=True,romSha1=meta['romSha1'],labels=widths),indent=2))
