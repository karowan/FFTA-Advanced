"""Package the verified native-art build without replacing any existing saves."""
import hashlib,json
from pathlib import Path
from native_art import ROOT,sha

EXPECTED='316a40524b960c49ad7213ac4b0bea539bfa9513'

def main():
    review=ROOT/'build/art/native-final-integration-2026-09-20'
    manifest=review/'candidate.json';meta=json.loads(manifest.read_text())
    rom=Path(meta['path']);assert meta['romSha1']==EXPECTED
    assert hashlib.sha1(rom.read_bytes()).hexdigest()==EXPECTED
    evidence=review/'evidence.json';record=json.loads(evidence.read_text())
    assert record['romSha1']==EXPECTED and record['manifestSha256']==sha(manifest.read_bytes())
    assert len(record['screenshots'])==33
    for item in record['runs']+record['reports']+record['screenshots']:
        path=ROOT/item['path'];assert sha(path.read_bytes())==item['sha256'],path
    index=json.loads((review/'save-latest.json').read_text())
    proof_path=Path(index['report']);assert sha(proof_path.read_bytes())==index['sha256']
    proof=json.loads(proof_path.read_text());assert proof['status']=='passed' and proof['romSha1']==EXPECTED
    seed=Path(proof['save']);assert sha(seed.read_bytes())==proof['saveSha256']
    protected={str(p):sha(p.read_bytes()) for base in (ROOT/'saves',ROOT/'roms/play')
               if base.exists() for p in base.rglob('*') if p.is_file()}
    release=ROOT/'build/releases/native-art-final';folder=ROOT/'saves/native-art-final-2026-09-20'
    target=release/'FFTA_Reviewed_All_Classes.gba';save=folder/'FFTA_Reviewed_All_Classes.sav'
    for path in (target,save):
        assert path.resolve().is_relative_to(ROOT.resolve())
        assert not any(p.is_symlink() for p in (path,*path.parents))
    release.mkdir(parents=True,exist_ok=True);folder.mkdir(parents=True,exist_ok=True)
    if target.exists():assert target.read_bytes()==rom.read_bytes(),'Existing release differs'
    else:
        with target.open('xb') as stream:stream.write(rom.read_bytes())
    installed=not save.exists()
    if installed:
        with save.open('xb') as stream:stream.write(seed.read_bytes())
    for path,digest in protected.items():assert sha(Path(path).read_bytes())==digest,path
    result=dict(status='verified native-art local build',rom=str(target),romSha1=EXPECTED,
        manifest=str(manifest),manifestSha256=sha(manifest.read_bytes()),
        evidence=str(evidence),evidenceSha256=sha(evidence.read_bytes()),
        saveDirectory=str(folder),save=str(save),seedInstalled=installed,
        saveReport=str(proof_path),saveReportSha256=sha(proof_path.read_bytes()),
        protectedFiles=protected,launcher='Play New Sprites.cmd')
    (release/'current.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],romSha1=EXPECTED,seedInstalled=installed,
                         protectedFiles=len(protected),save=str(save))))

if __name__=='__main__':main()
