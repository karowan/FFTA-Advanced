"""Actual Judge resolution, turn return and native cold-save card persistence."""
import ctypes as C,hashlib,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1];meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text());ROM=pathlib.Path(meta['path']);LAB=ROM.parent;OUT=LAB/'judge-game';OUT.mkdir(exist_ok=True);rom=ROM.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
proof=json.loads((LAB/'higanbana-game/report.json').read_text());assert proof['passed'] and proof['romSha1']==meta['romSha1']
hit=next(o['seed'] for o in proof['outcomes'] if o['damage']>0);miss=next(o['seed'] for o in proof['outcomes'] if o['damage']==0)
Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];menu=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'));checks=0;outcomes=[]
def check(ok,detail):
 global checks
 checks+=1;assert ok,detail
def tap(e,key,wait=180):e.run(8,key);e.run(wait)
def ready(e):
 for frame in range(9000):
  if menu['menu_visible'](e):return frame
  e.run(1)
  if frame%180==179:e.run(8,256)
 raise AssertionError('Judge sequence never returned to native turn menu')
def cards(e):
 r=e.memory();return [r[0x183],r[0x182]]
# Native status menu757A0 loads literal103 at758D8;757BC builds102.
check(struct.unpack_from('<I',rom,0x758d8)[0]==0x103,'Native yellow-card field')
for label,seed,kind,value in (('banned-hit',hit,16,0),('banned-miss',miss,16,0),('Poison-control',hit,15,9)):
 image=bytearray(rom);check(image[0x529348:0x52934a]==b'\x0f\x1c','Fixture first law');image[0x529348:0x52934a]=bytes((kind,value));path=OUT/(label+'.gba');path.write_bytes(image);e=Emulator(path)
 try:
  e.load(LAB/'higanbana-game/confirmation.state');before=cards(e);C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4)
  tap(e,256,1800);e.screenshot(OUT/(label+'-resolved.png'));tap(e,256,900);frames=ready(e);after=cards(e)
  e.save(OUT/(label+'-next-turn.state'));(OUT/(label+'-next-turn.ram')).write_bytes(e.memory())
  print('judge',label,before,after,'wait',frames,flush=True)
  check(after==[before[0]+(label=='banned-hit'),before[1]],('Card counts',label,before,after))
  outcome=dict(label=label,seed=seed,before=before,after=after,menuFrames=frames);outcomes.append(outcome)
  if label!='banned-hit':continue
  old=e.memory(0)
  for key in (1,8,16,256,256):tap(e,key)
  tap(e,256,300);saved=e.memory(0);check(saved!=old,'Native suspend did not write');(OUT/'suspended.sav').write_bytes(saved)
 finally:e.close()
 if label=='banned-hit':
  e=Emulator(path)
  try:
   e.set_memory(0,saved,0);e.run(3600)
   for key,frames in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):tap(e,key,frames)
   menu['wait_for_menu'](e,limit=9000);check(cards(e)==after,('Cold card counts',cards(e),after));outcome['coldCards']=cards(e);e.save(OUT/'cold-resumed.state')
  finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],checks=checks,outcomes=outcomes,scope='Native Judge penalty on Higanbana Wound, no card for miss/specific Poison, bounded native turn return, native suspend and fresh cold resume; only initial law card data and RNG are fixtures')
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
