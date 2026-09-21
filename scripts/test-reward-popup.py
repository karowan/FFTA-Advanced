"""Preserve the native mixed reward namespace and actual popup rendering branches.

These native routine tests do not invoke a mission-completion event or a user
save. New equipment is shops-only, so encoded reward IDs376..502 stay quest IDs.
"""
import ast,ctypes as C,hashlib,importlib.util,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
OUT=ROOT/'build/expansion/probes';clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
meta=json.loads((OUT/'combat.json').read_text());image=(OUT/'combat.gba').read_bytes()
engine=(ROOT/'build/expansion/engine.bin').read_bytes();sha=lambda b:hashlib.sha1(b).hexdigest()
word=lambda b,p:struct.unpack_from('<I',b,p)[0]
assert sha(image)==meta['romSha1'] and sha(engine)==meta['engineSha1']
assert image[0x1100000:0x1100000+len(engine)]==engine
FROZEN=OUT/'reward-popup'/sha(image);FROZEN.mkdir(parents=True,exist_ok=True)
(FROZEN/'frozen.gba').write_bytes(image);(FROZEN/'manifest.json').write_text(json.dumps(meta,indent=2))
# All127 quest records, including every numerical collision with new gear.
assert 0x51faa4+375*16==0x521214 and 0x521214+128*16==0x521a14
for local in range(1,128):assert struct.unpack_from('<H',clean,0x521214+local*16)[0]==375+local
assert image[0x521214:0x521a14]==clean[0x521214:0x521a14]
assert image[0x391bbc:0x391ca2]==clean[0x391bbc:0x391ca2],'Reward lookup content changed'
d=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
callers=[]
for p in range(0,0x150000,2):
 if clean[p+1]<0xf0:continue
 decoded=list(d.disasm(clean[p:p+4],0x08000000+p))
 if decoded and decoded[0].mnemonic=='bl' and decoded[0].op_str=='#0x8039df4':callers.append(p)
assert callers==[0x3a500]
assert all(word(clean,p) not in (0x08039df4,0x08039df5) for p in range(0,len(clean),4))
assert all(word(image,p)!=0x08039df5 for p in range(0,len(image),4)),'New direct popup caller needs namespace review'
# Read only the reusable harness definitions; no other test's main runs.
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')],type_ignores=[]),'<native-harness>','exec'))
iwram=iwram_from_boot();native=ARM(clean,iwram);expanded=ARM(image,iwram)
def bios_copy(u,pc,size,data):
 # Model only BIOS CpuSet; all popup/decoder instructions stay native.
 source=u.reg_read(UC_ARM_REG_R0);target=u.reg_read(UC_ARM_REG_R1);control=u.reg_read(UC_ARM_REG_R2)
 width=4 if control&0x04000000 else 2;count=control&0x1fffff
 block=bytes(u.mem_read(source,width if control&0x01000000 else count*width))
 u.mem_write(target,block*count if control&0x01000000 else block)
 u.reg_write(UC_ARM_REG_PC,(pc+2)|1)
for m in (native,expanded):
 m.u.mem_map(0x06000000,0x20000)
 m.u.hook_add(UC_HOOK_CODE,bios_copy,begin=0x0814186c,end=0x0814186c)

