"""Native recruitment lesson-count loop with expanded-job and original controls."""
import ast,collections,hashlib,itertools,json,pathlib,struct,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
P=ROOT/'build/expansion/probes';OUT=P/'recruit-prerequisites';OUT.mkdir(exist_ok=True)
base=(P/'combat.gba').read_bytes();meta=json.loads((P/'combat.json').read_text());assert hashlib.sha1(base).hexdigest()==meta['romSha1']
symbols={p[2]:int(p[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=l.split())==3}
if '--current' in sys.argv:
 rom=base;control=bytearray(base);clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();control[0x620ac:0x620b8]=clean[0x620ac:0x620b8];base=bytes(control)
else:
 prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=OUT/'private.elf';binary=OUT/'private.bin'
 (OUT/'link.s').write_text('.syntax unified\n.cpu arm7tdmi\n.thumb\n.global ffta_job_prerequisite_count\n.thumb_func\nffta_job_prerequisite_count:\n ldr r3,='+hex(symbols['ffta_job_prerequisite_count']|1)+'\n bx r3\n')
 subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-Wl,-Ttext=0x09190000,-e,ffta_recruit_prerequisite_entry',str(OUT/'link.s'),str(ROOT/'src/engine/recruit-prerequisites.c'),str(ROOT/'src/engine/recruit-prerequisites.s'),'-o',str(elf)],check=True)
 subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True)
 symbols.update({p[2]:int(p[0],16) for l in subprocess.check_output([prefix+'nm.exe','-n',str(elf)],text=True).splitlines() if len(p:=l.split())==3})
 rom=bytearray(base);code=binary.read_bytes();assert rom[0x1190000:0x1190000+len(code)]==b'\xff'*len(code);rom[0x1190000:0x1190000+len(code)]=code
 assert rom[0x620ac:0x620b8].hex()=='281c291c252266f05dfa041c'
 struct.pack_into('<HHHHI',rom,0x620ac,0xb408,0x46c0,0x4b00,0x4718,symbols['ffta_recruit_prerequisite_entry']|1)
LAB=OUT/hashlib.sha1(rom).hexdigest();LAB.mkdir(exist_ok=True);(LAB/'private.gba').write_bytes(rom)
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=300000'))
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
SNAP=P/'chop-preview-council/9f773e96fa6f98ceb9fc443ee96c56a8a64c4adc-break-exec-seed0';iwram=(SNAP/'after.iwram').read_bytes();ram=(SNAP/'after.ram').read_bytes()
m,n=ARM(rom,iwram),ARM(base,iwram);counts=collections.Counter();align=[]
def check(g,a,b):counts[g]+=1;assert a==b,(g,a,b)
m.u.hook_add(UC_HOOK_CODE,lambda u,p,s,d:align.append(u.reg_read(UC_ARM_REG_SP)%8),begin=symbols['ffta_recruit_prerequisite_count']&~1,end=symbols['ffta_recruit_prerequisite_count']&~1)
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
def fixture(machine,race,mode):
 machine.put(0x02000000,ram);machine.put(0x03000000,iwram);machine.put(0x02001e70,b'FFTAEXP1\x01')
 u=bytearray(264);u[4]=1;u[6]=race;u[5]=u[7]=2 if race==1 else 16
 for i in range(142):u[0x40+i]=(127 if mode==1 else 128 if mode==2 else (i*17)%128 if mode==3 else 0)
 machine.put(UNIT,u);machine.put(0x02001b40,bytes((127 if mode==1 else 128 if mode==2 else ((i+144)*17)%128 if mode==3 else 0) for i in range(34)))
 if mode==4:
  for i in (range(172,178) if race==1 else range(105,111) if race==2 else ()):
   machine.put(0x02001b40+i-144 if race==1 else UNIT+0x40+i,b'\x7f')
def loop(machine,job,residue,v):
 sp=STACK+residue;machine.put(sp,b'\xa5'*128);machine.u.reg_write(UC_ARM_REG_CPSR,0x30|(0xf0000000 if v else 0xe0000000))
 for i,r in enumerate((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12)):machine.u.reg_write(r,0x55000000+i)
 for reg,value in ((UC_ARM_REG_R5,job),(UC_ARM_REG_R7,UNIT),(UC_ARM_REG_SP,sp),(UC_ARM_REG_LR,RETURN|1)):machine.u.reg_write(reg,value)
 machine.u.emu_start(0x080620ad,0x08062112,count=300000)
 assert machine.u.reg_read(UC_ARM_REG_PC)==0x08062112
 return machine.u.reg_read(UC_ARM_REG_R3)
for job,mode,residue,v in itertools.product(tuple(range(2,80))+tuple(range(116,126)),range(5),(0,4),(0,1)):
 race=n.call(0x080c8570,job,job,1)
 if not 1<=race<=5:continue
 for machine in (m,n):fixture(machine,race,mode)
 before=m.read(0x02000000,0x40000);actual=loop(m,job,residue,v)
 if job not in (2,16) and not 116<=job<=125:
  expected=loop(n,job,residue,v);group='original_jobs_native_loop'
 else:
  # Independent table/list oracle, not the production counter itself.
  if job in (2,16):indices=list(range(1,12)) + list(range(172,178)) if job==2 else list(range(33,44))+list(range(105,111))
  else:indices=[o['abilityIndex'] for l in registry['lessons'] for o in l['owners'] if o['jobId']==job]
  expected=0
  for index in indices:
   row=n.call(0x080cd480,race,index);record=n.read(row,8)
   ap=m.read(UNIT+0x40+index if race!=1 or index<142 else 0x02001b40+index-144,1)[0]
   expected+=int(record[6]==1 and (ap&127)>=record[7])
  group='expanded_lists_independent_oracle'
 check(group,actual,expected);check('unit_and_saved_state_unchanged',m.read(0x02000000,0x40000),before);check('balanced_SP',m.u.reg_read(UC_ARM_REG_SP),STACK+residue);check('caller_guard',m.read(STACK+residue+24,104),b'\xa5'*104)
check('C_stack_alignment',set(align),{0})
result={'passed':True,'romSha1':hashlib.sha1(rom).hexdigest(),'baseSha1':meta['romSha1'],'checks':sum(counts.values()),'groups':dict(counts),'scope':__doc__}
(LAB/'native.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
