"""Create a fresh exact-candidate Viking battle with the fixed native script."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import hashlib,json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
meta=_load_job_candidate(ROOT/'build/expansion/probes/viking/current.json');rom=pathlib.Path(meta['path'])
assert hashlib.sha1(rom.read_bytes()).hexdigest()==meta['romSha1']
fixture=rom.parent/'fixture';cache=fixture/'prepare-cache.json';sha=lambda p:hashlib.sha1(p.read_bytes()).hexdigest()
inputs=dict(romSha1=meta['romSha1'],heapEnd=meta['heapEnd'],files={str(p.relative_to(ROOT)):sha(p) for p in [pathlib.Path(__file__),*[ROOT/'scripts'/n for n in ('create-battle-fixture.py','emulator-test.py','battle-menu-observation.py','test-battle-inventory.py','probe-ap-copy-heap.py','fixtures/native-turn-menu.json')],ROOT/'build/test-lab/early-town.sav']})
if cache.exists():
 proof=json.loads(cache.read_text())
 if proof['inputs']==inputs and all((fixture/n).is_file() and sha(fixture/n)==value for n,value in proof['outputs'].items()):
  print(json.dumps(dict(passed=True,reused=True,romSha1=meta['romSha1'],evidence=str(cache))));sys.exit(0)
subprocess.run([sys.executable,str(ROOT/'scripts/create-battle-fixture.py'),'--rom',str(rom),'--out',str(rom.parent/'fixture'),'--heap-end',hex(meta['heapEnd'])],cwd=ROOT,check=True)
cache.write_text(json.dumps(dict(inputs=inputs,outputs={n:sha(fixture/n) for n in ('frozen.gba','battle-ready.state','battle-ready.ram','battle-ready.iwram','report.json')}),indent=2))
