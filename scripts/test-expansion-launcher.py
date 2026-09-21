"""Validate the actual PowerShell launcher without starting mGBA."""
import hashlib,json,pathlib,shutil,subprocess,uuid
ROOT=pathlib.Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def player_files():
 result={}
 for directory in ('roms/play','saves','build/foundation'):
  base=ROOT/directory
  if base.exists():
   for p in base.rglob('*'):
    if p.is_file() and p.suffix.lower() in ('.gba','.sav','.srm','.state','.ss0','.ss1','.ss2','.ss3','.ss4','.ss5','.ss6','.ss7','.ss8','.ss9'):
     result[p.relative_to(ROOT).as_posix()]=digest(p)
 for name in ('Play FFTA.cmd','Play Development Build.cmd'):
  result[name]=digest(ROOT/name)
 return result
before=player_files()
manifest=json.loads((ROOT/'build/releases/v0.7/manifest.json').read_text(encoding='utf-8'))
base=ROOT/'build/releases/v0.7'
for name,sha in manifest['documents'].items():assert digest(base/name)==sha,name
for name,sha in manifest['packagingSources'].items():assert digest(ROOT/name)==sha,name
assert digest(base/manifest['patch']['file'])==manifest['patch']['sha256']
assert digest(base/'acceptance.json')==manifest['acceptanceSha256']
command=[shutil.which('powershell.exe'),'-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'scripts/launch-expansion.ps1'),'-ValidateOnly']
result=subprocess.run(command,capture_output=True,text=True)
assert result.returncode == 0, result.stdout+'\n'+result.stderr
data=json.loads(result.stdout)
assert data['validated'] and not data['launched']
assert pathlib.Path(data['rom'])==ROOT/manifest['rom']['path']
assert pathlib.Path(data['saveDirectory'])==ROOT/manifest['saves']['directory']
assert data['arguments']==['-C','"savegamePath='+data['saveDirectory']+'"',
 '-C','"savestatePath='+data['saveDirectory']+'"',
 '-C','"screenshotPath='+data['saveDirectory']+'"','"'+data['rom']+'"']
assert player_files()==before,'Player files or existing launchers changed'
# A separate disposable tree proves a changed ROM is refused before any game
# process starts. The path deliberately contains spaces. Normal inherited ACLs.
fixture=ROOT/'build/launcher-tests'/('wrong ROM '+uuid.uuid4().hex)
(fixture/'scripts').mkdir(parents=True)
shutil.copyfile(ROOT/'scripts/launch-expansion.ps1',fixture/'scripts/launch-expansion.ps1')
wrong=fixture/manifest['rom']['path'];wrong.parent.mkdir(parents=True);wrong.write_bytes(b'wrong ROM')
fixture_manifest=fixture/'build/releases/v0.7/manifest.json'
fixture_manifest.parent.mkdir(parents=True);fixture_manifest.write_text(json.dumps(manifest),encoding='utf-8')
negative=subprocess.run([*command[:-2],str(fixture/'scripts/launch-expansion.ps1'),'-ValidateOnly'],capture_output=True,text=True)
assert negative.returncode != 0 and 'differs from the verified' in negative.stderr, negative.stderr
report={'passed':True,'romSha1':manifest['rom']['sha1'],'launcher':data,
 'protectedFiles':before,'wrongRomRejected':True,
 'scope':'Actual launcher validation mode, wrong-ROM negative, manifest hashes and unchanged existing games/saves; no GUI launch.'}
(base/'launcher-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'protectedFiles':len(before),'launched':False}))
