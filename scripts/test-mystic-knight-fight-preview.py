"""Native UI/AI Fight forecasts, exact sorted hand, and read-only controls.

Exercise real native callers, never fabricated caller addresses or substituted
formula returns. This does not certify late Judge reporting or rendered menus.
"""
import collections
import copy
import itertools
import json
import pathlib
import struct

ROOT = pathlib.Path(__file__).resolve().parents[1]
source = ROOT / 'scripts/test-mystic-knight-commands.py'
ns = {'__file__': str(source), '__name__': 'mystic_fight_preview_fixture'}
exec(compile(source.read_text().split('# Native casts cover')[0], str(source), 'exec'), ns)
m, S, meta, OUT, A, T, STACK, fixture, call, record = (
    ns[x] for x in ('m', 'S', 'meta', 'OUT', 'A', 'T', 'STACK', 'fixture', 'call', 'record'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0

rom = pathlib.Path(meta['path']).read_bytes()
oracle = m.__class__(rom, m.read(0x03000000, 0x8000))
table = struct.unpack_from('<I', rom, 0xcbc74)[0]
table_bytes = rom[table - 0x08000000:table - 0x08000000 + 461 * 32]
elements = (0, 1, 5, 6, 0, 0, 0, 0, 0, 0, 0, 7)
checks, failures, samples = collections.Counter(), [], []
observed = {'actual': [], 'oracle': []}
case = None
calls = 0
raw_values = {'actual': [], 'oracle': []}


def check(name, actual, expected):
    checks[name] += 1
    if actual != expected:
        failures.append(dict(case=case, check=name, actual=copy.deepcopy(actual), expected=copy.deepcopy(expected)))


def watch(label):
    def observe(u, pc, size, data):
        v = u.reg_read(UC_ARM_REG_R0)
        observed[label].append((pc, v if v < 0x80000000 else v - 0x100000000))
    return observe


for machine, label in ((m, 'actual'), (oracle, 'oracle')):
    for pc in (0x080b5730, 0x080bdf58, 0x080c2368,
               0x0812e7dc, 0x0812e978, 0x0812e9a8, 0x0812ea02, 0x081356ec):
        machine.u.hook_add(UC_HOOK_CODE, watch(label), begin=pc, end=pc)


def live(machine, records):
    return (machine.read(A, 264) + machine.read(T, 264) +
            b''.join(machine.read(p, 22) for p in records) + machine.read(0x030034b0, 4))


def invoke(machine, path, item, residue=0):
    global calls
    sp = STACK + residue
    machine.put(sp, struct.pack('<5I', 0, 255, 0, 0, 0))
    if path == 'UI':
        machine.call(0x080b55cc, ns['wrappers'][A], ns['wrappers'][T], 0, item, stack=sp)
    elif path == 'AI-score':
        machine.call(0x080bdecc, ns['wrappers'][A], ns['wrappers'][T], 0, 0, stack=sp)
    elif path == 'AI-detail':
        machine.put(sp, struct.pack('<2I', item, 0))
        machine.call(0x080c2618, 0x02028000, ns['wrappers'][A], ns['wrappers'][T], 0, stack=sp)
    elif path == 'law-damage':
        # Original damage-threshold law56, one active law in the native list.
        machine.put(0x02003c33, b'\x01\x38\x00')
        machine.call(0x0813569c, A, T, 0, 0, stack=sp)
    elif path.startswith('reaction-'):
        machine.call(0x0812e6e0, A, T, 0, int(path.split('-')[1]), stack=sp)
    else:
        machine.put(sp, struct.pack('<2I', 0, 2))
        return_value = machine.call(0x08130200, A, T, 0, item, stack=sp)
        raw_values['actual' if machine is m else 'oracle'].append(return_value)
    calls += 1


# Native UI, score and detailed AI use their first power-sorted weapon.
# Independent original-item/WDef controls match ONLY when that is primary.
pairs = ((88, 0), (88, 88), (88, 89), (89, 88))
for kind, affinity, pair, residue, path in itertools.product(
        range(1, 12), range(5), pairs, (0, 4), ('UI', 'AI-score', 'AI-detail', 'law-damage')):
    case = (path, kind, affinity, pair, residue)
    fixture(0); ns['job'](A, 1, 7)
    m.put(table, table_bytes)
    m.put(A + 0x2a, struct.pack('<5H', *pair, 0, 0, 0))
    m.put(T + 0x0d, bytes((affinity,)) * 8)
    call('ffta_myk_grant', A, kind)
    records = (record(A), record(T))
    count = m.call(0x0812f0d8, A, 0x02028200, stack=STACK)
    items = struct.unpack('<' + 'H' * count, m.read(0x02028200, 2 * count))
    power = [m.call(0x080ca7a4, i, 10, stack=STACK) & 255 for i in pair]
    primary_first = not pair[1] or power[0] >= power[1]
    oracle.put(table, table_bytes)
    oracle.put(0x02000000, m.read(0x02000000, 0x40000))
    oracle.put(0x03000000, m.read(0x03000000, 0x8000))
    oracle.put(records[0] + 20, bytes(2))
    if primary_first:
        oracle.put(table + pair[0] * 32 + 9, bytes((elements[kind],)))
        if kind == 8:
            defense = int.from_bytes(oracle.read(T + 0x22, 2), 'little')
            oracle.put(T + 0x22, struct.pack('<H', defense * 3 // 4))
    for machine, label in ((m, 'actual'), (oracle, 'oracle')):
        observed[label].clear()
        before = live(machine, records)
        invoke(machine, path, items[0], residue)
        check('forecast-preserves-units-state-RNG', live(machine, records).hex(), before.hex())
        check('forecast-retires-scope', machine.read(0x0203f730, 4).hex(), bytes(4).hex())
        check('forecast-retires-snapshot', machine.read(0x0203ff44, 8).hex(), bytes(8).hex())
    check('native-preview-was-reached', len(observed['actual']) > 0, True)
    check('native-preview-matches-independent-hand-control', observed['actual'], observed['oracle'])
    samples.append(dict(case=case, primaryFirst=primary_first, items=items, result=list(observed['actual'])))

# Reaction eligibility also asks for a first-sorted preview; it must be pure
# and agree with the same independently altered native item/defense inputs.
for kind, pair, reaction in itertools.product((1, 8), pairs, (1, 12, 13, 14)):
    case = ('reaction', kind, pair, reaction)
    fixture(0); ns['job'](A, 1, 7); m.put(table, table_bytes)
    m.put(A + 0x2a, struct.pack('<5H', *pair, 0, 0, 0)); m.put(T + 0x0d, b'\x04' * 8)
    call('ffta_myk_grant', A, kind); records = (record(A), record(T))
    power = [m.call(0x080ca7a4, i, 10, stack=STACK) & 255 for i in pair]
    oracle.put(table, table_bytes)
    oracle.put(0x02000000, m.read(0x02000000, 0x40000)); oracle.put(0x03000000, m.read(0x03000000, 0x8000))
    oracle.put(records[0] + 20, bytes(2))
    if not pair[1] or power[0] >= power[1]:
        oracle.put(table + pair[0] * 32 + 9, bytes((elements[kind],)))
        if kind == 8: oracle.put(T + 0x22, struct.pack('<H', 25 * 3 // 4))
    for machine, label in ((m, 'actual'), (oracle, 'oracle')):
        observed[label].clear(); before = live(machine, records)
        invoke(machine, 'reaction-' + str(reaction), 0)
        check('reaction-query-preserves-units-state-RNG', live(machine, records).hex(), before.hex())
    check('reaction-preview-matches-independent-hand-control', observed['actual'], observed['oracle'])

# A direct item-equal formula call has no authoritative native hand owner.
for kind in range(1, 12):
    case = ('unowned-formula', kind); fixture(0); m.put(table, table_bytes)
    records = (record(A), record(T)); call('ffta_myk_grant', A, kind)
    oracle.put(table, table_bytes)
    oracle.put(0x02000000, m.read(0x02000000, 0x40000)); oracle.put(0x03000000, m.read(0x03000000, 0x8000))
    oracle.put(records[0] + 20, bytes(2))
    before = live(m, records); invoke(m, 'unowned', 88); invoke(oracle, 'unowned', 88)
    check('unowned-formula-has-no-enchanted-effect', raw_values['actual'][-1], raw_values['oracle'][-1])
    check('unowned-formula-is-pure', live(m, records).hex(), before.hex())
    check('unowned-formula-does-not-leave-fuel', call('ffta_myk_fight_kind', A, 88), 0)

# Native drain must be replaced in forecasts too. Restorative weapons retain
# healing even when absorption would otherwise invert the native sign twice.
# The independent control removes only drain, sets the native element/defense,
# then applies the explicit restorative sign rule to its measured result.
for effect, kind, affinity, path in itertools.product(
        (0x3d, 0x3f), range(1, 12), range(5), ('UI', 'AI-score', 'AI-detail')):
    case = ('weapon-property', effect, kind, affinity, path)
    fixture(0); m.put(table, table_bytes)
    m.put(table + 88 * 32 + 26, bytes((effect, 0, 0)))
    m.put(T + 0x0d, bytes((affinity,)) * 8); call('ffta_myk_grant', A, kind)
    records = (record(A), record(T))
    oracle.put(table, table_bytes)
    oracle.put(table + 88 * 32 + 26, bytes((0 if effect == 0x3d else effect, 0, 0)))
    oracle.put(table + 88 * 32 + 9, bytes((elements[kind],)))
    oracle.put(0x02000000, m.read(0x02000000, 0x40000)); oracle.put(0x03000000, m.read(0x03000000, 0x8000))
    oracle.put(records[0] + 20, bytes(2))
    if kind == 8: oracle.put(T + 0x22, struct.pack('<H', 25 * 3 // 4))
    for machine, label in ((m, 'actual'), (oracle, 'oracle')):
        observed[label].clear(); before = live(machine, records); invoke(machine, path, 88)
        check('weapon-query-is-pure', live(machine, records).hex(), before.hex())
    expected = [(pc, -abs(v) if effect == 0x3f else v) for pc, v in observed['oracle']]
    check('weapon-query-matches-native-control-and-restoration-rule', observed['actual'], expected)

m.put(table, table_bytes)
check('nonvacuous-primary-second', any(not x['primaryFirst'] for x in samples), True)
check('nonvacuous-positive-forecast', any(v > 0 for x in samples for pc, v in x['result']), True)
check('nonvacuous-absorbed-forecast', any(v < 0 for x in samples for pc, v in x['result']), True)
report = dict(passed=not failures, romSha1=meta['romSha1'], assertions=sum(checks.values()),
              nativeCalls=calls, checks=dict(checks), failures=failures, samples=samples,
              limits=['Late Judge and status/recovery predictions remain separate acceptance',
                      'Native forecast callers are executed; rendered menus and full AI turns are separate'])
(OUT / 'mystic-knight-fight-preview.json').write_text(json.dumps(report, indent=2))
print(json.dumps({k: v for k, v in report.items() if k != 'samples'}, indent=2))
assert not failures, ('Mystic Fight forecast failures', len(failures))
