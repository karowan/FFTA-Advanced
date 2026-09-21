"""Native acquisition gates under declared original progress, calendar and map inputs.

Exercises offline name-confirmation variants, renewable mission construction,
completion/reposting and the installed shop entry. Battle/dispatch outcomes
are controlled; no campaign, rendered reward or affordability claim is made.
"""
import ast
import atexit
import datetime
import hashlib
import json
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
meta = json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
rom = pathlib.Path(meta['path']).read_bytes()
sha = lambda b: hashlib.sha1(b).hexdigest()
assert sha(rom) == meta['romSha1']
base = pathlib.Path(meta['path']).parent
FIX = base/'fixture-two-geomancers'
proof = json.loads((FIX/'prepare-cache.json').read_text())
assert proof['inputs']['romSha1'] == meta['romSha1']
ram, iw = [(FIX/name).read_bytes() for name in ('battle-ready.ram', 'battle-ready.iwram')]
for name, value in (('battle-ready.ram', ram), ('battle-ready.iwram', iw)):
    assert sha(value) == proof['outputs'][name]
records = json.loads((ROOT/'build/reports/mission-item-dependencies.json').read_text())
assert records['candidateSha1'] == meta['romSha1']
records = records['installedRecords']
RETURN, STACK = 0x08000100, 0x03006800
tree = ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000', 'count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ARM'], type_ignores=[]), '<native ARM>', 'exec'))
m = ARM(rom, iw)
OUT = base/('original-source-gates-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
OUT.mkdir()
BUFFER, VIEW = 0x02030000, 0x02010000
checks, cases = [], []


def check(ok, label):
    assert ok, label
    checks.append(label)


def report(passed=False):
    if not passed:
        (OUT/'failure.ram').write_bytes(m.read(0x02000000, 0x40000))
    (OUT/'report.json').write_text(json.dumps(dict(passed=passed, romSha1=meta['romSha1'],
        assertions=len(checks), checks=checks, cases=cases, scope=__doc__,
        fixture=proof['outputs']), indent=2)+'\n')


atexit.register(report)
put32 = lambda p, v: m.put(p, struct.pack('<I', v))


def set_flag(index):
    p = 0x02001f70+(index >> 3)
    m.put(p, bytes((m.read(p, 1)[0] | (1 << (index & 7)),)))


def flag(index):
    return bool(m.read(0x02001f70+(index >> 3), 1)[0] & (1 << (index & 7)))


def reset():
    m.put(0x02000000, bytes(0x40000))
    m.put(0x02000080, ram[0x80:0x1940])
    m.put(0x03000000, iw)
    put32(0x03002810, VIEW)
    put32(VIEW, 0x02002c10)
    put32(VIEW+4, 0x02002c10)
    for location in range(1, 31):
        m.put(0x02002cc3+(location-1)*12, bytes((location,)))
    m.put(0x02002e58, b'\x03')
    m.put(0x02002fba, b'\x01')
    put32(0x030034b0, 0)


def queue():
    node, previous, result = m.word(0x020028c8), 0, {}
    while node:
        assert 0x020025c8 <= node < 0x020028c8 and (node-0x020025c8) % 12 == 0 and len(result) < 64
        ptr, prev, nxt = struct.unpack('<III', m.read(node, 12))
        assert prev == previous and 0x020021c8 <= ptr < 0x020025c8 and (ptr-0x020021c8) % 16 == 0
        mission = int.from_bytes(m.read(ptr, 2), 'little') & 1023
        assert mission and mission not in result
        result[mission] = ptr
        previous, node = node, nxt
    return result


def pub(ptr):
    towns = []
    for town in range(8):
        m.put(BUFFER+256, b'\xa5'*4)
        count = m.call(0x080d0590, BUFFER, 64, town)
        check(count <= 64 and m.read(BUFFER+256, 4) == b'\xa5'*4, f'Pub buffer bound:{town}')
        if ptr in struct.unpack('<64I', m.read(BUFFER, 256))[:count]:
            towns.append(town)
    return towns



clean = (ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
teaching = json.loads((ROOT/'build/reports/vanilla-teaching-sources.json').read_text())
renewable = json.loads((ROOT/'build/reports/mission-renewable-chains.json').read_text())
assert teaching['candidateSha1'] == renewable['candidateSha1'] == meta['romSha1']
MODE = sys.argv[1] if len(sys.argv) > 1 else 'all'
assert MODE in ('all', 'variants', 'renewable', 'pools', 'shops')


def name_confirm(kind, seed):
    # The real name task's confirmation call, stopped before graphics teardown.
    # Context+6 is copied from the two original task constructors' name kind.
    ctx = BUFFER+0x800
    m.put(ctx+6, bytes((kind,)))
    put32(0x030034b0, seed)
    m.u.reg_write(UC_ARM_REG_R6, ctx)
    m.u.reg_write(UC_ARM_REG_SP, STACK)
    m.u.emu_start(0x0812a3af, 0x0812a3b4, count=3000000)
    check(m.u.reg_read(UC_ARM_REG_PC) == 0x0812a3b4 and
          m.u.reg_read(UC_ARM_REG_SP) == STACK, f'Native name confirmation returns:{kind}/{seed}')
    expected = seed
    random = []
    for _ in range(3):
        expected = (expected*1103515245+12345) & 0xffffffff
        random.append((expected >> 16) & 0x7fff)
    check(m.word(0x02002168 if kind else 0x0200216c) == random[0] | (random[1] << 16),
          f'Native identity generated:{kind}/{seed}')
    check(flag(1445 if kind else 1446) == bool(random[2] & 1), f'Native variant flag generated:{kind}/{seed}')


if MODE in ('all', 'variants'):
    for lo, hi in ((0xcea80, 0xceb34), (0x12a3ae, 0x12a3b4),
                   (0x12b208, 0x12b258), (0x2804, 0x2824)):
        check(rom[lo:hi] == clean[lo:hi], f'Original naming and RNG code:{lo:x}')
    for first in (0, 1):
        for second in (0, 1):
            reset()
            name_confirm(1, first)
            name_confirm(0, second)
            # Original story qualifications for the three optional families.
            set_flag(778); set_flag(779)
            m.call(0x080cfcd0, 0)
            entries = queue()
            actual = sorted(mid for mid in entries if 326 <= mid <= 331)
            expected = {(0, 0): [326], (0, 1): [328], (1, 0): [330], (1, 1): [327, 329, 331]}[first, second]
            check(actual == expected, f'Offline variant offers:{first}/{second}')
            for mid in actual:
                check(bool(pub(entries[mid])), f'Offline variant is listed:{mid}')
            cases.append(dict(kind='offline-name-variants', seeds=[first, second], missions=actual))


POOL_MISSIONS = [215, 219, 235, 217, 218, 132, 131]
if MODE in ('all', 'renewable'):
    witnesses = {row['mission']: row for row in renewable['witnesses']}
    for mid in POOL_MISSIONS:
        if mid not in witnesses:
            witnesses[mid] = dict(positiveFlags=[c['index'] for c in records[mid]['unlock']
                                                if c['selector'] and c['value'] == 1])
    for mid, witness in witnesses.items():
        row = records[mid]
        assert row['repeatable'] and row['pubEnabled']
        reset()
        m.put(0x02002fba, bytes((row['pubMonth'] or 1,)))
        # First test without the source's direct story gate. Ingredient-chain
        # qualifications do not manufacture the source's own completion gate.
        direct = next(c['index'] for c in row['unlock'] if c['selector'] and c['value'] == 1)
        for index in witness['positiveFlags']:
            if index != direct: set_flag(index)
        m.call(0x080cfcd0, 0)
        check(mid not in queue(), f'Original story gate blocks early posting:{mid}')
        set_flag(direct)
        m.call(0x080cfcd0, 0)
        entries = queue()
        check(mid in entries, f'Original qualifications construct source:{mid}')
        ptr = entries[mid]
        check(bool(pub(ptr)), f'Original qualified source listed:{mid}')
        rewards = list(struct.unpack('<HH', m.read(ptr+8, 4)))
        for slot, value in enumerate(row['rewards']):
            if value < 0xfff1:
                check(rewards[slot] == value, f'Original fixed reward:{mid}/{slot}')
            else:
                pool = 7 if value == 0xffff else value-0xfff1
                allowed = struct.unpack_from('<20H', rom, 0x529494+40*pool)
                check(rewards[slot] in allowed, f'Original constructed random reward:{mid}/{slot}')
        # Required items are explicit inputs; the fixed-point source proof
        # establishes their independent routes. Native binding/consumption is
        # covered by the existing requirement consumer matrix.
        reqs = [r['localId'] for r in row['requirements']]
        for n, item in enumerate(reqs):
            m.put(0x02002b08+n*4, struct.pack('<BBH', item, 1, mid))
        m.call(0x080d0b48, ptr, 0x02000188 if row['type'] & 7 == 0 else 0,
               *(reqs+[0, 0])[:2])
        m.call(0x080d1e70, ptr, 1)
        check(flag(mid+0x2ff), f'Native completion records original source:{mid}')
        cooldown = rom[0x55ae4c+mid*70+63]
        for day in range(cooldown+1): m.call(0x080cf51c)
        m.call(0x080cfcd0, 0)
        check(mid in queue() and bool(pub(queue()[mid])), f'Completed original source posts again:{mid}')
        cases.append(dict(kind='renewable-original-source', mission=mid, positiveFlags=witness['positiveFlags'],
                          month=row['pubMonth'], requirements=reqs, rewards=rewards, cooldown=cooldown))

if MODE in ('all', 'pools'):
    # Use an independent machine for this interior instruction block. Earlier
    # whole-function execution can cache a translation across the stop address;
    # the standalone selector does not inherit campaign scratch registers.
    m = ARM(rom, iw)
    # Twenty fixed seeds exhaust the native slot selector without changing RNG
    # outputs. The actual record selects its pool; the original second-reward
    # block is executed from the RNG call through the cache write.
    seeds = {}
    for seed in range(1000):
        slot = (((seed*1103515245+12345) & 0xffffffff) >> 16 & 0x7fff) % 20
        seeds.setdefault(slot, seed)
    assert len(seeds) == 20
    observed = set()
    for pool, mid in enumerate(POOL_MISSIONS):
        record = 0x0855ae4c+mid*70
        assert records[mid]['rewards'][1] == 0xfff1+pool
        values = []
        for slot, seed in sorted(seeds.items()):
            put32(0x030034b0, seed)
            for reg, value in ((UC_ARM_REG_R4, record+0x25), (UC_ARM_REG_R7, record+0x24),
                               (UC_ARM_REG_R6, BUFFER), (UC_ARM_REG_SP, STACK)):
                m.u.reg_write(reg, value)
            m.u.emu_start(0x080d00c7, 0x080d010a, count=3000000)
            check(m.u.reg_read(UC_ARM_REG_PC) == 0x080d010a and m.u.reg_read(UC_ARM_REG_SP) == STACK,
                  f'Native pool selector returns:{pool}/{slot}')
            value = int.from_bytes(m.read(BUFFER+10, 2), 'little')
            check(value == struct.unpack_from('<H', rom, 0x529494+40*pool+2*slot)[0],
                  f'Native seeded reward matches slot:{pool}/{slot}')
            values.append(value); observed.add(value)
        cases.append(dict(kind='random-reward-pool', mission=mid, pool=pool, seeds=seeds, items=values))
    teachers = [r for r in teaching['rows'] if r['lessons'] and not (r['ordinaryTiers'] or r['specialStock'])
                and any(p['index'] < 7 and p['originalMissions'] for p in r['randomPools'])]
    check(len(teachers) == 70 and all(r['id'] in observed for r in teachers), 'All70 original random-pool teachers have renewable native witnesses')


if MODE in ('all', 'shops'):
    reset()
    teachers = {r['id'] for r in teaching['rows'] if r['lessons'] and (r['ordinaryTiers'] or r['specialStock'])}
    check(len(teachers) == 109, 'Original shop-teacher domain')
    all_seen = set()
    for territory in (0, 30):
        for n in range(30): m.put(0x02002cc1+n*12, bytes((3 if n < territory else 0,)))
        check(m.call(0x080cecf4) == territory, f'Original liberated-territory count:{territory}')
        for tier in (0, 20):
            for town in range(2, 7):
                seen = set()
                for tab in range(6):
                    m.put(BUFFER, bytes(2048)); m.put(BUFFER+2048, b'\xa5'*4)
                    count = m.call(0x080cbdc0, BUFFER, tab, tier, town)
                    check(count < 256 and m.read(BUFFER+2048, 4) == b'\xa5'*4,
                          f'Installed shop bound:{territory}/{tier}/{town}/{tab}')
                    ids = struct.unpack('<'+'HBB'*count, m.read(BUFFER, count*4))[::3]
                    seen.update(item for item in ids if item <= 375)
                if territory == 30 and tier == 20: all_seen.update(seen)
                cases.append(dict(kind='shop-stock', territory=territory, tierKey=tier, town=town,
                                  originalTeachers=sorted(teachers & seen)))
    check(teachers <= all_seen, f'All109 original shop teachers remain buyable at late tier:{sorted(teachers-all_seen)}')

report(True)
atexit.unregister(report)
print(json.dumps(dict(passed=True, mode=MODE, assertions=len(checks), cases=len(cases), report=str(OUT/'report.json'))))
