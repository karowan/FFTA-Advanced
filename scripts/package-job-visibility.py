"""Authenticate visibility acceptance, then publish the generic BPS release."""
import argparse, hashlib, json
from pathlib import Path
from mod_release import publish
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--config',type=Path,default=ROOT/'scripts/mod-release.json');a=p.parse_args()
    run=json.loads(a.run.read_text());assert run['status']=='passed' and run['inputsUnchanged']
    ids={'build-job-visibility','test-job-visibility','test-job-visibility-save'}
    assert {s['id'] for s in run['steps']}==ids and all(s['status']=='passed' for s in run['steps'])
    build=next(s for s in run['steps'] if s['id']=='build-job-visibility')
    build_entry=json.loads(Path(build['log']).read_text().splitlines()[-1])
    path=Path(build_entry['manifest'])
    meta=json.loads(path.read_text());rom=Path(meta['path']).read_bytes();digest=hashlib.sha1(rom).hexdigest()
    assert digest==meta['romSha1']==build_entry['romSha1']
    assert sha(ROOT/'src/engine/job-wheel.c')==meta['jobVisibility']['sourceSha256']
    evidence=[]
    for step in run['steps']:
        log=Path(step['log']);entry=json.loads(log.read_text().splitlines()[-1])
        assert entry['status']=='passed' and entry['romSha1']==digest
        report=Path(entry.get('report',entry.get('manifest')))
        assert report.is_relative_to(path.parent)
        if 'report' in entry:
            proof=json.loads(report.read_text());assert proof['status']=='passed' and proof['romSha1']==digest
        evidence.append(dict(id=step['id'],path=str(report),sha256=sha(report),log=str(log),logSha256=sha(log)))
    protected={str(f):sha(f) for base in (ROOT/'saves',ROOT/'roms/play',ROOT/'build/releases/approved-first-pass',ROOT/'build/releases/native-art-final') for f in base.rglob('*') if f.is_file()}
    package=publish(meta,a.run,evidence,a.config)
    for f,d in protected.items():assert sha(Path(f))==d,f
    package.update(run=str(a.run.resolve()),runSha256=sha(a.run),reports=evidence,protectedFiles=protected)
    receipt=Path(package['archive']).parent/'local-build-receipt.json'
    receipt.write_text(json.dumps(package,indent=2)+'\n')
    print(json.dumps(dict(status='passed',romSha1=digest,protectedFiles=len(protected),archive=package['archive'],archiveBytes=package['archiveBytes'],patchBytes=package['patchBytes'],report=str(receipt))))
if __name__=='__main__':main()
