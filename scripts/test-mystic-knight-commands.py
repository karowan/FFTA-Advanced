"""Fixed native Mystic command matrix; no injected hit, damage or paid result.

This accepts command behavior separately from the still unfinished enchanted
Fight, defensive reactions, whole Doublecast and player/AI playback.
"""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-dancer.py'
ns={'__file__':str(source),'__name__':'mystic_command_fixture'}
exec(compile(source.read_text().split('# The two separate native formula terms')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,C,STACK,regs,call,equip,half,job,hp,record=(ns[x] for x in
 ('m','S','meta','OUT','A','T','C','STACK','regs','call','equip','half','job','hp','record'))
wrappers=ns['ns']['wrappers'];counts=collections.Counter();failures=[];samples=[];case=None
costs=dict(zip(range(410,424),(6,6,6,6,10,8,12,20,12,8,12,10,14,24)))
def check(k,a,b):
 counts[k]+=1
 if a!=b:failures.append(dict(check=k,actual=repr(a),expected=repr(b),case=case))
def fixture(action,seed=0):
 ns['fixture'](action,weapon=88,seed=seed);job(A,4,125);job(T,4,125)
 m.put(record(A),bytes(22));m.put(record(T),bytes(22));m.put(T+0x2a,struct.pack('<H',88))
def bit(u,b):return bool(m.read(u+0xe8+b//8,1)[0]&(1<<(b%8)))
def grant(u,b):
 m.put(u+0xe8+b//8,bytes((m.read(u+0xe8+b//8,1)[0]|(1<<(b%8)),)))
def execute(action,self_target=False,choice=0):
 m.put(regs[13],struct.pack('<4I',action,choice,0,255))
 return m.call(0x080a433c,regs[0],wrappers[A],4 if self_target else 5,14,stack=regs[13])

# Native casts cover all commands, misses retained, exact single payment and
# self modes. The first enchant must not empower its own attempt.
for action,seed,self_target in itertools.product(range(410,424),range(8),(False,True)):
 if self_target and action>420:continue
 case=('native-command',action,seed,self_target);fixture(action,seed)
 equip(A,'MYK-S1');call('ffta_myk_grant',A,3)
 if action==421:grant(T,25)
 if action==422:call('ffta_myk_grant',A,1 if seed%2 else 8)
 before=(half(A+0x18),half(A+0x1c),half(T+0x18),half(T+0x1c))
 execute(action,self_target,8 if action==421 else 0)
 after=(half(A+0x18),half(A+0x1c),half(T+0x18),half(T+0x1c))
 loss=before[2]-after[2];mp_loss=before[3]-after[3]
 expected_mp=costs[action]-(mp_loss if action==419 else 0)
 check('single-native-MP-payment',before[1]-after[1],expected_mp)
 if action<=420:check('grants-even-when-strike-misses',call('ffta_myk_enchantment',A),action-409)
 if self_target:
  check('self-no-HP-damage',after[0],before[0]);check('self-no-opponent-effect',after[2:],before[2:])
 elif action==416:check('Drain-actual-loss-and-cap',after[0]-before[0],min(max(0,loss)*35//100,75))
 elif action==419:check('Osmose-actual-loss-and-cap',mp_loss,min(max(0,loss)//4,10,before[3]))
 if action==421:
  check('Spellbreak-preserves-enchant',call('ffta_myk_enchantment',A),3)
  if loss>0:check('Spellbreak-removes-selected-Protect',bit(T,25),False)
 if action==422:check('Release-consumes-on-committed-miss',call('ffta_myk_enchantment',A),0)
 if action==423:
  check('Break-no-preliminary-damage',loss,0);check('Break-preserves-enchant',call('ffta_myk_enchantment',A),3)
 check('one-sequence-category',call('ffta_myk_sequence',A),1 if action==421 else 2)
 check('native-snapshot-roots-retired',m.read(0x0203ff44,8),bytes(8))
 samples.append(dict(action=action,seed=seed,self=self_target,loss=loss,mpLoss=mp_loss,
   statuses=[b for b in (6,9,22,26,27) if bit(T,b)],before=before,after=after))
for action in range(410,423):check('nonvacuous-damage-'+str(action),any(x['action']==action and x['loss']>0 for x in samples),True)
for action,b in ((413,9),(414,26),(415,27),(418,22),(423,6)):
 check('nonvacuous-native-status-'+str(action),any(x['action']==action and b in x['statuses'] for x in samples),True)
for action in range(410,424):
 for flag in (18,19,26):check('no-Reflect-Return-Magic-Doublecast',m.call(0x080ccd50,action,flag,stack=STACK),0)

# Actual recipient HP loss drives the resource rider; high power, overkill,
# nearly-full users and MP-starved targets exercise both independent caps.
resource_casts=0
for action,current_hp,current_mp,target_hp,target_mp,seed in itertools.product((416,419),(100,490),(20,99),(1,500),(0,5,99),(0,3)):
 case=('resource-boundaries',action,current_hp,current_mp,target_hp,target_mp,seed);fixture(action,seed)
 hp(A,current_hp,500,current_mp);hp(T,target_hp,500,target_mp)
 m.put(A+0x20,struct.pack('<H',240));execute(action);resource_casts+=1
 removed=max(0,target_hp-half(T+0x18))
 if action==416:
  check('Drain-overkill-cap-and-missing-HP',half(A+0x18)-current_hp,min(removed*35//100,75,500-current_hp))
  check('Drain-cannot-siphon-MP',half(T+0x1c),target_mp)
  check('Drain-exact-command-cost',half(A+0x1c),current_mp-12)
 else:
  siphoned=min(removed//4,10,target_mp)
  check('Osmose-target-limited-loss',target_mp-half(T+0x1c),siphoned)
  check('Osmose-user-missing-cap',half(A+0x1c),min(100,current_mp-8+siphoned))
  check('Osmose-no-HP-recovery',half(A+0x18),current_hp)

# Rejected commitments cannot debit MP, change the prepared blade, or earn a
# sequence. These use the installed native executor and its real payment gate.
for action,why in itertools.product(range(410,424),('silenced','wrong-weapon')):
 case=('invalid-commit',action,why);fixture(action);call('ffta_myk_grant',A,1)
 if why=='silenced':m.put(A+0xeb,b'\x08')
 else:m.put(A+0x2a,struct.pack('<H',1))
 if action==421:grant(T,25)
 before=m.read(record(A),22);execute(action,choice=8)
 check('invalid-commit-no-cost',half(A+0x1c),99)
 check('invalid-commit-no-state-change',m.read(record(A),22),before)
for choice in (0,1,8,21,22,65535):
 case=('no-selected-buff',choice);fixture(421);call('ffta_myk_grant',A,3);before=m.read(record(A),22)
 execute(421,choice=choice)
 check('absent-choice-no-cost',half(A+0x1c),99);check('absent-choice-no-damage',half(T+0x18),500)
 check('absent-choice-no-sequence',m.read(record(A),22),before)
for blade in (0,4,5,6,7,9,10):
 case=('invalid-release-kind',blade);fixture(422)
 if blade:call('ffta_myk_grant',A,blade)
 before=m.read(record(A),22);execute(422)
 check('invalid-Release-no-cost',half(A+0x1c),99);check('invalid-Release-preserves-state',m.read(record(A),22),before)

# Context forecasts leave original units, their owned effects and RNG intact.
# Spellbreak removes only the selected defense on its independent copy.
for selected in (7,8,11,14,15,21):
 case=('dispel-prediction',selected);fixture(421);grant(T,24);grant(T,25)
 call('ffta_drk_grant_tbn',T,T);m.put(record(T)+10,b'\x12');call('ffta_myk_grant',T,8)
 m.put(C+14,struct.pack('<H',selected));m.put(C+0x26,b'\x10')
 before=m.read(A,264)+m.read(T,264)+m.read(record(A),22)+m.read(record(T),22)
 rng=m.read(0x030034b0,4);call('ffta_myk_eligibility',C)
 check('admission-RNG-pure',m.read(0x030034b0,4),rng)
 check('nonvacuous-native-forecast',call('ffta_myk_magnitude',C)>0,True)
 check('forecast-preserves-original-owned-units',m.read(A,264)+m.read(T,264)+m.read(record(A),22)+m.read(record(T),22),before)

# The installed native status-law evaluator receives an explicitly owned copy,
# removes only the selected protection and never writes the original defender.
for selected,status,removal,residue in itertools.product((7,8),(24,25),(0,1),(0,4)):
 case=('native-selected-status-law',selected,status,removal,residue);fixture(421);grant(T,24);grant(T,25)
 copy=0x03007500;check('law-copy-opens',call('ffta_snapshotted_evaluated_init',copy,T),1)
 before=m.read(A,264)+m.read(T,264)+m.read(record(T),22)
 m.put(STACK+residue,struct.pack('<2I',status,removal))
 result=m.call(0x081342cc,A,copy,421,selected,stack=STACK+residue)
 check('native-law-exact-selected-removal',result,int(bool(removal) and status==selected+17))
 check('native-law-original-unit-isolation',m.read(A,264)+m.read(T,264)+m.read(record(T),22),before)
 call('ffta_snapshotted_evaluated_close',copy)

# All original native fields remain authoritative; self-enchantment uses Sure
# and the enemy uses A. Break uses one S descriptor, not an extra A check.
for action,weapon,silenced,own,friendly in itertools.product(range(410,424),(0,1,35,74,88,416),(False,True),(False,True),(False,True)):
 case=('admission',action,weapon,silenced,own,friendly);fixture(action)
 m.put(A+0x2a,struct.pack('<H',weapon));target=A if own else T
 m.put(C+4,struct.pack('<II',target,target))
 if friendly and not own:m.put(T+0x29,b'\0')
 if silenced:m.put(A+0xeb,b'\x08')
 if action==421:grant(T,25);m.put(C+14,struct.pack('<H',8))
 if action==422:call('ffta_myk_grant',A,1)
 wanted=weapon in (35,88,416) and not silenced and (not own if action==422 else (own or not friendly) if action<=420 else not own and not friendly)
 check('complete-admission-matrix',bool(call('ffta_myk_eligibility',C)),wanted)

# Each choice is stable and clears just its owned effect. Native harmful bits,
# equipment and unrelated job fields survive. Invalid/absent choices do nothing.
native=(2,3,4,5,12,21,24,25)
for choice in range(1,22):
 case=('selected-dispel',choice);fixture(421);p=record(T)
 grant(T,9);grant(T,22)
 if choice<=8:grant(T,native[choice-1])
 elif choice==9:call('ffta_centered_grant',T,0)
 elif choice==10:call('ffta_drk_grant_last_resort',T,0)
 elif choice==11:call('ffta_drk_grant_tbn',T,T)
 elif choice==12:call('ffta_viking_grant_war_cry',T,0)
 elif choice==13:call('ffta_inoculated_grant',T,0)
 elif choice in (14,15):m.put(p+10,bytes((2 if choice==14 else 16,)))
 elif choice==16:job(T,5,123);equip(T,'BRD-R1');m.put(p+11,b'\x01')
 elif choice==17:equip(T,'DNC-R1');m.put(p+3,b'\x40')
 elif choice in (18,19):m.put(p+18,bytes((4 if choice==18 else 32,)))
 elif choice==20:m.put(p+19,b'\x02')
 else:call('ffta_myk_grant',T,8)
 before=m.read(T,264);check('choice-present',call('ffta_myk_dispellable',T,choice),1)
 check('selected-effect-removed',call('ffta_myk_dispel',T,choice),1)
 check('choice-absent-after-removal',call('ffta_myk_dispellable',T,choice),0)
 check('Poison-preserved',bit(T,9),True);check('Slow-preserved',bit(T,22),True)
 check('equipment-passives-preserved',m.read(T+0x2a,0x16),before[0x2a:0x40])
 stable=m.read(T,264)+m.read(p,22)
 check('no-fallback-after-consumption',call('ffta_myk_dispel',T,choice),0)
 check('absent-is-read-only',m.read(T,264)+m.read(p,22),stable)

# Real command constructors and published selection preserve each lesson/AP
# identity across34 rows. Explicit buffers match the audited native allocation;
# full allocator/visible-window playback remains a separate acceptance step.
MENU,DESC,IDS,FLAGS=0x02028000,0x02028200,0x02028400,0x02028600
for entry,residue in itertools.product((0x08026d44,0x08026f9c),(0,4)):
 case=('native-menu',hex(entry),residue);fixture(421);grant(T,25)
 m.put(A+0x40,b'\xff'*0x90)
 manager=m.word(0x0200f438);m.put(manager+4,b'\x06');m.put(manager+24,struct.pack('<I',A))
 m.put(MENU,bytes(0xa4));m.put(MENU+10,b'\x04');m.put(MENU+0x94,struct.pack('<II',IDS,FLAGS))
 m.put(IDS-16,b'\xa5'*(16+42*4+16));m.put(FLAGS-16,b'\xa6'*(16+42+16));m.put(FLAGS,b'\x01'*42)
 bank=m.call(0x080cce60,A,1,DESC+4,DESC+5,stack=STACK+residue)
 m.put(DESC,struct.pack('<I',bank));m.put(DESC+6,bytes((125,0,0,0,0,0)))
 before=m.read(A,264);m.call(entry,MENU,DESC,stack=STACK+residue)
 count=m.read(DESC+9,1)[0];m.put(MENU+0x84,struct.pack('<H',count))
 ids=struct.unpack('<'+'I'*count,m.read(IDS,count*4));actions=[half(bank+8*i+4) for i in ids]
 #26F9C deliberately filters on native field21 (nonzero power) at26FE4.
 # Preserve this alternate menu's filter; ordinary command selection is26D44.
 wanted=list(range(410,421))+[421]*21+[422,423] if entry==0x08026d44 else [422]
 check('all-command-and-dispel-rows',actions,wanted)
 check('row-low-guard',m.read(IDS-16,16),b'\xa5'*16);check('row-high-guard',m.read(IDS+42*4,16),b'\xa5'*16)
 check('flag-high-guard',m.read(FLAGS+42,16),b'\xa6'*16);check('menu-preserves-learning',m.read(A,264),before)
 for i,action in enumerate(actions):
  if action!=421:continue
  choice=i-10;label=m.call(0x08025758,MENU,i,stack=STACK+residue)
  check('choice-label-pointer',label,m.word(S['ffta_mystic_choice_labels']+4*(choice-1)))
  check('only-existing-buff-enabled',m.read(FLAGS+i,1)[0],int(choice==8))
  m.call(S['ffta_dancer_menu_selected'],MENU,i,421,stack=STACK+residue)
  check('selected-choice-published',half(manager+16),choice)

report=dict(passed=not failures,romSha1=meta['romSha1'],assertions=sum(counts.values()),checks=dict(counts),failures=failures,samples=samples,resourceBoundaryCasts=resource_casts,
 limits=['Enchanted Fight, defensive reactions, whole Doublecast and full player/AI/law/save acceptance remain.'])
(OUT/'mystic-knight-commands.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
assert not failures,('Mystic command failures',len(failures))
