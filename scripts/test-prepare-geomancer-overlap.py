"""Reproducible two-Nu-Mou clan input followed by native battle construction."""
import hashlib,json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
rom=pathlib.Path(meta['path']);sha=lambda p:hashlib.sha1(p.read_bytes()).hexdigest()
assert sha(rom)==meta['romSha1']
out=rom.parent/'fixture-two-geomancers';cache=out/'prepare-cache.json'
profile=ROOT/'scripts/fixtures/two-geomancers.json'
files=[pathlib.Path(__file__),profile,ROOT/'build/expansion/registry.json',ROOT/'build/test-lab/early-town.sav',
 *[ROOT/'scripts'/name for name in ('create-battle-fixture.py','emulator-test.py','battle-menu-observation.py',
 'test-battle-inventory.py','probe-ap-copy-heap.py','fixtures/native-turn-menu.json')]]
inputs=dict(romSha1=meta['romSha1'],heapEnd=meta['heapEnd'],files={str(p.relative_to(ROOT)):sha(p) for p in files})
if cache.exists():
 proof=json.loads(cache.read_text())
 if proof['inputs']==inputs and all((out/n).is_file() and sha(out/n)==v for n,v in proof['outputs'].items()):
  print(json.dumps(dict(passed=True,reused=True,romSha1=meta['romSha1'],cache=str(cache))));sys.exit(0)
subprocess.run([sys.executable,str(ROOT/'scripts/create-battle-fixture.py'),'--rom',str(rom),'--out',str(out),
 '--heap-end',hex(meta['heapEnd']),'--party-profile',str(profile)],cwd=ROOT,check=True)
cache.write_text(json.dumps(dict(inputs=inputs,outputs={n:sha(out/n) for n in
 ('frozen.gba','battle-ready.state','battle-ready.ram','battle-ready.iwram','report.json')}),indent=2),encoding='utf-8')
