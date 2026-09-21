"""Deterministic native Higanbana execution and scoped reference ownership."""
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
P=ROOT/'build/expansion/probes';meta=json.loads((P/'samurai/current.json').read_text());OUT=pathlib.Path(meta['path']).parent
rom=pathlib.Path(meta['path']).read_bytes();base=(OUT/'input.gba').read_bytes();symbols=meta['symbols'];assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
fix=P/'samurai-state'/meta['baseSha1'];ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes();regs=struct.unpack_from('<17I',(fix/'execute-trap.state').read_bytes(),0x20)
UNIT,TARGET,RETURN,STACK,CTX,ACTIVE=0x02000080,0x020033e4,0x08000100,0x03007000,0x0200f3f0,0x0203ff44
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m,n=ARM(rom,iw),ARM(base,iw);counts=collections.Counter();outcomes=[]
def check(k,a,b):counts[k]+=1;assert a==b,(k,a,b)
def fresh(machine):machine.put(0x02000000,ram);machine.put(0x03000000,iw)
fresh(m);count=m.call(0x08099cdc,m.word(0x0200f4b0),0x02008000);check('native_actor_count',count,12)
wrappers={m.word(m.word(0x02008000+4*i)):m.word(0x02008000+4*i) for i in range(count)}
WRAPPER=wrappers[UNIT];TW=wrappers[TARGET]
# Full state differential covers the replaced success dispatcher for originals.
for action in list(range(347))+[357,358,423,424,425,426,427,428,429,430,431]:
 result=[]
 for machine in (n,m):
  fresh(machine);machine.put(regs[13],struct.pack('<I',action));machine.put(0x02001e98,b'\xa1'*36)
  machine.call(0x080a433c,*regs[:4],stack=regs[13]);result.append(machine.read(0x02000000,0x40000))
 check('original_executor_complete_RAM',result[0],result[1])
# Exercise ownership without injecting any battle result.
fresh(m);m.put(ACTIVE,bytes(4));scope,nested=0x03007400,0x03007300;obj=0x02035000;row=obj+0x20;dest=0x03007200
def call(name,*args):return m.call(symbols['ffta_execution_'+name],*args)
check('original_does_not_open',call('open',scope,UNIT,1),0)
check('higan_opens',call('open',scope,UNIT,355),1)
context=bytearray(0x34);struct.pack_into('<II',context,0,UNIT,TARGET);struct.pack_into('<H',context,12,355)
m.put(CTX,context);m.put(obj,struct.pack('<I',WRAPPER)+bytes(12)+struct.pack('<H',355)+bytes(0x300))
call('arm',obj,row,CTX);call('capture',123,355,UNIT,TARGET)
check('no_take_while_armed',call('take',obj,row,TARGET,dest),0)
check('nested_opens',call('open',nested,UNIT,1),1);call('arm',obj,row,CTX);call('capture',999,355,UNIT,TARGET);call('disarm')
check('nested_cannot_consume_parent',call('take',obj,row,TARGET,dest),0);call('close',nested)
check('nested_zeroed',m.read(nested,44),bytes(44));call('disarm')
check('wrong_row_rejected',call('take',obj,row+0x2c,TARGET,dest),0)
check('parent_capture_survives',call('take',obj,row,TARGET,dest),1);check('exact_reference',m.word(dest),123)
check('single_use',call('take',obj,row,TARGET,dest),0)
for flag,offset in [(0x10,0),(0,1),(0,15*0x2c)]:
 context[0x26]=flag;m.put(CTX,context);call('arm',obj,row+offset,CTX);call('capture',123,355,UNIT,TARGET);call('disarm');check('query_or_invalid_row_rejected',call('take',obj,row+offset,TARGET,dest),0)
call('close',scope);check('root_closed',m.word(ACTIVE),0);check('scope_zeroed',m.read(scope,44),bytes(44))

def reset(machine,packed,seed,exposed):
 fresh(machine);machine.put(ACTIVE,bytes(4));machine.put(ACTIVE+4,b'\xd7'*0xb8)
 for unit in (UNIT,TARGET):machine.put(unit+0xe8,bytes(8));machine.put(unit+0x3a,bytes(2))
 machine.put(UNIT+5,bytes((116,1,116)));machine.put(UNIT+0x35,b'\x74');machine.put(UNIT+0x2a,struct.pack('<5H',383,0,0,0,0))
 machine.put(UNIT+0x18,struct.pack('<4H',100,100,50,50));machine.put(TARGET+0x18,struct.pack('<4H',250,250,50,50))
 for unit,wrapper,x in ((UNIT,WRAPPER,4),(TARGET,TW,5)):
  machine.put(unit+0xf6,bytes((x,14)));machine.put(wrapper+8,struct.pack('<3H',x*32+16,32,14*32+16))
 machine.put(0x02001e98,bytes([packed])+bytes(35));machine.put(0x02001eb4,bytes([exposed]));machine.put(0x02001ebc,bytes(72))
 machine.put(0x030034b0,struct.pack('<I',seed));machine.put(regs[13],struct.pack('<4I',355,0,0,255))

