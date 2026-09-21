"""Unchanged relocated Samurai through native deployment and battle rendering.

Reuse the authenticated shipping pre-deployment world checkpoint and route.
Only a declared generic Human's class is set before battle actors exist.
No player save, injected result or post-allocation actor-memory edit is used.
"""
import ctypes as C,datetime,hashlib,json,runpy,struct,sys
from pathlib import Path
from native_art import ROOT,sha
from actor_render_evidence import compare as compare_actor_rendering
generated='--generated' in sys.argv
from art_candidate import candidate
meta=candidate('build/art/generated-actor-poc/current.json' if generated else 'build/art/actor-import/current.json','actor')
fixture=Path(meta['source']).parent/'fixture'
frozen=(fixture/'frozen.gba').read_bytes()
assert hashlib.sha1(frozen).hexdigest()==meta['baseRomSha1']
proof=json.loads((fixture/'report.json').read_text());assert proof['passed'] and proof['romSha1']==meta['baseRomSha1']
route=json.loads((fixture/'route.json').read_text());assert route['romSha1']==meta['baseRomSha1']
seed=fixture/'accepted-world.state';seed_bytes=seed.read_bytes()
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
out=ROOT/('build/art/generated-actor-poc/battle' if generated else 'build/art/actor-import/battle')/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True,exist_ok=False)
observations={};checks=[];inputs=[];e=None
render_reports={};baseline_bg={}
baseline_dir=None
if generated:
    candidates=[]
    for p in (ROOT/'build/art/actor-import/battle').glob('*/report.json'):
        r=json.loads(p.read_text())
        if r['status']=='passed' and r['romSha1']==meta['relocationRomSha1'] and r['baseRomSha1']==meta['baseRomSha1']:
            candidates.append((p,r))
    assert candidates,'Requires passing unchanged native actor battle evidence'
    selected,prior=sorted(candidates,key=lambda v:str(v[0]))[-1];baseline_dir=selected.parent
    observations['baseline']=prior['observations']['baseline']
    assert prior['fixtureSha256']==sha(seed_bytes) and prior['routeSha256']==sha((fixture/'route.json').read_bytes())
    generated_rom=Path(meta['path']).read_bytes()
    generated_tiles=[generated_rom[f['tile']:f['tile']+512] for f in meta['frames']]
    for name,observation in observations['baseline'].items():
        captured=(baseline_dir/f'baseline-{name}.vram').read_bytes()
        assert sha(captured)==observation['vram'],'Baseline VRAM capture drift'
        baseline_bg[name]=captured[:0x10000]
def check(ok,name):
    assert ok,name
    checks.append(name)
def tap(key,wait=180):
    inputs.append([8,key,wait]);e.run(8,key);e.run(wait)
def capture(name):
    ram=e.memory();vram=C.string_at(*e.maps[0x06000000]);iw=C.string_at(*e.maps[0x03000000])
    pointers=[dict(offset=hex(i*4),pointer=hex(v[0])) for i,v in enumerate(struct.iter_unpack('<I',ram))
              if 0x08000000+meta['used'][0]<=v[0]<0x08000000+meta['used'][1]]
    observations[kind][name]=dict(frame=sha(e.frame[0]),vram=sha(vram),owned=sha(ram[0x80:0x1e70]),newPointers=pointers)
    if generated:
        matches=[dict(frame=f,offset=i) for f,raw in enumerate(generated_tiles) for i in range(0x10000,len(vram)-511,32) if vram[i:i+512]==raw]
        observations[kind][name]['generatedTiles']=matches
        check(0x07000000 in e.maps and 0x05000000 in e.maps,name+' hardware graphics maps available')
        oam=C.string_at(*e.maps[0x07000000]);pal=C.string_at(*e.maps[0x05000000])
        expected=generated_rom[meta['nativePaletteReference']+2:meta['nativePaletteReference']+32]
        objects=[]
        for match in matches:
            tile=(match['offset']-0x10000)//32
            for i in range(128):
                a,b,c,_=struct.unpack_from('<4H',oam,i*8)
                if c&1023==tile and a&0x300!=0x200:
                    bank=c>>12
                    check(pal[0x200+32*bank+2:0x200+32*(bank+1)]==expected,name+' displayed OAM palette matches conversion reference')
                    objects.append(dict(index=i,tile=tile,paletteBank=bank))
        check(bool(objects),name+' generated tiles referenced by displayed OAM')
        observations[kind][name]['generatedObjects']=objects
    e.screenshot(out/f'{kind}-{name}.png')
    if 0x07000000 in e.maps:(out/f'{kind}-{name}.oam').write_bytes(C.string_at(*e.maps[0x07000000]))
    if 0x05000000 in e.maps:(out/f'{kind}-{name}.palette').write_bytes(C.string_at(*e.maps[0x05000000]))
    for suffix,data in [('ram',ram),('iwram',iw),('vram',vram)]: (out/f'{kind}-{name}.{suffix}').write_bytes(data)
    check(iw[0x6170:0x6d68]==frozen[0xa38d24:0xa3991c],kind+'/'+name+' native renderer code intact')
    check(ram[0x3ff44:]==bytes([0xd7])*0xbc,kind+'/'+name+' reserved memory guard intact')
