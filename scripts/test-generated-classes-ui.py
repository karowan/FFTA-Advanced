"""Ten generic racial headers and selected wheel miniatures with draft pixels.

Declared isolated presentation profile: set one existing same-race member's
appearance/job before menu entry. Montblanc is made generic for Moogle cases.
No persistent save, player game, job acquisition or gameplay acceptance.
"""
import ctypes as C,datetime,hashlib,json,runpy,struct
from pathlib import Path
from native_art import ROOT,sha
from native_miniatures import CONTAINER,decode
from actor_render_evidence import actors
meta=json.loads((ROOT/'build/art/generated-classes/current.json').read_text())
seedpath=ROOT/'build/showcase/20260917T160011.215713Z/showcase.sav';seed=seedpath.read_bytes()
assert hashlib.sha1(seed).hexdigest()=='7831543efb239ef145764889214f8d83cd56eb14'
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
out=ROOT/'build/art/generated-classes/ui'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
inputs=[];checks=[];observations={};e=None

def check(ok,label):
    assert ok,label
    checks.append(label)
def tap(key,wait=120):inputs.append([kind,job['job'],8,key,wait]);e.run(8,key);e.run(wait)

def capture(name):
    ram=e.memory();vram=C.string_at(*e.maps[0x06000000]);pal=C.string_at(*e.maps[0x05000000]);oam=C.string_at(*e.maps[0x07000000])
    stem=f'{kind}-{job["job"]}-{name}';e.screenshot(out/(stem+'.png'))
    for suffix,data in [('ram',ram),('vram',vram),('palette',pal),('oam',oam)]: (out/(stem+'.'+suffix)).write_bytes(data)
    obs=dict(frame=sha(e.frame[0]),owned=sha(ram[0x80:0x1e70]),vram=sha(vram),palette=sha(pal),oam=sha(oam))
    observations[kind][str(job['job'])][name]=obs
    if name.startswith('wheel'):
        figures=actors(rom,ram,vram);check(len(figures)==1,stem+' one real generic header')
        f=figures[0];obs['actor']=f
        check(f['resource']==job['resource'],stem+' actual class resource')
        check(f['declaredSequence'] and bool(f['displayedFrames']),stem+' actual native sequence and displayed frame')
        if kind=='generated':
            check(f['first']==0x08000004+job['sequences'][0]['target'],stem+' uses generated idle descriptor')
            mini=decode(rom,meta['container'],job['miniature']['index'])
            locations=[i for i in range(0x10000,len(vram)-639,32) if vram[i:i+640]==mini]
            check(len(locations)==1,stem+' selected generated miniature uploaded once')
            first=(locations[0]-0x10000)//32
            for tile in (first,first+16):
                owners=[struct.unpack_from('<3H',oam,i*8) for i in range(128)]
                owners=[v for v in owners if v[2]&1023==tile and v[0]&0x300!=0x200]
                check(bool(owners),stem+' miniature has native OAM owner')
                for a,b,c in owners:
                    p=job['miniature']['paletteReference'];bank=c>>12
                    check(pal[0x200+bank*32+2:0x200+(bank+1)*32]==rom[p+2:p+32],stem+' actual miniature palette matches conversion')
    return ram

try:
    for kind,path,digest in [('baseline',meta['source'],meta['baseRomSha1']),('generated',meta['path'],meta['romSha1'])]:
        rom=Path(path).read_bytes();check(hashlib.sha1(rom).hexdigest()==digest,kind+' authenticated ROM');observations[kind]={}
        for job in meta['jobs']:
            record=next(j for j in meta['classResources']['jobs'] if j['job']==job['job']);race=record['race'];slot={1:2,2:3,3:4,5:1,4:5}[race]
            observations[kind][str(job['job'])]={};e=E(Path(path));e.set_memory(0,seed,0);e.run(3600)
            for key in (8,256,256,256):tap(key,300)
            check(e.memory()[0x80+slot*264+6]==race,'existing member has declared race')
            profile=bytes([1,job['job'],race,job['job']]);e.set_memory(0x80+slot*264+4,profile)
            inputs.append([kind,job['job'],'presentation profile',slot,list(profile)])
            for key in (8,256):tap(key)
            if slot>=4:tap(32)
            for _ in range(slot%4):tap(128)
            tap(256);tap(32);tap(32);tap(256,600)
            ram=capture('wheel0');iw=C.string_at(*e.maps[0x03000000]);task=struct.unpack_from('<I',iw,0x2818)[0]-0x02000000
            check(ram[task+0x1287+28*ram[task+0x1275]]==job['job'],'actual wheel selected requested class')
            for i in range(1,4):e.run(16);capture('wheel'+str(i))
            tap(1,180);capture('cancelled');e.close();e=None
    from generated_class_ui_evidence import verify
    verify(meta,out,observations,check)
    check(seedpath.read_bytes()==seed,'source save unchanged')
    report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,inputs=inputs,observations=observations,
        scope='Ten generic racial job-wheel animated idle headers and separate static miniatures, native OAM/palette/upload, three idle advances and cancellation. Declared isolated appearance/job profile; no acquisition, battle actions/water, production-art or release acceptance.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),checks=checks,inputs=inputs,observations=observations),indent=2)+'\n');print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
