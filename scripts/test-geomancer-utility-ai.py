"""Native utility AI rows/scores, transferable supports and query purity.

This accepts recipient evaluation only, not full-turn placement or AI execution.
All scenarios use the existing deterministic native executor and fixed board.
"""
import collections,itertools,json,pathlib,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-geomancer-arts.py'
ns={'__file__':str(source),'__name__':'utility_ai_fixture'}
exec(compile(source.read_text(encoding='utf-8').split('\nfor action,seed in itertools.product')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,STACK,reset,state,equip,job=(ns[k] for k in ('m','S','meta','OUT','A','T','STACK','reset','state','equip','job'))
field,updraft=ns['ns']['field'],ns['ns']['updraft']
wrappers=ns['wrappers'];ROW=0x0202f000;NODE=0x02015488
checks=collections.Counter();cases=[];failures=[];case=None

def check(label,actual,expected=True):
 checks[label]+=1
 if actual!=expected:failures.append(dict(check=label,case=case,actual=actual,expected=expected))

def protected():
 return b''.join(m.read(u,264)+m.read(state(u),22) for u in (A,T))+m.read(0x030034b0,4)

def query(action,target,sp,original=False):
 m.put(ROW-16,b'\xa5'*52);m.put(ROW,bytes(20));m.put(sp,bytes(8));before=protected()
 m.call(S['ffta_ai_original_row'] if original else 0x080c2618,ROW,wrappers[A],wrappers[target],action,stack=sp)
 row=m.read(ROW,20)
 check('row-preserves-live-units-state-RNG',protected(),before)
 check('row-output-bounds',m.read(ROW-16,16)+m.read(ROW+20,16),b'\xa5'*32)
 m.put(NODE,struct.pack('<I',wrappers[A]));m.put(NODE+8,struct.pack('<HH',action,0));before=protected()
 score=m.call(S['ffta_ai_original_score'] if original else 0x080bdecc,wrappers[A],wrappers[target],action,0,stack=sp)
 if score&0x80000000:score-=0x100000000
 check('score-preserves-live-units-state-RNG',protected(),before)
 check('scope-retired',m.read(0x0203f728,4),bytes(4))
 return row,score

conditions=('enemy','ally','self','updraft','refuge','rime','floating','flying','surefoot',
 'light-foot','lower-ally','KO','petrified','sleeping-caster','charmed-caster','enemy-refuge')
for action,condition,sp in itertools.product((377,380,382),conditions,(STACK,STACK+4)):
 case=(action,condition,sp);reset(action)
 # fresh(377) deliberately starts with an ally; declare faction explicitly.
 m.put(T+0x29,bytes((128 if condition in ('enemy','charmed-caster') else 0,)))
 m.put(m.word(0x0200f438)+4,b'\0');target=A if condition=='self' else T
 if condition=='updraft':updraft(T)
 if condition=='refuge':field(A,2)
 if condition=='enemy-refuge':
  enemy=next(u for u in wrappers if u not in (A,T))
  m.put(enemy+0x29,b'\x80');m.put(enemy+0x18,struct.pack('<H',100));m.put(enemy+0xe8,bytes(8));field(enemy,2)
 if condition=='rime':field(A,1)
 if condition=='floating':m.put(T+0xfc,b'\x02')
 if condition=='flying':m.put(T+0xfc,b'\x03')
 if condition=='surefoot':job(T,3,21);equip(T,'GEO-S2')
 if condition=='light-foot':job(T,4,29);equip(T,'DNC-S2')
 if condition=='lower-ally':m.put(ns['GRID']+2*(14*16+4),b'\x12')
 if condition=='KO':m.put(T+0x18,bytes(2))
 if condition=='petrified':m.put(T+0xe8,b'\x40')
 if condition=='sleeping-caster':m.put(A+0xeb,b'\x10')
 if condition=='charmed-caster':m.put(A+0xeb,b'\x20')
 native,native_score=query(action,target,sp,True)
 actual,score=query(action,target,sp)
 nrow=struct.unpack('<10H',native);row=struct.unpack('<10H',actual)
 value=struct.unpack_from('<h',actual,12)[0]
 denied=condition in ('KO','petrified','sleeping-caster')
 if action==377:
  expected=0 if denied or condition in ('enemy','updraft','refuge') else -20 if condition=='lower-ally' else -16
 elif action==382:
  expected=0 if denied or condition in ('enemy','updraft','refuge','floating','flying') else -20
 else:
  excluded=denied or condition=='self'
  bonus=0 if condition in ('rime','updraft','floating','flying','surefoot') else 6
  expected=0 if excluded else struct.unpack_from('<h',native,12)[0]+bonus
  check('Rime-preserves-native-score-and-adds-only-terrain',score,0 if excluded else native_score+bonus)
 if action!=380:check('benefit-score-agrees-with-row',score,expected)
 check('recipient-value',value,expected)
 check('real-action-and-extra-preserved',actual[:4],native[:4])
 if expected:
  check('probability-law-and-count-preserved',actual[6:12]+actual[16:20],native[6:12]+native[16:20])
  check('sort-value-agrees',struct.unpack_from('<h',actual,14)[0],expected)
  check('native-category',row[2],nrow[2] if action==380 else 82)
 else:check('no-op-candidate-empty',actual[4:],bytes(16))
 cases.append(dict(case=case,nativeRow=list(nrow),row=list(row),nativeScore=native_score,score=score))

# Unrelated rows/scores still use their original forwarding path. Exclude
# already customized jobs and Fight, which have their own accepted consumers.
for action,sp in itertools.product((23,24,41,265,374,378),(STACK,STACK+4)):
 case=('ordinary-forwarding',action,sp);reset(action)
 native,native_score=query(action,T,sp,True);actual,score=query(action,T,sp)
 check('ordinary-row-identical',actual,native);check('ordinary-score-identical',score,native_score)

# JSON encodes byte snapshots only for failures; successful logs stay compact.
report=dict(passed=not failures,romSha1=meta['romSha1'],checks=dict(checks),
 total=sum(checks.values()),cases=cases,failures=failures,scope=__doc__)
(OUT/'geomancer-utility-ai.json').write_text(json.dumps(report,indent=2,default=lambda x:x.hex()),encoding='utf-8')
print(json.dumps(report,indent=2,default=lambda x:x.hex()))
assert not failures,failures
