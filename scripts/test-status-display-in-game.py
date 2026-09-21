"""Private status icons: real native rendering, attack, and suspend/cold load.

The status bytes are controlled setup. This verifies visibility and graphics
storage, not the still-unassembled actions that grant/expire these effects.
"""
import ctypes as C,hashlib,json,pathlib,runpy,struct,sys
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'build/expansion/probes'
meta=json.loads((P/'status-display/private/current.json').read_text())
if '--current' in sys.argv:
 from fell_test_context import load_context
 meta=load_context(True)
ROM=pathlib.Path(meta['path']);LAB=ROM.parent
FIX=LAB/'fixture';assert hashlib.sha1((FIX/'frozen.gba').read_bytes()).hexdigest()==meta['romSha1']
BASE=P/'battle-fixture';
if '--current' in sys.argv:BASE=P/'status-display/private/de421e6eeb26d694e607fb45d77951650461864c/base-fixture'
assert hashlib.sha1((BASE/'frozen.gba').read_bytes()).hexdigest()==meta['baseSha1']
Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];OUT=LAB/'game-tests';OUT.mkdir(exist_ok=True)
checks=[];outcomes=[]
def check(ok,label):assert ok,label;checks.append(label)
def tap(e,key,wait=180):e.run(8,key);e.run(wait)
def half(r,p):return struct.unpack_from('<H',r,p)[0]
def wrapper(r,unit):
 # Resolve the allocated wrapper by its canonical unit pointer and graphics
 # group shape. This test fixture's actual wrappers are retained as an oracle.
 for address in range(0x22000,0x24000,4):
  if struct.unpack_from('<I',r,address)[0]!=0x02000000+unit:continue
  owner=struct.unpack_from('<I',r,address+0x80)[0]-0x02000000
  sprite=struct.unpack_from('<I',r,address+0x48)[0]-0x02000000
  if 0<=owner<0x3f800 and 0<=sprite<0x3f800 and half(r,sprite+0x12)<0x400:return address
 raise AssertionError(('No native wrapper',hex(unit)))
def pool(r,unit=0x398):
 w=wrapper(r,unit);owner=struct.unpack_from('<I',r,w+0x80)[0]-0x02000000
 root=struct.unpack_from('<I',r,owner+8)[0]-0x02000000
 return struct.unpack_from('<4H',r,root+12)
def vram(e):return C.string_at(*e.maps[0x06000000])
anchor=Image.open(BASE/'battle-ready.png').convert('RGB').crop((530,345,650,375))
white=[i for i,p in enumerate(anchor.get_flattened_data()) if min(p)>=230]
assert len(white)>50
def ready(e,label,limit=900):
 # Bound input timing to an observed native Wait menu. The private overlay's
 # intro takes a few more frames; the generator's fixed-frame snapshot can
 # still precede the first menu. No keys are injected while waiting for it.
 for elapsed in range(0,limit,30):
  e.run(30);e.screenshot(OUT/'observed-menu.png')
  pixels=list(Image.open(OUT/'observed-menu.png').convert('RGB').crop((530,345,650,375)).get_flattened_data())
  if all(min(pixels[i])>=230 for i in white):return
 raise AssertionError(('Native turn menu did not appear',label))

control=Emulator(LAB/'base.gba')
try:
 control.load(BASE/'battle-ready.state');r=control.memory()
 control.set_memory(0x398+0xeb,bytes([r[0x398+0xeb]|2]));control.run(900)
 native_fixed=vram(control)[0x12400:0x13c00]
finally:control.close()
e=Emulator(ROM)
try:
 e.load(FIX/'battle-ready.state');r=e.memory();w=wrapper(r,0x398)
 check(pool(r)==(0,0x120,0x1e4,0x400),'fresh battle reserves exactly four tiles')
 e.set_memory(0x1e9b,b'\x05');e.set_memory(0x398+0xeb,bytes([r[0x398+0xeb]|2]))
 original=e.memory();fixed=vram(e)[0x12400:0x13c00];seen=set();tiles=set();captured=set()
 for frame in range(900):
  e.run(1);r=e.memory();icon=r[w+0x75];seen.add(icon)
  if icon in (25,26):
   sprite=struct.unpack_from('<I',r,w+0x48)[0]-0x02000000;tiles.add((icon,half(r,sprite+0x12)))
   if icon not in captured and (icon,half(r,sprite+0x12))==(icon,0x1e0+(icon-25)*2):
    e.screenshot(OUT/f'icon-{icon}.png');captured.add(icon)
 check({3,25,26}<=seen,('native Protect and both custom icons cycle',sorted(seen)))
 check((25,0x1e0) in tiles and (26,0x1e2) in tiles,'each custom icon uses its reserved tiles')
 (OUT/'atlas-before.bin').write_bytes(fixed);(OUT/'atlas-after.bin').write_bytes(vram(e)[0x12400:0x13c00])
 # The fixed UI area contains native text that updates after the fixture's
 # initial frame. Compare to the same actual native run, not a frozen before.
 check(vram(e)[0x12400:0x13c00]==native_fixed,'fixed battle atlas matches native control through all icons')
 check(e.memory()[0x1940:0x1ebc]==original[0x1940:0x1ebc],'rendering does not alter inventory/AP/preferences/status')
 e.set_memory(0x1e9b,b'\x00');e.run(300);seen.clear()
 for _ in range(180):e.run(1);seen.add(e.memory()[w+0x75])
 check(not seen.intersection({25,26}),'removed custom effects stop displaying')
 check(3 in seen,'original Protect remains visible after custom effects removed')
