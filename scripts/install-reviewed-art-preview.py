"""Prepare an isolated local art preview from the verified showcase save.

Does not replace the engineering release, import player progress, overwrite a
preview save, launch software, or claim final performance acceptance.
"""
import argparse,hashlib,json
from pathlib import Path
from native_art import ROOT,sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--native',action='store_true');args=parser.parse_args()
    meta_path=ROOT/'build/art/reviewed-integration'/('native-complete-candidate.json' if args.native else 'complete-candidate.json');meta=json.loads(meta_path.read_text())
    assert meta['romSha1']==('e11b2603b93f7b74cbe497291af22cd9a3f9f468' if args.native else '3db563a978a17ae517a5c2b4e7b39dd00b1c2fb7')
    assert hashlib.sha1(Path(meta['path']).read_bytes()).hexdigest()==meta['romSha1']
    index=json.loads((ROOT/'build/art/reviewed-integration'/('native-preview-save-latest.json' if args.native else 'preview-save-latest.json')).read_text())
    proof_path=Path(index['report']);assert sha(proof_path.read_bytes())==index['sha256']
    proof=json.loads(proof_path.read_text());assert proof['status']=='passed' and proof['romSha1']==meta['romSha1']
    source=Path(proof['save']);assert sha(source.read_bytes())==proof['saveSha256']
    folder=ROOT/'saves'/('reviewed-native-art-2026-09-20' if args.native else 'reviewed-art-2026-09-20');destination=folder/'FFTA_Reviewed_All_Classes.sav'
    for path in (folder,destination):
        assert path.resolve().is_relative_to(ROOT.resolve())
        assert not any(p.is_symlink() for p in (path,*path.parents))
    protected={}
    for base in (ROOT/'saves',ROOT/'roms/play'):
        if base.exists():
            for path in base.rglob('*'):
                if path.is_file():protected[str(path)]=sha(path.read_bytes())
    folder.mkdir(parents=True,exist_ok=True)
    installed=False
    if not destination.exists():
        with destination.open('xb') as stream:stream.write(source.read_bytes())
        installed=True
    for path,digest in protected.items():assert sha(Path(path).read_bytes())==digest,('Existing player file changed',path)
    result=dict(status='playable-art-preview',performanceAccepted=False,romSha1=meta['romSha1'],rom=meta['path'],
        sourceManifest=str(meta_path),sourceManifestSha256=sha(meta_path.read_bytes()),
        save=str(destination),saveSha256=sha(destination.read_bytes()),seedInstalled=installed,
        saveReport=str(proof_path),saveReportSha256=sha(proof_path.read_bytes()),
        launcher='Play Native Art Preview.cmd' if args.native else 'Play Reviewed Art Preview.cmd',
        gallery='build/art/reviewed-native-in-game-2026-09-20/index.html' if args.native else 'build/art/reviewed-in-game-2026-09-20/index.html',
        protectedFiles=protected,scope=__doc__)
    result['nativePalette']=args.native
    out=ROOT/'build/releases'/('reviewed-native-art-preview' if args.native else 'reviewed-art-preview');out.mkdir(parents=True,exist_ok=True)
    (out/'current.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],seedInstalled=installed,save=str(destination),protectedFiles=len(protected))))


if __name__=='__main__':main()
