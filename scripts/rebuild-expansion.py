"""Build in a fresh private workspace from source, pinned tools and clean ROM.

No existing build, manifest, generated binary, fixture or save is copied. Each
tool and ROM is a real copy. Never overwrites a playable ROM or the candidate.
This proves reproducibility only; it does not replace gameplay acceptance.
"""
import argparse,datetime,hashlib,json,os,pathlib,shutil,subprocess,sys,time
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import resource_guard
from engine_bootstrap_source import sources as bootstrap_sources
from historical_sources import source_file, source_tree
ROOT=pathlib.Path(__file__).resolve().parents[1]
CLEAN_SHA1='4ac05441f4de70a4ec3dd932116346c61b8783d9'
NEW_SOURCES=('Build Expansion.ps1','REPRODUCIBLE-BUILD.md','scripts/rebuild-expansion.py',
 'notes/reproducible-toolchain.json','notes/engine-bootstrap.json')
NEW_SOURCES+=('scripts/engine_bootstrap_source.py',)
NEW_SOURCES+=('scripts/historical_sources.py','scripts/resolve-python.ps1')
NEW_SOURCES+=('notes/native-art-gameplay-base.json',)
NEW_SOURCES+=('scripts/build-engineering-art.py','scripts/build-engineering-release.py','notes/native-art-build-inputs.json')

