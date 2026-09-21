"""Native descriptor, bounded rebuild and actual three-pose menu playback proof."""
import ast, ctypes as C, datetime, hashlib, json, runpy, struct, sys
from pathlib import Path
from native_art import ROOT, TILES, OAM, sha
from actor_render_evidence import actors
from samurai_idle_transport import build, START
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
out=ROOT/'build/art/samurai-idle/tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[]; inputs=[]; observations={}; e=None; meta={}
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    meta=build(); rom=Path(meta['path']).read_bytes(); base=Path(meta['source']).read_bytes()
    check(hashlib.sha1(rom).hexdigest()==meta['romSha1'],'Authenticated candidate')
    check(hashlib.sha1(base).hexdigest()==meta['baseRomSha1'],'Authenticated assembled parent')
    entry=meta['entry']; end=meta['used'][1]
    check(rom[:entry]==base[:entry] and rom[entry+4:START]==base[entry+4:START] and rom[end:]==base[end:] and len(rom)==len(base),'Whole-ROM delta limited to one actor table entry and owned reservation')
    a=ARM(rom,(Path(meta['fixtureSource']).parent/'fixture/battle-ready.iwram').read_bytes())
    check(a.call(0x080c8570,116,2,4)==256,'Native Samurai resolves owned resource')
    check(a.call(0x08021054,256)==16,'Native allocation remains16 tiles')
    check(a.call(0x080c8570,116,2,6)==1,'Native actor palette selector unchanged')
    old,new=meta['sourceDescriptors'],meta['descriptors'];size=meta['slots']*12
    check(rom[new+24:new+size]==base[old+24:old+size],'All non-idle descriptors exact')
    for seq in meta['sequences']:
        slot=seq['slot']; p=seq['target']; q=seq['source']
        for mode in ((0,3) if slot==0 else (1,2)):
            check(a.word(a.call(0x08021004,256,mode))==0x08000000+p,f'Native facing{mode} sequence')
        check(rom[new+12*slot+4:new+12*slot+12]==base[old+12*slot+4:old+12*slot+12],f'Slot{slot} descriptor metadata exact')
        for f,i in enumerate(seq['frames']):
            frame=meta['frames'][i];t,o=struct.unpack_from('<II',rom,p+4+20*f)
            check(rom[p+12+20*f:p+24+20*f]==base[q+12+20*f:q+24+20*f],f'{slot}/{f} original timing commands metadata')
            check(t+TILES==frame['tile'] and o+OAM==frame['oam'] and sha(rom[TILES+t:TILES+t+512])==frame['sha256'],f'{slot}/{f} exact generated source pixels and OAM')
    rebuilt=build(publish_current=False)
    check(rebuilt['romSha1']==meta['romSha1'] and Path(rebuilt['path']).read_bytes()==rom,'Deterministic exact source-stage rebuild')
    seedpath=ROOT/'build/showcase/20260917T160011.215713Z/showcase.sav';seed=seedpath.read_bytes()
    check(hashlib.sha1(seed).hexdigest()=='7831543efb239ef145764889214f8d83cd56eb14','Authenticated disposable save fixture')
    E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
    snapshots={}
    for case,path,blob in (('parent',meta['source'],base),('candidate',meta['path'],rom)):
        e=E(Path(path));e.set_memory(0,seed,0);e.run(3600)
        def tap(key,wait=120):
            inputs.append([case,8,key,wait]);e.run(8,key);e.run(wait)
        for key in (8,256,256,256):tap(key,300)
        p=0x80+264*2;check(e.memory()[p+6]==1,case+' same-race human fixture')
        e.set_memory(p+4,bytes([1,116,1,116]));inputs.append([case,'appearance',2,[1,116,1,116]])
        for key in (8,256,128,128,256,32,32):tap(key)
        tap(256,600)
        samples=[];seen=set()
        observations[case]=dict(samples=samples,seen=[])
        for tick in range(64):
            ram=e.memory();vram=C.string_at(*e.maps[0x06000000]);pal=C.string_at(*e.maps[0x05000000]);oam=C.string_at(*e.maps[0x07000000])
            found=actors(blob,ram,vram)
            observations[case]['lastActors']=found
            check(len(found)==1 and found[0]['resource']==256,case+f'/{tick} one intended actor')
            actor=found[0]
            # The actual menu reserves20 tiles; the native resource size and
            # generated OAM still draw16. Retained accepted parent capture
            # generated-116-wheel0 proves this same menu allocation contract.
            check(actor['declaredSequence'] and bool(actor['displayedFrames']) and actor['expectedTiles']==actor['tileCount']==16 and actor['allocation']==20,case+f'/{tick} valid native sequence and bounded upload')
            pos=0x10000+actor['tile']*32; raw=vram[pos:pos+512]
            frame=next((i for i,f in enumerate(meta['frames']) if sha(raw)==f['sha256']),None)
            if case=='candidate':
                check(frame is not None,case+f'/{tick} exact generated frame in VRAM');seen.add(frame)
            samples.append(dict(tick=tick,actor=actor,sourceFrame=frame,pixelSha256=sha(raw),paletteSha256=sha(pal),ownedSha256=sha(ram[0x80:0x1e70]),outsideActorSha256=sha(vram[:pos]+vram[pos+512:]),oamSha256=sha(oam)))
            if tick in (0,8,16,24,32,40,48,56):
                stem=out/f'{case}-{tick:02}';e.screenshot(stem.with_suffix('.png'))
                for suffix,data in (('ram',ram),('vram',vram),('pal',pal),('oam',oam)):stem.with_suffix('.'+suffix).write_bytes(data)
            e.run(1)
        if case=='candidate':check(seen=={0,1,2} or seen=={3,4,5},'All three actual idle poses observed across64 consecutive frames')
        observations[case]=dict(samples=samples,seen=sorted(seen));snapshots[case]=samples
        tap(1,180);tap(256,600)
        found=actors(blob,e.memory(),C.string_at(*e.maps[0x06000000]))
        check(len(found)==1 and found[0]['resource']==256 and found[0]['declaredSequence'] and bool(found[0]['displayedFrames']),case+' cancel/reopen preserves actor')
        e.close();e=None
    for old,new in zip(snapshots['parent'],snapshots['candidate']):
        for field in ('paletteSha256','ownedSha256','outsideActorSha256','oamSha256'):
            check(old[field]==new[field],f"Frame{old['tick']} unchanged {field}")
    check(seedpath.read_bytes()==seed,'Original fixture unchanged')
    report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,inputs=inputs,observations=observations,
        scope='Bounded exact rebuild; native getters for both idle sequences/all four facings; actual menu64-frame three-pose upload and cancel/reopen; paired unchanged roster, palette, hardware OAM and all VRAM outside owned actor. Other facing actual rendering, battle/water/action and production art not claimed.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta.get('romSha1'),error=str(error),checks=checks,inputs=inputs,observations=observations),indent=2)+'\n');print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
