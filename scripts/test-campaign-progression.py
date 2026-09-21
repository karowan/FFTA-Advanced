"""Connected native mission receipts and teaching gates from the opening fixture.

Battle and story outcomes are controlled successes, all territory identities
are declared placed, and recurring month windows are selected directly. This
tests native mission eligibility/completion, earned quest ingredients, rumors
and shop consumers continuously. It does not play story scenes, battles or map
placement. No later completion flag or ingredient is inserted by this driver.
"""
import ast
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
path = pathlib.Path(meta['path'])
rom = path.read_bytes()
assert sha(rom) == meta['romSha1']
clean = (ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
assert sha(clean) == '4ac05441f4de70a4ec3dd932116346c61b8783d9'
NATIVE_RANGES = [(0x5e104, 0x5e128), (0x5e154, 0x5e17a), (0x5e1b4, 0x5e1bc),
                 (0x61eaa, 0x61ec4), (0x61efe, 0x61f18), (0xcf118, 0xcf260),
                 (0x6130c, 0x61350), (0xd1b80, 0xd1c94), (0x5573f4, 0x5577ec)]
assert all(rom[lo:hi] == clean[lo:hi] for lo, hi in NATIVE_RANGES)
FIX = path.parent/'fixture'
proof = json.loads((FIX/'prepare-cache.json').read_text())
assert proof['inputs']['romSha1'] == meta['romSha1']
ram, iw = [(FIX/name).read_bytes() for name in ('battle-ready.ram', 'battle-ready.iwram')]
assert all(sha(data) == proof['outputs'][name] for name, data in
           (('battle-ready.ram', ram), ('battle-ready.iwram', iw)))
ledger = json.loads((ROOT/'build/reports/mission-item-dependencies.json').read_text())
assert ledger['candidateSha1'] == meta['romSha1']
records = ledger['installedRecords']
registry = json.loads((ROOT/'build/expansion/registry.json').read_text())
acquisition = json.loads((ROOT/'notes/equipment-acquisition.json').read_text())
item_ids = {item['id']: item['romItemId'] for item in registry['items']}
RETURN, STACK = 0x08000100, 0x03006800
source = (ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000', 'count=3000000')
tree = ast.parse(source)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ARM'],
                       type_ignores=[]), '<native ARM>', 'exec'))
