"""All five racial wheels and generic roster figures after wide-ID relocation.

Read-only reuse of the existing authenticated showcase seed. No new fixture,
player save or synthetic menu data. Original and candidate use identical input.
"""
import ctypes as C,datetime,hashlib,json,runpy,struct
from pathlib import Path
from native_art import ROOT,sha
from actor_render_evidence import actors
meta=json.loads((ROOT/'build/art/class-resources/current.json').read_text())
seedpath=ROOT/'build/showcase/20260917T160011.215713Z/showcase.sav';seed=seedpath.read_bytes()
assert hashlib.sha1(seed).hexdigest()=='7831543efb239ef145764889214f8d83cd56eb14'
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
out=ROOT/'build/art/class-resources/menus'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];observations={};inputs=[];e=None
cases=[(2,1,117),(3,2,118),(4,3,121),(1,5,123),(5,4,125)]

def check(ok,label):
    assert ok,label
    checks.append(label)

def tap(key,wait=120):inputs.append([kind,slot,8,key,wait]);e.run(8,key);e.run(wait)

def capture(name):
    ram=e.memory();iw=C.string_at(*e.maps[0x03000000]);vram=C.string_at(*e.maps[0x06000000])
    palette=C.string_at(*e.maps[0x05000000]);oam=C.string_at(*e.maps[0x07000000])
    stem=f'{kind}-slot{slot}-{name}';e.screenshot(out/(stem+'.png'))
    for suffix,data in [('ram',ram),('iwram',iw),('vram',vram),('palette',palette),('oam',oam)]:
        (out/(stem+'.'+suffix)).write_bytes(data)
    observations[kind][str(slot)][name]=dict(frame=sha(e.frame[0]),vram=sha(vram),palette=sha(palette),oam=sha(oam),owned=sha(ram[0x80:0x1e70]))
    if name=='wheel' or name.startswith('idle-'):
        figures=actors(current_rom,ram,vram)
        check(len(figures)==1,f'{kind}/{slot}/{name} one actual animated header figure')
        record=next(j for j in meta['jobs'] if j['job']==job)
        if slot!=1:
            expected=record['original'][0] if kind=='original' else record['resources'][0]
            check(figures[0]['resource']==expected,f'{kind}/{slot}/{name} actual complete resource ID')
        check(figures[0]['declaredSequence'] and bool(figures[0]['displayedFrames']),f'{kind}/{slot}/{name} native descriptor and displayed frame')
        observations[kind][str(slot)][name]['actorResource']=figures[0]['resource']
        pointer=0x02000000+figures[0]['address']
        task=struct.unpack_from('<I',iw,0x2818)[0]-0x02000000
        check(struct.unpack_from('<I',ram,task+0x448)[0]==pointer,f'{kind}/{slot}/{name} actual header owns actor')
        manager=struct.unpack_from('<I',ram,task+0x444)[0]-0x02000000
        if kind=='private':
            check(struct.unpack_from('<H',ram,manager+16)[0]==figures[0]['resource'],f'{kind}/{slot}/{name} allocated manager retains full ID')
        check(ram[task+0x434]==figures[0]['resource']&255,f'{kind}/{slot}/{name} legacy resource mirror')
        observations[kind][str(slot)][name]['adjacentFields']=sha(ram[task+0x435:task+0x440])
    return ram,iw

try:
    for kind,path,digest in [('original',meta['source'],meta['baseRomSha1']),('private',meta['path'],meta['romSha1'])]:
        current_rom=Path(path).read_bytes()
        check(hashlib.sha1(current_rom).hexdigest()==digest,kind+' authenticated ROM')
        observations[kind]={}
        for slot,race,job in cases:
            observations[kind][str(slot)]={};e=E(Path(path));e.set_memory(0,seed,0);e.run(3600)
            for key in (8,256,256,256):tap(key,300)
            for key in (8,256):tap(key)
            # Reuse the established four-column roster traversal.
            if slot>=4:tap(32)
            for _ in range(slot%4):tap(128)
            ram,_=capture('roster')
            check(ram[0x80+slot*264+6]==race and ram[0x80+slot*264+7]==job,f'{kind}/{slot} authenticated existing racial member/job')
            tap(256)
            p=struct.unpack_from('<I',C.string_at(*e.maps[0x03000000]),0x2818)[0]-0x02000000
            check(struct.unpack_from('<I',e.memory(),p+0x1d0c)[0]==0x02000080+264*slot,f'{kind}/{slot} native selected roster pointer')
            tap(32);tap(32);tap(256,600)
            ram,iw=capture('wheel')
            p=struct.unpack_from('<I',iw,0x2818)[0]-0x02000000
            check(0<=p<len(ram)-0x1400,f'{kind}/{slot} native menu task')
            check(ram[p+0x1287+28*ram[p+0x1275]]==job,f'{kind}/{slot} selected expected job')
            for f in range(3):e.run(8);capture('idle-'+str(f))
            tap(1,180);capture('cancelled');e.close();e=None
    for slot,race,job in cases:
        for name,before in observations['original'][str(slot)].items():
            after=observations['private'][str(slot)][name]
            for field in ('frame','vram','palette','oam','owned'):
                check(before[field]==after[field],f'{slot}/{name} exact {field}')
            if 'adjacentFields' in before:
                check(before['adjacentFields']==after['adjacentFields'],f'{slot}/{name} adjacent native byte fields unchanged')
    check(seedpath.read_bytes()==seed,'source save remains unchanged')
    report=dict(status='passed',romSha1=meta['romSha1'],baseRomSha1=meta['baseRomSha1'],checks=checks,inputs=inputs,observations=observations,
        cases=cases,seedSha256=sha(seed),scope='Five racial wheels: four generic land figures and Montblanc fixed appearance. Exact full display/OAM/palette/VRAM and owned-state comparison. This is not display acceptance for all20 resources, generic Moogle, job-change confirmation, battle action/water or final artwork.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),checks=checks,inputs=inputs,observations=observations),indent=2)+'\n')
    print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
