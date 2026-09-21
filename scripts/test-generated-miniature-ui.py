"""Prove the generated menu figure in a real cold-loaded job wheel.

Reuses exact passing untouched roster/wheel captures. No player-save writes,
interactive inputs, draw mocks or new fixture. A temporary art transport test.
"""
import ctypes as C,datetime,hashlib,json,runpy,struct
from pathlib import Path
from native_art import ROOT,sha
from native_miniatures import CONTAINER,decode
from art_candidate import candidate
meta=candidate('build/art/generated-miniature-poc/current.json','miniature')
data=Path(meta['path']).read_bytes()
assert hashlib.sha1(data).hexdigest()==meta['romSha1']
baseline=ROOT/'build/art/actor-import/ui/20260917T181440.373797Z'
prior=json.loads((baseline/'report.json').read_text())
assert prior['status']=='passed' and prior['romSha1']==meta['comparisonRomSha1']
seedpath=ROOT/'build/showcase/20260917T160011.215713Z/showcase.sav';seed=seedpath.read_bytes()
assert hashlib.sha1(seed).hexdigest()=='7831543efb239ef145764889214f8d83cd56eb14'
generated=bytes.fromhex(meta['imageBytes']);old=decode(data,CONTAINER,4)
assert decode(data,meta['container'],meta['imageIndex'])==generated
out=ROOT/'build/art/generated-miniature-poc/ui'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True,exist_ok=False)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
observations={};checks=[];inputs=[];e=None

def check(ok,name):
    assert ok,name
    checks.append(name)

def tap(key,wait=120):
    inputs.append([8,key,wait]);e.run(8,key);e.run(wait)

def capture(name,changed):
    ram=e.memory();iw=C.string_at(*e.maps[0x03000000]);vram=C.string_at(*e.maps[0x06000000])
    oam=C.string_at(*e.maps[0x07000000]);pal=C.string_at(*e.maps[0x05000000])
    for suffix,raw in [('ram',ram),('iwram',iw),('vram',vram),('oam',oam),('palette',pal)]:
        (out/f'{name}.{suffix}').write_bytes(raw)
    e.screenshot(out/f'{name}.png')
    previous=prior['observations']['relocated'][name]
    original=(baseline/f'relocated-{name}.vram').read_bytes()
    check(sha(original)==previous['vram'],name+' baseline capture authenticated')
    check(sha(ram[0x80:0x1e70])==previous['owned'],name+' roster inventory AP unchanged')
    expected=bytearray(original);locations=[];objects=[]
    if changed:
        locations=[i for i in range(0x10000,len(original)-639,32) if original[i:i+640]==old]
        check(len(locations)==1,name+' one baseline menu figure allocation')
        for i in locations:
            expected[i:i+640]=generated
            # Native32x40 image is displayed with a32x32 and32x8 object.
            # Verify the two tile ranges have enabled native OAM owners.
            first=(i-0x10000)//32
            for tile in (first,first+16):
                matches=[]
                for n in range(128):
                    a,b,c,_=struct.unpack_from('<4H',oam,n*8)
                    if c&1023==tile and a&0x300!=0x200:
                        matches.append(dict(index=n,tile=tile,bank=c>>12,attributes=[a,b,c]))
                check(bool(matches),name+f' displayed owner for tile{tile}')
                for obj in matches:
                    bank=obj['bank'];p=meta['nativePaletteReference']
                    check(pal[0x200+bank*32+2:0x200+(bank+1)*32]==data[p+2:p+32],name+' displayed palette matches imported pixels')
                objects.extend(matches)
        check(sha(e.frame[0])!=previous['frame'],name+' visible framebuffer changes')
    else:
        check(sha(e.frame[0])==previous['frame'],name+' unselected screen exact framebuffer')
    check(vram==bytes(expected),name+' exact full VRAM outside expected figure bytes')
    observations[name]=dict(frame=sha(e.frame[0]),vram=sha(vram),locations=locations,objects=objects)
    return ram,iw

try:
    e=E(Path(meta['path']));e.set_memory(0,seed,0);e.run(3600)
    for key in (8,256,256,256):tap(key,300)
    for key in (8,256):tap(key)
    capture('roster',False)
    tap(256);tap(32);tap(32);tap(256,600)
    ram,iw=capture('wheel',True)
    p=struct.unpack_from('<I',iw,0x2818)[0]-0x02000000
    check(ram[p+0x1287+28*ram[p+0x1275]]==116,'actual selected Samurai')
    for f in range(8):e.run(8);capture('idle-'+str(f),True)
    tap(1,180);capture('cancelled',False)
    check(seedpath.read_bytes()==seed,'read-only seed unchanged')
    report=dict(status='passed',romSha1=meta['romSha1'],baseRomSha1=meta['comparisonRomSha1'],
        checks=checks,observations=observations,inputs=inputs,seedSha256=sha(seed),
        baselineReportSha256=sha((baseline/'report.json').read_bytes()),
        coverage='Cold-loaded Samurai wheel, generated native640-byte figure, actual OAM ownership/palette, eight idle snapshots, exact surrounding VRAM, unchanged roster/cancel and owned data. Other jobs, changed-class roster, actions/water and production art remain separate.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),romSha1=meta['romSha1'],checks=checks,observations=observations,inputs=inputs),indent=2)+'\n')
    print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
