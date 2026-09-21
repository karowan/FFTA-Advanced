import pathlib,runpy,struct,ctypes as C,json
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'build/expansion/probes/chop-game-lab'
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'));e=h['Emulator'](OUT/'frozen.gba')
samples=[]
try:
 e.load(OUT/'prepreview.state')
 for frame in range(601):
  e.run(1,256 if frame<8 else 0)
  if frame in [0,1,2,3,4,5,6,7,8,9,10,20,30,60,120,180,300,600]:
   p=OUT/f'preview-frame-{frame:03}';e.save(p.with_suffix('.state'));e.screenshot(p.with_suffix('.png'))
   ram=e.memory();p.with_suffix('.ram').write_bytes(ram);p.with_suffix('.iwram').write_bytes(C.string_at(*e.maps[0x03000000]))
   state=p.with_suffix('.state').read_bytes()
   samples.append({'frame':frame,'regs':[hex(v) for v in struct.unpack_from('<17I',state,0x20)],'context':ram[0xf3f0:0xf424].hex(),'guard':ram[0x3ff44:0x3ff50].hex()})
finally:e.close()
(OUT/'preview-frames.json').write_text(json.dumps(samples,indent=2));print(json.dumps(samples[-1],indent=2))
