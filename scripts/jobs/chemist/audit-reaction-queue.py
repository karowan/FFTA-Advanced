"""Read-only native Counter queue observations from an immutable executor frame."""
import ast,collections,hashlib,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT/'tools/arm-python'),str(ROOT/'scripts')]
from unicorn import *
from unicorn.arm_const import *
from native_battle_wrappers import from_memory
P=ROOT/'build/expansion/probes';meta=json.loads((P/'chemist/current.json').read_text());ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1'];OUT=ROM.parent
fix=OUT/'executor';ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes();regs=struct.unpack_from('<17I',(fix/'execute-trap.state').read_bytes(),0x20)
UNIT,TARGET,RETURN,STACK=0x02000080,0x020033e4,0x08000100,0x03006800
exec(compile(ast.Module(body=[n for n in ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000')).body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m=ARM(rom,iw);wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()};events=[];cases=[];recording=False
PCs=(0x080a39f8,0x080a23b8,0x080a4e62,0x080a4adc,0x080a4c3a,0x080a529c)
def observe(u,pc,size,data):
 if not recording:return
 sp=u.reg_read(UC_ARM_REG_SP);args=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
 e=dict(pc=hex(pc),sp=hex(sp),args=[hex(x) for x in args],lr=hex(u.reg_read(UC_ARM_REG_LR)))
 if pc in (0x080a39f8,0x080a23b8):e['stackArgs']=list(struct.unpack('<8I',m.read(sp,32)))
 else:
  frame=m.read(sp,0xb8);e['frame']=frame.hex();out=struct.unpack_from('<I',frame,0x20)[0];arena,cursor,write=struct.unpack_from('<3I',frame,0x68)
  e.update(output=hex(out),count=m.read(out+0x26bd,1)[0],arena=hex(arena),cursor=hex(cursor),write=hex(write))
  if arena:e['requests']=m.read(arena,256).hex()
 events.append(e)
for pc in PCs:m.u.hook_add(UC_HOOK_CODE,observe,begin=pc,end=pc)
for action,reaction,seed in ((0,0,0),(0,8,0),(0,8,1),(23,11,0)):
 m.put(0x02000000,ram);m.put(0x03000000,iw)
 for unit,x in ((UNIT,4),(TARGET,5)):
  m.put(unit+5,bytes([2,1,2]));m.put(unit+0x35,b'\x02');m.put(unit+0x3a,bytes(2));m.put(unit+0xe8,bytes(8));m.put(unit+0x18,struct.pack('<4H',500,500,999,999));m.put(unit+0x2a,struct.pack('<5H',1,0,0,0,0));m.put(unit+0xf6,bytes([x,14]));m.put(wrappers[unit]+8,struct.pack('<H',x*32));m.put(wrappers[unit]+12,struct.pack('<H',14*32))
 if reaction:
  bank=m.word(m.word(0x080cd538)+4)
  index=next(i for i in range(144) if struct.unpack_from('<H',m.read(bank+i*8,8),4)[0]==reaction and m.read(bank+i*8+6,1)[0]==2)
  m.put(TARGET+0x3a,bytes([index]));m.put(TARGET+0x40+index,b'\xff');assert m.call(0x080cd4d4,TARGET)==reaction
 m.put(regs[13],struct.pack('<4I',action,0,0,255));m.put(0x030034b0,struct.pack('<I',seed));events=[];recording=True
 m.call(0x080a433c,regs[0],wrappers[UNIT],5,14,stack=regs[13]);recording=False
 cases.append(dict(action=action,reaction=reaction,seed=seed,events=events,hp=[int.from_bytes(m.read(u+0x18,2),'little') for u in (UNIT,TARGET)],output=m.read(regs[0],0x26c0).hex()))
assert any(e.get('requests') and bytes.fromhex(e['requests'])[14]==8 for c in cases for e in c['events']), 'Counter positive queue control absent'
report=dict(passed=True,romSha1=meta['romSha1'],scope='Unmodified native Counter/ReturnMagic queue read-only observations; no custom append acceptance',cases=cases)
(OUT/'reaction-queue-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(passed=True,romSha1=meta['romSha1'],cases=len(cases),events=sum(len(c['events']) for c in cases)),indent=2))
