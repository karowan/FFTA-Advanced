"""Patch-to-play, artifact switching, corruption rejection and save isolation."""
import copy, datetime, hashlib, json, shutil, subprocess, sys
from pathlib import Path
from mod_release import ROOT,sha,json_bytes,read_archive,archive_bytes,prepare,bps

out=ROOT/'build/release-tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
def reject(action,label):
    try:action()
    except (AssertionError,FileNotFoundError,ValueError,KeyError):checks.append(label)
    else:raise AssertionError('Accepted invalid input: '+label)
def protect():return {str(p):sha(p.read_bytes()) for base in (ROOT/'saves',ROOT/'roms/play') for p in base.rglob('*') if p.is_file()}
before=protect();channel_path=ROOT/'build/releases/current.json';channel=json.loads(channel_path.read_text())
archive=(ROOT/channel['archive']).read_bytes();manifest,files=read_archive(archive)
root=out/'independent installation';root.mkdir()
source=root/'clean.gba';shutil.copyfile(ROOT/channel['baseRom'],source)
(root/'emulator.exe').write_bytes(b'not executable; validation never launches it')
(root/'saves').mkdir();save=root/'saves'/'FFTA_Reviewed_All_Classes.sav';save.write_bytes(b'protected save sentinel')
local_channel=dict(schema=1,archive='release.zip',archiveSha256=sha(archive),baseRom='clean.gba',saveDirectory='saves',emulator='emulator.exe')
(root/'release.zip').write_bytes(archive);cp=root/'current.json';cp.write_bytes(json_bytes(local_channel))
def fixture_archive(contents):
    raw=archive_bytes(contents);(root/'release.zip').write_bytes(raw)
    c=copy.deepcopy(local_channel);c['archiveSha256']=sha(raw);cp.write_bytes(json_bytes(c))
def reset():
    (root/'release.zip').write_bytes(archive);cp.write_bytes(json_bytes(local_channel))
