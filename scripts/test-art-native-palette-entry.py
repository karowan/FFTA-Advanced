"""Fresh paired original-renderer entry for native shared-palette acceptance.

Same accepted world, declared four-class profiles, existing input route and
Status shortcut in the original-renderer control. Each ROM allocates its own
actors. The established Giza coordinate input is applied only after comparing
the complete entry route. No player saves or installed selectors are changed.
"""
import argparse,ctypes as C,datetime,hashlib,json,runpy,struct
from pathlib import Path
from PIL import Image
from native_art import ROOT,sha
from native_battle_wrappers import from_emulator,fixed_giza_formation
from actor_render_evidence import actors

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--bangaa-job',type=int,choices=(118,119),default=118,
                    help='Same-race profile selected before native battle allocation.')
args=parser.parse_args()
manifest=ROOT/'build/art/native-palettes/current.json';meta=json.loads(manifest.read_text())
native=meta['components']['nativePaletteTransport'];live=meta['components']['livePalette']
candidate=Path(meta['path']).read_bytes();original=Path(live['source']).read_bytes()
assert hashlib.sha1(candidate).hexdigest()==meta['romSha1']
assert hashlib.sha1(original).hexdigest()==live['baseRomSha1']=='0fa7d1707e2d85fb2a8602f061b5eb4479ff3211'
out=ROOT/'build/art/native-palette-entry'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
start=live['symbols']['ffta_art_status_next_entry']-0x08000000;leaf=candidate[start:start+32]
assert leaf.hex()=='a37801331b061b16182b03dca37008bc01480047014b184763dd09081d631e09'
assert original[start:start+32]==b'\xff'*32 and original[0x9dd58:0x9dd5c]==struct.pack('<I',0x091e631d)
control=bytearray(original);control[start:start+32]=leaf;control[0x9dd58:0x9dd5c]=struct.pack('<I',start+0x08000001)
assert all(a==b or start<=i<start+32 or 0x9dd58<=i<0x9dd5c for i,(a,b) in enumerate(zip(original,control)))
control_path=out/'native-control.gba';control_path.write_bytes(control)
world=Path(meta['fixtureSource']).parent/'fixture';seed=world/'accepted-world.state';seedbytes=seed.read_bytes()
route=json.loads((world/'route.json').read_text());proof=json.loads((world/'report.json').read_text())
assert proof['passed'] and proof['romSha1']==route['romSha1']==hashlib.sha1(Path(meta['fixtureSource']).read_bytes()).hexdigest()
reference=ROOT/'build/art/live-palette/battle/20260918T043030.693824Z/parent-entry-2.png'
assert sha(reference.read_bytes())=='3d6447c179ea198dad3a02361ab02be34124d81fae1988b86668b76de7186dc7'
target=Image.open(reference).resize((240,160),Image.Resampling.NEAREST).crop((72,12,191,54)).tobytes()
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
menus=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
word=lambda b,p:struct.unpack_from('<I',b,p)[0]
profiles={2:(117,1),3:(args.bangaa_job,2),4:(120,3),5:(124,4)}
checks=[];records={};inputs=[];failures=[];e=None;case='setup';clock=0;entries=[]

def check(ok,label):
    assert ok,case+'/'+label
    checks.append(case+'/'+label)

def sample():
    r=e.memory();iw=C.string_at(*e.maps[0x03000000])
    return dict(frame=clock,units=sha(r[0x80:0x1e70]),shadow=iw[0x3860:0x3c60].hex(),
                palette=C.string_at(*e.maps[0x05000000]).hex(),nativeFrame=struct.unpack_from('<H',iw,0xeb4)[0])

def capture(label):
    e.save(out/(case+'-'+label+'.state'))
    if e.frame:e.screenshot(out/(case+'-'+label+'.png'))
    for ext,address in [('ram',0x02000000),('iwram',0x03000000),('vram',0x06000000),('palette',0x05000000),('oam',0x07000000)]:
        (out/(case+'-'+label+'.'+ext)).write_bytes(C.string_at(*e.maps[address]))

def step(n,key=0):
    global clock
    e.run(n,key);clock+=n

