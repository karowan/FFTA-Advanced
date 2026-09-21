"""Run a declared original job scenario against the actual integrated image."""
import hashlib
import json
import os
import pathlib
import runpy
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
assert len(sys.argv)==2,'Supply one declared workspace job check'
script=(ROOT/sys.argv[1]).resolve()
assert script.is_relative_to(ROOT/'scripts/jobs') and script.suffix=='.py'
manifest=ROOT/'build/expansion/probes/integrated-jobs/current.json'
candidate=json.loads(manifest.read_text())
assert hashlib.sha1(pathlib.Path(candidate['path']).read_bytes()).hexdigest()==candidate['romSha1']
os.environ['FFTA_TEST_CANDIDATE']=str(manifest)
sys.argv=[str(script)]
print(json.dumps(dict(script=str(script.relative_to(ROOT)),candidate=candidate['romSha1']),sort_keys=True),flush=True)
runpy.run_path(str(script),run_name='__main__')
