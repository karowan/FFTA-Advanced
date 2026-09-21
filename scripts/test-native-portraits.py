"""Differential portrait export/import through the unmodified native decoders."""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
from native_portraits import PIXELS,LAYOUTS,PALETTES,entry,decode,encode,archive,layout
from native_miniatures import decode as palette_decode,encode as palette_encode
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=1000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
digest=hashlib.sha1(rom).hexdigest();assert digest=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
release=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
iw=(Path(release['path']).parent/'fixture/battle-ready.iwram').read_bytes()
a=ARM(rom,iw);checks=[]
out=ROOT/'build/art/native-reference/portrait-tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
def check(ok,label):
    assert ok,label
    checks.append(label)
def guard(raw):
    dest=0x02022020;a.put(dest-32,b'\xa5'*(len(raw)+64));return dest
def verify(dest,raw,label):
    actual=a.read(dest,len(raw))
    if actual!=raw:
        (out/'expected.bin').write_bytes(raw);(out/'actual.bin').write_bytes(actual)
    check(actual==raw,label+' exact native decoded bytes')
    check(a.read(dest-32,32)==a.read(dest+len(raw),32)==b'\xa5'*32,label+' destination boundaries')
try:
    records=[]
    for i in range(103):
        p=entry(rom,PIXELS,i);raw,end=decode(rom,p);objects,oam=layout(rom,entry(rom,LAYOUTS,i))
        check(a.call(0x080071a8,0x08000000+PIXELS,i)==0x08000000+p,f'{i} native archive lookup')
        check(a.call(0x080cb84c,i)==len(raw),f'{i} native decoded size')
        check(a.call(0x080cb968,i)==0x08000000+entry(rom,LAYOUTS,i),f'{i} native OAM lookup')
        for stack in (STACK,STACK-4):
            dest=guard(raw);a.call(0x080cb8b4,dest,i,stack=stack);verify(dest,raw,f'{i}/{stack:x} original')
            encoded=encode(raw);a.put(0x09e00000,encoded);dest=guard(raw)
            check(a.call(0x0800543c,dest,0x09e00000,stack=stack)==len(raw),f'{i}/{stack:x} re-encoded return size')
            verify(dest,raw,f'{i}/{stack:x} re-encoded')
        check(max(v['tile']*32+v['width']*v['height'] for v in objects)<=len(raw),f'{i} OAM ranges fit pixels')
        records.append(encoded)
    blob=archive(records,4);a.put(0x09e00000,blob)
    for i,record in enumerate(records):
        pointer=a.call(0x080071a8,0x09e00000,i)
        check(a.read(pointer,len(record))==record,f'{i} rebuilt archive native lookup')
    for mode,base in enumerate(PALETTES):
        a.put(0x02002fc2,bytes([mode]));records=[palette_decode(rom,base,i) for i in range(165)]
        encoded=palette_encode(records,96);a.put(0x09e00000,encoded)
        for i,raw in enumerate(records):
            check(len(raw)==96,f'{mode}/{i} 48-color source')
            dest=guard(raw);a.call(0x080cb8d4,dest,i);verify(dest,raw,f'{mode}/{i} original palette')
            dest=guard(raw);a.call(0x08005318,0x09e00000,dest,i,1);verify(dest,raw,f'{mode}/{i} re-encoded palette')
    report=dict(status='passed',romSha1=digest,checks=checks,scope='103 original portrait pixel/OAM records and495 palettes; Python/native differential decode, literal re-encode, native archive lookup, destination canaries and pixel decoder stack alignments. No generated portrait or rendered-consumer acceptance.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=digest,error=str(error),checks=checks),indent=2)+'\n');print('Artifacts: '+str(out));raise
