"""Reconcile current native graphics consumers and reusable action contracts.

Read-only ROM/data audit. No emulator, build, generated artwork or player files.
This proves final-stage dependency boundaries; runtime reports remain evidence
only for their documented scenarios, not exhaustive spell/encounter coverage.
"""
import datetime, hashlib, json, struct
from pathlib import Path
from native_art import ROOT, TILES, sha

manifest=ROOT/'build/art/connected/a28b624bb13c8f2f2597a4d4bd3999b17c234b99/manifest.json'
meta=json.loads(manifest.read_text());parts=meta['components'];stage=parts['nativePaletteTransport']
rom=Path(meta['path']).read_bytes();parent=Path(stage['source']).read_bytes()
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
gameplay=Path(parts['livePalette']['source']).read_bytes()
out=ROOT/'build/art/native-consumer-audit'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];resources=[];hooks=[]
word=lambda data,p:struct.unpack_from('<I',data,p)[0]
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    check(hashlib.sha1(rom).hexdigest()==meta['romSha1']=='a28b624bb13c8f2f2597a4d4bd3999b17c234b99','Current candidate authenticated')
    check(hashlib.sha1(parent).hexdigest()==stage['baseRomSha1']=='5a14e6c7b69f9f9984a6965faf5740d3b318e41a','Completed-action parent authenticated')
    check(hashlib.sha1(clean).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9' and hashlib.sha1(gameplay).hexdigest()==parts['livePalette']['baseRomSha1'],'Original renderer and clean US authenticated')
    allowed=bytearray(len(rom));a,b=stage['used'];allowed[a:b]=b'\1'*(b-a)
    for patch in stage['patches']:
        p=patch['offset'];n=patch['bytes'];allowed[p:p+n]=b'\1'*n
        check(parent[p:p+n].hex()==patch['before'] and rom[p:p+n].hex()==patch['after'],'Exact final-stage patch '+hex(p))
    check(len(rom)==len(parent) and all(x==y or allowed[p] for p,(x,y) in enumerate(zip(parent,rom))),'Every byte outside authenticated final-stage data/patches retained')
    for segment in stage['segments']:
        p=segment['offset'];n=segment['bytes'];check(sha(rom[p:p+n])==segment['sha256'],'Exact converted segment '+hex(p))
    current_table=word(rom,0x2102c)-0x08000000;old_table=word(parent,0x2102c)-0x08000000
    current_sizes=word(rom,0x21060)-0x08000000;old_sizes=word(parent,0x21060)-0x08000000
    count=parts['weapon']['resource']+1
    for resource in range(count):
        check(rom[current_sizes+2*resource:current_sizes+2*resource+2]==parent[old_sizes+2*resource:old_sizes+2*resource+2],'Native allocation bound retained '+str(resource))
        if not 256<=resource<276:
            check(word(rom,current_table+4*resource)==word(parent,old_table+4*resource),'Original or held-weapon resource routing retained '+str(resource))
    maps={p['job']:bytes(p['indexMap'][x&15]|p['indexMap'][x>>4]<<4 for x in range(256)) for p in stage['palettes']}
    for resource in stage['resources']:
        ident=resource['resource'];old=resource['sourceDescriptors'];new=resource['descriptors'];frames=0;nonempty=0
        check(word(rom,current_table+4*ident)==new+0x08000000 and word(parent,old_table+4*ident)==old+0x08000000,'Actual old/new descriptor routing '+str(ident))
        for slot in range(resource['slots']):
            left=parent[old+12*slot:old+12*(slot+1)];right=rom[new+12*slot:new+12*(slot+1)]
            p,q=word(left,0),word(right,0)
            check(bool(p)==bool(q) and left[4:]==right[4:],'All slot metadata and null selections retained '+str((ident,slot)))
            if not p:continue
            nonempty+=1;p-=0x08000000;q-=0x08000000;n=word(parent,p)
            check(0<n<100 and word(rom,q)==n,'Bounded original command count '+str((ident,slot)))
            for frame in range(n):
                x=parent[p+4+20*frame:p+24+20*frame];y=rom[q+4+20*frame:q+24+20*frame]
                if x[9]==1:
                    check(x[4:]==y[4:],'Complete draw metadata/OAM/timing retained '+str((ident,slot,frame)))
                    before=parent[TILES+word(x,0):TILES+word(x,0)+512];after=rom[TILES+word(y,0):TILES+word(y,0)+512]
                    check(len(before)==len(after)==512 and before.translate(maps[resource['job']])==after,'Complete native-indexed imagegen pixels '+str((ident,slot,frame)))
                else:check(x==y,'Complete non-draw command retained '+str((ident,slot,frame)))
                frames+=1
        resources.append(dict(resource=ident,job=resource['job'],slots=resource['slots'],nonempty=nonempty,frames=frames))
    for patch in parts['livePalette']['changes']:
        p=patch['offset'];n=patch['bytes']
        if p not in stage['restoredNativeHooks']:continue
        reference=gameplay if p==0x36d4bc else clean
        check(rom[p:p+n]==reference[p:p+n],'Native graphics entry matches its authoritative implementation '+hex(p))
        hooks.append(dict(offset=p,bytes=n,reference='existing gameplay copy handler' if p==0x36d4bc else 'clean US',sha256=sha(rom[p:p+n])))
    check(len(hooks)==29,'All restored graphics/fade/copy entries accounted for')
    expected={116:[9],117:[1,5,6],118:[31],119:[1,5,6],120:[7,12],121:[11,12],122:[7,12],123:[7,16],124:[7,8],125:[3,8]}
    jobs=word(rom,0xc8598)-0x08000000;permissions=word(rom,0xcac40)-0x08000000;items=word(rom,0x79aec)-0x08000000;actual={}
    for job,wanted in expected.items():
        mask=word(rom,permissions+4*rom[jobs+52*job+0x2d])
        actual[job]=sorted({rom[items+32*i+8] for i in range(1,461) if rom[items+32*i+8] in (*range(1,20),31) and mask&(1<<(rom[items+32*i+8]-1))})
        check(actual[job]==wanted,'Actual allowed weapon families match retained Fight coverage '+str(job))
    check(sum(map(len,actual.values()))==20,'All twenty allowed class/weapon families accounted for')
    for name in ('classes','portraits','effect'):
        a,b=parts[name]['used'];check(rom[a:b]==parent[a:b],'Independent '+name+' payload retained')
    a,b=parts['weapon']['used'];owned_pointers=set(range(current_table+256*4,current_table+276*4))
    check(all(rom[p]==parent[p] or p in owned_pointers for p in range(a,b)),'Held-weapon payload/code retained except separately verified class table pointers')
    a,b=parts['equipment']['reservation'];check(rom[a:b]==parent[a:b],'Independent equipment code/payload retained')
    a=parts['status']['offset'];n=parts['status']['bytes'];check(rom[a:a+n]==parent[a:a+n],'Independent status glyphs retained')
    a=parts['preview']['reservation'][0];n=parts['preview']['bytes'];check(rom[a:a+n]==parent[a:a+n],'Equipment eligibility UI code/payload retained')
    report=dict(status='passed',romSha1=meta['romSha1'],parentSha1=stage['baseRomSha1'],checks=checks,resources=resources,restoredHooks=hooks,weaponFamilies=actual,scope=__doc__,manifest=str(manifest),manifestSha256=sha(manifest.read_bytes()))
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),reports=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',checks=checks,error=str(error),resources=resources),indent=2)+'\n',encoding='utf-8');print('Artifacts: '+str(out));raise
