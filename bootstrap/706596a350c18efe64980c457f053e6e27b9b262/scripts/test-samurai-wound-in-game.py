"""Actual Higanbana menu, preview/cancel, native P, hit/miss and refresh."""
import ast,ctypes as C,hashlib,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1];meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text())
ROM=pathlib.Path(meta['path']);LAB=ROM.parent;FIX=LAB/'fixture';image=ROM.read_bytes();OUT=LAB/'higanbana-game';OUT.mkdir(exist_ok=True)
assert hashlib.sha1(image).hexdigest()==meta['romSha1'] and (FIX/'frozen.gba').read_bytes()==image
Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
from native_battle_wrappers import fixed_giza_formation
ACTOR,TARGET,AS,TS=0x80,0x33e4,0x1e98,0x1eb4;guard=b'\xd7'*0xb8;checks=0;outcomes=[]
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
weapon=next(item['romItemId'] for item in registry['items'] if item['name']=='Red Spider Katana')
half=lambda r,p:struct.unpack_from('<H',r,p)[0]
tree=ast.parse((ROOT/'scripts/test-samurai-in-game.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('check','tap','active','ready_menu')],type_ignores=[]),'<native input helpers>','exec'))
def capture(e,label):
 r=e.memory();e.save(OUT/f'{label}.state');e.screenshot(OUT/f'{label}.png');(OUT/f'{label}.ram').write_bytes(r);check(r[0x3ff48:]==guard,('guard',label));return r
control=bytearray(image);control[0x1300e2:0x1300f2]=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()[0x1300e2:0x1300f2];CONTROL=OUT/'native-P.gba';CONTROL.write_bytes(control)
e=Emulator(ROM)
try:
 e.load(FIX/'battle-ready.state');ready_menu(e);fixed_giza_formation(image,e)
 for offset in (5,7,0x35):e.set_memory(ACTOR+offset,b'\x74')
 e.set_memory(ACTOR+0x2a,struct.pack('<5H',weapon,0,0,0,0));e.set_memory(0x1b48,b'\xff');e.set_memory(0x3ff44,bytes(4));e.set_memory(0x3ff48,guard)
 for turn in range(4):
  previous=active(e)
  for key in (32,32,256,256):tap(e,key)
  ready_menu(e,previous)
 check(active(e)==0x02000080,'Marche ready')
 e.set_memory(ACTOR+0x18,struct.pack('<4H',100,100,50,50));e.set_memory(ACTOR+0xe8,bytes(8));e.set_memory(AS,b'\x05')
 e.set_memory(TARGET+0x18,struct.pack('<4H',250,250,49,49));e.set_memory(TARGET+0xe8,bytes(8));e.set_memory(TS,b'\x01');e.set_memory(0x1ef4,b'\x07\x80')
 ready=capture(e,'ready');stable=ready[0x1940:0x1e70]
 for key in (256,128,128,32):tap(e,key)
 tap(e,256,600)
 for key in (256,32,256):tap(e,key)
 capture(e,'ability-menu')
 for key in (256,128,256):tap(e,key)
 preview=capture(e,'preview');check(half(preview,0xf3fc)==355,'Higanbana selected')
 check((half(preview,ACTOR+0x1c),preview[AS],half(preview,0x1ef4))==(50,5,0x8007),'Preview mutation')
 tap(e,1);cancel=capture(e,'cancelled');check((half(cancel,ACTOR+0x1c),cancel[AS],half(cancel,0x1ef4))==(50,5,0x8007),'Cancel mutation')
 # Native cancellation can recenter the cursor. Restore the observed preview
 # state so the commit replay starts from the same selected enemy.
 e.load(OUT/'preview.state');e.run(1);tap(e,256);capture(e,'confirmation')
finally:e.close()
seen=set()
for seed in range(16):
 results=[];rng=[]
 for label,path in [('native-P',CONTROL),('higanbana',ROM)]:
  e=Emulator(path)
  try:
   e.load(OUT/'confirmation.state');C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4);tap(e,256,1500);r=capture(e,f'{label}-{seed}')
   results.append(r);rng.append(C.string_at(e.maps[0x03000000][0]+0x34b0,4))
  finally:e.close()
 ref,r=results;p=250-half(ref,TARGET+0x18);damage=250-half(r,TARGET+0x18)
 check(damage==p*80*5*6//2000,('native P',seed,p,damage));check(half(r,0x1ef4)==(0x8000|p//2 if damage else 0x8007),('snapshot/refresh',seed))
 check(rng[0]==rng[1],'Extra RNG sample');check((half(r,ACTOR+0x1c),r[AS])==(42,1),'MP/Centered');check(r[0x1940:0x1e70]==stable,'AP/inventory');check(r[0x3ff44:0x3ff48]==bytes(4),'Scope not retired')
 seen.add(damage>0);outcomes.append(dict(seed=seed,P=p,damage=damage,wound=half(r,0x1ef4)))
 if seen=={False,True}:break
check(seen=={False,True},'Bounded hit/miss coverage')
report=dict(passed=True,romSha1=meta['romSha1'],checks=checks,outcomes=outcomes,scope='Native menu/preview/cancel/commit, same-sample P and RNG, hit/miss, wound refresh and Centered/Exposed composition; pulse tests separate')
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
