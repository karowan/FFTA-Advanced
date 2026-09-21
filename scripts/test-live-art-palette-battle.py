"""Paired live class palette coexistence, bounded entry and real Move/cancel.

Reuses the accepted isolated world fixture and established deterministic inputs.
No player saves, launcher selection or running game are modified.
"""
import argparse,ctypes as C,datetime,hashlib,json,runpy,struct
from pathlib import Path
from PIL import Image
from native_art import ROOT,sha
from native_battle_wrappers import fixed_giza_formation,from_emulator
from actor_render_evidence import actors
from native_body_display import pending_from_anchor,retained,layout_reset_display

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--current',type=Path,default=ROOT/'build/art/live-palette/poc.json')
parser.add_argument('--entry-only',action='store_true')
parser.add_argument('--ready-only',action='store_true')
parser.add_argument('--press-frames',type=int,choices=(8,16),default=16)
parser.add_argument('--require-variants',action='store_true')
parser.add_argument('--status-control',action='store_true',help='Give the private parent only the verified status shortcut for matched engine-cost comparison.')
parser.add_argument('--mixed-class-group',choices=('first','second','moogle-chemist','moogle-bard'))
parser.add_argument('--trace-unit-writes',action='store_true')
parser.add_argument('--trace-workspace-request',action='store_true')
parser.add_argument('--trace-palette-target',action='store_true')
parser.add_argument('--idle-art',action='store_true',help='Record a full96-frame idle cycle and require three distinct focus poses')
parser.add_argument('--entry-checkpoint',type=int,choices=range(26),help='Retain an exact declared route boundary for focused read-only diagnosis; does not change inputs or acceptance.')
args=parser.parse_args()
assert not args.trace_workspace_request or args.trace_unit_writes
assert not args.trace_palette_target or (args.mixed_class_group and not args.trace_unit_writes)
assert not args.trace_unit_writes or args.mixed_class_group
assert not args.mixed_class_group or (args.ready_only and not args.require_variants), 'Mixed class proof is a bounded ready-state check'
assert not args.idle_art or (args.ready_only and args.mixed_class_group)
meta=json.loads(args.current.read_text())
fixture_source=Path(meta.get('fixtureSource',meta['releaseSource']))
fixture=fixture_source.parent/'fixture';seed=fixture/'accepted-world.state';seedbytes=seed.read_bytes()
routepath=fixture/'route.json';route=json.loads(routepath.read_text());proof=json.loads((fixture/'report.json').read_text())
assert proof['passed'] and proof['romSha1']==route['romSha1']==hashlib.sha1(fixture_source.read_bytes()).hexdigest()
assert (fixture/'frozen.gba').read_bytes()==fixture_source.read_bytes()
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];menu=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
out=ROOT/'build/art/live-palette/battle'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
write_trace=None
if args.trace_unit_writes:
    from art_unit_write_trace import build as trace_build
    meta,write_trace=trace_build(meta,out,args.trace_workspace_request)
if args.trace_palette_target:
    assert meta['traceTarget']
    write_trace=dict(log=meta['ramReservation'][0]+meta['transientStateBytes'],logBytes=40,type='first-table-target-refusal')
