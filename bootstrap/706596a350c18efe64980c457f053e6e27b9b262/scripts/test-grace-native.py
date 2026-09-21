"""Grace: native A accuracy, independent frontal-divisor oracle and untouched S."""
import ast,collections,hashlib,itertools,json,pathlib,struct,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
P=ROOT/'build/expansion/probes';OUT=P/'grace';OUT.mkdir(exist_ok=True)
CURRENT='--current' in sys.argv
if CURRENT:
 base=bytearray((P/'combat.gba').read_bytes());clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();base[0x12c89c:0x12c8a8]=clean[0x12c89c:0x12c8a8]
 rom=(P/'combat.gba').read_bytes();symbols={p[2]:int(p[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=l.split())==3}
 assert struct.unpack_from('<I',rom,0x12c8a4)[0]==symbols['ffta_grace_evade_entry']|1
else:
 source=json.loads((P/'dark-sword/current.json').read_text());base=pathlib.Path(source['path']).read_bytes();assert hashlib.sha1(base).hexdigest()==source['romSha1']
 prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=OUT/'grace.elf';binary=OUT/'grace.bin'
 subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-I',str(ROOT/'build/expansion'),'-Wl,-Ttext=0x091a0000,-e,ffta_grace_evade_entry',str(ROOT/'src/engine/mobility-supports.c'),str(ROOT/'src/engine/mobility-supports.s'),'-o',str(elf)],check=True)
 subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True)
 symbols={p[2]:int(p[0],16) for l in subprocess.check_output([prefix+'nm.exe','-n',str(elf)],text=True).splitlines() if len(p:=l.split())==3}
 rom=bytearray(base);code=binary.read_bytes();assert rom[0x11a0000:0x11a0000+len(code)]==b'\xff'*len(code);rom[0x11a0000:0x11a0000+len(code)]=code
 assert rom[0x12c89c:0x12c8a8].hex()=='00214156301c15f009ff041c'
 struct.pack_into('<HHHHI',rom,0x12c89c,0xb408,0x46c0,0x4b00,0x4718,symbols['ffta_grace_evade_entry']|1)
sha=lambda b:hashlib.sha1(b).hexdigest();LAB=OUT/sha(rom);LAB.mkdir(exist_ok=True)
(LAB/'grace.gba').write_bytes(rom);(LAB/'control.gba').write_bytes(base)
oracle=bytearray(base);assert oracle[0x3a8444:0x3a8448]==bytes([1,2,2,4]);oracle[0x3a8444:0x3a8448]=bytes([1]*4)
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000;TARGET=0x020033e4
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=300000'));exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
SNAP=P/'chop-preview-council/9f773e96fa6f98ceb9fc443ee96c56a8a64c4adc-break-exec-seed0';iwram=(SNAP/'after.iwram').read_bytes();ram=(SNAP/'after.ram').read_bytes()
n,m,o=ARM(base,iwram),ARM(rom,iwram),ARM(oracle,iwram);counts=collections.Counter();samples=[];hookcalls=[];observedA=set()
def check(group,a,b):counts[group]+=1;assert a==b,(group,a,b)
def centry(u,pc,size,_):hookcalls.append(u.reg_read(UC_ARM_REG_SP)%8)
m.u.hook_add(UC_HOOK_CODE,centry,begin=symbols['ffta_grace_evade_divisor']&~1,end=symbols['ffta_grace_evade_divisor']&~1)
pointers=struct.unpack_from('<I',base,0xcd538)[0]
def fixture(machine,support=140,attack_support=0,reaction=0,status=-1,job=33):
 machine.put(0x02000000,ram);machine.put(0x03000000,iwram)
 table=bytearray(base[pointers-0x08000000:pointers-0x08000000+96]);machine.put(0x080cd538,struct.pack('<I',0x02021800));machine.put(0x080cd500,struct.pack('<I',0x02021800))
 for race,sptr,sval in ((1,0x02024000,attack_support),(4,0x02025000,support)):
  p=struct.unpack_from('<I',table,race*4)[0];data=bytearray(base[p-0x08000000:p-0x08000000+0x800])
  struct.pack_into('<HHHBB',data,0x80*8,0,0,sval,3,1);struct.pack_into('<HHHBB',data,0x81*8,0,0,reaction,2,1)
  machine.put(sptr,data);struct.pack_into('<I',table,race*4,sptr)
 machine.put(0x02021800,table)
 a=bytearray(ram[0x80:0x80+264]);b=bytearray(ram[0x5a8:0x5a8+264])
 a[0x3b]=0x80 if attack_support else 0;b[0x3b]=0x80 if support else 0;b[0x3a]=0x81 if reaction else 0
 a[4]=b[4]=1;a[6]=1;b[6]=4;b[5]=b[7]=b[0x35]=job
 struct.pack_into('<HHHH',a,0x18,100,100,50,50);struct.pack_into('<HHHH',b,0x18,100,100,50,50)
 a[0xe8:0xf0]=bytes(8);b[0xe8:0xf0]=bytes(8)
 if status>=0:b[0xe8+status//8]|=1<<(status%8)
 machine.put(UNIT,a);machine.put(TARGET,b)
def A(machine,xy=(7,6),facing=0,kind=1,reactions=0,residue=0,targetxy=(6,6)):
 sp=STACK+residue;machine.put(sp,struct.pack('<6I',xy[1],*targetxy,facing,reactions,kind));before=machine.read(UNIT,264)+machine.read(TARGET,264)
 value=machine.call(0x0812c7f4,UNIT,TARGET,389,xy[0],stack=sp)
 check('A-unit-isolation',machine.read(UNIT,264)+machine.read(TARGET,264),before);observedA.add(value);return value
xylist=((7,6),(7,7),(6,7),(5,7),(5,6),(5,5),(6,5),(7,5))
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12]
def inline(machine,index,evade,residue,v):
 sp=STACK+residue;machine.put(sp,b'\x91'*128)
 machine.u.reg_write(UC_ARM_REG_CPSR,0x30|(0xf0000000 if v else 0xe0000000))
 for i,r in enumerate(REGS):machine.u.reg_write(r,0x55000000+i)
 for reg,val in ((UC_ARM_REG_R0,0x083a8444+index),(UC_ARM_REG_R6,evade),(UC_ARM_REG_R7,TARGET),(UC_ARM_REG_SP,sp),(UC_ARM_REG_LR,RETURN|1)):machine.u.reg_write(reg,val)
 machine.u.emu_start(0x0812c89d,0x0812c8a8,count=10000)
 assert machine.u.reg_read(UC_ARM_REG_PC)==0x0812c8a8
 return [machine.u.reg_read(r) for r in REGS],machine.u.reg_read(UC_ARM_REG_CPSR)&0xf0000000,machine.u.reg_read(UC_ARM_REG_SP),machine.read(sp,128)
