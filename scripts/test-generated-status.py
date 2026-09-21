"""Generated status import: native bounded rendering and actual icon cycling.

Reuses the authenticated current-candidate water-ready capture. Status grants
are explicit disposable setup, not a proof of gameplay application/expiration.
"""
import ast,ctypes as C,datetime,hashlib,json,runpy,struct,sys
from pathlib import Path
from native_art import ROOT,sha
from native_battle_wrappers import from_emulator
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
arm_source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace(
    'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
    'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(arm_source)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
meta=json.loads((ROOT/'build/art/generated-status/current.json').read_text());release=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
connected='--manifest' in sys.argv
if connected:
    assembled=json.loads((ROOT/sys.argv[sys.argv.index('--manifest')+1]).read_text());assert assembled['schema']==3
    meta=dict(assembled['components']['status'],path=assembled['path'],romSha1=assembled['romSha1'],releaseSource=assembled['fixtureSource'])
base=Path(meta['source']).read_bytes();rom=Path(meta['path']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1'] and hashlib.sha1(base).hexdigest()==meta['baseRomSha1']
seed=ROOT/'build/art/generated-actions/battle/20260917T221612.382005Z/generated-water-ready.state'
if connected:
    assert '--retained-ready' in sys.argv
    source_report=ROOT/sys.argv[sys.argv.index('--retained-ready')+1];prior=json.loads(source_report.read_text())
    assert prior['status']=='passed' and prior['romSha1']==meta['romSha1']
    seed=source_report.parent/'candidate-ready.state'
seedbytes=seed.read_bytes()
iw=(Path(meta['releaseSource']).parent/'fixture/battle-ready.iwram').read_bytes()
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
out=ROOT/'build/art/generated-status/tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];inputs=[];captures={};e=None
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    if connected:
        # Replay only against this exact candidate and a control differing in
        # the128 glyph bytes. All saved actor/code pointers remain unchanged.
        original_status=base[meta['offset']:meta['offset']+128]
        base=rom[:meta['offset']]+original_status+rom[meta['offset']+128:]
        controlpath=out/'original-status-control.gba';controlpath.write_bytes(base)
        meta['source']=str(controlpath);meta['baseRomSha1']=hashlib.sha1(base).hexdigest()
    check(rom[:meta['offset']]==base[:meta['offset']] and rom[meta['offset']+128:]==base[meta['offset']+128:],'Only owned128-byte glyph payload differs')
    a,b=ARM(rom,iw),ARM(base,iw)
    for machine in (a,b):machine.u.mem_map(0x06000000,0x20000)
    fn=release['symbols']['ffta_integrated_status_visual'];sprite=0x02025000
    for icon in range(56):
        for machine in (a,b):machine.put(sprite,b'\xa5'*128);machine.put(0x06000000,b'\x6b'*0x20000)
        actual=a.call(fn,sprite,icon);expected=b.call(fn,sprite,icon)
        check(actual==expected,str(icon)+' tile selector preserved')
        check(a.read(sprite,128)==b.read(sprite,128),str(icon)+' original shape and actor record preserved')
        av=a.read(0x06000000,0x20000);bv=b.read(0x06000000,0x20000)
        if icon in (25,26):
            check(av[0x13c00:0x13c80]==rom[meta['offset']:meta['offset']+128],str(icon)+' exact generated tile upload')
            check(av[:0x13c00]==bv[:0x13c00] and av[0x13c80:]==bv[0x13c80:],str(icon)+' every other VRAM byte preserved')
        else:check(av==bv,str(icon)+' all other native/custom status pixels preserved')
    from generated_status_transport import build
    if connected:
        original_component=assembled['components']['status']
        rebuilt=build(Path(original_component['source']).parent/'manifest.json',publish_current=False)
        check(rebuilt['romSha1']==original_component['romSha1'],'Exact inherited status-stage rebuild')
        check(Path(rebuilt['path']).read_bytes()[meta['offset']:meta['offset']+128]==rom[meta['offset']:meta['offset']+128],'Final ROM retains rebuilt glyph payload')
    else:
        rebuilt=build();check(Path(rebuilt['path']).read_bytes()==rom,'Exact generated status rebuild')
    for case,path,image in (('baseline',meta['source'],base),('generated',meta['path'],rom)):
        e=E(Path(path));e.load(seed);wrappers=from_emulator(image,e);w=wrappers[0x398]
        if connected:
            check(e.memory()==(source_report.parent/'candidate-ready.ram').read_bytes(),case+' exact retained candidate RAM before status grants')
            check(C.string_at(*e.maps[0x03000000])==(source_report.parent/'candidate-ready.iwram').read_bytes(),case+' exact retained candidate IWRAM')
        # Exposed bit0 and Centered duration2; original Protect bitEB.1.
        e.set_memory(0x1e9b,b'\x05');r=e.memory();e.set_memory(0x398+0xeb,bytes([r[0x398+0xeb]|2]));initial=e.memory()
        inputs.append(dict(case=case,stateSha256=sha(seedbytes),packedStatusAddress=0x1e9b,value=5,protectAddress=0x398+0xeb))
        seen=set();captured={};hardware=[]
        for frame in range(900):
            e.run(1);r=e.memory();icon=r[w+0x75];seen.add(icon)
            if icon not in (25,26) or icon in captured:continue
            sprite_address=struct.unpack_from('<I',r,w+0x48)[0]-0x02000000;tile=struct.unpack_from('<H',r,sprite_address+0x12)[0]
            if tile!=0x1e0+(icon-25)*2:continue
            vram=C.string_at(*e.maps[0x06000000]);oam=C.string_at(*e.maps[0x07000000]);pal=C.string_at(*e.maps[0x05000000]);objects=[]
            for i in range(128):
                aa,bb,cc=struct.unpack_from('<3H',oam,8*i)
                if cc&1023==tile and not aa&0x300 and aa&255<160 and bb&511<240:objects.append(dict(index=i,a=aa,b=bb,c=cc,palette=cc>>12))
            if not objects:continue
            check(all(x['a']>>14==2 and x['b']>>14==0 for x in objects),case+'/'+str(icon)+' actual narrow8x16 OAM')
            check(all(x['palette']==0 for x in objects),case+'/'+str(icon)+' actual native palette bank0')
            check(pal[512:544]==rom[meta['paletteOffset']:meta['paletteOffset']+32],case+'/'+str(icon)+' actual hardware palette authenticated')
            check(vram[0x13c00:0x13c80]==image[meta['offset']:meta['offset']+128],case+'/'+str(icon)+' complete generated/original status upload')
            e.screenshot(out/f'{case}-{icon}.png')
            for ext,data in (('ram',r),('vram',vram),('oam',oam),('palette',pal)):(out/f'{case}-{icon}.{ext}').write_bytes(data)
            captured[icon]=dict(frame=frame,objects=objects,pixelSha256=sha(vram[0x10000+tile*32:0x10000+(tile+2)*32]))
        check({3,25,26}<=seen,case+' original Protect and two custom statuses cycle')
        check(set(captured)=={25,26},case+' both icons actually reach hardware OAM')
        check(e.memory()[0x1940:0x1ebc]==initial[0x1940:0x1ebc],case+' storage unchanged by rendering')
        r=e.memory();vram=C.string_at(*e.maps[0x06000000]);pal=C.string_at(*e.maps[0x05000000]);oam=C.string_at(*e.maps[0x07000000])
        if case=='baseline':control=(r,vram,pal,oam)
        else:
            check(r==control[0] and pal==control[2] and oam==control[3],'Exact paired final EWRAM palette OAM unchanged')
            check(vram[:0x13c00]==control[1][:0x13c00] and vram[0x13c80:]==control[1][0x13c80:],'Every other actual background body weapon HUD tile preserved')
        e.set_memory(0x1e9b,b'\x00');e.run(300);removed=set()
        for frame in range(180):e.run(1);removed.add(e.memory()[w+0x75])
        check(not removed.intersection({25,26}) and 3 in removed,case+' removed effects disappear while Protect remains')
        check(e.memory()[0x3ff4c:]==b'\xd7'*0xb4,case+' guard intact')
        captures[case]=dict(icons=captured,seen=sorted(seen),afterRemoval=sorted(removed));e.close();e=None
    check(seed.read_bytes()==seedbytes,'Source battle state unchanged')
    report=dict(status='passed',romSha1=meta['romSha1'],baseRomSha1=meta['baseRomSha1'],checks=checks,inputs=inputs,captures=captures,
        sourceArt=meta['sourceArt'],sourceArtSha256=meta['sourceArtSha256'],scope='All56 integrated status renderer outputs preserved except two exact generated payloads; actual Exposed/Centered plus Protect cycling, hardware OAM/palette/tiles, removal and paired full-state/VRAM isolation. Controlled status setup. Not grant/expiry gameplay, other new artwork or production acceptance.')
    if connected:report['retainedSource']=dict(report=str(source_report),reportSha256=sha(source_report.read_bytes()),stateSha256=sha(seedbytes),romSha1=assembled['romSha1'],control='Exact final ROM with only128 status pixels restored; identical retained RAM/IWRAM before grants.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    if e:
        e.save(out/'failed.state');e.screenshot(out/'failed.png')
        for ext,addr in (('ram',0x02000000),('iwram',0x03000000),('vram',0x06000000),('palette',0x05000000),('oam',0x07000000)):(out/('failed.'+ext)).write_bytes(C.string_at(*e.maps[addr]))
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),checks=checks,inputs=inputs,captures=captures),indent=2)+'\n');print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
