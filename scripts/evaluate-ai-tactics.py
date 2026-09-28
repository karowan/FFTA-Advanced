"""Measure desired tactics separately from hard correctness and speed gates.

Uses the reusable, own-ROM native allocations from ai-timing-fixtures. Only
declared combat inputs are written, before candidate construction. Every native
planner instruction executes; no chosen action, score or destination is supplied.
Observe mode reports quality failures without pretending that they passed.
Strict mode is intentionally red until all desired behaviors pass. Ratchet mode
protects previously passing seeds while known quality failures remain visible.
"""
import argparse
from contextlib import ExitStack
import ctypes as C
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import runpy
import struct

from ai_planner_seed import BOUNDARY, PlannerSeed
from chemist_candidate import ROOT, candidate
from native_battle_wrappers import fixed_giza_formation, from_emulator
from native_ai_eval_probe import forecast_rows

BASE = ROOT / 'build/expansion/ai-tactics'
SPEC = ROOT / 'scripts/ai-tactics-cases.json'
LOCK = ROOT / 'scripts/ai-tactics-baseline.json'
FPS = 16777216 / 280896
word = lambda b, p: struct.unpack_from('<I', b, p)[0]
half = lambda b, p: struct.unpack_from('<H', b, p)[0]
digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def judge(case, result, units):
    """Small outcome predicates, intentionally independent of AI score code.

    Elemental black magic and the healing spells in this corpus use their
    original cross-shaped radius-one footprint. Exact recipient eligibility,
    damage, execution and general shapes are NOT inferred from this distance.
    """
    wanted = case['expect']
    action = result['action']
    center = result['center']
    distance = lambda a, b: sum(abs(x-y) for x, y in zip(a, b))
    checks = {'published-action': result['success'] == 1}
    if 'actions' in wanted:
        checks['appropriate-action'] = action in wanted['actions']
    if 'excludeActions' in wanted:
        checks['no-wasted-action'] = action not in wanted['excludeActions']
    if 'target' in wanted:
        checks['intended-target'] = result['target'] == wanted['target']
    if 'cover' in wanted:
        checks['covers-beneficiary'] = distance(center, units[str(wanted['cover'])]['position']) <= 1
    if 'minimumEnemyDistance' in wanted:
        distances = [distance(result['destination'], u['position']) for u in units.values()
                     if not u['ally'] and not u['judge'] and u['hp'] > 0]
        checks['safe-ranged-distance'] = min(distances) >= wanted['minimumEnemyDistance']
    if 'avoidElementalArea' in wanted:
        checks['no-lethal-friendly-blast'] = action not in range(23, 32) or distance(
            center, units[str(wanted['avoidElementalArea'])]['position']) > 1
        checks['hostile-attack'] = action in (0, *range(23, 32)) and result['target'] is not None and not units[str(result['target'])]['ally']
    return checks


def regressions(report, lock):
    """Freeze inputs and each green assertion, not a preferred action number."""
    for field in ('specSha256','harnessSha256','probeSha256','coreSha256','seedBoundary'):
        assert lock[field]==report[field], ('Evaluation contract changed',field)
    expected={(r['id'],r['seed']):r for r in lock['records']}
    actual={(r['id'],r['seed']):r for r in report['records']}
    assert len(expected)==len(lock['records']) and len(actual)==len(report['records'])
    assert set(actual)==set(expected), 'Ratchet requires complete corpus'
    failures=[]
    for key,r in actual.items():
        old=expected[key]
        assert old['inputSha256']==r['inputSha256'], ('Scenario inputs drifted',key)
        assert set(old['checks'])==set(r['checks']), ('Assertion coverage changed',key)
        for check,passed in old['checks'].items():
            if passed and not r['checks'][check]:
                failures.append(dict(id=r['id'],seed=r['seed'],check=check))
        limit=(old['decisionFrames']*105+99)//100
        if not 0<r['result']['decisionFrames']<=limit:
            failures.append(dict(id=r['id'],seed=r['seed'],check='planning-budget',maximum=limit))
    return failures


