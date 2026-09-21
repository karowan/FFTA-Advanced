"""Capture an exact-candidate native executor entry from fixed battle inputs."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ctypes as C,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
from native_battle_wrappers import fixed_giza_formation
meta=_load_job_candidate(ROOT/'build/expansion/probes/viking/current.json');ROM=pathlib.Path(meta['path'])
source=ROM.read_bytes();sha=lambda b:hashlib.sha1(b).hexdigest();assert sha(source)==meta['romSha1']
fixture=ROM.parent/'fixture';assert (fixture/'frozen.gba').read_bytes()==source
out=ROM.parent/'executor';out.mkdir(exist_ok=True)
inputs_hashes={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [pathlib.Path(__file__),ROOT/'scripts/native_battle_wrappers.py',ROOT/'scripts/emulator-test.py',ROOT/'scripts/battle-menu-observation.py',ROOT/'scripts/fixtures/native-turn-menu.json',fixture/'battle-ready.state',fixture/'battle-ready.ram',fixture/'battle-ready.iwram']}
if (out/'manifest.json').exists():
 cached=json.loads((out/'manifest.json').read_text())
 if cached.get('inputsHashes')==inputs_hashes and cached['romSha1']==meta['romSha1'] and all((out/n).is_file() and sha((out/n).read_bytes())==v for n,v in cached['files'].items()):
  print(json.dumps(dict(passed=True,reused=True,romSha1=meta['romSha1'],evidence=str(out/'manifest.json'))));sys.exit(0)
image=bytearray(source);image[0xa433c:0xa433e]=bytes.fromhex('fee7');trap=out/'entry-trap.gba';trap.write_bytes(image)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];e=E(trap)
observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
inputs=[256,128,128,128,256,256,256,128,256,256,256]
try:
 e.load(fixture/'battle-ready.state');e.run(1);fixed_giza_formation(source,e)
 e.set_memory(0x33fc,struct.pack('<HH',250,250));e.set_memory(0x1e98,bytes(36));e.set_memory(0x3ff44,bytes(8)+b'\xd7'*0xb4)
 for step,key in enumerate(inputs):
  e.run(8,key);e.run(180)
  # Moving can still be animating at180 frames. Wait for the actual command
  # menu before Act instead of losing an input to the movement transition.
  if step==4:observe['wait_for_menu'](e)
 e.save(out/'execute-trap.state');(out/'execute-trap.ram').write_bytes(e.memory());(out/'execute-trap.iwram').write_bytes(C.string_at(*e.maps[0x03000000]))
 registers=struct.unpack_from('<17I',(out/'execute-trap.state').read_bytes(),0x20)
 assert registers[15]==0x080a433e,('Native executor entry not reached',[hex(x) for x in registers])
finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],trapSha1=sha(image),heapEnd=meta['heapEnd'],inputs=inputs,inputsHashes=inputs_hashes,
 files={p.name:sha(p.read_bytes()) for p in out.glob('execute-trap.*')})
(out/'manifest.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
