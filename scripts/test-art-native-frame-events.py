"""Observe native scheduling at two fixed input phases without changing execution.

Every observed action frame must match ordinary retro_run's complete native
state and framebuffer. The compositor-bypass ROM is a private diagnostic.
"""
import ctypes as C
import argparse
import datetime
import hashlib
import json
import runpy
import struct
from pathlib import Path
from native_art import ROOT, sha
from native_battle_wrappers import from_emulator
from mgba_instruction_trace import InstructionTrace, DLL_SHA256

SOURCE = ROOT/'build/art/live-palette/battle/20260918T183919.610099Z'
META = ROOT/'build/art/connected/4a7d55ce09cd4a40965a0bb97de2701d276789c5/live-palette-view.json'
PINS = {
    'candidate-ready.state': 'a0208a9a4721b41afa45a760007a90b694d3c7aa20023689d944bea59ba641d3',
    'candidate-ready.ram': '0a0de57cd3ee8b617475b572b856b2181628eed8ed0e120af93451394f642018',
    'candidate-ready.iwram': '6ab0ad9dd121fc844eb9aaa15f184ee83ba4f1ebdb8cd9b5109ad433f686ada4',
}
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--candidate-manifest', type=Path)
parser.add_argument('--retained-report', type=Path)
parser.add_argument('--legacy-plan-control', action='store_true',
                    help='Keep composition enabled; redirect only scene_apply to the original live planner.')
parser.add_argument('--foreground-events', action='store_true',
                    help='Also observe native foreground stages and paired scheduler callbacks.')
parser.add_argument('--battle-stages', action='store_true',
                    help='Observe the individual calls inside the measured battle update/render callbacks.')
parser.add_argument('--palette-events', action='store_true',
                    help='Capture native palette shadow/hardware around actual composition and DMA decisions.')
parser.add_argument('--graphics-inputs',action='store_true',
                    help='Observe exact native OAM/OBJ input changes and Thumb OBJ writes; no cache assumption.')
parser.add_argument('--composition-costs',action='store_true',
                    help='Authenticate compiled call/return sites and measure inclusive costs without changing execution.')
parser.add_argument('--scoped-costs',action='store_true',
                    help='Separate standard scoped ARM wrapper copy and leaf execution with read-only host observation.')
parser.add_argument('--controller-costs',action='store_true',
                    help='Profile actual direct native battle-controller calls; inclusive costs, no code changes.')
parser.add_argument('--movement-costs',action='store_true',
                    help='Include authenticated Geomancer tile callback children in controller profiling.')
args = parser.parse_args()
if args.scoped_costs:args.composition_costs=True
if args.movement_costs:args.controller_costs=True
if args.graphics_inputs:
    from art_graphics_trace import GraphicsTrace,GRAPHICS_SITES
    InstructionTrace=GraphicsTrace
assert bool(args.candidate_manifest) == bool(args.retained_report)
assert not args.legacy_plan_control or args.candidate_manifest
assert not args.battle_stages or args.foreground_events
candidate_sha1 = '4a7d55ce09cd4a40965a0bb97de2701d276789c5'
if args.candidate_manifest:
    META, SOURCE = args.candidate_manifest, args.retained_report.parent
    retained = json.loads(args.retained_report.read_text(encoding='utf-8'))
    assert retained['status'] in ('passed', 'failed')
    candidate_sha1 = retained['romSha1']
    PINS = {name: sha((SOURCE/name).read_bytes()) for name in
            ('candidate-ready.state', 'candidate-ready.ram', 'candidate-ready.iwram', args.retained_report.name)}
