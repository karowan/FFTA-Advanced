"""Paired real-core AI decision latency; an investigation, not an optimization.

Own-ROM cold allocations, original jobs, common starting combat fields, native
terrain and fixed formation. Observe every video frame, including during input
holds. The elapsed emulated frames include time spent in hooks and VBlank, but
exclude movement/attack animation after the planner publishes phase 8.
"""
from contextlib import ExitStack
import ctypes as C
import hashlib
import json
import runpy
import statistics
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path
from chemist_candidate import candidate, ROOT
from native_battle_wrappers import from_emulator, fixed_giza_formation
from ai_planner_seed import PlannerSeed, BOUNDARY

BASE = ROOT / 'build/expansion/ai-timing'
index = json.loads((BASE / 'fixtures.json').read_text())
FIX = Path(index['directory'])
assert candidate()['romSha1'] == index['modSha1']
OUT = BASE / ('measure-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
OUT.mkdir()
E = runpy.run_path(str(ROOT / 'scripts/emulator-test.py'))['Emulator']
menu = runpy.run_path(str(ROOT / 'scripts/battle-menu-observation.py'))['menu_visible']
word = lambda b, p: struct.unpack_from('<I', b, p)[0]
half = lambda b, p: struct.unpack_from('<H', b, p)[0]
FPS = 16777216 / 280896
CASES = [(0x290, 'Human Soldier'), (0x188, 'Moogle Black Mage'),
         (0x4a0, 'Nu Mou White Mage'), (0x5a8, 'Viera Archer')]
SEEDS = [0, 5, 18]
STARTING = '--starting-skills' in sys.argv
if '--pilot' in sys.argv: CASES, SEEDS = CASES[-1:], [5]
common = (FIX / 'vanilla/battle-ready.ram').read_bytes()
rows, inputs, pins = [], [], {}
for name in ('vanilla', 'mod'):
    for file in ('frozen.gba', 'battle-ready.state', 'report.json'):
        p = FIX / name / file
        pins[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()


def checkpoint(e, folder, name):
    e.save(folder / (name + '.state'))
    e.screenshot(folder / (name + '.png'))
    (folder / (name + '.ram')).write_bytes(e.memory())


def result(status, error=None):
    report = dict(status=status, error=error, scope=__doc__, fixtureDirectory=str(FIX),
                  skillProfile='original starting mastery' if STARTING else 'fully learned primary job',
                  coreSha256=hashlib.sha256((ROOT / 'tools/mgba-test-core/mgba_libretro.dll').read_bytes()).hexdigest(),
                  fps=FPS, seeds=SEEDS, seedBoundary=BOUNDARY, records=rows, inputs=inputs, pins=pins)
    if status == 'completed':
        report['summary'] = {}
        for name in ('vanilla', 'mod'):
            sample = [r['decisionFrames'] for r in rows if r['build'] == name]
            report['summary'][name] = dict(count=len(sample), meanFrames=statistics.mean(sample),
                meanSeconds=statistics.mean(sample)/FPS, medianFrames=statistics.median(sample),
                maxFrames=max(sample))
    (OUT / 'report.json').write_text(json.dumps(report, indent=2))
    (BASE / ('latest-starting.json' if STARTING else 'latest-measurement.json')).write_text(json.dumps(dict(report=str(OUT / 'report.json'))))
    return report


result('running')
try:
    for actor, label in CASES:
        for seed in SEEDS:
            for build in ('vanilla', 'mod'):
                folder = OUT / f'{actor:04x}-{seed}-{build}'
                folder.mkdir()
                path = FIX / build / 'frozen.gba'
                image = path.read_bytes()
                proof = json.loads((FIX / build / 'report.json').read_text())
                assert hashlib.sha1(image).hexdigest() == proof['romSha1']
                with E(path) as e, ExitStack() as seed_scope:
                    e.load(FIX / build / 'battle-ready.state')
                    wrappers = from_emulator(image, e)
                    fixed_giza_formation(image, e)
                    for u in wrappers:
                        # Copy declared original combat inputs, not pointers,
                        # allocator metadata, sprite objects or AI decisions.
                        e.set_memory(u+5, common[u+5:u+0x40])
                        e.set_memory(u+0x40, common[u+0x40:u+0xd0])
                        e.set_memory(u+0xd0, common[u+0xd0:u+0xd6])
                        e.set_memory(u+0x101, common[u+0x101:u+0x102])
                        e.set_memory(u+0xe8, bytes(8))
                        e.set_memory(u+0x18, struct.pack('<4H', 999,999,100,100))
                        e.set_memory(u+0x3a, bytes(3))
                        # Other combatants are manually waited; only the focus
                        # actor plans. Judge keeps its native noncombat side.
                        if u != 0x34ec: e.set_memory(u+0x29, bytes((128 if u==actor else 0,)))
                    if not STARTING:e.set_memory(actor+0x40, bytes([255])*0x90)
                    e.set_memory(actor+8, b'\0')
                    e.set_memory(actor+0x36, bytes(2))
                    # Let the open player's menu settle after setup. No AI
                    # interval is skipped: the focus is a different unit.
                    e.run(60)
                    checkpoint(e, folder, 'declared-start')
                    trace, queue = [], []
                    activated = started = finished = None
                    canonical_hash = None
                    available_actions = None
                    planner_seed = None
                    prior = None
                    for frame in range(20000):
                        r = e.memory()
                        live_wrapper = word(r, 0xf4ec)
                        live = word(r, live_wrapper-0x02000000) if 0x02000000<=live_wrapper<0x02040000 else 0
                        if live == 0x02000000+actor and activated is None:
                            activated = frame
                            # Restore the declared formation/resources before
                            # this unit's native planner creates target copies.
                            fixed_giza_formation(image, e)
                            C.memmove(e.maps[0x03000000][0]+0x34b0, struct.pack('<I',seed),4)
                            queue = []
                            checkpoint(e, folder, 'activation')
                            r = e.memory()
                        phase = half(r, 0x156ec)
                        owner = word(r, 0x101fc)
                        state = (live, owner, phase)
                        if state != prior:
                            trace.append(dict(frame=frame, live=hex(live), owner=hex(owner), phase=phase))
                            prior = state
                        if activated is not None and owner == live_wrapper and live == 0x02000000+actor:
                            if phase <= 7 and started is None:
                                assert phase == 0, ('Missed native planning start', phase)
                                started = frame
                                # Pin randomness at the actual planning boundary,
                                # after camera/setup delays. Frame-based native RNG
                                # may still diverge during different-length searches.
                                C.memmove(e.maps[0x03000000][0]+0x34b0, struct.pack('<I',seed),4)
                                # All 262 non-name bytes of every canonical unit
                                # must match across the paired runs, including CT,
                                # statuses, native flags, equipment and positions.
                                canonical_hash = hashlib.sha256(b''.join(r[u+2:u+264] for u in sorted(wrappers))).hexdigest()
                                checkpoint(e, folder, 'planning-start')
                                planner_seed = PlannerSeed(e, seed)
                                seed_scope.enter_context(planner_seed)
                            if phase == 1 and available_actions is None:
                                seed_scope.close()
                                assert len(planner_seed.pins)==1, 'Exactly one native constructor seed'
                                base = word(r,0x101f8)-0x02000000
                                assert 0<=base<0x3a000
                                count=half(r,base+0x58)
                                assert 0<count<=40
                                available_actions=list(struct.unpack_from('<'+str(count)+'H',r,base+8))
                            if phase == 8 and started is not None:
                                finished = frame
                                checkpoint(e, folder, 'choice-published')
                                break
                        if activated is None and not queue and menu(e):
                            inputs.append(dict(build=build, actor=actor, seed=seed, frame=frame, buttons=[32,32,256,256]))
                            for key in (32,32,256,256): queue.extend([key]*8 + [0]*180)
                        e.run(1, queue.pop(0) if queue else 0)
                    else:
                        (folder / 'trace.json').write_text(json.dumps(trace, indent=2))
                        checkpoint(e,folder,'timeout')
                        raise AssertionError(('No complete native decision',build,label,seed,activated,started))
                    row = dict(build=build,label=label,actor=hex(actor),seed=seed,romSha1=proof['romSha1'],
                        activationFrame=activated,planningStartFrame=started,choiceFrame=finished,
                        decisionFrames=finished-started,activationToChoiceFrames=finished-activated,
                        canonicalInputSha256=canonical_hash,availableActions=available_actions,
                        seedPins=planner_seed.pins,
                        action=half(r,0x156b6),choice=half(r,0x156b8),success=r[0x15639],
                        trace=trace,folder=str(folder))
                    rows.append(row)
                    if build == 'mod':
                        other = rows[-2]
                        assert other['canonicalInputSha256']==canonical_hash, 'Paired canonical combat inputs differ'
                        assert other['availableActions']==available_actions, 'Paired native action lists differ'
                    print(json.dumps({k:v for k,v in row.items() if k not in ('trace','folder')}),flush=True)
                    result('running')
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==digest for p,digest in pins.items())
    print(json.dumps(result('completed')['summary'],indent=2),flush=True)
except Exception as error:
    result('failed',repr(error))
    raise
