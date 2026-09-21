"""Native Viking outgoing factors and exact frozen action-start relationships."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT/'tools/arm-python'),str(ROOT/'scripts')]
from unicorn import *
from unicorn.arm_const import *
from native_battle_wrappers import from_memory
meta=_load_job_candidate(ROOT/'build/expansion/probes/viking/current.json');ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes();S=meta['symbols'];fix=ROM.parent/'executor'
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes();regs=struct.unpack_from('<17I',(fix/'execute-trap.state').read_bytes(),0x20)
UNIT,TARGET,ALLY,EQUIPMENT,RETURN,STACK=0x02000080,0x020033e4,0x02000398,0x02002000,0x08000100,0x03007000
node=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'));exec(compile(ast.Module(body=[n for n in node.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m=ARM(rom,iw);control=bytearray(rom);offset=S['ffta_viking_outgoing_numerator']-0x08000000
# Independent native reference removes ONLY the new outgoing rational factor.
# All native accuracy, magic, defenses, statuses, weapon effects and costs run.
assert offset%4==0
control[offset:offset+8]=struct.pack('<HHI',0x4800,0x4770,1000);baseline=ARM(control,iw)
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()};checks=collections.Counter();samples=[]
def check(k,a,b):checks[k]+=1;assert a==b,(k,a,b,globals().get('case'))
def record(engine,unit):return engine.call(S['ffta_job_state'],unit)
def reset(engine,support,status,challenge):
 engine.put(0x02000000,ram);engine.put(0x03000000,iw);engine.put(0x0203ff44,bytes(8));engine.call(S['ffta_job_reset'])
 for unit in wrappers:
  xy=(4,14) if unit==UNIT else ((5,14) if unit==ALLY else ((5,13) if unit==TARGET else (0,0)))
  engine.put(unit+0xf6,bytes(xy));engine.put(wrappers[unit]+8,struct.pack('<H',xy[0]<<5));engine.put(wrappers[unit]+12,struct.pack('<H',xy[1]<<5))
 for unit in (UNIT,ALLY,TARGET):
  engine.put(unit+0xe8,bytes(8));engine.put(unit+0x3a,bytes(2));engine.put(unit+0x18,struct.pack('<4H',250,250,50,50))
  engine.put(unit+0x2a,struct.pack('<5H',399,0,0,0,0))
  engine.put(unit+0x29,bytes([0 if unit==UNIT else 128]))
 engine.put(UNIT+5,bytes([118,2,118]));engine.put(UNIT+0x35,bytes([118]));engine.put(UNIT+0x3b,bytes([101 if support else 0]))
 if status:
  for unit in (ALLY,TARGET):engine.put(unit+0xe9,bytes([2]))
 if challenge:engine.call(S['ffta_viking_grant_challenge'],UNIT,TARGET)
def execute(engine,action,seed):
 engine.put(0x030034b0,struct.pack('<I',seed));engine.put(regs[13],struct.pack('<4I',action,0,0,255))
 engine.call(0x080a433c,regs[0],wrappers[UNIT],5,14,stack=regs[13])
 return {u:250-struct.unpack('<H',engine.read(u+0x18,2))[0] for u in (ALLY,TARGET)}
for action,support,status,challenge,seed in itertools.product((365,369,371,370),(0,1),(0,1),(0,1),range(16)):
 case=(action,support,status,challenge,seed)
 reset(baseline,support,status,challenge);plain=execute(baseline,action,seed)
 reset(m,support,status,challenge);actual=execute(m,action,seed)
 for unit in (ALLY,TARGET):
  numerator=(13 if support and status else 10)*(7 if challenge and unit!=TARGET else 10)
  check('native-outgoing-product',actual[unit],plain[unit]*numerator//100)
 check('native-cost-preserved',m.read(UNIT+0x1c,2),baseline.read(UNIT+0x1c,2))
 samples.append(dict(action=action,support=support,status=status,challenge=challenge,seed=seed,plain=plain,actual=actual))
check('nonvacuous-native-positive-damage',any(any(v>0 for v in row['plain'].values()) for row in samples),True)
check('nonvacuous-native-boost',any(any(row['actual'][u]>v for u,v in row['plain'].items()) for row in samples),True)
check('nonvacuous-native-challenge-penalty',any(any(0<row['actual'][u]<v for u,v in row['plain'].items()) for row in samples),True)
# Native Damage to MP must receive the same unmodified resource amount even
# when both outgoing HP factors would otherwise apply.
bank=m.word(m.word(0x080cd538)+4)
r13=next(i for i in range(142) if struct.unpack_from('<H',m.read(bank+8*i,8),4)[0]==13 and m.read(bank+8*i+6,1)[0]==2)
for action,support,challenge,seed in itertools.product((365,370),(0,1),(0,1),range(16)):
 case=('MP-only',action,support,challenge,seed);results=[]
 for engine in (baseline,m):
  reset(engine,support,1,challenge);engine.put(ALLY+5,bytes([2,1,2]));engine.put(ALLY+0x3a,bytes([r13]));engine.put(ALLY+0x1c,struct.pack('<HH',999,999))
  loss=execute(engine,action,seed);results.append((loss[ALLY],engine.read(ALLY+0x1c,2)))
 check('MP-interception-excludes-outgoing-factors',results[1],results[0])
 check('intercepted-HP-untouched',results[1][0],0)

# Exercise the actual shared snapshot API; fixture state is initialized before
# the operation, then mutated between reads to distinguish frozen/live behavior.
FRAME=0x03007500
for reverse in (False,True):
 reset(m,1,1,1);check('open-frozen-action',m.call(S['ffta_snapshot_begin'],FRAME,UNIT,ALLY,1),1)
 m.call(S['ffta_action_started'],UNIT,371,1,2)
 expected={ALLY:910,TARGET:1300}
 for unit in ((TARGET,ALLY) if reverse else (ALLY,TARGET)):
  check('frozen-target-order',m.call(S['ffta_viking_outgoing_numerator'],UNIT,unit,371),expected[unit])
  if unit==TARGET:
   m.call(S['ffta_viking_lifecycle_event'],TARGET,2)
   check('live-source-KO-cleans-next-action',m.read(record(m,UNIT)+5,1),b'\0')
 m.call(S['ffta_snapshot_end'],FRAME)
 check('next-action-cleanup-observed',m.call(S['ffta_viking_outgoing_numerator'],UNIT,ALLY,371),1300)
# A status added by the current hit cannot qualify that hit; later action can.
reset(m,1,0,0);m.call(S['ffta_snapshot_begin'],FRAME,UNIT,ALLY,1);m.call(S['ffta_action_started'],UNIT,369,1,2)
m.put(ALLY+0xea,b'\x40');check('no-self-qualification',m.call(S['ffta_viking_outgoing_numerator'],UNIT,ALLY,369),1000)
m.call(S['ffta_snapshot_end'],FRAME);check('subsequent-action-qualification',m.call(S['ffta_viking_outgoing_numerator'],UNIT,ALLY,369),1300)
reset(m,1,1,1);m.call(S['ffta_snapshot_begin'],FRAME,UNIT,ALLY,1);m.call(S['ffta_action_started'],UNIT,0,2,1)
check('reaction-exclusion',m.call(S['ffta_viking_outgoing_numerator'],UNIT,ALLY,0),1000);m.call(S['ffta_snapshot_end'],FRAME)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),samples=samples,scope=__doc__)
(ROM.parent/'damage-passives.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
