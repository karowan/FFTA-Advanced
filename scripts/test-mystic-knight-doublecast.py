"""Fixed native Doublecast call-site slices and real subcast constructors.

Inputs supply the captured native controller ABI, chosen spells and targets.
The actual controller BL, full native constructors/executors and completion
hook run untouched. This is not full frame-driven menu/animation acceptance.
"""
import pathlib,json,struct,itertools,collections,argparse
parser=argparse.ArgumentParser()
parser.add_argument('--section',choices=('all','lifecycle'),default='all')
section=parser.parse_args().section
core=section=='all'
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-mystic-knight-commands.py'
ns={'__file__':str(source),'__name__':'doublecast_fixture'}
exec(compile(source.read_text().split('# Native casts cover')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,C,STACK,call,half,fixture,equip,record=(ns[x] for x in
 ('m','S','meta','OUT','A','T','C','STACK','call','half','fixture','equip','record'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
wrappers=ns['wrappers'];B=0x0200f4e8;SP=0x03007100
checks=collections.Counter();failures=[];samples=[];case=None;grants=[];executions=[]

def check(k,a,b):
 checks[k]+=1
 if a!=b:failures.append(dict(case=case,check=k,actual=repr(a),expected=repr(b)))

def w(p,v):m.put(p,struct.pack('<I',v))
def h(p,v):m.put(p,struct.pack('<H',v))
def setup(spells=(23,23),previous=1,seed=1,shell=False):
 fixture(spells[0],seed);ns['job'](A,4,29)
 h(A+0x18,500);h(T+0x18,180 if shell else 500)
 if previous>=0:equip(A,'MYK-S1');h(record(A)+20,previous<<13)
 if shell:equip(T,'MYK-R1')
 w(B+4,wrappers[A]);h(B+0xa6,33);h(B+0xa8,0)
 h(B+0xaa,spells[0]);h(B+0xac,spells[1]);m.put(B+0xaf,b'\0')
 m.put(B+0xcb,bytes((5,5,14,14)));w(B+0xd0,0)
 grants.clear();executions.clear()

def grant_observer(u,pc,size,data):
 if u.reg_read(UC_ARM_REG_R0)==T and u.reg_read(UC_ARM_REG_R1):grants.append(1)
def executor_observer(u,pc,size,data):
 executions.append((m.read(B+0xaf,1)[0],half(u.reg_read(UC_ARM_REG_SP))))
m.u.hook_add(UC_HOOK_CODE,grant_observer,begin=0x080ce070,end=0x080ce070)
m.u.hook_add(UC_HOOK_CODE,executor_observer,begin=0x080a433c,end=0x080a433c)

def native_slice(start,end,residue=0):
 m.u.reg_write(UC_ARM_REG_SP,SP+residue)
 m.u.reg_write(UC_ARM_REG_R8,B);m.u.reg_write(UC_ARM_REG_R9,B+0xd0)
 m.u.reg_write(UC_ARM_REG_R6,wrappers[A]);m.u.reg_write(UC_ARM_REG_R7,B+0xdc)
 m.u.reg_write(UC_ARM_REG_LR,0x08096b15)
 try:m.u.emu_start(start|1,end,count=3000000)
 except Exception:
  print(json.dumps(dict(nativeSlice=hex(start),pc=hex(m.u.reg_read(UC_ARM_REG_PC)),
   sp=hex(m.u.reg_read(UC_ARM_REG_SP)),lr=hex(m.u.reg_read(UC_ARM_REG_LR)),
   regs=[hex(m.u.reg_read(r)) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7)])))
  raise
 check('native-slice-reaches-original-continuation',m.u.reg_read(UC_ARM_REG_PC),end)
 check('native-slice-preserves-SP',m.u.reg_read(UC_ARM_REG_SP),SP+residue)
 return m.u.reg_read(UC_ARM_REG_R0)

def cast(index,residue=0):
 m.put(B+0xaf,bytes((index,)))
 output=native_slice(0x08095b18,0x08095b64,residue)
 w(B+0x4c+index*4,output)
 return output

def finish(residue=0):
 native_slice(0x08095d66,0x08095d72,residue)

def slot():return call('ffta_battle_workspace',0x2610)

def dispose(outputs):
 for output in outputs:
  if output:m.call(0x08022854,output,stack=STACK)

# Compare every register/flag and the phase write with the exact original
# displaced span. The independent control changes only those12 ROM bytes;
# neither side receives injected register/results while executing.
original=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()[0x95d66:0x95d72]
installed=m.read(0x08095d66,12)
cpu=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,
 UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,
 UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12,UC_ARM_REG_SP,
 UC_ARM_REG_LR,UC_ARM_REG_CPSR)
for residue,flags in itertools.product((0,4),(0x0000003f,0xf000003f)):
 case=('completion-hook-native-ABI',residue,flags);pair=[]
 for span in (original,installed):
  setup();m.put(0x08095d66,span)
  # Flush translated instructions when switching the isolated native control.
  m.u.ctl_remove_cache(0x08095d66,0x08095d72)
  for i,r in enumerate(cpu[:13]):m.u.reg_write(r,0x55110000+i)
  m.u.reg_write(UC_ARM_REG_CPSR,flags)
  native_slice(0x08095d66,0x08095d72,residue)
  pair.append(([m.u.reg_read(r) for r in cpu],half(B+0xdc)))
 check('completion-hook-exact-native-registers-and-flags',pair[1],pair[0])

# Each subcast is a real independent native transaction. The old category
# remains visible throughout both; only the outer finish publishes Magic.
for spells,previous,seed,residue in (itertools.product(((23,23),(23,1),(1,23)),(0,1,2),range(3),(0,4)) if core else ()):
 case=('native-pair',spells,previous,seed,residue);setup(spells,previous,seed)
 before_mp=half(A+0x1c);outputs=[];health=[]
 for i in (0,1):
  outputs.append(cast(i,residue));health.append(half(T+0x18))
  check('sequence-not-committed-between-subcasts',call('ffta_myk_sequence',A),previous)
  check('no-active-snapshot-between-ticks',m.read(0x0203ff44,8),bytes(8))
  s=slot();p=m.word(s+4)
  check('owned-continuation-exists',bool(p),True)
  check('continuation-not-an-active-stack-snapshot',m.word(p+24),0)
 finish(residue)
 check('one-final-Magic-category',call('ffta_myk_sequence',A),2)
 check('two-original-native-executors',executions,[(0,spells[0]),(1,spells[1])])
 check('native-cost-for-both-spells',before_mp-half(A+0x1c),12) # Original Cure/Fire are6 MP each.
 check('outer-completion-retires-buffer',m.read(slot(),16),bytes(16))
 samples.append(dict(spells=spells,previous=previous,seed=seed,residue=residue,health=health,mp=half(A+0x1c)))
 dispose(outputs)

# Independent no-support controls establish the exact original damage for
# each subcast. Spellweave's final rational multiplier applies to BOTH spells.
for seed in (range(4) if core else ()):
 values=[]
 for previous in (-1,1,2):
  case=('both-damage-bonuses',seed,previous);setup(previous=previous,seed=seed)
  damage=[];outputs=[]
  for i in (0,1):
   before=half(T+0x18);outputs.append(cast(i));damage.append(before-half(T+0x18))
  finish();values.append(damage);dispose(outputs)
 check('both-native-spells-get-alternation',values[1],[v*27//20 for v in values[0]])
 check('same-category-has-no-bonus',values[2],values[0])

# First-cast opportunity persists even if Shell is dispelled between ticks;
# a fresh subsequent Doublecast gets a fresh opportunity. Removal here is a
# declared boundary input, not an injected hit or altered spell outcome.
for residue in ((0,4) if core else ()):
 case=('Shell-once-per-Doublecast',residue);setup(previous=1,shell=True)
 first=cast(0,residue);check('first-spell-Shell',bool(m.read(T+0xeb,1)[0]&1),True)
 call('ffta_myk_dispel',T,7);h(T+0x18,180);w(0x030034b0,1)
 second=cast(1,residue)
 check('second-spell-cannot-repeat-Shell',bool(m.read(T+0xeb,1)[0]&1),False)
 check('one-Shell-grant',len(grants),1)
 finish(residue);dispose((first,second))
 # Keep the same live scene and actor to reject a cross-action lock.
 h(A+0x18,500);h(A+0x1c,99);h(T+0x18,180);w(0x030034b0,1)
 third=cast(0,residue);check('new-Doublecast-can-trigger-again',bool(m.read(T+0xeb,1)[0]&1),True)
 finish(residue);dispose((third,))

# Native cancellation reaches the same finish hook after just one subcast.
# KO/Petrify lifecycle clears must not be resurrected by delayed commitment.
for cancel in (('second-cancelled','KO','Petrify','support-removed','actor-replaced') if core else ()):
 case=('cancel',cancel);setup();first=cast(0)
 if cancel=='KO':h(A+0x18,0);call('ffta_myk_event',A,2)
 if cancel=='Petrify':ns['grant'](A,6);call('ffta_myk_event',A,3)
 if cancel=='support-removed':m.put(A+0x3b,b'\0');call('ffta_myk_event',A,8)
 if cancel=='actor-replaced':w(B+4,wrappers[T])
 finish()
 wanted=2 if cancel=='second-cancelled' else 1 if cancel=='actor-replaced' else 0
 check('cancellation-no-stale-sequence',call('ffta_myk_sequence',A),wanted)
 check('cancellation-frees-owner',m.read(slot(),16),bytes(16));dispose((first,))

# Native teardown must release the optional continuation as well as the pool,
# including when the whole manager is freed while an action is unfinished.
for owner in ('pool','manager','explicit'):
 case=('owner-retirement',owner);setup();first=cast(0)
 s=slot();p=m.word(s+4);manager=m.word(0x0200f4b0);pool=m.word(manager+0x438)
 check('continuation-native-allocation',half(p-8),0x616c)
 if owner=='explicit':call('ffta_myk_doublecast_retire')
 else:m.call(0x08022854,pool if owner=='pool' else manager,stack=STACK)
 check('continuation-released-with-owner',half(p-8)!=0x616c,True)
 check('retired-continuation-cannot-commit',call('ffta_myk_sequence',A),1)
 if owner=='explicit':check('explicit-retirement-clears-slot',m.read(s,16),bytes(16))
 else:check('retired-pool-not-exposed',slot(),0)

# Insufficient second payment preserves the completed first category. A pair
# with no committed spell preserves its old category and retires its owner.
for mp,wanted in ((0,1),(6,2)):
 case=('native-payment-cancellation',mp);setup();h(A+0x1c,mp)
 outputs=[cast(0),cast(1)];finish()
 check('only-real-paid-subcasts-commit',call('ffta_myk_sequence',A),wanted)
 check('no-free-second-cast',half(A+0x1c),0)
 check('payment-cancel-retires-owner',m.read(slot(),16),bytes(16));dispose(outputs)

# Defensive malformed-selection contract: native UI cannot select Fight for
# Doublecast, but an ambiguous physical/magical pair must clear, not turn the
# final physical subcast into a retained Magic bonus. This does not grant UI
# access to an ineligible action.
case=('mixed-category-negative',);setup((23,0));outputs=[cast(0),cast(1)];finish()
check('mixed-category-clears-sequence',call('ffta_myk_sequence',A),0);dispose(outputs)
for action in range(347,432):
 check('new-action-remains-ineligible-for-Doublecast',m.call(0x080ccd50,action,19,stack=STACK),0)

report=dict(passed=not failures,section=section,romSha1=meta['romSha1'],assertions=sum(checks.values()),checks=dict(checks),failures=failures,samples=samples,
 scope=__doc__,limits=['Full controller ticks/menu/animation and non-Mystic outer-action reaction aggregation remain separate gates.'])
(OUT/('mystic-knight-doublecast'+('' if core else '-lifecycle')+'.json')).write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
assert not failures,('Mystic Doublecast failures',len(failures))
