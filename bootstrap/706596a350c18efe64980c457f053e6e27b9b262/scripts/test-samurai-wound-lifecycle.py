"""Native lifecycle transactions preserve original state and clear exact wounds."""
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text());OUT=pathlib.Path(meta['path']).parent
rom=pathlib.Path(meta['path']).read_bytes();base=(OUT/'input.gba').read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
fix=ROOT/'build/expansion/probes/samurai-state'/meta['baseSha1'];ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes()
UNIT,EQUIPMENT,RETURN,STACK,CTX=0x02000080,0x02002000,0x08000100,0x03007000,0x0200f3f0
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
n,m=ARM(base,iw),ARM(rom,iw);checks=collections.Counter();records=struct.pack('<36H',*[0x8000+i for i in range(36)])
units=[0x02000080+264*i for i in range(24)]+[0x02002fc4+264*i for i in range(12)]
def check(k,a,b):
 checks[k]+=1;assert a==b,(k,[(hex(i),x,y) for i,(x,y) in enumerate(zip(a,b)) if x!=y][:12] if isinstance(a,bytes) else (a,b))
def fresh(machine):machine.put(0x02000000,ram);machine.put(0x03000000,iw);machine.put(0x02001ebc,records)
def compare(fn,args,index,clears,stack):
 for machine in (n,m):fresh(machine);machine.call(fn,*args,stack=stack)
 expected=bytearray(n.read(0x02000000,0x40000))
 if clears:expected[0x1ebc+index*2:0x1ebe+index*2]=bytes(2)
 check('native_transaction_RAM',m.read(0x02000000,0x40000),bytes(expected))
for stack,index in itertools.product((STACK,STACK+4),range(36)):
 unit=units[index];compare(0x08097298,(unit,),index,True,stack)
 for v in (0,1,256,257):compare(0x080cddd0,(unit,v),index,bool(v&255),stack)
 for status,v in itertools.product(range(44),(0,1)):compare(0x080cd884,(unit,status,v),index,status==6 and v,stack)
for stack,job in itertools.product((STACK,STACK+4),(ram[0x87],2,3,10,116)):
 compare(0x080c8c24,(UNIT,job),0,job!=ram[0x87],stack)
# Whole native effect dispatcher, including applicability and query guards.
stages={11:next(i for i in range(256) if base[0x553e70+i*4+1]==11),79:139}
for effect,status,query,stack in itertools.product(stages,range(-1,44),(0,16),(STACK,STACK+4)):
 for machine in (n,m):
  fresh(machine);machine.put(UNIT+0xe8,struct.pack('<Q',0 if status<0 else 1<<status))
  context=bytearray(0x34);struct.pack_into('<IIIHH',context,0,0x02000398,UNIT,UNIT,264,0);struct.pack_into('<H',context,0x26,query);struct.pack_into('<I',context,0x30,0x08553e70+stages[effect]*4);machine.put(CTX,context)
 allowed=n.call(0x08133a58,UNIT,effect)
 for machine in (n,m):machine.call(0x0813388c,stack=stack)
 expected=bytearray(n.read(0x02000000,0x40000))
 if allowed and not query:expected[0x1ebc:0x1ebe]=bytes(2)
 check('native_remedy_complete_RAM',m.read(0x02000000,0x40000),bytes(expected))
for event in range(10):
 fresh(m);m.call(meta['symbols']['ffta_wound_event'],UNIT,event);wanted=bytearray(records)
 if 2<=event<=6:wanted[:2]=bytes(2)
 check('event_mask',m.read(0x02001ebc,72),bytes(wanted))
# Execute installed battle-end and scripted-KO inline hooks on native frames.
for stack,status in itertools.product((STACK,STACK+4),range(44)):
 outputs=[]
 for image in (base,rom):
  machine=ARM(image,iw);fresh(machine);machine.put(0x02008000,bytes([0,0,status,1]));machine.put(0x02008010,struct.pack('<I',UNIT))
  machine.u.reg_write(UC_ARM_REG_R4,0x02008000);machine.u.reg_write(UC_ARM_REG_R5,0x02008010);machine.u.reg_write(UC_ARM_REG_SP,stack);machine.u.reg_write(UC_ARM_REG_LR,RETURN|1)
  machine.u.emu_start(0x081230f3,0x08123104,count=50000);check('event_returns',machine.u.reg_read(UC_ARM_REG_PC),0x08123104);outputs.append(machine.read(0x02000000,0x40000))
 expected=bytearray(outputs[0])
 if status==0:expected[0x1ebc:0x1ebe]=bytes(2)
 check('scripted_KO_RAM',outputs[1],bytes(expected))
for stack in (STACK,STACK+4):
 outputs=[]
 for image in (base,rom):
  machine=ARM(image,iw);fresh(machine);machine.u.reg_write(UC_ARM_REG_SP,stack);machine.u.reg_write(UC_ARM_REG_LR,RETURN|1)
  machine.u.emu_start(0x08095215,0x0809522a,count=3000000);check('battle_end_returns',machine.u.reg_read(UC_ARM_REG_PC),0x0809522a);outputs.append(machine.read(0x02000000,0x40000))
 expected=bytearray(outputs[0]);expected[0x1ebc:0x1f04]=bytes(72);check('battle_end_all_owners',outputs[1],bytes(expected))
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),scope='Native KO, both Petrify writers, job transaction, broad-remedy dispatchers, script KO and battle-end frame; exact owner and query preservation')
(OUT/'wound-lifecycle-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
