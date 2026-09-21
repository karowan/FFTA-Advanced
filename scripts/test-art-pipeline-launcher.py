"""Validate real launcher, isolated saves and changed-ROM rejection; no launch."""
import datetime,hashlib,json,shutil,subprocess,uuid
from pathlib import Path
from native_art import ROOT,sha

def protected():
    result={}
    for name in ('roms/play','saves','build/foundation'):
        for p in (ROOT/name).rglob('*'):
            if p.is_file() and p.suffix.lower() in ('.gba','.sav','.srm','.state','.ss0','.ss1','.ss2','.ss3','.ss4','.ss5','.ss6','.ss7','.ss8','.ss9'):
                result[str(p.relative_to(ROOT))]=sha(p.read_bytes())
    return result

before=protected();meta=json.loads((ROOT/'build/art/pipeline/delivery/current.json').read_text())
out=ROOT/'build/art/pipeline/launcher'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[]
try:
    command=[shutil.which('powershell.exe'),'-NoProfile','-ExecutionPolicy','Bypass','-File']
    def run(script):return subprocess.run(command+[str(script),'-ValidateOnly'],capture_output=True,text=True)
    result=run(ROOT/'scripts/launch-art-pipeline.ps1');(out/'validation.log').write_text(result.stdout+'\n'+result.stderr)
    assert result.returncode==0,result.stderr
    value=json.loads(result.stdout);assert value['validated'] and not value['launched']
    assert Path(value['rom'])==ROOT/meta['rom']['path']
    assert Path(value['saveDirectory'])==ROOT/meta['saves']['directory']
    assert value['arguments']==['-C','"savegamePath='+value['saveDirectory']+'"','-C','"savestatePath='+value['saveDirectory']+'"','-C','"screenshotPath='+value['saveDirectory']+'"','"'+value['rom']+'"']
    checks.append('actual launcher validates exact ROM and three isolated storage overrides without launching')
    fixture=out/'wrong ROM';(fixture/'scripts').mkdir(parents=True)
    shutil.copyfile(ROOT/'scripts/launch-art-pipeline.ps1',fixture/'scripts/launch-art-pipeline.ps1')
    index=fixture/'build/art/pipeline/delivery/current.json';index.parent.mkdir(parents=True);index.write_text(json.dumps(meta))
    rom=fixture/meta['rom']['path'];rom.parent.mkdir(parents=True);rom.write_bytes(b'wrong ROM')
    negative=run(fixture/'scripts/launch-art-pipeline.ps1');(out/'negative.log').write_text(negative.stdout+'\n'+negative.stderr)
    assert negative.returncode!=0 and 'differs from the verified' in negative.stderr
    checks.append('wrong ROM refused before launch, even with a valid-looking delivery manifest')
    assert protected()==before
    checks.append('all existing player ROMs and save files unchanged')
    report=dict(status='passed',romSha1=meta['rom']['sha1'],checks=checks,protectedFiles=before,launcher=value,scope='Launcher validation only; no visible game launch or new save.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n');raise