finally:e.close()

# Compare native Fight and graphics allocation against a separately fresh
# baseline. In the composed build, icons can shift the frame in which a roll
# occurs. Use explicit deterministic RNG oracles for this graphics-isolation
# comparison; unmodified hit/miss RNG is covered by the Fell gameplay suite.
random_oracles=[]
for name,rom,fix,active in [('native',LAB/'base.gba',BASE,False),('overlay',ROM,FIX,False),('icons',ROM,FIX,True)]:
 if '--current' in sys.argv:
  image=bytearray(rom.read_bytes())
  for offset,expected in ((0x2804,'044a1168'),(0x2838,'70b54e46')):
   assert image[offset:offset+4].hex()==expected
   image[offset:offset+4]=bytes.fromhex('00207047')
  rom=OUT/(name+'-graphics-rng-control.gba');rom.write_bytes(image)
  random_oracles.append(dict(case=name,romSha1=hashlib.sha1(image).hexdigest(),fixedReturn=0,offsets=[0x2804,0x2838]))
 e=Emulator(rom)
 try:
  e.load(fix/'battle-ready.state');ready(e,name);e.set_memory(0x33e4+0x18,struct.pack('<HH',250,250))
  if active:e.set_memory(0x1e9b,b'\x05')
  initial=e.memory();fixed=vram(e)[0x12400:0x13c00]
  for key in (256,128,128,128):tap(e,key)
  tap(e,256,600)
  for key in (256,256,128,256,256):tap(e,key)
  C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',2),4)
  tap(e,256,2400)
  tap(e,256,600) # Move+Act spent both slots: confirm native end-turn facing.
  ready(e,name+' following turn',6300);r=e.memory();e.screenshot(OUT/(name+'-fight.png'))
  check(half(r,0x33e4+0x18)<250,name+' native Fight completed')
  check(r[0x1940:0x1ebc]==initial[0x1940:0x1ebc],name+' attack preserves storage')
  check(r[0x3ff44:]==initial[0x3ff44:],name+' guard preserved')
  # Native animated UI tiles elsewhere in the fixed region depend on frame
  # phase. Compare the complete original status-icon atlas and stable HUD.
  final_atlas=vram(e)[0x128e0:0x134e0]
  hud=Image.open(OUT/(name+'-fight.png')).convert('RGB').crop((0,320,445,480)).tobytes()
  if name=='native':native_attack_atlas=final_atlas
  else:check(final_atlas==native_attack_atlas,name+' all24 native status icons preserved after weapon animation')
  if name=='native':native_hud=hud
  else:check(hud==native_hud,name+' following-turn HUD matches native control')
  outcomes.append(dict(case=name,damage=250-half(r,0x33e4+0x18),actorHP=half(r,0x398+0x18),actorMP=half(r,0x398+0x1c)))
 finally:e.close()
check(all({k:v for k,v in row.items() if k!='case'}=={k:v for k,v in outcomes[0].items() if k!='case'} for row in outcomes),'native Fight outcomes identical with overlay and visible custom icons')

e=Emulator(ROM)
try:
 e.load(FIX/'battle-ready.state');ready(e,'suspend');e.set_memory(0x1e9b,b'\x05');e.run(60)
 for key in (1,8,32,32,32,32,32,256,256,256):tap(e,key)
 saved=e.memory(0);(OUT/'icons-suspend.sav').write_bytes(saved)
finally:e.close()
e=Emulator(ROM)
try:
 e.set_memory(0,saved,0);e.run(3600)
 for key,wait in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):tap(e,key,wait)
 r=e.memory();check(r[0x1e9b]==5,'native suspend and cold Resume retain packed status')
 check(pool(r)==(0,0x120,0x1e4,0x400),'cold Resume reconstructs reserved graphics pool')
 w=wrapper(r,0x398);seen=set()
 for _ in range(450):e.run(1);seen.add(e.memory()[w+0x75])
 check({25,26}<=seen,('both custom icons visible after cold Resume',sorted(seen)))
 e.screenshot(OUT/'cold-resume.png')
finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],baseSha1=meta['baseSha1'],checks=checks,total=len(checks),outcomes=outcomes,randomOracles=random_oracles,scope='Fresh per-ROM fixtures, native icon cycles, original fixed atlas, Fight graphics with recorded RNG controls, and unmodified native suspend/cold Resume. Status grants are controlled setup; production hit/miss RNG and lifecycle are tested separately.')
(LAB/'status-game-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
