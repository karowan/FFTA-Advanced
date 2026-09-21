"""Observe current native utility-action admission and scoring before I08 edits."""
import collections,itertools,json,pathlib,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-geomancer-fields.py';ns={'__file__':str(source),'__name__':'utility_ai_audit'}
exec(compile(source.read_text(encoding='utf-8').split('for action,seed in itertools.product')[0],str(source),'exec'),ns)
m,meta,OUT,A,T,STACK,fresh,field,state,updraft,call=(ns[k] for k in ('m','meta','OUT','A','T','STACK','fresh','field','state','updraft','call'))
wrappers=ns['ns']['ns']['wrappers'];ROW=0x0202f000;NODE=0x02015488
checks=collections.Counter();rows=[]
def protected():
 return m.read(A,264)+m.read(T,264)+m.read(state(A),22)+m.read(state(T),22)+m.read(0x030034b0,4)
def check(label,ok):checks[label]+=1;assert ok,(label,case)
for action,condition in itertools.product((377,380,382),('enemy','ally','self','active-updraft','active-rime','active-refuge','no-MP','Silence','KO-target')):
 case=(action,condition);fresh(action);m.put(m.word(0x0200f438)+4,b'\0')
 m.put(T+0x29,b'\x80')
 target=A if condition=='self' else T
 if condition in ('ally','active-updraft','active-refuge'):m.put(T+0x29,b'\0')
 if condition=='active-updraft':updraft(T)
 if condition=='active-rime':field(A,1)
 if condition=='active-refuge':field(A,2)
 if condition=='no-MP':m.put(A+0x1c,bytes(2))
 if condition=='Silence':m.put(A+0xeb,b'\x08')
 if condition=='KO-target':m.put(T+0x18,bytes(2))
 m.put(ROW-16,b'\xa5'*52);m.put(ROW,bytes(20));m.put(STACK,bytes(8));before=protected()
 m.call(0x080c2618,ROW,wrappers[A],wrappers[target],action,stack=STACK)
 row=m.read(ROW,20);check('row-preserves-units-state-and-RNG',protected()==before)
 check('row-output-bounds',m.read(ROW-16,16)+m.read(ROW+20,16)==b'\xa5'*32)
 m.put(NODE,struct.pack('<I',wrappers[A]));m.put(NODE+8,struct.pack('<HH',action,0));before=protected()
 score=m.call(0x080bdecc,wrappers[A],wrappers[target],action,0,stack=STACK)
 if score&0x80000000:score-=0x100000000
 check('score-preserves-units-state-and-RNG',protected()==before)
 check('scope-retired',m.read(0x0203f728,4)==bytes(4))
 rows.append(dict(action=action,condition=condition,row=list(struct.unpack('<10H',row)),score=score))
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),rows=rows,
 scope='Baseline observations and query-purity checks only; no utility-AI acceptance')
(OUT/'geomancer-utility-ai-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
