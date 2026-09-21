"""Paired actual Tomahawk impact from its authenticated native confirmation."""
import ctypes as C,datetime,hashlib,json,runpy,struct
from pathlib import Path
from native_art import ROOT,sha
from native_effect_art import reference
from ffta_maps import lz77
out=ROOT/'build/art/generated-effect/battle'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
m=json.loads((ROOT/'build/art/generated-effect/current.json').read_text());rom=Path(m['path']).read_bytes();base=Path(m['source']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==m['romSha1'] and hashlib.sha1(base).hexdigest()==m['baseRomSha1']
source=ROOT/'build/art/generated-projectile/20260917T233435.237211Z';proofpath=source/'report.json';proof=json.loads(proofpath.read_text())
assert proof['status']=='passed' and proof['romSha1']==m['baseRomSha1']
seed=source/'generated-confirmation.state';seedbytes=seed.read_bytes();seedram=(source/'generated-confirmation.ram').read_bytes()
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];menus=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
checks=[];inputs=[];observations={};outcomes={};e=None;case='setup'
word=lambda r,p:struct.unpack_from('<I',r,p)[0]
half=lambda r,p:struct.unpack_from('<H',r,p)[0]
def check(ok,label):
    assert ok,case+'/'+label
    checks.append(case+'/'+label)
def capture(name):
    e.screenshot(out/(case+'-'+name+'.png'))
    for ext,address in (('ram',0x02000000),('vram',0x06000000),('oam',0x07000000),('palette',0x05000000)):
        (out/(case+'-'+name+'.'+ext)).write_bytes(C.string_at(*e.maps[address]))
def active():
    r=e.memory();return word(r,word(r,0xf438)-0x02000000+24)
try:
    original=reference(base);palettes={p['raw'] for p in original['palettes']}
    for case,path,pixels in (('baseline',Path(m['source']),original['pixels']),('generated',Path(m['path']),lz77(rom,m['payload']+4).data)):
        e=E(path);e.load(seed);before=e.memory();check(before==seedram,'Retained native confirmation RAM exact')
        manager=word(before,0xf438)-0x02000000
        check(before[manager+4]==11 and word(before,manager+20)==425,'Actual Tomahawk final confirmation')
        C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',1),4);inputs.append([case,'native RNG',1])
        e.run(8,256);inputs.append([case,8,256]);samples=[];seen=set()
        for frame in range(0,720,4):
            e.run(4);vram=C.string_at(*e.maps[0x06000000]);pal=C.string_at(*e.maps[0x05000000]);oam=C.string_at(*e.maps[0x07000000]);objects=[]
            for index in range(128):
                a,b,c=struct.unpack_from('<3H',oam,index*8);tile=c&1023;x=b&511;y=a&255
                if a&0x300==0x200 or c>>12!=6 or not 996<=tile<1023 or x>=240 or y>=160:continue
                objects.append(dict(index=index,attributes=[a,b,c],tile=tile,x=x,y=y))
            if objects:
                check(vram[0x17c80:0x17fe0]==pixels,'Actual impact atlas exact in VRAM')
                check(pal[704:736].hex() in palettes,'Native cycling impact palette')
                pose=(min(o['tile'] for o in objects)-996)//9;seen.add(pose)
                samples.append(dict(frame=frame+4,pose=pose,objects=objects,paletteSha256=sha(pal[704:736]),frameSha256=sha(e.frame[0])))
                if sum(s['pose']==pose for s in samples)==1:capture('impact-'+str(pose)+'-'+str(frame+4))
        e.run(1080);after=e.memory();capture('executed')
        check(seen=={0,1,2},'All three native impact poses visibly scheduled')
        check(half(after,0x9c)==12 and half(after,0x33fc)==232,'Exact18damage and4MP')
        for lo,hi in ((0xaa,0xb4),(0x1940,0x1ebc)):
            check(after[lo:hi]==before[lo:hi],f'Persistent storage unchanged {lo:x}')
        check(after[0x3ff44:0x3ff4c]==bytes(8) and after[0x3ff4c:]==b'\xd7'*0xb4,'Roots retired/guard intact')
        outcomes[case]=dict(damage=250-half(after,0x33fc),mp=half(after,0x9c),exp=after[0x8a]);observations[case]=samples
        for key in (32,32,256,256):inputs.append([case,8,key,180]);e.run(8,key);e.run(180)
        for waited in range(0,6300,30):
            if active()!=0x02000080 and menus['menu_visible'](e):break
            e.run(30)
        else:raise AssertionError('Following turn missing')
        check(active()!=0x02000080,'Native following turn');capture('returned');e.close();e=None
    check(outcomes['baseline']==outcomes['generated'],'Paired gameplay exact')
    check(seed.read_bytes()==seedbytes,'Source confirmation unchanged')
    report=dict(status='passed',romSha1=m['romSha1'],baseRomSha1=m['baseRomSha1'],checks=checks,inputs=inputs,observations=observations,outcomes=outcomes,
        sourceProof=dict(path=str(proofpath),sha256=sha(proofpath.read_bytes()),seedSha256=sha(seedbytes)),
        scope='Retained native Tomahawk confirmation before effect allocation; paired original/generated primary impact atlas, three actual hardware OAM poses, palette cycling, exact damage/MP/storage and next turn. Temporary generated impact; other effect families/final art separate.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    if e:e.save(out/(case+'-failed.state'));capture('failed')
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=m['romSha1'],error=str(error),checks=checks,inputs=inputs,observations=observations,outcomes=outcomes),indent=2)+'\n');print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
