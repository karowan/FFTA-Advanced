"""Diagnostic private Exposed/Centered icons alongside native battle sprites."""
import pathlib,json,runpy,ctypes as C,hashlib,struct
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'build/expansion/probes';meta=json.loads((P/'status-display/private/current.json').read_text());ROM=pathlib.Path(meta['path']);OUT=ROM.parent/'visual';OUT.mkdir(exist_ok=True)
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'));e=h['Emulator'](ROM)
try:
 fixture=ROM.parent/'fixture'
 assert hashlib.sha1((fixture/'frozen.gba').read_bytes()).hexdigest()==meta['romSha1']
 e.load(fixture/'battle-ready.state');e.set_memory(0x1e98,b'\x04');e.set_memory(0x1e9b,b'\x01')
 r=e.memory();owner=struct.unpack_from('<I',r,0x22874+0x80)[0]-0x02000000;pool=struct.unpack_from('<I',r,owner+8)[0]-0x02000000
 assert struct.unpack_from('<4H',r,pool+12)==(0,0x120,0x1e4,0x400)
 for i in range(16):
  e.run(20);e.screenshot(OUT/f'{i:02}.png');e.save(OUT/f'{i:02}.state');(OUT/f'{i:02}.ram').write_bytes(e.memory());(OUT/f'{i:02}.vram').write_bytes(C.string_at(*e.maps[0x06000000]))
 print(str(OUT))
finally:e.close()
