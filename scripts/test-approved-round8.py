"""Authenticate approval/import boundaries and execute native portrait routing."""
# See src/art/native-ui-review/README.md, sections 6-7. These checks prove exact
# import and native routing, not aesthetic quality or full campaign acceptance.
# Keep __doc__ stable: it is recorded as the historical report scope below.
import ast, datetime, hashlib, json, struct, sys
from pathlib import Path
from PIL import Image
from native_art import ROOT, sha, pack_tiles, tile_image
from native_portraits import entry, decode, pack, PALETTES
from native_miniatures import decode as palette_decode

sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=1000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native portrait ARM>','exec'))


def main():
    folder=ROOT/'build/art/approved-first-pass-2026-09-20'
    path=folder/'candidate.json';meta=json.loads(path.read_text())
    proof=meta['components']['approvedRound8'];planpath=Path(proof['plan']);plan=json.loads(planpath.read_text())
    rom=Path(meta['path']).read_bytes();before=Path(meta['source']).read_bytes()
    out=folder/'tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    checks=[]
    def check(ok,label):
        assert ok,label
        checks.append(label)
    try:
        check(hashlib.sha1(rom).hexdigest()==meta['romSha1'] and hashlib.sha1(before).hexdigest()==meta['baseRomSha1'],'Candidate and baseline authenticated')
        check(sha(planpath.read_bytes())==proof['planSha256'],'Exact user approval receipt')
        check(sha((ROOT/plan['review']['path']).read_bytes())==plan['review']['sha256'],'Exact approved review data')
        allowed=set()
        for p in proof['patches']:
            start=p['offset'];end=start+p['bytes'];allowed.update(range(start,end))
            check(sha(before[start:end])==p['beforeSha256'] and sha(rom[start:end])==p['sha256'],'Declared patch '+p['kind'])
        check(len(before)==len(rom) and all(a==b or i in allowed for i,(a,b) in enumerate(zip(before,rom))),'Every other ROM byte unchanged, including animation records, palettes and code')
        native=ARM(rom,bytes(0x8000));old=ARM(before,bytes(0x8000))
        portrait=meta['components']['portraits'];badge=meta['components']['reviewedMenuBadges'];dest=0x02022020
        for i in range(113):
            raw,_=decode(rom,entry(rom,portrait['pixelArchive'],i))
            native.put(dest-32,b'\xa5'*(len(raw)+64));native.call(0x080cb8b4,dest,i)
            check(native.read(dest,len(raw))==raw and native.read(dest-32,32)==native.read(dest+len(raw),32)==b'\xa5'*32,f'Portrait{i} native decoder and bounds')
        for row in plan['jobs']:
            job=row['job'];j=next(x for x in portrait['jobs'] if x['job']==job)
            approved=Image.open(ROOT/row['portrait']['path'])
            transport=Image.open(j['nativeImage'])
            # Invert the import's fixed placement, OAM compensation and index
            # shift. This must recover every approved pixel without resampling.
            recovered=transport.crop((8,8,56,64)).transpose(Image.Transpose.FLIP_LEFT_RIGHT).point(lambda v:v-96 if v else 0)
            check(recovered.tobytes()==approved.tobytes(),f'{job} exact approved48x56, no resampling, native flip compensated')
            check(pack(transport)==decode(rom,entry(rom,portrait['pixelArchive'],j['portrait']))[0],f'{job} reviewed pixels in ROM')
            unit=bytearray(264);race=native.call(0x080c8570,job,2,1);unit[4:8]=bytes([1,job,race,job]);native.put(UNIT,unit)
            native.call(0x080cb868,dest,UNIT)
            check(sha(native.read(dest,4096))==j['pixelsSha256'],f'{job} actual unit portrait upload')
            for flag in (0,1):
                check(native.call(0x080cb7c0,UNIT,flag)==row['portraitPalette'],f'{job}/{flag} selects existing native palette')
            for mode,archive in enumerate(portrait['paletteArchives']):
                native.put(0x02002fc2,bytes([mode]));native.call(0x080cb8d4,dest,row['portraitPalette'])
                check(native.read(dest,96)==palette_decode(before,PALETTES[mode],row['portraitPalette']),f'{job}/{mode} original palette bytes reach native decoder')
                check(palette_decode(rom,archive,row['portraitPalette'])==palette_decode(before,archive,row['portraitPalette']),f'{job}/{mode} palette archive unchanged')
            image=Image.open(ROOT/row['badge']['path']);at=badge['offset']+(job-116)*256
            check(pack_tiles(image,8)==rom[at:at+256],f'{job} exact approved badge pixels in ROM')
            check(native.call(0x080cba14,job)==row['badgeBank'],f'{job} reviewed existing badge palette')
        for job in range(126):
            if job==124:continue
            check(native.call(0x080cba14,job)==old.call(0x080cba14,job),f'{job} other badge palette selection unchanged')
        for row in plan['walk']:
            image=Image.open(ROOT/row['image']['path'])
            a=next(x for x in meta['components']['reviewedActions']['assets'] if x['job']==116 and x['pose']==row['pose'])
            check(pack_tiles(image,16)==rom[a['tile']:a['tile']+512],row['pose']+' exact approved native movement pixels')
        report=dict(status='passed',romSha1=meta['romSha1'],manifestSha256=sha(path.read_bytes()),checks=checks,scope=__doc__)
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
    except Exception as error:
        (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),checks=checks),indent=2)+'\n')
        raise


if __name__=='__main__': main()
