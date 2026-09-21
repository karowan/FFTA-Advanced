"""Exact current-key confirmation against the original scalar function.

No game fixture or palette-history lifetime assumptions; compiled ARMv4T calls
cover every byte value, each mismatch lane, requests, alignment and fences.
"""
import ast,datetime,json,random,struct,subprocess,sys
from pathlib import Path
from native_art import ROOT,sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007800
source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace(
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
exec(compile(ast.Module(body=[n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
out=ROOT/'build/art/fast-confirm'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[]
def check(ok,label):assert ok,label;checks.append(label)
try:
 prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
 common=[prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wall','-Wextra','-Werror','-DFFTA_ART_HISTORY_SLOTS=20']
 source='src/engine/art-palette-provisional.c';old=out/'reference.o';elf=out/'confirm.elf';binary=out/'confirm.bin'
 commands=[common+['-Dffta_art_provisional_confirm=reference_confirm','-Dffta_art_provisional_reconcile=reference_reconcile','-c',source,'-o',str(old)],
  common+['-DFFTA_ART_FAST_CONFIRM=1','-Wl,-Ttext=0x09f90000','-Wl,-e,ffta_art_provisional_confirm',source,str(old),'-o',str(elf)]]
 for i,command in enumerate(commands):
  result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);(out/f'compile-{i}.log').write_text(result.stdout+result.stderr);result.check_returncode()
 subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True,capture_output=True)
 symbols={v[2]:int(v[0],16) for line in subprocess.check_output([prefix+'nm.exe',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 code=binary.read_bytes();rom=bytearray(b'\xff'*0x2000000);rom[0x1f90000:0x1f90000+len(code)]=code;a=ARM(rom,bytes(0x8000))
 cases=[];allbits=(1<<20)-1
 for key in range(256):
  for mask in (0,allbits):cases.append((bytes([key])*20,bytes([key])*20,mask))
 for slot in range(20):
  for key in (0,127,159,160,254,255):
   keys=bytes([key])*20;confirmed=bytearray(keys);confirmed[slot]^=1
   for mask in (0,1<<slot,0xffffffff):cases.append((keys,bytes(confirmed),mask))
 rng=random.Random(0x46544641)
 for _ in range(64):cases.append((rng.randbytes(20),rng.randbytes(20),rng.getrandbits(32)))
 for index,(keys,confirmed,mask) in enumerate(cases):
  for vk,ck in ((0,0),(1,0),(0,1),(3,2)):
   for stack in (STACK,STACK+4):
    v=0x02010010+vk;c=0x02010060+ck;initial=bytearray(b'\xa5'*256)
    initial[v-0x02010000:v-0x02010000+20]=keys;initial[c-0x02010000:c-0x02010000+20]=confirmed
    a.put(0x02010000,initial);a.call(symbols['reference_confirm'],v,c,mask,stack=stack);expected=a.read(0x02010000,256)
    a.put(0x02010000,initial);a.call(symbols['ffta_art_provisional_confirm'],v,c,mask,stack=stack)
    check(a.read(0x02010000,256)==expected,'Exact scalar result and input/scale/output fences '+str((index,vk,ck,stack)))
 report=dict(status='passed',checks=checks,cases=len(cases),compiledSha256=sha(code),sources={source:sha((ROOT/source).read_bytes())},commands=commands,
  scope='Compiled current-key equality path and original scalar fallback, all256 equal key values, every mismatch lane with boundary values and masks, deterministic mixed values, aligned/unaligned pointers and both stack residues. Complete256-byte comparison includes input/scale/output fences. No game lifetime, performance or full engineering acceptance.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n');raise
