"""Install the latest verified showcase to its own files; never replace a save."""
import hashlib,json,pathlib,subprocess,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
latest=json.loads((ROOT/'build/showcase/latest.json').read_text(encoding='utf-8'))
assert latest['passed']
report_path=pathlib.Path(latest['report']);report=json.loads(report_path.read_text(encoding='utf-8'))
assert report['passed'] and report['directory']==str(report_path.parent)
sha=lambda b:hashlib.sha1(b).hexdigest()
rom=(ROOT/'roms/play/expansion-v0.7/FFTA_Expansion_v0.7.gba').read_bytes()
save=(report_path.parent/'showcase.sav').read_bytes()
assert sha(rom)==report['romSha1']=='1b070824a8dad4995434eee3ab40fa08187a6120'
assert sha(save)==report['saveSha1']
assert 'Native cold Continue preserves entire showcase profile' in report['checks']
for name,payload,is_save in (
 ('roms/play/expansion-showcase-v0.7/FFTA_Expansion_Showcase_v0.7.gba',rom,False),
 ('saves/expansion-showcase-v0.7/FFTA_Expansion_Showcase_v0.7.sav',save,True)):
 p=ROOT/name
 for part in (p,*p.parents):
  assert not part.is_symlink() and not part.is_junction(),('Linked output',part)
  if part==ROOT:break
 assert p.resolve().is_relative_to(ROOT.resolve())
 if p.exists():
  # Even an unchanged existing showcase save belongs to its player now.
  assert not is_save,'A showcase save already exists; it will not be replaced.'
  assert p.read_bytes()==payload,'Existing showcase ROM differs'
 else:
  p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb') as stream:stream.write(payload)
 assert p.read_bytes()==payload
result=subprocess.run([shutil.which('powershell.exe'),'-NoProfile','-ExecutionPolicy','Bypass',
 str(ROOT/'scripts/launch-expansion-showcase.ps1'),'-ValidateOnly'],capture_output=True,text=True)
assert result.returncode==0,result.stdout+'\n'+result.stderr
validation=json.loads(result.stdout);assert validation['validated'] and not validation['launched']
installation={'passed':True,'sourceReport':str(report_path),'sourceReportSha1':sha(report_path.read_bytes()),
 'romSha1':sha(rom),'seededSaveSha1':sha(save),'launcher':validation,'existingSavesReplaced':False}
(report_path.parent/'installation.json').write_text(json.dumps(installation,indent=2)+'\n',encoding='utf-8')
print(json.dumps(installation,indent=2))
