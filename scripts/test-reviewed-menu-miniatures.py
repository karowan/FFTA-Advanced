"""Native menu decoder, upload ownership, bright/dim routing and draw forwarding.

Declared component scenarios run under ARM emulation. Actual screen, concurrent
palette consumers and lifecycle acceptance use the separate menu UI test.
"""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
from native_miniatures import decode
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007800
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=1000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<menu miniature ARM>','exec'))

def main():
    index=ROOT/'build/art/reviewed-integration/menu-candidate.json';meta=json.loads(index.read_text())
    rom=Path(meta['path']).read_bytes();parent=Path(meta['source']).read_bytes();p=meta['components']['reviewedMenuMiniatures'];s=p['symbols']
    out=ROOT/'build/art/reviewed-integration/menu-tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    checks=[]
    def check(ok,label):
        assert ok,label
        checks.append(label)
    try:
        check(hashlib.sha1(rom).hexdigest()==meta['romSha1'] and hashlib.sha1(parent).hexdigest()==meta['baseRomSha1'],'Candidate and parent identities')
        check(sha(Path(p['parentManifest']).read_bytes())==p['parentManifestSha256'],'Immutable parent provenance')
        check(Path(meta['archivedManifest']).read_bytes()==index.read_bytes(),'Immutable candidate provenance')
        allowed=set()
        for patch in p['patches']:
            start=patch['offset'];end=start+patch['bytes'];allowed.update(range(start,end))
            check(sha(parent[start:end])==patch['beforeSha256'] and sha(rom[start:end])==patch['sha256'],'Exact patch '+patch['kind'])
        check(all(a==b or i in allowed for i,(a,b) in enumerate(zip(parent,rom))),'Only declared menu ROM bytes changed')
        a=ARM(rom,bytes(0x8000));dest=0x02022020
        for n in range(64):
            raw=decode(rom,p['container'],n)
            for residue in (0,4):
                a.put(dest-32,b'\xa5'*704);a.call(0x08005318,p['container']+0x08000000,dest,n,1,stack=STACK+residue)
                check(a.read(dest,640)==raw and a.read(dest-32,32)==a.read(dest+640,32)==b'\xa5'*32,f'Native bounded decoder {n}/{residue}')
            if n<54:check(raw==decode(parent,p['priorContainer'],n),f'Original miniature {n} unchanged')
            else:check(sha(raw)==p['jobs'][n-54]['tileSha256'],f'Exact reviewed pixels {n}')
        table=s['ffta_reviewed_menu_palette_table']-0x08000000
        for mode in range(4):
            old=struct.unpack_from('<2I',parent,0x393e78+mode*8);new=struct.unpack_from('<2I',rom,table+mode*8)
            check(old[0]==new[0],f'Original background palette mode {mode}')
            for bank in list(range(9))+[12]:
                q=old[1]-0x08000000+32*bank;r=new[1]-0x08000000+32*bank
                check(parent[q:q+32]==rom[r:r+32],f'Unowned menu palette {mode}/{bank}')
        reset=s['ffta_reviewed_menu_reset'];upload=s['ffta_reviewed_menu_upload'];bank=s['ffta_reviewed_menu_bank'];container=p['container']+0x08000000
        a.put(0x0203ece0,b'\xa5'*0x148);a.call(reset)
        for j in p['jobs']:
            for palette in range(6):
                a.call(reset);a.call(upload,j['index'],0x06011500,container)
                expected=j['normalBank'] if palette<3 else j['dimBank']
                check(a.call(bank,0x0894eae4,168,palette)==expected,f'Exact upload and bright/dim bank {j["job"]}/{palette}')
                check(a.call(bank,0x0894eaf8,168,palette)==palette,'Other layout cannot inherit miniature ownership')
                check(a.call(bank,0x0894eae4,188,palette)==palette,'Adjacent unowned tiles retain native bank')
                a.call(upload,0,0x06011500,container)
                check(a.call(bank,0x0894eae4,168,palette)==palette,'Original upload retires generated tile owner')
        for dest_bad in (0x0600ffe0,0x06017da0,0x06011501):
            a.call(reset);a.call(upload,54,dest_bad,container)
            check(a.word(0x0203ed04)==1 and a.call(bank,0x0894eae4,168,0)==0,'Invalid upload destination refused')
        a.call(reset);a.call(upload,54,0x06011500,container);a.call(upload,0,0x06011520,container)
        check(a.call(bank,0x0894eae4,168,0)==0,'Partial native overlap retires stale generated owner')
        check(a.read(0x0203ece0,32)==a.read(0x0203ee08,32)==b'\xa5'*32,'Miniature RAM fences intact')
        # Execute the actual native OAM producer for both wrapper and explicit
        # expected arguments; compare its complete double-buffered output.
        for n,j in enumerate(p['jobs']):
            for palette in (0,3):
                for residue in (0,4):
                    a=ARM(rom,bytes(0x8000));b=ARM(parent,bytes(0x8000));a.call(reset);a.call(upload,j['index'],0x06011500,container)
                    desc=bytearray(28);desc[16:21]=bytes((160,143,palette,1,0));struct.pack_into('<H',desc,22,168)
                    a.put(EQUIPMENT,desc)
                    expected=j['normalBank'] if palette<3 else j['dimBank']
                    b.put(STACK+residue,struct.pack('<7I',0,0,0,0,168,1,expected))
                    a.call(s['ffta_reviewed_menu_draw'],EQUIPMENT,0x0894eae4,stack=STACK+residue)
                    b.call(0x08001f34,0x0894eae4,160,143,0,stack=STACK+residue)
                    check(a.read(0x03000000,0x1000)==b.read(0x03000000,0x1000),f'Native OAM forwarding and ABI {j["job"]}/{palette}/{residue}')
        report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,scope=__doc__)
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
    except BaseException as error:
        (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],checks=checks,error=repr(error)),indent=2)+'\n');print(out);raise

if __name__=='__main__':main()
