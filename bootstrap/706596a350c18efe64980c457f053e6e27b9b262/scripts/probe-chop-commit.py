import pathlib,runpy,ctypes as C,struct,json
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'build/expansion/probes/chop-in-game'
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'));e=h['Emulator'](OUT/'frozen.gba')
def photo(name):
 e.screenshot(OUT/(name+'.png'));e.save(OUT/(name+'.state'));r=e.memory()
 (OUT/(name+'.ram')).write_bytes(r);(OUT/(name+'.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
 print(name,{'actorHP':struct.unpack_from('<H',r,0x98)[0],'actorXY':list(r[0x176:0x178]),
             'targetHP':struct.unpack_from('<H',r,0x33fc)[0],'targetXY':list(r[0x34da:0x34dc]),'exp':r[0x8a]})
try:
 e.load(OUT/'preview.state');e.run(8,256);e.run(180);photo('confirmation')
 e.run(8,256)
 for frame in range(0,720,12):
  e.run(12)
  if frame%24==0:e.screenshot(OUT/f'commit-frame-{frame:03}.png')
 e.run(600);photo('executed')
finally:e.close()
