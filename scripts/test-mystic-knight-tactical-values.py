"""Native tactical values with independent resource caps and prevention controls."""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-mystic-knight-resources.py';ns={'__file__':str(source),'__name__':'mystic_tactical_fixture'}
exec(compile(source.read_text(encoding='utf-8').split('conditions=')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,STACK,fixture,call,record,protected=(ns[x] for x in ('m','S','meta','OUT','A','T','STACK','fixture','call','record','protected'))
base=ns['ns'];wrappers=base['wrappers'];half=ns['half'];signed=ns['signed'];ROW=0x02028000
checks=collections.Counter();failures=[];samples=[];case=None

def check(k,a,b):
 checks[k]+=1
 if a!=b:failures.append(dict(check=k,case=case,actual=repr(a),expected=repr(b)))
def pair(action,sp):
 before=protected();context=m.read(0x0200f3f0,0x34)
 # Custom forecasting helpers restore their entry context; original public
 # native row/score routines deliberately replace the global query context.
 if action==423:call('ffta_myk_ai_break_value',A,T)
 else:call('ffta_myk_ai_strike_value',100,A,T,action)
 check('helper-preserves-context',m.read(0x0200f3f0,0x34),context)
 check('helper-preserves-live-state-RNG',protected(),before)
 scores=[signed(m.call(f,wrappers[A],wrappers[T],action,0,stack=sp)) for f in (S['ffta_ai_original_score'],0x080bdecc)]
 rows=[]
 for entry in (S['ffta_ai_original_row'],0x080c2618):
  m.put(ROW,bytes(20));m.put(sp,struct.pack('<II',88,0));m.call(entry,ROW,wrappers[A],wrappers[T],action,stack=sp);rows.append(m.read(ROW,20))
 check('queries-preserve-units-job-RNG-code',protected(),before)
 check('native-willingness-probability-preserved',rows[1][16],rows[0][16] if int.from_bytes(rows[1][10:12],'little') else 0)
 check('retired-query-roots' ,m.read(0x0203ff44,8)+m.read(0x0203f728,4),bytes(12))
 return scores,rows
for action,condition,sp in itertools.product(range(410,421),('bare','prepared','full','nearly-full','starved','overkill','undead','zero','damage-mp','silenced','ally'),(STACK,STACK+4)):
 case=(action,condition,sp);fixture(action);m.put(m.word(0x0200f438)+4,b'\0')
 base['hp'](A,100,500,20);base['hp'](T,500,500,99)
 if condition!='bare':call('ffta_myk_grant',A,action-409)
 if condition=='full':base['hp'](A,500,500,100)
 if condition=='nearly-full':base['hp'](A,499,500,99)
 if condition=='starved':base['hp'](T,500,500,0)
 if condition=='overkill':base['hp'](T,1,500,5)
 if condition=='undead':m.put(T+0x29,b'\x88')
 if condition=='zero':base['grant'](T,33)
 if condition=='silenced':base['grant'](A,27)
 if condition=='ally':m.put(T+0x29,b'\0')
 if condition=='damage-mp':
  base['job'](T,1,2);ns['native_lesson'](T,13,2);m.put(T+0x1c,struct.pack('<HH',999,999))
 damage=signed(call('ffta_integrated_mystic_effect_preview',A,T,action,88,0))
 removed=min(max(0,damage),half(T+0x18));expected=0
 if condition not in ('zero','damage-mp','silenced','ally') and removed:
  if condition=='bare':expected+=20
  if action==416:
   amount=min(removed*35//100,half(A+0x1a)*15//100)
   if condition!='undead':amount=min(amount,half(A+0x1a)-half(A+0x18))
   expected+=-amount if condition=='undead' else amount
  if action==419:
   loss=min(removed//4,10,half(T+0x1c));mp=half(A+0x1c)-8
   gain=min(loss,mp if condition=='undead' else half(A+0x1e)-mp)
   expected+=loss-gain if condition=='undead' else loss+gain
 scores,rows=pair(action,sp)
 check('native-score-exact-resource-and-preparation-value',scores[1]-scores[0],expected if scores[0] else 0)
 old,new=[struct.unpack_from('<h',r,12)[0] for r in rows]
 check('native-row-exact-resource-and-preparation-value',new-old,expected if old else 0)
 samples.append(dict(case=case,damage=damage,expected=expected,scores=scores))
for condition,sp in itertools.product(('healthy','near-KO','astra','immunity','inoculated','petrified','silenced','wrong-weapon','ally','KO'),(STACK,STACK+4)):
 case=('Petrify',condition,sp);fixture(423);m.put(m.word(0x0200f438)+4,b'\0')
 if condition=='near-KO':base['hp'](T,1,500,99)
 if condition=='astra':base['grant'](T,4)
 if condition=='immunity':base['job'](T,1,2);ns['native_lesson'](T,11,3)
 if condition=='inoculated':call('ffta_inoculated_grant',T,0)
 if condition=='petrified':base['grant'](T,6)
 if condition=='silenced':base['grant'](A,27)
 if condition=='wrong-weapon':m.put(A+0x2a,struct.pack('<H',1))
 if condition=='ally':m.put(T+0x29,b'\0')
 if condition=='KO':base['hp'](T,0,500,99)
 scores,rows=pair(423,sp);value=struct.unpack_from('<h',rows[1],12)[0]
 if condition in ('healthy','near-KO'):
  chance=struct.unpack_from('<h',rows[0],12)[0]
  check('Petrify-neutralizes-current-HP',value,chance+half(T+0x18)*chance//100)
  check('Petrify-row-score-agree',scores[1],value)
 else:
  check('no-prevented-Petrify-value',scores[1],0);check('no-prevented-Petrify-candidate',int.from_bytes(rows[1][10:12],'little'),0)
 samples.append(dict(case=case,scores=scores,rowValue=value))
# Isolated deterministic ordering contract: complete native records are moved,
# not modified; willingness, law flags and unrelated actions stay intact.
GROUP=0x02029000
for action,condition in itertools.product((410,416,419,423),('useful','worse','free-KO','no-candidate')):
 case=('order',action,condition);fixture(action);data=bytearray(0x290c)
 struct.pack_into('<I',data,0,wrappers[T]);struct.pack_into('<H',data,804,3);struct.pack_into('<H',data,0x2908,1)
 for i,(a,v) in enumerate(((23,200),(0,100),(action,150 if condition!='worse' else 90))):
  struct.pack_into('<HH3HHhhBBH',data,4+i*20,a,88,21,0,0,int(condition!='no-candidate' or i!=2),v,100,100,0,0)
 if condition=='free-KO':base['hp'](T,1,500,99)
 m.put(GROUP-16,b'\xa5'*16);m.put(GROUP,data);m.put(GROUP+len(data),b'\xa5'*16);before=protected()
 call('ffta_myk_ai_order',GROUP);actual=m.read(GROUP,len(data));expected=bytearray(data)
 if condition=='useful':expected[24:44],expected[44:64]=data[44:64],data[24:44]
 check('exact-tactical-row-order',actual,bytes(expected));check('order-keeps-live-state',protected(),before)
 check('order-guards',m.read(GROUP-16,16)+m.read(GROUP+len(data),16),b'\xa5'*32)
# Differential forwarding through the installed native sorting entry. The
# wrapper may reorder Mystic rows only; ordinary hostile/ally groups preserve
# exact native EWRAM writes, RNG and preserved ABI at both stack alignments.
AI=0x02029000;OUTPUT=0x02025000
for side,sp in itertools.product((0,1),(STACK,STACK+4)):
 case=('native-rank-forwarding',side,sp);fixture(410);data=bytearray(0x5274)
 struct.pack_into('<I',data,4,wrappers[A])
 g=0x2968 if side else 0x5c
 struct.pack_into('<I',data,g,wrappers[T]);struct.pack_into('<H',data,g+804,1);struct.pack_into('<H',data,g+0x2908,1)
 struct.pack_into('<HH3HHhhBBH',data,g+4,0,88,21,0,0,1,100,100,100,0,0)
 m.put(AI,data);m.put(OUTPUT,bytes(0x290c));ram=m.read(0x02000000,0x40000);iw=m.read(0x03000000,0x8000)
 result=m.call(S['ffta_myk_ai_original_rank'],AI,0,side,OUTPUT,stack=sp);expected=m.read(0x02000000,0x40000);rng=m.read(0x030034b0,4)
 m.put(0x02000000,ram);m.put(0x03000000,iw)
 actual=m.call(0x080c2940,AI,0,side,OUTPUT,stack=sp)
 # Native sorting is void: its epilogue returns through R0, whose incidental
 # value changes with the caller. ARM.call already checks SP/callee registers.
 check('native-rank-forwarding-EWRAM',m.read(0x02000000,0x40000),expected);check('native-rank-forwarding-RNG',m.read(0x030034b0,4),rng)
report=dict(passed=not failures,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),samples=samples,failures=failures)
(OUT/'mystic-knight-tactical-values.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2));assert not failures,len(failures)
