"""Deterministic actual icon cycling, glyph bytes, expiry and cold reconstruction."""
import ast,collections,ctypes as C,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text());ROM=pathlib.Path(meta['path']);FIX=ROM.parent/'fixture';OUT=ROM.parent/'wound-status';OUT.mkdir(exist_ok=True)
rom=ROM.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1'] and (FIX/'frozen.gba').read_bytes()==rom
Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];menu=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
RETURN,STACK=0x08000100,0x03007000;checks=collections.Counter();unit=0x398
half=lambda b,p:struct.unpack_from('<H',b,p)[0]
word=lambda b,p:struct.unpack_from('<I',b,p)[0]
def check(k,a,b):checks[k]+=1;assert a==b,(k,a,b)
def tap(e,k,w=180):e.run(8,k);e.run(w)
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
tree=ast.parse((ROOT/'scripts/test-arcs-in-game.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='native_wrappers'],type_ignores=[]),'<native wrappers>','exec'))
def pool(b,w):
 owner=word(b,w+0x80)-0x02000000;root=word(b,owner+8)-0x02000000
 return struct.unpack_from('<4H',b,root+12)
def cycle(e,w,label):
 seen=set();glyph=False
 for frame in range(900):
  e.run(1);b=e.memory();key=b[w+0x75];seen.add(key)
  if key==27:
   sprite=word(b,w+0x48)-0x02000000
   if half(b,sprite+0x12)==0x1e4:
    vram=C.string_at(*e.maps[0x06000000]);p=meta['symbols']['wound_rows']-0x08000000
    check('wound_glyph_exact_VRAM',vram[0x13c80:0x13cc0],rom[p:p+64])
    e.screenshot(OUT/(label+'.png'));glyph=True;break
 check('native_renderer_reaches_wound',glyph,True)
 return seen
e=Emulator(ROM)
try:
 e.load(FIX/'battle-ready.state');menu['wait_for_menu'](e,limit=9000);w=native_wrappers(e)[unit]
 check('reserves_six_tiles',pool(e.memory(),w),(0,0x120,0x1e6,0x400))
 e.set_memory(0x1e9b,b'\x05');e.set_memory(0x1ec2,b'\x0b\x80');e.set_memory(unit+0xeb,b'\x02')
 fixed=C.string_at(*e.maps[0x06000000])[0x128e0:0x134e0]
 seen=cycle(e,w,'wound-visible')
 for _ in range(900):e.run(1);seen.add(e.memory()[w+0x75])
 check('old_and_new_icons_coexist',{3,25,26,27}<=seen,True)
 check('native_icon_atlas_preserved',C.string_at(*e.maps[0x06000000])[0x128e0:0x134e0],fixed)
 old=e.memory(0)
 for key in (1,8,16,256,256):tap(e,key)
 tap(e,256,300);saved=e.memory(0);check('native_suspend_wrote',saved!=old,True);(OUT/'suspended.sav').write_bytes(saved)
finally:e.close()
e=Emulator(ROM)
try:
 e.set_memory(0,saved,0);e.run(3600)
 for key,frames in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):tap(e,key,frames)
 menu['wait_for_menu'](e,limit=9000);w=native_wrappers(e)[unit];check('cold_wound_record',half(e.memory(),0x1ec2),0x800b)
 check('cold_six_tile_pool',pool(e.memory(),w),(0,0x120,0x1e6,0x400));cycle(e,w,'cold-wound-visible')
 # Invoke native Esuna/Cureall through the actual game in the separate
 # lifecycle suite. Here the controlled state removal isolates icon expiry.
 e.set_memory(0x1ec2,bytes(2));e.run(300);seen=set()
 for _ in range(600):e.run(1);seen.add(e.memory()[w+0x75])
 check('wound_icon_stops_when_cured',27 in seen,False);check('original_icons_still_cycle',{3,25,26}<=seen,True)
finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),scope='Actual native status renderer, exact glyph/atlas/pool checks, old-icon coexistence and expiry, native suspend/fresh cold resume; no screenshot interpretation by agents')
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
