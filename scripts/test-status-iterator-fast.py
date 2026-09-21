"""Exact status-selector shortcut equivalence and native inline ABI.

Exhaust every cursor byte and every possible highest custom key with controlled
read-only getter contracts, then compare real native getters on retained units.
No gameplay fixture or player save is created.
"""
import ast, collections, datetime, hashlib, itertools, json, struct, subprocess, sys
from pathlib import Path
from native_art import ROOT, sha
sys.path.insert(0, str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007800
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=500000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
meta=json.loads((ROOT/'build/art/live-palette/21052ed615a6463251cba9b98952b4cc07ba4546/manifest.json').read_text())
rom=bytearray(Path(meta['source']).read_bytes());assert hashlib.sha1(rom).hexdigest()==meta['baseRomSha1']
release=json.loads((Path(meta['releaseSource']).parent/'manifest.json').read_text());native=release['symbols']
retained=ROOT/'build/art/live-palette/battle/20260918T070700.550270Z'
iw=(retained/'candidate-ready.iwram').read_bytes();ram=(retained/'candidate-ready.ram').read_bytes()
assert sha(iw)=='5750a1677a3832488b04855f8776e4c3702a62495976c4fe89be159d19e76581'
out=ROOT/'build/art/status-iterator'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
text=(ROOT/'src/engine/integrated-jobs.c').read_text();start=text.index('unsigned ffta_integrated_status_next_key(');end=text.index('\nunsigned ffta_integrated_status_visual',start)
function=text[start:end].replace('ffta_integrated_status_next_key','ffta_test_status_next_key')
deps=['ffta_myk_sequence','ffta_myk_enchantment','ffta_integrated_status_icon','ffta_wound_status_next_key']
c=out/'shortcut.c';c.write_text('#include <stdint.h>\n'+''.join('extern unsigned '+n+'(const uint8_t *,unsigned);\n' if n in deps[2:] else 'extern unsigned '+n+'(const uint8_t *);\n' for n in deps)+function+'\n')
bindings=out/'bindings.s';bindings.write_text('.syntax unified\n.thumb\n'+''.join('.global '+n+'\n.thumb_set '+n+','+hex(native[n]|1)+'\n' for n in deps)+'.global ffta_art_original_status_next_entry\n.thumb_set ffta_art_original_status_next_entry,'+hex(native['ffta_integrated_status_next_entry']|1)+'\n')
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=out/'shortcut.elf';binary=out/'shortcut.bin'
p=subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-nostdlib','-Wall','-Wextra','-Werror','-Wl,-Ttext=0x09f90000','-Wl,-e,ffta_test_status_next_key',str(c),str(bindings),'src/engine/status-iterator-fast.s','-o',str(elf)],cwd=ROOT,capture_output=True,text=True)
(out/'compile.log').write_text(p.stdout+p.stderr);p.check_returncode()
subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True,capture_output=True)
symbols={v[2]:int(v[0],16) for line in subprocess.check_output([prefix+'nm.exe',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
code=binary.read_bytes();assert len(code)<0x10000 and rom[0x1f90000:0x1f90000+len(code)]==b'\xff'*len(code)
rom[0x1f90000:0x1f90000+len(code)]=code
original,fast=ARM(rom,iw),ARM(rom,iw)
assert rom[0x9dd62:0x9dd68].hex()=='012020560028'
fast.put(0x0809dd58,struct.pack('<I',symbols['ffta_art_status_next_entry']|1))
checks=collections.Counter();case=None;limit=24;reads=collections.Counter()
def check(group,actual,expected):
 checks[group]+=1;assert actual==expected,(case,group,actual,expected)
def getter(u,pc,size,data):
 name=data;reads[name]+=1
 if name==deps[0]:value=2 if limit==55 else 1 if limit==54 else 0
 elif name==deps[1]:value=limit-42 if 43<=limit<=53 else 0
 elif name==deps[2]:value=limit if u.reg_read(UC_ARM_REG_R1)==limit else 0
 else:
  value=(u.reg_read(UC_ARM_REG_R1)+1)&255
  if min(limit,27)<value<128:value=1
 u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
handles=[]
for machine in (original,fast):
 machine.put(0x02000000,ram)
 for name in deps:handles.append((machine,machine.u.hook_add(UC_HOOK_CODE,getter,user_data=name,begin=native[name]&~1,end=native[name]&~1)))
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12,UC_ARM_REG_LR,UC_ARM_REG_SP]
ROW=0x02025000
def inline(machine,previous,residue):
 machine.put(ROW,bytes([0xa7,0xb9,previous,0xc1])+b'\xd5'*8)
 machine.u.reg_write(UC_ARM_REG_CPSR,0x30)
 for i,reg in enumerate(REGS):machine.u.reg_write(reg,0x55000000+i)
 for reg,value in [(UC_ARM_REG_R4,ROW),(UC_ARM_REG_R6,UNIT),(UC_ARM_REG_SP,STACK+residue),(UC_ARM_REG_LR,RETURN|1)]:machine.u.reg_write(reg,value)
 # MOVS/ LDRSB / CMP unconditionally replace flags before their first
 # native consumer. Compare after that authenticated continuation.
 machine.u.emu_start(0x0809dd53,0x0809dd68,count=500000)
 check('inline reaches native continuation',machine.u.reg_read(UC_ARM_REG_PC),0x0809dd68)
 return ([machine.u.reg_read(r) for r in REGS],machine.u.reg_read(UC_ARM_REG_CPSR)&0xf0000000,machine.read(ROW,12))
try:
 for limit,previous in itertools.product(range(24,56),range(256)):
  case=('contract',limit,previous);expected=(previous+1)&255
  if limit<expected<128:expected=1
  for machine,address in [(original,native['ffta_integrated_status_next_key']),(fast,symbols['ffta_test_status_next_key'])]:
   check('compiled C exact cursor',machine.call(address,UNIT,previous),expected)
  for residue in (0,4):
   before=original.read(0x02000000,0x40000);old=inline(original,previous,residue);reads.clear();new=inline(fast,previous,residue)
   check('inline registers flags stack and cursor exact',new,old)
   following=(previous+1)&255
   check('fast path skips all status reads',sum(reads.values())==0,following<=24 or following>=128)
   check('only cursor byte written',fast.read(0x02000000,ROW-0x02000000)+fast.read(ROW+12,0x02040000-ROW-12),before[:ROW-0x02000000]+before[ROW-0x02000000+12:])
 for machine,handle in handles:machine.u.hook_del(handle)
 # Real getter code, original retained state, native/exposed/centered/wound
 # combinations, KO and petrify, two canonical units; every cursor byte.
 for unit,packed,wound,condition in itertools.product((UNIT,UNIT+264),(0,5),(0,0x400b),('alive','KO','petrify')):
  case=('native',unit,packed,wound,condition)
  for machine in (original,fast):
   machine.put(0x02000000,ram);machine.put(0x02001e98+(unit-UNIT)//264,bytes([packed]));machine.put(0x02001ebc+2*((unit-UNIT)//264),struct.pack('<H',wound))
   if condition=='KO':machine.put(unit+0x18,bytes(2))
   elif condition=='petrify':machine.put(unit+0xe8,bytes([machine.read(unit+0xe8,1)[0]|64]))
  before=fast.read(0x02000000,0x40000)
  for previous in range(256):
   check('actual native getters exact',fast.call(symbols['ffta_test_status_next_key'],unit,previous),original.call(native['ffta_integrated_status_next_key'],unit,previous))
  check('actual native getters read only',fast.read(0x02000000,0x40000),before)
 report=dict(status='passed',checks=dict(checks),total=sum(checks.values()),romSha1=meta['baseRomSha1'],compiledSha256=sha(code),ramSha256=sha(ram),iwramSha256=sha(iw),sources={f:sha((ROOT/f).read_bytes()) for f in ['src/engine/integrated-jobs.c','src/engine/status-iterator-fast.s']},scope='All cursor bytes and highest keys24..55 with read-only controlled getter contracts, both inline stack alignments and actual old native entry, real getter comparisons on retained canonical units with exposed/centered/wound/KO/petrify. Does not establish live timing, all custom-state lifetimes or final artwork.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=report['total'],report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),case=case,checks=dict(checks)),indent=2)+'\n');print(out);raise
