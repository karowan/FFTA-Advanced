"""Native turn allowance and terrain-cost ledger, independent of Passing UI.

Controlled route-map inputs exercise the actual native map readers. Live Move,
undo, AI turns and cold suspend remain the separate turn-admission replay.
"""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-bard.py';ns={'__file__':str(source),'__name__':'movement_fixture'}
exec(compile(source.read_text().split('# Native command flags')[0],str(source),'exec'),ns)
m,S,meta,OUT,ACTOR,STACK=(ns[k] for k in ('m','S','meta','OUT','ACTOR','STACK'))
setup,call,job,wrappers=(ns[k] for k in ('setup','call','job','wrappers'))
equip=ns['ns']['equip'];checks=collections.Counter();case=None;samples=[]
def check(k,a,b):checks[k]+=1;assert a==b,(k,a,b,case)
def record():return call('ffta_job_state',ACTOR)
def native():return m.call(0x080ca394,ACTOR,stack=STACK)
def read_budget():return call('ffta_turn_original_allowance',ACTOR),call('ffta_turn_step_remaining',ACTOR)

setup(0)
boots=next(i for i in range(1,461) if m.call(0x080ca7a4,i,16,stack=STACK)>0)
for race,j,light,gear,bonus,steady in itertools.product((4,), (33,124,125), (False,True), (0,boots), (0,1), range(8)):
 case=('native initial allowance',race,j,light,gear,bonus,steady)
 setup(0);job(ACTOR,race,j);m.put(ACTOR+0x2a,struct.pack('<5H',gear,0,0,0,0));m.put(ACTOR+0x3d,bytes((bonus,)))
 if light:equip(ACTOR,'DNC-S2')
 p=record();m.put(p+19,bytes((steady,)));allowance=native();before=m.read(ACTOR,264)
 call('ffta_turn_event',ACTOR,1)
 check('native-allowance-includes-support-gear-and-bonus',read_budget(),(allowance,min(2,allowance)))
 check('start-preserves-unit',m.read(ACTOR,264),before)
 check('Steady-low-bits-preserved',m.read(p+19,1)[0]&7,steady)
 # Removing a bonus after turn start cannot shrink the original ledger;
 # granting a bonus later cannot replenish it either.
 m.put(ACTOR+0x2a,bytes(10));m.put(ACTOR+0x3b,b'\x00');m.put(ACTOR+0x3d,b'\x00')
 check('original-does-not-recompute-mid-turn',read_budget(),(allowance,min(2,allowance)))
 saved=m.read(p,22);call('ffta_turn_close_movement',ACTOR)
 check('finishing-step-closes-remainder',read_budget(),(allowance,0))
 closed=m.read(p,22)
 check('closing-movement-preserves-other-domains',closed[:19]+closed[20:],saved[:19]+saved[20:])
 check('closing-preserves-Steady',closed[19]&7,saved[19]&7)
 if steady==0:samples.append(dict(job=j,lightFoot=light,gear=gear,bonus=bonus,allowance=allowance))
for row in (s for s in samples if s['lightFoot']):
 control=next(s for s in samples if not s['lightFoot'] and all(s[k]==row[k] for k in ('job','gear','bonus')))
 check('real-Light-Foot-positive-control',row['allowance'],control['allowance']+1)

# Same one-tile destination, different accumulated terrain costs. This catches
# charging Manhattan distance instead of actual movement points.
for used,reachable,ready,origin in itertools.product((0,1,2,3,4,5,7,255),(False,True),(False,True),(False,True)):
 case=('route cost',used,reachable,ready,origin);setup(0);job(ACTOR,4,124)
 p=record();m.put(p+19,b'\x05');call('ffta_turn_event',ACTOR,1);allowance=native()
 w=wrappers[ACTOR];grid=m.word(w+0x3c);node=grid+7*(16*14+5)
 m.put(0x0200f4ec,struct.pack('<I',w));m.put(w+8,struct.pack('<3H',5*32+16,32,14*32+16))
 m.put(grid+0x980,bytes((4 if ready else 3,)))
 m.put(grid+0x986,bytes((4 if origin else 3,14)))
 m.put(node+2,bytes((128 if reachable else 0,)));m.put(node+4,bytes((used,)))
 call('ffta_turn_flag',4,1,0x080968d3)
 expected=min(2,allowance-used) if origin and reachable and ready and 0<used<=allowance else 0
 check('actual-terrain-cost-and-map-provenance',read_budget(),(allowance,expected))
 check('completion-preserves-Steady',m.read(p+19,1)[0]&7,5)
 check('one-tile-history-independent-of-cost',m.read(p+14,1)[0]&7,3)
 call('ffta_turn_flag',4,0,0x08096343)
 check('undo-restores-original-capped-budget',read_budget(),(allowance,min(2,allowance)))

for authenticated,active,remainder in itertools.product((False,True),(False,True),range(4)):
 case=('old-or-invalid-ledger',authenticated,active,remainder);setup(0);p=record()
 m.put(p+14,bytes((32|int(active),)));m.put(p+19,bytes((int(authenticated)*128+remainder*32+5,)))
 check('unknown-ledger-cannot-grant-movement',call('ffta_turn_step_remaining',ACTOR),remainder if authenticated and active and remainder<=2 else 0)

for event,steady in itertools.product(range(2,6),range(8)):
 case=('ledger lifetime',event,steady);setup(0);p=record();m.put(p+19,bytes((steady,)))
 call('ffta_turn_event',ACTOR,1);before=m.read(p,22);call('ffta_turn_event',ACTOR,event);after=m.read(p,22)
 check('lifecycle-retires-entire-ledger',after[12:15]+bytes((after[19]&248,)),bytes(4))
 check('lifecycle-preserves-other-jobs',after[:12]+after[15:19]+bytes((after[19]&7,))+after[20:],before[:12]+before[15:19]+bytes((before[19]&7,))+before[20:])

report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),samples=samples,
 limits=['Route-map cases are controlled native-reader inputs, not terrain traversal playback. Passing Step selection and execution require separate playback acceptance.'])
(OUT/'turn-movement-budget.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
