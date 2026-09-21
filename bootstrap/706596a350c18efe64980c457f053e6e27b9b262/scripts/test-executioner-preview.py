"""Native UI chance entry differential, isolated or actual installed hook."""
import ast,hashlib,json,pathlib,struct,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
CURRENT='--current' in sys.argv
P=ROOT/'build/expansion/probes';OUT=P/'executioner-preview';OUT.mkdir(exist_ok=True)
rom=(P/'combat.gba').read_bytes();clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
TARGET,WRAPPER=0x020033e4,0x02022874
sha=lambda b:hashlib.sha1(b).hexdigest()
if CURRENT:
 symbols={p[2]:int(p[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=l.split())==3}
 assert struct.unpack_from('<I',rom,0xb581c)[0]==symbols['ffta_executioner_preview_entry']|1
 patched=rom
else:
 prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
 subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-I',str(ROOT/'build/expansion'),'-Wl,-Ttext=0x091d0000,-e,ffta_executioner_preview_entry',str(ROOT/'src/engine/gladiator-finishers.c'),str(ROOT/'src/engine/gladiator-finishers.s'),'-o',str(OUT/'preview.elf')],check=True)
 subprocess.run([prefix+'objcopy.exe','-O','binary',str(OUT/'preview.elf'),str(OUT/'preview.bin')],check=True)
 symbols={p[2]:int(p[0],16) for l in subprocess.check_output([prefix+'nm.exe','-n',str(OUT/'preview.elf')],text=True).splitlines() if len(p:=l.split())==3}
 patched=bytearray(rom);code=(OUT/'preview.bin').read_bytes();assert patched[0x11d0000:0x11d0000+len(code)]==b'\xff'*len(code)
 patched[0x11d0000:0x11d0000+len(code)]=code;assert patched[0xb5816:0xb5820]==clean[0xb5816:0xb5820]
 struct.pack_into('<HHHI',patched,0xb5816,0xb408,0x4b00,0x4718,symbols['ffta_executioner_preview_entry']|1)
 patched=bytes(patched);(OUT/'isolated.gba').write_bytes(patched)
base=bytearray(patched);base[0xb5816:0xb5820]=clean[0xb5816:0xb5820]
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
native,expanded=ARM(bytes(base),bytes(0x8000)),ARM(patched,bytes(0x8000))
R=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
checks=0;entries=[]
def centry(u,pc,size,_):entries.append(u.reg_read(UC_ARM_REG_SP))
expanded.u.hook_add(UC_HOOK_CODE,centry,begin=symbols['ffta_executioner_preview_chance'],end=symbols['ffta_executioner_preview_chance'])
def run(m,chance,action,hp,maximum,residue,v):
 sp=STACK+residue;m.put(sp,b'\x91'*128);m.put(TARGET,b'\x59'*264);m.put(TARGET+0x18,struct.pack('<HH',hp,maximum));m.put(WRAPPER,struct.pack('<I',TARGET))
 m.u.reg_write(UC_ARM_REG_CPSR,0x30|(0xf0000000 if v else 0xe0000000))
 for n,r in enumerate(R):m.u.reg_write(r,0x55000000+n)
 for reg,val in [(UC_ARM_REG_R4,chance),(UC_ARM_REG_R6,WRAPPER),(UC_ARM_REG_R8,action),(UC_ARM_REG_R10,0xdeadff89),(UC_ARM_REG_SP,sp),(UC_ARM_REG_LR,RETURN|1)]:m.u.reg_write(reg,val)
 before=m.read(TARGET,264);m.u.emu_start(0x080b5817,0x080b5820,count=10000)
 assert m.u.reg_read(UC_ARM_REG_PC)==0x080b5820
 return [m.u.reg_read(r) for r in R],m.u.reg_read(UC_ARM_REG_CPSR)&0xf0000000,m.u.reg_read(UC_ARM_REG_SP),m.read(sp,128),m.read(TARGET,264)==before
for action in list(range(347))+[424,425,426,427,428,429,430,431,65535]:
 for chance in ((0,1,50,74,75,94,95,100) if action!=430 else range(101)):
  for hp,maximum in ((125,250),(126,250),(0,0)):
   for residue in (0,4):
    for v in (0,1):
     expected=min(95,chance+20) if action==430 and chance and maximum and hp*2<=maximum else chance
     a=run(native,expected,action,hp,maximum,residue,v);b=run(expanded,chance,action,hp,maximum,residue,v)
     checks+=1;assert a==b,(action,chance,hp,maximum,residue,v,a[:3],b[:3])
assert entries and all(x%8==0 for x in entries)
report=dict(passed=True,current=CURRENT,inputSha1=sha(rom),testSha1=sha(patched),checks=checks,alignedCalls=len(entries),scope='Exact installed UI argument/flags/frame and explicit-target isolation; no original action changes')
(OUT/('current-report.json' if CURRENT else 'report.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