def text_ready():
    raw,w,h,pitch,pixel=e.frame
    assert (w,h)==(240,160) and pixel in (0,1,2)
    if pixel==1:return Image.frombytes('RGB',(w,h),raw,'raw','BGRX',pitch).crop((72,12,191,54)).tobytes()==target
    rgb=bytearray()
    for y in range(12,54):
        for x in range(72,191):
            v=int.from_bytes(raw[y*pitch+x*2:y*pitch+x*2+2],'little')
            if pixel==2:r,g,b=(v>>11)&31,(v>>5)&63,v&31;g=g*255//63
            else:r,g,b=(v>>10)&31,(v>>5)&31,v&31;g=g*255//31
            rgb.extend((r*255//31,g,b*255//31))
    return bytes(rgb)==target

def tap(key,wait=180,entry=False):
    inputs.append([case,8,key,wait]);step(8,key);step(wait)
    if not entry:return
    if len(entries)==2:
        waited=0
        while not text_ready() and waited<180:step(1);waited+=1
        check(text_ready(),'Original first-dialogue text revealed within180 extra frames')
        inputs.append([case,'observe original dialogue',waited])
    label='entry-'+str(len(entries));entries.append(dict(label=label,**sample()))
    if label=='entry-6':capture(label)

def active():
    r=e.memory();return word(r,word(r,0xf438)-0x02000000+24)

try:
    for patch in live['changes']:
        if patch['offset'] in native['restoredNativeHooks']:
            p=patch['offset'];n=patch['bytes']
            check(candidate[p:p+n]==original[p:p+n]==bytes.fromhex(patch['before']),'Original renderer entry '+hex(p))
    for case,path in [('control',control_path),('candidate',Path(meta['path']))]:
        rom=path.read_bytes();e=E(path);e.load(seed);clock=0;entries=[]
        story=e.memory()[0x80:0x290]
        for slot,(job,race) in profiles.items():
            unit=0x80+264*slot;check(e.memory()[unit+6]==race,'Existing same-race profile '+str(slot))
            e.set_memory(unit+4,bytes((1,job,race,job)));e.set_memory(unit+0x35,bytes((job,)))
        check(e.memory()[0x80:0x290]==story,'Fixed story profiles preserved')
        items=word(rom,0x79aec)-0x08000000
        sword=next(i for i in range(1,461) if rom[items+32*i+8]==2)
        e.set_memory(0x2ba,struct.pack('<5H',sword,0,0,0,0));e.set_memory(0x3ff44,bytes(8))
        inputs.append([case,'preallocation profiles',profiles,'focus sword',sword])
        for x,y,key in route['path']:step(1,key)
        step(30);tap(256,1200,True)
        for _ in range(7):tap(256,600,True)
        for _ in range(3):tap(256,entry=True)
        for _ in range(3):
            for key in (128,256,256,256):tap(key,entry=True)
        tap(8,600,True);tap(256,600,True);tap(256,600,True)
        waited=menus['wait_for_menu'](e);clock+=waited
        inputs.append([case,'bounded initial menu wait',waited])
        for turn in range(12):
            if active()==0x02000290:break
            previous=active();inputs.append([case,'Wait preceding actor',previous])
            for key in (32,32,256,256):tap(key)
            for waited in range(0,6300,30):
                if active()!=previous and menus['menu_visible'](e):break
                step(30)
            else:raise AssertionError('Native turn did not advance')
        check(active()==0x02000290,'Actual recruited focus turn reached')
        preplacement=sample();capture('preplacement')
        fixed_giza_formation(rom,e);step(30);wrappers=from_emulator(rom,e)
        check(len(wrappers)==12,'Complete original twelve-actor Giza roster')
        r=e.memory();vram=C.string_at(*e.maps[0x06000000]);bodies={u:word(r,p+0x44)-0x02000000 for u,p in wrappers.items()}
        figures={a['address']:a for a in actors(rom,r,vram,set(bodies.values()))}
        for slot,(job,race) in profiles.items():
            a=figures[bodies[0x80+264*slot]]
            check(a['resource']==256+2*(job-116) and a['declaredSequence'],'Fresh correct class resource '+str(job))
            check(a['expectedTiles']==a['tileCount']<=a['allocation'] and bool(a['displayedFrames']),'Exact bounded native idle upload '+str(job))
        check(struct.unpack_from('<3H',r,wrappers[0x290]+8)==(48,32,432),'Declared Giza focus start1,13')
        capture('ready');ready=sample()
        idle=[]
        for tick in range(20):step(1);idle.append(sample())
        records[case]=dict(path=str(path),romSha1=hashlib.sha1(rom).hexdigest(),entries=entries,
            preplacement=preplacement,ready=ready,idle=idle,wrappers=wrappers)
        e.close();e=None
    for label in ('entries','idle'):
        a,b=records['candidate'][label],records['control'][label]
        check(len(a)==len(b),'Same complete '+label+' sample count')
        for i,(x,y) in enumerate(zip(a,b)):
            for field in ('frame','units','shadow','palette','nativeFrame'):
                if x[field]!=y[field]:failures.append(dict(sample=label,index=i,field=field))
    for label in ('preplacement','ready'):
        for field in ('frame','units','shadow','palette','nativeFrame'):
            if records['candidate'][label][field]!=records['control'][label][field]:failures.append(dict(sample=label,field=field))
    check(seed.read_bytes()==seedbytes,'World source preserved')
    result=dict(status='failed' if failures else 'passed',romSha1=meta['romSha1'],manifest=str(manifest),manifestSha256=sha(manifest.read_bytes()),
        control=dict(path=str(control_path),romSha1=hashlib.sha1(control).hexdigest(),sourceSha1=live['baseRomSha1'],statusLeafOffset=start,statusLeafSha256=sha(leaf)),
        checks=checks,failures=failures,records=records,inputs=inputs,profiles=profiles,source=dict(path=str(seed),sha256=sha(seedbytes)),scope=__doc__)
    dest=out/('failed.json' if failures else 'report.json');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    selector='latest.json' if args.bangaa_job==118 else 'bangaa-119.json'
    (ROOT/'build/art/native-palette-entry'/selector).write_text(json.dumps(dict(report=str(dest),sha256=sha(dest.read_bytes())),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],checks=len(checks),failures=failures,report=str(dest))))
    if failures:raise SystemExit(1)
except Exception as error:
    if e:capture('failed')
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,inputs=inputs,records=records,entries=entries),indent=2)+'\n',encoding='utf-8')
    print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
