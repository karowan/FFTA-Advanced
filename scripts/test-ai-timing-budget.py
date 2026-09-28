"""Accept completed matched timing evidence against the reviewed frame budgets.

No emulator is launched. Prepare and measure both profiles through the declared
plan first. Every report must describe the current ROM and original test core;
partial pilots, changed scenarios, altered choices and per-case slowdowns fail.
The 5% allowance is frame-based, never adjusted for host execution speed.
"""
from ai_planner_seed import BOUNDARY
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from chemist_candidate import ROOT, candidate

BASE = ROOT / 'build/expansion/ai-timing'
budget = json.loads((ROOT / 'scripts/ai-timing-budgets.json').read_text())
rom_sha = candidate()['romSha1']
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(ROOT / 'tools/mgba-test-core/mgba_libretro.dll') == budget['coreSha256']


def validate(report, profile, spec):
    assert report['status'] == 'completed' and report['error'] is None
    assert report['skillProfile'] == profile and report['seeds'] == budget['seeds']
    assert report['coreSha256'] == budget['coreSha256']
    assert report.get('seedBoundary') == BOUNDARY, 'Explicit constructor seed required'
    for row in report['records']:
        pins=row.get('seedPins',[])
        assert len(pins)==1 and pins[0]['seed']==row['seed'], 'Exactly one declared seed pin'
    assert report['fps'] == 16777216 / 280896
    rows = {(r['build'], r['label'], r['seed']): r for r in report['records']}
    expected = {(b, j, s) for b in ('vanilla', 'mod') for j in spec['jobs'] for s in budget['seeds']}
    assert set(rows) == expected and len(report['records']) == len(expected), 'Incomplete or duplicate cases'
    for job, frames in spec['jobs'].items():
        for i, seed in enumerate(budget['seeds']):
            original, mod = (rows[b, job, seed] for b in ('vanilla', 'mod'))
            assert original['romSha1'] == budget['vanillaSha1'] and mod['romSha1'] == rom_sha
            assert original['success'] == mod['success'] == 1
            for field in ('canonicalInputSha256', 'availableActions', 'action', 'choice'):
                assert original[field] == mod[field], (job, seed, field)
            assert original['decisionFrames'] == frames['vanilla'][i], 'Vanilla workload drift'
            maximum = (frames['mod'][i] * (100 + budget['allowancePercent']) + 99) // 100
            assert 0 < mod['decisionFrames'] <= maximum, (job, seed, mod['decisionFrames'], maximum)


evidence = []
rejections = 0
for profile, spec in budget['profiles'].items():
    path = Path(json.loads((BASE / spec['index']).read_text())['report'])
    report = json.loads(path.read_text())
    validate(report, profile, spec)
    assert report['pins'], 'Missing immutable fixture receipts'
    for p, digest in report['pins'].items():
        assert sha(p) == digest, ('Fixture changed', p)
    # Verify that the gate rejects partial, stale, slower and changed-choice
    # evidence without making new game fixtures or touching saved reports.
    for fault in ('partial', 'rom', 'slow', 'choice','seed'):
        bad = copy.deepcopy(report)
        row = next(r for r in bad['records'] if r['build'] == 'mod')
        if fault == 'partial': bad['records'].pop()
        elif fault == 'rom': row['romSha1'] = '0' * 40
        elif fault == 'slow': row['decisionFrames'] *= 2
        elif fault == 'seed':row['seedPins']=[]
        else: row['choice'] ^= 1
        try: validate(bad, profile, spec)
        except AssertionError: rejections += 1
        else: raise AssertionError('Gate accepted ' + fault)
    evidence.append(dict(profile=profile, report=str(path), sha256=sha(path), decisions=24))

out = BASE / ('budget-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
out.mkdir()
path = out / 'report.json'
path.write_text(json.dumps(dict(passed=True, romSha1=rom_sha, matchedPairs=24,
    rejectionChecks=rejections, allowancePercent=budget['allowancePercent'],
    scope=budget['scope'], evidence=evidence), indent=2) + '\n')
print(json.dumps(dict(passed=True, romSha1=rom_sha, matchedPairs=24, report=str(path))))
