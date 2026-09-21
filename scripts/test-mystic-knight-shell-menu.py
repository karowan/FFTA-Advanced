"""Deterministic native player preview with a confirmed first Doublecast area.

Uses the real B55CC UI caller and original Shell as the independent mitigation
oracle. Fixed native controller/targeter inputs, no substituted forecast values.
This is native menu calculation coverage, not rendered full-turn acceptance.
"""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-mystic-knight-doublecast.py'
ns={'__file__':str(source),'__name__':'shell_menu_fixture'}
exec(compile(source.read_text(encoding='utf-8').split('# Compare every register')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,STACK,B,call,half,setup,h,w,record=(ns[x] for x in
 ('m','S','meta','OUT','A','T','STACK','B','call','half','setup','h','w','record'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0
checks=collections.Counter();failures=[];samples=[];case=None;values=[]
def check(k,a,b):
 checks[k]+=1
 if a!=b:failures.append(dict(case=case,check=k,actual=repr(a),expected=repr(b)))
def observed(u,pc,size,data):
 v=u.reg_read(UC_ARM_REG_R0);values.append(v if v<0x80000000 else v-0x100000000)
m.u.hook_add(UC_HOOK_CODE,observed,begin=0x080b5730,end=0x080b5730)
def configure(first,second,center,mp,hp,reaction,existing,condition,scope='pair'):
 setup((first,second),previous=1,seed=1,shell=reaction)
 h(A+0x1c,mp);h(T+0x18,hp);m.put(B+0xcb,bytes((center,)))
 if condition=='immune':m.put(T+0x0d,b'\x02')
 if condition=='absorb':m.put(T+0x0d,b'\x03')
 if condition=='ward':ns['equip'](T,'MYK-S2')
 if existing:
  m.call(0x080ce070,T,1,stack=STACK);m.call(0x080ce440,T,3,stack=STACK)
 q=m.call(0x08022840,0x120,stack=STACK);check('allocated-targeter',bool(q),True)
 m.put(q,bytes(0x120));w(q+4,ns['wrappers'][A]);w(q+8,ns['wrappers'][T])
 h(q+0xec,second);h(q+0xee,88);w(B+0x60,q)
 m.put(B+0xae,b'\x01');h(B+0xdc,0x31)
 if scope=='first':m.put(B+0xae,b'\0')
 elif scope=='finished':m.put(B+0xae,b'\x02')
 elif scope=='cancelled':w(B+0x60,0)
 elif scope=='other-phase':h(B+0xdc,0x2f)
 elif scope=='other-command':h(B+0xa6,23)
 elif scope=='other-action':h(q+0xec,24)
 elif scope=='other-target':w(q+8,ns['wrappers'][A])
 elif scope=='other-actor':w(q+4,ns['wrappers'][T])
 elif scope=='other-item':h(q+0xee,89)
 return q

def invoke(action,path='UI',residue=0):
 values.clear();sp=0x03007800+residue
 m.put(sp,struct.pack('<2I',0,255 if path=='UI' else 2))
 if path=='UI':
  m.call(0x080b55cc,ns['wrappers'][A],ns['wrappers'][T],action,88,stack=sp)
  check('one-native-UI-value',len(values),1);return values[0]
 v=m.call(0x08130200,A,T,action,88,stack=sp)
 return v if v<0x80000000 else v-0x100000000

def live():
 return m.read(A,264)+m.read(T,264)+m.read(record(A),22)+m.read(record(T),22)+m.read(0x030034b0,4)

def release(q):m.call(0x08022854,q,stack=STACK)

# The first confirmed cross includes T at center5 or its edge6, not7.
# Each forecast starts fresh; ordinary Shell is never installed on the test
# recipient in the reaction branch. Adjacent threshold values catch rounding.
for (first,second,center,mp,condition),offset,residue in itertools.product(
 ((23,23,5,99,'normal'),(23,24,6,99,'normal'),(26,23,7,99,'normal'),
  (23,23,5,11,'normal'),(23,23,5,12,'normal'),
  (23,24,5,99,'immune'),(23,24,5,99,'absorb'),(26,23,5,99,'ward')),
 (-1,0,1),(0,4)):
 case=(first,second,center,mp,condition,offset,residue)
 q=configure(first,second,center,mp,500,False,False,condition)
 raw_first=invoke(first,'generic');raw_second=invoke(second,'generic');release(q)
 first_cost=m.call(0x0812ed98,A,first,stack=STACK)
 second_cost=m.call(0x0812ed98,A,second,stack=STACK)
 contribution=max(0,raw_first) if first!=1 and center in (5,6) and mp>=first_cost+second_cost else 0
 total=max(raw_second,0)+contribution;hp=min(500,250+total+offset)
 expected=total>0 and hp-total<=250
 q=configure(first,second,center,mp,hp,False,expected,condition);oracle=invoke(second,residue=residue);release(q)
 q=configure(first,second,center,mp,hp,True,False,condition)
 before=live();code=m.read(0x03006170,0xbf8);controller=m.read(B,0x140)
 actual=invoke(second,residue=residue)
 check('combined-preview-native-Shell-oracle',actual,oracle)
 check('UI-keeps-units-state-RNG',live(),before)
 check('UI-keeps-native-code',m.read(0x03006170,0xbf8),code)
 check('UI-keeps-controller',m.read(B,0x140),controller)
 check('UI-retires-snapshots',m.read(0x0203ff44,8),bytes(8))
 bank=call('ffta_battle_workspace',0x10)
 check('UI-retires-bank',m.read(bank,824*8),bytes(824*8))
 release(q);samples.append(dict(case=case,first=raw_first,second=raw_second,total=total,hp=hp,expected=expected,actual=actual,oracle=oracle))

# A valid-looking old selection must not contaminate a generic query, another
# targeter, or a cancelled/backtracked/finished native selection screen.
for scope,path,residue in itertools.product(('pair','first','finished','cancelled','other-phase','other-command','other-action','other-target','other-actor','other-item'),('UI','generic'),(0,4)):
 case=('scope',scope,path,residue)
 q=configure(23,23,5,99,500,False,False,'normal');raw=invoke(23,path,residue);release(q)
 hp=250+raw+1;expected=scope=='pair' and path=='UI'
 q=configure(23,23,5,99,hp,False,expected,'normal',scope);oracle=invoke(23,path,residue);release(q)
 q=configure(23,23,5,99,hp,True,False,'normal',scope)
 check('selection-and-caller-isolation',invoke(23,path,residue),oracle);release(q)
check('nonvacuous-pair-only-trigger',any(s['expected'] and s['hp']-s['second']>250 and s['actual']<s['second'] for s in samples),True)
report=dict(passed=not failures,romSha1=meta['romSha1'],total=sum(checks.values()),checks=dict(checks),failures=failures,samples=samples,
 limits=['Native UI forecast only; renderer, cancellation button playback and full-turn Shell evidence remain separate.','Forecast is conditional on successful magic; no RNG outcome is predicted.'])
(OUT/'mystic-knight-shell-menu.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(dict(passed=not failures,romSha1=meta['romSha1'],total=report['total'],checks=dict(checks),failureCounts=dict(collections.Counter(x['check'] for x in failures))),indent=2));assert not failures