SITES = {
    0x08000460: 'draw', 0x080004b0: 'vblank',
    0x0800221c: 'input', 0x08000498: 'input-return',
    0x080069f4: 'dispatch', 0x080012bc: 'compose',
    0x080004dc: 'compose-return', 0x08000788: 'display-end',
    0x080003fa: 'foreground-clear-fast', 0x08000416: 'foreground-clear',
    0x0800042e: 'foreground-return', 0x080004c8: 'vblank-flag-check',
    0x080004fa: 'vblank-display-return',
}
if args.foreground_events:
    SITES.update({
        0x08000468: 'draw-reset-return', 0x0800046c: 'draw-prepare-return',
        0x08000476: 'draw-dispatch-return', 0x0800047a: 'draw-rng-return',
        0x08000482: 'draw-banks-return', 0x08000522: 'vblank-return',
        0x08006a34: 'task-call', 0x08006a38: 'task-return',
        0x08006a6a: 'single-task-call', 0x08006a6e: 'single-task-return',
        0x08006a74: 'dispatch-return',
    })
if args.battle_stages:
    SITES.update({
        0x08096e8c: 'battle-reset-call', 0x08096e90: 'battle-reset-return',
        0x08096ea0: 'battle-state-call', 0x08096ea4: 'battle-state-return-and-particles-call',
        0x08096ea8: 'battle-particles-return-and-effects-call',
        0x08096eac: 'battle-effects-return',
        0x08096eb4: 'battle-units-call', 0x08096eb8: 'battle-units-return',
        0x08096eba: 'battle-ui-call', 0x08096ebe: 'battle-ui-return',
        0x080231f8: 'render-ui-call', 0x080231fc: 'render-ui-return',
        0x08023208: 'render-units-call', 0x0802320c: 'render-units-return-and-effects-call',
        0x08023210: 'render-effects-return-and-flush-call',
        0x08023214: 'render-flush-return',
    })
SNAPSHOTS = {pc: {'shadow': (0x03003860,1024), 'palette': (0x05000000,1024)}
             for pc in (0x080004c8,0x080012bc,0x080004dc)} if args.palette_events else {}
NAVIGATION = [[8, key, 180] for key in (256, 128, 128, 128)]
ACTIONS = [('move', 256, 48, 144), ('cancel', 1, 144, 48)]
out = ROOT/'build/art/native-frame-events'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True)
checks, records = [], []
e = None
trace = None


def check(ok, label):
    assert ok, label
    checks.append(label)


def frame_hash(frame):
    raw, width, height, pitch, pixel = frame
    return sha(struct.pack('<4I', width, height, pitch, pixel)+raw)


def motion(rows, initial, target):
    positions = [row['position'] for row in rows]
    started = next(i for i, p in enumerate(positions) if p[0] != initial)
    arrived = next(i for i, p in enumerate(positions) if p[0] == target)
    changes = [i for i in range(1, len(rows)) if positions[i] != positions[i-1]]
    return dict(start=started, end=arrived, elapsed=arrived-started,
                changes=changes, positions=[positions[i] for i in changes])


