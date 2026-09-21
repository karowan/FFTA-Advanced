"""Paired native deployment, Move/Fight and turn return with generated actions.

Uses the authenticated shipping world seed and declared job/equipment profiles
before battle actors are constructed. Story appearance identities remain fixed;
four test members are generic. Explicit Moogle water profiles replace generic
slot5's presentation race and retain its test stats. No live actor edits, player
saves, natural recruitment or legal class-switch acceptance.
"""
import ctypes as C,datetime,hashlib,json,runpy,struct,sys
from pathlib import Path
from native_art import ROOT,sha
from actor_render_evidence import actors
from native_battle_wrappers import fixed_giza_formation,from_emulator
from native_body_display import retained,pending_from_anchor,completed_pending_facing
from native_queued_upload import completed as completed_queued_upload
weapon='--weapon' in sys.argv
meta=json.loads((ROOT/('build/art/generated-weapon/current.json' if weapon else 'build/art/generated-actions/current.json')).read_text())
connected='--manifest' in sys.argv
if connected:
    assert weapon, 'Connected manifest currently proves the held-weapon path'
    assembled=json.loads((ROOT/sys.argv[sys.argv.index('--manifest')+1]).read_text())
    assert assembled['schema']==3
    meta=dict(assembled['components']['weapon'],path=assembled['path'],romSha1=assembled['romSha1'],releaseSource=assembled['fixtureSource'])
    palette_meta=assembled['components']['livePalette']
natural_water='--natural-water' in sys.argv
live_palette='--live-palette-water' in sys.argv
assert not live_palette or (natural_water and not weapon)
water_job=int(sys.argv[sys.argv.index('--water-job')+1]) if '--water-job' in sys.argv else 118
assert 116<=water_job<=125 and ('--water-job' not in sys.argv or live_palette)
if natural_water:
    from natural_water_fixture import build as water_fixture,formation as water_formation,MAP as WATER_MAP,LAND,WATER
    if live_palette:
        meta=json.loads((ROOT/'build/art/live-palette/all-classes-workspace-current.json').read_text())
        assert meta['allClasses'] and meta['historySlots']==20
    else:
        assembled=json.loads((ROOT/'build/art/assembled/current.json').read_text())
        meta=dict(assembled['components']['actions'],path=assembled['path'],romSha1=assembled['romSha1'],releaseSource=assembled['source'])
profiles=[(0,116,1,9),(1,123,5,16),(2,117,1,1),(3,118,2,31),(4,120,3,12),(5,124,4,7)]
focus_slot=3
if '--water-job' in sys.argv:
    class_raw=Path(meta['classManifest']).read_bytes();assert sha(class_raw)==meta['classManifestSha256']
    races={j['job']:j['race'] for j in json.loads(class_raw)['classResources']['jobs']}
    race=races[water_job];focus_slot={1:2,2:3,3:4,4:5,5:5}[race]
    profiles=[(slot,water_job,race,0) if slot==focus_slot else (slot,job,original_race,family) for slot,job,original_race,family in profiles]
focus_unit=0x80+264*focus_slot;land_resource=256+2*(water_job-116)
allowed_owners={job-116 for slot,job,race,family in profiles if slot>=2}
fixture=Path(meta['releaseSource']).parent/'fixture';seed=fixture/'accepted-world.state';seedbytes=seed.read_bytes()
routepath=fixture/'route.json';route=json.loads(routepath.read_text())
release=Path(meta['releaseSource']).read_bytes();release_hash=hashlib.sha1(release).hexdigest()
assert route['romSha1']==release_hash and (fixture/'frozen.gba').read_bytes()==release
proof=json.loads((fixture/'report.json').read_text());assert proof['passed'] and proof['romSha1']==release_hash
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
out=ROOT/'build/art/generated-actions/battle'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];inputs=[];observations={};outcomes={};e=None;previous_actors={};wrapper_map={};render_failures=[];previous_weapons={};weapon_captures=set();provenance=[]
pending_anchors={};frame_clock=0
previous_weapon_samples={}
profile_isolation='--profile-isolation' in sys.argv
water='--water' in sys.argv or natural_water
pairs={frozenset((256+2*i,257+2*i)) for i in range(10)}
isolate='--entry-isolation' in sys.argv or profile_isolation
def check(ok,label):
    assert ok,label
    checks.append(label)
