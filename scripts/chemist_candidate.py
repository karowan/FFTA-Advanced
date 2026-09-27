"""Resolve the exact candidate selected by the deterministic test plan."""
import hashlib,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def candidate():
 p=Path(os.environ.get('FFTA_TEST_CANDIDATE_MANIFEST',ROOT/'build/expansion/chemist-progressions/help/current.json'))
 m=json.loads(p.read_text())
 if 'manifest' in m:m=json.loads(Path(m['manifest']).read_text())
 assert hashlib.sha1(Path(m['path']).read_bytes()).hexdigest()==m['romSha1']
 return m
