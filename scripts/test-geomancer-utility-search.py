"""Deterministic native utility placement; no candidate outcome or score stub.

Fixed deployed groups, mastery, movement maps, HP/MP and field inputs. Native
admission, geometry, hit/damage and learned spell discovery execute unchanged.
Whole-turn scheduler/renderer acceptance remains a separate consumer.
"""
import collections,itertools,json,pathlib,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-geomancer-ai.py';ns={'__file__':str(source),'__name__':'utility_search_fixture'}
exec(compile(source.read_text(encoding='utf-8').split('# Wind at the old tile')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,STACK,NODE,GROUP,MOVE,BUFFER,prepare,position,wrappers=(ns[k] for k in
 ('m','S','meta','OUT','A','T','STACK','NODE','GROUP','MOVE','BUFFER','prepare','position','wrappers'))
base=ns['ns'];state,job,equip=(base[k] for k in ('state','job','equip'))
field,updraft=base['ns']['field'],base['ns']['updraft']
E=next(u for u in wrappers if u not in (A,T));checks=collections.Counter();cases=[];failures=[];case=None
from unicorn import UC_HOOK_MEM_WRITE,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_PC,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2
diagnostic=[];phase='setup'
def code_write(u,access,address,size,value,data):
 if len(diagnostic)<12:diagnostic.append(dict(phase=phase,write=hex(address),size=size,pc=hex(u.reg_read(UC_ARM_REG_PC)),sp=hex(u.reg_read(UC_ARM_REG_SP))))
def formula(u,address,size,data):
 if len(diagnostic)<12:diagnostic.append(dict(phase=phase,formula=[hex(u.reg_read(r)) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)],sp=hex(u.reg_read(UC_ARM_REG_SP))))
m.u.hook_add(UC_HOOK_MEM_WRITE,code_write,begin=0x03005e80,end=0x03005fff)
m.u.hook_add(UC_HOOK_CODE,formula,begin=0x08130200,end=0x08130200)

def check(k,actual,expected=True):
 checks[k]+=1
 if actual!=expected:failures.append(dict(check=k,case=case,actual=repr(actual),expected=repr(expected)))

def protected():
 return b''.join(m.read(u,264)+m.read(state(u),22) for u in (A,T,E))+m.read(0x030034b0,4)+m.read(0x03005e80,384)

def setup(action,condition,sp):
 members=(A,T) if condition=='no-enemy' else (A,T,E)
 prepare(action,members=members)
 for u in (A,T,E):
  job(u,3,121);m.put(u+0x2a,bytes(10));m.put(u+0x3a,bytes(2));m.put(u+0xe8,bytes(8))
  m.put(u+0x18,struct.pack('<4H',500,500,100,100));m.put(u+0x0c,bytes([1]*9));m.put(u+0x40,b'\xff'*0x90)
  m.put(u+0x20,struct.pack('<4H',70,40,80,40));m.call(0x080ca2e8,u,stack=sp)
 m.put(A+0x29,b'\0');m.put(T+0x29,bytes((128 if action==380 else 0,)));m.put(E+0x29,b'\x80');position(E,9,14)
 target=A if condition=='self' else T
 if condition=='self':position(T,12,14)
 if condition=='no-MP':m.put(A+0x1c,bytes(2))
 if condition=='no-enemy-MP':m.put(E+0x1c,bytes(2))
 if condition=='unlearned-enemy':m.put(E+0x40,bytes(0x90))
 if condition=='sleeping':m.put(A+0xeb,b'\x10')
 if condition=='blocked':m.put(MOVE,b'\x80'*256)
 if condition=='refresh':
  if action==377:updraft(A);updraft(T)
  else:field(A,1 if action==380 else 2)
 if condition=='redundant-field':field(A,1,6,14)
 if condition=='floating':
  for u in (A,T):m.put(u+0xfc,b'\x02')
 if condition=='surefoot':
  for u in (A,T):equip(u,'GEO-S2')
 if condition=='light-foot':
  for u in (A,T):job(u,4,29);equip(u,'DNC-S2')
  job(A,3,121) # Keep the caster's actual Geomancy command.
 if condition=='protected':field(A,2,4,14)
 if condition in ('ice-immune','protect-existing','refresh','redundant-field') and action==380:m.put(T+0x11,b'\x02')
 if condition=='protect-existing':field(A,2,4,14)
 if condition=='ally-damage':m.put(T+0x29,b'\0')
 if condition=='moved-self':
  position(T,12,14);target=A
  m.put(MOVE,b'\x80'*256);m.put(MOVE+14*16+6,b'\x02')
 # Populate the real native per-recipient rows. BDF9C must find the selected
 # anchor/action in these native20-byte records, not a fabricated positive flag.
 for i,u in enumerate(members):
  m.put(sp,bytes(8));m.call(0x080c2618,GROUP+i*808+4,wrappers[A],wrappers[u],action,stack=sp)
  count=bool(int.from_bytes(m.read(GROUP+i*808+14,2),'little'))
  m.put(GROUP+i*808+804,struct.pack('<H',int(count)))
 m.put(NODE+4,struct.pack('<I',wrappers[target]));m.put(NODE+0x28,bytes((0 if action==380 else 1,)))
 m.put(BUFFER-16,b'\xa5'*1056)
 return 0x080beac8 if target==A else 0x080bef28

matrix={377:('base','self','moved-self','refresh','no-MP','sleeping','blocked','no-enemy','floating','surefoot','light-foot','protected'),
 380:('base','ice-immune','refresh','redundant-field','no-MP','sleeping','blocked','surefoot','floating','protect-existing','ally-damage'),
 382:('base','self','moved-self','refresh','no-MP','sleeping','blocked','no-enemy','no-enemy-MP','unlearned-enemy','floating','surefoot')}
for action in matrix:
 for condition,sp in itertools.product(matrix[action],(STACK,STACK+4)):
  case=(action,condition,sp);diagnostic=[];phase='setup';entry=setup(action,condition,sp);before=protected();phase='search'
  for tick in range(257):
   try:more=m.call(entry,NODE,0,stack=sp)
   except Exception:
    from unicorn.arm_const import UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_SP
    print('Native search failure',case,tick,{k:hex(m.u.reg_read(r)) for k,r in
     (('pc',UC_ARM_REG_PC),('lr',UC_ARM_REG_LR),('sp',UC_ARM_REG_SP))},diagnostic,flush=True)
    raise
   check('scope-retired',m.read(0x0203f728,4),bytes(4))
   if not more:break
  else:raise AssertionError(('unbounded search',case))
  check('query-preserves-units-state-RNG-renderer',protected(),before)
  check('actual1024-byte-native-buffer-bounds',m.read(BUFFER-16,16)+m.read(BUFFER+1024,16),b'\xa5'*32)
  success=m.read(NODE+0x1b1,1)[0];coords=list(m.read(NODE+0x1ac,4));score=m.word(NODE+0x1c)
  rejected=condition in ('redundant-field','no-MP','sleeping','blocked','no-enemy','no-enemy-MP','unlearned-enemy','protected','protect-existing','ally-damage') or (action!=380 and condition=='refresh') or (action==382 and condition=='floating')
  check('useful-placement-only',success,int(not rejected))
  if success:
   check('positive-score',score>0);check('no-invented-choice',m.read(NODE+10,2),bytes(2))
   if condition in ('self','moved-self'):
    check('self-follows-proposed-origin',abs(coords[0]-coords[2])+abs(coords[1]-coords[3])<=1)
   if condition=='moved-self':check('only-legal-origin',coords[:2],[6,14])
   if action==380:check('Rime-covers-enemy',abs(coords[2]-5)+abs(coords[3]-14)<=1)
   if action==380 and condition=='refresh':
    check('Rime-relocation-removes-friendly-penalty',abs(coords[2]-4)+abs(coords[3]-14)>1)
    check('Rime-relocation-values-only-friendly-relief',score,600)
  cases.append(dict(case=case,success=success,score=score,coordinates=coords,callbacks=tick+1))
report=dict(passed=not failures,romSha1=meta['romSha1'],total=sum(checks.values()),checks=dict(checks),cases=cases,failures=failures,scope=__doc__)
(OUT/'geomancer-utility-search.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2));assert not failures,failures
