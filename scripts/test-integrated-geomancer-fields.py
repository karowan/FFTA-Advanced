"""Fixed native Updraft/field casts, movement, frozen shelter and state ownership.

Rime's terrain-dependent Slow and field overlays are not accepted here.
"""
import collections,itertools,json,pathlib,struct
from fractions import Fraction
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-geomancer.py';ns={'__file__':str(source),'__name__':'field_fixture'}
exec(compile(source.read_text().split('# Native transferability')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,C,STACK,regs=(ns[x] for x in ('m','S','meta','OUT','A','T','C','STACK','regs'))
fixture,run,call,job,hp,half,equip=(ns[x] for x in ('fixture','run','call','job','hp','half','equip'))
checks=collections.Counter();samples=[];lookups=[];case=None
def check(k,a,b):
 checks[k]+=1
 assert a==b,(k,a,b,case)
def state(u):return call('ffta_job_state',u)
def field(u,kind,x=5,y=14,timer=6):
 s=state(u);m.put(s+15,bytes((x,y,(m.read(s+17,1)[0]&224)|(timer<<2)|kind)))
def updraft(u,jump=False,timer=2):
 s=state(u);m.put(s+18,bytes((timer<<1|(timer<<4 if jump else 0),)))
def fresh(action,seed=0):
 fixture(action,seed);job(A,3,121)
 if action==377:m.put(T+0x29,b'\x00')
 m.call(0x080ca2e8,A,stack=STACK);m.call(0x080ca2e8,T,stack=STACK)
def cast(action,seed=0):
 fresh(action,seed);before=half(A+0x1c);ids=run(action)
 check('native-one-payment',before-half(A+0x1c),8 if action==377 else 12)
 check('native-single-command',ids,[action])
 check('native-action-roots-retire',m.read(0x0203ff44,8),bytes(8))

for action,seed in itertools.product((377,380,382),range(8)):
 case=('native cast',action,seed);cast(action,seed)
 if action==377:
  check('native-Updraft-ally',call('ffta_geo_updraft',T,0),1)
  check('native-Updraft-self',call('ffta_geo_updraft',A,0),1)
  check('native-Updraft-No-HP-change',half(T+0x18),500)
 else:
  check('native-field-placement',call('ffta_geo_field_kind',A),1 if action==380 else 2)
  check('native-chosen-center',m.read(state(A)+15,2),bytes((5,14)))
  if action==382:check('Refuge-no-healing-or-damage',half(T+0x18),500)
  samples.append(dict(action=action,seed=seed,loss=500-half(T+0x18)))
 for flag in (18,19,26):check('no-Reflect-Doublecast-ReturnMagic',m.call(0x080ccd50,action,flag,stack=STACK),0)
check('Rime-retains-positive-damage',any(x['action']==380 and x['loss']>0 for x in samples),True)
check('Rime-field-on-miss',any(x['action']==380 and x['loss']==0 for x in samples),True)

# Empty target cells are ordinary selected map cells, not fabricated result
# callbacks. The field is owned by the caster even with no recipient rows.
for action in (380,382):
 case=('empty cross',action);fresh(action)
 for u,w in ns['ns']['wrappers'].items():
  if u==A:continue
  m.put(u+0xf6,bytes((0,0)));m.put(w+8,struct.pack('<3H',16,32,16))
 m.put(A+0xf6,bytes((2,14)));m.put(ns['ns']['wrappers'][A]+8,struct.pack('<3H',80,32,464))
 run(action)
 check('empty-native-cross-field',call('ffta_geo_field_kind',A),1 if action==380 else 2)
 check('empty-cross-paid',half(A+0x1c),88)

# Native field replacement, independent Wisp bits and exact caster turns.
for previous,action in itertools.product((1,2),(380,382)):
 case=('replacement',previous,action);fresh(action);field(A,previous,4,14)
 m.put(state(A)+17,bytes((m.read(state(A)+17,1)[0]|64,)))
 run(action);check('replace-one-slot',call('ffta_geo_field_kind',A),1 if action==380 else 2)
 check('placement-preserves-Wisp',m.read(state(A)+17,1)[0]>>5,2)
 for turn,expected in enumerate((True,True,False),1):
  call('ffta_drk_lifecycle_turn_end',A)
  check('field-second-subsequent-turn-expiry',bool(call('ffta_geo_field_kind',A)),expected)

# Controlled height differences use the actual decoded native height grid.
# Updraft's recipients and Float duration are independent of the caster's job.
for light,sure,lower,self_target in itertools.product((False,True),repeat=4):
 if light and sure:continue # One legal support slot.
 case=('Updraft movement',light,sure,lower,self_target);fresh(377)
 u=A if self_target else T
 if light:job(u,4,29);equip(u,'DNC-S2')
 if sure:job(u,3,21);equip(u,'GEO-S2')
 hm=int.from_bytes(m.read(0x02007f14,4),'little');width=m.read(0x02007f18,1)[0]
 # Width is checked against native tile lookup before any test mutation.
 assert 1<=width<=32,('native height width',width)
 if not self_target:m.put(hm+2*(14*width+4),bytes((6 if lower else 4,)));m.put(hm+2*(14*width+5),b'\x04')
 m.call(0x080ca2e8,u,stack=STACK);before_jump=m.read(u+0xfe,1)[0];before_move=m.call(0x080ca394,u,stack=STACK)
 m.put(C+4,struct.pack('<II',u,u));call('ffta_geo_updraft_apply',C)
 check('Move-plus-one-stacks-with-Light-Foot',m.call(0x080ca394,u,stack=STACK),before_move+1)
 check('Jump-only-lower-recipient',m.read(u+0xfe,1)[0],before_jump+int(lower and not self_target))
 check('Float-tag-not-flight',call('ffta_geo_grounded',u),0)
 first=m.read(state(u)+18,1);call('ffta_geo_updraft_apply',C)
 check('Updraft-does-not-stack',m.read(state(u)+18,1),first)
 check('repeat-does-not-stack-Move',m.call(0x080ca394,u,stack=STACK),before_move+1)
 call('ffta_drk_lifecycle_event',u,1)
 check('native-turn-budget-includes-Updraft',call('ffta_turn_original_allowance',u),before_move+1)
 for turn in range(1,4):
  call('ffta_drk_lifecycle_turn_end',u)
  check('Updraft-recipient-T2',call('ffta_geo_updraft',u,0),int(turn<(3 if self_target else 2)))
 check('expired-Move-restored',m.call(0x080ca394,u,stack=STACK),before_move)
 check('expired-cached-Jump-restored',m.read(u+0xfe,1)[0],before_jump)
 check('expired-cached-Jump-complement',m.read(u+0xff,1)[0],before_jump^255)

# Both kinds have exactly a cross, bounded height, all valid legal map cells,
# one entering surcharge regardless of caster count; no changed blocked bits.
grid=0x0202d000;wrapper=ns['ns']['wrappers'][T]
for kind,air,sure,overlap in itertools.product((0,1,2),range(4),(False,True),(False,True)):
 case=('native grid',kind,air,sure,overlap);fresh(23)
 if sure:equip(T,'GEO-S2')
 m.call(0x080ca2e8,T,stack=STACK)
 if air==1:updraft(T)
 if air==2:m.put(T+0xfc,b'\x02')
 if air==3:m.put(T+0xfd,b'\x05')
 m.put(grid,bytes(0x98a))
 for y,x in itertools.product(range(16),repeat=2):m.call(0x08097814,grid,x,y,wrapper,stack=STACK)
 control=m.read(grid,0x700)
 if kind:
  field(A,kind)
  if overlap:field(T,kind)
 m.put(grid,bytes(0x98a))
 for y,x in itertools.product(range(16),repeat=2):m.call(0x08097814,grid,x,y,wrapper,stack=STACK)
 got=m.read(grid,0x700)
 for y,x in itertools.product(range(16),repeat=2):
  offset=7*(16*y+x);old=control[offset:offset+7];new=got[offset:offset+7]
  h=m.call(0x0801cc18,x,y,stack=STACK);center_h=m.call(0x0801cc18,5,14,stack=STACK)
  inside=abs(x-5)+abs(y-14)<=1 and abs(h-center_h)<=2
  surcharge=int(kind==1 and not air and not sure and bool(old[0]&128) and inside)
  expected=bytearray(old);expected[1]=(old[1]&240)|min(15,(old[1]&15)+surcharge)
  check('native-grid-only-one-legal-entering-cost',new,bytes(expected))

# Shelter uses frozen incoming-action occupancy, does not qualify Poise or
# first-buff Encouragement, never protects enemies or airborne recipients.
for air,friendly,cross,physical,raw in itertools.product(range(4),(False,True),(False,True),(False,True),(1,17,99)):
 case=('Refuge frozen factor',air,friendly,cross,physical,raw);fresh(0 if physical else 23)
 field(T,2,5 if cross else 0,14 if cross else 0)
 if air==1:updraft(T)
 if air==2:m.put(T+0xfc,b'\x03')
 if air==3:m.put(T+0xfd,b'\x05')
 if friendly:m.put(A+0x29,b'\x80')
 expected=raw*4//5 if not physical and not air and not friendly and cross else raw
 check('Refuge-one-rational-direct-HP-factor',call('ffta_integrated_exposed_native_stage',raw,C),expected)
 if not air:check('field-is-not-Poise-status',call('ffta_integrated_beneficial',T),0)
 frame=0x03007400;call('ffta_snapshot_begin',frame,A,T,1);call('ffta_action_started',A,0 if physical else 23,1,1 if physical else 2)
 m.put(state(T)+17,b'\x00');m.put(T+0xf6,b'\x00\x00')
 check('action-start-occupancy-frozen',call('ffta_integrated_exposed_native_stage',raw,C),expected)
 call('ffta_snapshot_end',frame)
 check('future-action-loses-shelter',call('ffta_integrated_exposed_native_stage',raw,C),raw)

for event in range(1,9):
 case=('lifecycle',event);fresh(377);field(A,2);updraft(A,True);s=state(A)
 call('ffta_geo_mobility',A);jump=m.read(A+0xfe,1)[0]
 m.put(s+19,b'\xe2');m.put(s+20,b'\xab\xcd');call('ffta_geo_event',A,event)
 check('field-cleanup-domain',call('ffta_geo_field_kind',A),0 if event in (2,3,4,5) else 2)
 check('Updraft-dispel-and-cleanup',call('ffta_geo_updraft',A,0),0 if event in (2,3,4,5,7) else 1)
 check('movement-ledger-high-bits-preserved',m.read(s+19,1)[0]&248,224)
 check('Mystic-Knight-state-preserved',m.read(s+20,2),b'\xab\xcd')
 check('cleanup-refreshes-cached-Jump',m.read(A+0xfe,1)[0],jump-int(event in (2,3,4,5,7)))

# Independent evaluated units must never borrow a missing live caster's
# field. Their own explicitly copied field remains representable.
for own in (False,True):
 case=('independent copy',own);fresh(23);field(T if own else A,1)
 copy=0x03007300;check('evaluated-copy-created',call('ffta_snapshotted_evaluated_init',copy,T),1)
 check('copied-field-only-exact-owner',call('ffta_geo_field_at',copy,5,14,1),int(own))
 call('ffta_snapshotted_evaluated_close',copy)

# Complete native incoming actions use the shelter created by a prior cast.
# Clear only that field for the same-seed differential control.
incoming=[]
for seed in range(8):
 outcomes=[]
 for enabled in (False,True):
  case=('native incoming shelter',seed,enabled);cast(382,seed)
  if not enabled:m.put(state(A)+17,b'\x00')
  job(T,3,21);m.put(T+0x24,struct.pack('<H',200))
  m.put(0x030034b0,struct.pack('<I',seed));m.put(regs[13],struct.pack('<4I',23,0,0,255))
  ns['ns']['ns']['context'](23);m.put(C,struct.pack('<III',T,A,A))
  m.call(0x080a433c,regs[0],ns['ns']['wrappers'][T],4,14,stack=regs[13])
  ns['executions']+=1;outcomes.append(500-half(A+0x18))
 check('native-Refuge-positive-damage-reduction',outcomes[1],outcomes[0]*4//5)
 incoming.append(dict(seed=seed,loss=outcomes))
check('native-Refuge-positive-control',any(x['loss'][0]>0 for x in incoming),True)

# Both status icons stay outside the dynamic OBJ allocation and each other.
for enabled in (False,True):
 case=('bounded live field lookup',enabled);fresh(23)
 if enabled:field(A,1)
 visits=[];address=meta['symbols']['ffta_job_state']&~1
 # Follow the explicit imported-symbol shim to the actual record accessor.
 while m.read(address,4)==bytes.fromhex('08b4024b'):
  address=int.from_bytes(m.read(address+12,4),'little')&~1
 check('query-cell-is-native-valid',bool(m.call(0x0801cc7c,5,14,stack=STACK)),True)
 trace=[]
 assert call.__globals__['m'] is m,'Counter must observe the actual execution machine'
 hook=m.u.hook_add(ns['ns']['ns']['UC_HOOK_CODE'],lambda u,a,z,d:trace.append(a))
 m.u.ctl_flush_tb()
 check('fast-field-query-preserves-result',call('ffta_geo_field_at',T,5,14,1),int(enabled))
 m.u.hook_del(hook)
 visits=[a for a in trace if a==address]
 (OUT/'geomancer-lookup-trace.json').write_text(json.dumps(dict(address=hex(address),instructions=len(trace),counts={hex(a):n for a,n in collections.Counter(trace).items() if a>=0x09100000}),indent=2))
 case=(*case,len(visits));check('bounded-live-record-lookups',0<len(visits)<=2,True)
 lookups.append(dict(field=enabled,lookups=len(visits)))
m.u.mem_map(0x06000000,0x20000)
for icon,first in ((39,0x06013f80),(40,0x06013fc0),(41,0x06014000),(42,0x06014040)):
 case=('status icon',icon);fresh(377);sprite=0x02029000
 m.put(first-4,b'\x91'*4);m.put(first+64,b'\x92'*4)
 check('native-icon-tile',call('ffta_geo_status_visual',sprite,icon),0x1fc+2*(icon-39))
 check('icon-left-boundary',m.read(first-4,4),b'\x91'*4)
 check('icon-right-boundary',m.read(first+64,4),b'\x92'*4)
check('dynamic-OBJ-after-all-custom-icons',ns['ns']['ns']['rom'][0x97098:0x9709c],bytes.fromhex('88239b00'))

for origin,raw in itertools.product((1,2),(1,17,99)):
 case=('incoming reaction protection',origin,raw);fresh(23);field(T,2)
 frame=0x03007400;call('ffta_snapshot_begin',frame,A,T,1);call('ffta_action_started',A,23,origin,2)
 check('Refuge-incoming-reactions-retain-defense',call('ffta_integrated_exposed_native_stage',raw,C),raw*4//5)
 call('ffta_snapshot_end',frame)
for buff in (False,True):
 case=('legal allied Poise',buff);fresh(23);job(T,1,2);equip(T,'SAM-S2')
 if buff:updraft(T)
 check('Updraft-qualifies-Poise',call('ffta_integrated_exposed_native_stage',100,C),75 if buff else 100)

report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),nativeExecutions=ns['executions'],samples=samples,incoming=incoming,lookups=lookups,
 limits=['Rime terrain Slow is not implemented in this batch','Field tiles have a caster icon; map overlay and full visual/save playback remain separate','No affinity mapping or remaining Geomancy actions accepted here'])
(OUT/'geomancer-fields.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
