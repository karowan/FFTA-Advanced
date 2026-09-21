"""Actual native self-buff AI rows retain law flags and source-unit purity."""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-carrier-element-laws.py'
exec(compile(source.read_text().split('\nfor action,self_target,seed in ')[0],str(source),'exec'))
observations=[]
for action,race,jid,status in ((359,1,117,24),(359,2,119,24),(398,5,123,12)):
 for banned in (status,25):
  case=(action,race,banned);fixture(action);ns['job'](A,race,jid);m.put(A+0x2a,bytes(10))
  m.put(m.word(0x0200f438)+4,b'\0');m.put(0x0203f728,bytes(4))
  judge=0x020005a8;m.put(judge+0x28,struct.pack('<H',0x1000));m.put(judge+0x18,struct.pack('<HH',500,500));m.put(judge+0xe8,bytes(8))
  m.put(0x08529348,bytes((15,banned)));m.put(ROW,bytes(20));m.put(STACK,bytes(8))
  protected=[(A,264),(record(A),22),(0x030034b0,4),(0x03005e80,384)]
  before=[m.read(p,n) for p,n in protected]
  m.call(0x080c2618,ROW,wrappers[A],wrappers[A],action,stack=STACK);row=m.read(ROW,20)
  for (p,n),b in zip(protected,before):check('self-AI-query-pure-'+hex(p),m.read(p,n),b)
  check('native-self-AI-positive',int.from_bytes(row[10:12],'little')>0,True)
  check('native-self-AI-law',bool(row[17]&2),banned==status)
  observations.append(dict(action=action,race=race,banned=banned,row=row.hex()))
report=dict(passed=True,romSha1=meta['romSha1'],total=sum(checks.values()),checks=dict(checks),observations=observations)
(OUT/'self-buff-law-ai.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
