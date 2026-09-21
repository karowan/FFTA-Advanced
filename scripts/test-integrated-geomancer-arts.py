"""Deterministic Geomancy command, choice and cross-job effect contracts.

Material masks are declared inputs on a private flat board. Production catalog,
player playback and AI search have separate acceptance gates.
"""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-geomancer-fields.py';ns={'__file__':str(source),'__name__':'arts_fixture'}
exec(compile(source.read_text().split('for action,seed in itertools.product')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,C,STACK,regs=(ns[k] for k in ('m','S','meta','OUT','A','T','C','STACK','regs'))
call,half,state,job,equip=(ns[k] for k in ('call','half','state','job','equip'))
checks=collections.Counter();samples=[];failures=[];case=None;executions=0
wrappers=ns['ns']['ns']['wrappers'];MATERIALS=0x091f0000;GRID=0x02026000
costs=(4,6,8,8,10,10,12,18,12);elements=(3,0,4,0,0,1,5,2,0)
def check(k,a,b):
 checks[k]+=1
 if a!=b:failures.append(dict(check=k,actual=repr(a),expected=repr(b),case=case))
def reset(action,seed=0,material=0):
 ns['fresh'](action,seed)
 if action in (377,378):m.put(T+0x29,b'\x00')
 m.put(MATERIALS,bytes(163*256));m.put(MATERIALS+14*16+4,bytes((material,)))
 m.put(GRID,bytes((16,0))*256);info=bytearray(16)
 struct.pack_into('<I',info,4,GRID);info[8]=info[13]=info[15]=16;m.put(0x02007f10,info)
 for u,w in wrappers.items():m.put(w+10,struct.pack('<H',256))
def execute(action,choice=0):
 global executions
 m.put(regs[13],struct.pack('<4I',action,choice,0,255))
 try:ns['run'](action)
 except Exception:
  from unicorn.arm_const import UC_ARM_REG_PC,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3
  print('Native execution failed:',case,{k:hex(m.u.reg_read(v)) for k,v in dict(pc=UC_ARM_REG_PC,sp=UC_ARM_REG_SP,lr=UC_ARM_REG_LR,r0=UC_ARM_REG_R0,r1=UC_ARM_REG_R1,r2=UC_ARM_REG_R2,r3=UC_ARM_REG_R3).items()},flush=True)
  raise
 executions+=1

for action,seed in itertools.product(range(374,383),range(8)):
 case=('command',action,seed);reset(action,seed);execute(action,2 if action==381 else 1 if action==376 else 0)
 loss=500-half(T+0x18);samples.append(dict(action=action,seed=seed,loss=loss,wisp=call('ffta_geo_wisp',T),status=m.read(T+0xe8,8).hex()))
 check('native-cost-once',half(A+0x1c),100-costs[action-374])
 check('native-element-record',m.call(0x080ccd50,action,1,stack=STACK),elements[action-374])
 check('magic-sequencing',call('ffta_integrated_action_category',A,action),2)
 check('native-direct-magic-classification',m.call(0x080ccd50,action,28,stack=STACK),1)
 for flag in (18,19,26):check('no-native-cast-chain-flags',m.call(0x080ccd50,action,flag,stack=STACK),0)
 if action==378:check('Earthen-Ward-native-Protect',bool(m.read(T+0xeb,1)[0]&2),True)
 if action==379:check('Wisp-only-after-positive-loss',call('ffta_geo_wisp',T),int(loss>0))
 if action==375 and not loss:check('Tanglevine-no-rider-on-miss',bool(m.read(T+0xeb,1)[0]&64),False)
 check('roots-clean-after-command',m.read(0x0203ff44,8),bytes(8))
for action in (374,375,376,379,380,381):check('positive-native-damage-'+str(action),any(x['action']==action and x['loss']>0 for x in samples),True)
check('positive-native-Immobilize',any(x['action']==375 and bytes.fromhex(x['status'])[3]&64 for x in samples),True)

# Material effects use independent fixed masks, not the engine's affinity result
# as the expected multiplier. Same-seed native casts retain hit/miss outcomes.
for action,material in ((374,1),(378,1),(379,8),(380,16)):
 for seed in range(8):
  values=[]
  for mask in (0,material):
   case=('affinity',action,mask,seed);reset(action,seed,mask);execute(action)
   values.append((500-half(T+0x18),call('ffta_geo_wisp',T),call('ffta_geo_steady',T),bool(m.read(T+0xea,1)[0]&64)))
  if action==374:check('stone-one-fifth-bonus',values[1][0],values[0][0]*6//5)
  if action==378:check('ward-displacement-tag',tuple(v[2] for v in values),(0,1))
  if action==379:check('heat-strengthens-Wisp',tuple(v[1] for v in values),(1,2) if values[0][0]>0 else (0,0))
  if action==380:check('nonice-no-Slow',values[0][3],False)
  samples.append(dict(action=action,material=material,seed=seed,values=values))
check('ice-positive-Slow',any(x.get('material')==16 and x['values'][1][3] for x in samples),True)

for material in (0,1,2,4,8,16,31):
 case=('nearby-affinity',material);reset(374,material=material)
 check('exact-input-material',call('ffta_geo_affinity',A),material)
 m.put(MATERIALS+14*16+4,b'\x00');m.put(MATERIALS+13*16+4,bytes((material,)))
 check('orthogonal-neighbor',call('ffta_geo_affinity',A),material)
 m.put(GRID+2*(13*16+4),b'\x13');check('height-limit',call('ffta_geo_affinity',A),0)
 m.put(GRID+2*(13*16+4),b'\x12');check('height-boundary-included',call('ffta_geo_affinity',A),material)
reset(374);m.put(GRID+2*(13*16+4)+1,b'\x02');check('native-water-without-annotation',call('ffta_geo_affinity',A),4)

# Chosen elements pass through the native element consumer; the same choice
# must not become a weapon index in the native attack-stat consumer.
for choice,seed in itertools.product(range(1,6),range(8)):
 case=('Gaia native element',choice,seed);reset(381,seed,31)
 check('chosen-native-element',m.call(0x0812f8a4,A,381,choice,stack=STACK),choice)
 execute(381,choice);loss=500-half(T+0x18)
 samples.append(dict(gaia=choice,seed=seed,loss=loss))
for seed in range(8):
 check('choice-is-not-equipment',len({x['loss'] for x in samples if 'gaia' in x and x['seed']==seed}),1)

for choice,seed in itertools.product(range(1,6),range(8)):
 values=[]
 for attuned in (False,True):
  case=('Gaia Attunement',choice,seed,attuned);reset(381,seed,31)
  m.put(T+0x0c+choice,b'\x00')
  if attuned:equip(A,'GEO-S1')
  execute(381,choice);values.append((500-half(T+0x18),half(A+0x1c)))
 check('Gaia-selected-weakness-bonus',values[1][0],values[0][0]*5//4)
 check('Gaia-exact-single-refund',values[1][1],86 if values[1][0]>0 else 82)

# The second-stage S bonus precedes War Cry's defensive reduction. The native
# status formula remains authoritative for base accuracy and immunity.
for seed,vegetation,warcry in itertools.product(range(8),(False,True),(False,True)):
 case=('Tanglevine S',seed,vegetation,warcry);reset(375,seed,2 if vegetation else 0)
 m.put(C+0x28,b'\x01');m.put(C+0x30,struct.pack('<I',m.word(0x0812f2a0)+71*4))
 if warcry:call('ffta_viking_grant_war_cry',T,0)
 before=m.read(0x02000000,0x40000);rng=m.read(0x030034b0,4)
 base=call('ffta_original_viking_status_accuracy',C)
 expected=min(95,base+15) if base and vegetation else base
 if warcry:expected=max(0,expected-25)
 check('vegetation-before-defensive-reduction',m.call(0x08131220,C,stack=STACK),expected)
 check('S-query-preserves-state',m.read(0x02000000,0x40000),before)
 check('S-query-preserves-RNG',m.read(0x030034b0,4),rng)

for action,seed in itertools.product((375,376,379,380),range(8)):
 case=('native Damage to MP',action,seed);reset(action,seed,31);job(T,1,2)
 bank=m.word(m.word(0x080cd538)+4)
 index=next(i for i in range(142) if half(bank+8*i+4)==13 and m.read(bank+8*i+6,1)[0]==2)
 m.put(T+0x3a,bytes((index,)));m.put(T+0x40+index,b'\xff');m.put(T+0x1c,struct.pack('<HH',999,999))
 check('native-Damage-to-MP-equipped',m.call(0x0812e6a4,T,stack=STACK),13)
 execute(action,1 if action==376 else 0)
 check('MP-interception-no-HP-loss',half(T+0x18),500)
 check('MP-interception-no-Wisp',call('ffta_geo_wisp',T),0)
 check('MP-interception-no-Immobilize-Slow',m.read(T+0xea,2)[0]&64 | m.read(T+0xeb,1)[0]&64,0)
 check('MP-interception-no-push',m.read(T+0xf6,2),bytes((5,14)))
 samples.append(dict(mpIntercept=action,seed=seed,mpLoss=999-half(T+0x1c)))
check('nonvacuous-MP-interception',any(x.get('mpLoss',0)>0 for x in samples),True)

for seed,inoculated in itertools.product(range(8),(False,True)):
 case=('Wisp prevention',seed,inoculated);reset(379,seed,8)
 if inoculated:call('ffta_inoculated_grant',T,0)
 execute(379)
 check('Inoculated-prevents-Wisp-after-damage',call('ffta_geo_wisp',T),0 if inoculated or half(T+0x18)==500 else 2)

# Exposure starts after its source hit; subsequent direct magical HP damage
# sees exactly one frozen multiplier. Physical damage is unaffected.
for action,strong,seed in itertools.product((0,23),(False,True),range(8)):
 values=[]
 for active in (False,True):
  case=('Wisp incoming',action,strong,seed,active);reset(action,seed)
  if active:
   s=state(T);m.put(s+17,b'\x40');m.put(s+18,bytes((int(strong),)))
  execute(action);values.append(500-half(T+0x18))
 factor=25 if strong else 23
 check('Wisp-magical-only-single-rounding',values[1],values[0] if action==0 else values[0]*factor//20)

for seed in range(8):
 case=('weak-does-not-refresh-strong',seed);reset(379,seed)
 s=state(T);m.put(s+17,b'\x20');m.put(s+18,b'\x01');execute(379)
 check('strong-retains-one-turn',m.read(s+17,1)[0]>>5,1)
 check('strong-retains-strength',call('ffta_geo_wisp',T),2)
for effect in (24,26,51):
 reset(378);s=state(T);before=m.call(0x08133a58,T,effect,stack=STACK)
 m.put(s+19,b'\x02')
 check('Steady-only-displacement',m.call(0x08133a58,T,effect,stack=STACK),0 if effect==26 else before)

# All directions are selected once before native execution. Landing legality,
# immunity, occupancy and the original damage transaction remain native.
for direction,seed,blocked in itertools.product(range(1,5),range(8),(False,True)):
 case=('Torrent',direction,seed,blocked);reset(376,seed,4)
 dx,dy=((0,-1),(1,0),(0,1),(-1,0))[direction-1];dest=(5+dx,14+dy)
 if blocked:
  u=next(u for u in wrappers if u not in (A,T));m.put(u+0xf6,bytes(dest));m.put(wrappers[u]+8,struct.pack('<3H',dest[0]*32+16,256,dest[1]*32+16))
 execute(376,direction);loss=500-half(T+0x18)
 wanted=dest if loss and not blocked and dest!=(4,14) else (5,14)
 check('chosen-native-one-tile-push',tuple(m.read(T+0xf6,2)),wanted)
 samples.append(dict(torrent=direction,seed=seed,blocked=blocked,loss=loss,xy=list(m.read(T+0xf6,2))))
check('positive-Torrent-displacement',any('torrent' in x and x['xy']!=[5,14] for x in samples),True)

for strong,seed in itertools.product((False,True),range(8)):
 case=('Wisp cleanup',strong,seed);reset(379,seed,8 if strong else 0);execute(379)
 if not call('ffta_geo_wisp',T):continue
 s=state(T);m.put(s+15,b'\x05\x0e');m.put(s+17,bytes((m.read(s+17,1)[0]|25,)))
 m.put(s+18,bytes((m.read(s+18,1)[0]|4,)));m.put(s+19,b'\xe2')
 call('ffta_geo_event',T,6)
 check('remedy-clears-Wisp',call('ffta_geo_wisp',T),0)
 check('remedy-preserves-field',m.read(s+17,1)[0]&31,25)
 check('remedy-preserves-Updraft',m.read(s+18,1)[0]&14,4)
 check('remedy-preserves-Steady-ledger',m.read(s+19,1),b'\xe2')

# Native Move defers unit coordinates until execution. Only the exact active
# wrapper may override those coordinates during menu/forecast queries. Copies
# must keep their own simulated tile, even if character/job identity matches.
COPY=0x02028800
for ui_mode,owner,wrapper_owner in itertools.product((5,6,8,11,12),(False,True),(False,True)):
 case=('moved affinity owner',ui_mode,owner,wrapper_owner);reset(381,material=1)
 manager=m.word(0x0200f438);w=wrappers[A]
 m.put(manager+4,bytes((ui_mode,)));m.put(manager+24,struct.pack('<I',A if owner else T))
 m.put(0x0200f4ec,struct.pack('<I',w if wrapper_owner else wrappers[T]))
 m.put(w+8,struct.pack('<3H',8*32+16,256,14*32+16))
 m.put(MATERIALS+14*16+8,b'\x18');m.put(COPY,m.read(A,264))
 before=m.read(0x02000000,0x40000);rng=m.read(0x030034b0,4)
 check('displayed-tile-exact-owner-only',call('ffta_geo_affinity',A),24 if 6<=ui_mode<=11 and owner and wrapper_owner else 1)
 check('copied-candidate-keeps-simulated-tile',call('ffta_geo_affinity',COPY),1)
 check('affinity-owner-query-read-only',m.read(0x02000000,0x40000),before)
 check('affinity-owner-query-no-RNG',m.read(0x030034b0,4),rng)
reset(381,material=1);manager=m.word(0x0200f438);w=wrappers[A]
m.put(manager+4,b'\x06');m.put(manager+24,struct.pack('<I',A));m.put(0x0200f4ec,struct.pack('<I',w))
for x,y in ((16,14),(4,16),(2047,2047)):
 m.put(w+8,struct.pack('<3H',x*32+16,256,y*32+16))
 check('wrapper-position-bounds',call('ffta_geo_affinity',A),0)

# Native menu uses one AP record for each action even with multiple choices.
MENU,DESC,IDS,FLAGS=0x02028000,0x02028200,0x02028400,0x02028500
for material in (0,31):
 case=('Geomancy menu',material);reset(374,material=material)
 m.put(A+0x35,bytes((121,121,0)));m.put(A+0x40,b'\xff'*0x90)
 manager=m.word(0x0200f438);m.put(manager+4,b'\x06');m.put(manager+24,struct.pack('<I',A))
 m.put(MENU,bytes(0xa4));m.put(MENU+10,b'\x03');m.put(MENU+0x94,struct.pack('<II',IDS,FLAGS))
 m.put(IDS-16,b'\xa5'*(16+88+16));m.put(FLAGS-16,b'\xa6'*(16+22+16));m.put(FLAGS,b'\x01'*22)
 bank=m.call(0x080cce60,A,1,DESC+4,DESC+5,stack=STACK);m.put(DESC,struct.pack('<I',bank));m.put(DESC+6,bytes((121,0,0,0,0,0)))
 before=m.read(A,264);m.call(0x08026d44,MENU,DESC,stack=STACK);count=m.read(DESC+9,1)[0]
 check('menu-capacity',count<=22,True);m.put(MENU+0x84,struct.pack('<H',count))
 check('menu-does-not-change-learning',m.read(A,264),before)
 rows=list(struct.unpack('<'+'I'*count,m.read(IDS,count*4)));actions=[half(bank+i*8+4) for i in rows]
 check('all-nine-Geomancy-lessons',set(actions),set(range(374,383)))
 for action,wanted in ((376,[1,2,3,4]),(381,[2,3,4,1,5] if material else [2])):
  indices=[i for i,a in enumerate(actions) if a==action];check('exact-choice-count',len(indices),len(wanted))
  check('one-mastery-record',len({rows[i] for i in indices}),1)
  for row,choice in zip(indices,wanted):
   pointer=m.call(0x08025758,MENU,row,stack=STACK);width=m.call(0x080161bc,pointer,stack=STACK)
   check('bounded-label',width<=13,True);check('menu-width-covers-label',width<=m.read(DESC+7,1)[0],True)
   check('selected-original-action',call('ffta_dancer_menu_selected',MENU,row,action),action)
   check('selected-operand',half(manager+16),choice)
   m.call(0x0812f230,C,action,choice,0,stack=STACK);check('constructor-retains-operand',half(C+14),choice)
 for p,n,value in ((IDS-16,16,165),(IDS+88,16,165),(FLAGS-16,16,166),(FLAGS+22,16,166)):check('menu-boundary',m.read(p,n),bytes((value,))*n)

report=dict(passed=not failures,romSha1=meta['romSha1'],total=sum(checks.values()),checks=dict(checks),nativeExecutions=executions,samples=samples,failures=failures,
 limits=['Material masks above are fixed test inputs; production terrain has separate acceptance.','Full native UI playback, laws, save transport and AI choice search remain separate acceptance gates.'])
(OUT/'geomancer-arts.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
assert not failures,('Geomancy contract failures',len(failures))
