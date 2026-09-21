"""Deterministic frame observation on actual native menu and intro snapshots."""
import json,pathlib,runpy,types
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'build/expansion/probes'
observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];checks=0
def check(value,label):
 global checks
 assert value,label;checks+=1
for pixel,stride in ((0,2),(1,4),(2,2)):
 for fill in (0,255):
  fake=types.SimpleNamespace(frame=(bytes([fill])*(240*160*stride),240,160,240*stride,pixel))
  check(not observe['menu_visible'](fake),('blank/flash must not qualify',pixel,fill))
base=P/'battle-fixture';e=Emulator(base/'frozen.gba')
try:
 e.load(base/'battle-ready.state');e.run(1)
 check(observe['menu_visible'](e),'actual native turn menu recognized')
 check(observe['wait_for_menu'](e,0)==0,'already visible menu needs no extra frames')
finally:e.close()
meta=json.loads((P/'status-display/private/current.json').read_text());lab=pathlib.Path(meta['path']).parent
e=Emulator(pathlib.Path(meta['path']))
try:
 e.load(lab/'fixture/battle-ready.state');e.run(1)
 check(not observe['menu_visible'](e),'actual pre-menu intro snapshot rejected')
 try:observe['wait_for_menu'](e,0)
 except AssertionError:check(True,'zero budget fails before injecting input')
 else:raise AssertionError('Unready intro accepted without waiting')
 before=e.memory()[0x1940:0x1ebc];frames=observe['wait_for_menu'](e,1800)
 check(frames>0 and observe['menu_visible'](e),'bounded observation reaches actual turn menu')
 check(e.memory()[0x1940:0x1ebc]==before,'readiness wait does not alter inventory/AP/preferences/status')
finally:e.close()
print(json.dumps(dict(passed=True,checks=checks,privateReadyWaitFrames=frames),indent=2))