def setup(e, image, wrappers, common, case, activated=False):
    actor = 0x2fc4
    fixed_giza_formation(image, e)
    for u in wrappers:
        e.set_memory(u+5, common[u+5:u+0xd6])
        e.set_memory(u+0x101, common[u+0x101:u+0x102])
        e.set_memory(u+0xe8, bytes(8))
        e.set_memory(u+0x18, struct.pack('<4H', 500, 500, 100, 100))
        e.set_memory(u+0x3a, bytes(3))
        if u != 0x34ec:
            e.set_memory(u+0x29, bytes((128 if u == actor or (activated and u >= 0x2fc4) else 0,)))
    # Team membership is held in native battle-manager cohorts, not just the
    # control bit. Use an actual enemy allocation and its existing teammates.
    # Copy declared original-job combat inputs only, never wrapper/heap fields.
    template = case['actor']
    e.set_memory(actor+5, common[template+5:template+0xd6])
    e.set_memory(actor+0xe8, bytes(8))
    e.set_memory(actor+0x18, struct.pack('<4H',500,500,100,100))
    e.set_memory(actor+0x29,b'\x80')
    e.set_memory(actor+0x3a,bytes(3))
    def swap_positions(a,b):
        r=e.memory()
        for target,source in ((a,b),(b,a)):
            e.set_memory(target+0xf6,r[source+0xf6:source+0xf8])
            e.set_memory(wrappers[target]+8,r[wrappers[source]+8:wrappers[source]+14])
    swap_positions(actor,template)
    e.set_memory(actor+0x40, bytes([255])*0x90)
    e.set_memory(actor+8, b'\0')
    e.set_memory(actor+0x36, bytes(2))
    if 'actorStats' in case:
        e.set_memory(actor+0x20, struct.pack('<4H', *case['actorStats']))
    # Move declared beneficiaries using existing valid native tile/elevation
    # pairs. Other occupants exchange places, so no units overlap.
    if 'beneficiaryTemplate' in case:
        source=case['beneficiaryTemplate'];u=0x30cc
        e.set_memory(u+5,common[source+5:source+0xd6])
        e.set_memory(u+0x18,struct.pack('<4H',500,500,100,100))
        e.set_memory(u+0x3a,bytes(3));e.set_memory(u+0xe8,bytes(8))
        e.set_memory(u+0x29,bytes((128 if activated else 0,)))
        swap_positions(u,source)
    # Restore native enemy control when the focus activates. Before that,
    # non-focus turns are manually Waited by the deterministic input controller.
    if activated:
        if 'onlyLivingOpponent' in case:
            for u in wrappers:
                if u < 0x2fc4 and u != case['onlyLivingOpponent']:
                    e.set_memory(u+0x18,bytes(2))
        for text, spec in case.get('units', {}).items():
            u = actor if text=='actor' else int(text)
            assert u in wrappers and u != 0x34ec
            if 'hp' in spec: e.set_memory(u+0x18, struct.pack('<H', spec['hp']))
            if 'mp' in spec: e.set_memory(u+0x1c, struct.pack('<H', spec['mp']))
            bits = sum(1 << bit for bit in spec.get('statusBits', []))
            e.set_memory(u+0xe8, bits.to_bytes(8, 'little'))