def capture(name):
    ram=e.memory();vram=C.string_at(*e.maps[0x06000000])
    body_addresses={struct.unpack_from('<I',ram,w+0x44)[0]-0x02000000 for w in wrapper_map.values()} if wrapper_map else None
    figures=actors(rom,ram,vram,body_addresses if live_palette else None)
    auxiliaries=[]
    if wrapper_map:
        body_addresses={struct.unpack_from('<I',ram,w+0x44)[0]-0x02000000 for w in wrapper_map.values()}
        auxiliaries=[a for a in figures if a['address'] not in body_addresses]
        figures=[a for a in figures if a['address'] in body_addresses]
    obs=dict(frame=sha(e.frame[0]),owned=sha(ram[0x80:0x1e70]),vram=sha(vram),actors=figures,auxiliaryActors=auxiliaries);observations[kind][name]=obs
    next_actors={}
    failed_render=False
    for a in figures:
        a['tileOffset']=struct.unpack_from('<I',ram,a['address']+0x20)[0]
        if not isolate:
            p=0x10000+a['tile']*32;block=vram[p:p+a['allocation']*32]
            direct=bool(a['displayedFrames']);old=previous_actors.get(a['address'])
            if (natural_water or connected) and not direct:
                anchor=pending_anchors.get(a['address'])
                hold=pending_from_anchor(a,block,anchor,frame_clock-anchor['frame'],pairs) if anchor else None
                if not hold:hold=retained(a,block,old,pairs)
                if not hold and anchor:hold=completed_pending_facing(rom,a,block,anchor,frame_clock-anchor['frame'])
            else:hold=retained(a,block,old,pairs) if not direct else None
            for ok,label in [(a['declaredSequence'] and (direct or hold),'exact current or bounded retained display'),
                             (a['expectedTiles']==a['tileCount']<=a['allocation'],'native OAM within allocation')]:
                if ok:checks.append(kind+'/'+name+' '+label)
                else:render_failures.append(dict(case=kind,snapshot=name,address=a['address'],label=label));failed_render=True
            a['displayProof']='current' if direct else hold or 'unverified'
            next_actors[a['address']]=dict(direct=direct and a['declaredSequence'],identity=(a['resource'],a['tile'],a['allocation']),block=block,first=a['first'],index=a['index'])
            if natural_water or connected:
                if direct and a['declaredSequence']:pending_anchors[a['address']]=dict(next_actors[a['address']],frame=frame_clock,actor=dict(a))
                elif not hold:pending_anchors.pop(a['address'],None)
                a['anchorAge']=frame_clock-pending_anchors[a['address']]['frame'] if a['address'] in pending_anchors else None
    previous_actors.clear();previous_actors.update(next_actors)
    if (live_palette and kind=='generated' or connected) and wrapper_map:
        if connected and 'nativePaletteTransport' in assembled['components']:
            from native_shared_palette_evidence import observe as palette_observe
            obs['nativePalette']=palette_observe(rom,ram,C.string_at(*e.maps[0x05000000]),C.string_at(*e.maps[0x07000000]),wrapper_map,
                lambda ok,label:check(ok,kind+'/'+name+' '+label),allowed_owners)
        else:
            from live_palette_evidence import observe as palette_observe
            obs['livePalette']=palette_observe(palette_meta if connected else meta,rom,ram,C.string_at(*e.maps[0x05000000]),C.string_at(*e.maps[0x07000000]),
                lambda ok,label:check(ok,kind+'/'+name+' '+label),allowed_owners)
    if weapon and 0x398 in wrapper_map:
        w=wrapper_map[0x398];expected_resource=meta['resource'] if kind=='generated' else meta['donor'];seen=[];next_weapons={}
        hardware=C.string_at(*e.maps[0x07000000]);pal=C.string_at(*e.maps[0x05000000])
        for channel,offset in enumerate((0x4c,0x50)):
            address=struct.unpack_from('<I',ram,w+offset)[0]-0x02000000
            for a in auxiliaries:
                if a['address']!=address:continue
                table=struct.unpack_from('<I',rom,0x2102c)[0]-0x08000000
                desc=struct.unpack_from('<I',rom,table+a['resource']*4)[0]-0x08000000
                desc+=(a['mode']&~3)*6+(12 if a['mode']&3 in (1,2) else 0)+channel*4
                declared=a['first']==struct.unpack_from('<I',rom,desc)[0]+4
                p=0x10000+a['tile']*32;block=vram[p:p+a['allocation']*32];direct=bool(a['displayedFrames'])
                old_weapon=previous_weapons.get(address)
                if connected and not direct:
                    hold=pending_from_anchor(a,block,old_weapon,frame_clock-old_weapon['frame']) if old_weapon else None
                else:hold=retained(a,block,old_weapon) if not direct else None
                check(a['resource']==expected_resource and declared,kind+'/'+name+' owned held weapon resource/channel')
                check(a['expectedTiles']==a['tileCount']<=a['allocation'],kind+'/'+name+' held weapon OAM within allocation')
                visible=[]
                for index in range(128):
                    aa,bb,cc=struct.unpack_from('<3H',hardware,index*8)
                    if aa&0x300==0x200 or cc&1023!=a['tile']:continue
                    x=bb&511;y=aa&255
                    if x>=240 or y>=160:continue
                    bank=cc>>12;colors=pal[512+bank*32:544+bank*32]
                    matched=[]
                    if channel==0:
                        check(colors==rom[meta['paletteOffset']:meta['paletteOffset']+32],kind+'/'+name+' held weapon actual hardware palette')
                    else:
                        # Native98976 explicitly assigns secondary trail bank6;
                        # it is not the blade's item-selector8 palette. Keep its
                        # original rendered colors exact in the paired child.
                        check(bank==6,kind+'/'+name+' native secondary trail palette bank6')
                        if connected:
                            native_colors=C.string_at(e.maps[0x03000000][0]+0x3a60+6*32,32)
                            check(colors==native_colors,kind+'/'+name+' trail hardware equals current native palette shadow')
                        if kind=='generated':
                            if connected:
                                # This complete original action has one steady
                                # trail palette. Require that unique value AND
                                # the current native shadow, not an arbitrary
                                # matching frame/pose. Timing remains separate.
                                candidates=[(label,a0,v) for label,old in observations['baseline'].items()
                                    if label.startswith('attack-') for a0 in old.get('heldWeapons',[])
                                    if a0['channel']==channel and a0['mode']==a['mode']
                                    for v in a0['hardwareObjects']]
                                prior_colors={v['paletteSha256'] for _,_,v in candidates}
                                check(len(prior_colors)==1,kind+'/'+name+' complete original trail has one steady palette')
                                matched=sorted({label for label,_,v in candidates if v['paletteSha256']==sha(colors)})
                            else:
                                prior=observations['baseline'][name].get('heldWeapons',[])
                                prior_colors={v['paletteSha256'] for a0 in prior if a0['channel']==channel for v in a0['hardwareObjects']}
                            check(sha(colors) in prior_colors,kind+'/'+name+' secondary trail palette equals paired original')
                    visible.append(dict(index=index,attributes=[aa,bb,cc],x=x,y=y,paletteBank=bank,paletteSha256=sha(colors),steadyPaletteControlSamples=matched))
                proof='current' if direct else hold
                if not proof and connected and a['address'] in previous_weapon_samples:
                    previous_sample=previous_weapon_samples[a['address']]
                    proof=completed_queued_upload(rom,a,block,previous_sample,frame_clock-previous_sample['frame'],channel)
                if not proof and connected and not visible and a['flags']&0x120000:
                    proof='not emitted; pending native upload (no displayed-frame acceptance)'
                if not proof:render_failures.append(dict(case=kind,snapshot=name,address=address,label='held weapon frame'));failed_render=True
                else:checks.append(kind+'/'+name+' held weapon display or un-emitted pending state accounted for')
                a.update(channel=channel,heldSequence=declared,hardwareObjects=visible,displayProof=proof or 'unverified');seen.append(a)
                next_weapons[address]=old_weapon if connected and hold else dict(direct=direct and declared,identity=(a['resource'],a['tile'],a['allocation']),block=block,first=a['first'],index=a['index'],frame=frame_clock)
                previous_weapon_samples[address]=dict(actor=dict(a),identity=(a['resource'],a['tile'],a['allocation']),block=block,frame=frame_clock)
                if visible and (kind,channel,a['first']) not in weapon_captures:
                    weapon_captures.add((kind,channel,a['first']));failed_render=True # retain the first actual held display, not a failure
        previous_weapons.clear();previous_weapons.update(next_weapons);obs['heldWeapons']=seen
    check(ram[0x3ff4c:]==b'\xd7'*0xb4,kind+'/'+name+' guard beyond owned action roots intact')
    if failed_render or name in ('deployed','ready','moved','fight','returned','water','land-return') or name.startswith('action-stage'):
        e.screenshot(out/(kind+'-'+name+'.png'))
        for ext,data in [('ram',ram),('vram',vram),('palette',C.string_at(*e.maps[0x05000000])),('oam',C.string_at(*e.maps[0x07000000]))]:(out/(kind+'-'+name+'.'+ext)).write_bytes(data)
    return ram
