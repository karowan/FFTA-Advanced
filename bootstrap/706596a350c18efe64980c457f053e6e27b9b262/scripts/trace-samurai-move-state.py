"""Fixed native Move/cancel/Wait sequence for Composure timing discovery."""
import hashlib,json,pathlib,runpy,struct
from native_battle_wrappers import from_emulator,fixed_giza_formation
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text())
ROM=pathlib.Path(meta['path']);assert hashlib.sha1(ROM.read_bytes()).hexdigest()==meta['romSha1']
OUT=ROM.parent/'move-state';OUT.mkdir(exist_ok=True)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
menu=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
def word(r,p):return struct.unpack_from('<I',r,p)[0]
def tap(e,k,wait=180):e.run(8,k);e.run(wait)
flag_base=struct.unpack_from('<I',ROM.read_bytes(),0xc9568)[0]-0x02000000
assert flag_base==0x1f70
e=E(ROM);samples=[]
try:
 e.load(ROM.parent/'fixture/battle-ready.state');fixed_giza_formation(ROM.read_bytes(),e);e.run(1)
 wrapper=from_emulator(ROM.read_bytes(),e)[0x398]
 def capture(label,position):
  r=e.memory();p=word(r,0xf438)-0x02000000
  assert 0<=p<=len(r)-0x100
  coords=tuple(struct.unpack_from('<H',r,wrapper+o)[0]//32 for o in (8,12))
  assert coords==position,(label,coords,position)
  e.save(OUT/(label+'.state'));(OUT/(label+'.ram')).write_bytes(r)
  samples.append(dict(label=label,position=coords,currentUnit=hex(word(r,p+24)),nativeMoveFlag=bool(r[flag_base]&16),controller=hex(p),controllerBytes=r[p:p+0x100].hex(),wrapper=hex(wrapper),wrapperBytes=r[wrapper:wrapper+0x80].hex(),unitBytes=r[0x398:0x4a0].hex()))
 capture('start',(1,14));assert samples[-1]['currentUnit']=='0x2000398'
 tap(e,256);tap(e,16);tap(e,16);tap(e,256,900);capture('moved',(1,12))
 tap(e,1,600);capture('cancelled',(1,14))
 tap(e,16);tap(e,16);tap(e,256,900);capture('moved-again',(1,12))
 tap(e,32);tap(e,256);tap(e,256,900);menu['wait_for_menu'](e,limit=9000)
 capture('next-turn',(1,12));assert samples[-1]['currentUnit']!='0x2000398'
 assert [s['nativeMoveFlag'] for s in samples]==[False,True,False,True,False]
 # Selecting the origin is a separate native path from cancelling a move.
 e.load(OUT/'start.state');e.run(1);tap(e,256);tap(e,256,900);capture('zero-distance',(1,14))
 assert not samples[-1]['nativeMoveFlag'],'Selecting the origin must not count as movement'
finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],samples=samples,scope=__doc__,limitations='Timing discovery only; does not assert a Composure implementation or infer an action-start flag.')
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
