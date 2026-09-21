"""Native portrait decoder, palette routing and exact owned-payload boundaries."""
import argparse,ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
from native_portraits import entry,decode,layout,PIXELS,LAYOUTS,PALETTES
from native_miniatures import decode as palette_decode
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=1000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native portrait ARM>','exec'))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--manifest',type=Path,default=ROOT/'build/art/reviewed-integration/portrait-candidate.json')
    path=parser.parse_args().manifest;meta=json.loads(path.read_text())
    rom=Path(meta['path']).read_bytes();before=Path(meta['source']).read_bytes();p=meta['components']['portraits'];proof=meta['components']['reviewedPortraits']
    out=ROOT/'build/art/reviewed-integration/portrait-import-tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    checks=[]
    def check(ok,label):
        assert ok,label
        checks.append(label)
    try:
        check(hashlib.sha1(rom).hexdigest()==meta['romSha1'] and hashlib.sha1(before).hexdigest()==meta['baseRomSha1'],'Candidate and parent identity')
        check(sha(Path(proof['plan']).read_bytes())==proof['planSha256'],'Reviewed source plan identity')
        check(sha(Path(proof['parentManifest']).read_bytes())==proof['parentManifestSha256'],'Parent manifest identity')
        check(Path(meta['archivedManifest']).read_bytes()==path.read_bytes(),'Immutable manifest identity')
        allowed=set()
        for patch in proof['patches']:
            start=patch['offset'];end=start+patch['bytes'];allowed.update(range(start,end))
            check(sha(before[start:end])==patch['beforeSha256'] and sha(rom[start:end])==patch['sha256'],'Exact payload '+patch['kind'])
        check(len(rom)==len(before) and all(a==b or i in allowed for i,(a,b) in enumerate(zip(rom,before))),'Only declared ten portrait/placement and60 palette payloads changed')
        parent=json.loads(Path(proof['parentManifest']).read_text())['components']['portraits']
        a=ARM(rom,bytes(0x8000));dest=0x02022020
        for i in range(113):
            raw,_=decode(rom,entry(rom,p['pixelArchive'],i));old,_=decode(before,entry(before,parent['pixelArchive'],i))
            a.put(dest-32,b'\xa5'*(len(raw)+64));a.call(0x080cb8b4,dest,i)
            check(a.read(dest,len(raw))==raw and a.read(dest-32,32)==a.read(dest+len(raw),32)==b'\xa5'*32,f'{i} native pixel decode bounded')
            objects,oam=layout(rom,entry(rom,p['oamArchive'],i))
            if i<103:
                check(oam==layout(before,entry(before,parent['oamArchive'],i))[1],f'{i} original OAM unchanged')
                check(raw==old,f'{i} original portrait bytes unchanged')
            else:
                check(len(objects)==1 and objects[0]['x']==-56 and objects[0]['y']==-64 and objects[0]['width']==objects[0]['height']==64,f'{i} explicit menu portrait placement')
        for mode,archive in enumerate(p['paletteArchives']):
            a.put(0x02002fc2,bytes([mode]))
            for i in range(185):
                raw=palette_decode(rom,archive,i);a.put(dest-32,b'\xa5'*160);a.call(0x080cb8d4,dest,i)
                check(a.read(dest,96)==raw and a.read(dest-32,32)==a.read(dest+96,32)==b'\xa5'*32,f'{mode}/{i} native palette decode bounded')
                if i<165:check(raw==palette_decode(before,parent['paletteArchives'][mode],i),f'{mode}/{i} original palette unchanged')
        for j in p['jobs']:
            n=j['job'];race=a.call(0x080c8570,n,2,1);unit=bytearray(264);unit[4:8]=bytes((1,n,race,n));a.put(UNIT,unit)
            a.put(dest-32,b'\xa5'*4160);a.call(0x080cb868,dest,UNIT)
            check(sha(a.read(dest,4096))==j['pixelsSha256'],f'{n} real unit portrait path')
            check(a.read(dest-32,32)==a.read(dest+4096,32)==b'\xa5'*32,f'{n} real unit bounded upload')
            check(sha((ROOT/j['source']).read_bytes())==j['sourceSha256'],f'{n} archived image source')
            for flag,index in ((1,0),(0,1)):
                check(a.call(0x080cb7c0,UNIT,flag)==j['paletteIDs'][index],f'{n}/{flag} portrait palette selection')
        report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,scope='Native decoder and exact source/payload ownership. Rendered menu acceptance separate.')
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
    except Exception as error:
        (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),checks=checks),indent=2)+'\n');print(out);raise

if __name__=='__main__':main()
