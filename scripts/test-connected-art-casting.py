"""Actual custom Viking Thunder/Thundaga with four generated racial bodies.

Uses the authenticated exact-ROM mixed ready state, native menus and native
casts. Learning, stats, formation and RNG are declared disposable inputs.
Control removes only class composition; it is never a playable deliverable.
"""
import argparse, ast, ctypes as C, datetime, hashlib, json, runpy, struct
from pathlib import Path
from native_art import ROOT, sha
from native_battle_wrappers import fixed_giza_formation, from_emulator
from actor_render_evidence import actors

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--current-ready',action='store_true')
parser.add_argument('--reviewed-entry',action='store_true',help='Use the authenticated reviewed action candidate and its own cold-entry capture.')
parser.add_argument('--action',type=int,choices=(365,371))
parser.add_argument('--manifest',type=Path,
                    help='Explicit connected manifest; requires pinned retained ready evidence.')
parser.add_argument('--ready-evidence',type=Path,
                    help='Committed report/state/RAM/IWRAM hashes for an existing exact-ROM ready capture.')
parser.add_argument('--native-entry',type=Path,
                    help='Authenticated paired native-palette entry selector; each branch uses its own ROM/state.')
parser.add_argument('--secondary',action='store_true',
                    help='Use Viking Arts as A2 on an already allocated Bangaa Dark Knight119.')
args=parser.parse_args()
assert bool(args.manifest)==bool(args.ready_evidence)
assert not args.manifest or not args.current_ready
assert not args.native_entry or not (args.manifest or args.current_ready)
assert not args.reviewed_entry or not (args.manifest or args.current_ready or args.native_entry)
assert not args.secondary or args.native_entry
native_entry=None;source_pins={};trace=None
if args.native_entry:
    entry_index=json.loads(args.native_entry.read_text());entry_path=Path(entry_index['report'])
    assert sha(entry_path.read_bytes())==entry_index['sha256']
    native_entry=json.loads(entry_path.read_text());assert native_entry['status']=='passed'
    meta_path=Path(native_entry['manifest']);assert sha(meta_path.read_bytes())==native_entry['manifestSha256']
    source_pins={str(entry_path):sha(entry_path.read_bytes()),str(meta_path):sha(meta_path.read_bytes())}
else:
    meta_path=ROOT/'build/art/reviewed-integration/action-candidate.json' if args.reviewed_entry else args.manifest or (ROOT/'build/art/connected/current.json' if args.current_ready else ROOT/'build/art/connected/4a7d55ce09cd4a40965a0bb97de2701d276789c5/manifest.json')
meta=json.loads(meta_path.read_text());rom=Path(meta['path']).read_bytes();live=meta['components']['livePalette']
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
stem='candidate-ready';report_name='observed.json';evidence=None
if args.reviewed_entry:
    entry_index=json.loads((ROOT/'build/art/reviewed-integration/action-entry-latest.json').read_text())
    entry_path=ROOT/entry_index['report'];assert sha(entry_path.read_bytes())==entry_index['sha256']
    entry=json.loads(entry_path.read_text());assert entry['status']=='passed' and entry['romSha1']==meta['romSha1']
    assert entry['manifestSha256']==sha(meta_path.read_bytes())
    source=entry_path.parent;stem='ready';report_name='report.json'
    index={kind+'Sha256':sha((source/(stem+'.'+ext)).read_bytes()) for kind,ext in [('state','state'),('ram','ram'),('iwram','iwram')]}
elif native_entry:
    assert 'nativePaletteTransport' in meta['components'] and native_entry['romSha1']==meta['romSha1']
    source=entry_path.parent;report_name=entry_path.name
    index={kind+'Sha256':sha((source/(stem+'.'+ext)).read_bytes()) for kind,ext in [('state','state'),('ram','ram'),('iwram','iwram')]}
    for branch_name in ('candidate','control'):
        for ext in ('state','ram','iwram'):
            path=source/(branch_name+'-ready.'+ext);source_pins[str(path)]=sha(path.read_bytes())
elif args.ready_evidence:
    evidence=json.loads(args.ready_evidence.read_text(encoding='utf-8'))
    assert evidence['romSha1']==meta['romSha1']
    source=ROOT/evidence['directory'];stem=evidence['stem'];report_name=evidence['report']
    assert Path(stem).name==stem and Path(report_name).name==report_name
    index=evidence['hashes']
    assert sha((source/report_name).read_bytes())==index['reportSha256']
