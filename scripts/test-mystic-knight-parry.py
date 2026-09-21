"""Spell Parry: real native hit/miss transactions and read-only forecasts.

Fixed inputs only; instrumentation observes the native formula/writer without
changing registers, random samples, hit outcomes or damage.
"""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-mystic-knight-commands.py'
ns={'__file__':str(source),'__name__':'mystic_parry_fixture'}
exec(compile(source.read_text().split('# Native casts cover')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,C,STACK,call,half,fixture,grant,execute,equip,record=(ns[x] for x in
 ('m','S','meta','OUT','A','T','C','STACK','call','half','fixture','grant','execute','equip','record'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2
checks=collections.Counter();failures=[];samples=[];case=None;hits=[]
def check(k,a,b):
 checks[k]+=1
 if a!=b:failures.append(dict(case=case,check=k,actual=repr(a),expected=repr(b)))
def observe(u,pc,size,data):
 hits.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2)))
p=S['ffta_myk_parry_hit'];m.u.hook_add(UC_HOOK_CODE,observe,begin=p,end=p)
def setup(action,seed,parry=True,condition='normal'):
 fixture(action,seed)
 if parry:equip(T,'MYK-R2')
 call('ffta_myk_grant',T,1)
 if action==421:grant(T,25)
 if condition=='immune':m.put(T+0x0d,b'\x02')
 if condition=='ally':m.put(T+0x29,b'\x00')
 if condition=='asleep':grant(T,26)
 if condition=='weapon-lost':m.put(T+0x2a,bytes(2))
 hits.clear()

# Damage retains a single rounding boundary with every original formula.
# Magic and status carriers cannot spend the blade. Positive and zero-damage
# successful physical hits use the same consumption boundary.
for action,seed,condition in itertools.product((0,112,410,414,421,23,423),range(16),('normal','immune')):
 outcomes=[]
 for parry in (False,True):
  case=('native',action,seed,condition,parry);setup(action,seed,parry,condition)
  execute(action,choice=8 if action==421 else 0)
  outcomes.append(dict(hp=half(T+0x18),blade=call('ffta_myk_enchantment',T),
   status=m.read(T+0xe8,8).hex(),hits=list(hits)))
  check('native-roots-retired',m.read(0x0203ff44,8),bytes(8))
 base,parried=outcomes
 physical=action in (0,112,410,414,421)
 if physical:
  check('half-physical-HP',500-parried['hp'],max(0,500-base['hp'])//2 if base['hp']<=500 else 500-base['hp'])
  successful=any(a==A and t==T and i==action for a,t,i in parried['hits'])
  check('consume-on-hit-preserve-on-miss',parried['blade'],0 if successful else 1)
 else:
  check('magic-or-status-unchanged',parried,base)
 samples.append(dict(action=action,seed=seed,condition=condition,base=base,parry=parried))
check('nonvacuous-physical-hit',any(s['action']==0 and s['parry']['hp']<500 for s in samples),True)
check('nonvacuous-miss',any(s['action']==0 and not s['parry']['hits'] for s in samples),True)
check('nonvacuous-zero-damage-consumption',any(s['action']==410 and s['condition']=='immune' and
 s['parry']['hp']==500 and s['parry']['blade']==0 for s in samples),True)

# Native Fight forecast must agree with the installed formula without paying
# fuel, including both native stack residues. Ineligible defenders preserve
# the exact vanilla result. This is not an injected execution result.
for condition,action,residue in itertools.product(('normal','ally','asleep','weapon-lost'),(0,112,23),(0,4)):
 values=[]
 for parry in (False,True):
  case=('forecast',condition,action,residue,parry);setup(action,0,parry,condition)
  native_ready=not m.call(0x080c8280,T,stack=STACK) and bool(m.call(0x08133adc,T+0xe8,5,stack=STACK))
  before=m.read(A,264)+m.read(T,264)+m.read(record(T),22);rng=m.read(0x030034b0,4)
  m.put(STACK+residue,struct.pack('<2I',0,2))
  values.append(m.call(0x08130200,A,T,action,88,stack=STACK+residue))
  check('forecast-keeps-live-units-and-fuel',m.read(A,264)+m.read(T,264)+m.read(record(T),22),before)
  check('forecast-keeps-RNG',m.read(0x030034b0,4),rng)
 check('forecast-physical-reduction-and-exclusions',values[1],values[0]//2 if action in (0,112) and condition in ('normal','asleep') and native_ready else values[0])

# Native Reflex's actual status mask is the adopted capability rule. Do not
# assume a status disables interception from its translated name alone.
for bit in range(44):
 case=('native-status-capability',bit);setup(0,0);grant(T,bit)
 ready=not m.call(0x080c8280,T,stack=STACK) and bool(m.call(0x08133adc,T+0xe8,5,stack=STACK)) and bool(half(T+0x18)) and not bool(m.read(T+0xe8,1)[0]&64)
 check('all-native-status-capabilities',call('ffta_myk_parry_factor',A,T,0),1 if ready else 2)

# Two actual native weapon objects share one incoming-action snapshot. Observe
# each HP writer to compare rounding per component and prove the second hit
# retains protection after the first has spent the live blade.
from unicorn.arm_const import UC_ARM_REG_R9
writes=[]
def hp_observer(u,pc,size,data):
 if u.reg_read(UC_ARM_REG_R0)==T:
  value=u.reg_read(UC_ARM_REG_R1);writes.append(value if value<0x80000000 else value-0x100000000)
m.u.hook_add(UC_HOOK_CODE,hp_observer,begin=0x080a2210,end=0x080a2210)
dual=[]
for seed in range(16):
 pair=[]
 for parry in (False,True):
  case=('dual-native-weapons',seed,parry);setup(0,seed,parry)
  ns['job'](A,1,7);m.put(A+0x2a,struct.pack('<2H',1,1));writes.clear()
  execute(0);pair.append(dict(writes=list(writes),blade=call('ffta_myk_enchantment',T),hits=list(hits)))
 check('dual-each-component-halved',pair[1]['writes'],[x//2 if x>0 else x for x in pair[0]['writes']])
 if pair[1]['hits']:check('dual-consumes-fuel',pair[1]['blade'],0)
 dual.append(dict(seed=seed,base=pair[0],parry=pair[1]))
check('nonvacuous-two-hit-action',any(len(x['parry']['writes'])==2 for x in dual),True)

# Explicit snapshot API contracts supplement real execution. Frozen readiness
# survives a consumed blade, including exact evaluated copies, but nested
# previews inherit disabled reactions and may never manufacture a claim.
frame,child,copy=0x03007500,0x03006f00,0x02028000
for origin,permission in itertools.product((0,1,2,3),(0,1)):
 case=('snapshot-boundaries',origin,permission);setup(0,0)
 check('snapshot-opens',call('ffta_snapshot_begin',frame,A,T,1),1)
 call('ffta_action_started',A,0,origin,1)
 m.put(frame+16,struct.pack('<I',permission))
 ready=call('ffta_action_unit_extension_flags',T)
 check('fast-reaction-flags-match-snapshot',call('ffta_action_unit_extension_reaction_flags',T),ready)
 call('ffta_myk_clear',T)
 expected=1 if permission and origin in (0,1) else 2
 check('frozen-consumed-blade-factor',call('ffta_myk_parry_factor',A,T,0),expected)
 m.put(copy,m.read(T,264));call('ffta_snapshot_copy',copy,T)
 check('copied-consumed-blade-factor',call('ffta_myk_parry_factor',A,copy,0),expected)
 check('query-does-not-claim',call('ffta_action_unit_extension_flags',T),ready)
 check('nested-preview-opens',call('ffta_snapshot_begin',child,A,T,0),1)
 check('nested-preserves-permission-and-origin',call('ffta_myk_parry_factor',A,T,0),expected)
 call('ffta_myk_parry_hit',A,T,0)
 check('nested-preview-cannot-claim',call('ffta_action_unit_extension_flags',T),ready)
 call('ffta_snapshot_end',child)
 check('combo-exclusion',call('ffta_myk_parry_factor',A,T,265),2)
 check('self-exclusion',call('ffta_myk_parry_factor',T,T,0),2)
 call('ffta_snapshot_end',frame)

# Actual ally Fight still resolves natively, but cannot trigger Parry.
for seed in range(8):
 values=[]
 for parry in (False,True):
  case=('ally-execution',seed,parry);setup(0,seed,parry,'ally');execute(0)
  values.append((half(T+0x18),call('ffta_myk_enchantment',T)))
 check('ally-attack-preserves-damage-and-fuel',values[1],values[0])

report=dict(passed=not failures,romSha1=meta['romSha1'],assertions=sum(checks.values()),checks=dict(checks),
 nativeCasts=len(samples)*2+48,failures=failures,samples=samples,dual=dual)
(OUT/'mystic-knight-parry.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
assert not failures,('Mystic Parry failures',len(failures))
