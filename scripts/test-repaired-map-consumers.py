"""Run affected map component loaders in the assembled art candidate.

Uses the existing declared native-loader boot probe and retained clean-ROM
outputs. No Python decoder replaces native execution; the probe changes only
the reset vector and a checked empty private ROM reservation. This is loader
acceptance, not mission traversal or full campaign playback.
"""
import datetime,hashlib,json,runpy,struct,subprocess
from pathlib import Path
from native_art import ROOT,sha
from ffta_maps import Maps,COUNT,CLEAN_SHA1

out=ROOT/'build/art/repaired-map-consumers'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True);checks=[];observations=[];e=None

def check(ok,label):
    assert ok,label
    checks.append(label)

try:
    manifestpath=ROOT/'build/art/generated-effect/current.json';meta=json.loads(manifestpath.read_text())
    rom=Path(meta['path']).read_bytes();clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    check(hashlib.sha1(rom).hexdigest()==meta['romSha1'],'Authenticated assembled candidate')
    check(hashlib.sha1(clean).hexdigest()==CLEAN_SHA1,'Authenticated native revision')
    repairpath=ROOT/'build/art/native-data-repair/current.json';repair=json.loads(repairpath.read_text())
    records=repair['records'];check(len(records)==139,'Exact previously reviewed repair set')
    for row in records:
        p=row['offset'];check(rom[p:p+4]==clean[p:p+4]==struct.pack('<I',row['old']),f'{p:x} original bytes restored in assembled ROM')
    native=Maps(clean);affected={};hits={}
    for index in range(COUNT):
        for field in (4,8,16):
            for kind,stream in native.components(index,field):
                if stream.codec=='packed':continue
                offsets=[r['offset'] for r in records if stream.address<r['offset']+4 and r['offset']<stream.end]
                if offsets:
                    affected.setdefault(index,{}).setdefault(field,set()).update(offsets)
                    for p in offsets:hits.setdefault(p,set()).add(index)
    check(len(hits)==11 and sum(map(len,affected.values()))==15,'Exact affected compressed map component set')
    retained=ROOT/'build/expansion/terrain'/CLEAN_SHA1/'native-loader'
    retainedpath=retained/'report.json';prior=json.loads(retainedpath.read_text())
    check(prior['passed'] and prior['cleanRomSha1']==CLEAN_SHA1 and len(prior['maps'])==COUNT,'Retained complete native clean-map reference')
    # The three recursive loaders and map record table remain the native code
    # and pointers, not newly supplied decompression/geometry implementations.
    check(rom[0x1f1a8:0x1f584]==clean[0x1f1a8:0x1f584],'Original recursive native loader instructions unchanged')
    check(rom[0x569104:0x569104+88*COUNT]==clean[0x569104:0x569104+88*COUNT],'All native map records unchanged')
    address=0x1fc0000;source=ROOT/'scripts/terrain-native-probe.s'
    prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
    for tool,args in [('as',['-mcpu=arm7tdmi',str(source),'-o',str(out/'probe.o')]),
                      ('ld',['-Ttext='+hex(0x08000000+address),'-e','_start',str(out/'probe.o'),'-o',str(out/'probe.elf')]),
                      ('objcopy',['-O','binary',str(out/'probe.elf'),str(out/'probe.bin')])]:
        subprocess.run([prefix+tool+'.exe',*args],check=True)
    code=(out/'probe.bin').read_bytes();check(rom[address:address+len(code)]==b'\xff'*len(code),'Probe uses empty isolated ROM space')
    probe=bytearray(rom);probe[address:address+len(code)]=code
    struct.pack_into('<I',probe,0,0xea000000|((address-8)//4));path=out/'native-map-probe.gba';path.write_bytes(probe)
    E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];e=E(path);e.run(2)
    check(struct.unpack_from('<I',e.memory(),0x3ffe4)[0]==1,'Native probe booted')
    for ordinal,index in enumerate(sorted(affected)):
        e.set_memory(0x3ffe0,struct.pack('<I',index+1));request=[index+1,30]
        for frame in range(30):
            e.run(1);ram=e.memory()
            if struct.unpack_from('<I',ram,0x3ffe0)[0]==0:break
        check(struct.unpack_from('<II',ram,0x3ffe0)==(0,ordinal+2),f'{index} original map loaders completed')
        old=next(v for v in prior['maps'] if v['map']==index);parts={}
        for name,p,n in [('arrangement',0x91a0,0x4000),('height',0x7cb0,0x200),('clipping',0xd1a0,0x2000)]:
            reference=(retained/f'map-{index:03}-{name}.bin').read_bytes();actual=ram[p:p+n]
            check(hashlib.sha1(reference).hexdigest()==old[name+'Sha1'] and len(reference)==n,f'{index}/{name} authenticated retained original')
            (out/f'map-{index:03}-{name}.bin').write_bytes(actual)
            check(actual==reference,f'{index}/{name} native candidate output equals original')
            parts[name]=dict(bytes=n,sha256=sha(actual),originalSha1=old[name+'Sha1'])
        observations.append(dict(map=index,request=request,frames=frame+1,affected={str(k):sorted(v) for k,v in affected[index].items()},parts=parts))
    result=dict(status='passed',romSha1=meta['romSha1'],probeRomSha1=hashlib.sha1(probe).hexdigest(),checks=checks,
        sourceManifestSha256=sha(manifestpath.read_bytes()),repairManifestSha256=sha(repairpath.read_bytes()),
        retainedReport=str(retainedpath),retainedReportSha256=sha(retainedpath.read_bytes()),probeSourceSha256=sha(source.read_bytes()),maps=observations,
        scope='All139 repaired words exact in assembled candidate; affected maps execute original recursive arrangement/clipping/height loaders through mGBA BIOS and equal authenticated retained native clean outputs. Isolated reset probe only. No rendered terrain traversal, campaign replay or classification of other data consumers.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),maps=len(observations),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,maps=observations),indent=2)+'\n');print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
