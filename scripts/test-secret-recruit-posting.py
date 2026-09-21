"""Native recruit posting/expiry and original-to-retry transitions.

Eligibility flags/calendar are declared inputs. Whole native generator, linked
queue, town filtering, expiry and completion execute without replaced results.
Campaign acquisition of prerequisite flags and story scripts remain separate.
"""
import ast,collections,hashlib,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text(encoding='utf-8'))
path=pathlib.Path(meta['path']);ROM=path.read_bytes();LAB=path.parent
ledger=json.loads((ROOT/'build/reports/secret-recruit-sources.json').read_text(encoding='utf-8'))
missions=json.loads((ROOT/'build/reports/mission-item-dependencies.json').read_text(encoding='utf-8'))['installedRecords']
assert hashlib.sha1(ROM).hexdigest()==meta['romSha1']==ledger['candidateSha1']
FIX=LAB/'fixture-two-geomancers';proof=json.loads((FIX/'prepare-cache.json').read_text(encoding='utf-8'))
assert proof['inputs']['romSha1']==meta['romSha1']
for name,value in proof['outputs'].items():assert hashlib.sha1((FIX/name).read_bytes()).hexdigest()==value
base=(FIX/'battle-ready.ram').read_bytes();iw=(FIX/'battle-ready.iwram').read_bytes()
tree=ast.parse((ROOT/'scripts/test-battle-inventory.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM helper>','exec'))
m=ARM(iw);OUT=LAB/'secret-recruit-posting';OUT.mkdir(exist_ok=True)
counts=collections.Counter();cases=[];failures=[];case=None
BUFFER=0x02030000

def check(label,value):
 counts[label]+=1
 assert value,(case,label)

def flag(r,index,value=True):
 p=0x1f70+index//8;b=1<<(index&7);r[p]=(r[p]|b) if value else r[p]&~b

def initial(record):
 r=bytearray(base);r[0x1e79]=2;r[0x1f70:0x2030]=bytes(0xc0)
 r[0x21c8:0x28cc]=bytes(0x704);r[0x2b08:0x2c08]=bytes(256)
 for clause in record['unlock']:
  if clause['kind']=='counter':r[0x2030+clause['index']]=clause['value']
  elif clause['value'] in (0,1):flag(r,clause['index'],clause['value'])
 if record['eventLocation']:r[0x2cc3+(record['eventLocation']-1)*12]=1
 r[0x2fba]=record['pubMonth'] or 1
 return r

def reset(r):
 m.put(0x02000000,r);m.put(0x03000000,iw);m.w32(0x030034b0,0)

def queue():
 node=m.r32(0x020028c8);seen={};previous=0
 while node:
  assert 0x020025c8<=node<0x020028c8 and (node-0x020025c8)%12==0 and len(seen)<64
  ptr,prev,nxt=struct.unpack('<III',m.get(node,12))
  assert prev==previous and 0x020021c8<=ptr<0x020025c8 and (ptr-0x020021c8)%16==0
  mission=m.r16(ptr)&1023;assert mission and mission not in seen
  seen[mission]=ptr;previous,node=node,nxt
 return seen

def pub(ptr):
 towns=[]
 for town in range(8):
  m.put(BUFFER+256,b'\xa5'*4)
  count=m.call(0x080d0590,BUFFER,64,town)
  assert count<=64 and m.get(BUFFER+256,4)==b'\xa5'*4
  values=struct.unpack('<64I',m.get(BUFFER,256))
  if ptr in values[:count]:towns.append(town)
 return towns

try:
 # Hidden record400 is Shara's candidate template. Actual player offer381 is
 # a repeatable dispatch; do not equate template posting with visible access.
 ids=sorted({60,381}|{x['record'] for row in ledger['rows'] for x in row['missions']})
 for mission in ids:
  case=('posting',mission);record=missions[mission];r=initial(record);reset(r)
  m.call(0x080cfcd0,0);entries=queue()
  check('native-generator-constructs-source',mission in entries)
  ptr=entries[mission];towns=pub(ptr)
  check('native-pub-visibility',bool(towns)==(mission!=400))
  m.call(0x080cfcd0,0)
  check('native-generator-prevents-duplicate',queue()==entries)
  posted=m.get(0x02000000,0x40000)
  duration=m.get(ptr+3,1)[0]
  if duration!=255:
   for day in range(duration):m.call(0x080cf51c)
   cooldown=ROM[0x55ae4c+70*mission+64]
   if cooldown:
    check('expired-offer-enters-native-cooldown',m.get(ptr+2,1)[0]&0x1c==12 and m.get(ptr+3,1)[0]==cooldown)
    for day in range(cooldown):m.call(0x080cf51c)
   check('unaccepted-offer-expires-natively',mission not in queue())
   m.call(0x080cfcd0,0)
   check('expired-offer-reposts-under-same-eligibility',mission in queue())
   check('expired-offer-returns-to-pub',bool(pub(queue()[mission])))
  cases.append(dict(mission=mission,name=record['name'],towns=towns,duration=duration,
   cooldown=ROM[0x55ae4c+70*mission+64]))
  # Original special battle success commits its real completion flag. The
  # corresponding native monthly dispatch then offers the same character.
  row=next((x for x in ledger['rows'] if x['retryException'] and mission in x['originalMissions'] and mission!=x['retryException']),None)
  if row:
   case=('completed-original-to-retry',mission,row['retryException'])
   reset(posted);m.call(0x080d1e70,ptr,1)
   complete=mission+0x2ff
   check('original-completion-flag-written',bool(m.get(0x02001f70+complete//8,1)[0]&(1<<(complete&7))))
   target=missions[row['retryException']]
   m.put(0x02002fba,bytes([target['pubMonth'] or 1]))
   m.call(0x080cfcd0,0);retry=queue()
   check('completed-original-unlocks-native-retry',target['record'] in retry)
   check('native-retry-visible',bool(pub(retry[target['record']])))
   m.w32(0x030034b0,0)
   result=m.call(0x080d241c,target['record'],0x02002fc4)
   check('native-retry-generates-correct-special',result and m.get(0x02002fc8,1)[0]==row['type'])
   cases.append(dict(original=mission,retry=target['record'],candidateType=row['type']))
except BaseException as error:
 failures.append(dict(case=case,error=repr(error)))
 (OUT/'failure.ram').write_bytes(m.get(0x02000000,0x40000))
report=dict(passed=not failures,romSha1=meta['romSha1'],counts=dict(counts),cases=cases,failures=failures,
 inputs=dict(fixture=proof['outputs'],seed=0,towns=list(range(8))),scope=__doc__)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
assert not failures,failures
