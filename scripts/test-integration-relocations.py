"""Verify linked integration instruction bytes survive table relocation intact."""
import pathlib,json,hashlib,subprocess
from arm_literal_relocations import ELFData
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
rom=pathlib.Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
work=pathlib.Path(meta['path']).parent.parent;elf=work/'integrated.elf'
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');data=ELFData(elf,prefix)
# Preserve the exact regression even when later compiler allocation no longer
# emits the coincidental pointer-shaped instruction pair in production code.
fixture=pathlib.Path(meta['path']).parent/'relocation-collision';fixture.mkdir(exist_ok=True)
(fixture/'collision.s').write_text('''.syntax unified
.cpu arm7tdmi
.thumb
.text
.global collision
.type collision,%function
.thumb_func
collision:
 ldr r1,[sp,#16]
 lsrs r2,r4,#4
 bx lr
.size collision,.-collision
.align 2
.type literal,%object
literal:
 .word 0x09229904
.size literal,.-literal
''')
obj=fixture/'collision.o';binary=fixture/'collision.bin'
subprocess.run([prefix+'as.exe',str(fixture/'collision.s'),'-o',str(obj)],check=True)
subprocess.run([prefix+'objcopy.exe','-O','binary','-j','.text',str(obj),str(binary)],check=True)
classification=ELFData(obj,prefix);sample=binary.read_bytes()
assert sample[:4]==sample[8:12]==bytes.fromhex('04992209')
assert not classification.contains_word(0),'Instruction collision classified as data'
assert classification.contains_word(8),'Real identical literal rejected'
checks=2;relocations=[]
for label,filename in (('integration','integrated.bin'),('geomancerAI','geomancer-ai.bin'),('mysticKnight','mystic-knight.bin')):
 start,end=meta['regions'][label];linked=(work/filename).read_bytes();assert end-start==len(linked)
 for offset in range(0,len(linked),4):
  before=linked[offset:offset+4];after=rom[start+offset:start+offset+4]
  checks+=1
  if before==after:continue
  assert len(before)==4 and data.contains_word(0x08000000+start+offset),('instructions modified',label,hex(offset),before.hex(),after.hex())
  relocations.append(dict(offset=start+offset,before=before.hex(),after=after.hex()))
collisions=[c for c in meta['changes'] if c['kind']=='preserved instruction collision']
for c in collisions:
 start=c['offset'];assert int.from_bytes(rom[start:start+4],'little')==c['value']
 checks+=1
report=dict(passed=True,romSha1=meta['romSha1'],checkedWords=checks,relocations=relocations,preservedInstructionCollisions=collisions)
(pathlib.Path(meta['path']).parent/'integration-relocations.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
