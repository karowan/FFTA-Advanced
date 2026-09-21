"""Native Bard support/reaction executions and cross-job timing contracts."""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-bard.py';ns={'__file__':str(source),'__name__':'bard_passives_fixture'}
exec(compile(source.read_text().split('# Native command flags')[0],str(source),'exec'),ns)
m,S,meta,OUT,ACTOR,TARGET,CTX,STACK,regs=(ns[x] for x in ('m','S','meta','OUT','ACTOR','ENEMY','CTX','STACK','regs'))
setup,execute,call,job,hp,half,status=(ns[x] for x in ('setup','execute','call','job','hp','half','status'))
equip=ns['ns']['equip'];check_counts=collections.Counter();samples=[];case=None
native_execute=execute;native_executions=0

def execute(action):
 global native_executions
 result=native_execute(action);native_executions+=1;return result
def check(k,a,b):check_counts[k]+=1;assert a==b,(k,a,b,case)
def state(u):return call('ffta_job_state',u)
def charge(u):m.put(state(u)+11,b'\x01')
def results():
 count=m.read(regs[0]+0x26bd,1)[0]
 return [half(regs[0]+i*0x2c4+0x10) for i in range(count)]

# Real native MP getter for every original and new action. Existing martial,
# medicine, zero-cost and Hide controls must retain their original cost.
for action in range(432):
 case=('Clear Voice MP',action);setup(393)
 baseline=m.call(0x0812ed98,ACTOR,action,stack=STACK);equip(ACTOR,'BRD-S2')
 tagged=(23<=action<=42 and action not in (33,37)) or (393<=action<=400 and action!=398)
 expected=(baseline*3+3)//4 if baseline and tagged else baseline
 check('native-MP-discount',m.call(0x0812ed98,ACTOR,action,stack=STACK),expected)

# Song/Black/Time Magic costs are paid through the whole native transaction.
for action,seed in itertools.product((23,34,35,36,38,39,40,41,42,393,394,395,396,397,398,399,400),range(4)):
 case=('native Clear Voice',action,seed);setup(action,seed);equip(ACTOR,'BRD-S2')
 expected=m.call(0x0812ed98,ACTOR,action,stack=STACK);before=half(ACTOR+0x1c);execute(action)
 check('one-discounted-payment',before-half(ACTOR+0x1c),expected)

# Every declared seed, both reactions, physical versus magical HP loss,
# and reaction-suppressing Silence/Petrify. Keep positive hits and misses.
for reaction,action,blocked,seed in itertools.product(('BRD-R1','BRD-R2'),(0,23),(False,True),range(8)):
 case=('native reaction',reaction,action,blocked,seed);setup(action,seed)
 job(ACTOR,1,2);job(TARGET,5,123);hp(TARGET,500,500);m.put(TARGET+0x29,b'\x80')
 equip(TARGET,reaction)
 if blocked:m.put(TARGET+(0xe8 if reaction=='BRD-R1' else 0xeb),bytes((64 if reaction=='BRD-R1' else 8,)))
 execute(action);ids=results();loss=500-half(TARGET+0x18)
 expected=bool(loss and not blocked and (reaction=='BRD-R1' or action==0))
 check('queued-reaction-exact-admission',(439 if reaction=='BRD-R1' else 440) in ids,expected)
 check('native-charge-or-Haste',bool(m.read(state(TARGET)+11,1)[0]&1) if reaction=='BRD-R1' else status(TARGET,21),expected)
 check('retired-transient-roots',m.read(0x0203ff44,8),bytes(8))
 samples.append(dict(reaction=reaction,action=action,blocked=blocked,seed=seed,loss=loss,ids=ids))
check('nonvacuous-both-reactions',all(any((439 if r=='BRD-R1' else 440) in x['ids'] for x in samples) for r in ('BRD-R1','BRD-R2')),True)

