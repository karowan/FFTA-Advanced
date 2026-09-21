"""Generated axe icon: equipment/quest namespace preservation and native UI."""
import ast,ctypes as C,datetime,hashlib,json,runpy,struct,sys
from pathlib import Path
from PIL import Image
from native_art import ROOT,sha,tile_image
from native_miniatures import decode
manifest=ROOT/'build/art/generated-equipment/current.json'
if '--manifest' in sys.argv:manifest=ROOT/sys.argv[sys.argv.index('--manifest')+1]
meta=json.loads(manifest.read_text());rom=Path(meta['path']).read_bytes();base=Path(meta['source']).read_bytes()
if 'components' in meta:
    assembled=meta;meta=dict(assembled['components']['equipment'])
    meta.update(path=assembled['path'],romSha1=assembled['romSha1'])
    rom=Path(meta['path']).read_bytes();base=Path(meta['source']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1'] and hashlib.sha1(base).hexdigest()==meta['baseRomSha1']
raw=decode(rom,meta['symbols']['ffta_art_axe_container']-0x08000000,0);assert sha(raw)==meta['pixelsSha256']
out=ROOT/'build/art/generated-equipment/tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];inputs=[];observations={};provenance=[];e=None
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    if '--native' in sys.argv:
        sys.path.insert(0,str(ROOT/'tools/arm-python'))
        from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
        from unicorn.arm_const import *
        tree=ast.parse((ROOT/'scripts/test-equipment-icons.py').read_text())
        exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native icon ABI>','exec'))
        a,b=ARM(rom),ARM(base)
        sites=(0x8168a,0x7031c,0x749e8,0x8e3f2,0x6e6a4,0xd6614)
        references=[];unsupported=[];refout=ROOT/'build/art/native-reference/equipment';refout.mkdir(parents=True,exist_ok=True)
        count=int.from_bytes(base[0x3c83fe:0x3c8400],'big')
        for ident in range(count):
            try:pixels=decode(base,0x3c83fc,ident)
            except (AssertionError,IndexError) as error:
                # Historical377330c4 inherited shipping corruption. The clean
                # original has all522 valid records; repair acceptance is a
                # separate declared test. Keep this parent's gap explicit.
                if meta['romSha1']!='377330c4c16a1c8d3352bf6ae748f45a4fc90a00' or ident not in (467,469):raise
                unsupported.append(dict(index=ident,error=repr(error)));continue
            check(a.icon(0x080cb980,ident,True)==b.icon(0x080cb980,ident,True)==pixels,str(ident)+' generic namespace unchanged native decode')
            references.append(dict(index=ident,bytes=len(pixels),sha256=sha(pixels)))
            (refout/f'icon-{ident:03}.4bpp').write_bytes(pixels)
        (refout/'report.json').write_text(json.dumps(dict(sourceSha1=meta['baseRomSha1'],container=0x3c83fc,records=references,unsupported=unsupported,scope='Valid generic equipment/quest payloads decoded and compared through native API. Shipping corruption467/469 retained as parent gaps, not malformed originals. Palette selectors unchanged; not final artwork.'),indent=2)+'\n')
        for site,mode in [(p,4) for p in sites]+[(0x6796e,m) for m in (4,5,6)]:
            for ident in range(461):
                actual=a.icon(0x08000000+site,ident,True,block=True,mode=mode)
                expected=raw if ident in meta['items'] and mode==4 else b.icon(0x08000000+site,ident,True,block=True,mode=mode)
                check(actual==expected,f'{site:x}/{mode}/{ident} bounded pixels and ABI')
        for ident in range(461):check(a.icon(0x080cb99c,ident,False)==b.icon(0x080cb99c,ident,False),str(ident)+' palette namespace unchanged')
        from generated_equipment_transport import build
        rebuilt=build(Path(meta['source']).parent/'manifest.json',publish_current=False);check(Path(rebuilt['path']).read_bytes()==rom,'Exact generated equipment rebuild')
        scope=f'{len(references)} valid compressed icon payloads; {len(unsupported)} explicitly retained parent gaps. All461 IDs at six equipment/projectile draw callers and shared shop modes4/5/6, canaries/callee registers/stack, unchanged palette API and exact rebuild. Held weapon and actual projectile playback separate.'
    else:
        import numpy as np
        resume='--resume-sell' in sys.argv
        if resume:
            previous=ROOT/'build/art/generated-equipment/tests/20260917T223706.865550Z/failed.json';previous_bytes=previous.read_bytes();prior=json.loads(previous_bytes)
            assert sha(previous_bytes)=='c7bd766b3986a43c5bb13d0cb418ac9b814b6c8cb30a9fd40b25ef18f6d69631'
            assert prior['romSha1']==meta['romSha1'] and prior['error']=='sell-baseline actual Recruit Axe list row exists'
            for surface in ('inventory','buy'):
                assert surface+' exact paired roster inventory AP state' in prior['checks']
                for variant in ('baseline','generated'):
                    name=surface+'-'+variant;obs=prior['observations'][name]['selected']
                    r=(previous.parent/(name+'-selected.ram')).read_bytes();assert sha(r[0x80:0x1e70])==obs['owned']
                    if variant=='generated':assert obs['screenPositions'] and obs['pixelFormat']==2
                    observations[name]=prior['observations'][name]
            checks.extend(prior['checks']);inputs.extend(prior['inputs']);provenance.append(dict(source=str(previous),sha256=sha(previous_bytes),reused='Inventory and Buy complete paired checks; Sell setup failed before dependent acceptance'))
        E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
        seedpath=ROOT/'build/test-lab/early-town.sav';seed=seedpath.read_bytes();check(hashlib.sha1(seed).hexdigest()=='b0199e7490f7c22f84512825a4a1bde08d3b3eec','Authenticated private world seed')
        def tap(key,wait=120):inputs.append([case,8,key,wait]);e.run(8,key);e.run(wait)
        def snapshot(name,expect):
            r=e.memory();vram=C.string_at(*e.maps[0x06000000]);pal=C.string_at(*e.maps[0x05000000]);e.screenshot(out/(case+'-'+name+'.png'))
            for ext,data in (('ram',r),('vram',vram),('palette',pal)):(out/f'{case}-{name}.{ext}').write_bytes(data)
            obs=dict(owned=sha(r[0x80:0x1e70]),money=r[0x1f64:0x1f68].hex(),frame=sha(e.frame[0]));observations[case][name]=obs
            if expect:
                matches=[p for p in range(0,len(vram)-127,32) if vram[p:p+128]==raw];check(bool(matches),case+'/'+name+' generated icon reaches VRAM');obs['VRAM']=matches
                # Require the indexed opaque pixels on the actual native-size
                # screen too, not merely a stale decoded buffer in VRAM.
                # The retained libretro RGB565 frame shifts GBA's five green
                # bits left once; screenshot() scales that six-bit value by
                # 255/63. Match that measured transport exactly, not an RGB555
                # preview or an arbitrary per-channel tolerance.
                pixel_format=e.frame[4];check(pixel_format==2,case+'/'+name+' authenticated RGB565 screen format');obs['pixelFormat']=pixel_format
                rgb=[(((v>>s)&31)*2*255//63 if s==5 else ((v>>s)&31)*255//31) for v in struct.unpack('<16H',rom[meta['paletteOffset']:meta['paletteOffset']+32]) for s in (0,5,10)]
                icon=tile_image(raw,rgb,16);idx=np.array(icon);colors=np.array(icon.convert('RGB'),dtype=np.int16)
                screen=np.array(Image.open(out/(case+'-'+name+'.png')).convert('RGB').resize((240,160),Image.Resampling.NEAREST),dtype=np.int16)
                ys,xs=np.nonzero(idx);visible=[]
                for yy in range(145):
                    candidates=np.nonzero(np.max(np.abs(screen[yy+ys[0],xs[0]:225+xs[0]]-colors[ys[0],xs[0]]),axis=1)==0)[0]
                    for xx in candidates:
                        if np.max(np.abs(screen[yy+ys,xx+xs]-colors[ys,xs]))==0:visible.append([int(xx),yy])
                check(bool(visible),case+'/'+name+' complete opaque icon visible at native resolution');obs['screenPositions']=visible
            return r
        for surface in (('sell',) if resume else ('inventory','buy','sell')):
            for variant,path in (('baseline',meta['source']),('generated',meta['path'])):
                case=surface+'-'+variant;observations[case]={};e=E(Path(path));e.set_memory(0,seed,0);e.run(3600)
                for key,wait in ((8,180),(256,60),(256,60),(256,180)):tap(key,wait)
                if surface!='buy':e.set_memory(0x1940+453,b'\x01');inputs.append([case,'disposable owned Recruit Axe453',1])
                initial=e.memory()
                if surface=='inventory':
                    for key in (8,256,8,128):tap(key,180)
                    r=e.memory();context=struct.unpack_from('<I',C.string_at(*e.maps[0x03000000]),0x2818)[0]-0x02000000
                    list_at=struct.unpack_from('<I',r,context+0x2d50)[0]-0x02000000
                    check(0<=list_at<=0x40000-0x2700,case+' native owned inventory list is in RAM')
                    count=struct.unpack_from('<I',r,list_at)[0]
                    check(count<=460,case+' bounded native inventory count')
                    ids=[struct.unpack_from('<I',r,list_at+0x234+i*20)[0] for i in range(count)]
                else:
                    for key,wait in ((256,240),(32,120),(256,180)):tap(key,wait)
                    if surface=='sell':tap(32)
                    tap(256);tap(128)
                    if surface=='buy':tap(128)
                    r=e.memory();context=struct.unpack_from('<I',r,0xf428)[0]-0x02000000;count=struct.unpack_from('<H',r,context+0xa338)[0]
                    ids=[struct.unpack_from('<H',r,context+0x9c08+i*4)[0] for i in range(count)]
                check(453 in ids and ids.index(453)<50,case+' actual Recruit Axe list row exists')
                for _ in range(ids.index(453)):tap(32,20)
                current=snapshot('selected',variant=='generated')
                check(current[0x1f64:0x1f68]==initial[0x1f64:0x1f68],case+' viewing performs no purchase/sale')
                if variant=='baseline':control=current
                else:check(current[0x80:0x1e70]==control[0x80:0x1e70],surface+' exact paired roster inventory AP state')
                tap(1,180);e.close();e=None
        check(seedpath.read_bytes()==seed,'Private source save unchanged')
        scope=f'Actual inventory/Buy/Sell Recruit Axe selection, exact VRAM and native-resolution opaque pixel visibility, paired gameplay preservation and no transactions. All{len(meta["items"])} IDs native-tested separately; held weapon/effects/projectile playback and final art remain open.'
    report=dict(status='passed',romSha1=meta['romSha1'],baseRomSha1=meta['baseRomSha1'],checks=checks,inputs=inputs,observations=observations,provenance=provenance,scope=scope)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    if e:
        e.save(out/'failed.state');e.screenshot(out/'failed.png')
        for ext,addr in (('ram',0x02000000),('iwram',0x03000000),('vram',0x06000000),('palette',0x05000000),('oam',0x07000000)):(out/('failed.'+ext)).write_bytes(C.string_at(*e.maps[addr]))
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),checks=checks,inputs=inputs,observations=observations),indent=2)+'\n');print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
