"""Fixed Counter breakpoint at the Poise factor for the Samurai recipient."""
import ctypes as C,hashlib,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1];meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text());ROM=pathlib.Path(meta['path']);LAB=ROM.parent;OUT=LAB/'poise-counter-trace';OUT.mkdir(exist_ok=True)
proof=json.loads((LAB/'game-report.json').read_text());assert proof['passed'] and proof['romSha1']==meta['romSha1']
rom=bytearray(ROM.read_bytes());entry=meta['symbols']['ffta_poise_factor'];p=entry-0x08000000
# Only stop on the Samurai or its native copies. The unrelated enemy has no
# Poise and gets the neutral factor4. This diagnostic is not gameplay proof.
rom[p:p+12]=bytes.fromhex('c179742900d1fee704207047');path=OUT/'breakpoint.gba';path.write_bytes(rom)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];e=E(path)
try:
 e.load(LAB/'game-352/confirmation.state');e.set_memory(0x80+0x3b,bytes([154]));e.set_memory(0x1b4a,b'\xff');e.set_memory(0x1e98,b'\x00');e.set_memory(0x80+0xe8,b'\x00');e.set_memory(0x80+0xeb,b'\x00');e.set_memory(0x98,struct.pack('<HH',500,500));e.set_memory(0x3ff48,bytes(4))
 e.set_memory(0x33e4+5,bytes((16,2,16)));e.set_memory(0x33e4+0x3a,bytes([53]));e.set_memory(0x33e4+0x40+53,b'\xff');e.set_memory(0x33e4+0x2a,struct.pack('<5H',460,0,0,0,0))
 C.memmove(e.maps[0x03000000][0]+0x34b0,bytes(4),4);e.run(8,256);e.run(3000)
 e.save(OUT/'counter.state');r=e.memory();(OUT/'counter.ram').write_bytes(r);iw=C.string_at(*e.maps[0x03000000]);(OUT/'counter.iwram').write_bytes(iw)
 regs=struct.unpack_from('<17I',(OUT/'counter.state').read_bytes(),0x20);assert regs[15]==entry+8,[hex(v) for v in regs]
 root=struct.unpack_from('<I',r,0x3ff48)[0];report=dict(passed=True,romSha1=meta['romSha1'],registers=[hex(v) for v in regs],root=hex(root),snapshot=iw[root-0x03000000:root-0x03000000+528].hex() if 0x03000000<=root<0x03008000 else None)
 (OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
finally:e.close()
