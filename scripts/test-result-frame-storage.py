"""Native Counter result scope: live external owner, isolation and retirement.

Actual queued native execution supplies the frame; diagnostic hooks only read
it. Forged/stale token cases are isolated getter inputs on captured memory.
"""
import collections,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP
source=ROOT/'scripts/test-integrated-dancer.py';ns={'__file__':str(source),'__name__':'result_storage_fixture'}
exec(compile(source.read_text().split('# The two separate native formula terms')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,fixture,execute=(ns[k] for k in ('m','S','meta','OUT','A','T','fixture','execute'))
fixture(0)
POOL=m.call(S['ffta_integrated_result_storage'],stack=ns['STACK']);assert POOL
END,ACTIVE=POOL+6592,0x0203ff48
checks=collections.Counter();events=[];captured=[];outcomes=[];case=None
def check(k,v):checks[k]+=1;assert v,(k,case)
def observe(u,address,size,data):
 event=u.reg_read(UC_ARM_REG_R2);actor=u.reg_read(UC_ARM_REG_R0);action=u.reg_read(UC_ARM_REG_R1)
 root=m.word(ACTIVE);origin=m.word(root+792) if root else 0
 row=dict(event=event,actor=actor,action=action,root=root,origin=origin)
 events.append(row)
 if event==2 and actor==T:
  check('native-reaction-uses-reserved-frame',POOL+4<=root<END and (root-POOL-4)%824==0)
  token=m.word(root-4)
  check('exact-live-stack-token',u.reg_read(UC_ARM_REG_SP)<=token<=0x03007ffc and m.word(token)==root)
  check('reaction-origin-is-independent',origin==2 and m.word(root+812)==T)
  previous=m.word(root+8)
  check('reaction-retains-primary-parent',0x03000000<=previous<0x03008000 and m.word(previous+812)==A)
  captured.append((m.read(0x02000000,0x40000),m.read(0x03000000,0x8000),root,token,u.reg_read(UC_ARM_REG_SP)))
hook=m.u.hook_add(UC_HOOK_CODE,observe,begin=S['ffta_integrated_action_event']&~1,end=S['ffta_integrated_action_event']&~1)
try:
 for action in (0,409):
  for seed in (0,3,18):
   case=('actual native Counter',action,seed);fixture(action,seed=seed)
   bank=m.word(m.word(0x080cd538)+4)
   index=next(i for i in range(1,144) if int.from_bytes(m.read(bank+8*i+4,2),'little')==8 and m.read(bank+8*i+6,1)==b'\x02')
   m.put(T+0x3a,bytes((index,)));m.put(T+0x40+index,b'\xff')
   m.put(T+0x2a,struct.pack('<5H',1,0,0,0,0));m.put(T+0x20,struct.pack('<H',100))
   m.put(POOL,bytes(END-POOL));m.put(POOL-4,b'\xd7'*4);m.put(END,b'\xd7'*4)
   before=len(captured);execute(action)
   output=ns['regs'][0];count=m.read(output+0x26bd,1)[0]
   queued=sum(m.word(m.word(output+i*0x2c4))==T for i in range(1,count))
   check('each-actual-native-Counter-has-one-fresh-frame',len(captured)==before+queued)
   check('bounded-native-reaction-count',queued in (0,1))
   outcomes.append(dict(action=action,seed=seed,queuedCounters=queued,
                        actorXY=list(m.read(A+0xf6,2)),targetXY=list(m.read(T+0xf6,2))))
   check('complete-pool-released',m.read(POOL,END-POOL)==bytes(END-POOL))
   check('pool-neighbor-guards',m.read(POOL-4,4)+m.read(END,4)==b'\xd7'*8)
   check('primary-root-restored-then-closed',m.read(ACTIVE,4)==bytes(4))
finally:m.u.hook_del(hook)
for action in (0,409):check('nonvacuous-Counter-evidence-'+str(action),any(o['action']==action and o['queuedCounters']==1 for o in outcomes))
ram,iw,root,token,sp=captured[0];call_stack=sp&~7
for mutation in ('valid','token-value','token-pointer','expired-stack','copied-RAM','bad-self','bad-count','closed'):
 case=('external owner query',mutation);m.put(0x02000000,ram);m.put(0x03000000,iw)
 if mutation=='token-value':m.put(token,bytes(4))
 if mutation=='token-pointer':m.put(root-4,struct.pack('<I',0x02000100))
 if mutation=='expired-stack':m.put(root-4,struct.pack('<I',call_stack-256))
 if mutation=='copied-RAM':
  copied=0x0202c000;m.put(copied,m.read(root,820));m.put(copied+4,struct.pack('<I',copied));m.put(ACTIVE,struct.pack('<I',copied))
 if mutation=='bad-self':m.put(root+4,bytes(4))
 if mutation=='bad-count':m.put(root+12,struct.pack('<I',65))
 if mutation=='closed':m.put(root-4,bytes(824))
 before=m.read(0x02000000,0x40000)
 check('only-exact-live-frame-is-current',m.call(S['ffta_action_origin'],stack=call_stack)==(2 if mutation=='valid' else 0))
 check('getter-does-not-repair-or-mutate-foreign-state',m.read(0x02000000,0x40000)==before)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),events=events,outcomes=outcomes,
            scope=__doc__)
(OUT/'result-frame-storage.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
