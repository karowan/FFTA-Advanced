"""Thundaga plus repeated Status lifetime at the retained all-ten 13-actor state.

Reuse its exact own-ROM allocation. Declare only mastery, HP/MP and native RNG;
retain positions, classes and roster. Native menus select and execute the spell.
Observe heap each action frame, then require all actors and two balanced Status
lifetimes. No full-campaign, all-spell or final-art claim; no player files.
"""
import argparse, ast, ctypes as C, datetime, hashlib, json, runpy, struct
from pathlib import Path
from native_art import ROOT, sha
from native_battle_wrappers import from_emulator
from actor_render_evidence import actors
from live_palette_evidence import observe as palette_observe

index_path=ROOT/'notes/native-art-capacity-action-inputs.json';index=json.loads(index_path.read_text())
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--resume-targeting',action='store_true',help='Resume pinned failed range-four targeting and move one tile right to the legal range-three center.')
parser.add_argument('--resume-executed',action='store_true',help='Reuse pinned completed cast; verify exact sentinel preservation and continue remaining menu lifetimes.')
parser.add_argument('--reviewed-capacity',type=Path,help='Passing combined-ROM all-class report; reuse its own ready allocation')
args=parser.parse_args()
assert not (args.resume_targeting and args.resume_executed)
if args.reviewed_capacity:
    assert not (args.resume_targeting or args.resume_executed)
    index_path=args.reviewed_capacity;capacity=json.loads(index_path.read_text())
    meta_path=Path(capacity['manifest']);meta=json.loads(meta_path.read_text())
    assert capacity['status']=='passed' and capacity['manifestSha256']==sha(meta_path.read_bytes())
    assert capacity['romSha1']==meta['romSha1'] and 'reviewedActions' in meta['components']
    folder=index_path.parent
    index=dict(candidateSha1=capacity['romSha1'],fixtureRomSha1=capacity['fixtureRomSha1'],files={
        name:dict(path=str(folder/name),sha256=sha((folder/name).read_bytes())) for name in
        ('report.json','fixture.gba','ready.state','ready.ram','ready.iwram')})
