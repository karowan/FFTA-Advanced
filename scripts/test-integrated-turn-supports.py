"""Native turn-support arithmetic, execution, frozen copies and exclusions."""
import pathlib,json,struct,itertools,collections,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-bard.py';ns={'__file__':str(source),'__name__':'turn_fixture'}
exec(compile(source.read_text().split('# Native command flags')[0],str(source),'exec'),ns)
m,S,meta,OUT,ACTOR,TARGET,CTX,STACK,regs=(ns[x] for x in ('m','S','meta','OUT','ACTOR','ENEMY','CTX','STACK','regs'))
setup,native_execute,call,job,hp,half,status=(ns[x] for x in ('setup','execute','call','job','hp','half','status'))
equip=ns['ns']['equip'];wrappers=ns['wrappers'];checks=collections.Counter();case=None;executions=0
def check(k,a,b):checks[k]+=1;assert a==b,(k,a,b,case)
def record(u):return call('ffta_job_state',u)
def execute(action):
 global executions
 result=native_execute(action);executions+=1;return result
def turn_setup(action,lesson,moved=0,enabled=True,seed=0):
 setup(action,seed)
 human=lesson=='SAM-S1'
 jobs={0:2,1:7,23:8,350:116,361:117} if human else {0:119,2:18,15:18,361:119,431:16}
 job(ACTOR,1 if human else 2,jobs.get(action,2 if human else 119))
 if enabled:equip(ACTOR,lesson)
 hp(ACTOR,200,500,99);hp(TARGET,100 if action in (1,2,350) else 500,500)
 m.put(TARGET+0x29,bytes((0 if action in (1,2,350) else 128,)))
 weapon=377 if action==350 else 399 if action==431 else 384 if action==361 or (not human and action==0) else 0 if action in (1,2,15,23) else 1
 m.put(ACTOR+0x2a,struct.pack('<5H',weapon,0,0,0,0))
 m.put(ACTOR+0xf6,bytes((4-moved,14)));call('ffta_turn_event',ACTOR,1)
 m.put(ACTOR+0xf6,bytes((4,14)))
 m.put(0x0200f4ec,struct.pack('<I',wrappers[ACTOR]))
 if moved:call('ffta_turn_flag',4,1,0x080968d3)

