"""Actual native AI score rows carry the custom harmful-status law flag.

Fixed current rule and native unit/equipment inputs; neither row values nor
law results are supplied. Player confirmation is not a native law forecaster.
"""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-custom-status-law-prediction.py'
exec(compile(source.read_text().split('\nconditions=')[0],str(source),'exec'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R2
ROW=0x02028000
queries=[]
gates=[]
def observe(u,address,size,data):queries.append(u.reg_read(UC_ARM_REG_R2))
m.u.hook_add(UC_HOOK_CODE,observe,begin=0x081343c8,end=0x081343c8)
for pc in (0x080c2698,0x080c26a4,0x080c26b0,0x080c26bc):
 m.u.hook_add(UC_HOOK_CODE,lambda u,p,s,d:gates.append((hex(p),hex(u.reg_read(UC_ARM_REG_R0)))),begin=pc,end=pc)
for action,condition,residue in itertools.product((355,373,379,404,405),
 ('normal','inoculated','immune','MP','cureall-stock','cureall-empty','cureall-disabled','strong-Wisp','strong-heat'),(0,4)):
 case=(action,condition,residue);setup(action,condition)
 m.put(0x0203f728,bytes(4));m.put(m.word(0x0200f438)+4,b'\0')
 # The retained Giza monster encounter has no Judge unit. Declare an alive
 # Judge in a third wrapper, just as other tests declare jobs/equipment. The
 # native enumerator and eligibility gate still decide whether laws apply.
 judge=0x020005a8
 m.put(judge+0x28,struct.pack('<H',0x1000));m.put(judge+0x18,struct.pack('<HH',500,500));m.put(judge+0xe8,bytes(8))
 check('native-finds-declared-Judge',m.call(0x08099544,m.word(0x0200f4b0),stack=STACK),wrappers[judge])
 m.put(0x08529348,bytes((16,0)))
 check('declared-current-law',m.read(0x02003c33,3),bytes((1,65,0)))
 expected=query(action,A,T,residue)
 m.put(ROW-16,b'\xa5'*52);m.put(ROW,bytes(20))
 m.put(STACK+residue,struct.pack('<II',0,0));queries.clear();gates.clear()
 protected=[(A,264),(T,264),(state(A),22),(state(T),22),(0x02001940,512),
            (0x030034b0,4),(0x03005e80,384),(0x0203ff44,8),(0x0203f728,4)]
 before=[m.read(p,n) for p,n in protected]
 m.call(0x080c2618,ROW,wrappers[A],wrappers[T],action,stack=STACK+residue)
 row=m.read(ROW,20);count=int.from_bytes(row[10:12],'little')
 for (p,n),b in zip(protected,before):check('row-preserves-'+hex(p),m.read(p,n),b)
 check('row-guards',m.read(ROW-16,16)+m.read(ROW+20,16),b'\xa5'*32)
 if bool(row[17]&2)!=bool(expected and count):print('row diagnostic',case,row.hex(),queries,gates,flush=True)
 check('actual-row-law-flag',bool(row[17]&2),bool(expected and count))
 if count:check('native-row-consumes-law-query',action in queries,True)
 if condition=='normal':check('positive-normal-row',bool(count and row[17]&2),True)
 samples.append(dict(action=action,condition=condition,residue=residue,count=count,law=bool(row[17]&2),queries=list(queries)))
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),samples=samples)
(OUT/'custom-status-law-ai.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
