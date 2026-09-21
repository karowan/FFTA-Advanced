"""Fixed-input discovery/acceptance for the actual equipment preview controls."""
import ctypes as C,datetime,hashlib,json,runpy,struct,sys
from pathlib import Path
from native_art import ROOT
from art_candidate import candidate
meta=candidate('build/art/equipment-preview/current.json','preview')
rom=Path(meta['path']);assert hashlib.sha1(rom.read_bytes()).hexdigest()==meta['romSha1']
out=ROOT/'build/art/equipment-preview/ui'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True,exist_ok=False)
sell='--sell' in sys.argv;shop='--shop' in sys.argv or sell
seedpath=ROOT/('build/test-lab/early-town.sav' if shop and not sell else 'build/showcase/20260917T160011.215713Z/showcase.sav')
seed=seedpath.read_bytes();assert hashlib.sha1(seed).hexdigest()==('b0199e7490f7c22f84512825a4a1bde08d3b3eec' if shop and not sell else '7831543efb239ef145764889214f8d83cd56eb14')
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
e=E(rom);inputs=[];checks=[];observations=[]
def tap(key,wait=120):inputs.append([8,key,wait]);e.run(8,key);e.run(wait)
def enter_shop():
    for key,wait in ((256,240),(32,120),(256,180)):tap(key,wait)
    if sell:tap(32,120)
    tap(256,120)
def check(ok,name):
    assert ok,name
    checks.append(name)
def observe(name):
    e.screenshot(out/(name+'.png'))
    vram=C.string_at(*e.maps[0x06000000])
    for ext,addr in [('palette',0x05000000),('iwram',0x03000000)]:
        (out/(name+'.'+ext)).write_bytes(C.string_at(*e.maps[addr]))
    marker=struct.unpack_from('<H',vram,0x5cfe if shop else 0x54fe)[0]
    observations.append(dict(name=name,marker=marker))
    return marker
try:
    e.set_memory(0,seed,0);e.run(3600)
    for key in (8,256,256,256):tap(key,300)
    before=e.memory()[0x80:0x1e70];money=e.memory()[0x1f64:0x1f68]
    if not shop:
        # The roster's on-screen shortcut is START: Item List. A on an item
        # opens the eligibility grid directly, without a context menu.
        for key in (8,256,8):tap(key,300)
        observe('items-menu');tap(256,180)
        check(observe('party-open')==0xa700,'Item List A opens original-jobs page')
    else:
        # Native help: description, category, then SELECT at the category prompt.
        enter_shop()
        observe('shop-list')
        for key in (4,256,256,4):tap(key,180)
        check(observe('shop-open')==0xa700,'Native shop help opens original-jobs page')
    original_vram=C.string_at(*e.maps[0x06000000])
    prefix='sell' if sell else 'shop' if shop else 'party'
    tap(2048,180);check(observe(prefix+'-new-jobs')==0xa701,'R opens all ten new jobs')
    vram=C.string_at(*e.maps[0x06000000]);(out/(prefix+'-new-jobs.vram')).write_bytes(vram)
    if '--manifest' in sys.argv:
        selected=json.loads((ROOT/sys.argv[sys.argv.index('--manifest')+1]).read_text())
        if 'reviewedMenuBadges' in selected['components']:
            proof=selected['components']['reviewedMenuBadges'];data=rom.read_bytes()
            check(hashlib.sha256(data[proof['offset']:proof['offset']+proof['bytes']]).hexdigest()==proof['sha256'],'Reviewed badge payload authenticated')
            graphics=0xb000 if shop else 0x20
            for n in range(10):
                for row in (0,128):
                    p=graphics+256*n+row;q=proof['offset']+256*n+row
                    check(vram[p:p+64]==data[q:q+64],f'Approved badge {116+n} head row {row//128} reaches actual VRAM')
    tap(1024,180);check(observe(prefix+'-original-jobs')==0xa700,'L returns original jobs')
    tap(1024,180);check(observe(prefix+'-wrap-new-jobs')==0xa701,'L wraps to new jobs')
    tap(1,180);check(observe(prefix+'-closed')==0,'B closes panel and clears page marker')
    after=e.memory()[0x80:0x1e70]
    delta=[dict(address=hex(i+0x02000080),before=a,after=b) for i,(a,b) in enumerate(zip(before,after)) if a!=b]
    (out/'owned-memory-delta.json').write_text(json.dumps(delta,indent=2))
    if shop:
        # Compare the same help lifetime against the authenticated shipping ROM;
        # distinguish native menu bookkeeping from any change introduced here.
        check(e.memory()[0x1f64:0x1f68]==money,'Preview navigation preserves money')
        e.close()
        base=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
        basepath=Path(base['path']);assert hashlib.sha1(basepath.read_bytes()).hexdigest()==base['romSha1']
        e=E(basepath);e.set_memory(0,seed,0);e.run(3600)
        for key in (8,256,256,256):tap(key,300)
        baseline_before=e.memory()[0x80:0x1e70]
        enter_shop()
        for key in (4,256,256,4):tap(key,180)
        e.screenshot(out/'shop-baseline-original.png')
        baseline_vram=C.string_at(*e.maps[0x06000000])
        for row in range(6):
            for y in range(2):
                start=0x5800+((2+row*3+y)*32+1)*2
                check(original_vram[start:start+56]==baseline_vram[start:start+56],f'Original grid row {row}/{y} matches shipping layout and palettes')
        tap(1,180)
        baseline_after=e.memory()[0x80:0x1e70]
        baseline_delta=[dict(address=hex(i+0x02000080),before=a,after=b) for i,(a,b) in enumerate(zip(baseline_before,baseline_after)) if a!=b]
        (out/'baseline-owned-memory-delta.json').write_text(json.dumps(baseline_delta,indent=2))
        check(delta==baseline_delta,'Preview introduces no roster inventory or AP changes beyond native help bookkeeping')
    else:check(after==before,'Preview navigation preserves roster inventory and AP')
    check(seedpath.read_bytes()==seed,'Private seed file unchanged')
    check(e.memory()[0x1f64:0x1f68]==money,'Preview navigation preserves money')
    (out/'report.json').write_text(json.dumps(dict(status='passed',romSha1=meta['romSha1'],checks=checks,inputs=inputs,observations=observations,
        coverage='Actual '+prefix+' preview opening, paging, wrapping and exit. Production artwork still pending.'),indent=2)+'\n')
    print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),romSha1=meta['romSha1'],checks=checks,inputs=inputs,observations=observations),indent=2)+'\n')
    print('Artifacts: '+str(out),flush=True);raise
finally:e.close()