elif args.current_ready:
    index=json.loads((Path(meta['path']).parent/'mixed-first-fixture.json').read_text())
    assert index['romSha1']==meta['romSha1']
    source=Path(index['directory'])
    assert sha((source/'observed.json').read_bytes())==index['reportSha256']
else:
    source=ROOT/'build/art/live-palette/battle/20260918T183919.610099Z'
    index=dict(stateSha256='a0208a9a4721b41afa45a760007a90b694d3c7aa20023689d944bea59ba641d3',
        ramSha256='0a0de57cd3ee8b617475b572b856b2181628eed8ed0e120af93451394f642018',
        iwramSha256='6ab0ad9dd121fc844eb9aaa15f184ee83ba4f1ebdb8cd9b5109ad433f686ada4')
seed=source/(stem+'.state');seedbytes=seed.read_bytes()
ram0=(source/(stem+'.ram')).read_bytes();iw0=(source/(stem+'.iwram')).read_bytes()
assert (sha(seedbytes),sha(ram0),sha(iw0))==(index['stateSha256'],index['ramSha256'],index['iwramSha256'])
prior=json.loads((source/report_name).read_text());assert prior['status']=='passed' and prior['romSha1']==meta['romSha1']
patch=next(p for p in live['changes'] if p['offset']==0x12bc)
out=ROOT/'build/art/connected/casting'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
if native_entry:
    controlpath=Path(native_entry['records']['control']['path']);control=controlpath.read_bytes()
    assert hashlib.sha1(control).hexdigest()==native_entry['records']['control']['romSha1']
    assert rom[0x12bc:0x12c4]==control[0x12bc:0x12c4]==bytes.fromhex(patch['before'])
else:
    assert rom[0x12bc:0x12c4].hex()==patch['after'] and patch['bytes']==8
    control=bytearray(rom);control[0x12bc:0x12c4]=bytes.fromhex(patch['before'])
    controlpath=out/'composition-bypass.gba';controlpath.write_bytes(control)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
