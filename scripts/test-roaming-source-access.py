"""Native roaming generation, map lookup and current content-source coverage.

Declared world inputs: all thirty locations placed in two permutations, no
displayed clan actors, progression counters, queue occupancy and fixed RNG seeds.
Reuse only authenticated boot-installed IWRAM from the exact candidate capture;
do not pass a battle RAM image off as a campaign fixture. Run original routines
without replacing callbacks, their results, or generated queue entries.
This is native selection evidence, not a campaign or rendered world-map replay.
"""
import ast
import atexit
import collections
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

sha = lambda data: hashlib.sha1(data).hexdigest()
meta = json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
rom = pathlib.Path(meta['path']).read_bytes()
assert sha(rom) == meta['romSha1']
clean = (ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
base = pathlib.Path(meta['path']).parent
fix = base/'fixture-two-geomancers'
proof = json.loads((fix/'prepare-cache.json').read_text())
assert proof['inputs']['romSha1'] == meta['romSha1']
iw = (fix/'battle-ready.iwram').read_bytes()
assert sha(iw) == proof['outputs']['battle-ready.iwram']
ledger = json.loads((ROOT/'build/expansion/probes/monster-access/sources.json').read_text())
assert ledger['romSha1'] == meta['romSha1']
RETURN, STACK = 0x08000100, 0x03006800
tree = ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000', 'count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ARM'], type_ignores=[]), '<native ARM>', 'exec'))
m = ARM(rom, iw)
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
OUT = base/('roaming-access-'+stamp)
OUT.mkdir()
Q, VIEW, TYPE = 0x02002e34, 0x02010000, 0x02011000
checks, cases, coverage = [], [], {}
lifecycle_only = '--lifecycle-only' in sys.argv


def check(value, label):
    assert value, label
    checks.append(label)


def report(passed=False):
    data = dict(passed=passed, romSha1=meta['romSha1'], assertions=len(checks),
                checks=checks, cases=cases, coverage=coverage, scope=__doc__,
                iwram=dict(path=str(fix/'battle-ready.iwram'), sha1=sha(iw)),
                sourceLedgerSha1=sha((ROOT/'build/expansion/probes/monster-access/sources.json').read_bytes()),
                limits=['Queue retirement is covered only in lifecycle mode; rendered world-map/campaign flow is separate.',
                        'Absent roaming gear is reported for repeatable mission follow-up, not declared unobtainable.',
                        'Learning, Capture and theft consumers retain their separate evidence.'])
    (OUT/'report.json').write_text(json.dumps(data, indent=2)+'\n')
    return data


atexit.register(report)
u16 = lambda p: struct.unpack_from('<H', rom, p)[0]
u32 = lambda p: struct.unpack_from('<I', rom, p)[0]
put32 = lambda p, v: m.put(p, struct.pack('<I', v))
weights = list(rom[0x563a50:0x563a6e])
check(len(weights) == 30 and min(weights) > 0, 'Every location has a positive native selection weight')
for start, end in ((0xcf690, 0xcfa48), (0x36330, 0x364bc), (0xd17c4, 0xd1a18),
                   (0x9c04, 0x9c94), (0x2804, 0x2824)):
    check(rom[start:end] == clean[start:end], f'Original encounter consumer:{start:x}')
check(rom[0xcfcec:0xcfcf4] == clean[0xcfcec:0xcfcf4], 'Daily caller retains aging then generation')


def reset(reverse=False, progress=255, placed=True):
    m.put(0x02000000, bytes(0x40000))
    m.put(0x03000000, iw)
    put32(0x03002810, VIEW)
    # The view contains no currently displayed actors. Placement table records
    # map locations by ID, with a one-based physical position in byte+3.
    for location in range(1, 31):
        m.put(0x02002cc3+(location-1)*12,
              bytes((31-location if reverse else location,)) if placed else b'\0')
    m.put(0x02002190, bytes((progress,)))
    m.put(0x02002e58, b'\x03')


def event(row):
    return (row[2] >> 7) | ((row[3] & 127) << 1)


def queue():
    data = m.read(Q, 30)
    return [data[i:i+6] for i in range(0, 30, 6) if data[i] & 7]


def seed_for(location, occupancy=0):
    # A bounded host reference selects fixed inputs, never native results.
    lo, hi = sum(weights[:location-1]), sum(weights[:location])
    for seed in range(100000):
        first = (seed*0x41c64e6d+12345) & 0xffffffff
        second = (first*0x41c64e6d+12345) & 0xffffffff
        if ((first >> 16) & 32767) % 100 <= rom[0x563a4c+occupancy] and lo <= ((second >> 16) & 32767) % sum(weights) < hi:
            return seed
    raise AssertionError('No declared seed')


def generate(location, occupancy=0):
    seed = seed_for(location, occupancy)
    put32(0x030034b0, seed)
    m.call(0x080cf7f4)
    return seed


for progress, placed in (() if lifecycle_only else ((0, True), (4, True), (255, False))):
    reset(progress=progress, placed=placed)
    put32(0x030034b0, 0)
    m.call(0x080cf7f4)
    check(not queue(), f'No spawn before gate/without placements:{progress}/{placed}')

for reverse in (() if lifecycle_only else (False, True)):
    for location in range(1, 31):
        reset(reverse=reverse)
        seed = generate(location)
        rows = queue()
        expected_event = 225+location
        position = 31-location if reverse else location
        check(len(rows) == 1 and event(rows[0]) == expected_event, f'Native selected event:{reverse}/{location}')
        check(rows[0][2] & 31 == position, f'Placed position survives permutation:{reverse}/{location}')
        check(rows[0][5] >> 1 == 6, f'Native six-day initial lifetime:{reverse}/{location}')
        prior = m.read(Q, 30)
        generate(location, 1)
        check(m.read(Q, 30) == prior, f'No duplicate active clan:{reverse}/{location}')
        m.call(0x080cf690)
        check(not (queue()[0][1] & 128), f'New encounter visible after native aging:{reverse}/{location}')
        m.put(TYPE, b'\xff')
        found = m.call(0x080d17c4, location, position, TYPE)
        check(found == expected_event and m.read(TYPE, 1) == b'\x03', f'Native map lookup selects generated roaming event:{reverse}/{location}')
        m.call(0x08009c18, 0x08563a70+found*12, location)
        formations = struct.unpack('<HH', m.read(0x02002170, 4))
        check(formations == (u16(0x563a70+found*12+2), u16(0x563a70+found*12+4)),
              f'Native initial event-to-formation pair:{reverse}/{location}')
        check(m.call(0x0800a018) == formations[0] and m.call(0x0800a024) == formations[1],
              f'Native formation selectors:{reverse}/{location}')
        other_location = location % 30+1
        m.call(0x08009c18, 0x08563a70+found*12, other_location)
        check(m.call(0x0800a018) == u16(0x563a70+(225+other_location)*12+2),
              f'Movement changes map/deployment formation:{reverse}/{location}')
        check(m.call(0x0800a024) == formations[1], f'Movement retains actual clan enemy roster:{reverse}/{location}')
        cases.append(dict(location=location, position=position, reverse=reverse, seed=seed,
                          event=found, formations=list(formations), queueHex=m.read(Q, 30).hex()))

# Fill capacity with real generator outputs; the fourth blocks further spawns.
if not lifecycle_only:
    reset()
    for location in range(1, 5):
        generate(location, location-1)
        check(len(queue()) == location, f'Native occupancy:{location}')
    prior = m.read(Q, 30)
    put32(0x030034b0, seed_for(5))
    m.call(0x080cf7f4)
    check(m.read(Q, 30) == prior, 'Four occupied slots block an additional random encounter')

if lifecycle_only:
    # D0FB2's installed mission-completion hook is outside the roaming branch;
    # authenticate the entry and direct retirement branch, not that mission arm.
    for start, end in ((0xd2e6c, 0xd2e78), (0xd0f74, 0xd0f94), (0xd11f8, 0xd1218), (0x30168, 0x301b0)):
        check(rom[start:end] == clean[start:end], f'Original queue lifecycle consumer:{start:x}')
    # Native UI callers clear the new flag at32E4C, retire an expired entry at
    #33162, and mark the selected battle entry at30168. These calls below run
    #the same complete consumers. Animation/scene orchestration is separate.
    for location in range(1, 31):
        for completed_battle in (False, True):
            reset()
            # Declare all ordinary mission completion receipts already earned.
            for mission in range(1, 407):
                index = mission+0x2ff
                address = 0x02001f70+(index >> 3)
                m.put(address, bytes((m.read(address, 1)[0] | (1 << (index & 7)),)))
            history = m.read(0x02001f70, 0xc0)
            seed = generate(location)
            check(len(queue()) == 1, f'Generate after original opportunities:{location}/{completed_battle}')
            m.call(0x080cf690)
            m.call(0x080d2e6c, Q)
            check(not (queue()[0][2] & 32), f'Native appearance finishes:{location}/{completed_battle}')
            if completed_battle:
                # Selected encounter slot is one-based in the real world view.
                put32(VIEW+4, 0x02002c10)
                m.put(0x02002cba, b'\x01')
                m.put(0x02002e54, bytes((location,)))
                m.call(0x08030168)
                check(bool(queue()[0][2] & 64), f'Battle return marks selected encounter:{location}')
            else:
                for day in range(1, 7):
                    m.call(0x080cf690)
                    row = queue()[0]
                    check(row[5] >> 1 == max(0, 6-day), f'Native remaining days:{location}/{day}')
                    check(bool(row[2] & 64) == (day == 6), f'Native expiration boundary:{location}/{day}')
            m.call(0x080d0f74, Q)
            check(not queue() and m.read(Q, 30) == bytes(30), f'Native queue retirement:{location}/{completed_battle}')
            check(m.read(0x02001f70, 0xc0) == history, f'Retirement preserves history:{location}/{completed_battle}')
            generate(location)
            check(len(queue()) == 1 and event(queue()[0]) == 225+location,
                  f'Same native encounter can return:{location}/{completed_battle}')
            m.call(0x080cf690)
            found = m.call(0x080d17c4, location, location, TYPE)
            check(found == 225+location, f'Returned encounter selected by map consumer:{location}/{completed_battle}')
            cases.append(dict(location=location, event=found, seed=seed,
                              completedBattle=completed_battle, queueHex=m.read(Q, 30).hex()))
    coverage['lifecycle'] = 'All30 origins expire and retire after battle, then regenerate with original mission receipts retained.'

# Initial generated events are enough to witness some or all content. Do not
# claim repeatable mission gates from their data bits or manufacture witnesses.
events = {row['event'] for row in cases}
learned = {}
for row in ledger['rows']:
    learned[row['id']] = [s for s in row['sources'] if s['kind'] == 'roaming-clan' and s['event'] in events]
coverage['learnableActions'] = learned
coverage['missingRoamingActions'] = [a for a, sources in learned.items() if not sources]
check(not coverage['missingRoamingActions'], 'All20 learnable actions have generated roaming witnesses')
monsters, equipment = collections.defaultdict(list), collections.defaultdict(list)
for event_id in sorted(events):
    formation = u16(0x563a70+event_id*12+4) or u16(0x563a70+event_id*12+2)
    p = 0x54cd54+formation*40
    count, units = rom[p], u32(p+4) & 0x1ffffff
    check(0 < count <= 13 and 0x52a4d0 <= units and units+48*count <= 0x54bb30, f'Formation bounds:{event_id}')
    for slot in range(count):
        unit = units+slot*48
        witness = dict(event=event_id, formation=formation, slot=slot, unitOffset=unit, job=rom[unit+1])
        monsters[rom[unit+1]].append(witness)
        for gear in range(5):
            item = u16(unit+8+gear*2)
            if item in (68, 116, 183, 313, 314):
                equipment[item].append(dict(**witness, gear=gear, supportIndex=rom[unit+41]))
coverage['monsterSpecies'] = {j: monsters[j] for j in range(44, 68) if monsters[j]}
coverage['rareEquipment'] = {j: equipment[j] for j in (68, 116, 183, 313, 314)}
coverage['missingRoamingEquipment'] = [j for j in (68, 116, 183, 313, 314) if not equipment[j]]
check(set(coverage['monsterSpecies']) == set(range(44, 68)), 'All24 original monster jobs have generated sources, including all20 capturable jobs')
check(coverage['missingRoamingEquipment'] == [183], 'Four rare gear witnesses; Oathbow remains a mission-source obligation')
check(len(cases) == 60, 'All thirty roaming origins in both lifecycle branches' if lifecycle_only else 'All thirty roaming origins in both map permutations')
result = report(True)
atexit.unregister(report)
print(json.dumps(dict(passed=True, assertions=len(checks), cases=len(cases),
                     missingRoamingActions=coverage['missingRoamingActions'],
                     missingRoamingEquipment=coverage['missingRoamingEquipment'], report=str(OUT/'report.json'))))
