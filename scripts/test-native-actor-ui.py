"""Compare separate roster/wheel miniatures after actor resource relocation.

These compressed miniatures do not consume native actor sequences or OAM.
"""
import ctypes as C,datetime,hashlib,json,runpy,struct
from pathlib import Path
from native_art import ROOT,sha
meta=json.loads((ROOT/'build/art/actor-import/current.json').read_text())
out=ROOT/'build/art/actor-import/ui'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True,exist_ok=False)
seedpath=ROOT/'build/showcase/20260917T160011.215713Z/showcase.sav';seed=seedpath.read_bytes()
assert hashlib.sha1(seed).hexdigest()=='7831543efb239ef145764889214f8d83cd56eb14'
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
observations={};inputs=[];checks=[];e=None
def check(ok,name):
    assert ok,name
    checks.append(name)
def tap(key,wait=120):
    inputs.append([8,key,wait]);e.run(8,key);e.run(wait)
def capture(name):
    e.screenshot(out/f'{kind}-{name}.png')
    ram=e.memory();vram=C.string_at(*e.maps[0x06000000]);iw=C.string_at(*e.maps[0x03000000])
    pointers=[dict(offset=hex(i*4),pointer=hex(v[0])) for i,v in enumerate(struct.iter_unpack('<I',ram))
              if 0x08000000+meta['used'][0]<=v[0]<0x08000000+meta['used'][1]]
    observations[kind][name]=dict(frame=sha(e.frame[0]),vram=sha(vram),owned=sha(ram[0x80:0x1e70]),newPointers=pointers[:30])
    (out/f'{kind}-{name}.ram').write_bytes(ram);(out/f'{kind}-{name}.vram').write_bytes(vram)
    return ram,iw
try:
    for kind,path,digest in [('baseline',Path(meta['source']),meta['baseRomSha1']),('relocated',Path(meta['path']),meta['romSha1'])]:
        check(hashlib.sha1(path.read_bytes()).hexdigest()==digest,kind+' authenticated ROM')
        observations[kind]={};e=E(path);e.set_memory(0,seed,0);e.run(3600)
        for key in (8,256,256,256):tap(key,300)
        for key in (8,256):tap(key)
        capture('roster')
        tap(256);tap(32);tap(32);tap(256,600)
        ram,iw=capture('wheel')
        p=struct.unpack_from('<I',iw,0x2818)[0]-0x02000000
        check(ram[p+0x1287+28*ram[p+0x1275]]==116,kind+' selected Samurai')
        for f in range(8):
            e.run(8);capture('idle-'+str(f))
        tap(1,180);capture('cancelled')
        e.close();e=None
    for name,old in observations['baseline'].items():
        new=observations['relocated'][name]
        for field in ('frame','vram','owned'):check(new[field]==old[field],name+' unchanged '+field)
    check(seedpath.read_bytes()==seed,'Read-only seed unchanged')
    report=dict(status='passed',romSha1=meta['romSha1'],baseRomSha1=meta['baseRomSha1'],checks=checks,inputs=inputs,observations=observations,
                coverage='Cold-loaded roster and selected Samurai wheel, 64 idle frames and cancellation, exact framebuffer/VRAM/owned-state comparison. These separate compressed miniatures do not prove native actor sequence playback. No water/battle/generated-art acceptance.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),romSha1=meta['romSha1'],checks=checks,inputs=inputs,observations=observations),indent=2)+'\n')
    print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
