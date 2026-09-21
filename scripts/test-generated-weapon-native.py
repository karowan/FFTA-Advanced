"""Held-weapon resource identity, native getters/lookup and sequence contract."""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
from generated_weapon_transport import build
out=ROOT/'build/art/generated-weapon/native-tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    m=build();rom=Path(m['path']).read_bytes();base=Path(m['source']).read_bytes()
    sys.path.insert(0,str(ROOT/'tools/arm-python'))
    from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
    from unicorn.arm_const import *
    UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
    tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<held native ARM>','exec'))
    iw=(Path(m['releaseSource']).parent/'fixture/battle-ready.iwram').read_bytes();a=ARM(rom,iw);b=ARM(base,iw)
    check(hashlib.sha1(rom).hexdigest()==m['romSha1'],'Authenticated held-axe candidate')
    oldtable=struct.unpack_from('<I',base,0x2102c)[0]-0x08000000;oldsizes=struct.unpack_from('<I',base,0x21060)[0]-0x08000000
    check(rom[m['table']:m['table']+276*4]==base[oldtable:oldtable+276*4],'All276 previous animation references exact')
    check(rom[m['sizeTable']:m['sizeTable']+276*2]==base[oldsizes:oldsizes+276*2],'All276 previous allocation sizes exact')
    for item in range(461):
        for selector in range(10):
            before=b.call(0x080ca7a4,item,selector);after=a.call(0x080ca7a4,item,selector)
            check(after==(276 if item in m['items'] and selector==9 else before),f'{item}/{selector} native item consumer')
        p=m['itemTable']+32*item;before=base[p:p+32];after=rom[p:p+32]
        check(after[:14]==before[:14] and after[16:]==before[16:],f'{item} gameplay and remaining item bytes exact')
    check(a.call(0x08021054,276)==b.call(0x08021054,128)==16,'Native resource allocation size preserved')
    mapping={s['source']:s['target'] for s in m['sequences']}
    for mode in range(20):
        old=b.read(b.call(0x08021004,128,mode),12);new=a.read(a.call(0x08021004,276,mode),12)
        values=struct.unpack('<3I',old)
        expected=struct.pack('<3I',*[mapping[v-0x08000000]+0x08000000 if v else 0 for v in values])
        check(new==expected,f'{mode} actual native held-weapon descriptor includes both channels')
    for s in m['sequences']:
        for f in s['frames']:
            p=4+20*f['index'];old=base[s['source']+p:s['source']+p+20];new=rom[s['target']+p:s['target']+p+20]
            check(old==new if f['commandOnly'] else old[4:]==new[4:],f'{s["source"]:x}/{f["index"]} sentinel/OAM/attachment/commands/timing preserved')
            if not f['commandOnly']:check(sha(rom[f['tile']:f['tile']+128])==m['pixelsSha256'] and rom[f['tile']+128:f['tile']+32*f['tiles']]==bytes(32*(f['tiles']-4)),f'{s["source"]:x}/{f["index"]} generated axe and bounded transparent padding')
    check(Path(build()['path']).read_bytes()==rom,'Exact held-resource build reproduction')
    report=dict(status='passed',romSha1=m['romSha1'],checks=checks,scope='Native item selectors0..9 for461 IDs, all gameplay bytes,277-entry table preservation,20 native held descriptor lookups and both sequence channels including sentinel frames; exact rebuild. Actual native rendered swing and new artwork acceptance separate.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n');print('Artifacts: '+str(out));raise
