"""Bounded native posting gates, before construction/queue insertion or acceptance.

Executes the installed Thumb code with declared RAM inputs. No replacement gate
implementation is installed, no user save is read, and no campaign is played.
"""
import collections
import hashlib
import json
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *

meta = json.loads((ROOT / 'build/expansion/probes/integrated-jobs/current.json').read_text(encoding='utf-8'))
rom = pathlib.Path(meta['path']).read_bytes()
clean = (ROOT / 'roms/clean/FFTA_US_clean.gba').read_bytes()
ledger = json.loads((ROOT / 'build/reports/mission-item-dependencies.json').read_text(encoding='utf-8'))
assert hashlib.sha1(rom).hexdigest() == meta['romSha1'] == ledger['candidateSha1']
assert hashlib.sha1(clean).hexdigest() == ledger['cleanSha1'] == '4ac05441f4de70a4ec3dd932116346c61b8783d9'
# The separate flag writer C9574 has an intentional turn-lifecycle hook;
# posting only calls these unchanged readers, never that writer.
for start, end in ((0xcfd0c, 0xcffb8), (0xc9540, 0xc9574), (0xc95a8, 0xc95c0), (0x36330, 0x36350)):
    assert rom[start:end] == clean[start:end], f'Native gate changed at {start:x}'

u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
for address, size in ((0x02000000, 0x40000), (0x03000000, 0x8000), (0x08000000, 0x2000000)):
    u.mem_map(address, size)
u.mem_write(0x08000000, rom)
STACK, SYNTHETIC, DURATION = 0x03007000, 0x09f00000, 0x02030000
ACCEPT, REJECT = 0x080cff40, 0x080d056e
stops = {ACCEPT, REJECT, 0x080cffb8}
u.hook_add(UC_HOOK_CODE, lambda machine, address, size, data: machine.emu_stop() if address in stops else None)
counts = collections.Counter()
observations = []


def block(start, registers):
    for reg, value in registers.items():
        u.reg_write(reg, value)
    u.reg_write(UC_ARM_REG_SP, STACK)
    u.reg_write(UC_ARM_REG_LR, 0x08000101)
    u.emu_start(start | 1, 0x08000100, count=10000)
    pc = u.reg_read(UC_ARM_REG_PC)
    assert pc in stops, f'Gate escaped: {pc:x}'
    return pc


def set_flag(ram, index, value):
    offset, bit = 0x1f70 + index // 8, 1 << (index & 7)
    ram[offset] = (ram[offset] | bit) if value else (ram[offset] & ~bit)


