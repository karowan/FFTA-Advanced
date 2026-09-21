"""Fresh native Soldier Tomahawk with generated projectile pixels and control.

Starts from the authenticated world checkpoint, constructs battle objects with
the current ROM, and uses native menus. Only profiles, learning and formation
are declared inputs. The control delegates the icon dispatcher to its original
implementation; item identity, action/effect code and held weapons stay exact.
"""
import ctypes as C,datetime,hashlib,json,runpy,struct,sys
from pathlib import Path
from native_art import ROOT,sha
from native_miniatures import decode
from native_battle_wrappers import fixed_giza_formation,from_emulator

connected='--manifest' in sys.argv
if connected:
    manifest=ROOT/sys.argv[sys.argv.index('--manifest')+1];chain=json.loads(manifest.read_text())
    assert chain['schema']==3
    m=dict(chain['components']['weapon'],path=chain['path'],romSha1=chain['romSha1'],releaseSource=chain['fixtureSource'])
    equipment=chain['components']['equipment'];live=chain['components']['livePalette'];effect=chain['components']['effect']
    from native_effect_art import reference
    from ffta_maps import lz77
else:
    m=json.loads((ROOT/'build/art/generated-weapon/current.json').read_text())
    chain=json.loads((ROOT/'build/art/clean-chain/current.json').read_text());equipment=chain['components']['equipment']
    assert m['baseRomSha1']==chain['romSha1']
image=Path(m['path']).read_bytes();assert hashlib.sha1(image).hexdigest()==m['romSha1']
assert struct.unpack_from('<I',image,0xcb984)[0]==equipment['symbols']['ffta_art_equipment_entry']|1
control=bytearray(image);struct.pack_into('<I',control,0xcb984,equipment['originalEntry']|1)
assert control[:0xcb984]==image[:0xcb984] and control[0xcb988:]==image[0xcb988:]
out=ROOT/'build/art/generated-projectile'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
controlpath=out/'original-icon-control.gba';controlpath.write_bytes(control)
fixture=Path(m['releaseSource']).parent/'fixture';seed=fixture/'accepted-world.state';seedbytes=seed.read_bytes()
routepath=fixture/'route.json';route=json.loads(routepath.read_text());proof=json.loads((fixture/'report.json').read_text())
assert proof['passed'] and proof['romSha1']==route['romSha1']==hashlib.sha1(Path(m['releaseSource']).read_bytes()).hexdigest()
assert (fixture/'frozen.gba').read_bytes()==Path(m['releaseSource']).read_bytes()
registry=json.loads((ROOT/'build/expansion/registry.json').read_text());lesson=next(l for l in registry['lessons'] if l['id']=='SLD-AX-A2')
assert lesson['globalAbilityId']==425 and lesson['owners']==[dict(jobId=2,race=1,abilityIndex=173)]
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];menu=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
raw=decode(image,equipment['symbols']['ffta_art_axe_container']-0x08000000,0);original=decode(image,0x3c83fc,52)
assert sha(raw)==equipment['pixelsSha256'] and raw!=original
checks=[];inputs=[];observations={};outcomes={};coexistence={};e=None;case='setup'
half=lambda r,p:struct.unpack_from('<H',r,p)[0]
word=lambda r,p:struct.unpack_from('<I',r,p)[0]
def check(ok,label):
    assert ok,case+'/'+label
    checks.append(case+'/'+label)
def active():
    r=e.memory();return word(r,word(r,0xf438)-0x02000000+24)
def tap(key,wait=180):
    inputs.append([case,8,key,wait]);e.run(8,key);e.run(wait)
def capture(name):
    e.screenshot(out/(case+'-'+name+'.png'));e.save(out/(case+'-'+name+'.state'))
    r=e.memory()
    for ext,address in (('ram',0x02000000),('iwram',0x03000000),('vram',0x06000000),('palette',0x05000000),('oam',0x07000000)):
        (out/(case+'-'+name+'.'+ext)).write_bytes(C.string_at(*e.maps[address]))
    return r