try:
    for name, digest in PINS.items():
        check(sha((SOURCE/name).read_bytes()) == digest, 'Pinned source '+name)
    meta = json.loads(META.read_text(encoding='utf-8'))
    if meta.get('repeatFrame'):
        assert not args.graphics_inputs,'Separate exact repeat audit from generic graphics-writer tracing'
        from art_repeat_trace import RepeatTrace
        InstructionTrace=lambda emulator,sites,snapshots:RepeatTrace(emulator,sites,snapshots,meta)
    if meta.get('fusedCompose'):
        assert not args.graphics_inputs and not meta.get('repeatFrame')
        from art_fused_trace import FusedTrace
        InstructionTrace=lambda emulator,sites,snapshots:FusedTrace(emulator,sites,snapshots,meta)
    rom = Path(meta['path']).read_bytes()
    arm_cost_sites={}
    if args.scoped_costs:
        from art_scoped_costs import boundaries as scoped_boundaries,ScopedTrace
        arm_cost_sites,scoped_proof,scoped_executions=scoped_boundaries(meta,rom)
        InstructionTrace=lambda emulator,sites,snapshots:ScopedTrace(emulator,sites,snapshots,meta,arm_cost_sites,scoped_executions)
    cost_boundaries=[]
    if args.controller_costs:
        from art_controller_costs import boundaries as controller_boundaries, summarize as controller_summary
        controller_events,controller_proof=controller_boundaries(rom,movement=args.movement_costs)
        assert not set(controller_events)&set(SITES),'Unique native controller observer sites'
        SITES.update(controller_events)
    if args.composition_costs:
        from art_composition_costs import cost_sites,summarize_costs
        cost_events,cost_boundaries=cost_sites(meta,rom)
        assert not set(cost_events)&set(SITES),'Unique observer addresses'
        SITES.update(cost_events)
    check(hashlib.sha1(rom).hexdigest() == meta['romSha1'] == candidate_sha1,
          'Exact retained-state ROM and report, including serialized actor pointers')
    change = next(x for x in meta['changes'] if x['offset'] == 0x12bc)
    check(rom[0x12bc:0x12c4].hex() == change['after'] and
          change['before'] == 'f0b557464e464546', 'Authenticated compositor entry')
    if meta.get('nativeOamPrefix'):
        check(sha(bytes.fromhex(change['before'])+rom[0x12c4:0x14c8])=='9b66e36f26b094d61539c4790834bd83d102e90433cf5b7e443c268cabbf8c64',
              'Exact native producer including sentinel fill, four DMA clips and affine-only tail updates')
        pc=meta['symbols']['ffta_art_palette_live_apply_prefix']&~1
        assert pc not in SITES
        SITES[pc]='native-prefix-apply'
        SNAPSHOTS[pc]={'oam':(0x07000000,1024),'tags':(meta['ramReservation'][0]+meta['tagOffset'],128),
            'main':(0x03000020,12),'front':(0x03002c50,8),
            'ui':(0x03002f58,16),'tail':(0x03003168,8)}
        if meta.get('fusedCompose'):
            fused_pc=meta['symbols']['ffta_art_palette_live_apply_fused']&~1
            assert fused_pc not in SITES
            SITES[fused_pc]='native-fused-apply'
            SNAPSHOTS[fused_pc]=SNAPSHOTS[pc]
    owner_returns={}
    if meta.get('nativeOwnerProducer'):
        assert meta.get('nativeOamPrefix') and args.composition_costs,'Native producer requires the complete call-boundary audit'
        pc=meta['symbols']['ffta_art_owners_compose_native']&~1
        assert pc not in SITES
        SITES[pc]='native-owner-input'
        SNAPSHOTS[pc]={'oam':(0x07000000,1024),'sources':(0x03000030,2048),
            'owners':(meta['ramReservation'][0]+4,2056),'main':(0x03000020,12),
            'front':(0x03002c50,8),'ui':(0x03002f58,16),'tail':(0x03003168,8)}
        boundaries=[row for row in cost_boundaries if row['caller']=='ffta_art_live_compose' and row['callee']=='ffta_art_owners_compose_native']
        assert len(boundaries)==1
        owner_return=boundaries[0]['returnPC']
        owner_returns[pc]=owner_return
        SNAPSHOTS[owner_return]={'tags':(meta['ramReservation'][0]+meta['tagOffset'],128)}
        if meta.get('fusedCompose'):
            fused_pc=meta['symbols']['ffta_art_owners_compose_fused']&~1
            assert fused_pc not in SITES
            SITES[fused_pc]='native-owner-input'
            SNAPSHOTS[fused_pc]=SNAPSHOTS[pc]
            boundaries=[row for row in cost_boundaries if row['caller']=='ffta_art_live_compose' and row['callee']=='ffta_art_owners_compose_fused']
            assert len(boundaries)==1
            owner_returns[fused_pc]=boundaries[0]['returnPC']
            SNAPSHOTS[boundaries[0]['returnPC']]=SNAPSHOTS[owner_return]
    bypass = bytearray(rom)
    if args.legacy_plan_control:
        check(meta.get('planReuse') is True, 'Scene-reuse control requires matching candidate ABI')
        site = meta['symbols']['ffta_art_palette_scene_apply']-0x08000000
        target = meta['symbols']['ffta_art_palette_live_apply']
        check(site%4 == 0 and meta['used'][0]<=site<site+8<=meta['used'][1]
              and meta['used'][0]<=target-0x08000000<meta['used'][1]
              and struct.unpack_from('<H', rom, site)[0]&0xfe00 == 0xb400,
              'Authenticated aligned Thumb scene_apply and original live planner')
        patch = dict(offset=site, before=rom[site:site+8].hex(),
                     after=struct.pack('<HHI',0x4b00,0x4718,target|1).hex())
        control_name = 'legacy'
    else:
        patch = dict(offset=0x12bc, before=change['after'], after=change['before'])
        control_name = 'bypass'
    site = patch['offset']
    bypass[site:site+8] = bytes.fromhex(patch['after'])
    check(bypass[:site] == rom[:site] and bypass[site+8:] == rom[site+8:],
          'Only authenticated eight-byte control entry changed')
    control = out/(control_name+'-control.gba')
    control.write_bytes(bypass)
    E = runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
    for case, path in [('active', Path(meta['path'])), (control_name, control)]:
        for delay in (0, 4):
            label = case+'/idle-'+str(delay)
            e = E(path)
            e.load(SOURCE/'candidate-ready.state')
            check(e.memory() == (SOURCE/'candidate-ready.ram').read_bytes() and
                  C.string_at(*e.maps[0x03000000]) == (SOURCE/'candidate-ready.iwram').read_bytes(),
                  label+' exact restored RAM/IWRAM')
            wrapper = from_emulator(rom, e)[0x290]
            canonical = e.memory()[0x80:0x1e70]
            for press, key, wait in NAVIGATION:
                e.run(press, key)
                e.run(wait)
            e.run(delay)
            start = C.create_string_buffer(e.core.retro_serialize_size())
            assert e.core.retro_serialize(start, len(start))
            trace = InstructionTrace(e, SITES, SNAPSHOTS)
            initial_native = trace.state()
            baseline = []
            first_native = None
            keys = [key if i < 8 else 0 for _, key, _, _ in ACTIONS for i in range(128)]
            for key in keys:
                e.run(1, key)
                native = trace.state()
                if first_native is None:
                    first_native = native
                baseline.append((sha(native), frame_hash(e.frame)))
            # State restoration can rebase pending audio events in an already
            # advanced core. Both branches start with a fresh core, the same
            # retained seed and identical navigation; do not normalize bytes.
            e.close()
            e = E(path)
            e.load(SOURCE/'candidate-ready.state')
            for press, key, wait in NAVIGATION:
                e.run(press, key)
                e.run(wait)
            e.run(delay)
            trace = InstructionTrace(e, SITES, SNAPSHOTS)
            restored_native = trace.state()
            if args.graphics_inputs and meta.get('dmaTileCache'):
                cache=meta['ramReservation'][0]-0x02000000+meta['visibleColorsOffset']+meta['historySlots']*32
                trace.dirty_cache_pointer=e.maps[0x02000000][0]+cache
            if restored_native != initial_native:
                (out/'before-restore.state').write_bytes(initial_native)
                (out/'after-restore.state').write_bytes(restored_native)
            check(restored_native == initial_native, label+' identical navigation reproduces complete action-start state')
            actions = {}
            with trace:
                for action_index, (action, key, initial, target) in enumerate(ACTIONS):
                    rows = []
                    event_start = len(trace.events)
                    for tick in range(128):
                        before = trace.cycles()
                        frame = trace.frame_counter(trace.core)
                        pressed = key if tick < 8 else 0
                        e.run(1, pressed)
                        state = trace.state()
                        expected = baseline[action_index*128+tick]
                        if (sha(state), frame_hash(e.frame)) != expected:
                            (out/(label.replace('/', '-')+'-mismatch.state')).write_bytes(state)
                            (out/'first-normal.state').write_bytes(first_native)
                            (out/'mismatch.json').write_text(json.dumps(dict(expected=expected,
                                actual=[sha(state), frame_hash(e.frame)], action=action, tick=tick), indent=2)+'\n', encoding='utf-8')
                        check((sha(state), frame_hash(e.frame)) == expected,
                              label+'/'+action+' frame '+str(tick)+' entire state and framebuffer identical')
                        ram = e.memory()
                        rows.append(dict(tick=tick, input=pressed, videoFrame=frame,
                            startCycle=before, endCycle=trace.cycles(),
                            position=list(struct.unpack_from('<3H', ram, wrapper+8))))
                        if meta.get('planReuse'):
                            rows[-1]['reuseCounters'] = list(struct.unpack_from('<2I', ram,
                                meta['ramReservation'][0]-0x02000000+meta['planReuseOffset']+940))
                        if meta.get('repeatFrame'):
                            rows[-1]['repeatCounters']=list(struct.unpack_from('<3I',ram,
                                meta['ramReservation'][0]-0x02000000+meta['repeatOffset']))
                    check(rows[-1]['position'] == [target, 32, 432], label+'/'+action+' native target reached')
                    check(ram[0x80:0x1e70] == canonical, label+'/'+action+' canonical player records unchanged')
                    actions[action] = dict(motion=motion(rows, initial, target), frames=rows,
                                           events=trace.events[event_start:])
                    if args.scoped_costs:
                        events=actions[action]['events']
                        measured=summarize_costs(events)['calls']
                        for stem in ('fused_owners','publish'):
                            name='ffta_art_frame_'+stem
                            pairs=[]
                            for phase in ('copy','execute'):
                                spans=[v for k,v in measured.items() if k.startswith(name+'/'+phase+'@')]
                                check(len(spans)==(1 if case=='active' else 0),label+'/'+action+'/'+name+'/'+phase+' observed path')
                                pairs.append(spans[0] if spans else [])
                                check(len(pairs[-1])==(128 if case=='active' else 0),label+'/'+action+'/'+name+'/'+phase+' every actual frame')
                            check([r['videoFrame'] for r in pairs[0]]==[r['videoFrame'] for r in pairs[1]],label+'/'+action+'/'+name+' copy/execute frame pairing')
                        check(not any('/fallback@' in k for k in measured),label+'/'+action+' no ROM fallback in this scenario; fallback timing not covered')
                        check(sum('copiedLeafSha256' in x for x in events)==(256 if case=='active' else 0),label+'/'+action+' exact executed IWRAM bytes for every scoped leaf')
                    if meta.get('repeatFrame'):
                        events=actions[action]['events']
                        proofs=[x for x in events if x['site']=='repeat-key-proof']
                        applies=[x for x in events if x['site']=='validated-repeat-apply']
                        check(len(proofs)==len(applies),label+'/'+action+' every repeat entry audited against exact current inputs')
                        check(all(x.get('completeFootprint') for x in proofs),label+'/'+action+' independently complete ordered pixel footprint at every repeat entry')
                        if meta.get('repeatKeyVersion')==2:check(all(x.get('freshOwners') for x in proofs),label+'/'+action+' independently reconstructed native ownership at every repeat entry')
                        if case=='active':check(len(proofs)>0,label+'/'+action+' actual repeat fast path exercised')
                    if args.graphics_inputs:
                        graphics=[x for x in actions[action]['events'] if x['site']=='graphics-inputs']
                        check(len(graphics)==128,label+'/'+action+' all graphics inputs observed')
                        if meta.get('dmaTileCache'):
                            check(all('dirtyCache' in x for x in graphics),label+'/'+action+' dirty-cache audit ran at every graphics boundary')
                    if args.palette_events:
                        events=actions[action]['events']
                        decisions=[x for x in events if x['site']=='vblank-flag-check']
                        starts=[x for x in events if x['site']=='compose']
                        ends=[x for x in events if x['site']=='compose-return']
                        check(len(decisions)==len(starts)==len(ends)==128,
                              label+'/'+action+' all native DMA/composition boundaries captured')
                        for tick,(decision,before,after) in enumerate(zip(decisions,starts,ends)):
                            prefix=label+'/'+action+'/'+str(tick)
                            check(decision['videoFrame']==before['videoFrame']==after['videoFrame'],
                                  prefix+' same native frame boundary')
                            check(before['memory']['shadow']==after['memory']['shadow'],
                                  prefix+' complete native palette shadow unchanged by composition')
                            check(before['memory']['palette'][:1024]==after['memory']['palette'][:1024],
                                  prefix+' every native background hardware color unchanged by composition')
                            expected=decision['memory']['palette'][:1024] if decision['frameFlag'] else before['memory']['shadow'][:1024]
                            check(before['memory']['palette'][:1024]==expected,
                                  prefix+' actual native fresh-or-skipped background DMA phase retained')
                    if meta.get('nativeOamPrefix'):
                        applies=[x for x in actions[action]['events'] if x['site'] in ('native-prefix-apply','native-fused-apply')]
                        check(len(applies)==(128 if case=='active' else 0),label+'/'+action+' every actual prefix apply independently observed')
                        if meta.get('fusedCompose') and case=='active':
                            check(any(x['site']=='native-fused-apply' for x in applies),label+'/'+action+' actual fused consumer exercised')
                        for index,event in enumerate(applies):
                            mem={k:bytes.fromhex(v) for k,v in event['memory'].items()}
                            bank=mem['main'][8]^1;other=mem['ui'][0]^1
                            check(bank in (0,1) and other in (0,1),label+'/'+action+' valid current producer buffers')
                            main=struct.unpack_from('<I',mem['main'],bank*4)[0]
                            front=struct.unpack_from('<I',mem['front'],bank*4)[0]
                            ui=struct.unpack_from('<I',mem['ui'],8+other*4)[0]
                            tail=struct.unpack_from('<I',mem['tail'],other*4)[0]
                            check(front<=48 and ui<=32 and main<=128 and tail<=16,label+'/'+action+' current bounded producer counters')
                            expected=min(128,front+min(ui,max(0,128-main-front))+main+tail)
                            count=struct.unpack('<I',mem['extent'])[0] if event['site']=='native-fused-apply' else event['registers'][3]
                            check(count==expected,label+'/'+action+' passed count matches current native producer extent')
                            check(all(mem['oam'][i*8:i*8+6]==bytes.fromhex('a800f8000000') and mem['tags'][i]==255 for i in range(count,128)),
                                  label+'/'+action+' complete omitted tail independently proves unowned bank0 sentinels')
                            if event['site']=='native-fused-apply':
                                frame=struct.unpack('<8I',mem['frame'])
                                check(frame[:4]==(0x07000000,0x06010000,meta['ramReservation'][0]+meta['tagOffset'],0x05000200) and frame[7]==meta['historySlots'],label+'/'+action+' actual fused planner current frame arguments')
                                occupied=requested=0;indices=[];valid=True
                                for i in range(count):
                                    a,b,c=struct.unpack_from('<3H',mem['oam'],i*8)
                                    if a&0x300==0x200:continue
                                    if a>>14==3:valid=False;continue
                                    owner=mem['tags'][i]
                                    if owner!=255:
                                        if owner>=frame[7] or a&0xe100 or b>>14!=2:valid=False
                                        else:requested|=1<<owner
                                    elif a&0x2000:indices.append(i)
                                    else:occupied|=1<<(c>>12)
                                actual=struct.unpack_from('<3I',mem['demands'])
                                check(actual==(occupied,requested,len(indices) if valid else 129),label+'/'+action+' prepared demands equal independent current OAM and mapped history classification')
                                check(mem['demands'][12:12+len(indices)]==bytes(indices),label+'/'+action+' every current 8bpp demand present in exact native order')

                    if meta.get('nativeOwnerProducer'):
                        inputs=[x for x in actions[action]['events'] if x['site']=='native-owner-input']
                        outputs=[x for x in actions[action]['events'] if x['pc'] in owner_returns.values()]
                        check(len(inputs)==len(outputs)==(128 if case=='active' else 0),label+'/'+action+' every producer-dependent ownership invocation captured')
                        for before,after in zip(inputs,outputs):
                            mem={k:bytes.fromhex(v) for k,v in before['memory'].items()}
                            check(after['pc']==owner_returns[before['pc']],label+'/'+action+' matching actual native or fused ownership return')
                            check(before['videoFrame']==after['videoFrame'] and before['cycle']<after['cycle'],label+'/'+action+' exact ownership call interval')
                            check(before['registers'][:4]==[meta['ramReservation'][0]+4,0x03000000,0x07000000,meta['ramReservation'][0]+meta['tagOffset']],label+'/'+action+' actual native ownership arguments')
                            bank=mem['main'][8]^1;other=mem['ui'][0]^1
                            check(bank in (0,1) and other in (0,1),label+'/'+action+' selected source bank valid')
                            main=struct.unpack_from('<I',mem['main'],bank*4)[0];front=struct.unpack_from('<I',mem['front'],bank*4)[0]
                            ui=struct.unpack_from('<I',mem['ui'],8+other*4)[0]
                            tail=struct.unpack_from('<I',mem['tail'],other*4)[0]
                            check(main<=128 and front<=48 and ui<=32 and tail<=16 and struct.unpack_from('<I',mem['owners'],2048+bank*4)[0]==0x4152544f,label+'/'+action+' bounded initialized current owner bank')
                            offset=front+min(ui,max(0,128-main-front));shown=min(main,128-offset)
                            expected=bytearray([255]*128)
                            for index in range(shown):
                                source=mem['sources'][bank*1024+index*8:bank*1024+index*8+6]
                                check(mem['oam'][(offset+index)*8:(offset+index)*8+6]==source,label+'/'+action+' native producer proves every copied main attr0..2')
                                record=mem['owners'][bank*1024+index*8:bank*1024+index*8+8]
                                if record[6]<10 and record[:6]==source:expected[offset+index]=record[6]
                            mask=sum(1<<owner for owner in set(expected) if owner<10)
                            check(bytes.fromhex(after['memory']['tags'])==expected and after['registers'][0]==mask,label+'/'+action+' all fresh native owner tags and requested classes exact')
            check(trace.slot.value == trace.original, label+' original host table restored')
            records.append(dict(case=case, idleFramesBeforeMove=delay,
                actionStartStateSha256=sha(start.raw), hostRvas=trace.host_rvas, actions=actions))
            e.close()
            e = None
            print(json.dumps(dict(case=label, motion={k: {f: v['motion'][f] for f in
                ('start', 'end', 'elapsed')} for k, v in actions.items()})), flush=True)
    for action, _, _, _ in ACTIONS:
        reference = records[0]['actions'][action]['motion']['positions']
        for record in records:
            check(record['actions'][action]['motion']['positions'] == reference,
                  str((record['case'], record['idleFramesBeforeMove'], action))+' same ordered logical movement')
    for name, digest in PINS.items():
        check(sha((SOURCE/name).read_bytes()) == digest, 'Source remains unchanged '+name)
    report = dict(status='passed', checks=checks, romSha1=meta['romSha1'],
        coreSha256=DLL_SHA256, controlSha1=hashlib.sha1(bypass).hexdigest(),
        controlPatch=patch, controlKind=control_name,
        source=str(SOURCE), inputHashes=PINS,
        manifestSha256=sha(META.read_bytes()),
        eventSites={**SITES,**arm_cost_sites,**(GRAPHICS_SITES if args.graphics_inputs else {})},
        memorySnapshots=SNAPSHOTS,
        navigation=NAVIGATION, actionInputs=[[8, key, 120] for _, key, _, _ in ACTIONS],
        records=records, scope='Two fixed input phases in one exact-ROM mixed battle. Host instruction observation must match every complete native state and framebuffer against normal emulation in all Move/cancel frames. Control bypasses only class composition and is not playable acceptance. Raw native event timing retained; no phase normalization, final timing acceptance, new fixture or production change.')
    if args.legacy_plan_control:
        report['scope'] = 'Two fixed input phases in one exact-ROM mixed battle. Control redirects only scene_apply to the same ROM original live planner, retaining all native/custom composition; tiny Thumb jump overhead remains. Every observed complete native state and framebuffer equals its ordinary-emulation replay. Raw input/phase/timing retained. No scene-entry, final timing or art acceptance.'
    if args.graphics_inputs:
        report['scope']+=' Exact OAM/OBJ and visible8bpp byte lifetimes plus Thumb word/halfword writes observed. ARM/BIOS/other store forms are not complete writer coverage. For dmaTileCache candidates, every valid cached tile mask is checked against all current pixels at native OAM completion.'
    if args.composition_costs:
        report['compositionCostBoundaries']=cost_boundaries
        report['compositionCosts']=[dict(case=r['case'],idle=r['idleFramesBeforeMove'],
            actions={name:summarize_costs(a['events']) for name,a in r['actions'].items()}) for r in records]
        report['compositionCostObserverSha256']=sha((ROOT/'scripts/art_composition_costs.py').read_bytes())
        report['scope']+=' Authenticated compiled Thumb call/return boundaries measure inclusive GBA cycles, including scoped ARM leaves; nested costs must not be added twice.'
    if args.controller_costs:
        report['controllerBoundaries']=controller_proof
        report['controllerCosts']=[dict(case=r['case'],idle=r['idleFramesBeforeMove'],
            actions={name:controller_summary(a['events'],controller_proof) for name,a in r['actions'].items()}) for r in records]
        report['controllerCostObserverSha256']=sha((ROOT/'scripts/art_controller_costs.py').read_bytes())
        report['scope']+=' Authenticated native controller direct-call profiling; includes interrupt and child time. Indirect calls are not separately attributed.'
    if args.scoped_costs:
        report['scopedCostBoundaries']=scoped_proof
        report['scopedCostObserverSha256']=sha((ROOT/'scripts/art_scoped_costs.py').read_bytes())
        report['scope']+=' Standard ARM wrappers fully authenticated: allocation/copy and actual leaf branch/return costs separated. Every executed IWRAM blob matches its ROM leaf. ROM fallback is not exercised in these scenarios; return-only shared fallback exits are excluded explicitly.'
    if meta.get('fusedCompose'):
        report['fusedAudit']=dict(sourceSha256=sha((ROOT/'scripts/art_fused_trace.py').read_bytes()))
        report['scope']+=' Every fused apply independently checks current OAM against actual stack demands, including mapped history IDs and ordered 8bpp indices; ordinary prefix fallback remains separately observed.'
    if meta.get('repeatFrame'):
        report['repeatAudit']=dict(keyVersion=meta.get('repeatKeyVersion',1),site=meta['symbols']['ffta_art_palette_apply_validated']&~1,
            sourceSha256=sha((ROOT/'scripts/art_repeat_trace.py').read_bytes()))
        report['scope']+=' Every repeat fast entry independently checks actual OAM/plan/history/pixels; key version2 also reconstructs fresh native ownership and verifies history remapping. Counter and coverage records are required, not inferred from frame equality.'
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(status='passed', checks=len(checks), report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed', error=str(error),
        checks=checks, records=records, pendingEvents=trace.events if trace else []), indent=2)+'\n', encoding='utf-8')
    print('Artifacts: '+str(out))
    raise
finally:
    if e:
        e.close()
