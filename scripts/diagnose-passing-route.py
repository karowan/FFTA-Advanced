"""Fixed native Move/undo observations for Passing Step route integration.

Read-only observation of a private battle fixture; no route/result injection.
This is an analysis prerequisite, not Passing Step acceptance.
"""
import ctypes as C,hashlib,json,pathlib,runpy,struct
from native_battle_wrappers import fixed_giza_formation,from_emulator
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
ROM=pathlib.Path(meta['path']);image=ROM.read_bytes();OUT=ROM.parent/'passing-route-trace';OUT.mkdir(exist_ok=True)
assert hashlib.sha1(image).hexdigest()==meta['romSha1']
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
word=lambda r,p:struct.unpack_from('<I',r,p)[0]
half=lambda r,p:struct.unpack_from('<H',r,p)[0]
samples=[]
def tap(e,key):e.run(8,key);e.run(180)
def capture(e,label,w):
 r=e.memory();folder=OUT/label;folder.mkdir(exist_ok=True)
 e.save(folder/'state.bin');e.screenshot(folder/'frame.png');(folder/'ram.bin').write_bytes(r)
 (folder/'iwram.bin').write_bytes(C.string_at(*e.maps[0x03000000]))
 manager=word(r,0xf438)-0x02000000
 sample=dict(label=label,actor=hex(word(r,manager+24)),mode=r[manager+4],flags=r[0x1f70],
  xy=[half(r,w+8)//32,half(r,w+12)//32],unit=r[0x5a8:0x6b0].hex(),
  battle=r[0xf4e8:0xf4e8+0x1ac].hex(),route=r[0xf4e8+0x124:0xf4e8+0x1a4].hex(),
  routeCount=word(r,0xf4e8+0x1a4),phase=half(r,0xf4e8+0xdc))
 samples.append(sample)
 return sample
for label,keys,position in [('one',(16,),(0,13)),('two',(16,16),(0,12))]:
 e=E(ROM)
 try:
  e.load(ROM.parent/'fixture/battle-ready.state');e.run(1);observe['wait_for_menu'](e)
  fixed_giza_formation(image,e);w=from_emulator(image,e)[0x5a8]
  for turn in range(12):
   r=e.memory();manager=word(r,0xf438)-0x02000000
   if word(r,manager+24)==0x020005a8:break
   previous=word(r,manager+24)
   for key in (32,32,256,256):tap(e,key)
   for frames in range(0,9001,10):
    r=e.memory();manager=word(r,0xf438)-0x02000000
    if observe['menu_visible'](e) and word(r,manager+24)!=previous:break
    assert frames<9000,'native turn timeout'
    e.run(10)
  start=capture(e,label+'-start',w);assert start['actor']=='0x20005a8' and start['xy']==[0,14]
  tap(e,256)
  for key in keys:tap(e,key)
  capture(e,label+'-selected',w)
  tap(e,256);e.run(720);observe['wait_for_menu'](e)
  moved=capture(e,label+'-moved',w);assert moved['xy']==list(position),(label,moved['xy'])
  tap(e,1);tap(e,1);observe['wait_for_menu'](e)
  undo=capture(e,label+'-undo',w);assert undo['xy']==[0,14]
 finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],samples=samples,scope=__doc__)
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
