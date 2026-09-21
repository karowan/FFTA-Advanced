"""Actual native resource selection and complete reviewed action byte contracts.

Executes the native resource/mode selectors in ARM emulation; this does not
claim live battle playback or approve provisional generated images.
"""
import argparse
import ast
import datetime
import hashlib
import json
import struct
import sys
from pathlib import Path
from native_art import ROOT, TILES, OAM, sha, layout
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007800
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native selector ARM>','exec'))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--manifest',type=Path,default=ROOT/'build/art/reviewed-integration/action-candidate.json')
    path=parser.parse_args().manifest;meta=json.loads(path.read_text())
    proof=meta['components']['reviewedActions'];rom=Path(meta['path']).read_bytes();before=Path(meta['source']).read_bytes()
    out=ROOT/'build/art/reviewed-integration/import-tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    checks=[];failure=None
    def check(ok,label):
        assert ok,label
        checks.append(label)
    try:
        check(hashlib.sha1(rom).hexdigest()==meta['romSha1'],'Candidate ROM authentication')
        check(hashlib.sha1(before).hexdigest()==meta['baseRomSha1'],'Parent ROM authentication')
        check(sha((ROOT/proof['catalog']).read_bytes())==proof['catalogSha256'],'Exact art catalog authentication')
        check(sha(Path(proof['sourceManifest']).read_bytes())==proof['sourceManifestSha256'],'Exact parent manifest authentication')
        if 'archivedManifest' in meta:
            check(Path(meta['archivedManifest']).read_bytes()==path.read_bytes(),'Immutable candidate manifest authentication')
        for asset in proof['assets']:
            check(sha((ROOT/asset['source']).read_bytes())==asset['sourceSha256'],'Immutable imported artwork source '+str((asset['job'],asset['pose'])))
        a=ARM(rom,bytes(0x8000));b=ARM(before,bytes(0x8000))
        poses={(p['job'],p['pose']):p for p in proof['assets']}
        table=proof['table'];start,end=proof['used']
        allowed=set(range(start,end));replaced=draws=controls=0
        job_table=struct.unpack_from('<I',before,0xc8598)[0]-0x08000000
        for change in proof.get('nativeSelectorChanges',[]):
            offset=job_table+52*change['job']+11
            check(change['offset']==offset and 116<=change['job']<=125,'Owned native class selector byte')
            check(before[offset]==change['before'] and rom[offset]==change['after'],'Declared native selector edit')
            check(rom[offset]&15 in (0,1,2) and rom[offset]>>4 in (0,1,2),'Existing native palettes only')
            allowed.add(offset)
        for segment in proof['segments']:
            p=segment['offset'];check(sha(rom[p:p+segment['bytes']])==segment['sha256'],'Exact segment '+hex(p))
        for resource in proof['resources']:
            rid=resource['id'];allowed.update(range(table+rid*4,table+rid*4+4))
            check(a.call(0x08021054,rid)==b.call(0x08021054,rid)==16,'Native 16-tile allocation '+str(rid))
            for mode in range(168):
                p=a.call(0x08021004,rid,mode);q=b.call(0x08021004,rid,mode)
                new=a.read(p,12);old=b.read(q,12)
                check(new[4:]==old[4:] and bool(struct.unpack_from('<I',new)[0])==bool(struct.unpack_from('<I',old)[0]),'Native mode/null/metadata '+str((rid,mode)))
            for seq in resource['sequences']:
                p=seq['target'];q=seq['source'];count=struct.unpack_from('<I',rom,p)[0]
                check(count==struct.unpack_from('<I',before,q)[0],'Sequence count '+str((rid,seq['slot'])))
                by_index={f['index']:f for f in seq['frames']}
                for i in range(count):
                    new=rom[p+4+20*i:p+24+20*i];old=before[q+4+20*i:q+24+20*i]
                    check(new[8:]==old[8:],'All native commands/timing/attachments '+str((rid,seq['slot'],i)))
                    if new[9]!=1:
                        check(new==old,'Control-only record unchanged');controls+=1;continue
                    draws+=1;record=by_index[i]
                    if not record['replaced']:
                        check(new==old,'Missing draft drawing explicitly retains prior bytes');continue
                    asset=poses[(resource['job'],record['pose'])];replaced+=1
                    t,o=struct.unpack_from('<II',new);objects,_=layout(rom,OAM+o)
                    check(TILES+t==asset['tile'] and OAM+o==asset['oam'],'Exact pose binding')
                    check(sha(rom[TILES+t:TILES+t+512])==asset['tileSha256'],'Exact packed 4bpp drawing')
                    check(len(objects)==1 and objects[0]['width']==objects[0]['height']==32 and objects[0]['tile']==0,'Single bounded 32px body')
                    check(objects[0]['y']+asset['generatedBottom']==asset['nativeBottom'],'Native baseline preserved')
                    check(objects[0]['x']==asset['x'],'Preserved worksheet anchor translation')
        check((draws,replaced,controls)==(proof['drawRecords'],proof['importedDrawRecords'],proof['controlRecords']),'Complete graph accounting')
        check(all(x==y or i in allowed for i,(x,y) in enumerate(zip(rom,before))),'Only owned graphics table entries, declared native class selectors and reservation changed')
        for rid in range(256):
            check(rom[table+rid*4:table+rid*4+4]==before[table+rid*4:table+rid*4+4],'Original actor pointer '+str(rid))
        ready=not proof['missing'] and not proof['provisional']
        check(meta['reviewedArtPilot']['fullAnimationCoverage']==ready,'Incomplete art cannot claim full coverage')
        check(not meta['reviewedArtPilot']['productionAccepted'],'Import proof does not claim production acceptance')
    except BaseException as error:failure=repr(error)
    report=dict(status='failed' if failure else 'passed',romSha1=meta['romSha1'],manifestSha256=sha(path.read_bytes()),
                checks=checks,failure=failure,scope=__doc__)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],checks=len(checks),failure=failure,report=str(out/'report.json'))))
    assert failure is None,failure


if __name__=='__main__':main()
