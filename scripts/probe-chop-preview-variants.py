"""Diagnostic ROM/state cross-load only, never an acceptance fixture."""
import pathlib,runpy,struct,json,ctypes as C
ROOT=pathlib.Path(__file__).resolve().parents[1];LAB=ROOT/'build/expansion/probes/chop-game-lab'
OUT=LAB/'variants';OUT.mkdir(exist_ok=True)
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
original=(LAB/'frozen.gba').read_bytes();clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();rows=[]
for variant in ['baseline','native-callbacks','native-all-combat','selected-rush','chop-rush-name']:
 rom=bytearray(original)
 if variant in ['native-callbacks','native-all-combat']:
  struct.pack_into('<I',rom,0x3a8604+8*4,0x08130a95)
  struct.pack_into('<I',rom,0x3a86f8+30*4,0x0813189d)
 if variant=='native-all-combat':
  for lo,hi in [(0x1300e2,0x1300f2),(0x130654,0x130660),(0x130688,0x130694)]:rom[lo:hi]=clean[lo:hi]
 if variant=='chop-rush-name':
  table=struct.unpack_from('<I',rom,0xccd84)[0]-0x08000000
  rom[table+423*28:table+423*28+2]=clean[0x55187c+112*28:0x55187c+112*28+2]
 path=OUT/(variant+'.gba');path.write_bytes(rom);e=h['Emulator'](path)
 try:
  e.load(LAB/'prepreview.state')
  if variant=='selected-rush':
   context=struct.unpack_from('<I',e.memory(),0xf438)[0]-0x02000000;e.set_memory(context+0x14,struct.pack('<H',112))
  e.run(8,256);e.run(172);e.screenshot(OUT/(variant+'.png'));e.save(OUT/(variant+'.state'))
  ram=e.memory();(OUT/(variant+'.ram')).write_bytes(ram);(OUT/(variant+'.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
  state=(OUT/(variant+'.state')).read_bytes();rows.append({'variant':variant,'pc':hex(struct.unpack_from('<I',state,0x5c)[0]),'context':ram[0xf3f0:0xf424].hex()})
 finally:e.close()
(OUT/'report.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
