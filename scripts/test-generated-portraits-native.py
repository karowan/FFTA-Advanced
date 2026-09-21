"""Native portrait routing, original preservation and exact append-stage rebuild."""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
from native_portraits import *
from native_miniatures import decode as palette_decode,encode as palette_encode
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=1000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
meta=json.loads((ROOT/'build/art/generated-portraits/current.json').read_text())
rom=Path(meta['path']).read_bytes();base=Path(meta['source']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1'] and hashlib.sha1(base).hexdigest()==meta['baseRomSha1']
iw=(Path(meta['releaseSource']).parent/'fixture/battle-ready.iwram').read_bytes()
a=ARM(rom,iw);b=ARM(base,iw);checks=[]
out=ROOT/'build/art/generated-portraits/native-tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
def check(ok,label):
    assert ok,label
    checks.append(label)
def decode_native(raw,pointer,label):
    dest=0x02022020;a.put(dest-32,b'\xa5'*(len(raw)+64));a.call(0x080cb8b4,dest,pointer)
    check(a.read(dest,len(raw))==raw,label+' native pixels')
    check(a.read(dest-32,32)==a.read(dest+len(raw),32)==b'\xa5'*32,label+' bounded native pixels')
try:
    for i in range(113):
        raw,_=decode(rom,entry(rom,meta['pixelArchive'],i));_,oam=layout(rom,entry(rom,meta['oamArchive'],i))
        decode_native(raw,i,str(i));check(a.call(0x080cb84c,i)==len(raw),str(i)+' allocation size')
        p=a.call(0x080cb968,i);check(a.read(p,len(oam))==oam,str(i)+' native layout')
        if i<103:
            check(raw==decode(base,entry(base,PIXELS,i))[0],str(i)+' original pixels unchanged')
            check(oam==layout(base,entry(base,LAYOUTS,i))[1],str(i)+' original layout unchanged')
    for mode,archive in enumerate(meta['paletteArchives']):
        a.put(0x02002fc2,bytes([mode]))
        for i in range(185):
            raw=palette_decode(rom,archive,i);dest=0x02022020;a.put(dest-32,b'\xa5'*160);a.call(0x080cb8d4,dest,i)
            check(a.read(dest,96)==raw and a.read(dest-32,32)==a.read(dest+96,32)==b'\xa5'*32,f'{mode}/{i} native bounded palette')
            if i<165:check(raw==palette_decode(base,PALETTES[mode],i),f'{mode}/{i} original palette unchanged')
    for job in meta['jobs']:
        n=job['job'];race=a.call(0x080c8570,n,2,1);unit=bytearray(264);unit[4:8]=bytes((1,n,race,n));a.put(UNIT,unit)
        check(a.call(0x080c8570,n,2,9)==job['portrait'],str(n)+' new generic portrait selector')
        raw=decode(rom,entry(rom,meta['pixelArchive'],job['portrait']))[0];dest=0x02022020
        a.put(dest-32,b'\xa5'*4160);a.call(0x080cb868,dest,UNIT)
        check(a.read(dest,4096)==raw and sha(raw)==job['pixelsSha256'],str(n)+' real unit pixel path')
        check(a.read(dest-32,32)==a.read(dest+4096,32)==b'\xa5'*32,str(n)+' unit path boundaries')
        check(a.call(0x080cb808,UNIT)==4096,str(n)+' unit allocation size')
        check(a.call(0x080cb928,UNIT)==0x08000000+entry(rom,meta['oamArchive'],job['portrait']),str(n)+' unit layout path')
        for flag,index in ((1,0),(0,1)):
            check(a.call(0x080cb7c0,UNIT,flag)==job['paletteIDs'][index],str(n)+' unit palette alternative')
        # Authentic named identities from the isolated showcase: Marche and
        # Montblanc, only with their own race's expansion jobs.
        for appearance,character,character_race in ((2,80,1),(8,82,5)):
            if race!=character_race:continue
            unit[4:8]=bytes((appearance,character,race,n));a.put(UNIT,unit);b.put(UNIT,unit)
            check(a.call(0x080cb808,UNIT)==b.call(0x080cb808,UNIT),f'{n}/{character} fixed portrait size unchanged')
            size=a.call(0x080cb808,UNIT);a.call(0x080cb868,dest,UNIT);b.call(0x080cb868,dest,UNIT)
            check(a.read(dest,size)==b.read(dest,size),f'{n}/{character} fixed portrait pixels unchanged')
            for flag in (0,1):check(a.call(0x080cb7c0,UNIT,flag)==b.call(0x080cb7c0,UNIT,flag),f'{n}/{character}/{flag} named palette unchanged')
    from native_miniatures import encode as mini_encode,decode as mini_decode
    oldmeta=json.loads((Path(meta['source']).parent/'manifest.json').read_text())
    images=[mini_decode(base,oldmeta['container'],i) for i in range(64)]
    check(sha(mini_encode(images))==oldmeta['containerSha256'],'Generalized encoder preserves prior miniature payload exactly')
    from generated_portrait_transport import build
    rebuilt=build();check(rebuilt['romSha1']==meta['romSha1'] and Path(rebuilt['path']).read_bytes()==rom,'Exact generated portrait rebuild')
    report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,scope='Native113-entry pixel/OAM and555 palette routing, original preservation, ten generic unit consumers and fixed-character differential controls, unchanged miniature encoding and exact rebuild. Rendered menu acceptance separate.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),checks=checks),indent=2)+'\n');print('Artifacts: '+str(out));raise
