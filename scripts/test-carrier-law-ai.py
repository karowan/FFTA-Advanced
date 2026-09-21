"""Real native AI rows consume theft-family and equipped-element laws."""
import pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-carrier-element-laws.py'
exec(compile(source.read_text().split('\nfor action,self_target,seed in ')[0],str(source),'exec'))
observations=[]
for action,weapon,race,jid,kind,value,loot in (
 (360,13,1,117,2,5,0),(361,13,1,117,2,5,0),(362,60,1,117,2,5,0),(408,91,4,124,2,1,0),
 (366,399,2,118,1,23,0),(367,399,2,118,1,23,354),(370,399,2,118,1,23,288)):
 if '--last-resort-only' in sys.argv and action!=360:continue
 for banned in (True,False):
  case=('native-AI-law',action,banned);fixture(action);ns['job'](A,race,jid)
  m.put(A+0x2a,struct.pack('<5H',weapon,0,0,0,0));m.put(T+0x2a,struct.pack('<5H',loot,0,0,0,0))
  m.put(m.word(0x0200f438)+4,b'\0');m.put(0x0203f728,bytes(4))
  judge=0x020005a8;m.put(judge+0x28,struct.pack('<H',0x1000));m.put(judge+0x18,struct.pack('<HH',500,500));m.put(judge+0xe8,bytes(8))
  m.put(0x08529348,bytes((kind,value if banned else 8)))
  m.put(ROW,bytes(20));m.put(STACK,bytes(8))
  protected=[(A,264),(T,264),(record(A),22),(record(T),22),(0x02001940,512),(0x030034b0,4),(0x03005e80,384)]
  before=[m.read(p,n) for p,n in protected]
  m.call(0x080c2618,ROW,wrappers[A],wrappers[T],action,stack=STACK);row=m.read(ROW,20)
  for (p,n),b in zip(protected,before):check('AI-query-pure-'+hex(p),m.read(p,n),b)
  check('actual-AI-row-admitted',int.from_bytes(row[10:12],'little')>0,True)
  check('actual-AI-carrier-law-flag',bool(row[17]&2),banned)
  observations.append(dict(action=action,banned=banned,row=row.hex()))
report=dict(passed=True,romSha1=meta['romSha1'],total=sum(checks.values()),checks=dict(checks),observations=observations)
(OUT/'carrier-law-ai.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
