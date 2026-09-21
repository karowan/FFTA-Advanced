"""Clean integration-build reconciliation and affected original map streams."""
import datetime,hashlib,json,struct
from pathlib import Path
from native_art import ROOT,sha
from ffta_maps import Maps,COUNT
from native_table_literals import authenticate,NATIVE_TABLE_LITERALS

out=ROOT/'build/art/native-repair-complete/data-tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];observations={}
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();authenticate(clean)
    meta=json.loads((ROOT/'build/art/native-repair-complete/current.json').read_text());rom=Path(meta['path']).read_bytes()
    check(hashlib.sha1(rom).hexdigest()==meta['romSha1'],'Authenticated repaired artwork candidate')
    repair=json.loads((ROOT/'build/art/native-data-repair/current.json').read_text());shipping=Path(repair['releaseSource']).read_bytes()
    check(hashlib.sha1(shipping).hexdigest()==repair['releaseSha1'],'Authenticated historical release')
    report_path=ROOT/'build/reproducibility/20260917T225624.978478Z/report.json';report=json.loads(report_path.read_text())
    check(report['passed'] and len(report['steps'])==8 and all(x['exitCode']==0 for x in report['steps']),'Fresh eight-stage source/tool/clean-ROM assembly passed')
    builtmeta=json.loads(Path(report['result']['manifest']).read_text());built=Path(builtmeta['path']).read_bytes()
    check(hashlib.sha1(built).hexdigest()==builtmeta['romSha1']==report['result']['romSha1'],'Authenticated full clean-build result')
    for name in ('scripts/build-integrated-jobs.py','scripts/native_table_literals.py','scripts/arm_literal_relocations.py','scripts/equipment_preview.py'):
        check(sha((ROOT/name).read_bytes())==report['sources'][name],name+' clean build used current production source')
    for s in report['steps']:check(sha(Path(s['log']).read_bytes())==s['logSha256'],s['stage']+' complete build log authenticated')
    expected=bytearray(shipping)
    for c in repair['records']:struct.pack_into('<I',expected,c['offset'],c['old'])
    # The current source also includes the previously accepted equipment-grid
    # module. Reconcile it separately rather than misattribute4458 bytes to the
    # relocation fix, or require equality with the known-corrupt old release.
    previews=[c for c in builtmeta['changes'] if c['kind']=='Paged native equipment preview'];assert len(previews)==1
    preview=previews[0];start,end=preview['reservation'];size=preview['bytes']
    check(expected[start:end]==b'\xff'*(end-start) and built[start+size:end]==b'\xff'*(end-start-size),'Bounded independent preview reservation')
    expected[start:start+size]=built[start:start+size]
    for c in preview['changes']:
        p=c['offset'];n=c['bytes'];check(expected[p:p+n].hex()==c['expected'],c['name']+' authenticated prior preview hook')
        expected[p:p+n]=built[p:p+n]
    check(bytes(expected)==built,'Full clean build equals repaired original plus declared existing preview only')
    collisions=[c for c in builtmeta['changes'] if c['kind']=='preserved native data collision']
    check({c['offset'] for c in collisions}=={c['offset'] for c in repair['records']},'Full clean builder preserved all139 exact data collisions')
    for p in NATIVE_TABLE_LITERALS:check(built[p:p+4]==shipping[p:p+4],f'{p:x} clean-build native table reference unchanged')
    # ffta_maps normally accepts only the clean image. Authenticate the other
    # images above, then explicitly create separate decoder views; do not relax
    # its normal production constructor or replace a file under test.
    native=Maps(clean);fixed=object.__new__(Maps);fixed.rom=rom;old=object.__new__(Maps);old.rom=shipping
    affected={};hits={};old_differences=[]
    for index in range(COUNT):
        for field in (4,8,16):
            for kind,stream in native.components(index,field):
                if stream.codec=='packed':continue # broad upper bound is not an exact consumed extent
                offsets=[c['offset'] for c in repair['records'] if stream.address<c['offset']+4 and c['offset']<stream.end]
                if offsets:
                    affected[index,field]=offsets
                    for p in offsets:hits.setdefault(p,[]).append([index,field])
    check(len(hits)==11 and len(affected)==15,'Exactly11 repaired words affect15 known compressed map component consumers')
    for (index,field),offsets in affected.items():
        method='planar' if field==4 else 'clipping' if field==8 else 'heights'
        want=getattr(native,method)(index);actual=getattr(fixed,method)(index)
        check(actual==want,f'{index}/{method} restored decoded original component exactly')
        row=dict(map=index,field=field,method=method,offsets=offsets,restoredSha256=sha(actual),bytes=len(actual))
        try:
            previous=getattr(old,method)(index);row['previousSha256']=sha(previous);different=previous!=want
        except Exception as error:
            row['previousError']=repr(error);different=True
        check(different,f'{index}/{method} historical corruption independently observable')
        old_differences.append(row)
    observations=dict(rebuildReport=str(report_path),rebuildReportSha256=sha(report_path.read_bytes()),rebuiltRomSha1=builtmeta['romSha1'],mapComponents=old_differences)
    result=dict(status='passed',romSha1=meta['romSha1'],checks=checks,observations=observations,
        scope='Authenticated fresh complete integration build; only139 data-word repair plus separately declared prior preview module differs from shipping.15 affected map clipping/arrangement consumers decode exactly to clean originals and expose historical corruption. Static map data proof, not native movement/rendering or full campaign acceptance; other restored-data consumers still unclassified.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,observations=observations),indent=2)+'\n');print('Artifacts: '+str(out));raise
