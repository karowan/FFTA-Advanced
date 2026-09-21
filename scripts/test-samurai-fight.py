"""Actual Samurai katana Fight reference and generated-action playback.

Fresh native entry from the authenticated disposable world checkpoint. Only
preallocation appearance/equipment and declared formation/HP/RNG are fixtures.
No player saves, live actor pose writes or production-art acceptance.
"""
import argparse,contextlib,ctypes as C,datetime,hashlib,json,runpy,struct
from pathlib import Path
from native_art import ROOT,sha
from native_battle_wrappers import fixed_giza_formation,from_emulator
from actor_render_evidence import actors
from native_body_display import pending_from_anchor,retained,layout_reset_display,completed_pending_facing
from live_palette_evidence import observe as palette_observe

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--current',type=Path,default=ROOT/'build/art/refinement/samurai-support-v1/current.json')
parser.add_argument('--baseline-report',type=Path)
parser.add_argument('--baseline-sha256')
parser.add_argument('--reviewed-entry',action='store_true',
                    help='Authenticate the separate own-ROM reviewed action cold-entry evidence')
parser.add_argument('--entry-index',type=Path,default=ROOT/'build/art/reviewed-integration/action-entry-latest.json')
parser.add_argument('--job',type=int,choices=range(116,126),default=116,
                    help='Declared preallocation racial profile; default preserves the Samurai reference.')
parser.add_argument('--weapon-type',type=int,choices=(*range(1,20),31),
                    help='Exercise a specific allowed native weapon family.')
parser.add_argument('--combo',action='store_true',
                    help='Select the native assigned Combo instead of Fight; verify exactly one JP debit.')
args=parser.parse_args();assert bool(args.baseline_report)==bool(args.baseline_sha256)
assert not args.combo or not args.baseline_report,'Combo requires its own outcome evidence'
if args.combo and args.job==123 and not args.weapon_type:args.weapon_type=16
meta=json.loads(args.current.read_text(encoding='utf-8'));rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
palette_meta=meta['components']['livePalette'] if 'components' in meta else meta
if args.reviewed_entry:
    index=json.loads(args.entry_index.read_text())
    entry_path=ROOT/index['report'];assert sha(entry_path.read_bytes())==index['sha256']
    entry=json.loads(entry_path.read_text());assert entry['status']=='passed' and entry['romSha1']==meta['romSha1']
    fixture=entry_path.parent/'cold-entry';fixture_rom=fixture/'frozen.gba'
    assert hashlib.sha1(fixture_rom.read_bytes()).hexdigest()==meta['romSha1']
else:
    fixture_rom=Path(meta['fixtureSource']);fixture=fixture_rom.parent/'fixture'
seed=fixture/'accepted-world.state';seedbytes=seed.read_bytes()
route=json.loads((fixture/'route.json').read_text(encoding='utf-8'));proof=json.loads((fixture/'report.json').read_text(encoding='utf-8'))
assert proof['passed'] and proof['romSha1']==route['romSha1']==hashlib.sha1(fixture_rom.read_bytes()).hexdigest()
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];menus=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
out=ROOT/('build/art/class-combo' if args.combo else 'build/art/samurai-fight' if args.job==116 else 'build/art/class-fight')/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];inputs=[];observations={};e=None;clock=0;anchor=None;previous=None;wrappers={};captures=set()
palette_trace=None;completed_composition_events=[]
job_table=struct.unpack_from('<I',rom,0xc8598)[0]-0x08000000
job_record=rom[job_table+args.job*52:job_table+(args.job+1)*52]
race=job_record[4];resource=struct.unpack_from('<H',job_record,7)[0]
assert race in range(1,6) and resource==256+2*(args.job-116)
ACTOR,TARGET={1:0x290,2:0x398,3:0x4a0,4:0x5a8,5:0x5a8}[race],0x33e4
SWAP=0x290 if ACTOR==0x398 else 0x398
word=lambda r,p:struct.unpack_from('<I',r,p)[0]
half=lambda r,p:struct.unpack_from('<H',r,p)[0]
def check(ok,label):
    assert ok,label
    checks.append(label)
def active():
    r=e.memory();return word(r,word(r,0xf438)-0x02000000+24)
def step(n,key=0):
    global clock
    e.run(n,key);clock+=n
def tap(key,wait=180):
    inputs.append([8,key,wait]);step(8,key);step(wait)
