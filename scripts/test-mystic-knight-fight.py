"""Native enchanted Fight damage/resource carriers, with independent controls.

Damage oracles alter only the original item's element or target WDef; they do
not inject hit decisions or outcomes. Status/effect replacement has a separate
companion test. Standalone forecast, law and player-interface remain pending.
"""
import collections
import copy
import itertools
import json
import pathlib
import struct

ROOT = pathlib.Path(__file__).resolve().parents[1]
source = ROOT / 'scripts/test-mystic-knight-commands.py'
ns = {'__file__': str(source), '__name__': 'mystic_fight_fixture'}
exec(compile(source.read_text().split('# Native casts cover')[0], str(source), 'exec'), ns)
m, S, meta, OUT, A, T, STACK, regs, fixture, execute, call, half, record = (
    ns[x] for x in ('m', 'S', 'meta', 'OUT', 'A', 'T', 'STACK', 'regs', 'fixture', 'execute', 'call', 'half', 'record'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP

rom = pathlib.Path(meta['path']).read_bytes()
oracle = m.__class__(rom, m.read(0x03000000, 0x8000))
item_table = struct.unpack_from('<I', rom, 0xcbc74)[0]
checks, failures, samples = collections.Counter(), [], []
case = None
writes = {'actual': [], 'oracle': []}
scope_hits = []


def check(name, actual, expected):
    checks[name] += 1
    if actual != expected:
        failures.append(dict(case=case, check=name, actual=copy.deepcopy(actual), expected=copy.deepcopy(expected)))


def watch(label):
    def callback(u, pc, size, data):
        if u.reg_read(UC_ARM_REG_R0) == T:
            delta = u.reg_read(UC_ARM_REG_R1)
            writes[label].append(delta if delta < 0x80000000 else delta - 0x100000000)
    return callback


for machine, label in ((m, 'actual'), (oracle, 'oracle')):
    machine.u.hook_add(UC_HOOK_CODE, watch(label), begin=0x080a2210, end=0x080a2210)


def scope_observer(u, pc, size, data):
    # Observe the installed C callback after authentication, with no nested
    # emulator call from instrumentation and no changes to CPU state.
    pointer = struct.unpack('<I', m.read(0x0203f730, 4))[0]
    if 0x03000000 <= pointer <= 0x03007fec:
        scope_hits.append(struct.unpack('<5I', m.read(pointer, 20)))


m.u.hook_add(UC_HOOK_CODE, scope_observer, begin=S['ffta_myk_fight_kind'], end=S['ffta_myk_fight_kind'])
elements = (0, 1, 5, 6, 0, 0, 0, 0, 0, 0, 0, 7)


def clone_oracle(primary, kind):
    oracle.put(0x02000000, m.read(0x02000000, 0x40000))
    oracle.put(0x03000000, m.read(0x03000000, 0x8000))
    oracle.put(record(A) + 20, bytes(2))
    # Original item selector4 reads byte9. Restore the whole table on each
    # scenario so the independently changed element never leaks into another.
    offset = item_table - 0x08000000
    oracle.put(item_table, rom[offset:offset + 461 * 32])
    oracle.put(item_table + primary * 32 + 9, bytes((elements[kind],)))
    if kind == 8:
        oracle.put(T + 0x22, struct.pack('<H', half(T + 0x22) * 3 // 4))


def oracle_execute():
    oracle.put(regs[13], struct.pack('<4I', 0, 0, 0, 255))
    oracle.call(0x080a433c, regs[0], ns['wrappers'][A], 5, 14, stack=regs[13])


# Single-weapon execution covers every prepared element category and preserves
# native criticals, variance, physical defenses and resistance/absorption.
for kind, affinity, seed in itertools.product(range(1, 12), range(5), range(8)):
    case = ('native-single', kind, affinity, seed)
    fixture(0, seed)
    m.put(T + 0x0d, bytes((affinity,)) * 8)
    call('ffta_myk_grant', A, kind)
    clone_oracle(88, kind)
    writes['actual'].clear(); writes['oracle'].clear(); scope_hits.clear()
    execute(0); oracle_execute()
    check('native-damage-matches-independent-oracle', writes['actual'], writes['oracle'])
    check('enchantment-persists', call('ffta_myk_enchantment', A), kind)
    check('scope-restored', m.read(0x0203f730, 4).hex(), bytes(4).hex())
    removed = max(0, 500 - half(T + 0x18))
    check('Drain-recovery', half(A + 0x18), 100 + min(removed * 35 // 100, 75) if kind == 7 else 100)
    check('Osmose-target-MP', half(T + 0x1c), 99 - min(removed // 4, 10, 99) if kind == 10 else 99)
    check('Osmose-user-MP', half(A + 0x1c), min(100, 99 + min(removed // 4, 10)) if kind == 10 else 99)
    samples.append(dict(kind=kind, affinity=affinity, seed=seed, writes=list(writes['actual']), loss=removed))

# Equal, different and attack-reversed two-weapon execution. Compare each
# component against an unenchanted native control and a separately enchanted
# item control. Identical item IDs therefore cannot hide offhand leakage.
dual = []
for kind, pair, seed in itertools.product((1, 8, 7, 10), ((88, 88), (88, 89), (89, 88)), range(8)):
    primary, secondary = pair
    case = ('native-dual', kind, primary, secondary, seed)
    fixture(0, seed); ns['job'](A, 1, 7)
    m.put(A + 0x2a, struct.pack('<5H', primary, secondary, 0, 0, 0))
    m.put(T + 0x0d, b'\x04' * 8)
    first = m.call(0x080ca7a4, primary, 10, stack=STACK) & 255
    second = m.call(0x080ca7a4, secondary, 10, stack=STACK) & 255
    primary_index = int(second > first)
    # Capture actual native object identity even when a hit misses. HP writes
    # alone cannot identify the successful component in a one-hit outcome.
    frames = []
    def object_observer(u, pc, size, data):
        sp = u.reg_read(UC_ARM_REG_SP)
        frames.append((struct.unpack('<I', m.read(sp + 0x34, 4))[0], len(writes['actual'])))
    observer = m.u.hook_add(UC_HOOK_CODE, object_observer, begin=0x080a4852, end=0x080a4852)
    saved_ram = m.read(0x02000000, 0x40000); saved_iw = m.read(0x03000000, 0x8000)
    writes['actual'].clear(); execute(0); base = list(writes['actual'])
    m.put(0x02000000, saved_ram); m.put(0x03000000, saved_iw)
    call('ffta_myk_grant', A, kind); clone_oracle(primary, kind)
    writes['actual'].clear(); writes['oracle'].clear(); frames.clear()
    execute(0); oracle_execute()
    got, changed = list(writes['actual']), list(writes['oracle'])
    m.u.hook_del(observer)
    check('dual-native-hit-count-preserved', len(got), len(base))
    check('dual-control-hit-count-preserved', len(changed), len(base))
    eligible = set()
    for i, (index, start) in enumerate(frames):
        end = frames[i + 1][1] if i + 1 < len(frames) else len(got)
        if index == primary_index:
            eligible.update(range(start, end))
    if len(got) == len(base) == len(changed):
        expected = [changed[i] if i in eligible else base[i] for i in range(len(base))]
        check('only-equipment-primary-modified', got, expected)
    primary_loss = sum(max(0, got[i]) for i in eligible)
    check('dual-primary-Drain-only', half(A + 0x18), 100 + min(primary_loss * 35 // 100, 75) if kind == 7 else 100)
    check('dual-primary-Osmose-only', half(T + 0x1c), 99 - min(primary_loss // 4, 10) if kind == 10 else 99)
    check('dual-scope-retired', m.read(0x0203f730, 4).hex(), bytes(4).hex())
    dual.append(dict(kind=kind, pair=pair, seed=seed, primaryIndex=primary_index, base=base, actual=got, changed=changed))

for kind in (1, 2, 3, 8, 11):
    check('nonvacuous-kind-' + str(kind), any(s['kind'] == kind and s['loss'] > 0 for s in samples), True)
check('nonvacuous-different-primary-and-offhand', any(d['actual'] != d['base'] and d['actual'] != d['changed'] for d in dual), True)

# Resource amounts depend on actual HP removed, with independent target/user
# caps and undead reversal. Ally Fight retains HP behavior without recovery.
boundary_casts = 0
for kind, condition, hp_pair, mp_pair, seed in itertools.product(
        (7, 10), ('living', 'undead', 'zombie', 'ally'), ((100, 1), (490, 500)),
        ((0, 0), (20, 5), (99, 99)), (1, 3)):
    case = ('resource-boundaries', kind, condition, hp_pair, mp_pair, seed)
    actor_hp, target_hp = hp_pair; actor_mp, target_mp = mp_pair
    fixture(0, seed)
    ns['hp'](A, actor_hp, 500, actor_mp); ns['hp'](T, target_hp, 500, target_mp)
    m.put(A + 0x20, struct.pack('<H', 240))
    if condition == 'undead':
        m.put(T + 0x29, bytes((m.read(T + 0x29, 1)[0] | 8,)))
    elif condition == 'zombie':
        ns['grant'](T, 11)
    elif condition == 'ally':
        m.put(T + 0x29, b'\0')
    call('ffta_myk_grant', A, kind); execute(0); boundary_casts += 1
    removed = max(0, target_hp - half(T + 0x18)) if condition != 'ally' else 0
    reversed_drain = condition in ('undead', 'zombie')
    if kind == 7:
        amount = min(removed * 35 // 100, 75)
        expected_hp = max(0, actor_hp - amount) if reversed_drain else min(500, actor_hp + amount)
        check('Drain-actual-HP-cap-and-reversal', half(A + 0x18), expected_hp)
        check('Drain-keeps-user-MP', half(A + 0x1c), actor_mp)
        check('Drain-keeps-target-MP', half(T + 0x1c), target_mp)
    else:
        amount = min(removed // 4, 10, target_mp)
        check('Osmose-actual-target-cap', half(T + 0x1c), target_mp - amount)
        check('Osmose-user-cap-and-reversal', half(A + 0x1c),
            max(0, actor_mp - amount) if reversed_drain else min(100, actor_mp + amount))
        check('Osmose-keeps-user-HP', half(A + 0x18), actor_hp)

# An actual native Counter has its own result object and must not inherit a
# primary Fight scope, even when the reacting unit has an active blade.
counter_casts = 0
counter_hits = 0
for kind, seed in itertools.product((1, 7, 8, 10), range(8)):
    values = []
    for enchanted in (False, True):
        case = ('native-Counter-exclusion', kind, seed, enchanted)
        fixture(0, seed); ns['job'](T, 1, 1)
        bank = m.word(m.word(0x080cd538) + 4)
        index = next(i for i in range(142) if m.read(bank + 8 * i + 4, 3) == bytes((8, 0, 2)))
        m.put(T + 0x3a, bytes((index,))); m.put(T + 0x40 + index, b'\xff')
        check('Counter-fixture-is-native-reaction', m.call(0x080cd4d4, T, stack=STACK), 8)
        m.put(A + 0x0d, b'\x04' * 8)
        if enchanted:
            call('ffta_myk_grant', T, kind)
        execute(0); counter_casts += 1
        values.append([half(A + 0x18), half(A + 0x1c), half(T + 0x18), half(T + 0x1c)])
        counter_hits += half(A + 0x18) < 100
    check('native-Counter-no-enchant-or-resource-rider', values[1], values[0])
check('nonvacuous-native-Counter-hit', counter_hits > 0, True)

# Standalone forecasts have no authenticated component. They remain pure;
# native menu/AI transport is a separate explicit integration requirement.
for pointer in (0, 1, 0x02000080, 0x03000000, 0x03008000):
    case = ('invalid-scope', pointer); fixture(0); call('ffta_myk_grant', A, 1)
    m.put(0x0203f730, struct.pack('<I', pointer))
    before = m.read(A, 264) + m.read(record(A), 22) + m.read(0x030034b0, 4)
    check('invalid-scope-inert', call('ffta_myk_fight_kind', A, 88), 0)
    check('invalid-scope-read-only', m.read(A, 264) + m.read(record(A), 22) + m.read(0x030034b0, 4), before)
    check('invalid-scope-not-repaired', m.read(0x0203f730, 4), struct.pack('<I', pointer))

report = dict(passed=not failures, romSha1=meta['romSha1'], assertions=sum(checks.values()), checks=dict(checks),
    failures=failures, nativeCasts=len(samples) * 2 + len(dual) * 3 + boundary_casts + counter_casts, samples=samples, dual=dual,
    limits=['Status/effect replacement covered by companion test', 'Forecast/law/UI integration pending'])
(OUT / 'mystic-knight-fight.json').write_text(json.dumps(report, indent=2))
print(json.dumps({k: v for k, v in report.items() if k not in ('samples', 'dual')}, indent=2))
assert not failures, ('Mystic Fight execution failed', len(failures))