def digest(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def inventory(path):
 if path.is_file():return {'':digest(path)}
 return {p.relative_to(path).as_posix():digest(p) for p in sorted(path.rglob('*')) if p.is_file()}

def tree_digest(items):
 return hashlib.sha256(json.dumps(items,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def json_write(path,data):path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--compare-current',action='store_true',help='Require exact equality with the current candidate, without modifying it')
 parser.add_argument('--keep-workspace',action='store_true',help='Keep the private workspace copy (tools, ROMs, build tree) after the report is written')
 parser.add_argument('--source-profile',choices=('current','native-art-base'),default='current',help='Reconstruct the explicitly pinned gameplay source stage before later art/menu modules')
 args=parser.parse_args()
 # Each workspace copies the pinned toolchain and rebuilds every probe; refuse
 # on a volume that cannot absorb that (notes/resource-incident-2026-09-15.md).
 admission=resource_guard.require_admission(ROOT,'clean source rebuild')
 output=ROOT/'build/reproducibility'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
 workspace=output/'workspace';output.mkdir(parents=True,exist_ok=False)
 report={'passed':False,'workspace':str(workspace),'steps':[],
  'scope':'Clean source assembly and optional byte equality; no gameplay acceptance.',
  'resources':{'admission':admission}}
 started=time.monotonic()
 try:
  clean=ROOT/'roms/clean/FFTA_US_clean.gba'
  assert hashlib.sha1(clean.read_bytes()).hexdigest()==CLEAN_SHA1,'Wrong clean USA ROM'
  report['cleanRomSha1']=CLEAN_SHA1
  reference_path=ROOT/'build/expansion/probes/integrated-jobs/current.json'
  reference=None
  if args.compare_current:
   reference=json.loads(reference_path.read_text(encoding='utf-8'))
   reference_rom=pathlib.Path(reference['path'])
   assert hashlib.sha1(reference_rom.read_bytes()).hexdigest()==reference['romSha1']
   report['reference']={'manifest':str(reference_path),'manifestSha256':digest(reference_path),
    'rom':str(reference_rom),'romSha1':reference['romSha1']}
  # Git is an inventory source only: take current working file bytes so an
  # authorized implementation sweep can be checked before its commit.
  names=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode('utf-8').split('\0')
  names=sorted(set(n for n in names if n)|set(NEW_SOURCES))
  allowed={'.py','.mjs','.js','.json','.md','.ps1','.c','.h','.s','.ld','.txt','.event','.cmd','.gitignore','.gitattributes'}
  sources={};checkout_sources={};source_overrides={}
  if args.source_profile=='native-art-base':
   profile_path=ROOT/'notes/native-art-gameplay-base.json';profile=json.loads(profile_path.read_text(encoding='utf-8'))
   assert profile['schema']==1
   for entry in profile['overrides']:
    name=entry['path'];assert name in names and name not in source_overrides
    raw=source_file(entry['commit'],name,ROOT)
    assert hashlib.sha256(raw).hexdigest()==entry['sha256'],('Pinned source profile mismatch',name)
    source_overrides[name]=raw
   report['sourceProfile']={**profile,'profileSha256':digest(profile_path)}
  for name in names:
   relative=pathlib.PurePosixPath(name)
   assert not relative.is_absolute() and '..' not in relative.parts
   original=ROOT/name
   if original.suffix.lower() not in allowed and original.name not in allowed:continue
   # Tests are copied as source, but never their private input/output trees.
   assert relative.parts[0] not in ('build','tools','roms','saves','.worktrees','.local')
   assert original.is_file() and not original.is_symlink(),('Source unavailable',name)
   target=workspace/name;target.parent.mkdir(parents=True,exist_ok=True)
   checkout_sources[name]=digest(original)
   if name in source_overrides:target.write_bytes(source_overrides[name])
   else:shutil.copyfile(original,target)
   sources[name]=digest(target)
  report['sources']=sources;report['sourceTreeSha256']=tree_digest(sources)
  report['checkoutSources']=checkout_sources
  bootstrap=json.loads((workspace/'notes/engine-bootstrap.json').read_text(encoding='utf-8'))
  assert len(bootstrap['sourceCommit'])==40
  # The public checkout carries these exact build inputs as text, so a fresh
  # Git history does not erase the required original engine layout.
  historical,origin=source_tree(bootstrap['sourceCommit'],ROOT)
  report['bootstrap']={**bootstrap,**origin,
   'sources':{n:hashlib.sha256(b).hexdigest() for n,b in historical.items()}}
  historical=bootstrap_sources(historical)
  report['bootstrap']['effectiveSources']={n:hashlib.sha256(b).hexdigest() for n,b in historical.items()}
  pins=json.loads((workspace/'notes/reproducible-toolchain.json').read_text(encoding='utf-8'))
  report['tools']={}
  for entry in pins['inputs']:
   name=entry['path'];original=ROOT/name;target=workspace/name
   print('Copying pinned input: '+name,flush=True)
   files=inventory(original)
   assert files and tree_digest(files)==entry['treeSha256'],('Tool prerequisite differs from recorded input',name)
   target.parent.mkdir(parents=True,exist_ok=True)
   if original.is_dir():shutil.copytree(original,target)
   else:shutil.copyfile(original,target)
   assert inventory(target)==files,('Tool copy mismatch',name)
   report['tools'][name]={'treeSha256':tree_digest(files),'files':files}
  target=workspace/'roms/clean/FFTA_US_clean.gba';target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(clean,target)
  node=shutil.which('node');powershell=shutil.which('pwsh') or shutil.which('powershell')
  assert node and powershell,'Node.js and PowerShell are required'
  report['runtimes']={}
  for label,executable,version_args in (('python',sys.executable,['--version']),('node',node,['--version']),
    ('powershell',powershell,['-NoProfile','-Command','$PSVersionTable.PSVersion.ToString()'])):
   report['runtimes'][label]={'path':executable,'sha256':digest(pathlib.Path(executable)),
    'version':subprocess.check_output([executable,*version_args],text=True).strip()}
  # Builders use relative local compilers and may invoke node/python children.
  environment=dict(os.environ);environment['PATH']=str(pathlib.Path(node).parent)+os.pathsep+environment.get('PATH','')
  stages=[('foundation',[powershell,'-NoProfile','-File','Build Foundation.ps1','-BuildOnly','-Python',sys.executable]),
   ('engine',[powershell,'-NoProfile','-File','Build Engine.ps1','-SkipTests','-Python',sys.executable]),
   *[(label,[sys.executable,script]) for label,script in (
    ('samurai','scripts/build-samurai-probe.py'),('job-state','scripts/build-job-state-probe.py'),
    ('chemist','scripts/jobs/chemist/build.py'),('dark-knight','scripts/jobs/dark-knight/build.py'),
    ('viking','scripts/jobs/viking/build.py'),('integrated','scripts/build-integrated-jobs.py'))]]
  for number,(label,command) in enumerate(stages,1):
   if label=='engine':
    for name,data in historical.items():
     target=workspace/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
   if label=='samurai':
    for name in historical:
     if name not in sources:(workspace/name).unlink()
    for name,value in sources.items():
     assert digest(ROOT/name)==checkout_sources[name],('Source changed before restoration',name)
     if name in source_overrides:(workspace/name).write_bytes(source_overrides[name])
     else:shutil.copyfile(ROOT/name,workspace/name)
   print(f'[{number}/{len(stages)}] clean {label}',flush=True)
   log=output/f'{number:02}-{label}.log';begin=time.monotonic()
   with log.open('w',encoding='utf-8') as stream:
    code,peak=resource_guard.run_contained(command,900,cwd=workspace,env=environment,stdout=stream,stderr=subprocess.STDOUT)
   row={'stage':label,'command':command,'exitCode':code,'seconds':round(time.monotonic()-begin,3),'log':str(log),'logSha256':digest(log)}
   if peak is not None:row['peakMemoryMB']=round(peak/1024**2,1)
   assert code is not None,('Build stage timed out; process tree terminated',label,str(log))
   class result:returncode=code
   report['steps'].append(row);json_write(output/'report.json',report)
   assert result.returncode==0,('Build stage failed',label,str(log))
   if label=='engine':
    for name,expected in (('build/expansion/engine.bin',bootstrap['engineSha1']),
      ('build/expansion/probes/combat.gba',bootstrap['combatRomSha1'])):
     actual=hashlib.sha1((workspace/name).read_bytes()).hexdigest()
     assert actual==expected,('Bootstrap differs from pinned source result',name,actual,expected)
  manifest_path=workspace/'build/expansion/probes/integrated-jobs/current.json'
  manifest=json.loads(manifest_path.read_text(encoding='utf-8'));rebuilt=pathlib.Path(manifest['path'])
  assert rebuilt.is_relative_to(workspace),'Builder escaped the isolated workspace'
  rebuilt_bytes=rebuilt.read_bytes();assert hashlib.sha1(rebuilt_bytes).hexdigest()==manifest['romSha1']
  old_symbols={p[2]:int(p[0],16) for line in (workspace/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=line.split())==3}
  report['retiredBootstrapEntries']=[]
  for site,name in ((0x130200,'ffta_exposed_preview_entry'),(0x130454,'ffta_exposed_combo_entry'),
    (0x9dd52,'ffta_status_next_entry'),(0x97ad0,'ffta_status_visual_entry')):
   literal=((site+5)&~3)+4;target=int.from_bytes(rebuilt_bytes[literal:literal+4],'little')
   assert target&1 and target!=old_symbols[name]|1,('Historical bootstrap entry remained installed',name)
   report['retiredBootstrapEntries'].append({'site':hex(site),'name':name,'finalTarget':hex(target),'bootstrapTarget':hex(old_symbols[name]|1)})
  report['result']={'manifest':str(manifest_path),'manifestSha256':digest(manifest_path),
   'rom':str(rebuilt),'romSha1':manifest['romSha1'],'romSha256':digest(rebuilt),'bytes':len(rebuilt_bytes)}
  # Source input files are immutable from the parent checkout's perspective;
  # generated headers/reports stay solely in the private workspace.
  assert all(digest(ROOT/name)==value for name,value in checkout_sources.items()),'Source changed during isolated build'
  if args.source_profile=='native-art-base':
   assert manifest['romSha1']==profile['expectedRomSha1'],('Source-profile result differs',manifest['romSha1'])
  assert hashlib.sha1(clean.read_bytes()).hexdigest()==CLEAN_SHA1,'Clean ROM changed'
  if reference:
   assert digest(reference_path)==report['reference']['manifestSha256'],'Current candidate manifest changed'
   reference_bytes=reference_rom.read_bytes()
   assert hashlib.sha1(reference_bytes).hexdigest()==reference['romSha1'],'Current candidate changed'
   report['byteIdentical']=rebuilt_bytes==reference_bytes
   if not report['byteIdentical']:
    report['firstDifference']=next((i for i,(a,b) in enumerate(zip(rebuilt_bytes,reference_bytes)) if a!=b),min(len(rebuilt_bytes),len(reference_bytes)))
   assert report['byteIdentical'],('Clean build differs from current candidate',report.get('firstDifference'))
  report['passed']=True
 except BaseException as error:
  report['error']=repr(error)
 finally:
  report['seconds']=round(time.monotonic()-started,3)
  # The report carries every hash the workspace could prove; the copied
  # toolchain and rebuilt probe tree are regenerable and are removed unless
  # explicitly kept, so repeated runs cannot accumulate gigabytes.
  report['workspaceRemoved']=False
  if not args.keep_workspace and workspace.is_dir():
   assert workspace.resolve().is_relative_to((ROOT/'build/reproducibility').resolve()),'Workspace cleanup escaped build/reproducibility'
   assert not workspace.is_symlink() and not workspace.is_junction(),'Workspace cleanup target is a link'
   shutil.rmtree(workspace,ignore_errors=True);report['workspaceRemoved']=not workspace.exists()
  json_write(output/'report.json',report)
  json_write(output.parent/'latest.json',{'passed':report['passed'],'report':str(output/'report.json')})
  print(json.dumps({k:v for k,v in report.items() if k not in ('sources','tools')},indent=2))
 if not report['passed']:raise SystemExit(1)

if __name__=='__main__':main()