def unit_inputs(r, wrappers, actor):
    return {str(u): dict(job=r[u+5], race=r[u+6], primary=r[u+7],
        hp=half(r,u+0x18), maximumHP=half(r,u+0x1a), mp=half(r,u+0x1c),
        stats=list(struct.unpack_from('<4H',r,u+0x20)),
        position=list(r[u+0xf6:u+0xf8]), ally=bool(r[u+0x29]&128)==bool(r[actor+0x29]&128),
        judge=u==0x34ec, status=r[u+0xe8:u+0xf0].hex(),
        equipment=list(struct.unpack_from('<5H',r,u+0x2a))) for u in sorted(wrappers)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('observe','strict','ratchet'), default='ratchet')
    parser.add_argument('--case', action='append', default=[])
    args = parser.parse_args()
    spec = json.loads(SPEC.read_text())
    assert spec['schema'] == 1 and len({c['id'] for c in spec['cases']}) == len(spec['cases'])
    cases = [c for c in spec['cases'] if not args.case or c['id'] in args.case]
    assert cases and set(args.case) <= {c['id'] for c in spec['cases']}
    meta = candidate()
    index = json.loads((ROOT/'build/expansion/ai-timing/fixtures.json').read_text())
    assert index['modSha1'] == meta['romSha1'], 'Run ai-timing-fixtures for this exact ROM first'
    fixture = Path(index['directory']) / 'mod'
    image = Path(meta['path']).read_bytes()
    assert hashlib.sha1((fixture/'frozen.gba').read_bytes()).hexdigest() == meta['romSha1']
    proof = json.loads((fixture/'report.json').read_text())
    assert proof['romSha1'] == meta['romSha1']
    common = (fixture/'battle-ready.ram').read_bytes()
    pins = {str(p): digest(p) for p in (SPEC, fixture/'frozen.gba', fixture/'battle-ready.state',
                                     fixture/'battle-ready.ram', fixture/'report.json')}
    E = runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
    menu = runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))['menu_visible']
    out = BASE / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    report = dict(schema=1, status='running', mode=args.mode, romSha1=meta['romSha1'],
        specSha256=digest(SPEC), harnessSha256=digest(__file__), seedBoundary=BOUNDARY,
        probeSha256=digest(ROOT/'scripts/native_ai_eval_probe.py'),
        coreSha256=digest(ROOT/'tools/mgba-test-core/mgba_libretro.dll'),
        scope=spec['scope'], pins=pins, records=[])
    def save():
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    save()
    try:
        for case in cases:
            for seed in spec['seeds']:
                folder = out / f"{case['id']}-{seed}"
                folder.mkdir()
                with E(Path(meta['path'])) as e, ExitStack() as controls:
                    e.load(fixture/'battle-ready.state')
                    wrappers = from_emulator(image,e)
                    setup(e,image,wrappers,common,case)
                    e.run(60)
                    actor = 0x2fc4
                    active = started = None
                    queue, inputs, trace = [], [], []
                    prior = available = controller = units = None
                    for frame in range(20000):
                        r=e.memory();w=word(r,0xf4ec)
                        live=word(r,w-0x02000000) if 0x02000000<=w<0x02040000 else 0
                        if live == actor+0x02000000 and active is None:
                            active=frame;queue=[]
                            setup(e,image,wrappers,common,case,activated=True)
                            r=e.memory()
                            units=unit_inputs(r,wrappers,actor)
                        phase=half(r,0x156ec);owner=word(r,0x101fc)
                        if (live,phase,owner)!=prior:
                            trace.append(dict(frame=frame,unit=live,phase=phase,owner=owner))
                            prior=(live,phase,owner)
                        if active is not None and live == actor+0x02000000 and owner == w:
                            if phase<=7 and started is None:
                                assert phase==0, ('Missed planner start',phase)
                                started=frame
                                e.save(folder/'planning-start.state')
                                (folder/'planning-start.ram').write_bytes(r)
                                input_hash=hashlib.sha256(b''.join(r[u+2:u+264] for u in sorted(wrappers))).hexdigest()
                                probes=forecast_rows(image,r,C.string_at(*e.maps[0x03000000]),wrappers,actor,case)
                                controller=PlannerSeed(e,seed);controls.enter_context(controller)
                            if phase==1 and available is None:
                                controls.close()
                                assert len(controller.pins)==1
                                p=word(r,0x101f8)-0x02000000
                                assert 0<=p<0x3a000
                                count=half(r,p+0x58);assert 0<count<=40
                                available=list(struct.unpack_from('<'+'H'*count,r,p+8))
                                cohorts=[]
                                for start in (p+0x5c,p+0x2968):
                                    n=half(r,start+0x2908);assert n<=13
                                    members=[]
                                    for i in range(n):
                                        wp=word(r,start+i*808)-0x02000000
                                        members.append(word(r,wp)-0x02000000)
                                    cohorts.append(members)
                                expected_allies={u for u in wrappers if u>=0x2fc4 and u!=0x34ec}
                                expected_enemies={u for u in wrappers if u<0x2fc4}
                                assert set(cohorts[0])==expected_allies, ('Native ally cohort mismatch',cohorts)
                                assert set(cohorts[1])==expected_enemies, ('Native enemy cohort mismatch',cohorts)
                            if phase==8 and started is not None:
                                assert available is not None
                                break
                        if active is None and not queue and menu(e):
                            inputs.append(dict(frame=frame,buttons=[32,32,256,256]))
                            for key in (32,32,256,256): queue.extend([key]*8+[0]*180)
                        e.run(1,queue.pop(0) if queue else 0)
                    else:
                        e.save(folder/'timeout.state')
                        (folder/'trace.json').write_text(json.dumps(trace))
                        raise AssertionError(('Planner timeout',case['id'],seed,active,started))
                    target_wrapper=word(r,0x1548c)-0x02000000
                    target=next((u for u,v in wrappers.items() if v==target_wrapper),None)
                    result=dict(action=half(r,0x156b6),choice=half(r,0x156b8),success=r[0x15639],
                        destination=list(r[0x15634:0x15636]),center=list(r[0x15636:0x15638]),
                        target=target,decisionFrames=frame-started,decisionSeconds=(frame-started)/FPS)
                    assert result['decisionFrames']>0 and len(controller.pins)==1
                    # A failed desire is data. Corrupt/unlearned selection is a
                    # hard harness/correctness failure, never an expected red.
                    assert not result['success'] or result['action'] in available
                    assert all(0<=v<16 for v in result['destination']+result['center'])
                    quality=judge(case,result,units)
                    record=dict(id=case['id'],category=case['category'],purpose=case['purpose'],seed=seed,
                        inputSha256=input_hash,units=units,availableActions=available,
                        seedPins=controller.pins,cohorts=cohorts,forecasts=probes,result=result,checks=quality,passed=all(quality.values()),
                        trace=trace,inputs=inputs)
                    report['records'].append(record)
                    e.save(folder/'choice-published.state');e.screenshot(folder/'choice-published.png')
                    (folder/'choice-published.ram').write_bytes(r)
                    (folder/'record.json').write_text(json.dumps(record,indent=2)+'\n')
                    print(json.dumps({k:record[k] for k in ('id','seed','passed','checks','result')}),flush=True)
                    save()
        assert all(digest(p)==h for p,h in pins.items()), 'Pinned input changed'
        report['qualityPassed']=all(r['passed'] for r in report['records'])
        report['summary']=dict(passed=sum(r['passed'] for r in report['records']),total=len(report['records']))
        report['regressions']=[]
        if args.mode=='ratchet':
            lock=json.loads(LOCK.read_text())
            report['regressions']=regressions(report,lock)
        report['status']='completed'
        report['accepted']=not report['regressions'] and (args.mode!='strict' or report['qualityPassed'])
        save()
        (BASE/'latest.json').write_text(json.dumps(dict(report=str(out/'report.json')))+'\n')
        print(json.dumps(dict(report=str(out/'report.json'),accepted=report['accepted'],quality=report['summary'])),flush=True)
        return 0 if report['accepted'] else 1
    except BaseException as error:
        report.update(status='error',error=repr(error),accepted=False);save()
        raise


if __name__=='__main__':
    raise SystemExit(main())