def run(frames,key=0,sample=None):
    global frame_clock
    if not sample:e.run(frames,key);frame_clock+=frames;return
    interval=1 if live_palette or connected else 8
    for i in range(0,frames,interval):
        step=min(interval,frames-i);e.run(step,key);frame_clock+=step;capture(sample+'-'+str(i))
def tap(key,wait=180,sample=None):
    inputs.append([kind,8,key,wait,sample]);run(8,key,sample+'-press' if sample else None);run(wait,0,sample)
try:
    cases=[('baseline',meta['source'],meta['baseRomSha1']),('generated',meta['path'],meta['romSha1'])]
    if connected and 'nativePaletteTransport' in assembled['components']:
        # The old weapon-stage parent still executes custom composition. Keep
        # current actors/renderer exact and revert only held-axe resource IDs.
        candidate=Path(meta['path']).read_bytes();control=bytearray(candidate);changed=set()
        for item in meta['items']:
            p=meta['itemTable']+32*item+14
            check(struct.unpack_from('<H',candidate,p)[0]==meta['resource'],'Native held control source item '+str(item))
            struct.pack_into('<H',control,p,meta['donor']);changed.update((p,p+1))
        check(all(a==b or i in changed for i,(a,b) in enumerate(zip(candidate,control))),'Control changes only declared held resource fields')
        controlpath=out/'native-held-donor.gba';controlpath.write_bytes(control)
        digest=hashlib.sha1(control).hexdigest();cases[0]=('baseline',str(controlpath),digest)
        provenance.append(dict(path=str(controlpath),romSha1=digest,sourceSha1=meta['romSha1'],changedOffsets=sorted(changed),scope='Only held resource276 to native128 in17 declared axe item records'))
    if weapon and '--reuse-weapon-baseline' in sys.argv:
        priorpath=ROOT/'build/art/generated-actions/battle/20260917T231532.908480Z/failed.json'
        priorbytes=priorpath.read_bytes();prior=json.loads(priorbytes)
        check(sha(priorbytes)=='c9e734a9744374b52627c40092d6c0b6eac291fdd59d6c551eea5dc4375515b6','Authenticated retained weapon baseline report')
        oldmanifest=json.loads((ROOT/'build/art/generated-weapon/644e53f420909b6a1515e6f852ad33c1fe1607f3/manifest.json').read_text())
        check(prior['romSha1']==oldmanifest['romSha1'] and oldmanifest['baseRomSha1']==meta['baseRomSha1']=='37afe0a7be1b80355d395d3d10685a9034b123d1','Retained baseline exact parent identity')
        check(hashlib.sha1(Path(meta['source']).read_bytes()).hexdigest()==meta['baseRomSha1'],'Retained baseline ROM still exact')
        check(not prior['renderFailures'] and prior['error']=='generated/attack-48 owned held weapon resource/channel','Retained failure affects generated weapon only')
        for label in ('native Fight damages target and returns','transient action roots retired','held axe reaches on-screen hardware OAM'):
            check('baseline '+label in prior['checks'],'Retained completed baseline '+label)
        for name in ('ready','returned'):
            ram=(priorpath.parent/('baseline-'+name+'.ram')).read_bytes()
            check(sha(ram[0x80:0x1e70])==prior['observations']['baseline'][name]['owned'],'Retained '+name+' state authentication')
        observations['baseline']=prior['observations']['baseline'];outcomes['baseline']=prior['outcomes']['baseline']
        checks.extend(c for c in prior['checks'] if c.startswith(('baseline/','baseline ')))
        inputs.extend(v for v in prior['inputs'] if v[0]=='baseline')
        provenance.append(dict(source=str(priorpath),sha256=sha(priorbytes),scope='Completed unchanged baseline only; prior generated checks excluded'))
        cases=cases[1:]
    if isolate:
        classes=json.loads((ROOT/'build/art/generated-classes/current.json').read_text())
        cases=[('release',meta['releaseSource'],release_hash),('classes',classes['path'],classes['romSha1'])]+cases
    if profile_isolation:cases=[(name,meta['releaseSource'],release_hash) for name in ('original-profile','viking-only')]
    for kind,path,digest in cases:
        rom=Path(path).read_bytes();check(hashlib.sha1(rom).hexdigest()==digest,kind+' authenticated candidate')
        if natural_water:
            fixtureout=out/kind;fixtureout.mkdir()
            path,rom,native_map,map_proof=water_fixture(rom,fixtureout)
            provenance.append(map_proof)
        observations[kind]={};previous_actors.clear();previous_weapons.clear();previous_weapon_samples.clear();wrapper_map.clear();pending_anchors.clear();frame_clock=0;e=E(Path(path));e.load(seed)
        # This old world seed predates the two transient action roots now
        # explicitly owned by execution-scope.c/action-snapshot.c. Normalize
        # them as in existing integrated gameplay fixtures, not as canaries.
        e.set_memory(0x3ff44,bytes(8));inputs.append([kind,'clear transient action roots',0x3ff44,8])
        # Default focus is same-race Viking slot3 with its legal axe. Explicit
        # water jobs keep test stats and use no weapon; the Moogle presentation
        # replacement is declared separately below, not a recruitment claim.
        itemtable=struct.unpack_from('<I',rom,0x79aec)[0]-0x08000000
        for slot,job,race,family in profiles:
            if profile_isolation and (kind=='original-profile' or slot!=3):continue
            p=0x80+264*slot
            if live_palette and slot==focus_slot and race==5:
                check(e.memory()[p+4]==1 and e.memory()[p+6]==4,kind+' declared generic Viera slot before isolated Moogle profile')
            else:check(e.memory()[p+6]==race,kind+' existing profile race')
            item=next(i for i in range(1,461) if rom[itemtable+i*32+8]==family) if family else 0
            profile=bytes((1,job,race,job))
            if slot in (0,1):profile=e.memory()[p+4:p+7]+bytes([job])
            e.set_memory(p+4,profile);e.set_memory(p+0x35,bytes([job]));e.set_memory(p+0x2a,struct.pack('<5H',item,0,0,0,0))
            inputs.append([kind,'pre-allocation profile',slot,list(profile),item])
        for x,y,key in route['path']:e.run(1,key)
        e.run(30);tap(256,1200)
        for _ in range(7):tap(256,600)
        for _ in range(3):tap(256)
        for _ in range(3):
            for key in (128,256,256,256):tap(key)
        capture('deployed');tap(8,600);tap(256,600);tap(256,600)
        inputs.append([kind,'ready wait',observe['wait_for_menu'](e)])
        if live_palette or connected:
            def active_unit():
                memory=e.memory();manager=struct.unpack_from('<I',memory,0xf438)[0]-0x02000000
                return struct.unpack_from('<I',memory,manager+24)[0]
            for turn in range(12):
                if active_unit()==0x02000000+focus_unit:break
                previous=active_unit();inputs.append([kind,'Wait preceding actor',previous])
                for key in (32,32,256,256):tap(key)
                for waited in range(0,6300,30):
                    if active_unit()!=previous and observe['menu_visible'](e):break
                    run(30)
                else:raise AssertionError('Native turn did not advance to declared focus')
            check(active_unit()==0x02000000+focus_unit,kind+' declared racial focus unit owns actual turn')
        # Live encounter placement consumes travel RNG; the cached unit
        # coordinates alone do not establish the current wrapper positions.
        # Reuse the repository's declared Giza formation before Move inputs.
        if natural_water:
            positions=water_formation(rom,e,native_map,focus_unit);inputs.append([kind,'original-map dry starting formation',positions]);run(30)
        else:fixed_giza_formation(rom,e);e.run(30);inputs.append([kind,'fixed_giza_formation'])
        wrappers=from_emulator(rom,e);wrapper_map.update(wrappers);r=e.memory()
        if natural_water:
            heights=native_map.heights(WATER_MAP);grid=struct.unpack_from('<I',r,0x7f14)[0]-0x02000000
            check(r[grid:grid+512]==heights,kind+' complete native-loaded original water geometry')
            check(r[0x91a0:0xd1a0]==native_map.planar(WATER_MAP),kind+' complete original native-loaded map arrangement')
            check(r[0xd1a0:0xf1a0]==native_map.clipping(WATER_MAP),kind+' complete original native-loaded clipping')
            start_position=(LAND[0]*32+16,heights[2*(LAND[1]*16+LAND[0])]*16,LAND[1]*32+16)
            check(struct.unpack_from('<3H',r,wrappers[focus_unit]+8)==start_position,kind+' declared dry-bank start')
        else:
            check(struct.unpack_from('<3H',r,wrappers[0x398]+8)==(48,16,464),kind+' declared actor at1,14')
            check(struct.unpack_from('<3H',r,wrappers[0x33e4]+8)==(176,32,464),kind+' declared target at5,14')
        initial=capture('ready');e.set_memory(0x33e4+0x18,struct.pack('<HH',250,250))
        if natural_water:
            tile=grid+2*(WATER[1]*16+WATER[0]);height,flags=initial[tile:tile+2]
            check(height>0 and flags&2 and not flags&9,kind+' unmodified natural water destination')
            e.save(out/(kind+'-water-ready.state'))
        elif water:
            # Controlled terrain fixture: change only one tile's water flag.
            # Native movement computes submerged height and chooses the body;
            # neither wrapper appearance nor live actor records are edited.
            grid=struct.unpack_from('<I',initial,0x7f14)[0]-0x02000000;width=initial[0x7f18]
            tile=grid+2*(14*width+4);height,flags=initial[tile:tile+2]
            check(width==16 and height>0 and not flags&11,kind+' legal dry destination')
            e.save(out/(kind+'-water-ready.state'))
            e.set_memory(tile+1,bytes([flags|2]));inputs.append([kind,'terrain water bit',tile+1,flags,flags|2])
        for key in ((256,128) if natural_water else (256,128,128,128)):tap(key)
        tap(256,600,'move');capture('moved')
        if water:
            r=capture('water');w=wrappers[focus_unit]
            expected_water=(WATER[0]*32+16,(height-1)*16,WATER[1]*32+16) if natural_water else (144,(height-1)*16,464)
            check(struct.unpack_from('<3H',r,w+8)==expected_water,kind+' native submerged destination height')
            check(struct.unpack_from('<H',r,w+0x34)[0]==land_resource+1,kind+' native wrapper selects declared water resource')
            body=struct.unpack_from('<I',r,w+0x44)[0]-0x02000000
            check(any(a['address']==body and a['resource']==land_resource+1 and a['displayedFrames'] for a in observations[kind]['water']['actors']),kind+' water body actually uploaded')
            tap(1,600,'cancel-move');r=capture('land-return')
            check(struct.unpack_from('<3H',r,w+8)==(start_position if natural_water else (48,16,464)),kind+' native cancel returns original land position')
            check(struct.unpack_from('<H',r,w+0x34)[0]==land_resource,kind+' native wrapper restores declared land resource')
            check(r[0x1940:0x1ebc]==initial[0x1940:0x1ebc],kind+' water preserves inventory AP preferences status')
            check(r[0x3ff44:0x3ff4c]==bytes(8),kind+' water leaves transient roots retired')
            if natural_water:check(r[grid:grid+512]==heights,kind+' full natural terrain unchanged after water/cancel')
            outcomes[kind]=dict(position=list(struct.unpack_from('<3H',r,w+8)),resource=struct.unpack_from('<H',r,w+0x34)[0],owned=sha(r[0x80:0x1e70]))
            e.close();e=None;continue
        for stage,key in enumerate((256,256,128,256,256)):
            tap(key);capture('action-stage'+str(stage))
        if isolate:
            r=e.memory();manager=struct.unpack_from('<I',r,0xf438)[0]-0x02000000
            outcomes[kind]=dict(romSha1=digest,mode=r[manager+4],substate=struct.unpack_from('<I',r,manager)[0],
                entryAdvanced=r[manager+4]==11)
            e.save(out/(kind+'-entry.state'));(out/(kind+'-entry.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
            e.close();e=None;continue
        C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',2),4);inputs.append([kind,'native RNG seed',2])
        tap(256,600,'attack');run(1800);capture('fight');tap(256,600)
        inputs.append([kind,'following menu wait',observe['wait_for_menu'](e,limit=6300)])
        final=capture('returned');damage=250-struct.unpack_from('<H',final,0x33e4+0x18)[0]
        check(damage>0,kind+' native Fight damages target and returns')
        check(final[0x1940:0x1ebc]==initial[0x1940:0x1ebc],kind+' inventory/AP/preferences/status storage unchanged')
        check(final[0x3ff44:0x3ff4c]==bytes(8),kind+' transient action roots retired')
        outcomes[kind]=dict(damage=damage,hp=struct.unpack_from('<H',final,0x398+0x18)[0],mp=struct.unpack_from('<H',final,0x398+0x1c)[0])
        seen={a['mode'] for v in observations[kind].values() for a in v['actors'] if a['resource']==260}
        check(any(4<=mode<8 for mode in seen),kind+' Viking walk sequence actually observed')
        check(any(80<=mode<168 for mode in seen),kind+' Viking weapon action actually observed')
        if weapon:
            held=[a for v in observations[kind].values() for a in v.get('heldWeapons',[]) if a['hardwareObjects']]
            check(bool(held),kind+' held axe reaches on-screen hardware OAM')
            if kind=='generated':check(all(a['resource']==meta['resource'] for a in held),'Generated axes use private276 rather than native heavy blade128')
        e.close();e=None
    if isolate:
        check(all(v['entryAdvanced'] for v in outcomes.values()),'Every build stage reaches actual final confirmation mode11')
        hashes=sorted({v['romSha1'] for v in outcomes.values()})
        report=dict(status='passed',romSha1=hashes[0] if len(hashes)==1 else None,testedRomSha1s=hashes,
            checks=checks,inputs=inputs,observations=observations,outcomes=outcomes,
            fixtureSha256=sha(seedbytes),scope='Bounded Fight confirmation diagnostic only; each outcome names its actual ROM. No complete attack or return acceptance.')
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))));sys.exit(0)
    check(outcomes['baseline']==outcomes['generated'],'Exact water/cancel outcome preservation' if water else 'Exact Move/Fight outcome preservation')
    old=observations['baseline']['ready'];new=observations['generated']['ready']
    check({a['resource'] for a in new['actors']} >= {256+2*owner for owner in allowed_owners},'All four declared generic actors deployed; story identities preserved')
    check(old['owned']==new['owned'],'Deployment preserves owned gameplay state')
    check(seed.read_bytes()==seedbytes,'Source world checkpoint unchanged')
    check(not render_failures,'All sampled unit-body graphics verified; auxiliary effects remain separate')
    report=dict(status='passed',romSha1=meta['romSha1'],baseRomSha1=meta['baseRomSha1'],checks=checks,inputs=inputs,observations=observations,outcomes=outcomes,
        fixtureSha256=sha(seedbytes),routeSha256=sha(routepath.read_bytes()),scope='Paired native deployment of four generic classes plus required Marche/Montblanc identities, declared canonical Giza formation, Viking Move/Fight unit-body frame sampling and following-turn return, bounded graphics and exact outcomes. Auxiliary effect actors are recorded but not accepted by the body oracle. No real water transition, other command families, custom palette or production-art acceptance.')
    if water:report['scope']='Paired native Viking Move into a declared single-tile water-flag fixture, submerged height, water-body rendering and cancel back to land. Four generic bodies sampled. Background remains Giza; no natural water-map, all-class water, attack, auxiliary graphics, custom-palette or production-art acceptance.'
    if natural_water:report['scope']='Paired original map92 graphics/geometry through the existing map70 encounter shell, intact native-loaded arrangement/clipping/heights, native Viking Move into unchanged natural water and cancel to land. Generated body uploads and exact outcomes. Not original map92 campaign encounter, all-class/action/custom-palette or final-art acceptance.'
    if live_palette:
        report['waterJob']=water_job;report['declaredProfiles']=profiles
        report['scope']='Paired native Move from land into intact map92 water and cancel back for the declared waterJob, all ten custom palettes enabled and four generic racial profiles. Explicit waterJob profiles are unarmed; Moogle replaces generic slot5 presentation identity while retaining its test stats. Story appearance identities remain intact. Exact generated colors, authenticated OAM owners, allocation/refusal counters, native body upload and gameplay outcomes. No other-class water/action coverage, original map92 campaign encounter, natural recruitment, native hardware phase or response-timing acceptance, maximum heap stress or final art.'
    report['provenance']=provenance
    if weapon:report['scope']='Paired actual Viking Move/Fight/next-turn with independent held weapon276 versus original128, exact attachment-owned sequence/tile/OAM/palette evidence and unchanged gameplay outcomes. Temporary generated pose through preserved motion; no final weapon art, all weapon families, other effects or campaign acceptance.'
    if connected:report['scope']='Fresh connected-ROM Viking Move/Fight/return with four generic racial classes, actual custom body palettes, independent held axe276 versus original128, both attachment-owned channels and native timing/command metadata. Every-frame observations during declared input/animation intervals; exact damage/outcomes, persistent storage and roots. No response-timing, all weapon/action families, final art or campaign acceptance.'
    if connected and 'nativePaletteTransport' in assembled['components']:
        report['scope']=report['scope'].replace('actual custom body palettes','exact native party/opposing baseline/dim body palettes')
        report['nativePaletteTransport']=True
        report['inheritedWeaponStageParentSha1']=report['baseRomSha1']
        report['baseRomSha1']=cases[0][2]
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    if e:
        e.save(out/(kind+'-failed.state'));e.screenshot(out/(kind+'-failed.png'))
        for ext,base_address in [('ram',0x02000000),('iwram',0x03000000),('vram',0x06000000),('palette',0x05000000),('oam',0x07000000)]:
            (out/(kind+'-failed.'+ext)).write_bytes(C.string_at(*e.maps[base_address]))
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),checks=checks,inputs=inputs,observations=observations,outcomes=outcomes,renderFailures=render_failures),indent=2)+'\n');print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
