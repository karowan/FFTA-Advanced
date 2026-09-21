"""Composite native buffs must publish their real status identities to laws."""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-carrier-category-laws.py'
exec(compile(source.read_text().split('\nweapon_actions=')[0],str(source),'exec'))
failures=[];observations=[]
original_check=check
def check(k,a,b):
 checks[k]+=1
 if a!=b:failures.append(dict(check=k,case=case,actual=repr(a),expected=repr(b)))
cases=[(351,1,116,383,True,(24,25)),(359,1,117,0,True,(24,)),
 (360,1,117,0,True,()),(364,1,117,0,False,()),(368,2,118,399,True,()),
 (377,3,121,0,False,()),(378,3,121,0,False,(25,)),
 (391,3,120,0,False,()),(392,3,120,0,False,(24,25)),
 (394,5,123,0,False,(25,)),(395,5,123,0,False,(24,)),(397,5,123,0,False,(3,)),
 (398,5,123,0,True,(12,)),(400,5,123,0,False,(3,24,25)),(410,4,125,88,True,())]
for (action,race,jid,weapon,own,native),refresh,seed in itertools.product(cases,(False,True),(0,3)):
 case=(action,refresh,seed);fixture(action,seed);ns['job'](A,race,jid)
 m.put(A+0x2a,struct.pack('<5H',weapon,0,0,0,0));m.put(T+0x29,b'\0')
 m.put(0x02001940+362,bytes([5])*14)
 target=A if own else T
 if refresh:
  for bit in native:
   p=target+0xe8+bit//8;m.put(p,bytes((m.read(p,1)[0]|(1<<(bit%8)),)))
 prediction={bit:law(action,15,bit,target=target) for bit in (3,12,24,25)}
 execute(action,own);native_rows=rows(action,target)
 status=m.read(target+0xe8,8)
 for bit in native:check('actual-native-buff-applied-'+str(bit),bool(status[bit//8]&(1<<(bit%8))),True)
 for _,_,row in native_rows:
  mask=m.read(row+0x14,8)
  for bit in (3,12,24,25):
   expected=int(bit in native)
   check('native-buff-prediction-'+str(bit),prediction[bit],expected)
   check('committed-native-buff-'+str(bit),law(action,15,bit,target=target,mask=row+0x14),expected)
   m.put(0x08529348,bytes((15,bit)));m.put(STACK,struct.pack('<II',0,row+0x14))
   check('native-late-buff-wrapper-'+str(bit),m.call(0x08135750,A,target,action,0,stack=STACK),expected)
  check('beneficial-is-not-harmful',law(action,16,target=target,mask=row+0x14),0)
  observations.append(dict(action=action,refresh=refresh,seed=seed,status=status.hex(),mask=mask.hex(),prediction=prediction))
# Native self forecasts own two different copies of the same source. Prove
# that only registered query copies can alias; copied bytes alone cannot.
C=ns['C'];copy_a=0x03007200;copy_t=0x03007400;raw=0x0203e200
for action,condition,kind,query_mode in itertools.product((359,398),('normal','disable','silence','KO'),('same','foreign','raw'),(False,True)):
 case=('self-query-ownership',action,condition,kind,query_mode);fixture(action)
 ns['job'](A,1 if action==359 else 5,117 if action==359 else 123)
 m.put(A+0x2a,bytes(10));m.put(T+0x29,b'\0')
 if condition=='disable':m.put(A+0xeb,b'\x10')
 if condition=='silence':m.put(A+0xeb,b'\x08')
 if condition=='KO':m.put(A+0x18,bytes(2))
 check('owned-actor-opens',call('ffta_snapshotted_evaluated_init',copy_a,A),1)
 check('owned-target-opens',call('ffta_snapshotted_evaluated_init',copy_t,A if kind!='foreign' else T),1)
 m.put(raw,m.read(copy_t,264));target=raw if kind=='raw' else copy_t
 c=bytearray(0x34);struct.pack_into('<IIIHH',c,0,copy_a,target,target,action,0);c[0x26]=16 if query_mode else 0;m.put(C,c)
 before=m.read(A,264)+m.read(T,264)+m.read(record(A),22)+m.read(record(T),22)+m.read(0x030034b0,4)+m.read(0x03005e80,384)
 expected=int(query_mode and kind=='same' and condition not in ('disable','KO'))
 check('self-copy-admission',call('ffta_drk_eligibility' if action==359 else 'ffta_bard_eligibility',C),expected)
 if action==359:check('self-copy-healing',call('ffta_drk_healing',C),100 if query_mode and kind=='same' and condition!='KO' else 0)
 check('owned-query-live-purity',m.read(A,264)+m.read(T,264)+m.read(record(A),22)+m.read(record(T),22)+m.read(0x030034b0,4)+m.read(0x03005e80,384),before)
 call('ffta_snapshotted_evaluated_close',copy_t);call('ffta_snapshotted_evaluated_close',copy_a)
report=dict(passed=not failures,romSha1=meta['romSha1'],total=sum(checks.values()),checks=dict(checks),failures=failures,observations=observations)
(OUT/'carrier-buff-laws.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
assert not failures,failures[:8]
