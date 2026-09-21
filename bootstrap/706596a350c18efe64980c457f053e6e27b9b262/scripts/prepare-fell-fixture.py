"""Generate a matching disposable battle for the current private Fell build."""
import hashlib,json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
from fell_test_context import load_context
meta=load_context('--current' in sys.argv)
rom=pathlib.Path(meta['path'])
assert hashlib.sha1(rom.read_bytes()).hexdigest()==meta['romSha1']
subprocess.run([sys.executable,str(ROOT/'scripts/create-battle-fixture.py'),
               '--rom',str(rom),'--out',str(rom.parent/'fixture')],cwd=ROOT,check=True)
