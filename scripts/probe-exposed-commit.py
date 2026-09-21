"""Disposable captured Fight callback breakpoints for incoming review."""
import ctypes as C,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'build/expansion/probes/exposed-effects/69a844aee6a536f29e2b00959acce62de1658e27'
base=(OUT/'isolated.gba').read_bytes();h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
for site in (0xa2914,0xa2946,0xa2210,0xa300a):
 image=bytearray(base);image[site:site+2]=b'\xfe\xe7';rom=OUT/f'break-{site:x}.gba';rom.write_bytes(image)
 e=h['Emulator'](rom)
 try:
  e.load(ROOT/'build/expansion/probes/exposed-storage/current/69a844aee6a536f29e2b00959acce62de1658e27/battle/battle-ready.state')
  e.run(1);e.set_memory(0x33e4+0x18,struct.pack('<HH',250,250))
  e.set_memory(0x1e98,bytes([0x0a])*36)
  for key in [256,128,128,128,256,256,256,128,256,256,256]:
   e.run(8,key);e.run(600)
  e.run(1200)
  e.save(OUT/f'break-{site:x}.state');ram=e.memory();iw=C.string_at(*e.maps[0x03000000])
  (OUT/f'break-{site:x}.ram').write_bytes(ram);(OUT/f'break-{site:x}.iwram').write_bytes(iw)
  regs=struct.unpack_from('<17I',(OUT/f'break-{site:x}.state').read_bytes(),0x20)
  print(hex(site),[hex(x) for x in regs], [hex(x) for x in struct.unpack_from('<4I',ram,0xf3f0)])
 finally:e.close()