# Approved charged Angelsong plus first Regen/Encouragement on a Human with
# Recuperation:117+67=184. Refresh loses only the separate67-point heal.
for action,recup,boost,refresh in itertools.product((393,394,395,397,400,42,36),(False,True),(False,True),(False,True)):
 case=('Encouragement mix',action,recup,boost,refresh);setup(action,1);hp(TARGET,1,300)
 equip(ACTOR,'BRD-S1');equip(ACTOR,'BRD-R1')
 if recup:equip(TARGET,'SLD-AX-S1')
 if boost:charge(ACTOR)
 bits={394:(25,),395:(24,),397:(3,),400:(25,24,3),42:(21,),36:(5,)}.get(action,())
 if refresh:
  for bit in bits:m.put(TARGET+0xe8+bit//8,bytes((m.read(TARGET+0xe8+bit//8,1)[0]|(1<<(bit%8)),)))
  if action in (394,395):ns['give'](TARGET,action==395)
 base=(120 if action==393 else 60 if action==397 else 0)*(13 if boost else 10)*(3 if recup else 2)//20
 bonus=45*(3 if recup else 2)//2 if bits and not refresh else 0
 execute(action);check('separate-healing-rounding',half(TARGET+0x18),1+base+bonus)
 check('one-follow-up-per-recipient',results().count(438),int(bool(bonus)))
 check('qualifying-cast-consumes-charge',m.read(state(ACTOR)+11,1)[0]&1,0)

for action,boost in itertools.product((0,23,398,399),(False,True)):
 case=('charge consumption',action,boost);setup(action,0);equip(ACTOR,'BRD-R1')
 if boost:charge(ACTOR)
 execute(action)
 check('only-incanted-consumes',bool(m.read(state(ACTOR)+11,1)[0]&1),boost and action in (0,398))

silence_controls=[]
for action,enabled,seed in itertools.product((41,297),(False,True),range(8)):
 case=('native Silence immunity',action,enabled,seed);setup(action,seed)
 job(ACTOR,1,2);job(TARGET,5,123);hp(TARGET,500,500);m.put(TARGET+0x29,b'\x80')
 if enabled:equip(TARGET,'BRD-S2')
 execute(action);silenced=status(TARGET,27)
 if enabled:check('all-native-Silence-routes-blocked',silenced,False)
 else:silence_controls.append(silenced)
check('native-Silence-control-can-hit',any(silence_controls),True)

for action,refresh in itertools.product((391,392),(False,True)):
 case=('Chemist Encouragement',action,refresh);setup(action,1);job(ACTOR,5,121)
 equip(ACTOR,'BRD-S1');hp(TARGET,1,300);equip(TARGET,'SLD-AX-S1')
 m.put(0x02001940+362,bytes([5])*14)
 if refresh:
  if action==391:call('ffta_inoculated_grant',TARGET,0)
  else:m.put(TARGET+0xeb,b'\x03')
 execute(action);check('preventive-medicine-new-buff-heal',half(TARGET+0x18),1 if refresh else 68)
 check('preventive-medicine-single-follow-up',results().count(438),0 if refresh else 1)
 for item in (362,374 if action==391 else 371):check('preventive-medicine-once-stock',m.read(0x02001940+item,1)[0],4)

for action in (0,39):
 case=('Magick Boost while Silenced',action);setup(action,1);job(ACTOR,1,2);job(TARGET,5,123)
 hp(TARGET,500,500);m.put(TARGET+0x29,b'\x80');m.put(TARGET+0xeb,b'\x08');equip(TARGET,'BRD-R1')
 execute(action);check('silence-does-not-prevent-charge',bool(m.read(state(TARGET)+11,1)[0]&1),half(TARGET+0x18)<500)

for seed in range(8):
 case=('charged native Fire',seed);damage=[]
 for boosted in (False,True):
  setup(23,seed);hp(TARGET,500,500);m.put(TARGET+0x29,b'\x80');equip(ACTOR,'BRD-R1')
  if boosted:charge(ACTOR)
  execute(23);damage.append(500-half(TARGET+0x18))
 check('charged-native-spell-final-damage',damage[1],damage[0]*13//10)

# Confuse/Charm are explicit forced-action statuses. Their casts retain a
# charge and cannot produce Encouragement. Compare actual native Fire damage
# with/without a charge, and require the native ally Haste application itself
# to succeed so absence of the follow-up is not an ineligible-target result.
for forced,action in itertools.product((16,32),(23,42)):
 case=('forced cast',forced,action);damage=[]
 for boosted in (False,True):
  setup(action,1);hp(TARGET,100,500);equip(ACTOR,'BRD-R1');equip(ACTOR,'BRD-S1')
  m.put(ACTOR+0xeb,bytes((forced,)))
  m.put(TARGET+0x29,bytes((128 if (action==23) != (forced==32) else 0,)))
  if boosted:charge(ACTOR)
  execute(action);damage.append(100-half(TARGET+0x18))
  check('forced-cast-preserves-charge',bool(m.read(state(ACTOR)+11,1)[0]&1),boosted)
  check('forced-cast-no-Encouragement',results().count(438),0)
  if action==42:check('forced-Haste-positive-control',status(TARGET,21),True)
 check('forced-cast-no-charge-amplification',damage[1],damage[0])

for action in (34,216,398):
 case=('Encouragement exclusions',action);setup(action,1);equip(ACTOR,'BRD-S1');hp(TARGET,1,300)
 execute(action);check('no-heal-for-Quick-Smile-self',results().count(438),0)

case=('ordinary Haste replaces Encore',);setup(42,1)
m.put(state(TARGET)+11,b'\x08');m.put(TARGET+0xea,b'\x20');execute(42)
check('ordinary-Haste-removes-custom-expiry',m.read(state(TARGET)+11,1)[0]&28,0)
check('ordinary-Haste-remains',status(TARGET,21),True)

# Normal Haste replaces the Encore timer; isolated end-turn calls verify
# exactly two subsequent turns and independent boost expiry/removal.
for own,event in itertools.product((False,True),range(1,9)):
 case=('owned lifecycle',own,event);setup(394);equip(TARGET,'SLD-AX-S1')
 p=state(TARGET);m.put(p+11,bytes((1|((6 if own else 2)<<2),)));m.put(TARGET+0xea,b'\x20')
 call('ffta_bard_passive_event',TARGET,event)
 if event in (2,3,4,5,7):check('owned-clear',m.read(p+11,1),b'\x00');check('owned-Haste-clear',status(TARGET,21),False)
for own in (False,True):
 case=('T2',own);setup(394);p=state(TARGET);m.put(p+11,bytes(((6 if own else 2)<<2,)));m.put(TARGET+0xea,b'\x20')
 for turn in range(1,4):
  call('ffta_bard_passive_turn_end',TARGET)
  check('exact-Haste-expiry',status(TARGET,21),turn<(3 if own else 2))

report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(check_counts),total=sum(check_counts.values()),nativeExecutions=native_executions,samples=samples,
 limits=['Bard reaction playback/cold resume has a separate declared test. Song playback, banner/icon recognition, full AP/acquisition and law/AI coverage remain separate acceptance.'])
(OUT/'bard-passives-native.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