m = ARM(rom, iw)
OUT = path.parent/('campaign-progression-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
OUT.mkdir()
checks, transitions, milestones = [], [], []
source_transitions, rumor_reads = [], []
queue_relief = []
BUFFER, VIEW = 0x02030000, 0x02010000
TOWNS = {2:'Cyril', 3:'Sprohm', 4:'Muscadet', 5:'Cadoan', 6:'Baguba Port'}
# Event receipts between main missions are original records, not invented flags.
ROUTE = [3, 4, 359, 5, 317, 6, 7, 318, 8, 9, 10, 11, 12, 13, 319,
         14, 27, 15, 16, 320, 17, 321, 18, 19, 20, 322, 21, 22, 323,
         23, 325, 24, 25, 26]


def check(ok, label):
    assert ok, label
    checks.append(label)


def flag(index):
    return bool(m.read(0x02001f70+(index >> 3), 1)[0] & (1 << (index & 7)))


def queue():
    node, previous, result = m.word(0x020028c8), 0, {}
    while node:
        assert 0x020025c8 <= node < 0x020028c8 and (node-0x020025c8) % 12 == 0 and len(result) < 64
        ptr, prev, nxt = struct.unpack('<III', m.read(node, 12))
        assert prev == previous and 0x020021c8 <= ptr < 0x020025c8 and (ptr-0x020021c8) % 16 == 0
        mid = int.from_bytes(m.read(ptr, 2), 'little') & 1023
        assert mid and mid not in result
        result[mid] = ptr
        previous, node = node, nxt
    return result


def stock(stage):
    seen = set()
    for town, name in TOWNS.items():
        m.put(BUFFER, bytes(2048))
        m.put(BUFFER+2048, b'\xa5'*4)
        count = m.call(0x080cbdc0, BUFFER, 2, 0, town)
        check(count < 256 and m.read(BUFFER+2048, 4) == b'\xa5'*4, f'Stock bounds:{stage}/{town}')
        ids = struct.unpack('<'+'HBB'*count, m.read(BUFFER, count*4))[::3]
        expected = {item_ids[item['id']] for item in acquisition['items']
                    if int(item['stageId'][1:]) <= stage and
                    name in [item['primaryShop']]+item['additionalShops']}
        actual = set(ids) & set(item_ids.values())
        check(actual == expected, f'Earned teaching stock:{stage}/{town}')
        seen.update(actual)
    data = m.read(0x02000000, 0x40000)
    name = f'stage-{stage}.ram'
    (OUT/name).write_bytes(data)
    milestones.append(dict(stage=stage, teachingItems=sorted(seen), ram=name, ramSha1=sha(data)))


def held(item):
    return sum(m.read(0x02002b08+i*4, 4) == bytes((item, 0, 0, 0)) for i in range(64))


def collect(item):
    """Execute original quest-reward insertion; stop before its UI refresh."""
    before = held(item)
    m.u.reg_write(UC_ARM_REG_R5, item)
    m.u.reg_write(UC_ARM_REG_SP, STACK)
    m.u.emu_start(0x08061eff, 0x08061f18, count=3000000)
    check(m.u.reg_read(UC_ARM_REG_PC) == 0x08061f18 and m.u.reg_read(UC_ARM_REG_SP) == STACK,
          f'Native quest reward insertion returns:{item}')
    check(held(item) == before+1, f'Native quest reward collected:{item}')


def bind_requirements(ptr, reqs):
    """Original pub's two selected-item commit blocks before D0B48."""
    context = VIEW+0x4000
    m.put(0x0200f448, struct.pack('<I', context))
    for slot, item in enumerate(reqs):
        selected = next(0x02002b08+i*4 for i in range(64)
                        if m.read(0x02002b08+i*4, 4) == bytes((item, 0, 0, 0)))
        # Native PC-relative context offset, authenticated against the clean ROM.
        literal = 0x5e1b8
        offset = struct.unpack_from('<I', rom, literal)[0]
        m.put(context+offset, struct.pack('<I', ptr))
        m.u.reg_write(UC_ARM_REG_R4, 0x0200f448)
        m.u.reg_write(UC_ARM_REG_R7 if slot == 0 else UC_ARM_REG_R6, selected)
        m.u.reg_write(UC_ARM_REG_SP, STACK)
        start, end = (0x0805e104, 0x0805e128) if slot == 0 else (0x0805e154, 0x0805e17a)
        m.u.emu_start(start | 1, end, count=3000000)
        check(m.u.reg_read(UC_ARM_REG_PC) == end and
              m.read(selected, 4) == struct.pack('<BBH', item, 1, int.from_bytes(m.read(ptr, 2), 'little') & 1023),
              f'Native pub binds selected ingredient:{item}/{slot}')


active = set()


def earn_flag(index):
    if flag(index):
        return
    if 768 <= index < 1279:
        complete_source(index-767)
    elif 1280 < index < 1408:
        topic = index-1280
        ptr = 0x085573f4+(topic-1)*8
        identity, town, required, reqvalue, excluded, exvalue = struct.unpack('<BBHBHB', m.read(ptr, 8))
        check(identity == topic and town == 0 and reqvalue == 1, f'Original rumor prerequisites:{topic}')
        earn_flag(required)
        check(not excluded or flag(excluded) != bool(exvalue), f'Rumor has not retired:{topic}')
        count = m.call(0x080d1b80, BUFFER, 64, 2)
        check(count <= 64 and ptr in struct.unpack('<64I', m.read(BUFFER, 256))[:count],
              f'Earned rumor is natively listed:{topic}')
        m.call(0x0806130c, ptr)
        rumor_reads.append(dict(topic=topic, required=required, history=index))
    else:
        raise AssertionError(f'Untraced non-mission flag:{index}')
    check(flag(index), f'Prerequisite earned without flag insertion:{index}')


def obtain(item, copies):
    while held(item) < copies:
        choices = [row for row in records[:406] if row['pubEnabled'] and item+375 in row['rewards']
                   and (row['repeatable'] or not flag(row['record']+767))
                   and row['record'] not in active]
        choices.sort(key=lambda row: (len(row['requirements']), len([c for c in row['unlock']
                     if c['selector'] and c['value'] == 1 and not flag(c['index'])]), row['record']))
        check(bool(choices), f'Original unspent source for ingredient:{item}')
        complete_source(choices[0]['record'])


def complete_source(mid):
    check(mid not in active, f'No circular source dependency:{mid}')
    active.add(mid)
    row = records[mid]
    for clause in row['unlock']:
        if not clause['selector']:
            continue
        check(clause['kind'] == 'flag' and clause['value'] in (0, 1), f'Bounded source flag clause:{mid}')
        if clause['value']:
            earn_flag(clause['index'])
        else:
            check(not flag(clause['index']), f'Original absence gate retained:{mid}/{clause["index"]}')
    reqs = [entry['localId'] for entry in row['requirements']]
    for item in sorted(set(reqs)):
        obtain(item, reqs.count(item))
    m.put(0x02002fba, bytes((row['pubMonth'] or 1,)))
    m.call(0x080cfcd0, 0)
    entries = queue()
    if mid not in entries:
        # Expire old unrelated offers/cooldowns through the native daily tick.
        # This advances a fixed120-day interval; it never edits a queue slot.
        for _ in range(120):
            m.call(0x080cf51c)
        m.put(0x02002fba, bytes((row['pubMonth'] or 1,)))
        m.call(0x080cfcd0, 0)
        entries = queue()
    # An all-territories/mostly-story-only clan can fill the original64 slots.
    # Complete already-offered finite side missions with available ingredients
    # rather than deleting queue entries or manufacturing completion flags.
    for _ in range(64):
        if mid in entries:
            break
        reserved = {req['localId'] for current in active for req in records[current]['requirements']}
        candidates = [i for i in sorted(entries) if 28 <= i < 406 and i not in active
                      and not records[i]['repeatable'] and not flag(i+767)
                      and all(c['kind'] == 'flag' and c['value'] in (0, 1)
                              for c in records[i]['unlock'] if c['selector'])
                      and all(req['localId'] not in reserved and held(req['localId']) >=
                              sum(other['localId'] == req['localId'] for other in records[i]['requirements'])
                              for req in records[i]['requirements'])]
        check(bool(candidates), f'Native queue has a finite side mission to complete:{mid}')
        relief = candidates[0]
        complete_source(relief)
        queue_relief.append(dict(waitingFor=mid, completed=relief))
        for _ in range(rom[0x55ae4c+70*relief+63]+1):
            m.call(0x080cf51c)
        m.put(0x02002fba, bytes((row['pubMonth'] or 1,)))
        m.call(0x080cfcd0, 0)
        entries = queue()
    check(mid in entries, f'Earned source constructed:{mid}/{row["name"]}')
    ptr = entries[mid]
    rewards = list(struct.unpack('<HH', m.read(ptr+8, 4)))
    before = {item:held(item) for item in set(reqs)}
    bind_requirements(ptr, reqs)
    m.call(0x080d0b48, ptr, 0x02000188 if row['type'] & 7 == 0 else 0, *(reqs+[0, 0])[:2])
    m.call(0x080d1e70, ptr, 1)
    check(flag(mid+767), f'Original source receipt earned:{mid}')
    for item in before:
        spent = sum(entry['consumed'] for entry in row['requirements'] if entry['localId'] == item)
        check(held(item) == before[item]-spent,
              f'Native earned ingredient consumption:{mid}/{item}:{before[item]}-{spent}={held(item)}')
    # Only the quest reward is collected; random ordinary gear is declined.
    for reward in rewards:
        if 375 < reward < 512:
            if all(m.read(0x02002b08+i*4, 1)[0] for i in range(64)):
                # Use native item disposal, retaining all supplies for the
                # chosen renewable witnesses and their finite prerequisites.
                wanted = {r['item'] for r in renewable['witnesses']} | {43, 106, 109}
                expendable = next((m.read(0x02002b08+i*4, 1)[0] for i in range(64)
                                  if m.read(0x02002b08+i*4, 1)[0] not in wanted), None)
                check(expendable is not None, 'Native quest bag has an unneeded item to discard')
                m.u.reg_write(UC_ARM_REG_R3, expendable)
                m.u.reg_write(UC_ARM_REG_SP, STACK)
                m.u.emu_start(0x08061eab, 0x08061f18, count=3000000)
                check(m.u.reg_read(UC_ARM_REG_PC) == 0x08061f18, f'Native item disposal:{expendable}')
            collect(reward-375)
    source_transitions.append(dict(mission=mid, name=row['name'], requirements=reqs, rewards=rewards,
                                   month=row['pubMonth'] or 1))
    active.remove(mid)


failure = None
final_sha = None
try:
    # Keep the authenticated opening's actual history, clan and inventories.
    # Detached native services need a minimal world view, not a running renderer.
    m.put(0x02000000, bytes(0x40000))
    m.put(0x02000080, ram[0x80:0x2190])
    m.put(0x03002810, struct.pack('<I', VIEW))
    m.put(VIEW, struct.pack('<II', 0x02002c10, 0x02002c10))
    for location in range(1, 31):
        m.put(0x02002cc3+(location-1)*12, bytes((location,)))
    m.put(0x02002e58, b'\x03')
    m.put(0x02002fba, b'\x01')
    m.put(0x030034b0, bytes(4))
    initial = [i for i in range(768, 1279) if flag(i)]
    check(initial == [768, 769, 1083], 'Authenticated opening has only its three original receipts')
    for mid in ROUTE:
        lo = 0x55ae4c+mid*70
        check(rom[lo:lo+70] == clean[lo:lo+70], f'Original story mission record preserved:{mid}')
    stock(0)
    for mid in ROUTE:
        row = records[mid]
        check(not row['requirements'], f'No manufactured quest ingredients:{mid}')
        check(not flag(mid+767), f'Next receipt absent:{mid}')
        m.call(0x080cfcd0, 0)
        entries = queue()
        check(mid in entries, f'Connected native eligibility:{mid}/{row["name"]}')
        ptr = entries[mid]
        before = m.read(0x02001f70, 0xc0)
        m.call(0x080d0b48, ptr, 0, 0, 0)
        m.call(0x080d1e70, ptr, 1)
        check(flag(mid+767), f'Native completion earns next receipt:{mid}')
        changed = [i for i in range(1536) if bool(before[i//8] & (1 << (i&7))) != flag(i)]
        transitions.append(dict(mission=mid, name=row['name'], type=row['type'],
                                prerequisites=row['unlock'], changedFlags=changed,
                                queuedMissions=sorted(entries)))
        if mid in (7, 13, 19):
            stock((7, 13, 19).index(mid)+1)
    check(len(milestones[-1]['teachingItems']) == 85, 'All85 teachers unlocked through connected receipts')
    renewable = json.loads((ROOT/'build/reports/mission-renewable-chains.json').read_text())
    check(renewable['candidateSha1'] == meta['romSha1'], 'Current renewable ingredient ledger')
    for witness in sorted(renewable['witnesses'], key=lambda row: (row['layer'], row['mission'])):
        complete_source(witness['mission'])
    check(all(flag(row['mission']+767) for row in renewable['witnesses']), 'All24 original renewable sources reached')
    final = m.read(0x02000000, 0x40000)
    (OUT/'final.ram').write_bytes(final)
    final_sha = sha(final)
except BaseException as error:
    failure = repr(error)
    (OUT/'failure.ram').write_bytes(m.read(0x02000000, 0x40000))
report = dict(passed=failure is None, romSha1=meta['romSha1'], sourceSha1=sha(pathlib.Path(__file__).read_bytes()),
              fixture=proof, route=ROUTE, assertions=len(checks), checks=checks,
              transitions=transitions, milestones=milestones, failure=failure, scope=__doc__)
report.update(sourceTransitions=source_transitions, rumorReads=rumor_reads, queueRelief=queue_relief,
              finalRamSha1=final_sha, nativeRanges=NATIVE_RANGES, seed=0,
              inputHashes={name:sha((ROOT/name).read_bytes()) for name in
                           ('build/reports/mission-item-dependencies.json',
                            'build/reports/mission-renewable-chains.json',
                            'build/expansion/registry.json', 'notes/equipment-acquisition.json')})
(OUT/'script.py').write_bytes(pathlib.Path(__file__).read_bytes())
(OUT/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
print(json.dumps(dict(passed=report['passed'], assertions=len(checks), transitions=len(transitions),
                      failure=failure, report=str(OUT/'report.json'))))
assert failure is None, failure
