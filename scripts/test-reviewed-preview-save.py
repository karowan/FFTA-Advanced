"""Verify the existing disposable showcase save on the combined reviewed ROM.

No new roster/AP/gear fixture is invented: reuse the previously authenticated
showcase with all class options unlocked. Save through the native menu, then
cold Continue and compare canonical player data before offering a private copy.
"""
import argparse,ctypes as C,datetime,hashlib,json,runpy,struct
from pathlib import Path
from native_art import ROOT,sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--native',action='store_true')
    parser.add_argument('--manifest',type=Path);parser.add_argument('--output-index',type=Path);args=parser.parse_args()
    meta=json.loads((args.manifest or ROOT/'build/art/reviewed-integration'/('native-complete-candidate.json' if args.native else 'complete-candidate.json')).read_text())
    rom=Path(meta['path']);assert hashlib.sha1(rom.read_bytes()).hexdigest()==meta['romSha1']
    source=ROOT/'build/showcase/20260917T160011.215713Z/showcase.sav';seed=source.read_bytes()
    assert hashlib.sha1(seed).hexdigest()=='7831543efb239ef145764889214f8d83cd56eb14'
    prior=json.loads((source.parent/'report.json').read_text());assert prior['passed'] and prior['saveSha1']==hashlib.sha1(seed).hexdigest()
    out=ROOT/'build/art/reviewed-integration/preview-save'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];checks=[];inputs=[];e=None;failure=None
    def check(ok,label):
        assert ok,label
        checks.append(label)
    def tap(key,wait=180):inputs.append([8,key,wait]);e.run(8,key);e.run(wait)
    def cold(saved):
        nonlocal e
        e=E(rom);e.set_memory(0,saved,0);e.run(3600)
        for key in (8,256,256,256):tap(key,300)
    def canonical(r):return [r[0x80:0x1e70],r[0x1e80:0x1e98],r[0x1f64:0x1f68]]
    try:
        cold(seed);original=e.memory();expected=canonical(original)
        for member in prior['party']:
            p=0x80+264*member['slot']
            check(original[p+6]==member['race'] and original[p+7]==member['job'],'Native Continue class/race '+str(member['slot']))
            check(original[p+8]==member['secondary'] and original[p+0x36]==member['secondary'],'Native secondary command '+str(member['slot']))
            check(struct.unpack_from('<H',original,p+0x2a)[0]==member['item'],'Native saved legal equipment '+str(member['slot']))
        e.screenshot(out/'world.png')
        for key,wait in ((8,180),(16,180),(256,180),(256,180),(256,180),(64,60),(256,300)):tap(key,wait)
        saved=e.memory(0);(out/'showcase.sav').write_bytes(saved)
        e.close();e=None;cold(saved)
        check(canonical(e.memory())==expected,'Native save and cold Continue preserve all roster/AP/inventory/gil bytes')
        check(e.memory()[0x2190:0x2192]==original[0x2190:0x2192],'Early campaign stage preserved')
        e.screenshot(out/'cold-continue.png')
        for key in (8,256):tap(key)
        e.screenshot(out/'party.png')
        check(source.read_bytes()==seed,'Existing showcase source preserved')
    except BaseException as error:
        failure=repr(error)
        if e and e.frame:e.screenshot(out/'failed.png')
    finally:
        if e:e.close()
    report=dict(status='failed' if failure else 'passed',romSha1=meta['romSha1'],checks=checks,inputs=inputs,failure=failure,
        source=str(source),sourceSha256=sha(seed),sourceReportSha256=sha((source.parent/'report.json').read_bytes()),
        save=str(out/'showcase.sav'),saveSha256=sha((out/'showcase.sav').read_bytes()) if (out/'showcase.sav').exists() else None,scope=__doc__)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],checks=len(checks),failure=failure,report=str(out/'report.json'))))
    assert failure is None,failure
    (args.output_index or ROOT/'build/art/reviewed-integration'/('native-preview-save-latest.json' if args.native else 'preview-save-latest.json')).write_text(json.dumps(dict(report=str(out/'report.json'),sha256=sha((out/'report.json').read_bytes())),indent=2)+'\n')


if __name__=='__main__':main()
