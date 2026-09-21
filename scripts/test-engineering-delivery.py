"""Verify complete package and actual dedicated launcher; never launch a game."""
import datetime, json, re, shutil, subprocess
from pathlib import Path
from native_art import ROOT, sha

out=ROOT/'build/art/engineering-delivery'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
def protected():
    result={}
    for name in ('roms/play','saves','build/foundation'):
        for p in (ROOT/name).rglob('*'):
            if p.is_file() and (p.suffix.lower() in ('.gba','.sav','.srm','.state') or p.suffix.lower() in {'.ss'+str(i) for i in range(10)}):result[p.relative_to(ROOT).as_posix()]=sha(p.read_bytes())
    for p in ROOT.glob('Play*.cmd'):result[p.name]=sha(p.read_bytes())
    return result
try:
    before=protected();index=ROOT/'build/releases/v0.7-engineering/current.json';meta=json.loads(index.read_text());folder=ROOT/meta['directory']
    check(meta['status']=='full engineering with placeholder artwork' and meta['rom']['sha1']=='a28b624bb13c8f2f2597a4d4bd3999b17c234b99','Full engineering package identity')
    check((folder/'manifest.json').read_bytes()==index.read_bytes(),'Immutable manifest matches selected delivery')
    for name,digest in meta['documents'].items():check(sha((folder/name).read_bytes())==digest,'Packaged guide/reference '+name)
    for name in meta['documents']:
        p=folder/name
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            if '://' not in link and not link.startswith('#'):
                check((p.parent/link.split('#')[0]).is_file(),'Bundled reference link '+name+' -> '+link)
    for name,digest in meta['packagingSources'].items():check(sha((ROOT/name).read_bytes())==digest,'Packaged launcher/source '+name)
    check(sha((folder/meta['patch']['file']).read_bytes())==meta['patch']['sha256'],'Delivered BPS hash')
    check(sha((folder/'acceptance.json').read_bytes())==meta['acceptanceSha256'],'Delivered full acceptance certificate')
    check(all(meta['checks'].values()) and not meta['saves']['importsPlayerSave'],'Patch proofs and no save import')
    check(meta['saves']['directory']=='saves/expansion-v0.7-engineering','Dedicated independent storage')
    check('launch-engineering-expansion.ps1' in (ROOT/'Play Expansion.cmd').read_text() and 'launch-expansion.ps1' in (ROOT/'Play Previous Expansion.cmd').read_text(),'Default and previous expansion launchers remain distinct')
    command=[shutil.which('powershell.exe'),'-NoProfile','-ExecutionPolicy','Bypass','-File']
    def run(script):return subprocess.run(command+[str(script),'-ValidateOnly'],capture_output=True,text=True)
    result=run(ROOT/'scripts/launch-engineering-expansion.ps1');(out/'validation.log').write_text(result.stdout+'\n'+result.stderr)
    check(result.returncode==0,'Actual launcher validation succeeds');value=json.loads(result.stdout)
    check(value['validated'] and not value['launched'] and Path(value['rom'])==ROOT/meta['rom']['path'],'Actual launcher validates exact delivered ROM without launch')
    save=str(ROOT/meta['saves']['directory']);check(value['saveDirectory']==save and value['arguments']==['-C','"savegamePath='+save+'"','-C','"savestatePath='+save+'"','-C','"screenshotPath='+save+'"','"'+value['rom']+'"'],'All three actual mGBA storage overrides point to dedicated folder')
    fixture=out/'wrong ROM';(fixture/'scripts').mkdir(parents=True);shutil.copyfile(ROOT/'scripts/launch-engineering-expansion.ps1',fixture/'scripts/launch-engineering-expansion.ps1')
    manifest=fixture/'build/releases/v0.7-engineering/current.json';manifest.parent.mkdir(parents=True);manifest.write_text(json.dumps(meta))
    wrong=fixture/meta['rom']['path'];wrong.parent.mkdir(parents=True);wrong.write_bytes(b'wrong ROM')
    negative=run(fixture/'scripts/launch-engineering-expansion.ps1');(out/'negative.log').write_text(negative.stdout+'\n'+negative.stderr)
    check(negative.returncode!=0 and 'differs from the verified' in negative.stderr,'Wrong ROM rejected before launch')
    check(protected()==before,'All existing ROMs, saves and launchers preserved')
    report=dict(status='passed',romSha1=meta['rom']['sha1'],checks=checks,manifest=str(index),manifestSha256=sha(index.read_bytes()),protectedFiles=before,launcher=value,scope=__doc__)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',checks=checks,error=str(error)),indent=2)+'\n');print('Artifacts: '+str(out));raise