for support,index,evade,residue,v in itertools.product((0,11,13,140,141),range(4),(0,1,4,50,127,255,0xffffffff),(0,4),(0,1)):
 fixture(n,support);fixture(m,support)
 check('installed-inline-live-registers-flags-frame',inline(m,index,evade,residue,v),inline(n,0 if support==140 else index,evade,residue,v))
for support,attack_support,xy,facing,kind,residue in itertools.product((0,1,4,13,140,141),(0,4,13),xylist,range(4),(0,1),(0,4)):
 for machine in (n,m,o):fixture(machine,support,attack_support)
 expected=A(o if support==140 else n,xy,facing,kind,0,residue);value=A(m,xy,facing,kind,0,residue)
 check('all-facing-A-physical-magic',value,expected)
 if support==140 and not attack_support and xy==(7,6) and kind==1 and not residue:samples.append(dict(facing=facing,ordinary=A(n,xy,facing),grace=value))
# Original automatic hit/prevention logic executes before the hook; statuses
# and all native reaction IDs retain exact independent-oracle behavior.
for support,status,reaction,kind,facing,residue in itertools.product((0,140),range(64),(0,1,2,3,4,5,6,7,8,9,10,11,12,13),(0,1),(0,2),(0,4)):
 for machine in (n,m,o):fixture(machine,support,reaction=reaction,status=status)
 check('native-status-reaction-prevention',A(m,xy=(4,14),targetxy=(5,14),facing=facing,kind=kind,reactions=1,residue=residue),A(o if support==140 else n,xy=(4,14),targetxy=(5,14),facing=facing,kind=kind,reactions=1,residue=residue))
def S(machine,status,xy,facing,residue):
 sp=STACK+residue;machine.put(sp,struct.pack('<4I',6,6,facing,status));return machine.call(0x0812d1dc,UNIT,TARGET,xy[0],xy[1],stack=sp)
for support,attack_support,status,xy,facing,residue in itertools.product((0,11,140),(0,4,11,13),range(4,65),xylist,range(4),(0,4)):
 fixture(n,0 if support==140 else support,attack_support);fixture(m,support,attack_support)
 check('SRes-unchanged-including-Turbo',S(m,status,xy,facing,residue),S(n,status,xy,facing,residue))
check('C-stack-alignment',set(hookcalls),{0})
check('nonvacuous-prevention-automatic-hit-and-cap',(0 in observedA,95 in observedA,100 in observedA),(True,True,True))
report=dict(passed=True,current=CURRENT,baseSha1=sha(base),romSha1=sha(rom),path=str(LAB/'grace.gba'),symbols=symbols,checks=dict(counts),total=sum(counts.values()),samples=samples)
(LAB/'native-report.json').write_text(json.dumps(report,indent=2));(OUT/'current.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='symbols'},indent=2))