raw={name:(ROOT/row['path']).read_bytes() for name,row in index['files'].items()}
assert all(sha(raw[name])==row['sha256'] for name,row in index['files'].items())
prior=json.loads(raw['report.json']);rom=raw['fixture.gba']
assert prior['status']=='passed' and prior['romSha1']==index['candidateSha1']
assert hashlib.sha1(rom).hexdigest()==prior['fixtureRomSha1']==index['fixtureRomSha1']
if not args.reviewed_capacity:meta=json.loads((ROOT/'build/art/connected'/index['candidateSha1']/'manifest.json').read_text())
live=meta['components']['livePalette']
assert meta['romSha1']==prior['romSha1'] and (args.reviewed_capacity or 'nativePaletteTransport' in meta['components'])
out=ROOT/'build/art/capacity-action'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
menus=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
tree=ast.parse((ROOT/'scripts/probe-ap-copy-heap.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='heap'],type_ignores=[]),'<native heap walk>','exec'))
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
lesson=next(x for x in registry['lessons'] if x['globalAbilityId']==371)
learned=next(x['abilityIndex'] for x in lesson['owners'] if x['jobId']==118)
CASTER=0x398;TARGETS=(0x2fc4,0x32dc);profiles={int(k):v for k,v in prior['profiles'].items()}
word=lambda b,p:struct.unpack_from('<I',b,p)[0]
half=lambda b,p:struct.unpack_from('<H',b,p)[0]
checks=[];samples=[];inputs=[];captures={};retained_action=None;e=None;phase='setup';tick=0;wrappers={}

def check(ok,label):
    assert ok,phase+'/'+label
    checks.append(phase+'/'+label)

def active():
    r=e.memory();return word(r,word(r,0xf438)-0x02000000+24)

def observe():
    r=e.memory();h=heap(r)
    check(h['end']==0x0203c000,'Heap respects reserved boundary at '+str(tick))
    check(h['freePayload']>=0 and h['largestFree']>=0,'Native heap walk valid at '+str(tick))
    if args.reviewed_capacity:
        base=live['ramReservation'][0]-0x02000000
        check(word(r,base+2584)==0 and not any(struct.unpack_from('<4I',r,base+live['refusalOffset'])) and
              word(r,base+live['bindingOffset']+live['bindingCounterOffset']+8)==0,
              'No custom palette allocation/effect failure at '+str(tick))
    samples.append(dict(phase=phase,frame=tick,free=h['freePayload'],largest=h['largestFree']))

def run(frames,key=0,sample=False):
    global tick
    if sample:
        for _ in range(frames):e.run(1,key);tick+=1;observe()
    else:e.run(frames,key);tick+=frames;observe()

def tap(key,wait=180):
    inputs.append(dict(phase=phase,frame=tick,press=8,key=key,wait=wait));run(8,key);run(wait)

def select_menu(wanted):
    # Observe the original yellow selection marker. The text background changes
    # during native menu transitions; disabled commands may also be skipped.
    for attempt in range(5):
        raw,width,height,pitch,pixel=e.frame
        check((width,height)==(240,160),'Native command menu dimensions')
        def colour(x,y):
            if pixel==1:
                blue,green,red=raw[y*pitch+x*4:y*pitch+x*4+3]
            else:
                v=int.from_bytes(raw[y*pitch+x*2:y*pitch+x*2+2],'little')
                if pixel==2:red,green,blue=(v>>11&31)*255//31,(v>>5&63)*255//63,(v&31)*255//31
                else:red,green,blue=(v>>10&31)*255//31,(v>>5&31)*255//31,(v&31)*255//31
            return red,green,blue
        def selected_marker(x,y):
            red,green,blue=colour(x,y)
            return red>=180 and green>=100 and blue<120
        counts=[sum(selected_marker(x,y) for y in range(82+16*row,95+16*row) for x in range(175,184)) for row in range(4)]
        check(max(counts)>10,'Visible native yellow menu selection '+str(counts))
        selected=counts.index(max(counts));inputs.append(dict(phase=phase,frame=tick,nativeMenuRow=selected,markerCounts=counts,wanted=wanted))
        # The existing text anchor deliberately includes black outline pixels.
        # Those change for the highlighted row; require its complete other
        # Wait/Status row instead, retaining original thresholds and coordinates.
        anchor=menus['ANCHOR'];unselected=lambda point:not 82+16*selected<=point[1]<95+16*selected
        points=[p for p in anchor['points'] if unselected(p)]
        dark=[p for p in anchor['darkPoints'] if unselected(p)]
        check(points and dark and all(min(colour(*p))>=anchor['threshold'] for p in points) and
            all(max(colour(*p))<=anchor['darkThreshold'] for p in dark),'Exact original unselected Wait/Status menu text')
        if selected==wanted:return
        tap(32,60)
    raise AssertionError('Requested native command row not reached')

def capture(label):
    e.save(out/(label+'.state'));e.screenshot(out/(label+'.png'))
    for ext,address in [('ram',0x02000000),('iwram',0x03000000),('vram',0x06000000),('palette',0x05000000),('oam',0x07000000)]:
        (out/(label+'.'+ext)).write_bytes(C.string_at(*e.maps[address]))
    captures[label]=dict(frame=tick,ramSha256=sha(e.memory()))

def bodies(label):
    r=e.memory();check(from_emulator(rom,e)==wrappers,label+' all13 exact native actors retained')
    pointers={unit:word(r,wrappers[unit]+0x44)-0x02000000 for unit in profiles}
    rows={a['address']:a for a in actors(rom,r,C.string_at(*e.maps[0x06000000]),set(pointers.values()))}
    check(set(rows)==set(pointers.values()),label+' all ten bodies configured')
    for unit,body in pointers.items():
        a=rows[body];job=profiles[unit]
        check(r[unit+7]==job and a['resource'] in (256+2*(job-116),257+2*(job-116)) and
            a['declaredSequence'] and a['expectedTiles']==a['tileCount']<=a['allocation'],label+' exact class and bounded resource '+str(job))
    if args.reviewed_capacity:
        if 'nativePaletteTransport' in meta['components']:
            from native_shared_palette_evidence import observe as native_observe
            native_observe(rom,r,C.string_at(*e.maps[0x05000000]),C.string_at(*e.maps[0x07000000]),wrappers,check,set(range(10)))
        else:
            palette_observe(live,rom,r,C.string_at(*e.maps[0x05000000]),C.string_at(*e.maps[0x07000000]),check,{0,1,2})

try:
    e=E(ROOT/index['files']['fixture.gba']['path']);e.load(ROOT/index['files']['ready.state']['path'])
    check(e.memory()==raw['ready.ram'] and C.string_at(*e.maps[0x03000000])==raw['ready.iwram'],'Exact own-ROM RAM/IWRAM loaded')
    wrappers=from_emulator(rom,e);check(len(wrappers)==13 and len(profiles)==10,'Retained 13 actors and ten classes')
    # Loading a libretro state restores memory but does not publish a frame.
    # Preserve the exact-load assertion above; render one no-input frame before
    # applying the existing screenshot-based menu observer.
    run(1)
    check(active()==0x02000000+CASTER and menus['menu_visible'](e),'Viking owns original ready turn')
    if args.resume_executed:
        resume={name:(ROOT/row['path']).read_bytes() for name,row in index['executionResume'].items()}
        for name,row in index['executionResume'].items():check(sha(resume[name])==row['sha256'],'Retained execution evidence '+name)
        failure=json.loads(resume['failed.json'])
        check(failure['error']=='execution/Action roots retired','Exact retained completed-cast failure')
        e.load(ROOT/index['executionResume']['executed.state']['path'])
        check(e.memory()==resume['executed.ram'] and C.string_at(*e.maps[0x03000000])==resume['executed.iwram'],'Exact own-ROM post-cast RAM/IWRAM')
        before=resume['confirmation.ram'];after=e.memory();phase='execution'
        retained_action=dict(files=index['executionResume'],samples=failure['samples'],inputs=failure['inputs'],scope='Actual earlier cast and per-frame heap observations reused; the failing sentinel-zero expectation is corrected, not claimed to have passed.')
        tick=failure['samples'][-1]['frame'];run(1)
        check(active()==0x02000000+CASTER and menus['menu_visible'](e),'Native post-cast menu remains ready')
    else:
        if args.resume_targeting:
            resume={name:(ROOT/row['path']).read_bytes() for name,row in index['targetingResume'].items()}
            for name,row in index['targetingResume'].items():check(sha(resume[name])==row['sha256'],'Retained targeting evidence '+name)
            failure=json.loads(resume['failed.json'])
            check(failure['error']=='targeting/Native target confirmation reached','Exact retained out-of-range attempt')
            e.load(ROOT/index['targetingResume']['failed.state']['path'])
            check(e.memory()==resume['failed.ram'] and C.string_at(*e.maps[0x03000000])==resume['failed.iwram'],'Exact own-ROM targeting RAM/IWRAM')
            phase='targeting';run(1)
            check(active()==0x02000000+CASTER and from_emulator(rom,e)==wrappers,'Retained caster and all13 actor identities')
            inputs.append(dict(resume=index['targetingResume'],correction='Center moves10,8 to11,8; native range3'))
            for key in (128,256,256):tap(key)
        else:
            e.set_memory(CASTER+0x40,bytes(144));e.set_memory(CASTER+0x40+learned,b'\xff')
            e.set_memory(CASTER+0x36,b'\0');e.set_memory(CASTER+0x3a,bytes(2))
            for unit in (CASTER,*TARGETS):e.set_memory(unit+0x18,struct.pack('<4H',500,500,100,100))
            inputs.append(dict(masteredAbility=371,abilityIndex=learned,caster=CASTER,targets=TARGETS,hp=500,mp=100,positions='unchanged'))
            run(30);bodies('before');capture('ready');phase='targeting'
            for key in (32,256,32,256,256):tap(key)
            r=e.memory();check(word(r,word(r,0xf438)-0x02000000+20)==371,'Native action menu selects Thundaga')
            # Thundaga r3: center Mystic11,8 includes adjacent Dark Knight10,8.
            # The old four-tile center10,8 was correctly refused by the game.
            for key in (64,16,16,256,256):tap(key)
        before=e.memory();manager=word(before,0xf438)-0x02000000;capture('confirmation')
        check(before[manager+4]==11 and half(before,0xf3fc)==371,'Native target confirmation reached')
        check(half(before,CASTER+0x1c)==100,'No premature MP payment')
        C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',1),4);inputs.append(dict(nativeRng=1))
        phase='execution';tap(256,0);run(1800,sample=True);after=e.memory();capture('executed')
    check(half(after,CASTER+0x1c)==80,'Exactly one Thundaga MP payment')
    damage={str(u):500-half(after,u+0x18) for u in TARGETS}
    check(all(0<x<500 for x in damage.values()),'Both adjacent enemy classes take bounded positive native damage')
    execution_root=bytes(4) if args.reviewed_capacity else bytes.fromhex('d7d7d7d7')
    check(before[0x3ff44:0x3ff48]==execution_root and after[0x3ff44:0x3ff48]==execution_root and after[0x3ff48:0x3ff4c]==bytes(4),'Declared unused execution root preserved; actual action snapshot retired')
    check(after[0x1940:0x1e70]==before[0x1940:0x1e70] and
        after[CASTER+0x40:CASTER+0xd0]==before[CASTER+0x40:CASTER+0xd0],'Inventory and mastery preserved')
    bodies('after spell');old=active();select_menu(2);tap(256);tap(256,900)
    for _ in range(240):
        if active()!=old and menus['menu_visible'](e):break
        run(30)
    else:raise AssertionError('No following native party menu within7200 frames')
    capture('next-turn');bodies('next turn');returned_heap=heap(e.memory())
    phase='status'
    for cycle in range(2):
        select_menu(3);tap(256)
        r=e.memory();ctx=word(C.string_at(*e.maps[0x03000000]),0x2818)
        check(0x02000000<=ctx<ctx+0x7280<=0x0203c000,'Status context bounds '+str(cycle))
        check(word(r,ctx-0x02000000+0x2d50)==ctx+0x4340,'Owned Status list '+str(cycle))
        ownership=struct.unpack_from('<4I',r,live['partyHeapRoot']-0x02000000)
        check(ownership[0]==0x50485232 and ownership[1]==word(r,0xf434),'Status shares actual live battle heap '+str(cycle))
        capture('status-'+str(cycle));tap(1);run(180)
        select_menu(0)
        check(menus['menu_visible'](e),'Actual native menu return '+str(cycle))
        r=e.memory();closed=struct.unpack_from('<4I',r,live['partyHeapRoot']-0x02000000)
        check(closed[0]==0 and closed[1]==word(r,0xf434) and closed[2]==closed[3] and word(r,0x3ff40)==0,
            'Status owner and copy root balanced '+str(cycle))
        check(heap(r)==returned_heap,'Complete heap allocation structure restored '+str(cycle))
        bodies('Status return '+str(cycle));capture('returned-'+str(cycle))
    for name,row in index['files'].items():check(sha((ROOT/row['path']).read_bytes())==row['sha256'],'Source evidence preserved '+name)
    report=dict(status='passed',checks=checks,romSha1=index['fixtureRomSha1'],candidateSha1=index['candidateSha1'],
        inputIndexSha256=sha(index_path.read_bytes()),scope=__doc__,inputs=inputs,samples=samples,captures=captures,
        damage=damage,retainedAction=retained_action,minFreeBytes=min(s['free'] for s in samples+(retained_action['samples'] if retained_action else [])),minLargestBlock=min(s['largest'] for s in samples+(retained_action['samples'] if retained_action else [])))
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),damage=damage,minFreeBytes=report['minFreeBytes'],report=str(out/'report.json'))))
except Exception as error:
    if e and e.frame:capture('failed')
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=index['fixtureRomSha1'],candidateSha1=index['candidateSha1'],inputIndexSha256=sha(index_path.read_bytes()),scope=__doc__,checks=checks,phase=phase,error=str(error),samples=samples,inputs=inputs,captures=captures),indent=2)+'\n',encoding='utf-8')
    print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
