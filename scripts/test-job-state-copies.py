"""All canonical sources through independently owned copy types and back.

Native allocation/copy/clear/free run unmodified. Fixed initial records supply
an independent byte-pattern oracle; no callback injects results at execution.
"""
import ast,collections,hashlib,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'build/expansion/probes'
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=json.loads((P/'job-state/current.json').read_text());rom=pathlib.Path(meta['path']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
symbols=meta['symbols'];OUT=pathlib.Path(meta['path']).parent/'copy-matrix';OUT.mkdir(exist_ok=True)
fixture=pathlib.Path(meta['path']).parent/'fixture'
iwram=(fixture/'battle-ready.iwram').read_bytes()
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
checks=collections.Counter()
def check(n,a,b):checks[n]+=1;assert a==b,(n,a,b)
units=[UNIT+i*264 for i in range(24)]+[0x02002fc4+i*264 for i in range(12)]
copy_entry=struct.unpack_from('<I',rom,0x36d4bc)[0]
clear_entry=struct.unpack_from('<I',rom,0x36d4b8)[0]
for residue in (0,4):
 m=ARM(rom,iwram)
 def call(n,*a):return m.call(symbols[n],*a,stack=STACK+residue)
 def w32(p,x):m.put(p,struct.pack('<I',x))
 def record(p):return call('ffta_job_state',p)
 def origin(p):return call('ffta_job_origin',p)
 def potion(p):return call('ffta_job_potion',p)
 m.put(0x02000000,bytes(0x40000));m.put(0x02001e70,b'FFTAEXP1\x01')
 m.call(0x080070c8,0x02018000,0x27000);w32(0x0200f434,0x02018000);call('ffta_job_reset')
 manager=m.call(0x08022840,0x430);w32(0x0200f4b0,manager);call('ffta_manager_register',manager)
 selection=m.call(0x08022840,0x3840);w32(0x0200f454,selection);call('ffta_selection_register',selection)
 party=m.call(0x08022840,0x7280);w32(0x03002818,party);call('ffta_party_copy_register')
 snapshot=m.call(0x08022840,0x1140);call('ffta_snapshot_register',snapshot)
 evaluated=call('ffta_evaluated_allocate',264)
 stack=0x03007500;call('ffta_evaluated_init',stack,UNIT)
 views=[manager+0x40,manager+0x148,selection+0xa4c,party+0x1be4,
        *[snapshot+4+i*264 for i in range(13)],evaluated,stack]
 groups=[units,views[:2],[views[2]],[views[3]],views[4:17],[evaluated],[stack]]
 output=0x02008000
 for group in groups:
  for unit in group:
   for capacity in (0,len(group)-1,len(group),36):
    m.put(output-4,b'\xD7'*152)
    count=call('ffta_job_peers',unit,output,capacity)
    check('complete peer enumeration',count,len(group) if capacity>=len(group) else 0)
    wanted=b''.join(struct.pack('<I',p) for p in group) if count else b''
    check('peer output and guards',m.read(output-4,152),b'\xD7'*4+wanted+b'\xD7'*(148-len(wanted)))
 for i,dest in enumerate(views):m.call(copy_entry,dest,units[i],264,stack=STACK+residue)
 for group in groups:
  represented={origin(p):p for p in group}
  for token in range(37):
   check('same owner lookup',call('ffta_job_peer',group[0],token),represented.get(token,0) if token else 0)
 m.call(copy_entry,views[1],units[0],264,stack=STACK+residue)
 check('ambiguous peer rejected',call('ffta_job_peer',views[0],1),0)
 for index,unit in enumerate(units):
  payload=bytes((index*29+j*19+3)&255 for j in range(22));preference=index%3 if index<24 else 0
  m.put(record(unit),payload)
  if index<24:m.put(potion(unit),bytes([preference]))
  for dest in views:
   before=m.read(0x0203f400,808)
   m.call(copy_entry,dest,unit,264,stack=STACK+residue)
   check('copy record',m.read(record(dest),22),payload);check('exact origin',origin(dest),index+1)
   check('copied preference',m.read(potion(dest),1),bytes([preference]))
   check('source records untouched',m.read(0x0203f400,808),before)
   # Every owner may be the source of another exact owned copy.
   second=views[0] if dest!=views[0] else views[1]
   m.call(copy_entry,second,dest,264,stack=STACK+residue)
   check('copy of copy',m.read(record(second),22),payload);check('copy of copy origin',origin(second),index+1)
   m.call(copy_entry,dest,dest,264,stack=STACK+residue)
   check('self copy',m.read(record(dest),22),payload)
   changed=bytes(x^0x5a for x in payload);m.put(record(dest),changed)
   check('modified copy isolated',m.read(record(unit),22),payload)
   m.call(copy_entry,unit,dest,264,stack=STACK+residue)
   check('native rollback',m.read(record(unit),22),changed);check('canonical origin after restore',origin(unit),index+1)
   if index<24:check('preference rollback',m.read(potion(unit),1),bytes([preference]))
   m.put(record(unit),payload)
   for length in (0,4,260,263,265):
    # Bookkeeping callback only for unusual byte lengths: actual native generic
    # copy alignment contracts are tested by their own consumer suite.
    prior=m.read(record(dest),22);call('ffta_on_unit_copy',dest,unit,length)
    check('partial copy unchanged',m.read(record(dest),22),prior)
   m.call(clear_entry,dest,264,stack=STACK+residue)
   check('whole copy clear',m.read(record(dest),22),bytes(22));check('cleared origin',origin(dest),0)
 for dest in views:
  m.put(record(dest),b'\xF3'*22);m.call(copy_entry,dest,0x02010000,264,stack=STACK+residue)
  check('unknown source clears',m.read(record(dest),22),bytes(22));check('unknown source origin',origin(dest),0)
  for offset in (1,4,263):
   check('foreign interior state',record(dest+offset),0);check('foreign interior origin',origin(dest+offset),0)
 call('ffta_evaluated_close',stack);check('closed stack rejected',record(stack),0)
 # Native persistent reorder runs outside stack evaluation. Independent heap
 # owners stay alive across the menu event and must follow source-token moves.
 active=views[:-1]
 for i,dest in enumerate(active):
  m.call(copy_entry,dest,units[i],264,stack=STACK+residue)
  m.put(record(dest),bytes([2,3,1,6,7,4,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]))
 call('ffta_job_swap',2,3)
 for i,dest in enumerate(active):
  check('copy links reindexed',m.read(record(dest),6),bytes([2,4,1,6,7,3]))
  check('copy origin reindexed',origin(dest),4 if i==2 else 3 if i==3 else i+1)
 call('ffta_job_forget_origin',4)
 for i,dest in enumerate(active):
  check('forgotten ward source clears active',m.read(record(dest),6),bytes([2,0,0,6,7,3]))
  check('forgotten copy origin',origin(dest),0 if i==2 else 3 if i==3 else i+1)
 call('ffta_job_forget_origin',3)
 for dest in active:check('forgotten challenge source',m.read(record(dest)+5,1),b'\0')
 for allocation,owned in [(manager,views[:2]),(selection,[views[2]]),(party,[views[3]]),
                           (snapshot,views[4:17]),(evaluated,[evaluated])]:
  m.call(0x08022854,allocation,stack=STACK+residue)
  for unit in owned:check('retired state',record(unit),0);check('retired origin',origin(unit),0);check('retired preference',potion(unit),0)
 # Independent canonical permutation oracle; all valid slot pairs plus invalid
 # values. Only the22-byte records and two declared link fields may move.
 payload=bytearray(bytes((i*31+j*17+9)&255 for i in range(36) for j in range(22)))
 for i in range(36):payload[i*22+1]=i+1;payload[i*22+5]=36-i
 for left in range(25):
  for right in range(25):
   m.put(0x0203f410,payload);before=m.read(0x02000000,0x40000);call('ffta_job_swap',left,right)
   expected=bytearray(payload)
   if left<24 and right<24:
    expected[left*22:(left+1)*22],expected[right*22:(right+1)*22]=payload[right*22:(right+1)*22],payload[left*22:(left+1)*22]
    for i in range(36):
     for byte in (1,5):
      p=i*22+byte
      if expected[p]==left+1:expected[p]=right+1
      elif expected[p]==right+1:expected[p]=left+1
   after=m.read(0x02000000,0x40000)
   check('all canonical roster permutations',after[0x3f410:0x3f728],bytes(expected))
   check('roster only owned bank writes',after[:0x3f410]+after[0x3f728:],before[:0x3f410]+before[0x3f728:])
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),
 scope='36 canonical sources,19 owned views, copy chains, native rollback, preferences, partial/full clear, foreign and retired owners, both stack residues. Roster permutation and linked-status policy remain separate.')
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
