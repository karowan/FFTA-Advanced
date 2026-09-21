"""Run original UI decoders against private buffers; no player save or game UI."""
import ast,hashlib,json,struct,sys
from pathlib import Path
from PIL import Image
from native_art import ROOT,palette,tile_image,pack_tiles,sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
assert hashlib.sha1(rom).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
candidate=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
iwram_path=Path(candidate['path']).parent/'fixture/battle-ready.iwram'
iwram=iwram_path.read_bytes()
machine=ARM(rom,iwram)
out=ROOT/'build/art/native-reference/ui';out.mkdir(parents=True,exist_ok=True)
records=[];checks=[]
try:
 for job in range(2,46):
  machine.put(0x02030000,bytes([0xd7])*512)
  machine.call(0x080cb9e0,0x02030000,job)
  raw=machine.read(0x02030000,256)
  assert machine.read(0x02030100,256)==bytes([0xd7])*256
  assert raw!=bytes([0xd7])*256
  bank=machine.call(0x080cba14,job)
  # The icon record stores destination OBJ bank13..15; the source palette
  # routine takes a zero-based source bank, as in the native caller.
  assert 13<=bank<=15
  pointer=machine.call(0x080cba3c,bank-13)
  mode=machine.read(0x02002fc2,1)[0]&3
  palette_base={0:0x419d60,1:0x41b340,2:0x41a860,3:0x419d60}[mode]
  assert pointer==0x08000000+palette_base+32*(bank-13)
  pal,rgb=palette(rom,pointer-0x08000000)
  image=tile_image(raw,rgb,32);path=out/f'job-{job:03}.png';image.save(path,bits=4)
  with Image.open(path) as saved:assert pack_tiles(saved,8)==raw
  records.append(dict(job=job,paletteIndex=bank,paletteOffset=pointer-0x08000000,
                      paletteHex=pal.hex(),tilesHex=raw.hex(),sha256=sha(raw)))
  checks.append(f'job-{job:03}: native decode, canary, indexed PNG import')
 report=dict(romSha1=hashlib.sha1(rom).hexdigest(),iwramSha256=sha(iwram),records=records,checks=checks)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(passCount=len(checks),output=str(out))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(error=str(error),checks=checks),indent=2)+'\n')
 raise
