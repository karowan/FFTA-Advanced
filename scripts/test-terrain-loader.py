"""Run every clean USA map through its unmodified native component loaders.

The private boot harness only supplies map IDs and captures the loader outputs.
It uses mGBA's BIOS implementation and the original game's decompression and
layout functions; no Python decoder substitutes for those functions.
"""
import hashlib,json,pathlib,runpy,struct,subprocess
from ffta_maps import Maps,COUNT,CLEAN_SHA1
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'build/expansion/terrain'/CLEAN_SHA1/'native-loader';OUT.mkdir(parents=True,exist_ok=True)
rom=bytearray((ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes());maps=Maps(bytes(rom))
prefix=ROOT/'tools/arm-gnu/bin/arm-none-eabi-'
def tool(name,*args):subprocess.run([str(prefix)+name+'.exe',*map(str,args)],cwd=ROOT,check=True)
tool('as','-mcpu=arm7tdmi',ROOT/'scripts/terrain-native-probe.s','-o',OUT/'probe.o')
tool('ld','-Ttext=0x09000000','-e','_start',OUT/'probe.o','-o',OUT/'probe.elf')
tool('objcopy','-O','binary',OUT/'probe.elf',OUT/'probe.bin')
code=(OUT/'probe.bin').read_bytes();rom.extend(b'\xff'*(0x1000000+len(code)-len(rom)))
rom[0x1000000:]=code;struct.pack_into('<I',rom,0,0xea000000|((0x1000000-8)//4))
private=OUT/'native-loader.gba';private.write_bytes(rom)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];e=E(private)
results=[];failures=[]
try:
 e.run(2);assert struct.unpack_from('<I',e.memory(),0x3ffe4)[0]==1,'Harness did not boot'
 for index in range(COUNT):
  e.set_memory(0x3ffe0,struct.pack('<I',index+1))
  for frame in range(30):
   e.run(1);ram=e.memory()
   if struct.unpack_from('<I',ram,0x3ffe0)[0]==0:break
  assert struct.unpack_from('<II',ram,0x3ffe0)==(0,index+2),('Native loader did not complete',index)
  arrangement=ram[0x91a0:0xd1a0];height=ram[0x7cb0:0x7eb0];clipping=ram[0xd1a0:0xf1a0]
  for name,data in [('arrangement',arrangement),('height',height),('clipping',clipping)]:
   (OUT/f'map-{index:03}-{name}.bin').write_bytes(data)
  expected=maps.planar(index)
  diff=[j for j,(a,b) in enumerate(zip(expected,arrangement)) if a!=b]
  hdiff=[j for j,(a,b) in enumerate(zip(maps.heights(index),height)) if a!=b]
  cdiff=[j for j,(a,b) in enumerate(zip(maps.clipping(index),clipping)) if a!=b]
  entry=dict(map=index,frames=frame+1,arrangementSha1=hashlib.sha1(arrangement).hexdigest(),heightSha1=hashlib.sha1(height).hexdigest(),clippingSha1=hashlib.sha1(clipping).hexdigest(),arrangementMismatchBytes=len(diff),heightMismatchBytes=len(hdiff),clippingMismatchBytes=len(cdiff),firstArrangementMismatches=diff[:12],firstHeightMismatches=hdiff[:12],firstClippingMismatches=cdiff[:12])
  results.append(entry)
  if diff or hdiff or cdiff:failures.append(entry)
finally:e.close()
report=dict(passed=not failures,cleanRomSha1=CLEAN_SHA1,probeRomSha1=hashlib.sha1(rom).hexdigest(),maps=results,failures=failures)
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(passed=report['passed'],maps=len(results),failures=failures),indent=2))
assert not failures,('Native loader differences',len(failures))