def popup(m,ident):
 # Start at the native namespace decision after the common prefix is drawn.
 # Execute the real icon decoder, palette getter, copy, and name lookup.
 m.put(0x02003c70,b'\xa5'*0x240);m.put(0x0600afa0,b'\xb6'*0x340)
 m.put(0x02001940,b'\xd7'*0x5dc);m.put(0x02002b08,b'\xe1'*0x100)
 for reg,value in [(UC_ARM_REG_R10,ident),(UC_ARM_REG_R9,0x02003cb0),(UC_ARM_REG_R7,5),(UC_ARM_REG_SP,0x03007000)]:m.u.reg_write(reg,value)
 try:m.u.emu_start(0x08039eef,0x08039fc0,count=100000)
 except Exception as error:raise AssertionError((ident,hex(m.u.reg_read(UC_ARM_REG_PC)),[hex(m.u.reg_read(r)) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)],str(error))) from error
 assert m.u.reg_read(UC_ARM_REG_PC)==0x08039fc0 and m.u.reg_read(UC_ARM_REG_SP)==0x03007000
 assert m.u.reg_read(UC_ARM_REG_R10)==ident and m.u.reg_read(UC_ARM_REG_R9)==0x02003cb0 and m.u.reg_read(UC_ARM_REG_R7)==5
 assert m.read(0x02003c70,64)==b'\xa5'*64 and m.read(0x02003d30,256)==b'\xa5'*256
 assert m.read(0x02001940,0x5dc)==b'\xd7'*0x5dc and m.read(0x02002b08,0x100)==b'\xe1'*0x100
 name=m.u.reg_read(UC_ARM_REG_R6);palette=m.u.reg_read(UC_ARM_REG_R8)
 assert 0x08000000<=name<0x0a000000
 return {'text':name,'palette':palette,'icon':m.read(0x02003cb0,128).hex(),'vram':m.read(0x0600afe0+5*64,128).hex()}

cases=[]
for ident in range(1,503):
 old=popup(native,ident);new=popup(expanded,ident)
 assert old==new,('Native reward popup changed',ident)
 if ident>375:
  assert new['text']==word(clean,0x526680+(ident+123)*4),('Quest name namespace',ident)
 cases.append(ident)
# Exercise each source-table decoder rather than merely reproducing its math.
source_cases=[]
for start,stop,base,count in [(0x3a3ca,0x3a406,0x391bbc,5),(0x3a33e,0x3a37e,0x391bd0,6),
                             (0x3a2a2,0x3a2e2,0x391be8,8),(0x3a456,0x3a48a,0x391c08,28)]:
 for code in range(1,count+1):
  expected=struct.unpack_from('<H',clean,base+(code-1)*4+2)[0]
  for m in (native,expanded):
   m.put(0x0201f474,bytes(4));m.u.reg_write(UC_ARM_REG_R5,code)
   m.u.reg_write(UC_ARM_REG_R7,0x0201f474);m.u.reg_write(UC_ARM_REG_R4,0x0201f46c)
   m.u.emu_start(0x08000001+start,0x08000000+stop,count=1000)
   assert m.u.reg_read(UC_ARM_REG_PC)==0x08000000+stop
   assert struct.unpack('<H',m.read(0x0201f46c,2))[0]==expected
  source_cases.append(expected)
for code in range(0x81,0x96):
 expected=struct.unpack_from('<H',clean,0x391c78+(code-0x81)*2)[0]
 for m in (native,expanded):
  m.put(0x0201f474,bytes(4));m.u.reg_write(UC_ARM_REG_R5,code)
  m.u.emu_start(0x0803a3ed,0x0803a406,count=1000)
  assert m.u.reg_read(UC_ARM_REG_PC)==0x0803a406
  assert struct.unpack('<H',m.read(0x0201f46c,2))[0]==expected
 source_cases.append(expected)
assert 421 in source_cases and 422 in source_cases,'Original overlapping quest rewards lost'
report={'passed':True,'romSha1':sha(image),'engineSha1':sha(engine),'nativePopupCases':len(cases),
 'questIds':'376..502 (all127 native quest records)','sourceDecoderCases':len(source_cases),
 'popupCaller':hex(callers[0]),'overlappingNativeRewards':[421,422],
 'productionChange':'None: the only native caller has a mixed reward namespace; expanded gear is shops-only',
 'scope':'Actual native popup decision, name pointer, icon decoding, palette and VRAM copy; all native reward source-table decoders. No mission completion or full popup-window event replay.'}
(FROZEN/'report.json').write_text(json.dumps(report,indent=2));(OUT/'reward-popup/report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
