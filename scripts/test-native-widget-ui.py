"""Actual dispatch member-selector widget creation, updates and teardown.

Uses the declared paid-recovery preparation on an isolated early-town seed,
with generic Ford's displayed job117. No dispatch confirmation or save writes.
"""
import ctypes as C,datetime,hashlib,json,runpy,struct
from pathlib import Path
from native_art import ROOT,sha
from actor_render_evidence import actors
meta=json.loads((ROOT/'build/art/class-resources/current.json').read_text())
seedpath=ROOT/'build/test-lab/early-town.sav';seed=seedpath.read_bytes()
assert hashlib.sha1(seed).hexdigest()=='b0199e7490f7c22f84512825a4a1bde08d3b3eec'
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
out=ROOT/'build/art/class-resources/widget-ui'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];observations={};inputs=[];e=None

def check(ok,label):
    assert ok,label
    checks.append(label)

def word(r,p):return struct.unpack_from('<I',r,p)[0]
def tap(key,wait=180):inputs.append([kind,8,key,wait]);e.run(8,key);e.run(wait)

def capture(name,expected=None):
    ram=e.memory();vram=C.string_at(*e.maps[0x06000000]);iw=C.string_at(*e.maps[0x03000000])
    palette=C.string_at(*e.maps[0x05000000]);oam=C.string_at(*e.maps[0x07000000])
    stem=kind+'-'+name;e.screenshot(out/(stem+'.png'))
    for suffix,data in [('ram',ram),('iwram',iw),('vram',vram),('palette',palette),('oam',oam)]:
        (out/(stem+'.'+suffix)).write_bytes(data)
    obs=dict(frame=sha(e.frame[0]),vram=sha(vram),palette=sha(palette),oam=sha(oam),owned=sha(ram[0x80:0x1e70]))
    figures=actors(rom,ram,vram);widgets=[]
    for f in figures:
        pointer=0x02000000+f['address']
        for i in range(0x7c,len(ram)-0x1010,4):
            if word(ram,i)==pointer and word(ram,i-8)==0x02000000+i+8:
                widgets.append(dict(address=i-0x7c,actor=f))
    obs['widgets']=widgets;observations[kind][name]=obs
    if expected is not None:
        check(len(widgets)==1,f'{kind}/{name} actual generic widget owner')
        w=widgets[0];f=w['actor'];p=w['address']
        check(f['resource']==expected,f'{kind}/{name} actual complete resource ID')
        check(f['declaredSequence'] and bool(f['displayedFrames']),f'{kind}/{name} descriptor and actual uploaded frame')
        units=struct.unpack_from('<H',ram,p+0x8a)[0]
        check(units==(1018 if kind=='private' else 1022),f'{kind}/{name} actual owner allocator boundary')
        if kind=='private':check(struct.unpack_from('<H',ram,p+0x1080)[0]==expected,f'{name} full ID survives actual UI lifetime')
    return ram

def enter_selection(label):
    for key,wait in ((256,240),(256,180),(256,120),(256,120)):tap(key,wait)
    r=e.memory();ctx=word(r,0xf448)-0x02000000
    check(0<=ctx<0x3e000,label+' native pub context')
    count=r[ctx+0x11a9]
    pointers=[word(r,ctx+0x11ac+i*4)-0x02000000 for i in range(count)]
    check(0<count<=16 and all(0x21c8<=p<0x25c8 for p in pointers),label+' native offer list')
    ids=[r[p]|((r[p+1]&3)<<8) for p in pointers]
    check(471 in ids,label+' declared recovery offer')
    for _ in range(ids.index(471)):tap(32)
    tap(256);capture(label+'-details')
    for key in (256,256,128,128):tap(key)
    return ctx

try:
    for kind,path,digest in [('original',meta['source'],meta['baseRomSha1']),('private',meta['path'],meta['romSha1'])]:
        rom=Path(path).read_bytes();check(hashlib.sha1(rom).hexdigest()==digest,kind+' authenticated ROM')
        observations[kind]={};e=E(Path(path));e.set_memory(0,seed,0);e.run(3600)
        for key,wait in ((8,180),(256,60),(256,60),(256,180)):tap(key,wait)
        r=e.memory()
        for bit in (54,22+0x2ff):
            at=0x1f70+(bit>>3);e.set_memory(at,bytes([r[at]|1<<(bit&7)]))
        e.set_memory(0x1f64,struct.pack('<I',50000));e.set_memory(0x1940+26,b'\0')
        e.set_memory(0x2b08,bytes(256));e.set_memory(0x299,b'\x32')
        e.set_memory(0x295,b'\x75');e.set_memory(0x297,b'\x75')
        inputs.append([kind,'declared-profile','paid-recovery prepare; Ford generic Human job117 level50'])
        expected=258 if kind=='private' else 1
        for cycle in range(2):
            label='cycle'+str(cycle);ctx=enter_selection(label)
            capture(label+'-ford',expected)
            for i in range(3):e.run(8);capture(label+'-idle'+str(i),expected)
            tap(128);capture(label+'-other')
            tap(64);capture(label+'-ford-return',expected)
            for _ in range(4):tap(1)
            # Pub exit is still in its black transition at180 frames. Let the
            # existing scene finish before sending the next entry input.
            inputs.append([kind,'settle-pub-exit',600]);e.run(600)
            capture(label+'-closed')
            check(not observations[kind][label+'-closed']['widgets'],label+' widget no longer active after cancellation')
            check(struct.unpack_from('<H',e.memory(),0x2a6)[0]==0,label+' no member dispatched')
            check(word(e.memory(),0x1f64)==50000,label+' no fee charged')
        e.close();e=None
    for name,before in observations['original'].items():
        after=observations['private'][name]
        for field in ('frame','vram','palette','oam','owned'):
            check(before[field]==after[field],name+' exact '+field)
    check(seedpath.read_bytes()==seed,'source save unchanged')
    report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,inputs=inputs,observations=observations,
        scope='Actual native dispatch selector: generic Human117 widget create/idle/change/cancel/reopen, display and owned-state equivalence. No dispatch execution, all-job UI coverage or final artwork.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),checks=checks,inputs=inputs,observations=observations),indent=2)+'\n')
    print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
