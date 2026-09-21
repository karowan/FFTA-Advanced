"""Fixed native Fight routes locate own-turn movement state at executor entry.

Private entry trap only; no Composure effect or expected action result injected.
"""
import ctypes as C,hashlib,json,pathlib,runpy,struct
from native_battle_wrappers import fixed_giza_formation,from_emulator
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/job-state/current.json').read_text());ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1'] and (ROM.parent/'fixture/frozen.gba').read_bytes()==rom
OUT=ROM.parent/'composure-entry';OUT.mkdir(exist_ok=True);image=bytearray(rom);image[0xa433c:0xa433e]=bytes.fromhex('fee7');TRAP=OUT/'entry-trap.gba';TRAP.write_bytes(image)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'));samples=[]
word=lambda r,p:struct.unpack_from('<I',r,p)[0]
def active(e):
 r=e.memory();p=word(r,0xf438)-0x02000000
 assert 0<=p<len(r)-28
 return word(r,p+24)
def tap(e,k,wait=180):e.run(8,k);e.run(wait)
def menu(e,previous=None):
 for elapsed in range(0,9001,10):
  if observe['menu_visible'](e) and (previous is None or active(e)!=previous):return
  if elapsed<9000:e.run(10)
 raise AssertionError(('turn menu timeout',hex(active(e))))
def capture(e,label):
 r=e.memory();e.save(OUT/(label+'.state'));(OUT/(label+'.ram')).write_bytes(r);e.screenshot(OUT/(label+'.png'))
 iw=C.string_at(*e.maps[0x03000000]);registers=struct.unpack_from('<17I',(OUT/(label+'.state')).read_bytes(),0x20)
 (OUT/(label+'.iwram')).write_bytes(iw)
 row=dict(label=label,currentUnit=hex(active(e)),moveFlag=bool(r[0x1f70]&16),nativeFlags=r[0x1f70:0x1f74].hex(),registers=list(registers))
 if registers[15]==0x080a433e:row['action']=word(iw,registers[13]-0x03000000)
 samples.append(row);(OUT/'samples.json').write_text(json.dumps(samples,indent=2));return row
for moved in (False,True):
 e=E(TRAP);name='moved' if moved else 'unmoved'
 try:
  e.load(ROM.parent/'fixture/battle-ready.state');e.set_memory(0x3ff44,bytes(8)+b'\xd7'*0xb4);fixed_giza_formation(rom,e)
  wrappers=from_emulator(rom,e);y=12 if moved else 13
  e.set_memory(0x33e4+0xf6,bytes((3,y)));e.set_memory(wrappers[0x33e4]+8,struct.pack('<3H',3*32+16,32,y*32+16))
  for turn in range(4):
   menu(e);previous=active(e)
   for key in (32,32,256,256):tap(e,key)
   menu(e,previous)
  assert active(e)==0x02000080
  before=capture(e,name+'-turn-ready');assert not before['moveFlag']
  if moved:
   for key in (256,16):tap(e,key)
   tap(e,256,900);after=capture(e,name+'-after-move');assert after['moveFlag']
   route=(256,256,128,256,256,256)
  else:route=(32,256,256,128,256,256,256)
  for step,key in enumerate(route):
   tap(e,key);row=capture(e,f'{name}-action-{step}')
   if row['registers'][15]==0x080a433e:break
  assert row['registers'][15]==0x080a433e,(name,'Fight entry not reached',row)
  assert row['action']==0,(name,'not Fight',row)
  wrapper=row['registers'][1]-0x02000000;assert word(e.memory(),wrapper)==0x02000080
  assert row['currentUnit']=='0x2000080'
 finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],samples=samples,scope=__doc__)
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
