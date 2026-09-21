"""Disposable native combo UI discovery; not a completed acceptance test."""
import ctypes as C,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
FIX=ROOT/'build/expansion/probes/battle-fixture'
OUT=ROOT/'build/expansion/probes/combo-ui-lab';OUT.mkdir(exist_ok=True)
rom=(FIX/'frozen.gba').read_bytes();ROM=OUT/'frozen.gba';ROM.write_bytes(rom)
(OUT/'initial.state').write_bytes((FIX/'battle-ready.state').read_bytes())
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
def tap(e,k,wait=180):e.run(8,k);e.run(wait)
def capture(e,label):
 e.screenshot(OUT/(label+'.png'));e.save(OUT/(label+'.state'))
 (OUT/(label+'.ram')).write_bytes(e.memory())
 print(label,hex(struct.unpack_from('<I',e.memory(),0xf438)[0]),flush=True)
e=h['Emulator'](ROM)
try:
 e.load(OUT/'initial.state');e.run(1)
 e.set_memory(0x398+5,b'\x76');e.set_memory(0x398+7,b'\x76')
 e.set_memory(0x398+0x35,b'\x76');e.set_memory(0x398+0x3c,b'\x68')
 e.set_memory(0x398+0x40+104,b'\x8a')
 e.set_memory(0x398+0xd6,struct.pack('<H',10))
 e.set_memory(0x398+0x2a,struct.pack('<5H',453,0,0,0,0))
 capture(e,'seeded')
 tap(e,32);tap(e,256);capture(e,'action-menu')
 for n in range(3):tap(e,32);capture(e,f'menu-down-{n}')
 tap(e,256);capture(e,'combo-targeting')
 tap(e,128);capture(e,'combo-target')
 tap(e,256);capture(e,'combo-preview')
 tap(e,256);capture(e,'combo-confirmation')
 tap(e,256,1800);capture(e,'combo-executed')
finally:e.close()
