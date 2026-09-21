"""Isolated native arc facing hook replay and ABI differentials.

Executes each actual veneer and native continuation. Original IDs compare
against the unmodified native fragment; arc oracles change only the explicitly
carried facing. This tests setup contracts, not a complete autonomous AI turn.
"""
import ast,ctypes as C,hashlib,importlib.util,itertools,json,pathlib,struct,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')],type_ignores=[]),'<native harness>','exec'))
P=ROOT/'build/expansion/probes';OUT=P/'arc-facing-hooks';OUT.mkdir(parents=True,exist_ok=True)
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');sources=['combat-area.c','combat-area.s']
for name in sources:(OUT/name).write_bytes((ROOT/'src/engine'/name).read_bytes())
subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-I',str(ROOT/'build/expansion'),'-Wl,-Ttext=0x091f0000','-Wl,-e,ffta_area_list',*[str(OUT/s) for s in sources],'-o',str(OUT/'hooks.elf')],check=True,capture_output=True)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(OUT/'hooks.elf'),str(OUT/'hooks.bin')],check=True)
symbols={p[2]:int(p[0],16) for l in subprocess.check_output([prefix+'nm.exe','-n',str(OUT/'hooks.elf')],text=True).splitlines() if len(p:=l.split())==3}
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();rom=bytearray(clean+bytes(0x1000000));binary=(OUT/'hooks.bin').read_bytes();rom[0x11f0000:0x11f0000+len(binary)]=binary
SITES={'confirm':(0xb6fb6,0xb6fc0,'ffta_arc_confirm_entry'),'commit':(0xa3aba,0xa3ac8,'ffta_arc_commit_entry'),'ai':(0x93a66,0x93a70,'ffta_arc_ai_entry'),'launch':(0x96a40,0x96a4c,'ffta_arc_launch_entry')}
for begin,end,name in SITES.values():
 if begin%4:struct.pack_into('<HHHI',rom,begin,0xb408,0x4b00,0x4718,symbols[name]|1)
 else:struct.pack_into('<HHHHI',rom,begin,0xb408,0x46c0,0x4b00,0x4718,symbols[name]|1)
CURRENT='--current' in sys.argv
if CURRENT:
 meta=json.loads((P/'combat.json').read_text());rom=(P/'combat.gba').read_bytes();binary=(ROOT/'build/expansion/engine.bin').read_bytes()
 assert hashlib.sha1(rom).hexdigest()==meta['romSha1'] and hashlib.sha1(binary).hexdigest()==meta['engineSha1']
 symbols={p[2]:int(p[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=l.split())==3}
 for begin,end,name in SITES.values():
  pointer=struct.unpack_from('<I',rom,begin+(6 if begin%4 else 8))[0]
  assert pointer==symbols[name]|1,('Installed hook',name,hex(pointer))
 (OUT/'current-frozen.gba').write_bytes(rom)
iwram=iwram_from_boot();native,patched=ARM(clean,iwram),ARM(bytes(rom),iwram)
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12]
WRAPPER,SELECTION,OBJECT,MANAGER,EVENT,NODE=0x02020000,0x02021000,0x02022000,0x02023000,0x02024000,0x02015488
counts={};case=None
def check(group,a,b):
 assert a==b,(group,case,a,b)
 counts[group]=counts.get(group,0)+1
def alignment(u,address,size,data):check('C_entry_alignment',u.reg_read(UC_ARM_REG_SP)%8,0)
for name in ('ffta_arc_confirm_facing','ffta_arc_commit_facing','ffta_arc_ai_facing','ffta_arc_launch_facing'):
 patched.u.hook_add(UC_HOOK_CODE,alignment,begin=symbols[name],end=symbols[name])

