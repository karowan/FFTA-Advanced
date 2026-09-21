"""Reuse a verified exact-base native executor fixture, with explicit hashes."""
import hashlib,json,pathlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'build/expansion/probes'
meta=json.loads((P/'samurai/current.json').read_text());source=P/'fell-main'/meta['baseSha1']
sha=lambda p:hashlib.sha1(p.read_bytes()).hexdigest()
assert sha(source/'fell.gba')==meta['baseSha1']
proof=json.loads((source/'executor-report.json').read_text())
assert proof['passed'] and proof['romSha1']==meta['baseSha1'] and proof['checks']==357
out=P/'samurai-state'/meta['baseSha1'];out.mkdir(parents=True,exist_ok=True)
files={}
for suffix in ('state','ram','iwram'):
 src=source/f'executor-capture.{suffix}';dst=out/f'execute-trap.{suffix}'
 shutil.copyfile(src,dst);files[dst.name]=sha(dst)
(out/'executor-fixture.json').write_text(json.dumps(dict(baseSha1=meta['baseSha1'],source=str(source),files=files),indent=2))
print(json.dumps(dict(passed=True,baseSha1=meta['baseSha1'],files=files)))
