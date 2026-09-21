"""Deterministic read-only capture at native execution before the failed Ward case.

A private entry loop stops both versions before any action effect. This locates
pre-execution RNG differences; it does not validate damage or alter results.
"""
import ctypes as C,hashlib,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/job-state/current.json').read_text());ROM=pathlib.Path(meta['path'])
assert hashlib.sha1(ROM.read_bytes()).hexdigest()==meta['romSha1']
OUT=ROM.parent/'ward-rng-entry';OUT.mkdir(exist_ok=True)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];observed=[]
for name in ('control','ward'):
 image=bytearray(ROM.read_bytes())
 if name=='control':
  for function,value in (('ffta_poise_factor',4),('ffta_blade_ward_factor',20)):
   p=meta['symbols'][function]-0x08000000;image[p:p+4]=bytes((value,0x20,0x70,0x47))
 image[0xa433c:0xa433e]=bytes.fromhex('fee7');path=OUT/(name+'.gba');path.write_bytes(image)
 e=E(path)
 try:
  e.load(ROM.parent/'game-352/confirmation.state');e.set_memory(0x1e98,b'\0');e.set_memory(0x3ff48,bytes(4))
  e.set_memory(0x33e4+5,bytes((116,1,116)));e.set_memory(0x33e4+0x3a,bytes((155,154)))
  e.set_memory(0x33e4+0x18,struct.pack('<4H',500,500,49,49));e.set_memory(0x33e4+0xe8,bytes((8,))+bytes(7))
  e.set_memory(0x33e4+0x2a,bytes(10));e.set_memory(0x1eb4,bytes((1 if name=='ward' else 0,)))
  C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',3),4)
  e.run(8,256);e.run(2100);e.save(OUT/(name+'.state'))
  ram=e.memory();iw=C.string_at(*e.maps[0x03000000]);(OUT/(name+'.ram')).write_bytes(ram);(OUT/(name+'.iwram')).write_bytes(iw)
  registers=struct.unpack_from('<17I',(OUT/(name+'.state')).read_bytes(),0x20)
  assert registers[15]==0x080a433e,(name,[hex(x) for x in registers])
  observed.append(dict(name=name,rng=iw[0x34b0:0x34b4].hex(),registers=list(registers),nativeFlags=ram[0x1f70:0x1f74].hex()))
 finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],observed=observed,scope=__doc__)
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
