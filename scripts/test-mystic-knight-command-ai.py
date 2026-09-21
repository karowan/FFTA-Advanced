"""Deterministic Mystic command admission and native AI values across modes."""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-mystic-knight-commands.py'
ns={'__file__':str(source),'__name__':'mystic_command_ai_fixture'}
exec(compile(source.read_text(encoding='utf-8').split('# Native casts cover')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,STACK,fixture,call,record=(ns[x] for x in ('m','S','meta','OUT','A','T','STACK','fixture','call','record'))
wrappers=ns['wrappers'];ROW=0x02028000;NODE=0x02015488
checks=collections.Counter();failures=[];samples=[];case=None

def check(k,a,b):
 checks[k]+=1
 if a!=b:failures.append(dict(check=k,case=case,actual=repr(a),expected=repr(b)))
def signed(n):return n if n<0x80000000 else n-0x100000000
def protected():return m.read(A,264)+m.read(T,264)+m.read(record(A),22)+m.read(record(T),22)+m.read(0x030034b0,4)+m.read(0x03005e80,64)
for action,condition,sp in itertools.product(range(410,424),('enemy','self','repeat-self','different-self','ally','silenced','wrong-weapon','no-fuel','bad-fuel','flare-fuel'),(STACK,STACK+4)):
 case=(action,condition,sp);fixture(action);m.put(m.word(0x0200f438)+4,b'\0')
 if action==421:ns['grant'](T,25)
 kind=8 if condition=='flare-fuel' else 5 if condition=='bad-fuel' else 0 if condition in ('no-fuel','self') else 1
 if kind:call('ffta_myk_grant',A,kind)
 if condition=='repeat-self' and action<=420:call('ffta_myk_grant',A,action-409)
 if condition=='different-self' and action<=420:call('ffta_myk_grant',A,2 if action==410 else 1)
 target=A if condition in ('self','repeat-self','different-self') else T
 if condition=='ally':m.put(T+0x29,b'\0')
 if condition=='silenced':ns['grant'](A,27)
 if condition=='wrong-weapon':m.put(A+0x2a,struct.pack('<H',1))
 m.put(ROW-16,b'\xa5'*52);m.put(ROW,bytes(20));m.put(sp,struct.pack('<II',88,0));before=protected()
 m.call(0x080c2618,ROW,wrappers[A],wrappers[target],action,stack=sp)
 row=m.read(ROW,20);count=int.from_bytes(row[10:12],'little');value=struct.unpack_from('<h',row,12)[0]
 check('native-row-query-pure',protected(),before);check('row-guards',m.read(ROW-16,16)+m.read(ROW+20,16),b'\xa5'*32)
 choice=int.from_bytes(row[2:4],'little');m.put(NODE,struct.pack('<I',wrappers[A]));m.put(NODE+8,struct.pack('<HH',action,choice))
 before=protected();score=signed(m.call(0x080bdecc,wrappers[A],wrappers[target],action,0,stack=sp));check('native-score-query-pure',protected(),before)
 check('query-roots-retired',m.read(0x0203f728,4)+m.read(0x0203ff44,8),bytes(12))
 invalid=condition in ('silenced','wrong-weapon') or (action==422 and condition in ('no-fuel','bad-fuel','self','repeat-self')) or (condition=='ally' and action!=422) or (target==A and action>420)
 if invalid:check('invalid-command-row-absent',count,0);check('invalid-command-score-zero',score,0)
 if condition in ('repeat-self','different-self') and action<=420:
  check('no-wasted-repeat-enchantment',count,0);check('no-wasted-repeat-score',score,0)
 if condition=='self' and action in range(410,421):
  check('new-self-enchantment-admitted',count>0,True);check('self-enchantment-beneficial-value',value<0 and score<0,True)
 if action==421 and condition=='enemy':check('Spellbreak-score-includes-damage-not-just-removal',score>20,True)
 samples.append(dict(action=action,condition=condition,stack=sp,row=row.hex(),count=count,value=value,score=score))
# Native self-search owns only its decision node, never unit state. Candidate
# rows and movement maps are declared inputs; forecasts and admission are real.
GROUP=0x02029000;MOVE=0x0202d400
for action,condition,sp in itertools.product(range(410,421),('bare','prepared','silenced','wrong-weapon','blocked-map'),(STACK,STACK+4)):
 case=('self-search',action,condition,sp);fixture(action);m.put(m.word(0x0200f438)+4,b'\0')
 if condition=='prepared':call('ffta_myk_grant',A,1)
 if condition=='silenced':ns['grant'](A,27)
 if condition=='wrong-weapon':m.put(A+0x2a,struct.pack('<H',1))
 m.put(GROUP,bytes(0x290c));m.put(GROUP,struct.pack('<I',wrappers[A]));m.put(GROUP+0x2908,struct.pack('<H',1))
 m.put(sp,struct.pack('<II',88,0));m.call(0x080c2618,GROUP+4,wrappers[A],wrappers[A],action,stack=sp)
 m.put(GROUP+804,struct.pack('<H',1))
 node=bytearray(0x21c);struct.pack_into('<IIHHII',node,0,wrappers[A],wrappers[A],action,88,GROUP,GROUP)
 node[0x28]=1;struct.pack_into('<I',node,0x214,MOVE);m.put(NODE,node)
 grid=bytearray(b'\x80'*256);x,y=m.read(A+0xf6,2)
 if condition!='blocked-map':grid[y*16+x]=2
 m.put(MOVE,grid);before=protected()
 check('self-search-bounded-completion',m.call(0x080beac8,NODE,0,stack=sp),0)
 check('self-search-query-pure',protected(),before)
 admitted=condition=='bare';check('self-search-exact-admission',m.read(NODE+0x1b1,1)[0],int(admitted))
 if admitted:
  check('self-search-stays-and-targets-self',m.read(NODE+0x1ac,4),bytes((x,y,x,y)))
  check('self-search-modest-benefit',m.word(NODE+0x1c),20)
 # The newly intercepted entry must preserve ordinary native self rejection.
 m.put(NODE+8,bytes(2));original=m.call(S['ffta_myk_ai_original_self_search'],NODE,0,stack=sp)
 expected=m.read(NODE,0x21c);actual=m.call(0x080beac8,NODE,0,stack=sp)
 check('native-self-search-forwarded',actual,original);check('native-self-search-unchanged-node',m.read(NODE,0x21c),expected)
report=dict(passed=not failures,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),samples=samples,failures=failures)
(OUT/'mystic-knight-command-ai.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2));assert not failures,len(failures)
