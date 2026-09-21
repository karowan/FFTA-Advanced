"""Wound status display: original getter/cycle/renderer preservation and new key27."""
import ast, collections, hashlib, itertools, json, pathlib, struct, sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
P=ROOT/'build/expansion/probes';meta=json.loads((P/'samurai/current.json').read_text())
ROM=pathlib.Path(meta['path']);LAB=ROM.parent;rom=ROM.read_bytes();base=(LAB/'input.gba').read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
FIX=LAB/'fixture';assert hashlib.sha1((FIX/'frozen.gba').read_bytes()).hexdigest()==meta['romSha1']
ram=(FIX/'battle-ready.ram').read_bytes();iwram=(FIX/'battle-ready.iwram').read_bytes()
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=500000'))
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
n,m=ARM(base,iwram),ARM(rom,iwram);counts=collections.Counter();alignment=[]
for machine in (n,m):
 machine.u.mem_map(0x06000000,0x18000)
 machine.u.mem_map(0x05000000,0x1000)
 machine.u.mem_map(0x04000000,0x1000)
 machine.put(0x02000000,ram)
for name in ('ffta_wound_status_icon','ffta_wound_status_next_key','ffta_wound_status_visual'):
 pc=meta['symbols'][name]&~1
 m.u.hook_add(UC_HOOK_CODE,lambda u,p,s,d:alignment.append(u.reg_read(UC_ARM_REG_SP)%8),begin=pc,end=pc)
def check(group,a,b):counts[group]+=1;assert a==b,(group,a,b)
def fixture(machine,packed=0,status=-1):
 machine.put(0x02000000,ram);machine.put(0x03000000,iwram)
 machine.put(UNIT+0xe8,bytes(8));machine.put(0x02001e98,bytes([packed]))
 if status>=0:machine.put(UNIT+0xe8+status//8,bytes([1<<(status%8)]))
for status,key,residue in itertools.product(range(-1,64),range(27),(0,4)):
 for machine in (n,m):fixture(machine,status=status)
 check('native-selector-unchanged',m.call(0x0809da0c,UNIT,key,stack=STACK+residue),n.call(0x0809da0c,UNIT,key,stack=STACK+residue))
for packed,key,residue in itertools.product(range(256),(25,26),(0,4)):
 fixture(m,packed);before=m.read(0x02000000,0x40000)
 active=(packed&1)!=0 if key==25 else 1<=((packed&0x0e)>>1&3)<=2
 check('all-packed-status-selectors',m.call(0x0809da0c,UNIT,key,stack=STACK+residue),key if active else 0)
 check('getter-has-no-state-writes',m.read(0x02000000,0x40000),before)
ROW=0x02025000
for status,start,residue in itertools.product(range(-1,64),(1,2,12,24),(0,4)):
 for machine in (n,m):
  fixture(machine,status=status);machine.put(ROW,bytes([1,0,start,0,1,0,0,0,0,0,0,0]))
 for frame in range(8):
  check('native-cycle-return',m.call(0x0809dcc4,UNIT,ROW,stack=STACK+residue),n.call(0x0809dcc4,UNIT,ROW,stack=STACK+residue))
  check('native-cycle-row',m.read(ROW,12),n.read(ROW,12))
for packed in (1,2,4,8,10,12,14,15,255):
 fixture(m,packed);m.put(ROW,bytes([1,0,24,0,1,0,0,0,0,0,0,0]));seen=set()
 for frame in range(500):
  m.call(0x0809dcc4,UNIT,ROW);seen.add(m.read(ROW,2)[1])
 expected={0}
 if packed&1:expected.add(25)
 if 1<=((packed&0x0e)>>1&3)<=2:expected.add(26)
 check('reachable-custom-cycle',seen,expected)
# Exercise the actual inline renderer with every original and new visual ID.
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12]
fixture(m)
count=m.call(0x08099cdc,m.word(0x0200f4b0),0x02008000)
WRAPPER=next(m.word(0x02008000+4*i) for i in range(count) if m.word(m.word(0x02008000+4*i))==UNIT)
SPRITE=m.word(WRAPPER+0x48)
def visual(machine,icon,residue):
 fixture(machine);machine.put(WRAPPER+0x75,bytes([icon]));machine.put(SPRITE+0x28,struct.pack('<I',0x08391624));machine.put(0x06000000,b'\x6b'*0x18000)
 sp=STACK+residue;machine.put(sp,b'\x91'*128)
 machine.u.reg_write(UC_ARM_REG_CPSR,0x30)
 for i,reg in enumerate(REGS):machine.u.reg_write(reg,0x55000000+i)
 for reg,value in ((UC_ARM_REG_R6,WRAPPER),(UC_ARM_REG_R8,WRAPPER+0x75),(UC_ARM_REG_SP,sp),(UC_ARM_REG_LR,RETURN|1)):machine.u.reg_write(reg,value)
 machine.u.emu_start(0x08097ad1,0x08097ae6,count=10000)
 check('renderer-return',machine.u.reg_read(UC_ARM_REG_PC),0x08097ae6)
 return ([machine.u.reg_read(r) for r in REGS],machine.u.reg_read(UC_ARM_REG_CPSR)&0xf0000000,machine.u.reg_read(UC_ARM_REG_SP),machine.read(sp,128))
for icon,residue in itertools.product(range(1,27),(0,4)):
 check('native-renderer-live-registers-flags-frame',visual(m,icon,residue),visual(n,icon,residue))
 check('native-renderer-EWRAM',m.read(0x02000000,0x40000),n.read(0x02000000,0x40000))
 check('native-renderer-VRAM',m.read(0x06000000,0x18000),n.read(0x06000000,0x18000))
for icon,residue in itertools.product((27,),(0,4)):
 visual(m,icon,residue)
 check('custom-tile-selection',struct.unpack('<H',m.read(SPRITE+0x12,2))[0],0x1e0+(icon-25)*2)
 check('fixed-native-atlas-intact',m.read(0x06000000,0x13c80),b'\x6b'*0x13c80)
 check('dynamic-atlas-intact',m.read(0x06013cc0,0x4340),b'\x6b'*0x4340)
# Every serialized record has a defined visual state; invalid count3 is inert.
fixture(m);saved=m.read(UNIT,264)
for record in range(65536):
 m.put(0x02001ebc,struct.pack('<H',record))
 check('all_wound_encodings',m.call(0x0809da0c,UNIT,27),27 if record>>14 in (1,2) else 0)
 check('wound_getter_preserves_record',m.read(0x02001ebc,2),struct.pack('<H',record))
check('wound_getter_preserves_unit',m.read(UNIT,264),saved)
# The enclosing native renderer rearms state0 at97B40. Calling only9DCC4
# leaves adjacent active statuses parked after their first fade-out.
for record in (0x400b,0x800b):
 fixture(m,5,25);m.put(0x02001ebc,struct.pack('<H',record))
 m.put(WRAPPER+0x74,bytes([1,0,24,0,1,0,0,0,0,0,0,0]));seen=set()
 for frame in range(600):
  m.call(0x08097a04,WRAPPER,m.word(WRAPPER+0x80))
  seen.add(m.read(WRAPPER+0x75,1)[0])
 check('all_four_statuses_cycle',seen,{0,3,25,26,27})
check('C-stack-alignment',set(alignment),{0})
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(counts),total=sum(counts.values()),scope='Native original selectors/cycles/inline renderer; custom state mask and reserved writes. Full battle rendering tested separately.')
(LAB/'wound-status-native-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
