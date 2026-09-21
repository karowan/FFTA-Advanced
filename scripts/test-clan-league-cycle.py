"""Original Clan League/color-clan posting and completion cycle.

Late story completion and the first earned League qualification are declared
inputs. Native generators, acceptance, completion effects, cooldowns and pub
enumeration supply every subsequent opportunity. Success/failure is a controlled
completion input; this does not simulate winning battles or recruit dialogs.
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
OUT = base/('clan-league-cycle-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
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
    m.put(0x02002fba, b'\x01')  # Native Yellow Powerz calendar requirement.
    set_flag(54)
    set_flag(24+0x2ff)
    set_flag(1411)
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


for missed_brown in ((True,) if '--missed-only' in sys.argv else (False, True)):
    reset()
    # A full win cycle qualifies for another League. A failed Brown Rabbits
    # still advances through the remaining colors, then restarts Yellow.
    path = [46, 107, 108, 109, 110]+([107, 108, 109] if missed_brown else [46, 107, 108, 109])
    for step, mission in enumerate(path):
        m.call(0x080cfcd0, 0)
        entries = queue()
        check(mission in entries, f'Native next offer:{missed_brown}/{step}/{mission}')
        ptr = entries[mission]
        towns = pub(ptr)
        deferred_days = 0
        if not towns:
            pending = m.read(ptr, 16)
            check(pending[2] & 0x1c == 12 and 0 < pending[3] < 255,
                  f'Unavailable repeat has a native cooldown:{missed_brown}/{step}/{mission}')
            deferred_days = pending[3]
            for day in range(deferred_days):
                m.call(0x080cf51c)
            m.call(0x080cfcd0, 0)
            check(mission in queue(), f'Cooldown returns source:{missed_brown}/{step}/{mission}')
            ptr = queue()[mission]
            towns = pub(ptr)
        check(bool(towns), f'Native pub exposes offer:{missed_brown}/{step}/{mission}')
        m.call(0x080d0b48, ptr, 0, 0, 0)
        check(m.read(ptr+2, 1)[0] & 0x1c == 0, f'Native acceptance:{missed_brown}/{step}/{mission}')
        if mission == 109:
            event_id = records[109]['event']
            m.call(0x08009c18, 0x08563a70+event_id*12, records[109]['eventLocation'])
            formation = m.call(0x0800a024)
            check(formation == 273, f'Native Brown Rabbits enemy formation:{missed_brown}/{step}')
            at = 0x54cd54+formation*40
            units = struct.unpack_from('<I', rom, at+4)[0] & 0x1ffffff
            witnesses = [(slot, gear) for slot in range(rom[at]) for gear in range(5)
                         if struct.unpack_from('<H', rom, units+48*slot+8+gear*2)[0] == 183]
            check(bool(witnesses), f'Actual selected formation contains Oathbow:{missed_brown}/{step}')
        success = not (missed_brown and step == 3)
        m.call(0x080d1e70, ptr, int(success))
        if mission == 110:
            check(flag(1410 if missed_brown else 1411), f'Native cycle chooses next qualification:{missed_brown}')
            check(m.read(0x020020b1, 1) == b'\0', f'Native cycle resets its four-result counter:{missed_brown}')
        # Let native cooldown/retirement run; no queue clearing or entitlement
        # flags are supplied between missions. Retire accepted encounter slots
        # only once their own native completion has marked them for removal.
        for day in range(rom[0x55ae4c+mission*70+64]+1):
            m.call(0x080cf51c)
        for slot in range(5):
            q = 0x02002e34+6*slot
            row = m.read(q, 6)
            if row[0] & 7 and row[2] & 64:
                m.call(0x080d0f74, q)
        cases.append(dict(missedBrown=missed_brown, step=step, mission=mission, success=success,
                          towns=towns, deferredDays=deferred_days, nextYellow=flag(1410), nextLeague=flag(1411),
                          counter=m.read(0x020020b1, 1)[0]))

check(len(cases) == (8 if '--missed-only' in sys.argv else 17), 'Selected native cycles and repeated Oathbow opportunities complete')
report(True)
atexit.unregister(report)
print(json.dumps(dict(passed=True, assertions=len(checks), cases=len(cases), report=str(OUT/'report.json'))))
