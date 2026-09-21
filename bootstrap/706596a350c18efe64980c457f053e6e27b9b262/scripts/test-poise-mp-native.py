"""Native full executor: Poise must not discount Damage-to-MP interception."""
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text());ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
FIX=ROOT/'build/expansion/probes/samurai-state'/meta['baseSha1'];ram=(FIX/'execute-trap.ram').read_bytes();iw=(FIX/'execute-trap.iwram').read_bytes();regs=struct.unpack_from('<17I',(FIX/'execute-trap.state').read_bytes(),0x20)
UNIT,TARGET,RETURN,STACK=0x02000080,0x020033e4,0x08000100,0x03006800
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
control=bytearray(rom);p=meta['symbols']['ffta_poise_factor']-0x08000000;control[p:p+4]=bytes.fromhex('04207047')
m,n=ARM(rom,iw),ARM(control,iw);m.put(0x02000000,ram)
def invalid_memory(u,access,address,size,value,data):
 print('invalid_memory',hex(address),'pc',hex(u.reg_read(UC_ARM_REG_PC)),'sp',hex(u.reg_read(UC_ARM_REG_SP)),'lr',hex(u.reg_read(UC_ARM_REG_LR)),flush=True)
 return False
for machine in (m,n):machine.u.hook_add(UC_HOOK_MEM_INVALID,invalid_memory)
from native_battle_wrappers import from_memory
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()}
bank=m.word(m.word(0x080cd538)+4)
reaction=next(i for i in range(144) if struct.unpack_from('<H',m.read(bank+8*i,8),4)[0]==13 and m.read(bank+8*i+6,1)[0]==2)
checks=collections.Counter();outcomes=[]
def check(k,a,b):checks[k]+=1;assert a==b,(k,a,b)
def half(machine,p):return int.from_bytes(machine.read(p,2),'little')
for action,mp,seed in itertools.product((0,23,90,112,125,266,347,355),(0,1,49,999),range(8)):
 pair=[]
 for machine in (n,m):
  machine.put(0x02000000,ram);machine.put(0x03000000,iw);machine.put(0x0203ff44,bytes(8));machine.put(0x02001e98,bytes(108))
  for unit,x in ((TARGET,4),(UNIT,5)):
   machine.put(unit+5,bytes((116,1,116)));machine.put(unit+0xe8,bytes(8));machine.put(unit+0x3a,bytes(2));machine.put(unit+0x18,struct.pack('<4H',500,500,999,999));machine.put(unit+0x2a,struct.pack('<5H',383,0,0,0,0));machine.put(unit+0xf6,bytes((x,14)));machine.put(wrappers[unit]+8,struct.pack('<3H',x*32+16,32,14*32+16))
  machine.put(UNIT+0xe8,b'\x08');machine.put(UNIT+0x3b,bytes([154]));machine.put(0x02001b4a,b'\xff');machine.put(UNIT+0x3a,bytes([reaction]));machine.put(UNIT+0x40+reaction,b'\xff');machine.put(UNIT+0x1c,struct.pack('<H',mp))
  check('equipped_Poise',machine.call(0x080cd50c,UNIT),129);check('equipped_MP_reaction',machine.call(0x080cd4d4,UNIT),13)
  # Query native admission independently, outside magnitude execution. Restore
  # its global scratch before the real executor, retaining only the oracle.
  saved_ram=machine.read(0x02000000,0x40000);saved_iw=machine.read(0x03000000,0x8000)
  admitted=machine.call(0x0812e6e0,TARGET,UNIT,action,13,stack=STACK)
  machine.put(0x02000000,saved_ram);machine.put(0x03000000,saved_iw)
  machine.put(0x030034b0,struct.pack('<I',seed));machine.put(regs[13],struct.pack('<4I',action,0,0,255))
  machine.call(0x080a433c,regs[0],wrappers[TARGET],5,14,stack=regs[13])
  pair.append(dict(hp=half(machine,UNIT+0x18),mp=half(machine,UNIT+0x1c),wound=half(machine,0x02001ebc),admitted=admitted))
  check('private_roots_retired',machine.read(0x0203ff44,8),bytes(8))
 print(action,mp,seed,pair,flush=True)
 check('native_admission_unchanged',pair[1]['admitted'],pair[0]['admitted'])
 if pair[0]['admitted']:
  check('MP_interception_unchanged',pair[1],pair[0]);check('redirected_HP_unchanged',pair[1]['hp'],500)
 else:
  check('no_MP_interception_without_admission',pair[1]['mp'],mp)
  check('HP_mitigation_not_increase',pair[1]['hp']>=pair[0]['hp'],True)
 outcomes.append(dict(action=action,mp=mp,seed=seed,control=pair[0],poise=pair[1]))
check('positive_MP_interception_exercised',any(x['mp'] and x['control']['mp']<x['mp'] for x in outcomes),True)
check('empty_MP_HP_mitigation_exercised',any(not x['mp'] and x['poise']['hp']>x['control']['hp'] for x in outcomes),True)
for action in (0,23,90,112,125,266,347,355):
 rows=[x for x in outcomes if x['action']==action]
 check('each_action_intercepts_positive_MP',any(x['mp']>1 and x['control']['mp']<x['mp'] for x in rows),True)
 check('each_action_mitigates_positive_HP',any(not x['mp'] and x['poise']['hp']>x['control']['hp'] for x in rows),True)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),outcomes=outcomes,scope=__doc__)
(ROM.parent/'poise-mp-native.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
