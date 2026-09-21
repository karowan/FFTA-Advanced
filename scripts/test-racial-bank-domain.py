"""Native24-race bank/name regression against a current built stage.

No historical battle state, emulator, save file, or UI fixture is required.
The ROM, manifest, engine and symbols are frozen before native execution.
"""
import argparse,hashlib,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',default='combat');args=p.parse_args()
OUT=ROOT/'build/expansion/probes';ROM=0x08000000
sha=lambda b:hashlib.sha1(b).hexdigest()
word=lambda b,p:struct.unpack_from('<I',b,p)[0]
meta=json.loads((OUT/(args.stage+'.json')).read_text())
image=(OUT/(args.stage+'.gba')).read_bytes();clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
engine=(ROOT/'build/expansion/engine.bin').read_bytes();symbols=(ROOT/'build/expansion/engine.symbols').read_bytes()
assert sha(image)==meta['romSha1'],'ROM/manifest mismatch'
assert sha(engine)==meta['engineSha1'] and image[0x1100000:0x1100000+len(engine)]==engine,'Engine snapshot mismatch'
assert sha(clean)=='4ac05441f4de70a4ec3dd932116346c61b8783d9','Wrong native baseline'
FROZEN=OUT/'racial-bank-domain'/sha(image);FROZEN.mkdir(parents=True,exist_ok=True)
for name,data in [('frozen.gba',image),('engine.bin',engine),('engine.symbols',symbols)]:
 (FROZEN/name).write_bytes(data)
(FROZEN/'manifest.json').write_text(json.dumps(meta,indent=2))
old=0x51ba84;new=word(image,0xcd538)-ROM
assert word(clean,old)==ROM+old+24*4,'Native table boundary changed'
assert 0x1000000<=new and new+96<=0x1100000,'Relocated table allocation bounds'
refs=[i for i in range(0,len(clean),4) if word(clean,i)==ROM+old]
assert len(refs)==22 and 0x2c088 in refs and 0xcd538 in refs
assert all(word(image,i)==ROM+new for i in refs),'A native bank consumer was not repointed'

class Machine:
 def __init__(self,rom):
  self.u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for address,size in [(0x02000000,0x40000),(0x03000000,0x8000),(ROM,0x2000000)]:self.u.mem_map(address,size)
  self.u.mem_write(ROM,rom)
 def get(self,address,n):return bytes(self.u.mem_read(address,n))
 def put(self,address,data):self.u.mem_write(address,bytes(data))
 def name(self,race,index):
  unit=0x02000080;obj=0x02008000
  self.put(unit,bytes(264));self.put(unit+6,bytes([race]));self.put(unit+0x3a,bytes([index]))
  self.put(obj+0xc,struct.pack('<I',unit))
  for reg,value in [(UC_ARM_REG_R5,obj),(UC_ARM_REG_SP,0x03007000)]:self.u.reg_write(reg,value)
  # Full native name-resolution fragment, including native C7EA4(unit,3).
  self.u.emu_start(0x0802c05f,0x0802c09a,count=2000)
  assert self.u.reg_read(UC_ARM_REG_PC)==0x0802c09a
  return self.u.reg_read(UC_ARM_REG_R2)
 def record(self,race,index):
  regs=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,
        UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for i,reg in enumerate(regs):self.u.reg_write(reg,0x55000000+i)
  for reg,value in [(UC_ARM_REG_R0,race),(UC_ARM_REG_R1,index),(UC_ARM_REG_SP,0x03007000),(UC_ARM_REG_LR,0x08000101)]:self.u.reg_write(reg,value)
  self.u.emu_start(0x080cd481,0x08000100,count=2000)
  assert self.u.reg_read(UC_ARM_REG_PC)==0x08000100 and self.u.reg_read(UC_ARM_REG_SP)==0x03007000
  assert all(self.u.reg_read(reg)==0x55000000+i for i,reg in enumerate(regs)),'CD480 ABI'
  return self.u.reg_read(UC_ARM_REG_R0)

baseline=Machine(clean);expanded=Machine(image);cases=0
others=word(image,0x2c08c)
for race in range(24):
 bank=word(image,new+race*4);native_bank=word(clean,old+race*4)
 if race==0 or race>=6:assert bank==native_bank,('Native bank lost',race)
 for index in range(8):
  native_name=baseline.name(race,index);actual_name=expanded.name(race,index)
  record=expanded.record(race,index);assert record==bank+index*8
  nameid=struct.unpack('<H',expanded.get(record,2))[0]
  expected=struct.unpack('<I',expanded.get(others+nameid*4,4))[0]
  assert actual_name==expected and ROM<=actual_name<0x0a000000,('Invalid native name',race,index,hex(actual_name))
  if race==0 or race>=6:
   assert expanded.get(record,8)==baseline.get(baseline.record(race,index),8),('Native record changed',race,index)
   assert actual_name==native_name,('Native name changed',race,index)
  cases+=1
# Keep the exact previously failing monster case explicit in the live test.
assert expanded.record(18,0)==0x0851cea4
assert expanded.name(18,0)==baseline.name(18,0)==0x085541b4
report={'passed':True,'stage':args.stage,'romSha1':sha(image),'engineSha1':sha(engine),
 'symbolsSha1':sha(symbols),'nativeBanks':24,'nativeLiteralReferences':len(refs),'nativeNameAndGetterCases':cases,
 'scope':'Eight actual native record/name resolutions per race; exact untouched bank/name preservation for0 and6..23; race18/name0 explicit regression'}
(FROZEN/'report.json').write_text(json.dumps(report,indent=2))
(OUT/'racial-bank-domain/report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
