"""Magic Shell native execution/forecast controls, fixed inputs and seeds.

Ordinary native Shell is the independent damage/timer oracle. Hooks observe
successful descriptors and Shell setters only; they never change execution.
Whole Doublecast and rendered reaction feedback have separate release gates.
"""
import pathlib,json,struct,itertools,collections,argparse
parser=argparse.ArgumentParser()
parser.add_argument('--section',choices=('all','lifecycle'),default='all')
section=parser.parse_args().section
core=section=='all'
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-mystic-knight-commands.py'
ns={'__file__':str(source),'__name__':'mystic_shell_fixture'}
exec(compile(source.read_text().split('# Native casts cover')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,C,STACK,call,half,fixture,grant,execute,equip,record=(ns[x] for x in
 ('m','S','meta','OUT','A','T','C','STACK','call','half','fixture','grant','execute','equip','record'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1
checks=collections.Counter();failures=[];samples=[];case=None;hits=[];grants=[];casts=0;pending=None

def check(k,a,b):
 checks[k]+=1
 if a!=b:failures.append(dict(case=case,check=k,actual=repr(a),expected=repr(b)))

def observe_hit(u,pc,size,data):
 global pending
 c=u.reg_read(UC_ARM_REG_R0)
 hits.append((half(c+12),int.from_bytes(m.read(c+8,4),'little')))
 pending=(m.read(C,0x34),m.read(0x030034b0,4))

def observe_formula(u,pc,size,data):
 global pending
 if pending:
  check('hit-forecast-restores-native-context-and-RNG',(m.read(C,0x34),m.read(0x030034b0,4)),pending)
  pending=None

def observe_grant(u,pc,size,data):
 if u.reg_read(UC_ARM_REG_R0)==T and u.reg_read(UC_ARM_REG_R1):grants.append(1)

p=S['ffta_myk_shell_hit'];m.u.hook_add(UC_HOOK_CODE,observe_hit,begin=p,end=p)
m.u.hook_add(UC_HOOK_CODE,observe_grant,begin=0x080ce070,end=0x080ce070)
p=S['ffta_samurai_magnitude'];m.u.hook_add(UC_HOOK_CODE,observe_formula,begin=p,end=p)

def shell(u):
 m.call(0x080ce070,u,1,stack=STACK);m.call(0x080ce440,u,3,stack=STACK)

def setup(action,seed,hp=300,condition='normal',reaction=False,existing=False):
 global pending
 pending=None
 fixture(action,seed);m.put(T+0x18,struct.pack('<H',hp))
 if reaction:equip(T,'MYK-R1')
 if action==422:call('ffta_myk_grant',A,1)
 if condition=='ally':m.put(T+0x29,b'\0')
 if condition=='petrify':grant(T,6)
 if condition=='immune':m.put(T+0x0d,b'\x02')
 if condition=='absorb':m.put(T+0x0d,b'\x03')
 if condition=='ward':equip(T,'MYK-S2')
 if condition=='barrier':call('ffta_drk_grant_tbn',T,T)
 if existing:shell(T)
 hits.clear();grants.clear()

def preview(action,residue=0):
 m.put(STACK+residue,struct.pack('<2I',0,2))
 value=m.call(0x08130200,A,T,action,88,stack=STACK+residue)
 return value if value<0x80000000 else value-0x100000000

def run(action):
 global casts
 execute(action);casts+=1
 return dict(hp=half(T+0x18),mp=half(T+0x1c),shell=bool(m.read(T+0xeb,1)[0]&1),
  statuses=m.read(T+0xe8,8).hex(),timer=m.read(T+0xdd,1)[0],rng=m.read(0x030034b0,4).hex(),hits=list(hits),grants=len(grants))

# Vary threshold, fixed hit/miss seeds, original/new magical damage, physical,
# status-only and MP-only actions. A forecast does not constitute a hit.
for action,hp,seed,condition in (itertools.product((23,422,410,423,402),(180,300,500),range(4),('normal','ally','immune','absorb','ward','barrier')) if core else ()):
 case=('native',action,hp,seed,condition)
 setup(action,seed,hp,condition);raw=preview(action);base=run(action)
 successful=(action,T) in base['hits']
 expected=successful and condition!='ally' and raw>0 and 2*(hp-raw)<=500
 setup(action,seed,hp,condition,existing=expected);control=run(action)
 setup(action,seed,hp,condition,reaction=True);actual=run(action)
 check('native-Shell-trigger',actual['shell'],expected)
 check('native-Shell-damage-oracle',actual['hp'],control['hp'])
 check('native-Shell-MP-unchanged',actual['mp'],control['mp'])
 check('single-actual-grant',actual['grants'],int(expected))
 check('native-Shell-timer',actual['timer'],control['timer'])
 check('forecast-does-not-consume-RNG',actual['rng'],base['rng'])
 check('native-snapshot-roots-retired',m.read(0x0203ff44,8),bytes(8))
 samples.append(dict(action=action,hp=hp,seed=seed,condition=condition,forecast=raw,expected=expected,base=base,actual=actual,control=control))
if core:
 check('nonvacuous-Shell-activation',any(s['expected'] for s in samples),True)
 check('nonvacuous-low-threshold-no-activation',any(s['action']==23 and s['condition']=='normal' and s['actual']['hits'] and not s['expected'] for s in samples),True)
 check('nonvacuous-miss',any(s['action']==422 and not s['actual']['hits'] for s in samples),True)
 check('nonvacuous-damage-reduction',any(s['actual']['hp']>s['base']['hp'] and s['expected'] for s in samples),True)

# Already-Shelled units retain the ordinary damage and timer; no refresh.
for action,seed in (itertools.product((23,422),range(8)) if core else ()):
 case=('existing-Shell',action,seed);pair=[]
 for reaction in (False,True):
  setup(action,seed,180,reaction=reaction,existing=True)
  m.call(0x080ce440,T,1,stack=STACK)
  pair.append(run(action))
 check('existing-Shell-native-result',pair[1],pair[0])

# Read-only menu/AI damage queries use an owned copy. Original units, saved
# extension records, RNG and current action ownership remain untouched.
for action,hp,condition,residue in (itertools.product((23,422,410,423,402),(180,300,500),('normal','ally','petrify','immune','absorb','ward','barrier'),(0,4)) if core else ()):
 case=('preview',action,hp,condition,residue)
 setup(action,0,hp,condition);raw=preview(action,residue)
 eligible=action in (23,422) and condition not in ('ally','petrify') and raw>0 and 2*(hp-raw)<=500
 setup(action,0,hp,condition,existing=eligible);control=preview(action,residue)
 setup(action,0,hp,condition,reaction=True)
 before=m.read(A,264)+m.read(T,264)+m.read(record(A),22)+m.read(record(T),22);rng=m.read(0x030034b0,4)
 actual=preview(action,residue)
 check('preview-native-Shell-oracle',actual,control)
 check('preview-preserves-units-and-owned-state',m.read(A,264)+m.read(T,264)+m.read(record(A),22)+m.read(record(T),22),before)
 check('preview-preserves-RNG',m.read(0x030034b0,4),rng)
 check('preview-no-live-grant',grants,[])
 check('preview-roots-retired',m.read(0x0203ff44,8),bytes(8))

# Threshold equality and adjacent HP values derive from the independent raw
# native forecast, not from the implementation's threshold helper.
for action in ((23,422) if core else ()):
 setup(action,0);raw=preview(action)
 for offset in (-1,0,1):
  hp=min(500,250+raw+offset);case=('threshold-boundary',action,hp,raw,offset)
  setup(action,0,hp,existing=hp-raw<=250 and raw>0);control=preview(action)
  setup(action,0,hp,reaction=True);check('exact-half-boundary',preview(action),control)

# Legal Viera main-job mixing, removal and subsequent incoming actions.
# A native magical hit is guaranteed by retaining the observed seed1 fixture,
# not by overwriting its accuracy or outcome.
for job in (27,29,125):
 case=('legal-main-job',job);setup(23,1,180,reaction=True);ns['job'](T,4,job)
 before=m.read(record(T),22);first=run(23)
 check('legal-job-Shell-trigger',first['shell'],True)
 check('ordinary-Shell-three-turn-timer',first['timer'],3)
 check('Shell-no-private-save-writes',m.read(record(T),22),before)
 check('native-Dispel-removes-Shell',call('ffta_myk_dispel',T,7),1)
 check('native-Dispel-clears-timer',m.read(T+0xdd,1),b'\0')
 m.put(T+0x18,struct.pack('<H',180));m.put(0x030034b0,struct.pack('<I',1));hits.clear();grants.clear()
 second=run(23)
 check('no-cross-action-lock',second['shell'],True)
 check('later-action-single-grant',second['grants'],1)

# Native reaction capability, not guessed translated status names. Existing
# Shell has its separate preservation rule; all other bits use native mask5.
for bit in range(44):
 case=('native-status-mask',bit);setup(23,0,180);grant(T,bit)
 raw=preview(23)
 capable=not m.call(0x080c8280,T,stack=STACK) and bool(m.call(0x08133adc,T+0xe8,5,stack=STACK)) and not bool(m.read(T+0xe8,1)[0]&64)
 setup(23,0,180,existing=capable and bit!=24 and raw>0);grant(T,bit);control=preview(23)
 setup(23,0,180,reaction=True);grant(T,bit)
 check('native-capability-preview',preview(23),control)

# Read-only scopes inherit origin and the engine's independent permission.
frame=0x03007500
for origin,permission in itertools.product((0,1,2,3),(0,1)):
 case=('scope-exclusions',origin,permission);setup(23,0,180);raw=preview(23)
 setup(23,0,180,existing=True);protected=preview(23)
 setup(23,0,180,reaction=True)
 check('scope-opens',call('ffta_snapshot_begin',frame,A,T,1),1)
 call('ffta_action_started',A,23,origin,2);m.put(frame+16,struct.pack('<I',permission))
 check('scope-forecast-exclusions',preview(23),protected if permission and origin in (0,1) else raw)
 before=m.read(T,264)+m.read(record(T),22)
 call('ffta_myk_shell_hit',C)
 check('query-or-executing-cannot-grant',m.read(T,264)+m.read(record(T),22),before)
 call('ffta_snapshot_end',frame)

report=dict(passed=not failures,section=section,romSha1=meta['romSha1'],assertions=sum(checks.values()),checks=dict(checks),nativeCasts=casts,failures=failures,samples=samples)
(OUT/('mystic-knight-shell'+('' if core else '-lifecycle')+'.json')).write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
assert not failures,('Mystic Shell failures',len(failures))