try:
    scenarios=[('relocated',Path(meta['path']),meta['romSha1'])]
    if not generated:scenarios.insert(0,('baseline',Path(meta['source']),meta['baseRomSha1']))
    for kind,path,digest in scenarios:
        check(hashlib.sha1(path.read_bytes()).hexdigest()==digest,kind+' ROM authenticated')
        e=E(path);e.load(seed);observations[kind]={}
        address=0x80+264*2
        check(e.memory()[address+4:address+8]==bytes([1,2,1,2]),kind+' declared generic Human slot2')
        for offset in (5,7,0x35):e.set_memory(address+offset,bytes([116]))
        for x,y,key in route['path']:e.run(1,key)
        e.run(30);tap(256,1200)
        for _ in range(7):tap(256,600)
        for _ in range(3):tap(256)
        for _ in range(3):
            for key in (128,256,256,256):tap(key)
        capture('deployed')
        tap(8,600);tap(256,600);tap(256,600)
        wait=observe['wait_for_menu'](e);inputs.append(dict(kind=kind,waitForMenu=wait))
        capture('battle-ready')
        for f in range(12):e.run(8);capture('idle-'+str(f))
        e.close();e=None
    for name,old in observations['baseline'].items():
        for field in (('owned',) if generated else ('frame','vram','owned')):
            check(observations['relocated'][name][field]==old[field],name+' unchanged '+field)
        if generated:
            before=(baseline_dir/f'baseline-{name}.vram').read_bytes()
            after=(out/f'relocated-{name}.vram').read_bytes()
            phases={'deployed':baseline_bg['deployed']} if name=='deployed' else {k:v for k,v in baseline_bg.items() if k!='deployed'}
            oracle=compare_actor_rendering(frozen,generated_rom,(baseline_dir/f'baseline-{name}.ram').read_bytes(),
                       (out/f'relocated-{name}.ram').read_bytes(),before,after,phases)
            render_reports[name]=oracle
            checks.extend(name+'/'+c for c in oracle['checks'])
    check(any(v['newPointers'] for v in observations['relocated'].values()),'Native battle actors hold relocated resource pointers')
    check(not any(v['newPointers'] for v in observations['baseline'].values()),'Baseline has no private actor pointers')
    check(seed.read_bytes()==seed_bytes,'Reused seed unchanged')
    if generated:
        seen={m['frame'] for v in observations['relocated'].values() for m in v['generatedTiles']}
        check(len(seen)>=2,'At least two complete generated idle frames reached actual battle VRAM')
        check(any(v['frame']!=observations['baseline'][n]['frame'] for n,v in observations['relocated'].items()),'Generated artwork changes actual framebuffer')
    report=dict(status='passed',romSha1=meta['romSha1'],baseRomSha1=meta['baseRomSha1'],
                fixture=str(seed),fixtureSha256=sha(seed_bytes),routeSha256=sha((fixture/'route.json').read_bytes()),
                declaredInputs='Generic Human slot2 job fields5/7/35=116 before native deployment, fixed saved Giza route and deployment inputs.',
                checks=checks,inputs=inputs,observations=observations,rendering=render_reports,
                reusedBaseline=str(baseline_dir) if generated else None,
                coverage=('Generated Samurai land idle: complete512-byte frame transport, all12 native resource/facing sequences and displayed tiles, allocation bounds, exact original background phases and unchanged owned state; reused passing baseline. Handles native deferred/queued uploads explicitly. No full directions/action/water/custom-palette/production acceptance.' if generated else 'Actual Samurai land deployment, first turn and96 idle frames; exact framebuffer/VRAM/owned-state equality and private resource pointers. No action/water/custom-art/palette acceptance.'))
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),romSha1=meta['romSha1'],checks=checks,inputs=inputs,observations=observations),indent=2)+'\n')
    print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