for lesson,moved,physical,raw in itertools.product(('SAM-S1','GLD-AX-S1'),range(3),(False,True),(1,3,17,99,511)):
 case=('damage factors',lesson,moved,physical,raw);action=0 if physical else 23;turn_setup(action,lesson,moved)
 factor=25 if lesson=='SAM-S1' and moved==0 else 27 if lesson=='GLD-AX-S1' and moved>=2 and physical else 20
 check('exact-damage-factor',call('ffta_turn_damage_numerator',ACTOR,TARGET,action,int(physical)),factor)
 check('single-final-round',call('ffta_integrated_exposed_native_stage',raw,CTX),min(999,raw*factor//20))

samples=[]
native_commands=[(lesson,action) for lesson,actions in (('SAM-S1',(0,1,23,350,361)),('GLD-AX-S1',(0,2,15,361,431))) for action in actions]
for (lesson,action),moved,enabled,seed in itertools.product(native_commands,range(3),(False,True),range(4)):
 # Racially legal commands: Human White/Iaido/Dark Arts; Bangaa Bishop,
 # Gladiator and Dark Arts. Murasame is Human-only.
 case=('native execution',lesson,action,moved,enabled,seed);turn_setup(action,lesson,moved,enabled,seed)
 execute(action);samples.append(dict(lesson=lesson,action=action,moved=moved,enabled=enabled,seed=seed,hp=half(TARGET+0x18)))
 check('one-payment',half(ACTOR+0x1c),99-m.call(0x0812ed98,ACTOR,action,stack=STACK))
 check('transient-roots-retired',m.read(0x0203ff44,8),bytes(8))
for x in (x for x in samples if x['enabled']):
 p=next(y for y in samples if all(x[k]==y[k] for k in ('lesson','action','moved','seed')) and not y['enabled'])
 qualifies=(x['lesson']=='SAM-S1' and x['moved']==0) or (x['lesson']=='GLD-AX-S1' and x['moved']==2 and x['action'] in (0,361,431))
 if not qualifies:check('unqualified-native-identical',x['hp'],p['hp'])
 elif x['action'] in (1,2,350):check('native-healing-improves',x['hp']>p['hp'],True)
 else:check('native-damage-never-decreases',x['hp']<=p['hp'],True)
check('Composure-native-positive',any(x['enabled'] and x['lesson']=='SAM-S1' and x['moved']==0 and x['action']==23 and x['hp']<next(y['hp'] for y in samples if not y['enabled'] and all(x[k]==y[k] for k in ('lesson','action','moved','seed'))) for x in samples),True)
check('Follow-Through-native-positive',any(x['enabled'] and x['lesson']=='GLD-AX-S1' and x['moved']==2 and x['action']==361 and x['hp']<next(y['hp'] for y in samples if not y['enabled'] and all(x[k]==y[k] for k in ('lesson','action','moved','seed'))) for x in samples),True)

for lesson,moved,caller,value in itertools.product(('SAM-S1','GLD-AX-S1'),range(3),(0x08095671,0x080937c3,0x0809674d,0x080968d3,0x08096343),(0,1)):
 case=('native flag callers',lesson,moved,caller,value);turn_setup(0,lesson,moved)
 before=m.read(record(ACTOR)+12,3);call('ffta_turn_flag',4,value,caller)
 expected=bytes((4-moved,14,(before[2]&248)|1)) if caller==0x08096343 and value==0 else bytes((4-moved,14,(before[2]&248)|3|(4 if moved>=2 else 0))) if caller==0x080968d3 and value==1 else before
 check('only-proven-move-and-undo',m.read(record(ACTOR)+12,3),expected)
 check('native-flag-operation-preserved',m.call(0x080c9540,4,stack=STACK),value)

for maximum,centered,recup in itertools.product((101,307,400,501),(False,True),(False,True)):
 case=('healing combined rounding',maximum,centered,recup);turn_setup(350,'SAM-S1');hp(TARGET,1,maximum)
 if centered:call('ffta_centered_grant',ACTOR,0)
 if recup:equip(TARGET,'SLD-AX-S1')
 expected=min(maximum-1,min(35*maximum,14000)*(5 if centered else 4)*(3 if recup else 2)*25//16000)
 check('Murasame-Centered-Composure-Recuperation',call('ffta_integrated_technique_healing',CTX),expected)
for action in (17,5,6,254,251):
 case=('non-restorative exclusions',action);turn_setup(action,'SAM-S1')
 check('drain-revival-MP-item-excluded',call('ffta_integrated_restoration_stage',-101&0xffffffff,CTX),-101&0xffffffff)

for lesson,moved in (('SAM-S1',0),('GLD-AX-S1',2)):
 for forced in (16,32):
  case=('forced exclusion',lesson,forced);turn_setup(23,lesson,moved);m.put(ACTOR+0xeb,bytes((forced,)))
  check('forced-factor-neutral',call('ffta_turn_damage_numerator',ACTOR,TARGET,23,1),20)
 for event in range(1,9):
  case=('lifecycle',lesson,event);turn_setup(0,lesson,moved);before=m.read(record(ACTOR),22)
  call('ffta_turn_event',ACTOR,event);after=m.read(record(ACTOR),22)
  other=lambda s:s[:12]+s[15:19]+bytes((s[19]&7,))+s[20:]
  check('other-jobs-owned-bytes-preserved',other(after),other(before))
  expected=bytes((4,14,1|((m.call(0x080ca394,ACTOR,stack=STACK)&31)<<3))) if event==1 else bytes(3) if event<=5 else before[12:15]
  check('exact-lifecycle',after[12:15],expected)
  if event==1:
   allowance=m.call(0x080ca394,ACTOR,stack=STACK)
   check('native-original-allowance',call('ffta_turn_original_allowance',ACTOR),allowance)
   check('native-initial-step-cap',call('ffta_turn_step_remaining',ACTOR),min(2,allowance))
  elif event<=5:
   check('cleared-movement-ledger',after[19]&248,0)
 case=('snapshot remains action-start',lesson);turn_setup(0,lesson,moved)
 frame,copy=0x03007500,0x02028000;call('ffta_snapshot_begin',frame,ACTOR,TARGET,1);call('ffta_action_started',ACTOR,0,1,1)
 expected=25 if lesson=='SAM-S1' else 27
 call('ffta_turn_end',ACTOR);m.put(copy,m.read(ACTOR,264));call('ffta_snapshot_copy',copy,ACTOR)
 check('later-movement-cannot-change-current-action',call('ffta_turn_damage_numerator',ACTOR,TARGET,0,1),expected)
 check('exact-copy-retains-current-action',call('ffta_turn_damage_numerator',copy,TARGET,0,1),expected)
 call('ffta_snapshot_end',frame);check('next-action-sees-end-turn',call('ffta_turn_damage_numerator',ACTOR,TARGET,0,1),20)
 # Reactions and explicit Combos cannot borrow either own-turn bonus.
 for category in (2,3):
  turn_setup(0,lesson,moved);call('ffta_snapshot_begin',frame,ACTOR,TARGET,1);call('ffta_action_started',ACTOR,0,category,1)
  check('reaction-combo-origin-excluded',call('ffta_turn_damage_numerator',ACTOR,TARGET,0,1),20);call('ffta_snapshot_end',frame)
 check('Combo-action-id-excluded',call('ffta_turn_damage_numerator',ACTOR,TARGET,265,1),20)

# Actual native Combo contribution formula, with both native stack residues.
# This verifies damage computation, not the full JP/menu/animation sequence.
combo_positive=0
for lesson,moved,strength,residue in itertools.product(('SAM-S1','GLD-AX-S1'),range(3),(5,20),(0,4)):
 case=('native Combo contribution',lesson,moved,strength,residue);values=[]
 for enabled in (False,True):
  turn_setup(0,lesson,moved,enabled)
  values.append(m.call(0x08130454,ACTOR,TARGET,strength,stack=STACK+residue))
  check('Combo-query-roots-retired',m.read(0x0203ff44,8),bytes(8))
 check('native-Combo-support-excluded',values[1],values[0])
 combo_positive+=int(values[0]>0)
 # Ended/off-turn contributors get no movement support bonus.
 call('ffta_turn_end',ACTOR)
 check('off-turn-Combo-no-bonus',m.call(0x08130454,ACTOR,TARGET,strength,stack=STACK+residue),values[0])
check('native-Combo-positive-control',combo_positive>0,True)

report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),nativeExecutions=executions,samples=samples,
 limits=['Actual movement and undo use the separate turn-admission replay. Prospective AI moved-tile scoring and complete law/AP/acquisition/Combo playback remain separate acceptance.'])
(OUT/'turn-supports-native.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
# Execute the native help decoder against the two new descriptions and every
# preexisting route/text using the image immediately before this help patch.
if '--combat-only' not in sys.argv:
 help_source=(ROOT/'scripts/test-samurai-help.py').read_text()
 help_source=help_source.replace("P/'samurai/current.json'","P/'integrated-jobs/current.json'")
 help_source=help_source.replace("help=meta['help']","help=meta['help']['turn']")
 help_source=help_source.replace("ROM.parent/'input.gba'","ROM.parent.parent/'turn-help-input.gba'")
 help_source=help_source.replace("ROM.parent/'help-tests.json'","ROM.parent/'turn-help-tests.json'")
 exec(compile(help_source,'<native turn support help>','exec'),{'__file__':__file__,'__name__':'turn_help'})
