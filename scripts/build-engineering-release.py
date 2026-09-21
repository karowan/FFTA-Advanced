"""Reconstruct full engineering from clean ROM/source and pinned image PNGs.

Uses an isolated eight-stage gameplay source build, then regenerates every
current art transport including action completion and native shared palettes.
No game launch, installed selector or player-save writes. This is build proof,
not a substitute for gameplay acceptance or final packaging.
"""
import argparse, datetime, hashlib, json, pathlib, shutil, subprocess, sys
from native_art import ROOT, sha
import resource_guard

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resume-base',type=pathlib.Path,help='Reuse this exact passed fresh base report after an art-stage failure')
    parser.add_argument('--resume-base-sha256',help='Required exact report identity when reusing the fresh gameplay prefix')
    args=parser.parse_args();out=ROOT/'build/art/engineering-rebuild'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    report=dict(status='running',scope=__doc__,steps=[]);workspace=None;art_output=None
    try:
        resource_guard.require_admission(ROOT,'full engineering source rebuild')
        recipe_path=ROOT/'notes/native-art-build-inputs.json';recipe=json.loads(recipe_path.read_text())
        current=ROOT/'build/art/native-palettes/current.json';current_bytes=current.read_bytes();meta=json.loads(current_bytes)
        expected=pathlib.Path(meta['path']).read_bytes();assert hashlib.sha1(expected).hexdigest()==recipe['candidateSha1']
        def run(label,command,cwd,timeout):
            log=out/(label+'.log');print('Building '+label,flush=True)
            with log.open('w',encoding='utf-8') as stream:code,peak=resource_guard.run_contained(command,timeout,cwd=cwd,stdout=stream,stderr=subprocess.STDOUT)
            report['steps'].append(dict(label=label,code=code,log=str(log),logSha256=sha(log.read_bytes()),peakMemoryBytes=peak))
            assert code==0,(label+' failed; retained log',str(log))
        if args.resume_base:
            base_report=args.resume_base.resolve();assert args.resume_base_sha256 and sha(base_report.read_bytes())==args.resume_base_sha256,'Resumed gameplay report identity changed'
        else:
            run('gameplay-base',[sys.executable,str(ROOT/'scripts/rebuild-expansion.py'),'--source-profile','native-art-base','--keep-workspace'],ROOT,900)
            base_report=pathlib.Path(json.loads((ROOT/'build/reproducibility/latest.json').read_text())['report'])
        base=json.loads(base_report.read_text());assert base['passed'] and base['sourceProfile']['profileSha256']==sha((ROOT/'notes/native-art-gameplay-base.json').read_bytes())
        assert base['result']['romSha1']==recipe['gameplayBaseSha1'];workspace=pathlib.Path(base['workspace']).resolve()
        assert workspace.is_relative_to((ROOT/'build/reproducibility').resolve()) and workspace.is_dir() and not workspace.is_symlink() and not workspace.is_junction()
        manifest=pathlib.Path(base['result']['manifest']);assert sha(manifest.read_bytes())==base['result']['manifestSha256']
        assert sha(pathlib.Path(base['result']['rom']).read_bytes())==base['result']['romSha256']
        report['gameplayBase']=dict(report=str(base_report),sha256=sha(base_report.read_bytes()),resumed=bool(args.resume_base))
        # Base-profile files return to the current later-stage source, in this
        # private workspace only. Preserve both stages' separate source hashes.
        for entry in base['sourceProfile']['overrides']:shutil.copyfile(ROOT/entry['path'],workspace/entry['path'])
        for name in ('scripts/build-engineering-art.py','notes/native-art-build-inputs.json'):shutil.copyfile(ROOT/name,workspace/name)
        report['artSources']={n:sha((ROOT/n).read_bytes()) for n in base['checkoutSources'] if n.startswith(('scripts/','src/'))}
        report['artSources']['scripts/build-engineering-art.py']=sha((ROOT/'scripts/build-engineering-art.py').read_bytes())
        for name in report['artSources']:
            target=workspace/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
        for row in recipe['inputs']:
            p=ROOT/row['path'];assert sha(p.read_bytes())==row['sha256']
            target=workspace/row['path'];assert target.resolve().is_relative_to(workspace)
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
        art_output=workspace/'build/engineering-art'/out.name
        run('complete-art',[sys.executable,str(workspace/'scripts/build-engineering-art.py'),'--base-manifest',str(manifest),'--output',str(art_output)],workspace,600)
        art_path=art_output/'report.json';art=json.loads(art_path.read_text());assert art['status']=='passed'
        rebuilt=pathlib.Path(art['path']).read_bytes();assert rebuilt==expected and art['romSha1']==recipe['candidateSha1']
        assert current.read_bytes()==current_bytes and pathlib.Path(meta['path']).read_bytes()==expected
        assert all(sha((ROOT/n).read_bytes())==h for n,h in report['artSources'].items())
        assert all(sha((ROOT/r['path']).read_bytes())==r['sha256'] for r in recipe['inputs'])
        (out/'FFTA_Engineering.gba').write_bytes(rebuilt);shutil.copyfile(art['manifest'],out/'candidate.json');shutil.copyfile(art_path,out/'art-report.json')
        report.update(status='passed',romSha1=art['romSha1'],romSha256=sha(rebuilt),path=str(out/'FFTA_Engineering.gba'),manifest=str(out/'candidate.json'),byteIdentical=True,recipeSha256=sha(recipe_path.read_bytes()),artReportSha256=sha(art_path.read_bytes()),workspace=str(workspace),workspaceRetained=True)
    except Exception as error:
        report.update(status='failed',error=repr(error),workspace=str(workspace) if workspace else None)
        if art_output and (art_output/'failed.json').exists():
            shutil.copyfile(art_output/'failed.json',out/'art-failed.json')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=report['status'],report=str(out/'report.json'),error=report.get('error'))),flush=True)
    if report['status']!='passed':raise SystemExit(1)

if __name__=='__main__':main()
