"""Native law warnings: possibility, prevention, owned copies and query purity."""
import collections,itertools,json,pathlib,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-custom-status-laws.py';ns={'__file__':str(source),'__name__':'custom_law_query_fixture'}
exec(compile(source.read_text().split('\nfor action,condition,seed in itertools.product')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,STACK,regs,reset,execute,call,half,state,job,equip,wrappers=(ns[k] for k in
 ('m','S','meta','OUT','A','T','STACK','regs','reset','execute','call','half','state','job','equip','wrappers'))
checks=collections.Counter();samples=[];case=None;LAW=0x0203e000;originalT=T

def check(k,a,b):checks[k]+=1;assert a==b,(k,case,a,b)

def native_lesson(unit,effect,kind):
 bank=m.word(m.word(0x080cd538)+4)
 index=next(i for i in range(1,144) if half(bank+8*i+4)==effect and m.read(bank+8*i+6,1)[0]==kind)
 m.put(unit+(0x3b if kind==3 else 0x3a),bytes((index,)));m.put(unit+0x40+index,b'\xff')
 check('actual-native-equipment',m.call(0x080cd50c if kind==3 else 0x080cd4d4,unit,stack=STACK),effect)

def setup(action,condition):
 global T
 T=originalT;reset(action)
 race,jid,weapon={355:(1,116,383),373:(2,118,399),379:(3,121,0),404:(4,124,0),405:(4,124,0)}[action]
 job(A,race,jid);m.put(A+0x2a,struct.pack('<5H',weapon,0,0,0,0))
 if condition.startswith('cureall'):
  T=0x02000188;job(T,5,42);m.put(T+0x18,struct.pack('<4H',500,500,100,100));m.put(T+0xe8,bytes(8));m.put(T+0x29,b'\0');m.put(A+0x29,b'\x80')
  m.put(T+0x3a,bytes(2));m.put(T+0x2a,bytes(10));equip(T,'CHM-R2')
  m.put(0x02001940+374,bytes((0 if condition=='cureall-empty' else 3,)))
  if condition=='cureall-disabled':m.put(T+0xeb,b'\x80')
 else:
  job(T,1,2);m.put(T+0x29,b'\x80');m.put(T+0x3a,bytes(2))
 m.put(state(T),bytes(22));m.put(call('ffta_owned_wound',T),bytes(2))
 if condition=='refresh':
  ns['T']=T;ns['existing'](action)
 if condition=='inoculated':call('ffta_inoculated_grant',T,0)
 if condition=='immune':native_lesson(T,11,3)
 if condition=='MP':native_lesson(T,13,2)
 if condition=='targetKO':m.put(T+0x18,bytes(2))
 if condition=='actorKO':m.put(A+0x18,bytes(2))
 if condition=='petrify':m.put(T+0xe8,b'\x40')
 if condition=='lethal':m.put(T+0x18,b'\x01\x00')
 if condition=='friend':m.put(T+0x29,b'\0')
 if condition=='confused':m.put(A+0xeb,b'\x10')
 if condition=='absorbed':m.put(T+0x0c,bytes([4]*9))
 if condition in ('strong-Wisp','strong-heat'):
  m.put(state(T)+17,b'\x40');m.put(state(T)+18,b'\x01')
  if condition=='strong-heat':m.put(0x091f0000+14*16+4,b'\x08')
 if condition=='shell':job(T,4,125);equip(T,'MYK-R1')
 if condition=='cureall-inoculated':call('ffta_inoculated_grant',T,0)
 ns['T']=T

def query(action,a,t,residue=0):
 m.put(LAW,bytes(4)+bytes((16,))+bytes(11));m.put(STACK+residue,struct.pack('<4I',0,0,0,LAW))
 receipt=call('ffta_battle_workspace',0x2620)
 locations=[(a,264),(t,264),(state(a),22),(state(t),22),(0x02001940,512),(0x0200f3f0,0x34),
            (receipt,64),(0x030034b0,4),(0x0203ff44,8),(0x03005e80,384)]
 before=[m.read(p,n) for p,n in locations]
 value=m.call(0x081343c8,a,t,action,0,stack=STACK+residue)
 for (p,n),b in zip(locations,before):check('query-preserves-'+hex(p),m.read(p,n),b)
 return value

conditions=('normal','refresh','inoculated','immune','MP','targetKO','actorKO','petrify','lethal','friend','confused','cureall-stock','cureall-empty','cureall-disabled','cureall-inoculated','strong-Wisp','strong-heat','shell')
for action,condition,residue in itertools.product((355,373,379,404,405),conditions,(0,4)):
 case=(action,condition,residue);setup(action,condition)
 expected=condition not in ('inoculated','immune','targetKO','actorKO','petrify','friend','confused','cureall-stock','cureall-inoculated')
 if condition in ('lethal','MP') and action!=373:expected=False
 if condition=='confused' and action==373:expected=True
 if condition=='strong-Wisp' and action==379:expected=False
 result=query(action,A,T,residue);check('native-law-expected-possibility',result,int(expected))
 # Explicit evaluated copies carry their own extension and exact origin.
 copyA,copyT=0x03007400,0x03007600
 check('actor-copy-opens',call('ffta_snapshotted_evaluated_init',copyA,A),1)
 check('target-copy-opens',call('ffta_snapshotted_evaluated_init',copyT,T),1)
 check('owned-copy-law-parity',query(action,copyA,copyT,residue),result)
 call('ffta_snapshotted_evaluated_close',copyT);call('ffta_snapshotted_evaluated_close',copyA)
 samples.append(dict(action=action,condition=condition,residue=residue,result=result))

# Provoke's installed native eligibility permits a confused actor; do not
# impose the damage-command exclusion on that different application path.
observed=False
for seed in (0,1,2,3):
 case=('native-confused-Provoke',seed);setup(373,'confused');warning=query(373,A,T)
 m.put(0x030034b0,struct.pack('<I',seed));execute(373)
 if call('ffta_viking_challenger',T):check('confused-Provoke-execution-warned',warning,1);observed=True
check('nonvacuous-confused-Provoke',observed,True)

debits=collections.Counter()
for action,condition,seed in itertools.product((355,373,379,404,405),
 ('cureall-stock','cureall-empty','cureall-disabled','cureall-inoculated'),(0,1,2,3)):
 case=('native-Cureall',action,condition,seed);setup(action,condition)
 # The actual Moogle party recipient owns player inventory; leave monster
 # units in their original cohort and move them away from the selected cell.
 for u,x,y in ((originalT,0,0),(T,5,14)):
  m.put(u+0xf6,bytes((x,y)));m.put(wrappers[u]+8,struct.pack('<3H',32*x+16,256,32*y+16))
 warning=query(action,A,T);before=m.read(0x02001940+374,1)[0]
 m.put(0x030034b0,struct.pack('<I',seed));execute(action)
 rows=[]
 for i in range(14):
  o=regs[0]+i*0x2c4
  if m.word(o)!=wrappers[A] or half(o+16)!=action:continue
  for j in range(m.read(o+0x2c0,1)[0]):
   row=o+0x20+j*0x2c;w=m.word(row)
   if w and m.word(w)==T:rows.append(row)
 check('native-party-recipient-row',bool(rows),True)
 hit=any(half(r+12)&128 and not half(r+12)&64 for r in rows) if action==373 else 0<half(T+0x18)<500
 prevented=condition in ('cureall-stock','cureall-inoculated')
 applied=bool(ns['effect'](action));check('actual-custom-prevention',applied,bool(hit and not prevented))
 spent=before-m.read(0x02001940+374,1)[0]
 check('exact-Cureall-debit',spent,int(hit and condition=='cureall-stock'))
 debits[action]+=spent
 for row in rows:check('late-law-agrees-with-prevention',ns['query'](action,row+0x14,half(row+0x1e)),int(applied))
 if applied:check('actual-unprevented-application-warned',warning,1)
for action in (355,373,379,404,405):check('nonvacuous-Cureall-debit-'+str(action),debits[action]>0,True)

for condition,seed in itertools.product(('strong-Wisp','strong-heat'),(0,1,2,3)):
 case=('native-strong-Wisp',condition,seed);setup(379,condition);warning=query(379,A,T)
 m.put(0x030034b0,struct.pack('<I',seed));execute(379)
 hit=0<half(T+0x18)<500;expected=int(hit and condition=='strong-heat')
 o=regs[0];rows=[o+0x20+j*0x2c for j in range(m.read(o+0x2c0,1)[0]) if m.word(m.word(o+0x20+j*0x2c))==T]
 check('strong-Wisp-native-row',bool(rows),True)
 for row in rows:check('strong-Wisp-refresh-law',ns['query'](379,row+0x14,half(row+0x1e)),expected)
 check('strong-Wisp-warning',warning,int(condition=='strong-heat'))

# Damage uncertainty is a real native-execution witness, not a chosen oracle
# value: seed3 succeeds, then lower the target's HP near its observed damage.
for action in (355,379,404,405):
 case=('near-KO',action);setup(action,'normal');m.put(0x030034b0,struct.pack('<I',3));execute(action)
 damage=500-half(T+0x18);check('positive-witness-damage',damage>0,True)
 found=False
 for hp in range(max(2,damage-5),damage+6):
  setup(action,'normal');m.put(T+0x18,struct.pack('<H',hp));warning=query(action,A,T)
  for seed in (0,1,2,3,18):
   setup(action,'normal');m.put(T+0x18,struct.pack('<H',hp));m.put(0x030034b0,struct.pack('<I',seed));execute(action)
   applied=bool(ns['effect'](action))
   if applied:check('every-observed-surviving-application-warned',warning,1);found=True
 check('nonvacuous-near-KO-survivor',found,True)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),samples=samples)
(OUT/'custom-status-law-prediction.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
