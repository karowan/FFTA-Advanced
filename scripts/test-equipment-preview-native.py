"""Execute the real preview renderer for both native consumers and both pages."""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
from art_candidate import candidate
meta=candidate('build/art/equipment-preview/current.json','preview')
data=Path(meta['path']).read_bytes();assert hashlib.sha1(data).hexdigest()==meta['romSha1']
base=Path(meta['source']).read_bytes();assert hashlib.sha1(base).hexdigest()==meta['baseRomSha1']
if '--reviewed-entry' in sys.argv:
    from native_art import sha
    entry_index=ROOT/(sys.argv[sys.argv.index('--entry-index')+1] if '--entry-index' in sys.argv else 'build/art/reviewed-integration/action-entry-latest.json')
    index=json.loads(entry_index.read_text())
    entry_path=ROOT/index['report'];assert sha(entry_path.read_bytes())==index['sha256']
    entry=json.loads(entry_path.read_text());assert entry['status']=='passed'
    if '--entry-index' in sys.argv:assert entry['romSha1']==meta['romSha1']
    else:
        action=json.loads((ROOT/'build/art/reviewed-integration/action-candidate.json').read_text())
        assert entry['romSha1']==action['romSha1']
    # Native resident routines only: no actor RAM or serialized state is loaded.
    iw=(entry_path.parent/'ready.iwram').read_bytes()
else:
    fixture_source=Path(meta.get('fixtureSource') or meta['source'])
    fixture=fixture_source.parent/'fixture'
    fixture_proof=json.loads((fixture/'report.json').read_text())
    assert fixture_proof['passed'] and fixture_proof['romSha1']==hashlib.sha1(fixture_source.read_bytes()).hexdigest()
    assert (fixture/'frozen.gba').read_bytes()==fixture_source.read_bytes()
    iw=(fixture/'battle-ready.iwram').read_bytes()
m=ARM(data,iw);original=ARM(base,iw)
m.u.mem_map(0x06000000,0x18000)
out=ROOT/'build/art/equipment-preview/tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True,exist_ok=False);checks=[]
def check(ok,name):
    assert ok,name
    checks.append(name)
symbols=meta['symbols'];items=[265,1,383,391,399,407,415,423,431,439,453]
try:
    expected=[list(range(2,44)),list(range(116,126))]
    for page in range(2):
        ids=[m.call(symbols['ffta_preview_job'],page,i) for i in range(43)]
        check([v for v in ids if v]==expected[page],f'page{page} exact unique job enumeration')
    check(m.call(symbols['ffta_preview_job'],2,0)==0,'invalid page is empty')
    for shop in (0,1):
        mapoff=0x5800 if shop else 0x5000
        graphic=0xb000 if shop else 0x20
        hint=0xf000 if shop else 0x4800
        for item in items:
            for page in range(2):
                m.put(0x06000000,b'\xd7'*0x18000)
                before=m.read(0x02000080,0x1df0)
                m.call(symbols['ffta_preview_draw'],item,shop,page)
                vram=m.read(0x06000000,0x18000)
                allowed=set(range(graphic,graphic+len(expected[page])*256))|set(range(hint,hint+288))
                for y in range(2,19):allowed.update(range(mapoff+y*64+2,mapoff+y*64+58))
                allowed.update(range(mapoff+19*64+2,mapoff+19*64+20))
                allowed.update(range(mapoff+19*64+62,mapoff+19*64+64))
                check(all(v==0xd7 or i in allowed for i,v in enumerate(vram)),f'{shop}/{item}/{page} bounded VRAM writes')
                check(m.read(0x02000080,0x1df0)==before,f'{shop}/{item}/{page} owned roster inventory AP unchanged')
                check(struct.unpack_from('<H',vram,mapoff+19*64+62)[0]==0xa700|page,f'{shop}/{item}/{page} local page marker')
                for i,job in enumerate(expected[page]):
                    eligible=original.call(0x080cb5a8,job,item)
                    palette=original.call(0x080cba14,job)
                    if '--manifest' in sys.argv:
                        assembled=json.loads((ROOT/sys.argv[sys.argv.index('--manifest')+1]).read_text())
                        if 'approvedRound8' in assembled.get('components',{}):
                            row=next((j for j in assembled['components']['reviewedMenuBadges']['jobs'] if j['job']==job),None)
                            if row:
                                palette=row['badge']['paletteBank']
                                check(m.call(0x080cba14,job)==palette,f'{job} approved native badge palette')
                    if not eligible:palette-=6 if shop else 13
                    for y in range(2):
                        tile=(0x180 if shop else 1)+8*i+4*y
                        actual=struct.unpack_from('<4H',vram,mapoff+((2+i//7*3+y)*32+1+i%7*4)*2)
                        check(actual==tuple((palette<<12)+tile+x for x in range(4)),f'{shop}/{item}/{page}/{job}/{y} actual eligibility palette and tile coordinates')
                    original.call(0x080cb9e0,0x02030000,job)
                    old=original.read(0x02030000,256)
                    new=vram[graphic+i*256:graphic+(i+1)*256]
                    if page==0:check(new==old,f'{shop}/{item}/{job} original icon preserved')
                    else:check(new!=old,f'{shop}/{item}/{job} new class abbreviation replaces donor label')
    (out/'report.json').write_text(json.dumps(dict(status='passed',romSha1=meta['romSha1'],items=items,checks=checks,
        coverage='Native party/shop renderer, 52 jobs, eleven items, exact original icons, new labels, eligibility palettes, VRAM and ownership bounds. No real UI input or new artwork acceptance.'),indent=2)+'\n')
    print(json.dumps(dict(status='passed',checks=len(checks),romSha1=meta['romSha1'],report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,romSha1=meta['romSha1']),indent=2)+'\n')
    raise