def segment(machine,kind,action,face,fallback,residue,flags,branch,denial='',oracle=False):
 u=machine.u;sp=STACK+residue;arc=action in (426,429)
 machine.put(STACK-256,b'\xa5'*0x700)
 machine.put(WRAPPER,b'\0'*0x6000);machine.put(NODE,b'\0'*0x21c)
 pointer=0 if denial=='null' else WRAPPER
 machine.put(WRAPPER,struct.pack('<I',UNIT));machine.put(WRAPPER+0x1f,bytes((face,)))
 machine.put(SELECTION,struct.pack('<I',pointer));machine.put(SELECTION+0xec,struct.pack('<H',action))
 machine.put(OBJECT,struct.pack('<I',pointer));machine.put(OBJECT+4,struct.pack('<H',0x1201));machine.put(OBJECT+8,bytes((fallback,)));machine.put(OBJECT+0x10,struct.pack('<H',action))
 machine.put(MANAGER+4,struct.pack('<I',pointer));machine.put(MANAGER+0xa6,struct.pack('<H',action))
 machine.put(NODE,struct.pack('<I',WRAPPER+4 if denial=='owner' else pointer));machine.put(NODE+8,struct.pack('<H',action+1 if denial=='action' else action));machine.put(NODE+0x1b0,bytes((face,0 if denial=='unsuccessful' else 1)))
 machine.put(sp+0x360,struct.pack('<I',branch));machine.put(sp+0x364,struct.pack('<I',action))
 allowed=arc and pointer and face<4 and (kind!='ai' or denial not in ('owner','action','unsuccessful'))
 values={0:face if oracle and allowed and kind=='launch' else fallback,3:face if oracle and allowed and kind=='confirm' else fallback,7:OBJECT if kind=='commit' else EVENT,8:SELECTION if kind=='confirm' else MANAGER}
 if oracle and allowed and kind=='commit':machine.put(OBJECT+8,bytes((face,)))
 if kind=='ai':
  machine.put(WRAPPER+0x1f,bytes((face if oracle and allowed else fallback,)))
 for i,r in enumerate(REGS):u.reg_write(r,values.get(i,0x55000000+i))
 u.reg_write(UC_ARM_REG_CPSR,flags|0x30);u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,RETURN|1)
 writes=[];begin,end,_=SITES[kind]
 def stop(u,address,size,data):
  if address==0x08000000+end:u.emu_stop()
 def written(u,access,address,size,value,data):writes.append((address,size))
 h=u.hook_add(UC_HOOK_CODE,stop);w=u.hook_add(UC_HOOK_MEM_WRITE,written)
 try:u.emu_start(0x08000001+begin,0,count=10000)
 finally:u.hook_del(h);u.hook_del(w)
 check('native_continuation',u.reg_read(UC_ARM_REG_PC),0x08000000+end);check('stack_restored',u.reg_read(UC_ARM_REG_SP),sp)
 # Scratch space below SP belongs to hooks; all caller-visible storage matches.
 result={'regs':[u.reg_read(r) for r in REGS],'flags':u.reg_read(UC_ARM_REG_CPSR)&0xf0000000,'frame':machine.read(sp,0x400),'objects':machine.read(WRAPPER,0x6000),'node':machine.read(NODE,0x21c)}
 if machine is patched:
  valid=lambda p,n: sp-256<=p and p+n<=sp or (kind=='commit' and p in (OBJECT+4,OBJECT+8)) or (kind=='ai' and p in (WRAPPER+0x1f,MANAGER+8,EVENT)) or (kind=='launch' and p in (MANAGER+0x88,MANAGER+0x8a))
  check('scoped_writes',all(valid(p,n) for p,n in writes),True)
 return result

for kind,action,face,residue,flags,branch in itertools.product(SITES,range(347),range(4),(0,4),(0,0x10000000,0x20000000,0x30000000),(0,1)):
 case=(kind,action,face,residue,flags,branch)
 a=segment(native,kind,action,face,3-face,residue,flags,branch)
 b=segment(patched,kind,action,face,3-face,residue,flags,branch)
 for key in a:check('all_original_'+key,a[key],b[key])
for kind,action,face,fallback,residue,flags,branch,denial in itertools.product(SITES,(426,429),(0,1,2,3,4,255),range(4),(0,4),(0,0x10000000,0x20000000,0x30000000),(0,1),('','null','owner','action','unsuccessful')):
 case=(kind,action,face,fallback,residue,flags,branch,denial)
 a=segment(native,kind,action,face,fallback,residue,flags,branch,denial,oracle=True)
 b=segment(patched,kind,action,face,fallback,residue,flags,branch,denial)
 for key in a:check('arc_oracle_'+key,a[key],b[key])
report={'passed':True,'isolated':not CURRENT,'romSha1':hashlib.sha1(rom).hexdigest(),'checks':sum(counts.values()),'groups':counts,'binarySha1':hashlib.sha1(binary).hexdigest(),'scope':__doc__}
(OUT/'results.json').write_text(json.dumps(report,indent=2));(P/'arc-facing-hook-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
