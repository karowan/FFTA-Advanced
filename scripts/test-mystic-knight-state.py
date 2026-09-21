"""Mystic state/support acceptance, exact damage arithmetic and native sequencing.

This does not accept the unfinished enchanted Fight, fourteen command actions,
defensive reactions, presentation, AI or campaign. Inputs are fixed here; no
interactive play, generated action outcomes or live player saves are used.
"""
import pathlib,json,struct,itertools,collections,random
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-dancer.py'
ns={'__file__':str(source),'__name__':'mystic_fixture'}
exec(compile(source.read_text().split('# The two separate native formula terms')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,C,STACK,regs,call,equip,half,job,hp,record=(ns[x] for x in
 ('m','S','meta','OUT','A','T','C','STACK','regs','call','equip','half','job','hp','record'))
from unicorn.arm_const import UC_ARM_REG_R1
checks=collections.Counter();case=None;samples=[]
def check(k,a,b):
 checks[k]+=1
 assert a==b,(k,a,b,case)
def fixture(action=23,seed=0):
 ns['fixture'](action,weapon=88,seed=seed);job(A,4,125);job(T,4,125)
 m.put(record(A),bytes(22));m.put(record(T),bytes(22))
 m.put(call('ffta_integrated_snapshot_storage'),bytes(2080));m.put(call('ffta_additional_extension_snapshot_storage'),bytes(1024));m.put(call('ffta_integrated_result_storage'),bytes(6592))
def sequence(u,n):
 p=record(u)+20;m.put(p,struct.pack('<H',(half(p)&0x1fff)|(n<<13)))
def ratio(p,b,n,d):
 m.put(STACK,struct.pack('<2I',n,d))
 low=call('ffta_damage_ratio',p&0xffffffff,p>>32,b&0xffffffff,b>>32)
 return low|(m.u.reg_read(UC_ARM_REG_R1)<<32)

# Independent arbitrary precision oracle includes overflowing products AND
# denominators, the old overflow boundary, and final saturation. Fixed seed.
fixture();maximum=(1<<64)-1
vectors=list(itertools.product((0,1,999,maximum//2,maximum),
 (1,1280000000,51200000000000,maximum),
 (0,1,27,28431,0xffffffff),(1,20,32000,0xffffffff)))
rng=random.Random(0x4d594b)
vectors += [(rng.getrandbits(64),rng.getrandbits(64) or 1,rng.getrandbits(32),rng.getrandbits(32) or 1) for _ in range(160)]
for p,b,n,d in vectors:
 case=('ratio',p,b,n,d)
 check('exact-ratio-versus-big-integers',ratio(p,b,n,d),min(maximum,p*n//(b*d)))

# Each persistent enchant binds to its ordered primary item. The neighboring
# twenty bytes are owned by other jobs and must survive every operation.
for kind,event in itertools.product(range(1,12),range(1,9)):
 case=('enchant-lifecycle',kind,event);fixture();p=record(A)
 pattern=bytes(range(20));m.put(p,pattern);equip(A,'MYK-S1');sequence(A,2)
 call('ffta_myk_grant',A,kind)
 check('all-eleven-enchants',call('ffta_myk_enchantment',A),kind)
 check('grant-preserves-sequence',call('ffta_myk_sequence',A),2)
 call('ffta_myk_event',A,event)
 check('lifecycle-enchantment',call('ffta_myk_enchantment',A),0 if event in (2,3,4,5,7) else kind)
 check('lifecycle-sequence',call('ffta_myk_sequence',A),0 if event in (2,3,4,5) else 2)
 check('other-job-state-preserved',m.read(p,20),pattern)
for weapon,wanted in ((0,False),(1,False),(35,True),(74,False),(88,True),(416,True),(423,True)):
 case=('primary-weapon',weapon);fixture();call('ffta_myk_grant',A,1)
 m.put(A+0x2a,struct.pack('<H',weapon))
 check('prepared-enchant-invalidated-by-replacement',call('ffta_myk_enchantment',A),1 if weapon==88 else 0)
 call('ffta_myk_event',A,8);call('ffta_myk_grant',A,11)
 check('new-enchant-primary-category',call('ffta_myk_enchantment',A),11 if wanted else 0)
 check('enchantment-beneficial-tag',bool(call('ffta_integrated_beneficial',A)),wanted)

# Declared storage ownership: fresh, frozen, nested copies, claim gates,
# retirement and both adjacent banks. No fake frame is used for native casts.
frame,child,copy=0x03007500,0x03006f00,0x02028000
for previous,mp in itertools.product((0,1,2),(0,49,50,100)):
 case=('snapshot',previous,mp);fixture();equip(A,'MYK-S1');equip(T,'MYK-S2')
 sequence(A,previous);call('ffta_myk_grant',A,3);hp(T,500,500,mp)
 m.put(0x0203ca20,b'\xa5'*32);m.put(call('ffta_integrated_result_storage'),b'\x5a'*32)
 check('snapshot-opens',call('ffta_snapshot_begin',frame,A,T,1),1)
 call('ffta_action_started',A,23,1,2)
 a_flags=call('ffta_action_unit_extension_flags',A);t_flags=call('ffta_action_unit_extension_flags',T)
 check('captured-enchant-and-sequence',a_flags&127,3|(previous<<4)|64)
 check('captured-Ward-threshold',bool(t_flags&128),mp>=50)
 call('ffta_myk_clear',A);sequence(A,2);hp(T,500,500,0)
 equip(A,'MYK-S2')
 check('frozen-actor',call('ffta_action_unit_extension_flags',A),a_flags)
 check('frozen-recipient',call('ffta_action_unit_extension_flags',T),t_flags)
 check('fast-support-query-keeps-frozen-actor',call('ffta_action_unit_extension_support_flags',A),a_flags)
 check('fast-support-query-keeps-frozen-recipient',call('ffta_action_unit_extension_support_flags',T),t_flags)
 check('execution-phase-cannot-claim',call('ffta_action_claim_extension',A,1<<16),0)
 m.put(copy,m.read(A,264));call('ffta_snapshot_copy',copy,A)
 check('exact-copy-flags',call('ffta_action_unit_extension_flags',copy),a_flags)
 check('nested-opens',call('ffta_snapshot_begin',child,copy,T,0),1)
 check('nested-copy-flags',call('ffta_action_unit_extension_flags',copy),a_flags)
 check('query-cannot-claim',call('ffta_action_claim_extension',copy,1<<16),0)
 call('ffta_snapshot_end',child)
 # This explicit API fixture tests claim permission independently of execution.
 m.put(frame+800,struct.pack('<I',2))
 check('frozen-low-bits-protected',call('ffta_action_claim_extension',A,1),0)
 check('claim-first',call('ffta_action_claim_extension',A,1<<16),1)
 check('claim-exactly-once',call('ffta_action_claim_extension',A,1<<16),0)
 check('unsupported-upper-claim-rejected',call('ffta_action_claim_extension',A,1<<22),0)
 check('highest-packed-claim',call('ffta_action_claim_extension',A,1<<21),1)
 check('packed-claim-round-trip',call('ffta_action_unit_extension_flags',A),a_flags|(1<<16)|(1<<21))
 call('ffta_snapshot_copy',copy,A)
 check('packed-claim-copy',call('ffta_action_unit_extension_flags',copy),a_flags|(1<<16)|(1<<21))
 check('unregistered-unit-cannot-claim',call('ffta_action_claim_extension',0x02029000,1<<16),0)
 for origin in (0,2,3):
  m.put(frame+792,struct.pack('<I',origin))
  check('non-primary-cannot-claim',call('ffta_action_claim_extension',A,1<<17),0)
 call('ffta_snapshot_end',frame)
 check('external-bank-retired',m.read(call('ffta_integrated_snapshot_storage'),2080)+m.read(call('ffta_additional_extension_snapshot_storage'),1024),bytes(3104))
 check('heap-boundary-preserved',m.read(0x0203ca20,32),b'\xa5'*32)
 check('result-bank-preserved',m.read(call('ffta_integrated_result_storage'),32),b'\x5a'*32)
 check('all-transient-roots-retired',m.read(0x0203ff44,8),bytes(8))

for forced in (16,32):
 case=('forced-action',forced);fixture();equip(A,'MYK-S1');sequence(A,1)
 m.put(A+0xeb,bytes((forced,)))
 check('forced-action-no-Spellweave',call('ffta_myk_weave_factor',A,23),20)

# Spellweave's sequence is independent of damage classification. Enchants
# are Magic sequencing; Spellbreak/Fight are Physical. No row allocation is
# claimed as native command implementation by these classification checks.
fixture();equip(A,'MYK-S1')
for action,wanted in [(0,1),(1,2),(4,2),(8,2),(23,2),(33,0),(35,2),(37,0),(52,2),(67,0),(68,2),(72,2),(76,0),(87,0),(265,0)]+[(i,1 if i==421 else 2) for i in range(410,424)]:
 case=('sequence-category',action)
 check('explicit-sequence-classification',call('ffta_myk_sequence_category',A,action),wanted)

# Cross-class native final stage against independent rational factors; one
# equipped support per unit, ordinary Fury/weakening and Bard state coexist.
for magic,previous,ward,weakening,fury,bard in itertools.product((False,True),(0,1,2),*( (False,True),)*4):
 case=('cross-class',magic,previous,ward,weakening,fury,bard);fixture(23 if magic else 0)
 equip(A,'MYK-S1');sequence(A,previous)
 if fury:equip(A,'DNC-R1')
 if ward:equip(T,'MYK-S2')
 m.put(record(A)+3,bytes(((16 if magic else 2)*weakening+64*fury,)))
 if bard:m.put(record(A)+10,bytes((16 if magic else 2,)))
 n=d=1
 if previous and previous!=(2 if magic else 1):n*=27;d*=20
 if magic and ward:n*=3;d*=4
 if weakening:n*=13;d*=20
 if fury and not magic:n*=27;d*=20
 if bard:n*=6;d*=5
 before=m.read(0x02000000,0x40000);random_state=m.read(0x030034b0,4)
 for raw in (0,1,3,17,99,511,997):
  expected=raw*n//d
  check('native-final-single-rounding',call('ffta_integrated_exposed_native_stage',raw,C),expected if magic else min(999,expected))
 check('query-state-purity',m.read(0x02000000,0x40000)==before,True)
 check('query-RNG-purity',m.read(0x030034b0,4),random_state)

# Actual original Fire and Cure casts establish Magic, including native misses.
# The test never writes action results, damage, MP payment or the final sequence.
for action,previous,seed in itertools.product((0,1,23),(0,1,2),range(4)):
 case=('native-cast',action,previous,seed);fixture(action,seed)
 equip(A,'MYK-S1');sequence(A,previous)
 if action==1:m.put(T+0x29,b'\x00');hp(T,100,500,99)
 before=(half(A+0x1c),half(T+0x18));ns['run'](action)
 check('native-MP-debit',before[0]-half(A+0x1c),6 if action else 0)
 check('native-action-establishes-category',call('ffta_myk_sequence',A),2 if action else 1)
 check('native-retired-extension-slots',m.read(call('ffta_integrated_snapshot_storage'),2080)+m.read(call('ffta_additional_extension_snapshot_storage'),1024),bytes(3104))
 samples.append(dict(action=action,previous=previous,seed=seed,beforeHP=before[1],afterHP=half(T+0x18)))
for action in (0,1,23):
 check('native-positive-effect-'+str(action),any(x['action']==action and x['beforeHP']!=x['afterHP'] for x in samples),True)
for seed in range(4):
 values={x['previous']:abs(x['beforeHP']-x['afterHP']) for x in samples if x['action']==1 and x['seed']==seed}
 check('Spellweave-does-not-scale-healing',len(set(values.values())),1)
 for action,opposite in ((0,2),(23,1)):
  damage={x['previous']:x['beforeHP']-x['afterHP'] for x in samples if x['action']==action and x['seed']==seed}
  check('native-opposite-category-damage',damage[opposite],damage[0]*27//20)
  check('native-same-category-no-bonus',damage[3-opposite],damage[0])
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),assertions=sum(checks.values()),nativeCasts=len(samples),samples=samples,
 remaining='Mystic commands, enchanted Fight, defensive reactions and native UI/AI/law/save acceptance remain separate.')
(OUT/'mystic-knight-state.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