try:
    if connected:
        effect_pixels=lz77(image,effect['payload']+4).data
        effect_palettes={p['raw'] for p in reference(image)['palettes']}
        check(sha(effect_pixels)==effect['pixelsSha256'],'Connected impact atlas authenticated')
    for case,path in (('baseline',controlpath),('generated',Path(m['path']))):
        rom=Path(path).read_bytes();e=E(path);e.load(seed);e.set_memory(0x3ff44,bytes(8))
        # Preserve named identities. Give Marche his actual Soldier command and
        # axe454 before any battle object exists; clear other native learning.
        check(e.memory()[0x86]==1,'Marche is human')
        e.set_memory(0x87,b'\x02');e.set_memory(0xb5,b'\x00');e.set_memory(0xaa,struct.pack('<5H',454,0,0,0,0))
        e.set_memory(0xc0,bytes(0x90));e.set_memory(0x1b5d,b'\xff')
        inputs.append([case,'Soldier2/axe454/Tomahawk173 learned before deployment'])
        if connected:
            for slot,job,race in ((2,116,1),(3,118,2),(4,120,3),(5,124,4)):
                p=0x80+264*slot
                check(e.memory()[p+4]==1 and e.memory()[p+6]==race,'Existing generic racial profile '+str(slot))
                e.set_memory(p+4,bytes((1,job,race,job)));e.set_memory(p+0x35,bytes([job]))
                e.set_memory(p+0x2a,bytes(10))
                inputs.append([case,'pre-allocation unarmed racial profile',slot,job,race])
        for x,y,key in route['path']:e.run(1,key)
        e.run(30);tap(256,1200)
        for _ in range(7):tap(256,600)
        for _ in range(3):tap(256)
        for _ in range(3):
            for key in (128,256,256,256):tap(key)
        tap(8,600);tap(256,600);tap(256,600);menu['wait_for_menu'](e)
        for turn in range(12):
            if active()==0x02000080:break
            old=active()
            for key in (32,32,256,256):tap(key)
            for waited in range(0,6300,30):
                if active()!=old and menu['menu_visible'](e):break
                e.run(30)
            else:raise AssertionError('Waiting actor did not advance')
        check(active()==0x02000080,'Native Soldier turn')
        fixed_giza_formation(rom,e);e.run(30);wrappers=from_emulator(rom,e)
        e.set_memory(0x98,struct.pack('<4H',100,100,16,16));e.set_memory(0x33fc,struct.pack('<HH',250,250))
        before=capture('ready');check(half(before,0xaa)==454,'Axe remains equipped')
        # Act -> Battle Tech -> sole learned Tomahawk. Target is3right/1down.
        for key in (32,256,32,256):tap(key)
        capture('command-list');tap(256)
        r=e.memory();manager=word(r,0xf438)-0x02000000
        check(word(r,manager+20)==425,'Native selected Tomahawk425')
        for key in (128,128,128,32,256,256):tap(key)
        confirmed=capture('confirmation');manager=word(confirmed,0xf438)-0x02000000
        check(confirmed[manager+4]==11,'Native final confirmation')
        C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',1),4);inputs.append([case,'native RNG',1])
        e.run(8,256);samples=[];expected=original if case=='baseline' else raw;positions=set();impact_seen=set();coexistence[case]=[]
        for frame in range(0,720,4):
            e.run(4);vram=C.string_at(*e.maps[0x06000000]);oam=C.string_at(*e.maps[0x07000000]);pal=C.string_at(*e.maps[0x05000000])
            found=[]
            for index in range(128):
                a,b,c=struct.unpack_from('<3H',oam,index*8);x=b&511;y=a&255;tile=c&1023
                # FE070 assigns projectile palette8. Held blade/trail palettes
                #0/6 cannot satisfy this oracle even when they share axe pixels.
                if a&0x300==0x200 or c>>12!=8 or x>=240 or y>=160:continue
                if vram[0x10000+tile*32:0x10000+tile*32+128]!=expected:continue
                check(pal[512+8*32:544+8*32]==rom[0x419d60:0x419d80],'Exact actual projectile palette')
                found.append(dict(index=index,attributes=[a,b,c],tile=tile,x=x,y=y))
                positions.add((x,y))
            if found:
                samples.append(dict(frame=frame+4,objects=found,frameSha256=sha(e.frame[0])))
                if len(samples)<=4:capture('projectile-'+str(frame+4))
            if connected:
                impacts=[]
                for index in range(128):
                    a,b,c=struct.unpack_from('<3H',oam,index*8);tile=c&1023
                    if a&0x300==0x200 or c>>12!=6 or not 996<=tile<1023 or b&511>=240 or a&255>=160:continue
                    impacts.append(dict(index=index,attributes=[a,b,c],tile=tile))
                if impacts:
                    check(vram[0x17c80:0x17fe0]==effect_pixels,'Connected actual impact atlas exact')
                    check(pal[704:736].hex() in effect_palettes,'Connected native impact cycling palette')
                    pose=(min(v['tile'] for v in impacts)-996)//9
                    if pose not in impact_seen:capture('impact-'+str(pose)+'-'+str(frame+4))
                    impact_seen.add(pose)
                # This action uses independent projectile8/impact6 banks. The
                # four unarmed idle allies must keep their baseline/dim colors.
                if 'nativePaletteTransport' in chain['components']:
                    from native_shared_palette_evidence import observe as palette_observe
                    state=palette_observe(rom,e.memory(),pal,oam,wrappers,check,{0,2,4,8})
                else:
                    from live_palette_evidence import observe as palette_observe
                    state=palette_observe(live,rom,e.memory(),pal,oam,check,{0,2,4,8})
                if found or impacts:
                    effect_banks=({8} if found else set())|({6} if impacts else set())
                    check(not (effect_banks&{v['bank'] for v in state['objects']}),
                          'Effect/projectile banks have no custom body owner')
                    coexistence[case].append(dict(frame=frame+4,custom=state,projectile=found,impact=impacts))
        e.run(1080);after=capture('executed')
        check(len(positions)>=2,'Generated/original projectile moves on visible hardware OAM')
        if connected:
            check(impact_seen=={0,1,2},'All three connected impact poses visibly scheduled')
            check(any(v['projectile'] for v in coexistence[case]) and any(v['impact'] for v in coexistence[case]),'Generated class palettes coexist with both projectile and impact')
        check(half(after,0x9c)==12,'Exactly4MP paid')
        check(half(after,0x33fc)<250,'Tomahawk hit completed')
        for lo,hi in ((0xaa,0xb4),(0x1940,0x1ebc)):
            check(after[lo:hi]==before[lo:hi],f'No equipment/inventory/AP mutation {lo:x}')
        check(after[0x3ff44:0x3ff4c]==bytes(8) and after[0x3ff4c:]==b'\xd7'*0xb4,'Transient roots retired and guard intact')
        outcomes[case]=dict(damage=250-half(after,0x33fc),mp=half(after,0x9c),exp=after[0x8a])
        observations[case]=samples
        for key in (32,32,256,256):tap(key)
        for waited in range(0,6300,30):
            if active()!=0x02000080 and menu['menu_visible'](e):break
            e.run(30)
        else:raise AssertionError('Tomahawk next turn missing')
        check(active()!=0x02000080,'Native following turn');capture('returned');e.close();e=None
    check(outcomes['baseline']==outcomes['generated'],'Exact paired action outcome')
    check(seed.read_bytes()==seedbytes,'Source world seed unchanged')
    report=dict(status='passed',romSha1=m['romSha1'],controlSha1=hashlib.sha1(control).hexdigest(),checks=checks,inputs=inputs,
        observations=observations,outcomes=outcomes,fixtureSha256=sha(seedbytes),routeSha256=sha(routepath.read_bytes()),
        scope='Fresh native Soldier Tomahawk targeting, palette8 original/generated projectile tile upload and on-screen hardware movement,4MP once/no consumption/exact paired damage and following turn. Built-in imagegen axe is temporary. No other effect, rotating final artwork, cold-save or campaign acceptance.')
    if connected:
        report['coexistence']=coexistence
        report['scope']='Fresh connected candidate Soldier Tomahawk through native menus with four declared generic racial allies, custom actor palettes, original/generated axe projectile control, all three generated impact poses and native cycling colors, disjoint hardware banks, exact gameplay outcome and following turn. Both controls use the same generated impact. Four-frame sampling; no other effect, caster-class, response timing, final-art or campaign acceptance.'
        if 'nativePaletteTransport' in chain['components']:
            report['scope']=report['scope'].replace('custom actor palettes','exact native baseline/dim body palettes')
            report['nativePaletteTransport']=True
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    if e:capture('failed')
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=m['romSha1'],error=str(error),checks=checks,inputs=inputs,observations=observations,outcomes=outcomes),indent=2)+'\n')
    print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
