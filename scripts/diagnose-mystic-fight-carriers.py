"""Authenticate Fight hand provenance before attaching persistent riders.

The native iterator sorts weapons by attack, so iteration zero is not always
the equipment-primary weapon. Observe original instructions and real results;
never alter their registers, random values, hit decisions or damage.
"""
import collections
import itertools
import json
import pathlib
import struct

ROOT = pathlib.Path(__file__).resolve().parents[1]
source = ROOT / 'scripts/test-mystic-knight-commands.py'
ns = {'__file__': str(source), '__name__': 'mystic_fight_carrier_fixture'}
exec(compile(source.read_text().split('# Native casts cover')[0], str(source), 'exec'), ns)
m, meta, OUT, A, T, STACK, fixture, execute, call, half = (
    ns[x] for x in ('m', 'meta', 'OUT', 'A', 'T', 'STACK', 'fixture', 'execute', 'call', 'half'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R3, UC_ARM_REG_R9, UC_ARM_REG_SP

checks = collections.Counter()
failures, cases, events = [], [], []
case = None


def word(address):
    return struct.unpack('<I', m.read(address, 4))[0]


def check(name, actual, expected):
    checks[name] += 1
    if actual != expected:
        failures.append(dict(case=case, check=name, actual=actual, expected=expected))


def observe(u, pc, size, data):
    sp = u.reg_read(UC_ARM_REG_SP)
    if pc == 0x080a4852:
        obj = u.reg_read(UC_ARM_REG_R0)
        events.append(dict(kind='result', index=word(sp + 0x34), count=word(sp + 0x38),
            object=obj, actor=word(word(obj)), item=half(obj + 0x12), action=half(obj + 0x10),
            frame=sp, wrapper=word(sp + 0x24), argumentWrapper=u.reg_read(UC_ARM_REG_R1)))
    elif pc in (0x080a2914, 0x080a2974):
        obj = u.reg_read(UC_ARM_REG_R9)
        events.append(dict(kind='formula', object=obj, actor=u.reg_read(UC_ARM_REG_R0),
            target=u.reg_read(UC_ARM_REG_R1), item=u.reg_read(UC_ARM_REG_R3),
            reaction=word(sp), mode=word(sp + 4)))
    else:
        value = u.reg_read(UC_ARM_REG_R1)
        events.append(dict(kind='HP', target=u.reg_read(UC_ARM_REG_R0),
            delta=value if value < 0x80000000 else value - 0x100000000))


for pc in (0x080a4852, 0x080a2914, 0x080a2974, 0x080a2210):
    m.u.hook_add(UC_HOOK_CODE, observe, begin=pc, end=pc)

# Fixed native equipment inputs: actual primary can be first/second in the
# sorted execution list. Equal/identical weapons must retain equipment order.
pairs = ((88, 0), (88, 88), (88, 89), (89, 88), (74, 88), (88, 74))
for (primary, secondary), seed in itertools.product(pairs, range(8)):
    case = (primary, secondary, seed)
    fixture(0, seed)
    # This fixture studies the native two-weapon executor, not menu legality.
    ns['job'](A, 1, 7)
    m.put(A + 0x2a, struct.pack('<5H', primary, secondary, 0, 0, 0))
    call('ffta_myk_grant', A, 1)
    first_power = m.call(0x080ca7a4, primary, 10, stack=STACK) & 255
    second_power = m.call(0x080ca7a4, secondary, 10, stack=STACK) & 255 if secondary else 0
    expected_order = [primary] if not secondary else (
        [secondary, primary] if second_power > first_power else [primary, secondary])
    expected_primary_index = int(bool(secondary) and second_power > first_power)
    events.clear()
    execute(0)
    observed = list(events)
    result_rows = [e for e in observed if e['kind'] == 'result' and e['actor'] == A and e['action'] == 0]
    check('native-equipment-order', [e['item'] for e in result_rows], expected_order)
    check('native-indices', [e['index'] for e in result_rows], list(range(len(expected_order))))
    check('native-counts', [e['count'] for e in result_rows], [len(expected_order)] * len(expected_order))
    for row in result_rows:
        check('exact-primary-wrapper', row['wrapper'], row['argumentWrapper'])
    primary_rows = [e for e in result_rows if e['index'] == expected_primary_index]
    check('one-equipment-primary-object', len(primary_rows), 1)
    if primary_rows:
        check('primary-object-item', primary_rows[0]['item'], primary)
    # Each successful Fight formula must belong to an observed current native
    # object; an item-ID comparison alone cannot distinguish duplicate blades.
    current = None
    for event in observed:
        if event['kind'] == 'result':
            current = event
        elif event['kind'] == 'formula' and event['actor'] == A:
            check('formula-has-actual-object', bool(current), True)
            if current:
                check('formula-object-owner', event['object'], current['object'])
                check('formula-object-item', event['item'], current['item'])
    check('snapshot-retired', m.read(0x0203ff44, 8).hex(), bytes(8).hex())
    cases.append(dict(primary=primary, secondary=secondary, seed=seed,
        primaryIndex=expected_primary_index, power=[first_power, second_power], events=observed))

check('nonvacuous-primary-executes-second', any(c['primaryIndex'] == 1 for c in cases), True)
check('nonvacuous-identical-dual', any(c['primary'] == c['secondary'] and c['secondary'] for c in cases), True)
check('nonvacuous-native-hit', any(e['kind'] == 'formula' for c in cases for e in c['events']), True)
report = dict(passed=not failures, romSha1=meta['romSha1'], assertions=sum(checks.values()),
    checks=dict(checks), failures=failures, nativeCasts=len(cases), cases=cases)
(OUT / 'mystic-fight-carriers.json').write_text(json.dumps(report, indent=2))
print(json.dumps({k: v for k, v in report.items() if k != 'cases'}, indent=2))
assert not failures, ('Native Fight carrier assumptions failed', len(failures))
