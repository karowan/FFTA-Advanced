"""Actual Higanbana execution reaches the native post-action harmful-status law."""
import ast,ctypes as C,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text());ROM=pathlib.Path(meta['path']);LAB=ROM.parent;OUT=LAB/'wound-law-game';OUT.mkdir(exist_ok=True);rom=ROM.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
proof=json.loads((LAB/'higanbana-game/report.json').read_text());assert proof['passed'] and proof['romSha1']==meta['romSha1']
seed=next(o['seed'] for o in proof['outcomes'] if o['damage']>0)
UNIT,TARGET,RETURN,STACK=0x02000080,0x020033e4,0x08000100,0x03007000
Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m=ARM(rom,(LAB/'fixture/battle-ready.iwram').read_bytes());m.put(0x02000000,(LAB/'higanbana-game/confirmation.ram').read_bytes());bank=m.word(m.word(0x080cd538)+4)
def index(effect,kind):return next(i for i in range(1,144) if struct.unpack_from('<H',m.read(bank+8*i,8),4)[0]==effect and m.read(bank+8*i+6,1)[0]==kind)
reaction,immunity=index(13,2),index(11,3);outcomes=[]
for condition,kind,value in [('hit',16,0),('MP',16,0),('immune',16,0),('lethal',16,0),('specific-Poison',15,9)]:
 image=bytearray(rom)
 # This fixture's first banned rule is the native Charm law at8529344.
 # Only its test copy becomes the broad harmful-status rule (or Poison control).
 assert image[0x529348:0x52934a]==b'\x0f\x1c'
 image[0x529348:0x52934a]=bytes((kind,value));image[0x135076:0x135078]=b'\xfe\xe7'
 path=OUT/(condition+'.gba');path.write_bytes(image);e=Emulator(path)
 try:
  e.load(LAB/'higanbana-game/confirmation.state')
  if condition in ('MP','immune'):
   i=reaction if condition=='MP' else immunity;e.set_memory(0x33e9,bytes((2,1,2)));e.set_memory(0x33e4+0x3a+(condition=='immune'),bytes([i]));e.set_memory(0x33e4+0x40+i,b'\xff')
  if condition=='lethal':e.set_memory(0x33fc,b'\x01\x00')
  C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4);e.run(8,256);e.run(3000)
  state=OUT/(condition+'.state');e.save(state);regs=struct.unpack_from('<17I',state.read_bytes(),0x20);r=e.memory()
  assert regs[15]==0x08135078,(condition,hex(regs[15]))
  expected=int(condition=='hit');assert regs[0]==expected,(condition,regs[0],expected)
  outcomes.append(dict(condition=condition,seed=seed,lawKind=kind,statusValue=value,nativeLawResult=regs[0],HP=struct.unpack_from('<H',r,0x33fc)[0],MP=struct.unpack_from('<H',r,0x3400)[0],wound=hex(struct.unpack_from('<H',r,0x1ef4)[0])))
  (OUT/(condition+'.ram')).write_bytes(r)
 finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],outcomes=outcomes,scope='Actual menu-confirmed attack, native result object and post-action law caller; modified rule data and return breakpoint are test-only. Judge animation/card persistence is a separate integration check.')
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
