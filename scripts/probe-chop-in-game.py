"""Disposable native UI investigation for the first combat slice."""
import ctypes as C,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
OUT=ROOT/'build/expansion/probes/chop-game-lab';OUT.mkdir(exist_ok=True)
FIX=OUT.parent/'battle-fixture';ROM=OUT/'frozen.gba'
resume='--resume' in sys.argv
if not resume:ROM.write_bytes((FIX/'frozen.gba').read_bytes())
e=h['Emulator'](ROM)
def tap(key,wait=180):e.run(8,key);e.run(wait)
try:
 e.load(OUT/'current.state' if resume else FIX/'battle-ready.state');e.run(1)
 if '--axe' in sys.argv:
  e.set_memory(0x80+0x2a,struct.pack('<H',453));e.set_memory(0x80+0x2e,b'\x00\x00');e.set_memory(0x1b40+28,b'\xe4')
 if '--keys' in sys.argv:
  for spec in sys.argv[sys.argv.index('--keys')+1].split(','):
   key,*wait=spec.split(':');tap(int(key),int(wait[0]) if wait else 180)
 e.save(OUT/'current.state');e.screenshot(OUT/'current.png')
 ram=e.memory();(OUT/'current.ram').write_bytes(ram);iw=C.string_at(*e.maps[0x03000000]);(OUT/'current.iwram').write_bytes(iw)
 def word(offset):return struct.unpack_from('<I',ram,offset)[0]
 def inside(p):return 0x02000000<=p<0x0203ff00
 result={'romSha1':hashlib.sha1(ROM.read_bytes()).hexdigest(),'battleContext':hex(word(0xf438)),
         'party':[{'ptr':hex(0x02000080+i*264),'job':ram[0x80+i*264+5],
                   'xy':list(ram[0x80+i*264+0xf6:0x80+i*264+0xf8])} for i in range(6)]}
 if inside(word(0xf438)):result['contextWords']=[hex(word(word(0xf438)-0x02000000+i)) for i in range(0,48,4)]
 print(json.dumps(result,indent=2))
finally:e.close()
