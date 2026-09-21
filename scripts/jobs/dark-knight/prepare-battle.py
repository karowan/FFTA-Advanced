"""Create a fresh exact-ROM battle from the isolated fixed early-town save."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import hashlib,json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
meta=_load_job_candidate(ROOT/'build/expansion/probes/dark-knight/current.json')
rom=pathlib.Path(meta['path']);assert hashlib.sha1(rom.read_bytes()).hexdigest()==meta['romSha1']
subprocess.run([sys.executable,str(ROOT/'scripts/create-battle-fixture.py'),'--rom',str(rom),'--out',str(rom.parent/'fixture'),'--heap-end',hex(meta['heapEnd'])],check=True,cwd=ROOT)
