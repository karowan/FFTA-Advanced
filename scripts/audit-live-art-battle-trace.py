"""Audit every retained battle sample, including checks after a fail-fast assertion.

Reads existing evidence only. Does not run a game or turn failed evidence into
acceptance. The source hash and this script's hash make derived metrics repeatable.
"""
import argparse, collections, hashlib, json, struct
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('report', type=Path)
args = parser.parse_args()
raw = args.report.read_bytes()
data = json.loads(raw)
traces = data['paletteTraces']
parent, candidate = traces['parent'], traces['candidate']
assert set(parent) == set(candidate) and 'ready' in parent, 'Complete paired traces required'
violations = collections.defaultdict(list)
shadow_indices, hardware_indices = collections.Counter(), collections.Counter()


def check(ok, kind, label):
    if not ok: violations[kind].append(label)


for label, current in candidate.items():
    old = parent[label]
    live = current['live']
    check(current['frame'] - candidate['ready']['frame'] == old['frame'] - parent['ready']['frame'], 'inputSchedule', label)
    check(current['units'] == old['units'], 'canonicalUnits', label)
    check(live['failed'] == 0, 'allocationOrOwnership', label)
    check(live['active'] != 0, 'missingBattleOverlay', label)
    check(live['unsupported'] == candidate['ready']['live']['unsupported'], 'newUnsupportedBinding', label)
    check(current['fenceIntact'], 'reservationFence', label)
    a, b = struct.unpack('<512H', bytes.fromhex(current['nativeShadow'])), struct.unpack('<512H', bytes.fromhex(old['nativeShadow']))
    changed = [i for i in range(512) if a[i] != b[i]]
    shadow_indices.update(changed)
    check(not changed, 'nativeShadow', label)
    actual, expected = bytes.fromhex(current['palette']), bytearray.fromhex(old['palette'])
    if live['active']:
        check(160 <= live['start'] <= live['end'] < 228, 'scanTiming', label)
        if not live['flags'] & 128: check(160 <= live['display'] < 228, 'displayTiming', label)
        for bank in range(16):
            if live['active'] & (1 << bank):
                colors = actual[512 + bank * 32:544 + bank * 32]
                check(colors == bytes.fromhex(current['visibleColors']), 'generatedHardwareColors', label)
                expected[512 + bank * 32:544 + bank * 32] = colors
    changed = [i for i in range(512) if actual[i * 2:i * 2 + 2] != expected[i * 2:i * 2 + 2]]
    hardware_indices.update(changed)
    check(not changed, 'unownedHardwareColors', label)

motion = {}
for action, initial, target in [('move', 48, 144), ('cancel', 144, 48)]:
    motion[action] = {}
    for case in ('parent', 'candidate'):
        rows = [(label, row) for label, row in data['observations'][case].items() if label.startswith(action + '-')]
        start = next((item for item in rows if item[1]['position'][0] != initial), None)
        end = next((item for item in rows if item[1]['position'][0] == target), None)
        assert start and end, 'Complete actual motion required'
        motion[action][case] = dict(start=start[0], end=end[0], startOffset=int(start[0].rsplit('-', 1)[1]),
                                   elapsed=end[1]['frame'] - start[1]['frame'])
    check(motion[action]['candidate']['elapsed'] <= motion[action]['parent']['elapsed'], 'movementSlowdown', action)
    check(motion[action]['candidate']['startOffset'] <= motion[action]['parent']['startOffset'], 'actionResponseDelay', action)

stack_guards = []
root = Path(__file__).resolve().parents[1]
manifest = root / 'build/art/live-palette' / data['romSha1'] / 'manifest.json'
if manifest.exists():
    metadata = json.loads(manifest.read_text())
    rom = Path(metadata['path']).read_bytes()
    assert hashlib.sha1(rom).hexdigest() == data['romSha1'], 'Stack audit ROM identity'
    expected_code = rom[0xa38d24:0xa3991c]
    for snapshot in sorted(args.report.parent.glob('*.iwram')):
        raw_iwram = snapshot.read_bytes()
        check(raw_iwram[0x6170:0x6d68] == expected_code, 'nativeExecutableIWRAM', snapshot.name)
        stack_guards.append(dict(path=str(snapshot), sha256=hashlib.sha256(raw_iwram).hexdigest(),
                                 matchesNativeCode=raw_iwram[0x6170:0x6d68] == expected_code))

result = dict(status='failed' if violations else 'passed', romSha1=data['romSha1'],
    source=str(args.report.resolve()), sourceSha256=hashlib.sha256(raw).hexdigest(),
    scriptSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    originalStatus=data['status'], originalError=data.get('error'), pairedSamples=len(candidate),
    violations=dict(violations), violationCounts={k: len(v) for k, v in violations.items()},
    nativeShadowIndices=dict(sorted(shadow_indices.items())),
    unownedHardwareIndices=dict(sorted(hardware_indices.items())), motion=motion,
    maximumActiveDisplayLine=max(r['live']['display'] for r in candidate.values() if r['live']['active']),
    activeSamples=sum(bool(r['live']['active']) for r in candidate.values()),
    unsupportedAtReady=candidate['ready']['live']['unsupported'],
    unsupportedAtReturn=candidate['returned']['live']['unsupported'],
    retainedNativeCodeGuards=stack_guards,
    nativeCodeGuardScope='Retained IWRAM snapshots only, not every frame or all stack/interrupt lifetimes.',
    scope='Derived audit of retained actual samples only. No phase waiver, new playback, battle completion, variants, unseen lifetimes or final-art acceptance.')
output = args.report.with_name('trace-audit.json')
output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({key: result[key] for key in ('status', 'pairedSamples', 'violationCounts', 'motion', 'maximumActiveDisplayLine')}))
print(str(output))
