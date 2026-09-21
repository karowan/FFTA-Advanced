"""Native all-class idle/miniature transport and exact source-stage rebuild."""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha,TILES,OAM
from native_miniatures import CONTAINER,decode
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
meta=json.loads((ROOT/'build/art/generated-classes/current.json').read_text())
rom=Path(meta['path']).read_bytes();base=Path(meta['source']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1'] and hashlib.sha1(base).hexdigest()==meta['baseRomSha1']
iw=(Path(meta['releaseSource']).parent/'fixture/battle-ready.iwram').read_bytes()
a=ARM(rom,iw);checks=[]
out=ROOT/'build/art/generated-classes/native-tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    for job in meta['jobs']:
        n=job['job'];resource=job['resource'];label=str(n)
        check(a.call(0x080c8570,n,2,4)==resource,label+' native job resolves owned actor')
        index=a.call(0x080c8570,n,2,6)
        check(0x419d60+32*index==job['nativePaletteReference'],label+' native source palette selector')
        check(a.call(0x08021054,resource)>=16,label+' native allocation fits generated32x32 tiles')
        old=job['sourceDescriptors'];new=job['descriptors']
        check(rom[new+24:new+12*job['slots']]==base[old+24:old+12*job['slots']],label+' all non-idle descriptors untouched')
        for seq in job['sequences']:
            offset=seq['target'];source=seq['source'];count=struct.unpack_from('<I',rom,offset)[0]
            check(count==struct.unpack_from('<I',base,source)[0]==4,label+' original frame count')
            for mode in ((0,3) if seq['slot']==0 else (1,2)):
                descriptor=a.call(0x08021004,resource,mode)
                check(a.word(descriptor)==0x08000000+offset,label+f' native facing{mode} descriptor')
            for frame,index in enumerate(seq['frames']):
                p=offset+4+frame*20;q=source+4+frame*20
                check(rom[p+8:p+20]==base[q+8:q+20],label+' frame command timing and metadata untouched')
                tiles,oam=struct.unpack_from('<II',rom,p)
                check(tiles+TILES==job['frames'][index]['tile'] and oam+OAM==job['oam'],label+' exact generated frame and OAM references')
                check(sha(rom[TILES+tiles:TILES+tiles+512])==job['frames'][index]['sha256'],label+' exact generated frame bytes')
        mini=job['miniature'];dest=0x02022020
        expected=decode(rom,meta['container'],mini['index'])
        check(sha(expected)==mini['sha256'],label+' generated miniature source')
        a.put(dest-32,b'\xa5'*704)
        check(a.call(0x08005318,0x08000000+meta['container'],dest,mini['index'],1)==0,label+' native miniature decode return')
        check(a.read(dest,640)==expected,label+' actual native miniature pixels')
        check(a.read(dest-32,32)==a.read(dest+640,32)==b'\xa5'*32,label+' miniature decode boundaries')
        check(rom[mini['mappingEntry']]==mini['index'],label+' independent actor to miniature mapping')
    for i in range(54):check(decode(rom,meta['container'],i)==decode(base,CONTAINER,i),f'Original miniature{i} preserved')
    for resource in meta['classResources']['resources']:
        if resource['lifetime']=='water':
            entry=meta['classResources']['table']+resource['id']*4
            check(rom[entry:entry+4]==base[entry:entry+4],str(resource['id'])+' water transport remains unchanged and unfinished')
    # Equipment-preview bytes are the already accepted implementation and exact
    # generated icon payload; reuse its runtime evidence if all bytes match.
    previous=json.loads((ROOT/'build/art/pipeline/current.json').read_text())
    old=Path(previous['path']).read_bytes();preview=meta['preview'];start=preview['reservation'][0]
    check(rom[start:start+preview['bytes']]==old[start:start+preview['bytes']],'Prior equipment-preview code and icons byte-exact')
    for change in preview['changes']:
        p=change['offset'];size=change['bytes'];check(rom[p:p+size]==old[p:p+size],'Prior equipment-preview hook byte-exact')
    from generated_class_transport import build
    rebuilt=build()
    check(rebuilt['romSha1']==meta['romSha1'] and Path(rebuilt['path']).read_bytes()==rom,'Exact all-class source-stage rebuild')
    report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,previewEvidenceRomSha1=previous['romSha1'],
        scope='Ten native actor/palette queries, all idle frame references/timing, preserved non-idle/water data, ten actual miniature decodes,54 original images, byte-exact prior preview code/icons, exact rebuild. Actual all-class display and final artwork remain separate.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),checks=checks),indent=2)+'\n');print('Artifacts: '+str(out));raise
