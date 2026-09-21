"""Native movement getter and movement budget with transferable Light Foot."""
import ast,ctypes as C,hashlib,importlib.util,itertools,json,pathlib,struct,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')],type_ignores=[]),'<native harness>','exec'))
P=ROOT/'build/expansion/probes';OUT=P/'mobility-supports';OUT.mkdir(exist_ok=True)
base=(P/'combat.gba').read_bytes();meta=json.loads((P/'combat.json').read_text());assert hashlib.sha1(base).hexdigest()==meta['romSha1']
CURRENT='--current' in sys.argv
if CURRENT:
 OUT=OUT/'current'/meta['romSha1'];OUT.mkdir(parents=True,exist_ok=True)
 rom=bytearray(base);engine=(ROOT/'build/expansion/engine.bin').read_bytes()
 assert hashlib.sha1(engine).hexdigest()==meta['engineSha1'] and rom[0x1100000:0x1100000+len(engine)]==engine
 assert 141 in meta['supports']
 symbols={p[2]:int(p[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=l.split())==3}
 base=bytearray(base);base[0xca394:0xca3a0]=bytes.fromhex('f0b5041c1e21fef7a9ff0006');base=bytes(base)
else:
 prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=OUT/'isolated.elf';binary=OUT/'isolated.bin'
 subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-I',str(ROOT/'build/expansion'),'-Wl,-Ttext=0x091b0000','-Wl,-e,ffta_move_with_support',str(ROOT/'src/engine/mobility-supports.c'),str(ROOT/'src/engine/mobility-supports.s'),'-o',str(elf)],check=True)
 subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True)
 symbols={p[2]:int(p[0],16) for l in subprocess.check_output([prefix+'nm.exe','-n',str(elf)],text=True).splitlines() if len(p:=l.split())==3}
 rom=bytearray(base);code=binary.read_bytes();assert set(rom[0x11b0000:0x11b0000+len(code)])=={255};rom[0x11b0000:0x11b0000+len(code)]=code
 assert rom[0xca394:0xca3a0].hex()=='f0b5041c1e21fef7a9ff0006'
 struct.pack_into('<HHHHI',rom,0xca394,0xb408,0x46c0,0x4b00,0x4718,symbols['ffta_move_support_entry']|1)
(OUT/'isolated.gba').write_bytes(rom);(OUT/'base.gba').write_bytes(base)
iwram=iwram_from_boot();m,n=ARM(rom,iwram),ARM(base,iwram);original=m.word(0x080cd538);counts={}
def check(k,a,b):
 assert a==b,(k,a,b)
 counts[k]=counts.get(k,0)+1
def aligned(u,p,size,data):check('C_stack_alignment',u.reg_read(UC_ARM_REG_SP)%8,0)
m.u.hook_add(UC_HOOK_CODE,aligned,begin=symbols['ffta_move_with_support'],end=symbols['ffta_move_with_support'])
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
items=[0]+[i for i in range(1,461) if n.call(0x080ca7a4,i,16)]
for job,support,item,move,residue in itertools.product((2,13,20,33,41,116,118,120,122,124,125),tuple(range(18))+(128,140,141,142,145),(0,items[-1]),(0,1,2),(0,4)):
 for machine in (m,n):
  machine.put(0x080cd538,struct.pack('<I',original));machine.fixture(job,[item],support)
  machine.put(UNIT+0x3d,bytes((move,)));machine.put(STACK+residue,b'\xa5'*16)
 before=m.read(UNIT,264);a=n.call(0x080ca394,UNIT,stack=STACK+residue);b=m.call(0x080ca394,UNIT,stack=STACK+residue)
 check('movement_value',b,min(127,a+1) if support==141 else a)
 check('native_movement_budget',m.call(0x080ca3ec,UNIT,stack=STACK+residue),b*10)
 check('unit_unchanged',m.read(UNIT,264),before);check('caller_guard',m.read(STACK+residue,16),b'\xa5'*16)
# Real relocated racial lesson, across every ordinary Viera job, independently
# of a synthetic support row or the Dancer primary command.
viera_jobs=tuple(j for j in range(2,44) if n.call(0x080c8570,j,j,1)==4)+(124,125)
for job,item,residue in itertools.product(viera_jobs,items,(0,4)):
 for machine in (m,n):
  machine.put(0x080cd538,struct.pack('<I',original));machine.fixture(job,[item]);machine.put(UNIT+0x3b,b'\x5f')
 check('real_Viera_support',m.call(0x080cd50c,UNIT),141)
 check('all_Viera_jobs_equipment',m.call(0x080ca394,UNIT,stack=STACK+residue),n.call(0x080ca394,UNIT,stack=STACK+residue)+1)
report={'passed':True,'baseSha1':meta['romSha1'],'romSha1':hashlib.sha1(rom).hexdigest(),'checks':sum(counts.values()),'groups':counts,'movementItems':items,'scope':__doc__}
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
