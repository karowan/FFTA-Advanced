"""Select repeatable native hit/miss fixtures without changing hit formulas."""
import pathlib,runpy,struct,ctypes as C,json
ROOT=pathlib.Path(__file__).resolve().parents[1];LAB=ROOT/'build/expansion/probes/chop-in-game'
OUT=LAB/'seeds';OUT.mkdir(exist_ok=True);h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
results=[]
for seed in range(8):
 e=h['Emulator'](LAB/'frozen.gba')
 try:
  e.load(LAB/'confirmation.state');C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4)
  e.run(8,256);e.run(1200);r=e.memory();e.screenshot(OUT/f'{seed}-result.png');e.save(OUT/f'{seed}-result.state')
  (OUT/f'{seed}-result.ram').write_bytes(r);(OUT/f'{seed}-result.iwram').write_bytes(C.string_at(*e.maps[0x03000000]))
  result={'seed':seed,'targetHP':struct.unpack_from('<H',r,0x33fc)[0],'actorHP':struct.unpack_from('<H',r,0x98)[0],
          'targetXY':list(r[0x34da:0x34dc]),'actorEXP':r[0x8a]}
  results.append(result);print(json.dumps(result),flush=True)
  if any(x['targetHP']<27 for x in results) and any(x['targetHP']==27 for x in results):break
 finally:e.close()
(OUT/'report.json').write_text(json.dumps(results,indent=2))