# Install observers before this machine executes translated native blocks.
m=ARM(rom,iw)
captured=[];observations=[]
def observe(u,address,size,data):
 observations.append([hex(address),*[u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]])
 if u.reg_read(UC_ARM_REG_R1)==355:captured.append(u.reg_read(UC_ARM_REG_R0))
m.u.hook_add(UC_HOOK_CODE,observe,begin=symbols['ffta_execution_capture'],end=symbols['ffta_execution_capture'])
reset(m,1,0,0);bank=m.word(m.word(0x080cd538)+4)
reaction=next(i for i in range(144) if struct.unpack_from('<H',m.read(bank+8*i,8),4)[0]==13 and m.read(bank+8*i+6,1)==b'\x02')
support=next(i for i in range(144) if struct.unpack_from('<H',m.read(bank+8*i,8),4)[0]==11 and m.read(bank+8*i+6,1)==b'\x03')
items=m.word(0x08130684);weapon_effect=m.read(items+383*32+26,3)
for packed,seed,exposed,condition in itertools.product((1,5),range(8),(0,1),('normal','MP','immune','KO','Protect','restorative')):
 reset(m,packed,seed,exposed);old=0x8007;m.put(0x02001ef4,struct.pack('<H',old))
 m.put(items+383*32+26,weapon_effect)
 if condition=='Protect':m.put(TARGET+0xeb,b'\x02')
 if condition=='restorative':m.put(items+383*32+26,b'\x3f\x00\x00');m.put(TARGET+0x18,struct.pack('<H',100))
 if condition in ('MP','immune'):
  index=reaction if condition=='MP' else support;m.put(TARGET+5,bytes((2,1,2)));m.put(TARGET+0x35,b'\x02');m.put(TARGET+0x3a+(condition=='immune'),bytes([index]));m.put(TARGET+0x40+index,b'\xff')
 if condition=='KO':m.put(TARGET+0x18,b'\x01\x00')
 before=int.from_bytes(m.read(TARGET+0x18,2),'little');captured.clear();observations.clear();m.call(0x080a433c,regs[0],WRAPPER,5,14,stack=regs[13])
 hp=int.from_bytes(m.read(TARGET+0x18,2),'little');record=int.from_bytes(m.read(0x02001ef4,2),'little');damage=before-hp
 expected=old
 if damage>0:
  if not captured:print('missing capture',observations,flush=True)
  check('exactly_one_native_reference',(packed,seed,exposed,condition,damage,len(captured)),(packed,seed,exposed,condition,damage,1))
  if hp==0:expected=0
  elif condition!='immune':expected=0x8000|(captured[0]//2)
  if hp:check('direct_damage_scaling',damage,captured[0]*80*(5 if packed==5 else 4)*(6 if exposed else 5)//2000)
 check('wound_on_actual_HP_loss',record,expected)
 check('root_retired',m.word(ACTIVE),0);check('reserved_RAM_guard',m.read(ACTIVE+4,0xb8),b'\xd7'*0xb8)
 check('one_payment',int.from_bytes(m.read(UNIT+0x1c,2),'little'),42)
 check('centered_retired',m.read(0x02001e98,1),b'\x01')
 outcomes.append(dict(packed=packed,seed=seed,exposed=exposed,condition=condition,damage=damage,reference=list(captured),record=record))
check('successful_wound_covered',any(o['record'] not in (0,0x8007) for o in outcomes),True)
check('miss_covered',any(o['condition']=='normal' and not o['damage'] for o in outcomes),True)
check('MP_redirect_covered',any(o['condition']=='MP' and not o['damage'] and o['reference'] for o in outcomes),True)
check('restorative_healing_covered',any(o['condition']=='restorative' and o['damage']<0 and o['record']==0x8007 for o in outcomes),True)
report=dict(passed=True,romSha1=meta['romSha1'],baseSha1=meta['baseSha1'],checks=dict(counts),total=sum(counts.values()),outcomes=outcomes,scope='Initial hit and wound application; pulse, remedy and UI acceptance are separate declared tests')
(OUT/'wound-native-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
