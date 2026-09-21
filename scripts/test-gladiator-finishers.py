"""Isolated Executioner hooks and explicit Exposed primitives; no shared build."""
import ast,ctypes as C,hashlib,importlib.util,json,pathlib,runpy,struct,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
CURRENT='--current' in sys.argv
SHA='5b90d5fb623457405d96948e33df623b342da14c'
SOURCE=ROOT/'build/expansion/probes/tomahawk-in-game'/SHA
OUT=ROOT/'build/expansion/probes/gladiator-finishers';OUT.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha1(b).hexdigest();word=lambda b,p:struct.unpack_from('<I',b,p)[0]
base=(SOURCE/'frozen.gba').read_bytes();assert sha(base)==SHA
original={p.name:sha(p.read_bytes()) for p in SOURCE.iterdir() if p.is_file()}
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
if CURRENT:
 meta=json.loads((ROOT/'build/expansion/probes/combat.json').read_text())
 image=bytearray((ROOT/'build/expansion/probes/combat.gba').read_bytes());assert sha(image)==meta['romSha1']
 binary=(ROOT/'build/expansion/engine.bin').read_bytes();assert sha(binary)==meta['engineSha1']
 assert image[0x1100000:0x1100000+len(binary)]==binary
 for literal in (0xcd538,0xccd84,0x130684):assert image[literal:literal+4]==base[literal:literal+4],('Captured frame table moved',hex(literal))
 symbols={p[2]:int(p[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=l.split())==3}
 clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();control=bytearray(image)
 for offset,symbol in [(0x131378,'ffta_executioner_chance_entry'),(0xa3004,'ffta_executioner_roll_entry')]:
  assert word(image,offset+8)==symbols[symbol]|1
  control[offset:offset+12]=clean[offset:offset+12]
 control=bytes(control)
else:
 prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
 subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-I',str(ROOT/'build/expansion'),'-Wl,-Ttext=0x091e0000','-Wl,-e,ffta_finisher_numerator',str(ROOT/'src/engine/gladiator-finishers.c'),str(ROOT/'src/engine/gladiator-finishers.s'),'-o',str(OUT/'isolated.elf')],check=True,capture_output=True)
 subprocess.run([prefix+'objcopy.exe','-O','binary',str(OUT/'isolated.elf'),str(OUT/'isolated.bin')],check=True)
 symbols={p[2]:int(p[0],16) for l in subprocess.check_output([prefix+'nm.exe','-n',str(OUT/'isolated.elf')],text=True).splitlines() if len(p:=l.split())==3}
 image=bytearray(base);binary=(OUT/'isolated.bin').read_bytes();image[0x11e0000:0x11e0000+len(binary)]=binary
 # Unenabled430 gets a diagnostic physical descriptor identical to425. This
 # permits its native chance path without installing new gameplay or costs.
 table=word(base,0x23320)-0x08000000
 image[table+430*28:table+431*28]=base[table+425*28:table+426*28]
 control=bytes(image)
 assert base[0x131378:0x131384].hex()=='30b5104d286869682a6b5278'
 assert base[0xa3004:0xa3010].hex()=='201c8cf0e9f80006002824d1'
 for offset,symbol in [(0x131378,'ffta_executioner_chance_entry'),(0xa3004,'ffta_executioner_roll_entry')]:
  struct.pack_into('<HHHHI',image,offset,0xb408,0x46c0,0x4b00,0x4718,symbols[symbol]|1)
 (OUT/'isolated.gba').write_bytes(image)
# Capture the real native executor frame from the unchanged fresh-ROM fixture.
halt=bytearray(base);halt[0xa2e70:0xa2e72]=b'\xfe\xe7';(OUT/'capture.gba').write_bytes(halt)
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'));e=h['Emulator'](OUT/'capture.gba')
try:
 e.load(SOURCE/'confirmation.state');e.run(8,256);e.run(400)
 e.save(OUT/'executor.state');ram=e.memory();iwram=C.string_at(*e.maps[0x03000000])
finally:e.close()
(OUT/'executor.ram').write_bytes(ram);(OUT/'executor.iwram').write_bytes(iwram)
registers=struct.unpack_from('<17I',(OUT/'executor.state').read_bytes(),0x20)
assert registers[15]==0x080a2e72,hex(registers[15])
native,expanded=ARM(control,iwram),ARM(bytes(image),iwram)
for m in (native,expanded):m.put(0x02000000,ram)
TARGET=0x020033e4;STATE=0x02028010;counts={}
def check(group,got,want):
 assert got==want,(group,got,want)
 counts[group]=counts.get(group,0)+1
# Independently identify all four fields with the untouched native getter.
# Its selector table maps19..22 to C8022/26/2A/2E, reading +18/+1A/+1C/+1E.
check('getter_dispatch',struct.unpack_from('<4I',base,0xc7ec0+19*4),(0x080c8022,0x080c8026,0x080c802a,0x080c802e))
native_stats=[]
for pointer in (UNIT,TARGET):
 values=[native.call(0x080c7ea4,pointer,selector) for selector in range(19,23)]
 check('captured_native_stats',tuple(values),struct.unpack_from('<4H',ram,pointer-0x02000000+0x18))
 native_stats.append({'unit':hex(pointer),'hp':values[0],'maximumHp':values[1],'mp':values[2],'maximumMp':values[3]})
for hp,maximum in ((13,27),(14,27),(50,100),(51,100)):
 for mp in (0,1,27,100,65535):
  expanded.put(TARGET+0x18,struct.pack('<4H',hp,maximum,mp,65535))
  native_hp=expanded.call(0x080c7ea4,TARGET,19);native_max=expanded.call(0x080c7ea4,TARGET,20)
  wounded=native_hp*2<=native_max
  check('hp_mp_independence',expanded.call(symbols['ffta_finisher_numerator'],430,TARGET),18 if wounded else 11)
  check('chance_hp_mp_independence',expanded.call(symbols['ffta_executioner_chance'],50,TARGET),70 if wounded else 50)
for maximum in (1,2,3,27,100,255,999,65535):
 for hp in sorted({1,maximum//2,max(1,maximum//2+1),maximum}):
  expanded.put(TARGET+0x18,struct.pack('<HHHH',hp,maximum,0,1))
  factor=18 if 2*hp<=maximum else 11
  for action in (0,112,424,425,426,429,430,431,65535):
   check('factor',expanded.call(symbols['ffta_finisher_numerator'],action,TARGET),18 if action==431 else factor if action==430 else 10)
  for chance in range(101):
   expected=min(95,chance+20) if chance and factor==18 else chance
   check('chance_boundaries',expanded.call(symbols['ffta_executioner_chance'],chance,TARGET),expected)
for active in range(256):
 for event in range(9):
  for immunity in (0,1):
   expanded.put(STATE-4,b'\xa5'*9);expanded.put(STATE,bytes([active]))
   result=expanded.call(symbols['ffta_exposed_transition'],STATE,event,immunity)
   wanted=active if event>6 or (event==0 and immunity) else active|1 if event==0 else active&0xfe
   check('exposed_transition',expanded.read(STATE,1),bytes([wanted]))
   check('exposed_result',result,0 if event==0 and immunity else 1)
   check('exposed_guards',expanded.read(STATE-4,4)+expanded.read(STATE+1,4),b'\xa5'*8)
 for damage in (-999,-1,0,1,999):
  for direct in (0,1):
   expanded.put(STATE,bytes([active]))
   check('exposed_factor',expanded.call(symbols['ffta_exposed_numerator'],STATE,damage&0xffffffff,direct),6 if active&1 and damage>0 and direct else 5)

# Installed native chance wrapper: all original IDs preserve returned values,
# evaluated units, and RNG. Test real descriptor selection, not a mocked getter.
for action in range(347):
 for residue in (0,4):
  results=[]
  for m in (native,expanded):
   m.put(0x02000000,ram);m.put(0x03000000,iwram)
   m.call(0x0812f2a4,action,454,0);m.put(0x0200f3f0,struct.pack('<II',UNIT,TARGET));m.call(0x0812f328,0)
   value=m.call(0x08131378,stack=STACK+residue)
   results.append((value,m.read(0x02000000,0x40000),m.read(0x030034b0,4)))
  check('original_native_chance',results[1],results[0])

status_results=[]
for affected in (UNIT,TARGET):
 for bit in range(44):
  values=[]
  for m in (native,expanded):
   m.put(0x02000000,ram);m.put(0x03000000,iwram)
   m.put(TARGET+0x18,struct.pack('<H',13));m.put(TARGET+0x1a,struct.pack('<H',27))
   address=affected+0xe8+bit//8;m.put(address,bytes([m.read(address,1)[0]|(1<<(bit%8))]))
   m.call(0x0812f2a4,430,454,0);m.put(0x0200f3f0,struct.pack('<II',UNIT,TARGET));m.call(0x0812f328,0)
   values.append(m.call(0x08131378))
  check('native_status_and_prevention',values[1],min(95,values[0]+20) if values[0] else 0)
  status_results.append({'unit':hex(affected),'bit':bit,'ordinary':values[0],'executioner':values[1]})
assert any(x['ordinary']==0 for x in status_results),'No preventing native result exercised'
assert any(x['ordinary']==100 for x in status_results),'No native forced100 result exercised'

# Restore the captured register frame and execute through actual hit/RNG,
# magnitude and HP application. The only new behavior installed is accuracy;
# actual coefficient integration and Exposed persistence are explicitly absent.
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12,UC_ARM_REG_SP,UC_ARM_REG_LR]
def executor(m,action,hp,seed,force_control_chance=None,flip_side=False):
 m.put(0x02000000,ram);m.put(0x03000000,iwram)
 m.put(registers[9]+0x10,struct.pack('<H',action));m.put(TARGET+0x18,struct.pack('<H',hp));m.put(TARGET+0x1a,struct.pack('<H',27));m.put(0x030034b0,struct.pack('<I',seed))
 if flip_side:
  side=struct.unpack('<H',m.read(UNIT+0x28,2))[0]^0x8000;m.put(UNIT+0x28,struct.pack('<H',side))
 m.u.reg_write(UC_ARM_REG_CPSR,registers[16])
 for reg,value in zip(REGS,registers):m.u.reg_write(reg,value)
 chances=[]
 def observe(u,pc,size,data):
  chance=u.reg_read(UC_ARM_REG_R0)
  if force_control_chance is not None:u.reg_write(UC_ARM_REG_R0,force_control_chance);chance=force_control_chance
  chances.append(chance)
 handle=m.u.hook_add(UC_HOOK_CODE,observe,begin=0x0812f1dc,end=0x0812f1dc)
 try:m.u.emu_start(0x080a2e71,0x080a3762,count=2000000)
 finally:m.u.hook_del(handle)
 check('executor_return',m.u.reg_read(UC_ARM_REG_PC),0x080a3762)
 check('executor_guard',m.read(0x0203ff44,0xbc),ram[0x3ff44:])
 return chances,m.read(0x02000000,0x40000),m.read(0x030034b0,4)
samples=[]
for hp in (13,14,27):
 for seed in (0,1,2,3,99,65535):
  old=executor(native,430,hp,seed);new=executor(expanded,430,hp,seed)
  expected=[min(95,x+20) if x and hp<=13 else x for x in old[0]]
  check('committed_final_chance',new[0],expected)
  assert len(expected)==1
  # Native executor with only its roll input replaced is an independent
  # equivalence oracle for the installed hooks' side effects and RNG use.
  oracle=executor(native,430,hp,seed,expected[0]);check('executor_equivalence',new,oracle)
  samples.append({'hp':hp,'seed':seed,'ordinary':old[0],'executioner':new[0]})
for seed in (0,1,99):check('original_executor',executor(expanded,425,27,seed),executor(native,425,27,seed))
for hp in (13,14):
 for seed in (0,1,99):
  old=executor(native,430,hp,seed,flip_side=True);new=executor(expanded,430,hp,seed,flip_side=True)
  expected=[min(95,x+20) if x and hp<=13 else x for x in old[0]]
  check('late_native_bonus',new[0],expected)
  if not expected:
   check('production-hostility-prevents-roll',new,old)
   continue
  oracle=executor(native,430,hp,seed,expected[0],flip_side=True);check('late_bonus_executor_equivalence',new,oracle)
  samples.append({'hp':hp,'seed':seed,'flippedSide':True,'ordinary':old[0],'executioner':new[0]})
assert {p.name:sha(p.read_bytes()) for p in SOURCE.iterdir() if p.is_file()}==original,'Original evidence changed'
report={'passed':True,'isolated':not CURRENT,'baseSha1':meta['romSha1'] if CURRENT else SHA,'binarySha1':sha(binary),'checks':sum(counts.values()),'groups':counts,'executorSamples':samples,'nativeStatusCases':status_results,'capturedNativeStats':native_stats,
 'scope':('Installed Executioner factors/chance/native executor regression; Exposed helper tests do not certify persistence or lifecycle integration.' if CURRENT else 'Isolated factors/chance/native executor accuracy and caller-owned Exposed helpers; no production action or Exposed ownership integration.')}
(OUT/('current-report.json' if CURRENT else 'report.json')).write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ('nativeStatusCases','executorSamples')},indent=2))