def flag(ram, index):
    return bool(ram[0x1f70 + index // 8] & (1 << (index & 7)))


def satisfy(record):
    ram = bytearray(0x40000)
    for clause in record['unlock']:
        if clause['kind'] == 'counter':
            ram[0x2030 + clause['index']] = clause['value']
        elif clause['value'] in (0, 1):
            set_flag(ram, clause['index'], clause['value'])
    if record['eventLocation'] is not None:
        ram[0x2cc3 + (record['eventLocation'] - 1) * 12] = 1
    return ram


def expected(record, ram, month):
    index = record['record']
    if not record['pubEnabled']:
        return False
    if any((int.from_bytes(ram[at:at+2], 'little') & 1023) == index for at in range(0x21c8, 0x25c8, 16)):
        return False
    if flag(ram, index + 0x2ff) and not record['repeatable']:
        return False
    if record['pubMonth'] and record['pubMonth'] != month:
        return False
    if record['eventLocation'] is not None and not ram[0x2cc3 + (record['eventLocation'] - 1) * 12]:
        return False
    for clause in record['unlock']:
        value, index = clause['value'], clause['index']
        if clause['kind'] == 'counter':
            if ram[0x2030 + index] < value:
                return False
        elif value in (0, 1) and flag(ram, index) != bool(value):
            return False
    return not any(flag(ram, index) for index in record['specialAbsentFlags'])


def check(record, ram, month, label, pointer=None):
    u.mem_write(0x02000000, bytes(ram))
    u.mem_write(STACK, struct.pack('<I', month))
    want = expected(record, ram, month)
    pc = block(0x080cfd00, {UC_ARM_REG_R5: pointer or 0x0855ae4c + 70 * record['record'], UC_ARM_REG_R6: record['record']})
    actual = pc == ACCEPT
    assert actual == want, (record['record'], label, actual, want)
    # Posting predicates must not change saved flags, inventory or world data.
    assert bytes(u.mem_read(0x02001940, 0x1800)) == bytes(ram[0x1940:0x3140]), (record['record'], label, 'mutation')
    counts[label] += 1
    observations.append({'record': record['record'], 'case': label, 'month': month, 'accepted': actual})


gate_keys = ('record', 'textId', 'pubEnabled', 'repeatable', 'unlock', 'pubMonth', 'pubDurationDays', 'eventLocation', 'specialAbsentFlags')
assert len(ledger['installedRecords']) == len(ledger['originalRecords']) == 512
for original, record in zip(ledger['originalRecords'], ledger['installedRecords']):
    if 407 <= record['record'] < 471:
        continue  # Installed recovery routes have their own exhaustive native test.
    assert all(original[k] == record[k] for k in gate_keys), record['record']
    if record['record'] == 0:
        continue  # Native loop starts at1;0 is the empty cached-record sentinel.
    base = satisfy(record)
    month = record['pubMonth'] or 1
    check(record, bytearray(0x40000), month, 'zero-state')
    check(record, base, month, 'declared-prerequisites')
    for test_month in range(1, 6):
        check(record, base, test_month, 'calendar')
    complete = base.copy()
    set_flag(complete, record['record'] + 0x2ff, 1)
    check(record, complete, month, 'completed')
    active = base.copy()
    struct.pack_into('<H', active, 0x21c8 + 63 * 16, record['record'] | 0xfc00)
    check(record, active, month, 'already-posted-last-slot')
    if record['eventLocation'] is not None:
        missing = base.copy()
        missing[0x2cc3 + (record['eventLocation'] - 1) * 12] = 0
        check(record, missing, month, 'location-not-placed')
    for slot, clause in enumerate(record['unlock']):
        fail = base.copy()
        if clause['kind'] == 'counter' and clause['value']:
            fail[0x2030 + clause['index']] = clause['value'] - 1
        elif clause['kind'] == 'flag' and clause['value'] in (0, 1):
            set_flag(fail, clause['index'], not clause['value'])
        else:
            continue
        check(record, fail, month, f'prerequisite-{slot + 1}-unsatisfied')
    for index in record['specialAbsentFlags']:
        special = base.copy()
        set_flag(special, index, 1)
        check(record, special, month, f'special-exclusion-{index}')
    u.mem_write(DURATION, b'\xa5' * 16)
    block(0x080cffa0, {UC_ARM_REG_R5: 0x0855ae4c + 70 * record['record'], UC_ARM_REG_R6: DURATION})
    assert bytes(u.mem_read(DURATION, 16)) == b'\xa5' * 3 + bytes([record['pubDurationDays'] or 255]) + b'\xa5' * 12
    counts['duration'] += 1

# Fixed boundary fixtures prove each of the three clause positions, ignored
# nonboolean flag values, and the flag/counter boundary independent of content.
for slot in range(3):
    for selector in (0x5ff, 0x600):
        for value in (0, 1, 2, 255):
            raw = bytearray(70)
            raw[3] = 0x20
            struct.pack_into('<HB', raw, 5 + slot * 3, selector, value)
            u.mem_write(SYNTHETIC, bytes(raw))
            clauses = [dict(selector=0, kind='flag', index=0, value=0) for _ in range(3)]
            clauses[slot] = dict(selector=selector, kind='flag' if selector < 0x600 else 'counter', index=selector if selector < 0x600 else 0, value=value)
            synthetic = dict(record=496, pubEnabled=True, repeatable=False, pubMonth=0, eventLocation=None, specialAbsentFlags=[], unlock=clauses)
            for observed in (0, 1, 2, 254, 255):
                ram = bytearray(0x40000)
                if selector < 0x600:
                    set_flag(ram, selector, bool(observed))
                else:
                    ram[0x2030] = observed
                check(synthetic, ram, 1, f'boundary-{slot}-{selector}-{value}-{observed}', SYNTHETIC)

report = dict(passed=True, romSha1=meta['romSha1'], totalCases=sum(counts.values()), counts=dict(counts),
              scope='Pre-construction native pub gates and posting duration only; not queue insertion, acceptance, rewards, recovery or campaign reachability.', observations=observations)
out = ROOT / 'build/reports/mission-pub-gates.json'
out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))
