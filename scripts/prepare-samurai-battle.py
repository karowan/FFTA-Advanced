"""Generate a fresh matching private Samurai battle without a testing agent."""
import hashlib,json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text());rom=pathlib.Path(meta['path'])
assert hashlib.sha1(rom.read_bytes()).hexdigest()==meta['romSha1']
subprocess.run([sys.executable,str(ROOT/'scripts/create-battle-fixture.py'),'--rom',str(rom),'--out',str(rom.parent/'fixture')],cwd=ROOT,check=True)
