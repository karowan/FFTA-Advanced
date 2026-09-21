"""Native primary Fight status timing and weapon-effect replacement.

Fixed executor inputs; no injected rolls, damage, status or action result.
The independent status control uses the already accepted command S stage on
the observed post-damage state. Disposable item variants test native effects.
"""
import collections
import itertools
import json
import pathlib
import struct

ROOT = pathlib.Path(__file__).resolve().parents[1]
source = ROOT / 'scripts/test-mystic-knight-commands.py'
ns = {'__file__': str(source), '__name__': 'mystic_fight_status_fixture'}
exec(compile(source.read_text().split('# Native casts cover')[0], str(source), 'exec'), ns)
m, S, meta, OUT, A, T, STACK, regs, fixture, execute, call, half, record = (
    ns[x] for x in ('m', 'S', 'meta', 'OUT', 'A', 'T', 'STACK', 'regs', 'fixture', 'execute', 'call', 'half', 'record'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1

rom = pathlib.Path(meta['path']).read_bytes()
oracle = m.__class__(rom, m.read(0x03000000, 0x8000))
item_table = m.word(0x080cbc74)
checks, failures, counts = collections.Counter(), [], collections.Counter()
case, captured, writes = None, [], []
native_casts = 0


def check(name, actual, expected):
    checks[name] += 1
    if actual != expected:
        failures.append(dict(case=case, check=name, actual=repr(actual), expected=repr(expected)))


def watch(u, pc, size, data):
    if u.reg_read(UC_ARM_REG_R0) == T:
        n = u.reg_read(UC_ARM_REG_R1)
        writes.append(n if n < 0x80000000 else n - 0x100000000)


def observe_status(u, pc, size, data):
    if u.reg_read(UC_ARM_REG_R1) != T:
        return
    obj = u.reg_read(UC_ARM_REG_R0)
    scope = m.word(0x0203f730)
    if 0x03000000 <= scope <= 0x03007fe8:
        state = struct.unpack('<6I', m.read(scope, 24))
        if state[0] == scope and state[1:3] == (A, obj) and state[5] == T:
            captured.append((m.read(0x02000000, 0x40000), m.read(0x03000000, 0x8000), state))


observer = m.u.hook_add(UC_HOOK_CODE, observe_status, begin=S['ffta_myk_fight_status'], end=S['ffta_myk_fight_status'])
m.u.hook_add(UC_HOOK_CODE, watch, begin=0x080a2210, end=0x080a2210)


def native_lesson(unit, native_id, typ):
    race = m.read(unit + 6, 1)[0]
    bank = m.word(m.word(0x080cd538) + race * 4)
    index = next(i for i in range(142) if m.read(bank + 8 * i + 4, 3) == bytes((native_id, 0, typ)))
    m.put(unit + (0x3a if typ == 2 else 0x3b), bytes((index,)))
    m.put(unit + 0x40 + index, b'\xff')


def restore_items(machine):
    start = item_table - 0x08000000
    machine.put(item_table, rom[start:start + 461 * 32])


def run():
    global native_casts
    execute(0)
    native_casts += 1


statuses = {4: (125, 9), 5: (97, 26), 6: (111, 27), 9: (104, 22)}
samples = []
for kind, condition, seed in itertools.product(statuses, (
        'normal', 'asleep', 'astra', 'inoculated', 'immune', 'warcry',
        'ally', 'lethal', 'zero', 'damage-mp', 'healer', 'restorative', 'silenced'), range(16)):
    case = ('status', kind, condition, seed)
    restore_items(m); fixture(0, seed)
    if condition == 'asleep': ns['grant'](T, 26)
    if condition == 'astra': ns['grant'](T, 4)
    if condition == 'inoculated': call('ffta_inoculated_grant', T, 0)
    if condition == 'warcry': call('ffta_viking_grant_war_cry', T, 0)
    if condition == 'immune':
        ns['job'](T, 1, 2); native_lesson(T, 11, 3)
        check('native-Immunity-assigned', m.call(0x080cd50c, T, stack=STACK), 11)
    if condition == 'ally': m.put(T + 0x29, b'\0')
    if condition == 'lethal': ns['hp'](T, 1, 500, 99)
    if condition == 'zero': ns['grant'](T, 33)  # native direct-HP nullification
    if condition == 'damage-mp':
        ns['job'](T, 1, 2); native_lesson(T, 13, 2)
        m.put(T + 0x1c, struct.pack('<HH', 999, 999))
    if condition == 'healer':
        m.put(A + 0x2a, struct.pack('<H', 124))  # actual native restorative staff
        check('native-Healer-is-restorative', m.call(0x08130620, 124, stack=STACK), 1)
    if condition == 'restorative': m.put(item_table + 88 * 32 + 26, b'\x3f\0\0')
    if condition == 'silenced': ns['grant'](A, 27)
    call('ffta_myk_grant', A, kind)
    captured.clear(); writes.clear(); run()
    check('single-primary-status-opportunity', len(captured) <= 1, True)
    if captured:
        ram, iw, scope = captured[0]
        oracle.put(0x02000000, ram); oracle.put(0x03000000, iw)
        restore_items(oracle)
        def oc(address, *args): return oracle.call(address, *args, stack=STACK)
        def oh(address): return int.from_bytes(oracle.read(address, 2), 'little')
        descriptor, status = statuses[kind]
        eligible = oh(T + 0x18) > 0
        if eligible:
            c = 0x0200f3f0
            # Use the accepted immediate enchantment's status stage as the
            # independent formula, with no command payment or damage stage.
            oc(0x0812f2a4, 409 + kind, scope[3], 1)
            oracle.put(c, struct.pack('<III', A, T, T))
            oc(0x0812f328, 1)
            # Native original descriptor eligibility, bypassing only the
            # command's separate positive-loss ledger (observed above).
            eligible = bool(oc(0x08130a94, c))
            if eligible:
                chance = oc(0x08131378)
                if chance and oc(0x080c8240, A) == 0: chance = min(100, chance + 10)
                if oc(0x0812f1dc, chance): oc(0x0813388c)
        actual = m.read(T + 0xe8, 8)
        expected = oracle.read(T + 0xe8, 8)
        check('native-S-stage-status-and-timers', actual, expected)
        counts[(kind, condition, 'attempt')] += eligible
    status = statuses[kind][1]
    landed = ns['bit'](T, status)
    counts[(kind, condition, 'landed')] += landed
    if condition in ('lethal', 'zero', 'damage-mp', 'healer', 'restorative', 'astra'):
        check('excluded-status-' + condition, landed, False)
    if condition in ('inoculated', 'immune') and kind != 9:
        check('curable-status-prevention', landed, False)
    if condition == 'astra':
        check('Astra-consumes-on-positive-HP-status-opportunity', ns['bit'](T, 4), not bool(captured))
    if condition in ('zero', 'damage-mp', 'healer', 'restorative'):
        check('fixture-really-has-no-HP-loss-' + condition, half(T + 0x18), 500)
    check('persistent-enchantment-retained', call('ffta_myk_enchantment', A), 0 if condition == 'healer' else kind)
    check('scope-cleanup', m.word(0x0203f730), 0)
    samples.append(dict(kind=kind, condition=condition, seed=seed, landed=landed, writes=list(writes)))

for kind in statuses:
    for condition in ('normal', 'silenced', 'ally'):
        check('nonvacuous-status-' + str(kind) + '-' + condition, counts[(kind, condition, 'landed')] > 0, True)
check('new-Sleep-survives-wake-cleanup', counts[(5, 'asleep', 'landed')] > 0, True)

for kind, seed in itertools.product(statuses, range(16)):
    case = ('command-Astra', kind, seed)
    fixture(409 + kind, seed); ns['grant'](T, 4)
    execute(409 + kind); native_casts += 1
    check('command-Astra-consumes-on-positive-damage', ns['bit'](T, 4), half(T + 0x18) == 500)
    check('command-Astra-blocks-status', ns['bit'](T, statuses[kind][1]), False)

dual_opportunities = collections.Counter()
for kind, pair, seed in itertools.product(statuses, ((88, 88), (88, 89), (89, 88)), range(16)):
    case = ('dual-status', kind, pair, seed)
    restore_items(m); fixture(0, seed); ns['job'](A, 1, 7)
    m.put(A + 0x2a, struct.pack('<5H', *pair, 0, 0, 0)); call('ffta_myk_grant', A, kind)
    captured.clear(); writes.clear(); run()
    check('dual-at-most-one-primary-status-attempt', len(captured) <= 1, True)
    for ram, iw, scope in captured:
        check('dual-status-exact-primary-item', scope[3], pair[0])
        check('dual-status-exact-enchantment', scope[4], kind)
        dual_opportunities[pair] += 1
    check('dual-scope-restored', m.word(0x0203f730), 0)
for pair in ((88, 88), (88, 89), (89, 88)):
    check('nonvacuous-dual-status-' + str(pair), dual_opportunities[pair] > 0, True)
m.u.hook_del(observer)

counter_hits = 0
for kind, seed in itertools.product(statuses, range(16)):
    case = ('status-Counter', kind, seed)
    values = []
    for enchanted in (False, True):
        restore_items(m); fixture(0, seed); ns['job'](T, 1, 1)
        native_lesson(T, 8, 2)
        if enchanted: call('ffta_myk_grant', T, kind)
        run(); counter_hits += half(A + 0x18) < 100
        values.append((m.read(A + 0x18, 8), m.read(A + 0xe8, 8), m.read(T + 0x18, 8), m.read(T + 0xe8, 8)))
    check('native-Counter-no-status-rider', values[0], values[1])
check('nonvacuous-native-Counter', counter_hits > 0, True)

# Reverse the real actor/recipient wrappers so the player inventory belongs to
# the recipient. Compare fixed-seed enemy attacks with/without Auto-Cureall;
# the control establishes whether a curable status really landed.
stock = 0x02001940 + 374
auto_spends = 0
for kind, inoculated, quantity, seed in itertools.product(statuses, (False, True), (0, 3), range(16)):
    case = ('native-Auto-Cureall', kind, inoculated, quantity, seed)
    values = []
    for automatic in (False, True):
        restore_items(m); fixture(0, seed)
        ns['job'](A, 3, 120)
        if automatic: ns['equip'](A, 'CHM-R2')
        if inoculated: call('ffta_inoculated_grant', A, 0)
        m.put(stock, bytes((quantity,)))
        call('ffta_myk_grant', T, kind)
        m.put(regs[13], struct.pack('<4I', 0, 0, 0, 255))
        m.call(0x080a433c, regs[0], ns['wrappers'][T], 4, 14, stack=regs[13]); native_casts += 1
        values.append((ns['bit'](A, statuses[kind][1]), m.read(stock, 1)[0], half(A + 0x18)))
    expected_spend = int(values[0][0] and kind != 9 and quantity > 0 and not inoculated)
    check('Auto-Cureall-one-item-on-real-curable-success', quantity - values[1][1], expected_spend)
    check('Auto-Cureall-keeps-HP-damage', values[1][2], values[0][2])
    check('Auto-Cureall-native-status-outcome', values[1][0], values[0][0] and not expected_spend)
    auto_spends += expected_spend
check('nonvacuous-native-Auto-Cureall-spends', auto_spends > 0, True)

# Every native equipment effect remains an equipment property. Enchantments
# replace only the primary hit's ordinary drain/proc (3D/3E); never erase
# equipment immunity/affinity or restorative3F. Compare the same candidate with
# only the actual on-hit effect removed in a disposable original item row.
effects = sorted(set(rom[item_table - 0x08000000 + i * 32 + j]
                     for i in range(1, 461) for j in (26, 27, 28)) | {0x3d, 0x3e, 0x3f})
weapon_samples = []
for effect, kind, undead, seed in itertools.product(effects, (1, 7, 10), (False, True), (1, 3)):
    case = ('weapon-effect', effect, kind, undead, seed)
    values = []
    for stripped in (False, True):
        restore_items(m); fixture(0, seed)
        m.put(item_table + 88 * 32 + 26, bytes((0 if stripped and effect in (0x3d, 0x3e) else effect, 0, 0)))
        if undead: m.put(T + 0x29, bytes((m.read(T + 0x29, 1)[0] | 8,)))
        ns['grant'](T, 20)  # native effect3E's removal target
        call('ffta_myk_grant', A, kind); run()
        check('no-original-on-hit-status-or-removal', m.read(T + 0xe8, 8), bytes.fromhex('0000100000000000'))
        values.append((m.read(A + 0x18, 8), m.read(T + 0x18, 8), m.read(A + 0xe8, 8), m.read(T + 0xe8, 8)))
    check('native-effect-replacement-and-property-preservation', values[0], values[1])
    weapon_samples.append(dict(effect=effect, kind=kind, undead=undead, seed=seed,
                               result=[x.hex() for x in values[0]]))
restore_items(m)

# A restorative component must not turn into damage/drain when elemental
# absorption and native healing would otherwise cancel their sign reversals.
for kind, affinity, seed in itertools.product(range(1, 12), range(5), (1, 3)):
    case = ('restorative-affinity', kind, affinity, seed)
    fixture(0, seed); m.put(item_table + 88 * 32 + 26, b'\x3f\0\0')
    m.put(T + 0x0d, bytes((affinity,)) * 8)
    call('ffta_myk_grant', A, kind); run()
    check('restorative-cannot-damage', half(T + 0x18), 500)
    check('restorative-cannot-drain-user-HP', half(A + 0x18), 100)
    check('restorative-cannot-drain-user-MP', half(A + 0x1c), 99)
    check('restorative-cannot-drain-target-MP', half(T + 0x1c), 99)
restore_items(m)

# Unenchanted controls establish that the ordinary effects remain active.
ordinary = collections.Counter()
for effect, seed in itertools.product((0x3d, 0x3e), range(16)):
    case = ('ordinary-weapon-effects', effect, seed)
    fixture(0, seed); m.put(item_table + 88 * 32 + 26, bytes((effect, 0, 0)))
    ns['grant'](T, 20); run()
    if effect == 0x3d: ordinary[effect] += half(A + 0x18) > 100
    else: ordinary[effect] += not ns['bit'](T, 20)
for effect in (0x3d, 0x3e): check('nonvacuous-unenchanted-effect-' + str(effect), ordinary[effect] > 0, True)
restore_items(m)
report = dict(passed=not failures, romSha1=meta['romSha1'], assertions=sum(checks.values()),
              checks=dict(checks), nativeCasts=native_casts, failures=failures, samples=samples,
              nativeItemEffects=effects, weaponSamples=weapon_samples,
              limits=['Standalone preview/law/player interface are separate obligations',
                      'Weapon matrix covers declared native effect bytes, not future added effects'])
(OUT / 'mystic-knight-fight-status.json').write_text(json.dumps(report, indent=2))
print(json.dumps({k: v for k, v in report.items() if k not in ('samples', 'weaponSamples')}, indent=2))
assert not failures, ('Mystic Fight status/effect failures', len(failures))
