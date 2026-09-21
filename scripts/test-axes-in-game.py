"""Render and commit native Fight with all eight axes on a disposable fixture.

This isolates axe assets and native weapon selection; it does not claim that
custom A-abilities are enabled or that this fixture acquired equipment normally.
"""
import ctypes as C, hashlib, json, pathlib, runpy, shutil, struct
from PIL import Image, ImageDraw
ROOT=pathlib.Path(__file__).resolve().parents[1]
FIX=ROOT/'build/expansion/probes/battle-fixture'
OUT=ROOT/'build/expansion/probes/axes-in-game';OUT.mkdir(exist_ok=True)
ROM=OUT/'frozen.gba';shutil.copy2(FIX/'frozen.gba',ROM)
shutil.copy2(FIX/'battle-ready.state',OUT/'initial.state')
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
a=runpy.run_path(str(ROOT/'scripts/test-battle-inventory.py'))
hp=runpy.run_path(str(ROOT/'scripts/probe-ap-copy-heap.py'))
guard=bytes([0xD7])*0xbc;results=[]
def tap(e,key,wait=120):e.run(8,key);e.run(wait)
def health(ram):return struct.unpack_from('<H',ram,0x1a0)[0]
for item in range(453,461):
 e=h['Emulator'](ROM)
 try:
  e.load(OUT/'initial.state');e.run(1)
  # Equipment slot0 is the actual primary. Preserve armor and remove any
  # other weapon/shield by reading its real type, rather than guessing slots.
  m=a['ARM'](C.string_at(*e.maps[0x03000000]));m.put(0x08000000,ROM.read_bytes());m.put(0x02000000,e.memory())
  table=m.r32(0x080ca7c4);gear=bytearray(e.memory()[0x3c2:0x3cc])
  for slot in range(1,5):
   old=struct.unpack_from('<H',gear,slot*2)[0]
   if old and (1<=m.get(table+old*32+8,1)[0]<=20 or m.get(table+old*32+8,1)[0]==31):struct.pack_into('<H',gear,slot*2,0)
  struct.pack_into('<H',gear,0,item);e.set_memory(0x3c2,bytes(gear))
  m.put(0x02000000,e.memory());m.call(0x0812f0cc,0x02000398,0x02008000)
  weapons=[m.r16(0x02008000),m.r16(0x02008002)]
  assert weapons==[item,0],(item,weapons)
  assert m.get(table+item*32+8,1)==b'\x1f'
  before=e.memory();before_hp=health(before)
  for key in [32,256,256,128,256]:tap(e,key)
  e.screenshot(OUT/f'{item}-preview.png');assert health(e.memory())==before_hp
  for _ in range(3):tap(e,1)
  assert health(e.memory())==before_hp
  for key in [256,256,128,256,256]:tap(e,key)
  assert health(e.memory())==before_hp
  e.run(8,256)
  frames=[]
  for frame in range(0,480,12):
   e.run(12);p=OUT/f'{item}-frame-{frame:03}.png';e.screenshot(p)
   if frame%36==0:frames.append(p)
  e.run(720);after=e.memory();e.screenshot(OUT/f'{item}-result.png')
  assert health(after)<before_hp,(item,'Fight did not damage adjacent target',before_hp,health(after))
  assert after[0x3a2]>before[0x3a2],(item,'No EXP award')
  assert after[0x3ff44:0x40000]==guard,(item,'Reserved guard')
  assert after[0x3c2:0x3cc]==bytes(gear),(item,'Equipment mutated')
  assert after[0x1b40:0x1e70]==before[0x1b40:0x1e70],(item,'AP sidecars mutated')
  assert hp['heap'](after)['end']==0x0203f800
  # A filmstrip records multiple phases, avoiding acceptance of a still
  # preview screenshot as evidence of a rendered attack animation.
  strip=Image.new('RGB',(480*4,340*4),'#18202b');draw=ImageDraw.Draw(strip)
  for i,p in enumerate(frames):
   im=Image.open(p).resize((480,320));x=(i%4)*480;y=(i//4)*340
   strip.paste(im,(x,y));draw.text((x+5,y+321),p.stem,fill='white')
  strip.save(OUT/f'{item}-filmstrip.png')
  results.append({'item':item,'primaryWeapon':weapons[0],'offhandWeapon':weapons[1],
                  'beforeHP':before_hp,'afterHP':health(after),'experience':after[0x3a2]-before[0x3a2],
                  'filmstrip':str(OUT/f'{item}-filmstrip.png')})
  print(json.dumps(results[-1]),flush=True)
 finally:e.close()
report={'passed':True,'romSha1':hashlib.sha1(ROM.read_bytes()).hexdigest(),
        'fixture':'Native Herb Picking first turn; only disposable Jona weapon slots changed',
        'results':results,'scope':'Native Fight preview/cancel/commit and rendered frames; no custom A-effect or audio acceptance'}
(OUT/'report.json').write_text(json.dumps(report,indent=2))
