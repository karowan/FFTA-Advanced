"""Native Viking growth, prerequisites, teaching, cross-job equipment and stock."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT/'tools/arm-python'),str(ROOT/'scripts')]
from unicorn import *
from unicorn.arm_const import *
P=ROOT/'build/expansion/probes';meta=_load_job_candidate(P/'viking/current.json');ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
parent=json.loads((P/'job-state/current.json').read_text());fix=pathlib.Path(meta['path']).parent/'executor'
ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes()
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m=ARM(rom,iw);counts=collections.Counter()
old={p[2]:int(p[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=l.split())==3}
registry=json.loads((ROOT/'build/expansion/registry.json').read_text());items=[x for x in registry['items'] if x['group']=='VIK']
def check(k,a,b):
 counts[k]+=1;assert a==b,(k,a,b)
def reset(job=118):
 m.put(0x02000000,ram);m.put(0x03000000,iw);m.put(UNIT+5,bytes([job,2,job]));m.put(UNIT+0x35,bytes([job]));m.put(UNIT+0x2a,bytes(10));m.put(UNIT+0x3a,bytes(2));m.put(UNIT+0x40,bytes(142))
for selector,value in {1:2,2:0,0x17:44,0x18:28,0x19:98,0x1a:84,0x1b:82,0x1c:76,0x1d:68,0x1e:3,0x1f:2,0x20:40,0x21:0,0x29:88,0x2a:28,0x2b:10,0x2c:84,0x2d:82,0x2e:76,0x2f:68}.items():
 check('approved-native-profile',m.call(0x080c8570,118,118,selector),value)
check('all14lessons-visible-to-consumer',m.call(old['ffta_job_lesson_count'],118),14)
for warriors,monks in itertools.product(range(5),range(3)):
 reset(13)
 for job,n in [(13,warriors),(17,monks)]:
  indexes=[m.call(old['ffta_job_lesson_at'],job,i) for i in range(m.call(old['ffta_job_lesson_count'],job))]
  action_indexes=[]
  for i in indexes:
   address=m.call(0x080cd480,2,i);row=m.read(address,8)
   if row[6]==1:action_indexes.append(i)
  for i in action_indexes[:n]:m.put(UNIT+0x40+i,b'\xff')
 check('Warrior3-WhiteMonk1-only',m.call(old['ffta_new_job_eligible'],UNIT,118),int(warriors>=3 and monks>=1))
for item in items:
 ident=item['romItemId']
 for job in (118,16,18):
  reset(job);allowed=m.call(0x080cb48c,UNIT,ident,0)&1
  check('legal-axe-transfer',allowed,int(job==18))
  if allowed:continue
  m.call(old['ffta_native_give_item'],ident,1);m.call(0x080caf78,UNIT,ident,0)
  learned=[i for i in range(91,105) if m.read(UNIT+0x40+i,1)[0]&128]
  expected=[x['abilityIndex'] for x in item['teaching'] if x['jobId']==job]
  check('native-equipment-teaching-only-Viking',learned,expected)
  for i in expected:
   check('equipment-is-not-mastery',m.read(UNIT+0x40+i,1),b'\x80')
  m.call(0x080caf78,UNIT,0,0)
  check('unmastered-lessons-revoked-on-unequip',[i for i in range(91,105) if m.read(UNIT+0x40+i,1)[0]&128],[])
  for i in expected:m.put(UNIT+0x40+i,b'\xff')
  m.call(0x080caf78,UNIT,ident,0);m.call(0x080caf78,UNIT,0,0)
  check('mastered-lessons-retained',[i for i in range(91,105) if m.read(UNIT+0x40+i,1)[0]&128],expected)
# Independently approved S0/S1/S2/S3 mapping, with all non-monotonic flag sets
# and original town-stock tier keys. Cyril2 and Sprohm3 are the only stores.
gates={392:0,393:0,394:774,395:774,396:780,397:780,398:786,399:786,448:774}
check('weapon-scope',set(gates),{x['romItemId'] for x in items})
for flags,town,tier in itertools.product(range(8),range(2,7),(0,10,20)):
 reset()
 for bit,flag in enumerate((774,780,786)):m.call(0x080c9574,flag,int(bool(flags&(1<<bit))))
 count=m.call(old['ffta_shop_buy_list'],0x02024000,2,tier,town)
 ids=[struct.unpack('<H',m.read(0x02024000+4*i,2))[0] for i in range(count)]
 expected={item for item,flag in gates.items() if town in (2,3) and (flag==0 or bool(flags&(1<<(774,780,786).index(flag))))}
 check('all-shipment-town-tiers',{i for i in ids if i in gates},expected)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(counts),scope=__doc__)
(ROM.parent/'content-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
