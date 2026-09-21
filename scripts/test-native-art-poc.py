"""Native icon dispatch/canaries and actual cold-loaded equipment teaching UI."""
import ast,ctypes as C,hashlib,json,runpy,struct,sys
from datetime import datetime,timezone
from pathlib import Path
from native_art import ROOT,sha,tile_image
from PIL import Image
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
portraits='--portraits' in sys.argv
build=ROOT/('build/art/equipment-preview' if portraits else 'build/art/poc')
from art_candidate import candidate
meta=candidate(str((build/('current.json' if portraits else 'manifest.json')).relative_to(ROOT)),'preview')
assets=Path(meta.get('assetDirectory',str(build)))
out=build/'attempts'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True,exist_ok=False)
data=Path(meta['path']).read_bytes();base=Path(meta['source']).read_bytes()
assert hashlib.sha1(data).hexdigest()==meta['romSha1']
iwram=(Path(meta['source']).parent/'fixture/battle-ready.iwram').read_bytes()
original,changed=ARM(base,iwram),ARM(data,iwram)
raw=b'' if portraits else (build/'samurai-icon.bin').read_bytes();checks=[];inputs=[]
def check(ok,name):
 assert ok,name
 checks.append(name)
e=None
try:
 for job in range(2,126):
  outputs=[]
  for machine in (original,changed):
   machine.put(0x02030000,bytes([0xd7])*512)
   machine.call(0x080cb9e0,0x02030000,job)
   check(machine.read(0x02030100,256)==bytes([0xd7])*256,f'job{job} decoder tail canary {len(outputs)}')
   outputs.append(machine.read(0x02030000,256))
  if portraits and 116<=job<=125:
   actual=tile_image(outputs[1],[0]*48,32)
   with Image.open(assets/f'portrait-{job}.png') as authored:
    check(all(actual.getpixel((x,y))==authored.getpixel((x,y)) for x in range(16) for y in range(16)),f'job{job} exact authored character pixels')
   check(outputs[1]!=outputs[0],f'job{job} donor portrait replaced')
   if job==116:raw=outputs[1]
  else:check(outputs[1]==(raw if job==116 else outputs[0]),f'job{job} new-only icon dispatch')
  check(original.call(0x080cba14,job)==changed.call(0x080cba14,job),f'job{job} palette preservation')
 # Immutable generated showcase seed, never the live player's save.
 seedpath=ROOT/'build/showcase/20260917T160011.215713Z/showcase.sav'
 seed=seedpath.read_bytes();check(hashlib.sha1(seed).hexdigest()=='7831543efb239ef145764889214f8d83cd56eb14','Authenticated private seed')
 E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
 e=E(Path(meta['path']));e.set_memory(0,seed,0);e.run(3600)
 def tap(key,wait=180):
  inputs.append([8,key,wait]);e.run(8,key);e.run(wait)
 for key in (8,256,256,256):tap(key,300)
 for key in (8,256,256,256,256):tap(key,300)
 r=e.memory();check(r[0x87]==116,'Selected member remains Samurai')
 # Inventory initially opens the helmet category. Traverse native tabs and
 # choose the actual teaching weapon by its returned item ID, not row guesses.
 found=False
 for tab in range(5):
  r=e.memory();count=struct.unpack_from('<I',r,0x3c000)[0]
  check(0<count<=512,f'Bounded native inventory tab {tab}')
  ids=[struct.unpack_from('<I',r,0x3c234+i*20)[0] for i in range(count)]
  if 383 in ids:
   for _ in range(ids.index(383)):tap(32,20)
   found=True;break
  tap(128,180)
 check(found,'Native inventory contains Moonblossom383')
 e.screenshot(out/'samurai-equipment.png');e.save(out/'samurai-equipment.state')
 vram=C.string_at(*e.maps[0x06000000])
 (out/'equipment.vram').write_bytes(vram)
 # Fixed diagnostic button scenarios establish the real consumer. Each starts
 # from the same privately captured item selection; nothing is equipped/saved.
 observations=[]
 for name,key in [('selected',0),('select',4),('left-shoulder',1024),('right-shoulder',2048)]:
  e.load(out/'samurai-equipment.state')
  if key:tap(key,180)
  e.screenshot(out/f'consumer-{name}.png')
  vram=C.string_at(*e.maps[0x06000000]);(out/f'consumer-{name}.vram').write_bytes(vram)
  observations.append(dict(name=name,key=key,fullIconOffset=vram.find(raw),
                           tileOffsets=[vram.find(raw[i*32:(i+1)*32]) for i in range(8)]))
 (out/'consumer-observations.json').write_text(json.dumps(observations,indent=2)+'\n')
 check(next(o for o in observations if o['name']=='right-shoulder')['fullIconOffset']>=0,
       'Authored icon reached native R equipment-teaching VRAM')
 check(seedpath.read_bytes()==seed,'Private seed unchanged')
 report=dict(status='passed',romSha1=meta['romSha1'],baseRomSha1=meta['baseRomSha1'],checks=checks,inputs=inputs,
             coverage='Native all-job dispatch/canaries, authored portrait pixels and actual Samurai equipment teaching icon. No actor animation or production artwork acceptance.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(status='passed',checks=len(checks),romSha1=meta['romSha1'],report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(error=str(error),checks=checks,inputs=inputs,romSha1=meta['romSha1']),indent=2)+'\n')
 raise
finally:
 if e:e.close()
