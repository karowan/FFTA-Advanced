"""Native Tsunami damage, center-driven legal displacement and water-only MP loss."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT/'tools/arm-python'),str(ROOT/'scripts')]
from unicorn import *
from unicorn.arm_const import *
from native_battle_wrappers import from_memory
meta=_load_job_candidate(ROOT/'build/expansion/probes/viking/current.json');ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes();S=meta['symbols'];fix=ROM.parent/'executor'
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes();regs=struct.unpack_from('<17I',(fix/'execute-trap.state').read_bytes(),0x20)
UNIT,TARGET,ALLY,EQUIPMENT,RETURN,STACK,GRID=0x02000080,0x020033e4,0x02000398,0x02002000,0x08000100,0x03007000,0x02026000
node=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'));exec(compile(ast.Module(body=[n for n in node.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m=ARM(rom,iw);wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()};checks=collections.Counter();samples=[];traces=[]
def check(k,a,b):checks[k]+=1;assert a==b,(k,a,b,globals().get('case'))
def reset(center,target,water,sea,block=False,uphill=False):
 m.put(0x02000000,ram);m.put(0x03000000,iw);m.put(0x0203ff44,bytes(8));m.call(S['ffta_job_reset'])
 for unit in wrappers:
  xy=(6,6) if unit==UNIT else (target if unit==TARGET else ((9,6) if unit==ALLY and block else (0,0)))
  m.put(unit+0xf6,bytes(xy));m.put(wrappers[unit]+8,struct.pack('<H',xy[0]<<5));m.put(wrappers[unit]+12,struct.pack('<H',xy[1]<<5))
 for unit in (UNIT,TARGET):
  m.put(unit+0xe8,bytes(8));m.put(unit+0x3a,bytes(2));m.put(unit+0x18,struct.pack('<4H',250,250,50,50));m.put(unit+0x2a,struct.pack('<5H',399,0,0,0,0))
  m.put(unit+5,bytes([118,2,118]));m.put(unit+0x35,b'\x76');m.put(unit+0x29,bytes([0 if unit==UNIT else 128]))
 m.put(TARGET+0x3b,bytes([100 if sea else 0]))
 grid=bytearray(bytes([16,0])*256)
 if water:grid[2*(5*16+6)+1]=2
 if uphill:grid[2*(6*16+9)]=17
 m.put(GRID,grid);info=bytearray(16);struct.pack_into('<I',info,4,GRID);info[8]=info[13]=info[15]=16;m.put(0x02007f10,info)
def observe(u,pc,size,data):
 ctx=u.reg_read(UC_ARM_REG_R0);c=bytes(u.mem_read(ctx,0x34));traces.append(dict(case=case,ctx=hex(ctx),data=c.hex(),target=bytes(u.mem_read(TARGET+0x18,8)).hex()))
pc=S['ffta_viking_tsunami_apply'];m.u.hook_add(UC_HOOK_CODE,observe,begin=pc,end=pc)
for center,target,want in [((8,6),(8,6),(9,6)),((8,6),(8,7),(8,8)),((8,6),(7,6),(6,6)),((8,8),(8,8),(8,8))]:
 for water,sea,seed in itertools.product((0,1),(0,1),range(16)):
  case=(center,target,water,sea,seed);reset(center,target,water,sea)
  check('native-water-affinity',m.call(S['ffta_viking_near_water'],UNIT),water)
  m.put(0x030034b0,struct.pack('<I',seed));m.put(regs[13],struct.pack('<4I',372,0,0,255))
  m.call(0x080a433c,regs[0],wrappers[UNIT],*center,stack=regs[13])
  damage=250-struct.unpack('<H',m.read(TARGET+0x18,2))[0];mp=struct.unpack('<H',m.read(TARGET+0x1c,2))[0];xy=tuple(m.read(TARGET+0xf6,2))
  sample=dict(case=case,damage=damage,mp=mp,xy=xy);samples.append(sample)
  (ROM.parent/'tsunami-observed.json').write_text(json.dumps(dict(samples=samples,traces=traces),indent=2))
  check('one-native-cost',struct.unpack('<H',m.read(UNIT+0x1c,2))[0],32)
  check('water-MP-loss-independent-of-Sea-Legs',mp,42 if water and damage>0 else 50)
  # Landing on caster (6,6) is occupied, so the western target stays put.
  expected=want if damage>0 and not sea and want!=(6,6) else target
  check('native-center-push',xy,expected)
check('nonvacuous-native-damage',any(s['damage']>0 for s in samples),True)
check('nonvacuous-native-miss',any(s['damage']==0 for s in samples),True)
for block,uphill in [(True,False),(False,True)]:
 for seed in range(16):
  case=('illegal-landing',block,uphill,seed);reset((8,6),(8,6),1,0,block,uphill)
  m.put(0x030034b0,struct.pack('<I',seed));m.put(regs[13],struct.pack('<4I',372,0,0,255));m.call(0x080a433c,regs[0],wrappers[UNIT],8,6,stack=regs[13])
  check('occupied-or-uphill-landing-rejected',m.read(TARGET+0xf6,2),bytes([8,6]))
for key in (18,19,26):check('no-reflect-doublecast-return',m.call(0x080ccd50,372,key),0)
reset((8,6),(8,6),0,0);m.put(UNIT+0xeb,b'\x08');check('incanted-Silence-block',m.call(0x08133e18,UNIT,372,255),0)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),samples=samples,scope=__doc__)
(ROM.parent/'tsunami.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