menus=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
tree=ast.parse((ROOT/'scripts/probe-ap-copy-heap.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='heap'],type_ignores=[]),'<read-only heap>','exec'))
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
ACTOR,TARGET=0x398,0x33e4
checks=[];inputs=[];results=[];samples=[];e=None;case='setup'
word=lambda r,p:struct.unpack_from('<I',r,p)[0]
half=lambda r,p:struct.unpack_from('<H',r,p)[0]

def check(ok,label):
    assert ok,case+'/'+label
    checks.append(case+'/'+label)

def active():
    r=e.memory();return word(r,word(r,0xf438)-0x02000000+24)

def tap(key,wait=180):
    inputs.append([case,8,key,wait]);e.run(8,key);e.run(wait)

def capture(name):
    e.screenshot(out/(case+'-'+name+'.png'));e.save(out/(case+'-'+name+'.state'))
    for ext,address in [('ram',0x02000000),('iwram',0x03000000),('vram',0x06000000),('oam',0x07000000),('palette',0x05000000)]:
        (out/(case+'-'+name+'.'+ext)).write_bytes(C.string_at(*e.maps[address]))

try:
    for action,cost in ((365,6),(371,20)):
        if args.action and action!=args.action:continue
        lesson=next(x for x in registry['lessons'] if x['globalAbilityId']==action)
        learned=next(x['abilityIndex'] for x in lesson['owners'] if x['jobId']==118)
        for branch,path in [('active',Path(meta['path'])),('bypass',controlpath)]:
            case=f'{action}-{branch}';e=E(path)
            branch_stem=('candidate' if branch=='active' else 'control')+'-ready' if native_entry else stem
            e.load(source/(branch_stem+'.state'))
            branch_rom=path.read_bytes()
            check(e.memory()==(source/(branch_stem+'.ram')).read_bytes() and C.string_at(*e.maps[0x03000000])==(source/(branch_stem+'.iwram')).read_bytes(),'Exact own-ROM retained ready RAM/IWRAM')
            if args.reviewed_entry:
                check(e.memory()[0x3ff44:0x3ff4c]==b'\xd7'*8,'Cold-entry allocation fence retained before action fixture')
                e.set_memory(0x3ff44,bytes(8))
                inputs.append([case,'replace cold-entry allocation canaries with empty execution/action roots',0x0203ff44,8])
            actor_job=119 if args.secondary else 118
            identity=bytes((1,actor_job,2,actor_job))
            check(e.memory()[ACTOR+4:ACTOR+8]==identity,'Native generic caster identity already allocated')
            e.set_memory(ACTOR+0x40,bytes(144));e.set_memory(ACTOR+0x40+learned,b'\xff')
            e.set_memory(ACTOR+0x36,bytes((118 if args.secondary else 0,)));e.set_memory(ACTOR+0x3a,bytes(2))
            if args.secondary:
                # Native secondary-command commit stores the selection at+36
                # and C9078's resolved job at+8 (7DFD2..7DFE8). Both are part
                # of this declared loadout; neither changes the actor's body.
                e.set_memory(ACTOR+8,b'\x76')
                items=word(branch_rom,0x79aec)-0x08000000
                sword=next(i for i in range(1,461) if branch_rom[items+32*i+8]==2)
                e.set_memory(ACTOR+0x2a,struct.pack('<5H',sword,0,0,0,0))
            inputs.append([case,'sole learned native command',action,learned,'secondary',args.secondary,
                'secondary selection/cache',list(e.memory()[ACTOR+p] for p in (0x36,8))])
            for _ in range(12):
                if active()==0x02000000+ACTOR:break
                old=active()
                for key in (32,32,256,256):tap(key)
                for wait in range(0,6300,30):
                    if active()!=old and menus['menu_visible'](e):break
                    e.run(30)
                else:raise AssertionError('Preceding actor did not advance')
            check(active()==0x02000000+ACTOR,'Declared caster owns native turn')
            fixed_giza_formation(branch_rom,e);wrappers=from_emulator(branch_rom,e)
            for unit in (ACTOR,TARGET):
                e.set_memory(unit+0x18,struct.pack('<4H',500,500,100,100));e.set_memory(unit+0xe8,bytes(8))
            inputs.append([case,'existing fixed_giza_formation and declared HP500 MP100 no native ailments'])
            e.run(30);capture('ready')
            # Existing proven Move route refreshes native targeting:1,14->4,14.
            for key in (256,128,128,128,256):tap(key)
            menus['wait_for_menu'](e)
            check(half(e.memory(),wrappers[ACTOR]+8)==144,'Native Move reaches4,14')
            # Remaining selected command is Act; choose A1 or A2, sole spell.
            for key in ((256,32,32,256,256) if args.secondary else (256,32,256,256)):tap(key)
            r=e.memory();manager=word(r,0xf438)-0x02000000
            check(word(r,manager+20)==action,'Native command list selects exact spell')
            for key in (128,256,256):tap(key)
            before=e.memory();manager=word(before,0xf438)-0x02000000;capture('confirmation')
            check(before[manager+4]==11 and half(before,0xf3fc)==action,'Native target confirmation selects spell')
            check(half(before,ACTOR+0x1c)==100,'No premature MP debit')
            if action==371 and (native_entry or branch=='active' and 'nativeHighlightOffset' in live):
                base=live['ramReservation'][0]-0x02000000
                if not native_entry:
                    check(word(before,base+live['nativeHighlightOffset'])==1,'Native shared target palette recognized')
                    check(not any(struct.unpack_from('<4I',before,base+live['refusalOffset'])),'No refusal during native area targeting')
                from mgba_instruction_trace import InstructionTrace
                trace=InstructionTrace(e,{0x080012bc:'compose',0x080004dc:'composed'},
                    {pc:{'bank9':(0x05000320,32)} for pc in (0x080012bc,0x080004dc)})
                with trace:e.run(32)
                pending=None;pairs=0
                for event in trace.events:
                    if event['site']=='compose':pending=event['memory']['bank9']
                    elif pending is not None:
                        check(event['memory']['bank9']==pending,'Composition preserves every native highlight hardware color '+str(pairs));pairs+=1;pending=None
                check(pairs>=10,'Native highlight has repeated observed composition boundaries')
                (out/(case+'-highlight-events.json')).write_text(json.dumps(trace.events,indent=2)+'\n',encoding='utf-8')
                trace=None
                before=e.memory()
                tags=before[base+live['tagOffset']:base+live['tagOffset']+128]
                hardware=C.string_at(*e.maps[0x07000000])
                highlighted=[i for i in range(128) if half(hardware,i*8+4)>>12==9 and half(hardware,i*8)&0x300!=0x200]
                check(bool(highlighted) and (native_entry or all(tags[i]==255 for i in highlighted)),'Actual highlighted shapes use native bank9')
                capture('highlight-verified')
            C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',1),4);inputs.append([case,'native RNG',1])
            tap(256,0);samples=[];modes=set();seen_cast=set();min_free=0x40000;min_largest=0x40000;anchor=None
            base=live['ramReservation'][0]-0x02000000;slots=live['historySlots']
            if native_entry:
                from mgba_instruction_trace import InstructionTrace
                from native_oam_evidence import reconstruct
                trace=InstructionTrace(e,{0x080004dc:'native-composed'},
                    {0x080004dc:dict(main=(0x03000000,0x830),auxiliary=(0x03002c50,0x860),mode=(0x03000940,2),oam=(0x07000000,1024),palette=(0x05000000,1024))})
                trace.__enter__()
            elif args.reviewed_entry:
                from mgba_instruction_trace import InstructionTrace
                from native_oam_evidence import snapshot_ranges
                trace=InstructionTrace(e,{0x080004dc:'native-composed'},{0x080004dc:snapshot_ranges(live)})
                trace.__enter__()
            sample_step=1 if args.reviewed_entry else 4
            last_configured=None
            for frame in range(0,1800,sample_step):
                e.run(sample_step);r=e.memory();pal=C.string_at(*e.maps[0x05000000]);oam=C.string_at(*e.maps[0x07000000]);vram=C.string_at(*e.maps[0x06000000])
                h=heap(r);min_free=min(min_free,h['freePayload']);min_largest=min(min_largest,h['largestFree'])
                body=word(r,wrappers[ACTOR]+0x44)-0x02000000
                figures=actors(branch_rom,r,vram,{body})
                reset=False
                if not figures:
                    # Native21618 can start a different action sequence while
                    # clearing the live layout/source. Prove the retained old
                    # display; never count it as the newly selected cast pose.
                    flags,resource,mode,timer,index,count=struct.unpack_from('<I2x5H',r,body)
                    tile,alternate,allocation=struct.unpack_from('<3H',r,body+0x12)
                    first,current=struct.unpack_from('<II',r,body+0x34)
                    table=word(branch_rom,0x2102c)-0x08000000
                    descriptor=word(branch_rom,table+resource*4)-0x08000000+(mode&~3)*6+(12 if mode&3 in (1,2) else 0)
                    block=vram[0x10000+tile*32:0x10000+(tile+allocation)*32]
                    objects=[struct.unpack_from('<3H',oam,i*8) for i in range(128)]
                    hardware=[x for x in objects if x[0]&0x300!=0x200 and x[2]&1023==tile]
                    check(anchor is not None and frame-anchor['frame']<=4 and anchor['direct'],
                          'Short reset immediately follows direct native display '+str(frame))
                    # Native21E28 can select phase1 immediately after the
                    # return-to-idle constructor. This is still a retained
                    # display, never evidence that the new pose was uploaded.
                    initial=index==0 and current==first and word(r,body+0x28)==anchor['actor']['oam']
                    manual=flags==0x167 and mode==7 and index==1 and current==first+20 and count==4
                    if manual:
                        from native_art import OAM
                        manual=word(branch_rom,current-0x08000000+4)+OAM+0x08000000==word(r,body+0x28)
                    check(flags in (0x65,0x67,0x165,0x167) and timer==0 and (initial or manual) and
                          word(r,body+0x20)==0xffffffff and word(r,body+0x2c)==0 and
                          word(branch_rom,descriptor)+4==first and word(branch_rom,first-0x08000004)==count,
                          'Exact native initial sequence/reset contract '+str(frame))
                    pixels_exact=block==anchor['block'];geometry_exact=hardware==anchor['hardware']
                    if args.reviewed_entry and not (pixels_exact and geometry_exact):
                        from native_oam_evidence import shapes_at_composition
                        geometry_exact=shapes_at_composition(live,branch_rom,trace.events[-1],oam,check)['nativeShapes']
                        old=last_configured['actor'] if last_configured and 0<frame-last_configured['frame']<=4 else anchor['actor']
                        q=old['first']-0x08000000;old_count=word(branch_rom,q-4)
                        if not pixels_exact and old['flags']&0x120000 and 0<old['index']<=old_count and old['current']==old['first']+20*min(old['index'],old_count-1):
                            command=q+20*(old['index']-1)
                            from native_art import TILES,OAM,layout
                            t,o=struct.unpack_from('<II',branch_rom,command)
                            if branch_rom[command+9]==1 and t==old['tileOffset'] and OAM+0x08000000+o==old['oam']:
                                parts,_=layout(branch_rom,OAM+o);size=sum(p['width']*p['height']//64 for p in parts)*32
                                pixels_exact=size==old['tileCount']*32 and size<=allocation*32 and block==branch_rom[TILES+t:TILES+t+size]+anchor['block'][size:]
                    if not ((resource,tile,allocation)==anchor['identity'] and pixels_exact and geometry_exact):
                        (out/(case+'-reset-diagnostic.json')).write_text(json.dumps(dict(frame=frame,anchorFrame=anchor['frame'],actor=anchor['actor'],identity=[resource,tile,allocation],anchorIdentity=anchor['identity'],priorPixels=sha(anchor['block']),currentPixels=sha(block),geometryExact=geometry_exact,pixelsExact=pixels_exact),indent=2)+'\n')
                    check((resource,tile,allocation)==anchor['identity'] and pixels_exact and geometry_exact,
                          'Reset retains exact previously displayed pixels layout and hardware '+str(frame))
                    a=dict(anchor['actor'],mode=mode,first=first,current=current,displayedFrames=[]);reset=True
                else:
                    check(len(figures)==1,'Native caster body remains allocated '+str(frame));a=figures[0]
                    tile,allocation=a['tile'],a['allocation'];objects=[struct.unpack_from('<3H',oam,i*8) for i in range(128)]
                    block=vram[0x10000+tile*32:0x10000+(tile+allocation)*32]
                    if args.reviewed_entry and not a['displayedFrames']:
                        from native_body_display import pending_from_anchor,completed_pending_facing
                        hold=pending_from_anchor(a,block,anchor,frame-anchor['frame']) if anchor else None
                        if not hold and anchor:hold=completed_pending_facing(branch_rom,a,block,anchor,frame-anchor['frame'])
                        check(bool(hold),'Exact bounded queued caster display '+str(frame))
                    if a['displayedFrames'] or not args.reviewed_entry:
                        anchor=dict(frame=frame,direct=bool(a['displayedFrames']),actor=a,first=a['first'],index=a['index'],
                            identity=(a['resource'],tile,allocation),block=block,
                            hardware=[x for x in objects if x[0]&0x300!=0x200 and x[2]&1023==tile])
                    last_configured=dict(frame=frame,actor=a)
                modes.add(a['mode'])
                check(a['resource']==256+2*(actor_job-116) and a['declaredSequence'] and a['expectedTiles']==a['tileCount']<=a['allocation'],
                      'Caster selects owned bounded native sequence '+str(frame))
                if a['mode']>=8 and a['displayedFrames']:
                    if a['mode'] not in seen_cast:capture('caster-mode-'+str(a['mode']))
                    seen_cast.add(a['mode'])
                state=dict(frame=frame+sample_step,mode=a['mode'],directDisplayed=bool(a['displayedFrames']),nativeLayoutReset=reset,free=h['freePayload'],largest=h['largestFree'])
                if native_entry:
                    event=trace.events[-1];memory=event['memory'];iw=bytearray(0x8000)
                    for name,p in [('main',0),('auxiliary',0x2c50),('mode',0x940)]:
                        raw=bytes.fromhex(memory[name]);iw[p:p+len(raw)]=raw
                    expected,counts=reconstruct(branch_rom,iw)
                    check(expected==oam==bytes.fromhex(memory['oam']),'Complete native OAM at actual composition boundary '+str(frame))
                    check(pal==bytes.fromhex(memory['palette']),'Actual native hardware palette '+str(frame))
                    state.update(paletteSha256=sha(pal),oamSha256=sha(oam),nativeObjects=counts)
                elif branch=='active':
                    refused=struct.unpack_from('<4I',r,base+live['refusalOffset'])
                    unsupported=word(r,base+live['bindingOffset']+live['bindingCounterOffset']+8)
                    check(not any(refused) and unsupported==0 and word(r,base+2584)==0,'No palette allocation/effect refusal '+str(frame))
                    tags=r[base+live['tagOffset']:base+live['tagOffset']+128];visible=r[base+live['visibleColorsOffset']:base+live['visibleColorsOffset']+slots*32]
                    owned=[]
                    for index,slot in enumerate(tags):
                        if slot>=slots:continue
                        aa,bb,cc=struct.unpack_from('<3H',oam,index*8)
                        if aa&0x300==0x200:continue
                        bank=cc>>12
                        check(pal[512+bank*32:544+bank*32]==visible[slot*32:slot*32+32],'Actual owned hardware palette equals computed visible effect colors '+str((frame,index)))
                        owned.append(bank)
                    check(bool(owned),'Generated bodies remain displayed during cast '+str(frame));state['banks']=owned
                samples.append(state)
            if trace:
                trace.__exit__(None,None,None)
                (out/(case+'-composition-events.json')).write_text(json.dumps(trace.events,indent=2)+'\n',encoding='utf-8')
                trace=None
            after=e.memory();capture('executed')
            check(bool(seen_cast),'A non-idle native casting/body phase actually reaches VRAM')
            check(100-half(after,ACTOR+0x1c)==cost,'Exactly one native spell MP payment')
            check(0<500-half(after,TARGET+0x18)<500,'Spell deals bounded positive native damage')
            check(after[0x1940:0x1e70]==before[0x1940:0x1e70] and after[ACTOR+0x40:ACTOR+0xd0]==before[ACTOR+0x40:ACTOR+0xd0],
                  'Inventory AP and learning unchanged')
            check(after[0x3ff44:0x3ff4c]==bytes(8),'Action roots retired')
            check(after[ACTOR+4:ACTOR+8]==identity,'Caster class identity preserved through execution')
            old=active();tap(256,900)
            for wait in range(0,6300,30):
                if active()!=old and menus['menu_visible'](e):break
                e.run(30)
            else:raise AssertionError('Following native turn missing')
            capture('returned')
            results.append(dict(action=action,branch=branch,damage=500-half(after,TARGET+0x18),mp=half(after,ACTOR+0x1c),
                modes=sorted(modes),displayedCastModes=sorted(seen_cast),minFreeBytes=min_free,minLargestBlock=min_largest,samples=samples))
            e.close();e=None
        left,right=results[-2:]
        check((left['damage'],left['mp'])==(right['damage'],right['mp']),'Paired composition control preserves exact cast outcome')
        if native_entry:
            for i,(a,b) in enumerate(zip(left['samples'],right['samples'])):
                check(all(a[k]==b[k] for k in ('frame','mode','paletteSha256','oamSha256')),'Exact paired native action mode, palette and OAM sample '+str(i))
    check(seed.read_bytes()==seedbytes,'Source state unchanged')
    check((source/(stem+'.ram')).read_bytes()==ram0 and (source/(stem+'.iwram')).read_bytes()==iw0,'Source ready memory captures unchanged')
    report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,inputs=inputs,results=results,
        source=dict(path=str(seed),sha256=sha(seedbytes)),control=dict(sha1=hashlib.sha1(control).hexdigest(),restore=patch),
        scope='Selected actual Bangaa Viking spell(s) listed in results from exact-ROM mixed ready state through native Move/menu/target/cast/next turn, paired composition-only control, bounded owned caster sequences and positive non-idle VRAM, palette refusal/visible-buffer hardware checks, HP/MP/AP and sampled live heap. Four-frame samples. Does not independently prove every transformed color, unsampled frame, other casting families, maximum encounter capacity or final animation artwork.')
    if evidence:report['readyEvidence']=dict(path=str(args.ready_evidence),sha256=sha(args.ready_evidence.read_bytes()),pins=evidence)
    if args.reviewed_entry:
        report['sampleIntervalFrames']=1
        report['scope']=report['scope'].replace('Four-frame samples.','Every-frame samples.').replace('unsampled frame, ','')
    if native_entry:
        for path,digest in source_pins.items():check(sha(Path(path).read_bytes())==digest,'Preserved source '+path)
        report.update(nativeEntry=dict(path=str(entry_path),pins=source_pins),secondary=args.secondary,
            control=dict(path=str(controlpath),sha1=hashlib.sha1(control).hexdigest(),entryControl=native_entry['control']),
            scope='Selected primary Viking or secondary Viking Arts on a preallocated Bangaa Dark Knight, declared native Move/menu/target/cast/next turn and HP/MP/AP checks. Each branch uses its own fresh native-renderer ROM/state. Exact bounded caster sequences, non-idle uploads, complete native OAM and hardware palettes at four-frame samples, paired raw mode/OAM/palette equality; Thundaga also observes native target bank9. Reuses prior gameplay/action graph evidence. Does not cover unsampled frames, all other effect families, maximum encounters or final artwork.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    if e and e.frame:capture('failed')
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),checks=checks,inputs=inputs,results=results,samples=samples),indent=2)+'\n',encoding='utf-8')
    print('Artifacts: '+str(out));raise
finally:
    if trace:trace.__exit__(None,None,None)
    if e:e.close()