try:
    check(archive_bytes(files)==archive,'Reproducible ZIP byte identity')
    check(set(files)=={'FFTA_Expansion.bps','README.md','CHANGELOG.md','manifest.json'},'Share ZIP contains only patch and public documentation')
    for name,raw in files.items():
        if name.endswith(('.json','.md')):check(str(ROOT).encode() not in raw and b'C:\\Users\\' not in raw,'No private local paths: '+name)
    first=prepare(cp,root);target=Path(first['rom'])
    check(hashlib.sha1(target.read_bytes()).hexdigest()==manifest['target']['sha1'],'Fresh installation reconstructed accepted ROM from ZIP')
    stamp=target.stat().st_mtime_ns;second=prepare(cp,root)
    check(second==first and target.stat().st_mtime_ns==stamp,'Validated cache reused without rewriting')
    check(first['saveDirectory']==str(save.parent) and target.name==save.with_suffix('.gba').name,'Existing save directory and basename retained')
    target_raw=target.read_bytes();target.write_bytes(b'corrupt cached ROM')
    reject(lambda:prepare(cp,root),'Corrupt cached ROM rejected')
    check(target.read_bytes()==b'corrupt cached ROM','Corrupt cache is not silently overwritten');target.write_bytes(target_raw)
    original=source.read_bytes();source.write_bytes(b'wrong clean ROM')
    reject(lambda:prepare(cp,root),'Wrong clean ROM rejected even when cache exists');source.write_bytes(original)
    (root/'release.zip').write_bytes(b'corrupt ZIP')
    reject(lambda:prepare(cp,root),'Damaged archive rejected');reset()
    c=copy.deepcopy(local_channel);c['archive']='missing.zip';cp.write_bytes(json_bytes(c))
    reject(lambda:prepare(cp,root),'Missing release rejected');reset()
    c=copy.deepcopy(local_channel);c['baseRom']='../clean.gba';cp.write_bytes(json_bytes(c))
    reject(lambda:prepare(cp,root),'Path outside installation rejected');reset()
    bad=copy.deepcopy(files);bad['FFTA_Expansion.bps']=bad['FFTA_Expansion.bps'][:-1]+bytes([bad['FFTA_Expansion.bps'][-1]^1]);fixture_archive(bad)
    reject(lambda:prepare(cp,root),'Patch checksum mismatch rejected');reset()
    bad=copy.deepcopy(files);m=copy.deepcopy(manifest);m['target']['file']='../escape.gba';bad['manifest.json']=json_bytes(m);fixture_archive(bad)
    reject(lambda:prepare(cp,root),'Unsafe target filename rejected');reset()
    bad=copy.deepcopy(files);bad['README.md']+=b'changed';fixture_archive(bad)
    reject(lambda:prepare(cp,root),'Changed documentation rejected');reset()
    bad=copy.deepcopy(files);bad['game.gba']=b'private';fixture_archive(bad)
    reject(lambda:prepare(cp,root),'Unexpected ROM in ZIP rejected');reset()
    # A second synthetic release proves channel-based selection without editing
    # the launcher. Never launch this test ROM or promote it to the real channel.
    revised=bytearray(target_raw);revised[-32]^=1
    revised_path=root/'synthetic candidate.gba';revised_path.write_bytes(revised)
    patch_path=root/'second.bps';bps('create',source,revised_path,patch_path)
    from mod_release import record
    m=copy.deepcopy(manifest);m['version']='test-only-second-release';m['target']=dict(file=target.name,**record(revised))
    patch=patch_path.read_bytes();m['patch'].update(bytes=len(patch),sha256=sha(patch))
    revised_files=copy.deepcopy(files);revised_files.update({'FFTA_Expansion.bps':patch,'manifest.json':json_bytes(m)});fixture_archive(revised_files)
    switched=prepare(cp,root)
    check(switched['rom']!=first['rom'] and Path(switched['rom']).read_bytes()==revised,'Channel selects a new release without launcher edits')
    check(target.read_bytes()==target_raw and save.read_bytes()==b'protected save sentinel','Prior release cache and saves preserved')
    # Target authentication is independent of the BPS patch's internal CRC.
    m['target']['sha256']='a'*64;revised_files['manifest.json']=json_bytes(m);fixture_archive(revised_files)
    reject(lambda:prepare(cp,root),'Wrong expected target hash rejected after patching')
    shell=shutil.which('powershell.exe');assert shell
    for launcher in ('launch-mod-release.ps1','launch-approved-art.ps1'):
        result=subprocess.run([shell,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'scripts'/launcher),'-ValidateOnly'],capture_output=True,text=True)
        (out/(launcher+'.log')).write_text(result.stdout+result.stderr)
        check(result.returncode==0,'Actual launcher validates '+launcher)
        info=json.loads(result.stdout)
        check(info['validated'] and not info['launched'] and info['romSha1']==manifest['target']['sha1'],'Actual launcher resolves shared artifact '+launcher)
        check(Path(info['saveDirectory'])==ROOT/channel['saveDirectory'],'Actual save override '+launcher)
        check(info['arguments'][-1]=='"'+info['rom']+'"','Actual launcher quotes ROM path')
    broken=copy.deepcopy(channel);broken['archiveSha256']='0'*64;negative=out/'invalid-channel.json';negative.write_bytes(json_bytes(broken))
    result=subprocess.run([shell,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'scripts/launch-mod-release.ps1'),'-ValidateOnly','-Channel',negative.relative_to(ROOT).as_posix()],capture_output=True,text=True)
    (out/'negative-launcher.log').write_text(result.stdout+result.stderr)
    check(result.returncode!=0 and 'no game launched' in result.stderr,'Actual launcher fails before launching on invalid release')
    check(channel_path.read_bytes()==json_bytes(channel),'Tests never promote synthetic release')
    check(protect()==before,'Player saves and existing ROMs unchanged')
    report=dict(status='passed',romSha1=manifest['target']['sha1'],archiveSha256=sha(archive),checks=checks,protectedFiles=before,
        scope='Portable BPS ZIP, fresh patch-to-play installation, unchanged-cache reuse, release switch, corruption/path negatives and actual launchers ValidateOnly. No gameplay execution or desktop launch.')
except Exception as error:
    report=dict(status='failed',romSha1=manifest['target']['sha1'],checks=checks,error=str(error));raise
finally:
    (out/'report.json').write_bytes(json_bytes(report));print(json.dumps(dict(status=report['status'],report=str(out/'report.json'),checks=len(checks))))
