"""Disposable native job-menu investigation. Not an acceptance test."""
import ctypes as C,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
OUT=ROOT/'build/expansion/probes/job-wheel-lab';OUT.mkdir(exist_ok=True)
ROM=OUT/'frozen.gba'
resume='--resume' in sys.argv
if not resume:ROM.write_bytes((OUT.parent/'job-ui.gba').read_bytes())
e=h['Emulator'](ROM)
def tap(key,wait=180):e.run(8,key);e.run(wait)
try:
 if resume:e.load(OUT/'current.state')
 else:
  e.set_memory(0,(ROOT/'build/test-lab/early-town.sav').read_bytes(),0);e.run(3600)
  for key,wait in [(8,180),(256,60),(256,60),(256,180)]:tap(key,wait)
 if '--unlock' in sys.argv:
  ram=e.memory()
  for i in range(24):
   p=0x80+i*264;race=ram[p+6]
   if ram[p+4] and 1<=race<=5:
    count=[0,142,111,124,118,116][race]
    e.set_memory(p+0x40,bytes([100])*count)
    if race==1:e.set_memory(0x1b40+i*34,bytes([100])*34)
 if '--keys' in sys.argv:
  for spec in sys.argv[sys.argv.index('--keys')+1].split(','):
   key,*wait=spec.split(':');tap(int(key),int(wait[0]) if wait else 180)
 e.save(OUT/'current.state');e.screenshot(OUT/'current.png')
 ram=e.memory();(OUT/'current.ram').write_bytes(ram);iw=C.string_at(*e.maps[0x03000000]);(OUT/'current.iwram').write_bytes(iw)
 menu=struct.unpack_from('<I',iw,0x2818)[0]
 result={'romSha1':hashlib.sha1(ROM.read_bytes()).hexdigest(),'menu':hex(menu)}
 if 0x02000000<=menu<0x02038000:
  p=menu-0x02000000
  result.update(state=ram[p+0x1258],wheelCount=struct.unpack_from('<I',ram,p+0x1270)[0],wheelIds=list(ram[p+0x1278:p+0x1284]),timer=ram[p+0x25])
 print(json.dumps(result,indent=2))
finally:e.close()