def initial_action_reset(r,v,hardware,body,producer=None):
    # Same cross-sequence constructor contract already exercised by the real
    # casting test. This is retained old display, never a new action-frame proof.
    if not anchor or not anchor['direct'] or not 0<clock-anchor['frame']<=4:return None
    flags,resource,mode,timer,index,count=struct.unpack_from('<I2x5H',r,body)
    tile,alternate,allocation=struct.unpack_from('<3H',r,body+0x12)
    first,current=struct.unpack_from('<II',r,body+0x34)
    if not (0x08000004<=first<0x08000000+len(rom)-4 and 1<=count<100):return None
    # Native21618 starts facings0/1 at45 and facings2/3 at65. Callers may
    # additionally set2/100; do not assume every action faces2/3.
    native_flags=0x65 if mode&3 in (2,3) else 0x45
    if flags not in (native_flags,native_flags|2,native_flags|0x100,native_flags|0x102) or timer or word(r,body+0x20)!=0xffffffff or word(r,body+0x2c):return None
    if (resource,tile,allocation)!=anchor['identity'] or half(r,body+0x24)!=anchor['actor']['tileCount']:return None
    initial=index==0 and current==first and word(r,body+0x28)==anchor['actor']['oam']
    manual=flags==0x167 and mode==7 and index==1 and current==first+20 and count==4
    if manual:
        from native_art import OAM
        manual=word(rom,current-0x08000000+4)+OAM+0x08000000==word(r,body+0x28)
    if not (initial or manual):return None
    table=word(rom,0x2102c)-0x08000000
    descriptor=word(rom,table+resource*4)-0x08000000+(mode&~3)*6+(12 if mode&3 in (1,2) else 0)
    if word(rom,descriptor)+4!=first or word(rom,first-0x08000004)!=count:return None
    block=v[0x10000+tile*32:0x10000+(tile+allocation)*32]
    objects=[struct.unpack_from('<3H',hardware,i*8) for i in range(128)]
    visible=[o for o in objects if o[0]&0x300!=0x200 and o[2]&1023==tile]
    if block!=anchor['block']:return None
    if not visible:
        # Dark Knight's native Combo changes sequence while the jumping actor
        # is offscreen. Retained tiles alone are not display evidence: require
        # the captured native compositor to prove that no hardware object
        # references any tile in this allocation during the constructor reset.
        if not args.combo or not producer or not producer.get('nativeShapes'):return None
        from native_oam_evidence import hidden_at_composition
        hidden_at_composition(palette_meta,rom,palette_trace.events[-1],hardware,tile,allocation,check,
                              native='nativePaletteTransport' in meta.get('components',{}))
        return dict(anchor['actor'],flags=flags,mode=mode,index=index,timer=timer,first=first,current=current,
                    displayedFrames=[],exactUpload=False,configured=False,
                    displayProof='Exact retained allocation during native-hidden action constructor')
    if visible!=anchor['hardware']:
        # Native Combo afterimages can add another use of the same tile block.
        # Require actual composition geometry proof and every prior copy still
        # present, rather than accepting an arbitrary new pose or movement.
        from collections import Counter
        if not producer or not producer.get('nativeShapes') or not anchor['hardware']:return None
        if Counter(anchor['hardware'])-Counter(visible):return None
    return dict(anchor['actor'],flags=flags,mode=mode,index=index,timer=timer,first=first,current=current,
                displayedFrames=[],exactUpload=False,configured=False,displayProof='Exact previous display across native action constructor')
