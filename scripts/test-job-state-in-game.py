"""Native save/footer transport, legacy import and corrupt-footer rejection."""
import hashlib,json,pathlib,runpy,struct,subprocess,sys,zlib
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'build/expansion/probes'
meta=json.loads((P/'job-state/current.json').read_text());ROM=pathlib.Path(meta['path']);OUT=ROM.parent/'save-tests';OUT.mkdir(exist_ok=True)
assert hashlib.sha1(ROM.read_bytes()).hexdigest()==meta['romSha1']
fixture=ROM.parent/'fixture'
subprocess.run([sys.executable,str(ROOT/'scripts/create-battle-fixture.py'),'--rom',str(ROM),
 '--out',str(fixture),'--heap-end',hex(meta['heapEnd'])],cwd=ROOT,check=True)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];menu=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
payload=bytes((i*37+11)&255 for i in range(792));bank=0x3f400;checks=0
def check(ok,detail):
 global checks
 checks+=1;assert ok,detail
def tap(e,k,wait=180):e.run(8,k);e.run(wait)
e=E(ROM)
try:
 e.load(fixture/'battle-ready.state');e.run(1)
 check(e.memory()[bank:bank+4]==struct.pack('<I',0x32534a46),'Native legacy load did not initialize bank')
 check(e.memory()[bank+16:bank+808]==bytes(792),'Legacy state did not start clear')
 e.set_memory(bank+16,payload);before=e.memory();old=e.memory(0)
 for k in (1,8,16,256,256):tap(e,k)
 tap(e,256,300);saved=e.memory(0);after=e.memory()
 check(saved!=old,'Native suspend flash did not change')
 check(after[bank+16:bank+808]==payload,'Save mutated live records')
 check(after[0x1f04:0x1f08]==before[0x1f04:0x1f08],'Save failed to restore marker')
 (OUT/'suspended.sav').write_bytes(saved);e.save(OUT/'saved.state')
finally:e.close()
sectors=[i for i in range(16) if saved[i*4096+0xca8:i*4096+0xcb0]==b'FFTAJS02']
check(len(sectors)==1,('footer sector count',sectors))
footer=sectors[0]*4096+0xca8
check(saved[footer+32:footer+824]==payload,'Serialized payload differs')
def resume(e,data):
 e.set_memory(0,data,0);e.run(3600)
 for k,wait in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):tap(e,k,wait)
e=E(ROM)
try:
 resume(e,saved);menu['wait_for_menu'](e,limit=9000);actual=e.memory()
 check(actual[bank+16:bank+808]==payload,'Cold resume lost the job records')
 check(actual[0x1940:0x1e70]==after[0x1940:0x1e70],'Inventory/AP/prefs changed')
 e.save(OUT/'resumed.state');(OUT/'resumed.ram').write_bytes(actual)
finally:e.close()
# Independent schema1 input in the real native flash transaction. The footer
# lies beyond the native payload CRC, so the original native pages remain exact.
legacy_payload=bytes((i*29+3)&255 for i in range(576))
legacy=bytearray(608);legacy[:8]=b'FFTAJS01';legacy[8:11]=bytes((1,16,36))
legacy[12:16]=saved[footer+12:footer+16];struct.pack_into('<I',legacy,20,576)
legacy[32:]=legacy_payload;struct.pack_into('<I',legacy,16,zlib.crc32(legacy))
legacy_flash=bytearray(saved);legacy_flash[footer:footer+608]=legacy
expected=bytearray(792)
for i in range(36):
 for j in range(15):
  if j!=3:expected[i*22+j]=legacy_payload[i*16+j]
e=E(ROM)
try:
 resume(e,bytes(legacy_flash));menu['wait_for_menu'](e,limit=9000);actual=e.memory()
 check(actual[bank+16:bank+808]==bytes(expected),'Native legacy migration lost assigned state or activated new fields')
 check(actual[0x1940:0x1e70]==after[0x1940:0x1e70],'Legacy migration changed inventory/AP/prefs')
 (OUT/'legacy-input.sav').write_bytes(legacy_flash);e.save(OUT/'legacy-resumed.state')
finally:e.close()
broken=bytearray(saved);broken[footer+49]^=0x80
e=E(ROM)
try:
 e.set_memory(0,bytes(broken),0);e.run(3600)
 sentinel=bytes((i*13+9)&255 for i in range(808));e.set_memory(bank,sentinel)
 for k,wait in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):tap(e,k,wait)
 check(e.memory()[bank:bank+808]==sentinel,'Corrupt footer published or reset live state')
 check(e.memory()[0x1f04:0x1f08]!=b'JST1','Corrupt load published native state')
 e.save(OUT/'rejected.state')
finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],checks=checks,footerSector=sectors[0],
 scope='Fresh native battle with1KiB additional heap reserve; legacy initialization, Save Now, schema2 cold resume, schema1 cold migration and corrupt-footer rejection. Copy/job effects pending.')
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
