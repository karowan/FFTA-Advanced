"""Cold native deployment of both jobs; no patched allocation or battle output.

The shared deterministic fixture builder supplies only the declared clan
loadout before the native battle manager and graphics are constructed.
"""
import ctypes as C,hashlib,json,runpy,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from chemist_candidate import candidate
meta=candidate()
rom=Path(meta['path']);assert hashlib.sha1(rom.read_bytes()).hexdigest()==meta['romSha1']
if '--trace-exception' in sys.argv:
 E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];e=E(rom)
 folder=rom.parent/'fixture';source=folder/'deployment-confirm.state'
 try:
  e.load(source);n=e.core.retro_serialize_size();buffer=C.create_string_buffer(n)
  def state():
   assert e.core.retro_serialize(buffer,n)
   return buffer.raw
  before=state()
  for frame in range(1800):
   e.run(1,256 if frame<8 else 0);after=state()
   if struct.unpack_from('<I',after,0x60)[0]&31==27:
    (folder/'pre-exception.state').write_bytes(before);(folder/'exception.state').write_bytes(after)
    (folder/'exception.ram').write_bytes(e.memory());(folder/'exception.iwram').write_bytes(C.string_at(*e.maps[0x03000000]))
    report=dict(romSha1=meta['romSha1'],frame=frame,before=[hex(x) for x in struct.unpack_from('<68I',before,0x20)],after=[hex(x) for x in struct.unpack_from('<68I',after,0x20)])
    (folder/'exception.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));break
   before=after
  else:raise AssertionError('No exception in declared bound')
 finally:e.close()
 sys.exit(0)
subprocess.run([sys.executable,str(ROOT/'scripts/create-battle-fixture.py'),'--rom',str(rom),
 '--out',str(rom.parent/'fixture'),'--heap-end','0x0203f000','--chemist-progression','--confirm-pub-exit',
 '--party-profile','scripts/fixtures/chemist-progressions.json'],cwd=ROOT,check=True)
