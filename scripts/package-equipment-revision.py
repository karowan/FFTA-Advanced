"""Authenticate equipment-revision acceptance, then publish the generic BPS release."""
import argparse, hashlib, json
from pathlib import Path
from mod_release import publish
ROOT=Path(__file__).resolve().parents[1]
STEPS=('build-teaching-rows','build-equipment-revision','test-equipment-revision',
       'test-revision-teaching-rows','test-revision-teaching-rows-ui')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def last(log):return json.loads(Path(log).read_text().splitlines()[-1])
def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--config',type=Path,default=ROOT/'scripts/mod-release.json');a=p.parse_args()
    run=json.loads(a.run.read_text());assert run['status']=='passed' and run['inputsUnchanged']
    assert tuple(s['id'] for s in run['steps'])==STEPS and all(s['status']=='passed' for s in run['steps'])
    steps={s['id']:s for s in run['steps']}
    rows=last(steps['build-teaching-rows']['log']);built=last(steps['build-equipment-revision']['log'])
    path=Path(built['manifest']);meta=json.loads(path.read_text())
    rom=Path(meta['path']).read_bytes();digest=hashlib.sha1(rom).hexdigest()
    assert digest==meta['romSha1']==built['romSha1']
    # The revision is built on the teaching-row candidate produced in this run.
    revision=meta['equipmentRevision'];assert Path(revision['parent'])==Path(rows['manifest'])
    assert revision['baseSha1']==rows['romSha1']
    rows_meta=json.loads(Path(rows['manifest']).read_text())
    for source,digest_expected in rows_meta['teachingRows']['sourceSha256'].items():
        assert sha(ROOT/source)==digest_expected,source
    assert sha(ROOT/'src/ability-display-names.mjs')==revision['compactNamesSha256']
    assert sha(ROOT/'notes/equipment-acquisition.json')==revision['designSha256']
    evidence=[]
    for step in run['steps']:
        entry=last(step['log']);assert entry['status']=='passed'
        report=Path(entry.get('report',entry.get('manifest')))
        if step['id']=='build-teaching-rows':
            assert entry['romSha1']==revision['baseSha1'] and report==Path(rows['manifest'])
        else:
            assert entry['romSha1']==digest and report.is_relative_to(path.parent)
        if 'report' in entry:
            proof=json.loads(report.read_text());assert proof['status']=='passed' and proof['romSha1']==entry['romSha1']
        evidence.append(dict(id=step['id'],path=str(report),sha256=sha(report),log=str(step['log']),logSha256=sha(Path(step['log']))))
    protected={str(f):sha(f) for base in (ROOT/'saves/native-art-final-2026-09-20',ROOT/'roms/play',ROOT/'build/releases/approved-first-pass',ROOT/'build/releases/native-art-final')
               if base.exists() for f in base.rglob('*') if f.is_file()}
    package=publish(meta,a.run,evidence,a.config)
    for f,d in protected.items():assert sha(Path(f))==d,f
    package.update(run=str(a.run.resolve()),runSha256=sha(a.run),reports=evidence,protectedFiles=protected)
    receipt=Path(package['archive']).parent/'local-build-receipt.json'
    receipt.write_text(json.dumps(package,indent=2)+'\n')
    print(json.dumps(dict(status='passed',romSha1=digest,protectedFiles=len(protected),archive=package['archive'],archiveBytes=package['archiveBytes'],patchBytes=package['patchBytes'],report=str(receipt))))
if __name__=='__main__':main()