control_path=Path(meta['source']);control_sha1=meta['baseRomSha1'];control_proof=None
if args.status_control:
    original=control_path.read_bytes();candidate=Path(meta['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==control_sha1 and hashlib.sha1(candidate).hexdigest()==meta['romSha1']
    start=meta['symbols']['ffta_art_status_next_entry']-0x08000000
    # Copy the exact leaf in place. Both literal targets are unchanged native
    # addresses; the control gains no palette hook, asset or RAM reservation.
    leaf=candidate[start:start+32]
    assert leaf.hex()=='a37801331b061b16182b03dca37008bc01480047014b184763dd09081d631e09'
    assert original[start:start+32]==b'\xff'*32 and original[0x9dd58:0x9dd5c]==struct.pack('<I',0x091e631d)
    control=bytearray(original);control[start:start+32]=leaf;control[0x9dd58:0x9dd5c]=struct.pack('<I',start+0x08000001)
    assert all(a==b or start<=i<start+32 or 0x9dd58<=i<0x9dd5c for i,(a,b) in enumerate(zip(original,control)))
    control_path=out/'status-only-control.gba';control_path.write_bytes(control);control_sha1=hashlib.sha1(control).hexdigest()
    control_proof=dict(path=str(control_path),romSha1=control_sha1,sourceSha1=meta['baseRomSha1'],offset=start,bytes=32,sha256=sha(leaf),scope='Only identical verified status iterator shortcut; no live-palette hooks or generated-color changes.')
checks=[];inputs=[];observations={};outcomes={};e=None;case='setup';clock=0;anchors={};previous={};wrappers={}
BASE=meta['ramReservation'][0]-0x02000000
LIMIT=meta['ramReservation'][1]-0x02000000
STATE=meta['transientStateBytes']
SLOTS=meta.get('historySlots',10)
TAG=meta.get('tagOffset',2608)
COUNTERS=meta.get('bindingCounterOffset',2840)
mixed_profiles={};moogle_profile=args.mixed_class_group in ('moogle-chemist','moogle-bard')
focus_job=116 if moogle_profile else 117
focus_resource=256+2*(focus_job-116)
if args.mixed_class_group:
    assert meta.get('allClasses') and SLOTS==20
    class_path=Path(meta['classManifest']);class_raw=class_path.read_bytes()
    assert sha(class_raw)==meta['classManifestSha256']
    class_races={j['job']:j['race'] for j in json.loads(class_raw)['classResources']['jobs']}
    group_jobs={'first':(117,118,120,124),'second':(117,119,121,125),
        'moogle-chemist':(116,118,120,122),'moogle-bard':(116,119,121,123)}
    mixed_profiles={slot:(job,class_races[job]) for slot,job in zip((2,3,4,5),group_jobs[args.mixed_class_group])}
colors=(ROOT/'build/art/imagegen/human-dark-knight/march-v2-own-palette/palette.bin').read_bytes()
assert sha(colors)==meta['paletteSha256']
entry={};entry_phase=True;action_steps={}
traces={};entry_traces={};fence=bytes([0xa7])*(LIMIT-BASE-STATE)

def palette_sample(name):
    ram=e.memory();iw=C.string_at(*e.maps[0x03000000]);pal=C.string_at(*e.maps[0x05000000]);oam=C.string_at(*e.maps[0x07000000])
    row=dict(frame=clock,palette=pal.hex(),nativeShadow=iw[0x3860:0x3c60].hex(),units=sha(ram[0x80:0x1e70]))
    if case=='candidate':
        active,applied,restored,failed=struct.unpack_from('<4I',ram,BASE+0xa0c)
        start,end=struct.unpack_from('<2H',ram,BASE+0xa1c)
        display,flags=struct.unpack_from('<2H',ram,BASE+meta.get('displayOffset',2736))
        starts,completions,unsupported=struct.unpack_from('<3I',ram,BASE+meta['bindingOffset']+COUNTERS)
        row['live']=dict(active=active,applied=applied,restored=restored,failed=failed,start=start,end=end,display=display,flags=flags,starts=starts,completions=completions,unsupported=unsupported,composePhase=struct.unpack_from('<I',ram,BASE+meta.get('composePhaseOffset',5604))[0],emitted=list(struct.unpack_from('<2I',ram,BASE+meta.get('emittedOffset',5596))))
        keys=ram[BASE+meta['variantOffset']:BASE+meta['variantOffset']+SLOTS]
        slot=keys.index(16) if 16 in keys else None
        row['normalBindingSlot']=slot
        binding=BASE+meta['bindingOffset']+SLOTS*252+(slot or 0)*32
        visible=BASE+meta.get('visibleColorsOffset',meta['bindingOffset']+SLOTS*252)+(slot or 0)*32
        row['bindingColors']=ram[binding:binding+32].hex() if slot is not None else None
        row['visibleColors']=ram[visible:visible+32].hex() if slot is not None else None
        row['tags']=ram[BASE+TAG:BASE+TAG+128].hex()
        row['oam']=oam.hex()
        row['nativeBackup']=ram[BASE+2060:BASE+2572].hex()
        row['fenceIntact']=ram[BASE+STATE:LIMIT]==fence
        if 'refusalOffset' in meta:
            row['refusals']=dict(zip(('variants','setup','target','tick'),struct.unpack_from('<4I',ram,BASE+meta['refusalOffset'])))
        if 'variantOffset' in meta:
            row['variantMapping']=ram[BASE+meta['variantOffset']:BASE+meta['variantOffset']+SLOTS*2].hex()
            row['allVisibleColors']=ram[BASE+meta['visibleColorsOffset']:BASE+meta['visibleColorsOffset']+SLOTS*32].hex()
    traces[case][name]=row

def check(ok,label):
    assert ok,case+'/'+label
    checks.append(case+'/'+label)
def active():
    r=e.memory();return struct.unpack_from('<I',r,struct.unpack_from('<I',r,0xf438)[0]-0x02000000+24)[0]
def step(frames,key=0):
    global clock
    if not (args.trace_unit_writes or args.trace_palette_target):
        e.run(frames,key);clock+=frames
    else:
        for _ in range(frames):
            previous=None
            if case=='candidate' and not entry_phase:
                previous=C.create_string_buffer(e.core.retro_serialize_size())
                assert e.core.retro_serialize(previous,len(previous))
                previous_memory=e.memory();previous_iw=C.string_at(*e.maps[0x03000000])
            e.run(1,key);clock+=1
            ram=e.memory();log=write_trace['log']-0x02000000
            trap=struct.unpack_from('<I',ram,log+4)[0] if case=='candidate' else 0
            null_free=trap==1
            if ram[0x80:0x84]==bytes(4) or trap:
                size=e.core.retro_serialize_size();cpu=C.create_string_buffer(size);assert e.core.retro_serialize(cpu,size)
                record=dict(case=case,frame=clock,romSha1=digest,cpu=list(struct.unpack_from('<16I',cpu,0x20)),
                    trace=write_trace,nullFree=null_free,allocationFailed=trap==2,workspaceRequest=trap==3,ring=ram[log:log+write_trace['logBytes']].hex())
                if previous is not None:
                    (out/'last-intact.state').write_bytes(previous.raw)
                    (out/'last-intact.ram').write_bytes(previous_memory)
                    (out/'last-intact.iwram').write_bytes(previous_iw)
                    record.update(previousStateSha256=sha(previous.raw),previousCpu=list(struct.unpack_from('<16I',previous,0x20)))
                (out/('palette-target.json' if trap==4 else 'workspace-request.json' if trap==3 else 'allocation-failed.json' if trap==2 else 'null-free.json' if null_free else 'first-erased-unit.json')).write_text(json.dumps(record,indent=2)+'\n')
                raise AssertionError('Palette target captured' if trap==4 else 'Workspace request captured' if trap==3 else 'Native allocation failed' if trap==2 else 'Native null free observed' if null_free else 'Canonical player identity erased; exact first-frame evidence retained')
def tap(key,wait=180):
    inputs.append([case,args.press_frames,key,wait]);step(args.press_frames,key);step(wait)
    if entry_phase:
        if len(entry[case])==2:
            # Wait for the last line of the actual first dialogue, not a guessed
            # additional A press. The immutable parent capture supplies pixels.
            reference=ROOT/'build/art/live-palette/battle/20260918T043030.693824Z/parent-entry-2.png'
            assert sha(reference.read_bytes())=='3d6447c179ea198dad3a02361ab02be34124d81fae1988b86668b76de7186dc7'
            target=Image.open(reference).resize((240,160),Image.Resampling.NEAREST).crop((72,12,191,54)).tobytes()
            def text_ready():
                raw,w,h,pitch,pixel=e.frame
                assert pixel in (0,1,2) and (w,h)==(240,160),'Dialogue video format'
                if pixel==1:
                    region=Image.frombytes('RGB',(w,h),raw,'raw','BGRX',pitch).crop((72,12,191,54)).tobytes()
                else:
                    rgb=bytearray()
                    for y in range(12,54):
                        for x in range(72,191):
                            v=int.from_bytes(raw[y*pitch+x*2:y*pitch+x*2+2],'little')
                            if pixel==2:r,g,b=(v>>11)&31,(v>>5)&63,v&31;g=g*255//63
                            else:r,g,b=(v>>10)&31,(v>>5)&31,v&31;g=g*255//31
                            rgb.extend((r*255//31,g,b*255//31))
                    region=bytes(rgb)
                return region==target
            waited=0
            while not text_ready() and waited<180:step(1);waited+=1
            check(text_ready(),'First native dialogue completely revealed within 180 additional frames')
            inputs.append([case,'observe exact original first-dialogue text',waited])
        label='entry-'+str(len(entry[case]))
        palette_sample(label)
        if args.entry_checkpoint==len(entry[case]):
            e.save(out/(case+'-'+label+'.state'))
            for ext,address in (('ram',0x02000000),('iwram',0x03000000)):
                (out/(case+'-'+label+'.'+ext)).write_bytes(C.string_at(*e.maps[address]))
        entry[case].append(dict(label=label,frame=clock,key=key,units=sha(e.memory()[0x80:0x1e70])))
        if args.require_variants and label=='entry-10':
            e.screenshot(out/(case+'-'+label+'-variants.png'))
            inputs.append([case,'consecutive deployment variant observations',64,0])
            for tick in range(64):step(1);palette_sample(label+'-steady-'+str(tick))
        if args.entry_only:
            e.screenshot(out/(case+'-'+label+'.png'))
            (out/(case+'-'+label+'.ram')).write_bytes(e.memory())
            (out/(case+'-'+label+'.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
    elif args.ready_only:
        index=action_steps.get(case,0);action_steps[case]=index+1
        e.screenshot(out/(case+'-turn-input-'+str(index)+'.png'))
        (out/(case+'-turn-input-'+str(index)+'.ram')).write_bytes(e.memory())
def capture(name):
    palette_sample(name)
    ram=e.memory();vram=C.string_at(*e.maps[0x06000000]);allactors=actors(rom,ram,vram)
    body=struct.unpack_from('<I',ram,wrappers[0x290]+0x44)[0]-0x02000000
    anchor=anchors.get(body);hardware=C.string_at(*e.maps[0x07000000])
    if case=='candidate':
        # Layout continuity compares original OAM geometry. Canonicalize only
        # a currently authenticated remapped owner; the full actual colors/OAM
        # are independently retained and checked by palette_sample.
        hardware=bytearray(hardware);live=traces[case][name]['live']
        for index in range(128):
            attr2=struct.unpack_from('<H',hardware,index*8+4)[0]
            slot=ram[BASE+TAG+index]
            if live['active']&(1<<(attr2>>12)) and slot<SLOTS:
                key=ram[BASE+meta['variantOffset']+slot]
                check((key>>4<10 if args.mixed_class_group else key>>4==1),name+' authenticated custom source class')
                nativebank=struct.unpack_from('<I',ram,BASE+meta['bindingOffset']+252*slot+248)[0]
                check(nativebank<16,name+' authenticated native bank for geometry comparison')
                struct.pack_into('<H',hardware,index*8+4,(attr2&4095)|(nativebank<<12))
    a=next((a for a in allactors if a['address']==body),None)
    if a is None:
        a=layout_reset_display(rom,ram,vram,hardware,body,anchor,clock-anchor['frame']) if anchor else None
    check(a is not None,name+' configured or strictly bounded native layout reset')
    a['tileOffset']=struct.unpack_from('<I',ram,body+0x20)[0]
    p=0x10000+a['tile']*32;block=vram[p:p+a['allocation']*32]
    direct=bool(a['displayedFrames']) and a['declaredSequence']
    hold=pending_from_anchor(a,block,anchor,clock-anchor['frame']) if anchor else None
    if not hold:hold=retained(a,block,previous.get(body))
    if not hold and a.get('configured') is False:hold=a['displayProof']
    row=dict(direct=direct,identity=(a['resource'],a['tile'],a['allocation']),block=block,first=a['first'],index=a['index'])
    if direct:
        objects=[struct.unpack_from('<3H',hardware,i*8) for i in range(128)]
        anchors[body]=dict(row,frame=clock,actor=a,hardware=[v for v in objects if v[0]&0x300!=0x200 and v[2]&1023==a['tile']])
    elif not hold:anchors.pop(body,None)
    previous[body]=row
    position=list(struct.unpack_from('<3H',ram,wrappers[0x290]+8))
    observations[case][name]=dict(actor=a,position=position,displayProof='current' if direct else hold,frame=clock,blockSha256=sha(block),owned=sha(ram[0x80:0x1e70]))
    check(a['resource']==focus_resource and a['declaredSequence'] and bool(direct or hold),name+' exact owned native body upload')
    check(a['expectedTiles']==a['tileCount']<=a['allocation'],name+' bounded native OAM')
    if name in ('ready','moved','returned') or 48<position[0]<144:
        if name in ('ready','moved','returned') or not any(v['actor']['mode']==a['mode'] and v['actor']['displayedFrames']==a['displayedFrames'] for k,v in observations[case].items() if k!=name):
            e.screenshot(out/(case+'-'+name+'.png'))
            for ext,data in (('ram',ram),('vram',vram),('palette',C.string_at(*e.maps[0x05000000])),('oam',C.string_at(*e.maps[0x07000000]))):(out/(case+'-'+name+'.'+ext)).write_bytes(data)
    return ram
def animated_tap(key,label):
    inputs.append([case,'sampled input',key,args.press_frames,600,1]);step(args.press_frames,key);capture(label+'-press')
    for tick in range(600):step(1);capture(label+'-'+str(tick))
try:
    for case,path,digest in (('parent',control_path,control_sha1),('candidate',meta['path'],meta['romSha1'])):
        rom=Path(path).read_bytes();check(hashlib.sha1(rom).hexdigest()==digest,'Authenticated ROM')
        e=E(Path(path));e.load(seed);e.set_memory(0x3ff44,bytes(8));clock=0;anchors.clear();previous.clear();observations[case]={};traces[case]={};entry[case]=[];entry_phase=True
        if write_trace and case=='candidate':e.set_memory(write_trace['log']-0x02000000,bytes(write_trace['logBytes']))
        check(e.memory()[0x296]==1,'Existing recruited human slot2')
        story_profile=e.memory()[0x188:0x188+264]
        e.set_memory(0x294,bytes([1,focus_job,1,focus_job]));e.set_memory(0x2c5,bytes([focus_job]));inputs.append([case,'preallocation human focus profile',2,[1,focus_job,1,focus_job]])
        if args.mixed_class_group:
            for slot,(job,race) in mixed_profiles.items():
                unit=0x80+slot*264
                if moogle_profile and slot==5:
                    check(e.memory()[unit+4]==1 and e.memory()[unit+6]==4,'Declared generic Viera slot before isolated Moogle presentation profile')
                else:check(e.memory()[unit+6]==race,'Mixed profile uses existing same-race member '+str(slot))
                e.set_memory(unit+4,bytes([1,job,race,job]));e.set_memory(unit+0x35,bytes([job]))
                inputs.append([case,'preallocation mixed class profile',slot,job,race])
            check(e.memory()[0x188:0x188+264]==story_profile,'Montblanc story record unchanged by declared profiles')
        items=struct.unpack_from('<I',rom,0x79aec)[0]-0x08000000
        katana=next(i for i in range(1,461) if rom[items+32*i+8]==2)
        e.set_memory(0x2ba,struct.pack('<5H',katana,0,0,0,0));inputs.append([case,'preallocation ordinary sword-only loadout',katana])
        for x,y,key in route['path']:step(1,key)
        step(30);tap(256,1200)
        for _ in range(7):tap(256,600)
        for _ in range(3):tap(256)
        for _ in range(3):
            for key in (128,256,256,256):tap(key)
        tap(8,600);tap(256,600);tap(256,600)
        entry_phase=False
        if args.entry_only:
            waited=menu['wait_for_menu'](e);clock+=waited
            inputs.append([case,'bounded native battle-menu observation',waited])
            outcomes[case]=dict(menuVisible=bool(menu['menu_visible'](e)),units=sha(e.memory()[0x80:0x1e70]))
            e.close();e=None;continue
        # Entry sampling diagnoses route differences; movement is compared separately.
        entry_traces[case]=traces[case].copy()
        traces[case].clear()
        waited=menu['wait_for_menu'](e);clock+=waited
        inputs.append([case,'bounded native battle-menu observation',waited])
        for turn in range(12):
            if active()==0x02000290:break
            old=active();inputs.append([case,'Wait preceding actor',old])
            for key in (32,32,256,256):tap(key)
            for waited in range(0,6300,30):
                if active()!=old and menu['menu_visible'](e):break
                step(30)
            else:raise AssertionError('Native turn did not advance')
        check(active()==0x02000290,'Actual recruited focus unit turn')
        if args.mixed_class_group:
            step(30);wrappers=from_emulator(rom,e)
            check({0x80+slot*264 for slot in mixed_profiles}<=set(wrappers),'All four declared racial profiles actually deployed')
            for slot,(job,race) in mixed_profiles.items():
                unit=0x80+slot*264
                check(e.memory()[unit+4:unit+8]==bytes([1,job,race,job]),'Deployed profile matches authoritative racial class '+str(job))
            inputs.append([case,'unchanged native mixed-party formation',sorted(wrappers)])
        else:
            fixed_giza_formation(rom,e);step(30);wrappers=from_emulator(rom,e);inputs.append([case,'canonical Giza start'])
        if case=='candidate':
            check(all(w+0x90<=BASE for w in wrappers.values()),'All twelve native wrappers below reserved palette storage')
            e.set_memory(BASE+STATE,fence);inputs.append([case,'owned unused reservation fence',BASE+STATE,LIMIT,'a7'])
        initial=capture('ready');w=wrappers[0x290]
        (out/(case+'-ready.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
        e.save(out/(case+'-ready.state'))
        if args.ready_only:
            for tick in range(96 if args.idle_art else 20):
                step(1)
                if args.idle_art and tick%4==0:capture('idle-'+str(tick))
                else:palette_sample('idle-'+str(tick))
            if args.idle_art and case=='candidate':
                check(len({v['blockSha256'] for v in observations[case].values()})>=3,'Three distinct generated focus poses displayed during full idle cycle')
            e.close();e=None;continue
        check(struct.unpack_from('<3H',initial,w+8)==(48,32,432),'Declared start1,13')
        for key in (256,128,128,128):tap(key)
        animated_tap(256,'move');moved=capture('moved')
        check(struct.unpack_from('<3H',moved,w+8)==(144,32,432),'Native three-cell Move to4,13')
        animated_tap(1,'cancel');final=capture('returned')
        check(struct.unpack_from('<3H',final,w+8)==(48,32,432),'Native cancel restores position')
        check(final[0x1940:0x1ebc]==initial[0x1940:0x1ebc] and final[0x3ff44:0x3ff4c]==bytes(8),'No inventory/status mutation or retained action root')
        walking=[v for v in observations[case].values() if 48<v['position'][0]<144 and v['actor']['displayedFrames']]
        check(bool(walking),'Actual interpolated walking positions with verified frames observed')
        if case=='candidate':
            check(len({v['blockSha256'] for v in walking})>=2,'Distinct generated walk poses uploaded')
            ready=traces[case]['ready']
            check(ready['live']['active']!=0,'Real battle actor receives an allocated custom bank')
            check(ready['bindingColors']==colors.hex(),'Unfaded battle binding uses generated baseline')
        outcomes[case]=dict(position=list(struct.unpack_from('<3H',final,w+8)),owned=sha(final[0x80:0x1e70]),active=active())
        e.close();e=None
    if args.entry_only or args.ready_only:
        if args.require_variants:
            rows=entry_traces.get('candidate',traces['candidate'])
            simultaneous=0
            for label,row in rows.items():
                mapping=bytes.fromhex(row['variantMapping']);tags=bytes.fromhex(row['tags']);oam=bytes.fromhex(row['oam'])
                palette=bytes.fromhex(row['palette']);visible=bytes.fromhex(row['allVisibleColors'])
                check(row['refusals']['variants']==0,label+' no simultaneous-variant refusal')
                check(sum(row['refusals'].values())==row['live']['unsupported'],label+' refusal diagnostics reconcile with total')
                keys={mapping[slot] for slot in set(tags) if slot<10}
                if {16,25}<=keys:
                    simultaneous+=1
                    check(bool(row['live']['active']),label+' normal and dim overlay active together')
                    check(row['live']['failed']==0 and 160<=row['live']['start']<=row['live']['end']<228 and 160<=row['live']['display']<228,label+' variant allocation and display timing remain valid')
                    for index,slot in enumerate(tags):
                        if slot>=10:continue
                        key=mapping[slot];factor=mapping[10+slot];bank=struct.unpack_from('<H',oam,index*8+4)[0]>>12
                        check(key in (16,25) and factor==(32 if key==16 else 19),label+' exact normal/dim source identity')
                        expected=struct.pack('<16H',*[sum((((v>>s)&31)*factor//32)<<s for s in (0,5,10)) for v in struct.unpack('<16H',colors)])
                        check(visible[slot*32:slot*32+32]==expected and palette[512+bank*32:544+bank*32]==expected,label+' exact native-multiplier generated variant reaches hardware')
            check(simultaneous>=65,'Actual deployment displayed both normal and dim generated copies across65 consecutive observations')
        if args.mixed_class_group:
            wanted={job-116 for job,race in mixed_profiles.values()}
            candidate_rom=Path(meta['path']).read_bytes()
            p=meta['symbols']['ffta_art_custom_colors']-0x08000000
            all_colors=struct.unpack_from('<160H',candidate_rom,p)
            for label,row in traces['candidate'].items():
                mapping=bytes.fromhex(row['variantMapping']);tags=bytes.fromhex(row['tags'])
                oam=bytes.fromhex(row['oam']);palette=bytes.fromhex(row['palette'])
                visible=bytes.fromhex(row['allVisibleColors'])
                parent_row=traces['parent'][label];native=bytes.fromhex(parent_row['palette'])
                live=row['live'];seen=set();banks=set()
                check(live['failed']==0 and live['unsupported']==0 and not any(row['refusals'].values()),label+' no mixed-class allocation or effect refusal')
                check(row['fenceIntact'],label+' enlarged reservation fence intact')
                check(160<=live['start']<=live['end']<228 and (live['flags']&128 or 160<=live['display']<228),label+' mixed palette and display work inside VBlank')
                check(row['units']==traces['parent'][label]['units'],label+' paired canonical unit bytes preserved')
                check(row['nativeShadow']==parent_row['nativeShadow'],label+' paired native palette shadow preserved')
                check(palette[:512]==native[:512],label+' every background palette color preserved')
                for index,slot in enumerate(tags):
                    if slot>=SLOTS:continue
                    a,b,c=struct.unpack_from('<3H',oam,index*8)
                    if a&0x300==0x200:continue
                    owner=mapping[slot]>>4;factor=mapping[SLOTS+slot];bank=c>>12
                    check(owner in wanted and factor in (19,32),label+' exact mixed class and brightness identity')
                    expected=struct.pack('<16H',*[sum((((v>>shift)&31)*factor//32)<<shift for shift in (0,5,10)) for v in all_colors[owner*16:owner*16+16]])
                    check(visible[slot*32:slot*32+32]==palette[512+bank*32:544+bank*32]==expected,label+' mixed generated colors reach exact hardware bank')
                    seen.add(owner);banks.add(bank)
                check(seen==wanted and len(banks)>=len(wanted),label+' all four generated classes coexist')
                check(live['active']==sum(1<<bank for bank in banks),label+' active bank mask matches authenticated owners')
                for bank in set(range(16))-banks:
                    check(palette[512+bank*32:544+bank*32]==native[512+bank*32:544+bank*32],label+' unowned hardware bank matches native control '+str(bank))
            check(seed.read_bytes()==seedbytes,'World fixture unchanged')
        report=dict(status='observed',romSha1=meta['romSha1'],baseRomSha1=meta['baseRomSha1'],inputs=inputs,outcomes=outcomes,entry=entry,entryPaletteTraces=entry_traces,paletteTraces=traces,scope='Battle-entry diagnosis only; observations are not gameplay acceptance.')
        if args.require_variants:
            report.update(status='passed',checks=checks,scope='Actual normal/dim deployment variants coexist with exact generated hardware colors and no variant refusal. Does not accept complete battle timing, phase equality, other variants/color modes or final artwork.')
        if args.mixed_class_group:
            report.update(status='passed',checks=checks,mixedProfiles=mixed_profiles,classManifestSha256=meta['classManifestSha256'],
                profileScope='Isolated generic slot5 Moogle presentation profile; prior Viera stats retained, no natural recruitment/class switch claim. Montblanc story record preserved.' if moogle_profile else 'Existing same-race generic members, authoritative class/race assignments.',
                scope='Actual four-class battle coexistence across the recorded ready/idle observations, exact generated hardware colors and unowned OBJ restoration, canonical unit isolation, VBlank bounds and reservation fence. Fresh native deployment route with declared racial profiles. No all-ten simultaneous deployment, movement/phase acceptance, maximum heap stress, natural recruitment/effect lifetime or final art.')
        (out/'observed.json').write_text(json.dumps(report,indent=2)+'\n')
        if args.ready_only:
            # Saved actors contain absolute ROM animation pointers: timing
            # replays require this exact ROM, not only a matching RAM layout.
            fixture_index=dict(romSha1=meta['romSha1'],directory=str(out),
                reportSha256=sha((out/'observed.json').read_bytes()),
                stateSha256=sha((out/'candidate-ready.state').read_bytes()),
                ramSha256=sha((out/'candidate-ready.ram').read_bytes()),
                iwramSha256=sha((out/'candidate-ready.iwram').read_bytes()))
            index='mixed-'+args.mixed_class_group+'-fixture.json' if args.mixed_class_group else 'cost-fixture.json'
            (Path(meta['path']).parent/index).write_text(json.dumps(fixture_index,indent=2)+'\n')
        print('Battle-entry observations: '+str(out/'observed.json'))
        if args.entry_only:check(outcomes['parent']['menuVisible'] and outcomes['candidate']['menuVisible'],'Both actual battle menus reached')
        raise SystemExit(0)
    check(outcomes['parent']==outcomes['candidate'],'Paired Move/cancel gameplay outcome exact')
    for label,row in traces['candidate'].items():
        old=traces['parent'][label];live=row['live'];actual=bytes.fromhex(row['palette']);expected=bytearray.fromhex(old['palette'])
        check(row['frame']-traces['candidate']['ready']['frame']==old['frame']-traces['parent']['ready']['frame'],label+' identical frame input schedule from actual ready state')
        check(row['units']==old['units'],label+' canonical units unchanged')
        check(row['nativeShadow']==old['nativeShadow'],label+' full native palette shadow unchanged')
        check(live['failed']==0,label+' no ownership or allocation failure')
        check(row['fenceIntact'],label+' unused owned reservation fence intact')
        if live['active']:
            check(160<=live['start']<=live['end']<228,label+' palette scan within VBlank')
            if not live['flags']&128:check(160<=live['display']<228,label+' actual display enable within VBlank')
            for bank in range(16):
                if live['active']&(1<<bank):
                    custom=actual[512+bank*32:544+bank*32]
                    check(custom==bytes.fromhex(row['visibleColors']),label+' latched generated colors reach hardware')
                    expected[512+bank*32:544+bank*32]=custom
        check(bytes(expected)==actual,label+' every unowned hardware color unchanged')
    check(seed.read_bytes()==seedbytes,'World fixture unchanged')
    report=dict(status='passed',romSha1=meta['romSha1'],baseRomSha1=meta['baseRomSha1'],checks=checks,inputs=inputs,outcomes=outcomes,observations=observations,paletteTraces=traces,fixtureSha256=sha(seedbytes),routeSha256=sha(routepath.read_bytes()),scope='Isolated accepted-world route through actual deployment, twelve-unit Dark Knight coexistence and three-cell native Move/cancel. Exact paired native shadow/unowned hardware/unit isolation, generated binding-to-hardware transport, frame timing and unused reservation fence. Does not accept unsupported color operations, all-class/maximum heap capacity, battle completion or final art.')
    report['statusControl']=control_proof
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    if e:
        e.save(out/(case+'-failed.state'));e.screenshot(out/(case+'-failed.png'))
        for ext,addr in (('ram',0x02000000),('iwram',0x03000000),('vram',0x06000000)):(out/(case+'-failed.'+ext)).write_bytes(C.string_at(*e.maps[addr]))
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],statusControl=control_proof,error=str(error),checks=checks,inputs=inputs,observations=observations,entryPaletteTraces=entry_traces,paletteTraces=traces),indent=2)+'\n');print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
