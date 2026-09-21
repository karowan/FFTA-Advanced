"""Real native command construction, names, enabled flags and selected-item ABI."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
P=ROOT/'build/expansion/probes';meta=_load_job_candidate(P/'chemist/current.json');OUT=pathlib.Path(meta['path']).parent
rom=pathlib.Path(meta['path']).read_bytes();base=(OUT/'input.gba').read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
fix=pathlib.Path(meta['path']).parent/'executor';iw=(fix/'execute-trap.iwram').read_bytes();ram=(fix/'execute-trap.ram').read_bytes()
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=500000'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
m,n=ARM(rom,iw),ARM(base,iw);counts=collections.Counter();registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
MENU,DESC,IDS,FLAGS=0x02028000,0x02028200,0x02028400,0x02028500

def check(k,a,b):counts[k]+=1;assert a==b,(k,a,b)
def setup(machine,race,job,stock=5):
 machine.put(0x02000000,ram);machine.put(0x03000000,iw);machine.put(UNIT+5,bytes((job,race,job,job)));machine.put(UNIT+0x35,bytes((job,job,0)));machine.put(UNIT+0xe8,bytes(8));machine.put(UNIT+0x2a,bytes(10));machine.put(UNIT+0x3a,bytes(3));machine.put(UNIT+0x40,b'\xff'*0x90)
 manager=machine.word(0x0200f438);machine.put(manager+4,b'\x06');machine.put(manager+24,struct.pack('<I',UNIT));machine.put(0x02001940+362,bytes([stock])*14)
 machine.put(MENU,bytes(0xa4));machine.put(MENU+10,bytes([race]));machine.put(MENU+0x94,struct.pack('<II',IDS,FLAGS));machine.put(IDS-16,b'\xa5'*(16+22*4+16));machine.put(FLAGS-16,b'\xa6'*(16+22+16));machine.put(FLAGS,b'\x01'*22)
 bank=machine.call(0x080cce60,UNIT,1,DESC+4,DESC+5);machine.put(DESC,struct.pack('<I',bank));machine.put(DESC+6,bytes((job,0,0,0,0,0)));return bank,manager
def build(machine,entry,sp):
 before=machine.read(UNIT,264);machine.call(entry,MENU,DESC,stack=sp);count=machine.read(DESC+9,1)[0];check('native22-capacity',count<=22,True);machine.put(MENU+0x84,struct.pack('<H',count))
 check('rows-low-guard',machine.read(IDS-16,16),b'\xa5'*16);check('rows-high-guard',machine.read(IDS+88,16),b'\xa5'*16);check('flags-high-guard',machine.read(FLAGS+22,16),b'\xa6'*16);check('learning-read-only',machine.read(UNIT,264),before)
 return list(struct.unpack('<'+'I'*count,machine.read(IDS,count*4))),list(machine.read(FLAGS,count))
def readtext(machine,p):
 result=[]
 for i in range(160):
  b=machine.read(p+i,1)[0]
  if not b:return bytes(result)
  result.append(b)
 raise AssertionError('unterminated native text')
for race,job in ((1,3),(2,17),(3,20),(4,29),(5,38)):
 for entry,sp in itertools.product((0x08026d44,0x08026f9c),(STACK,STACK+4)):
  setup(m,race,job);setup(n,race,job);actual,expected=build(m,entry,sp),build(n,entry,sp);check('original-native-menu',actual,expected)
  for row in range(len(actual[0])):check('original-native-names',readtext(m,m.call(0x08025758,MENU,row,stack=sp)),readtext(n,n.call(0x08025758,MENU,row,stack=sp)))
for race,job,stock,sp in itertools.product((3,5),(120,), (0,5),(STACK,STACK+4)):
 job=120 if race==3 else 122;bank,manager=setup(m,race,job,stock);ids,flags=build(m,0x08026d44,sp)
 actions=[struct.unpack('<H',m.read(bank+i*8+4,2))[0] for i in ids]
 check('choices-retain-action-and-AP-identity',actions,[383,384,384,384,384,385,386,386,387,388,389,390,391,392])
 for row,item in ((1,367),(2,368),(3,369),(4,371),(6,363),(7,364)):
  check('exact-choice-stock-grey',flags[row],int(stock>0));check('native-choice-label',readtext(m,m.call(0x08025758,MENU,row,stack=sp)),readtext(m,m.word(meta['symbols']['ffta_chemist_choice_labels']+4*((row-1) if row<5 else row-2))))
  m.call(meta['symbols']['ffta_chemist_menu_selected'],MENU,row,actions[row],stack=sp);check('native-selected-item-field',struct.unpack('<H',m.read(manager+16,2))[0],item)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(counts),total=sum(counts.values()));(OUT/'menu-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
