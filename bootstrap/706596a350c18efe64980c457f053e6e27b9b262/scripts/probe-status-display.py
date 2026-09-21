"""Disposable native status-panel captures for custom effect UI integration."""
import pathlib,runpy,ctypes as C,json
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'build/expansion/probes';F=P/'battle-fixture';OUT=P/'status-display';OUT.mkdir(exist_ok=True)
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'));e=h['Emulator'](F/'frozen.gba')
def tap(key):e.run(8,key);e.run(180)
def capture(label):
 e.screenshot(OUT/(label+'.png'));e.save(OUT/(label+'.state'));(OUT/(label+'.ram')).write_bytes(e.memory());(OUT/(label+'.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
try:
 e.load(F/'battle-ready.state');e.run(1)
 for key in (32,32,32,256):tap(key)
 capture('status')
 for index,key in enumerate((256,1,2048,1024,4,8,64,128,16,32)):
  e.load(OUT/'status.state');tap(key);capture('key-'+str(key))
finally:e.close()
