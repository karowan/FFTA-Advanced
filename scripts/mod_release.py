"""Portable BPS ZIP publication and local, verified patch-to-play resolution."""
import hashlib, io, json, os, re, shutil, subprocess, uuid, zipfile, zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def json_bytes(value):return (json.dumps(value,indent=2,sort_keys=True)+'\n').encode()
def record(raw):return dict(bytes=len(raw),sha256=sha(raw),sha1=hashlib.sha1(raw).hexdigest(),crc32=f'{zlib.crc32(raw):08x}')
def local(root,name):
    assert isinstance(name,str) and name and not any(c in name for c in ('"','\n','\r')), 'Invalid local path'
    p=root/name
    assert not Path(name).is_absolute() and p.resolve().is_relative_to(root.resolve()),'Path outside checkout'
    cursor=p
    while cursor!=root:
        assert not cursor.is_symlink() and not (cursor.exists() and getattr(cursor.stat(),'st_file_attributes',0)&0x400),'Linked release path'
        cursor=cursor.parent
    return p
def filename(value):
    assert isinstance(value,str) and re.fullmatch(r'[A-Za-z0-9_.-]+',value) and value not in ('.','..'),'Invalid release filename'
    return value
def immutable(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():assert path.read_bytes()==data,'Immutable release differs: '+str(path)
    else:
        with path.open('xb') as f:f.write(data)
def atomic(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.parent/(path.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        with tmp.open('xb') as f:f.write(data)
        os.replace(tmp,path)
    finally:
        if Path(tmp).exists():Path(tmp).unlink()
def bps(mode,source,input_path,output):
    node=shutil.which('node');assert node,'Node.js is required for the local ROM patcher'
    result=subprocess.run([node,str(ROOT/'scripts/release-bps.mjs'),mode,str(source),str(input_path),str(output)],cwd=ROOT,capture_output=True,text=True)
    output.with_suffix('.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0,'BPS '+mode+' failed: '+result.stderr
def archive_bytes(files):
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(filename(name),date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16;z.writestr(info,data)
    return stream.getvalue()
def read_archive(raw):
    assert len(raw)<64*1024*1024,'Oversize release ZIP'
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names=z.namelist();assert len(names)==len(set(names))==4,'Expected four unique release files'
        assert sum(i.file_size for i in z.infolist())<64*1024*1024,'Oversize release contents'
        assert set(names)=={'manifest.json','README.md','CHANGELOG.md','FFTA_Expansion.bps'},'Unexpected release contents'
        files={n:z.read(n) for n in names}
    m=json.loads(files['manifest.json']);assert m['schema']==1 and m['patch']['format']=='BPS','Unsupported release'
    assert m['patch']['file']=='FFTA_Expansion.bps' and m['patch']['sha256']==sha(files[m['patch']['file']]),'Patch checksum mismatch'
    assert m['patch']['bytes']==len(files[m['patch']['file']]) and files[m['patch']['file']][:4]==b'BPS1','Invalid BPS'
    assert set(m['documents'])=={'README.md','CHANGELOG.md'},'Document contract'
    for name,digest in m['documents'].items():assert sha(files[name])==digest,'Document checksum mismatch'
    filename(m['target']['file']);assert m['target']['file'].endswith('.gba')
    for item in ('source','target'):
        assert re.fullmatch('[a-f0-9]{64}',m[item]['sha256']) and re.fullmatch('[a-f0-9]{40}',m[item]['sha1'])
        assert 0<m[item]['bytes']<=32*1024*1024
    return m,files
def prepare(channel_path,root=ROOT):
    channel_path=local(root,str(channel_path.relative_to(root)))
    c=json.loads(channel_path.read_text());assert c['schema']==1
    archive=local(root,c['archive']);raw=archive.read_bytes()
    assert sha(raw)==c['archiveSha256'],'Release archive checksum mismatch'
    m,files=read_archive(raw)
    source=local(root,c['baseRom']);assert record(source.read_bytes())==m['source'],'Wrong clean ROM'
    save=local(root,c['saveDirectory']);emulator=local(root,c['emulator']);assert emulator.is_file(),'Missing local emulator'
    cache=local(root,'build/play-cache/'+m['target']['sha256']);cache.mkdir(parents=True,exist_ok=True)
    patch=cache/m['patch']['file'];immutable(patch,files[m['patch']['file']])
    target=cache/m['target']['file']
    if not target.exists():
        # Only install the output after the independent target hash passes.
        tmp=cache/(uuid.uuid4().hex+'.gba.tmp')
        try:
            bps('apply',source,patch,Path(tmp))
            assert record(Path(tmp).read_bytes())=={k:v for k,v in m['target'].items() if k!='file'},'Patched ROM checksum mismatch'
            immutable(target,Path(tmp).read_bytes())
        finally:
            if Path(tmp).exists():Path(tmp).unlink()
    assert record(target.read_bytes())=={k:v for k,v in m['target'].items() if k!='file'},'Cached ROM checksum mismatch'
    return dict(validated=True,launched=False,rom=str(target),romSha1=m['target']['sha1'],saveDirectory=str(save),emulator=str(emulator),releaseArchive=str(archive),version=m['version'])
def publish(candidate,run_path,evidence,config_path=ROOT/'scripts/mod-release.json'):
    config=json.loads(config_path.read_text());assert config['schema']==1
    source=local(ROOT,config['baseRom']);source_raw=source.read_bytes();target=Path(candidate['path']);target_raw=target.read_bytes()
    assert hashlib.sha1(source_raw).hexdigest()==config['baseSha1'],'Wrong clean USA base'
    assert hashlib.sha1(target_raw).hexdigest()==candidate['romSha1'] and sha(target_raw)==candidate['romSha256']
    version=filename(config['version']);target_name=filename(config['targetFilename'])
    root=ROOT/'build/releases';root.mkdir(exist_ok=True)
    temp=local(ROOT,'build/releases/packaging-'+uuid.uuid4().hex);temp.mkdir()
    patchpath=temp/'patch.bps';bps('create',source,target,patchpath);patch=patchpath.read_bytes()
    readme_text=local(ROOT,config['readmeTemplate']).read_text(encoding='utf-8')
    values={'MOD_NAME':config['name'],'VERSION':version,'SOURCE_BYTES':str(len(source_raw)),
            'SOURCE_SHA1':hashlib.sha1(source_raw).hexdigest(),'TARGET_SHA1':candidate['romSha1']}
    for key,value in values.items():
        token='{{'+key+'}}';assert token in readme_text,'Missing README field: '+key
        readme_text=readme_text.replace(token,value)
    assert '{{' not in readme_text and '}}' not in readme_text,'Unresolved README field'
    readme=readme_text.encode('utf-8')
    changes=('# Release notes\n\n'+config['notes']+'\n').encode()
    manifest=dict(schema=1,name=config['name'],version=version,source=record(source_raw),target=dict(file=target_name,**record(target_raw)),
        patch=dict(file='FFTA_Expansion.bps',format='BPS',bytes=len(patch),sha256=sha(patch)),documents={'README.md':sha(readme),'CHANGELOG.md':sha(changes)},
        validation=dict(candidateRunSha256=sha(run_path.read_bytes()),tests=[e['id'] for e in evidence],roundtrip=True,wrongSourceRejected=True,deterministicPatch=True))
    files={'manifest.json':json_bytes(manifest),'README.md':readme,'CHANGELOG.md':changes,'FFTA_Expansion.bps':patch}
    archive=archive_bytes(files);assert archive_bytes(files)==archive;read_archive(archive)
    folder=local(ROOT,'build/releases/artifacts/'+sha(archive));dest=folder/(version+'.zip');immutable(dest,archive)
    # Portable contents contain no private paths; local channel owns installation settings.
    channel=dict(schema=1,archive=dest.relative_to(ROOT).as_posix(),archiveSha256=sha(archive),
        baseRom=config['baseRom'],saveDirectory=config['saveDirectory'],emulator=config['emulator'])
    pending=folder/('local-channel-'+sha(json_bytes(channel))+'.json');immutable(pending,json_bytes(channel))
    ready=prepare(pending)
    atomic(root/'current.json',json_bytes(channel))
    return dict(status='passed',romSha1=candidate['romSha1'],archive=str(dest),archiveSha256=sha(archive),archiveBytes=len(archive),patchBytes=len(patch),channel=str(root/'current.json'),prepared=ready)