def capture(name):
    global anchor,previous
    r=e.memory();v=C.string_at(*e.maps[0x06000000]);hardware=C.string_at(*e.maps[0x07000000]);pal=C.string_at(*e.maps[0x05000000])
    body=word(r,wrappers[ACTOR]+0x44)-0x02000000
    found=actors(rom,r,v,{body});a=found[0] if found else None
    if a is None:a=layout_reset_display(rom,r,v,hardware,body,anchor,clock-anchor['frame']) if anchor else None
    if a is None:
        producer=None
        if args.combo and palette_trace and palette_trace.events:
            from native_oam_evidence import shapes_at_composition
            producer=shapes_at_composition(palette_meta,rom,palette_trace.events[-1],hardware,check)
        a=initial_action_reset(r,v,hardware,body,producer)
    check(a is not None,name+' native body configured or bounded reset')
    start=0x10000+a['tile']*32;block=v[start:start+a['allocation']*32]
    direct=bool(a['displayedFrames']) and a['declaredSequence'];hold=None
    if not direct:
        if anchor:hold=pending_from_anchor(a,block,anchor,clock-anchor['frame'])
        if not hold:hold=retained(a,block,previous)
        if not hold and anchor:hold=completed_pending_facing(rom,a,block,anchor,clock-anchor['frame'])
        if not hold and a.get('configured') is False:hold=a['displayProof']
    row=dict(direct=direct,identity=(a['resource'],a['tile'],a['allocation']),block=block,first=a['first'],index=a['index'])
    if direct:
        objects=[struct.unpack_from('<3H',hardware,i*8) for i in range(128)]
        anchor=dict(row,frame=clock,actor=a,hardware=[o for o in objects if o[0]&0x300!=0x200 and o[2]&1023==a['tile']])
    elif not hold:anchor=None
    previous=row
    check(a['resource']==resource and a['declaredSequence'] and bool(direct or hold),name+' exact bounded class body display')
    check(a['expectedTiles']==a['tileCount']<=a['allocation'],name+' native body allocation')
    if 'nativePaletteTransport' in meta.get('components',{}):
        emitted=any(attr&0x300!=0x200 and tile&1023==a['tile'] and (attr,x,tile)!=(0xa8,0xf8,0)
                    for attr,x,tile in (struct.unpack_from('<3H',hardware,i*8) for i in range(128)))
        if args.combo and not emitted:
            from native_oam_evidence import boundary_inputs,native_tiles_hidden
            check(palette_trace is not None and bool(palette_trace.events),'Native-hidden Combo has actual composition observation')
            _,iw=boundary_inputs(palette_meta,palette_trace.events[-1],hardware,check)
            palette_proof=native_tiles_hidden(rom,iw,hardware,a['tile'],a['allocation'],check)
        else:
            from native_shared_palette_evidence import observe as native_observe
            observed_combo=args.combo and palette_trace is not None and bool(palette_trace.events)
            if observed_combo:
                from native_oam_evidence import boundary_inputs,reconstruct
                _,iw=boundary_inputs(palette_meta,palette_trace.events[-1],hardware,check)
                expected,_=reconstruct(rom,iw)
                check(hardware==expected,'Complete native Combo geometry and banks, including offscreen jump')
            palette_proof=native_observe(rom,r,pal,hardware,wrappers,check,set(range(10)),require_visible=not observed_combo)
    elif args.combo and word(r,palette_meta['ramReservation'][0]-0x02000000+2572)==0:
        from native_oam_evidence import hidden_at_composition
        check(palette_trace is not None and bool(palette_trace.events),'Hidden Combo frame has actual native composition observation')
        palette_proof=hidden_at_composition(palette_meta,rom,palette_trace.events[-1],hardware,a['tile'],a['allocation'],check)
    else:
        owner=palette_meta.get('paletteGroups',{}).get('ownerMap',list(range(10)))[args.job-116]
        palette_proof=palette_observe(palette_meta,rom,r,pal,hardware,check,{owner})
    # Separate auxiliary actors remain observations, not accepted held-art proof.
    allactors=actors(rom,r,v)
    auxiliary=[x for x in allactors if x['address']!=body and x['resource']>=128 and x['resource']<256]
    slot=(a['mode']//4)*2+(1 if a['mode']%4 in (1,2) else 0)
    observation=dict(frame=clock,actor=a,slot=slot,displayProof='current' if direct else hold,blockSha256=sha(block),
                     position=list(struct.unpack_from('<3H',r,wrappers[ACTOR]+8)),auxiliaries=auxiliary,paletteProof=palette_proof)
    observations[name]=observation
    signature=(a['mode'],tuple(a['displayedFrames']),tuple((x['resource'],x['mode'],tuple(x['displayedFrames'])) for x in auxiliary))
    if name in ('ready','moved','confirmation','executed','returned') or (a['mode']>=8 and signature not in captures):
        captures.add(signature);e.screenshot(out/(name+'.png'))
        for ext,data in [('ram',r),('vram',v),('oam',hardware),('palette',pal)]:(out/(name+'.'+ext)).write_bytes(data)
    return r
try:
    e=E(Path(meta['path']));e.load(seed);e.set_memory(0x3ff44,bytes(8))
    check(e.memory()[ACTOR+6]==(4 if race==5 else race),'Existing declared generic racial slot')
    e.set_memory(ACTOR+4,bytes([1,args.job,race,args.job]));e.set_memory(ACTOR+0x35,bytes([args.job]))
    items=word(rom,0x79aec)-0x08000000
    permissions=word(rom,0xcac40)-0x08000000;mask=word(rom,permissions+job_record[0x2d]*4)
    if args.weapon_type:check(bool(mask&(1<<(args.weapon_type-1))),'Requested native weapon family allowed by actual class table')
    weapon=next(i for i in range(1,461) if rom[items+32*i+8] in (*range(1,20),31) and mask&(1<<(rom[items+32*i+8]-1)) and (not args.weapon_type or rom[items+32*i+8]==args.weapon_type))
    weapon_type=rom[items+32*weapon+8]
    e.set_memory(ACTOR+0x2a,struct.pack('<5H',weapon,0,0,0,0))
    inputs.append(['preallocation Human Samurai and ordinary katana',weapon] if args.job==116 else ['preallocation generic class/race/weapon profile',args.job,race,weapon,weapon_type])
    if args.combo:
        registry=json.loads((ROOT/'build/expansion/registry.json').read_text(encoding='utf-8'))
        lesson=next(x for x in registry['lessons'] if x['type']=='Combo' and any(o['jobId']==args.job for o in x['owners']))
        owner=next(o for o in lesson['owners'] if o['jobId']==args.job)
        check(owner['race']==race,'Combo lesson belongs to actual racial class')
        learned=owner['abilityIndex']
        ap=0x1b40+((ACTOR-0x80)//264)*34+learned-144 if race==1 and learned>=144 else ACTOR+0x40+learned
        for unit in (0x80,0x188,0x290,0x398,0x4a0,0x5a8):
            e.set_memory(unit+0xd6,struct.pack('<H',3 if unit==ACTOR else 0))
            e.set_memory(unit+0x3c,bytes([learned if unit==ACTOR else 0]))
        e.set_memory(ap,b'\x8a')
        inputs.append(['preallocation sole assigned mastered Combo, initiator JP3/others0',lesson['id'],learned,ap])
    for x,y,key in route['path']:step(1,key)
    step(30);tap(256,1200)
    for _ in range(7):tap(256,600)
    for _ in range(3):tap(256)
    for _ in range(3):
        for key in (128,256,256,256):tap(key)
    tap(8,600);tap(256,600);tap(256,600);menus['wait_for_menu'](e)
    for turn in range(12):
        if active()==0x02000000+ACTOR:break
        old=active()
        for key in (32,32,256,256):tap(key)
        for tick in range(0,6300,30):
            if active()!=old and menus['menu_visible'](e):break
            step(30)
        else:raise AssertionError('Native preceding turn missing')
    check(active()==0x02000000+ACTOR,'Actual native focus class turn')
    fixed_giza_formation(rom,e);wrappers=from_emulator(rom,e)
    # Reuse proven Giza katana/axe target lane, swapping only two allied starts.
    for unit,x,y,height in ((ACTOR,1,14,16),(SWAP,1,13,32)):
        e.set_memory(unit+0xf6,bytes((x,y)));e.set_memory(wrappers[unit]+8,struct.pack('<3H',x*32+16,height,y*32+16))
    e.set_memory(TARGET+0x18,struct.pack('<2H',250,250));inputs.append(['canonical Giza formation; slot2/3 starting tiles exchanged; target HP250'] if args.job==116 else ['canonical Giza formation; focus/swap lane; target HP250',ACTOR,SWAP])
    step(30);initial=capture('ready')
    check(struct.unpack_from('<3H',initial,wrappers[ACTOR]+8)==(48,16,464),'Declared1,14 start')
    if args.combo:check(half(initial,ACTOR+0xd6)==3 and initial[ACTOR+0x3c]==learned and initial[ap]==0x8a,'Actual turn retains assigned mastered Combo and JP3')
    for key in (256,128,128,128,256):tap(key)
    menus['wait_for_menu'](e);moved=capture('moved')
    check(half(moved,wrappers[ACTOR]+8)==144,'Native Move reaches4,14')
    for key in ((256,16,256,128,256,256) if args.combo else (256,256,128,256,256)):tap(key)
    before=capture('confirmation');manager=word(before,0xf438)-0x02000000
    check(before[manager+4]==11,'Actual '+('Combo' if args.combo else 'Fight')+' target confirmation')
    if args.combo:check(half(before,ACTOR+0xd6)==3,'No premature Combo JP debit')
    C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',2),4);inputs.append(['native RNG',2])
    # The confirmation input is sampled too, preserving short body/weapon poses.
    if args.combo:
        from mgba_instruction_trace import InstructionTrace
        from native_oam_evidence import snapshot_ranges
        palette_trace=InstructionTrace(e,{0x080004dc:'native-composed'}, {0x080004dc:snapshot_ranges(palette_meta)})
    with palette_trace if palette_trace is not None else contextlib.nullcontext():
        for tick in range(8):step(1,256);capture('press-'+str(tick))
        for tick in range(600):step(1);capture('attack-'+str(tick))
    # Composition snapshots describe only the observed window. Never compare
    # its final OAM event with a later turn's hardware after the trace stops.
    completed_composition_events=palette_trace.events if palette_trace else []
    palette_trace=None
    step(1200);after=capture('executed')
    check(0<250-half(after,TARGET+0x18)<250,'Native equipped action deals bounded positive damage')
    if args.combo:
        check(half(after,ACTOR+0xd6)==0,'Native Combo spends all three JP exactly once')
        check(after[ACTOR+0x3c]==learned and after[ap]==0x8a,'Combo assignment and mastery retained')
        check(all(half(after,unit+0xd6)==0 for unit in (0x80,0x188,0x290,0x398,0x4a0,0x5a8)),'No unintended participant or KO JP award')
    check(after[0x1940:0x1ebc]==initial[0x1940:0x1ebc] and after[ACTOR+0x40:ACTOR+0xd0]==initial[ACTOR+0x40:ACTOR+0xd0],'Inventory AP learning unchanged')
    check(after[0x3ff44:0x3ff4c]==bytes(8),'Action roots retired')
    old=active();tap(256,600);menus['wait_for_menu'](e,limit=6300);final=capture('returned')
    check(active()!=old,'Following native turn returned')
    action_rows=[v for v in observations.values() if v['actor']['mode']>=8 and v['actor']['displayedFrames']]
    check(bool(action_rows),'Actual non-idle class action frames uploaded')
    outcome=dict(damage=250-half(after,TARGET+0x18),hp=half(after,ACTOR+0x18),mp=half(after,ACTOR+0x1c),**({'katana':weapon} if args.job==116 else {'weapon':weapon}))
    if args.baseline_report:
        raw=args.baseline_report.read_bytes();check(sha(raw)==args.baseline_sha256,'Retained baseline report authenticated');prior=json.loads(raw)
        check(prior['status']=='passed' and prior['outcome']==outcome and prior['inputs']==inputs,'Exact paired katana outcome and fixed inputs preserved')
    check(seed.read_bytes()==seedbytes,'Source world checkpoint preserved')
    report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,inputs=inputs,outcome=outcome,observations=observations,
        nativeActionSlots=sorted({v['slot'] for v in action_rows}),fixtureSha256=sha(seedbytes),baseline=str(args.baseline_report) if args.baseline_report else None,
        scope='Actual generic Human Samurai katana Move/Fight/next turn; every-frame body upload/bounds and hardware palette checks during608 action frames. Auxiliary weapon/effect records and selected screenshots retained for pose/attachment study; auxiliary art not independently accepted. No final-art, every attack family or campaign acceptance.')
    report.update(job=args.job,race=race,resource=resource,weaponType=weapon_type)
    if args.job!=116:
        report['scope']='Actual declared class/race profile allocated before native deployment; allowed weapon selected from current native permission table. Native Move/Fight/next turn with608 every-frame action body/palette observations. Moogle cases explicitly repurpose the generic Viera slot before allocation; inherited unit stats are controlled fixture inputs, not growth/save acceptance. Auxiliary weapon/effect art is recorded but not independently accepted. No all-actions, final-art, performance or campaign acceptance.'
    if args.combo:
        report.update(command='Combo',lesson=lesson['id'],jpBefore=half(before,ACTOR+0xd6),jpAfter=half(after,ACTOR+0xd6))
        report['nativeOnlyFrames']=sum(bool(o['paletteProof'].get('nativeOnly')) for o in observations.values())
        report['compositionEvents']=completed_composition_events
        report['scope']='Actual declared generic class/race/allowed weapon allocated before native deployment, sole assigned mastered Combo and three JP. Native Move/Combo/next turn, positive damage, one JP debit, preserved mastery/equipment/inventory and608 every-frame body/palette observations. Native-only banner frames independently reconstruct complete original OAM at actual composition boundary and prove retained body tiles absent from display. Auxiliary actors recorded, not independently accepted. Does not prove participation chains, all action-tail frames, natural acquisition, cold saves, final art, performance or campaign; Moogle profiles retain disposable Viera base stats.'
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'),outcome=outcome,nativeActionSlots=report['nativeActionSlots'])))
except Exception as error:
    if e:
        e.save(out/'failed.state');e.screenshot(out/'failed.png')
        for ext,addr in (('ram',0x02000000),('iwram',0x03000000),('vram',0x06000000),('palette',0x05000000),('oam',0x07000000)):(out/('failed.'+ext)).write_bytes(C.string_at(*e.maps[addr]))
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),checks=checks,inputs=inputs,observations=observations,compositionEvents=palette_trace.events if palette_trace else completed_composition_events),indent=2)+'\n',encoding='utf-8');print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
