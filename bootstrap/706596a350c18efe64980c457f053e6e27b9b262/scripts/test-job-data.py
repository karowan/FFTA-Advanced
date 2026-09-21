"""Native job-data probe audit. Run after build-job-data-probe.mjs.

Expected stats/progression come from the approved Markdown, independently of
the builder's JSON profiles. This is data/getter coverage, not playable-job QA.
"""
import hashlib
import json
import pathlib
import re
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *

ROM = 0x08000000
UNIT = 0x02000080
STOP = 0x03000000
SP = 0x03007000
COUNTS = {}
CHARACTERS = json.loads((ROOT / 'tools/ffta-randomizer-source/src/main/ffta/utils/charLookup.json').read_text())


def check(condition, message, group='data'):
    assert condition, message
    COUNTS[group] = COUNTS.get(group, 0) + 1


def word(data, offset):
    return struct.unpack_from('<I', data, offset)[0]


def rom_offset(address):
    assert ROM <= address < ROM + 0x02000000
    return address - ROM


class ARM:
    def __init__(self, rom):
        self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        for address, size in [(ROM, 0x02000000), (0x02000000, 0x40000),
                              (0x03000000, 0x8000)]:
            self.u.mem_map(address, size)
        self.u.mem_write(ROM, rom)
        self.calls = 0

    def call(self, pc, *args):
        for reg, value in zip([UC_ARM_REG_R0, UC_ARM_REG_R1,
                               UC_ARM_REG_R2, UC_ARM_REG_R3], args):
            self.u.reg_write(reg, value)
        preserved = [UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6,
                     UC_ARM_REG_R7, UC_ARM_REG_R8, UC_ARM_REG_R9,
                     UC_ARM_REG_R10, UC_ARM_REG_R11]
        for index, reg in enumerate(preserved):
            self.u.reg_write(reg, 0x77000000 + index)
        self.u.reg_write(UC_ARM_REG_SP, SP)
        self.u.reg_write(UC_ARM_REG_LR, STOP | 1)
        self.u.emu_start(pc | 1, STOP, count=10000)
        assert self.u.reg_read(UC_ARM_REG_PC) == STOP, f'No return at {pc:x}: {args}'
        assert self.u.reg_read(UC_ARM_REG_SP) == SP, f'Stack changed: {pc:x}'
        for index, reg in enumerate(preserved):
            assert self.u.reg_read(reg) == 0x77000000 + index, f'ABI: {pc:x}/{reg}'
        self.calls += 1
        return self.u.reg_read(UC_ARM_REG_R0)

    def job(self, job, fallback, selector):
        return self.call(0x080C8570, job, fallback, selector)

    def unit(self, job, fallback=None):
        data = bytearray(264)
        data[4] = 1
        data[5] = job
        data[7] = job if fallback is None else fallback
        self.u.mem_write(UNIT, bytes(data))
        return bytes(data)


def decode_name(data, table, index):
    offset = rom_offset(word(data, table + index * 4))
    result = ''
    while data[offset]:
        a, b = data[offset:offset + 2]
        if a == 1:
            offset += 1
            continue
        if a == 0x80 and 0xB0 <= b <= 0xC9:
            result += chr(65 + b - 0xB0)
        elif a == 0x80 and 0xCA <= b <= 0xE3:
            result += chr(97 + b - 0xCA)
        elif (a, b) == (0x40, 0x73):
            result += ' '
        elif f'{a:X}{b:X}' in CHARACTERS:
            result += CHARACTERS[f'{a:X}{b:X}']
        elif f'{a:X}' in CHARACTERS:
            result += CHARACTERS[f'{a:X}']
            offset += 1
            continue
        else:
            raise AssertionError(f'Unexpected job-name encoding at {offset:x}: {a:x} {b:x}')
        offset += 2
    return result


clean = (ROOT / 'roms/clean/FFTA_US_clean.gba').read_bytes()
base = (ROOT / 'build/foundation/FFTA_vanillaplus_dev.gba').read_bytes()
probe = (ROOT / 'build/expansion/probes/job-data.gba').read_bytes()
manifest = json.loads((ROOT / 'build/expansion/probes/job-data.json').read_text())
registry = json.loads((ROOT / 'build/expansion/registry.json').read_text())
spec = (ROOT / 'JOB-CLASS-SPECIFICATION.md').read_text(encoding='utf-8')
sha = lambda data: hashlib.sha1(data).hexdigest()
check(sha(clean) == '4ac05441f4de70a4ec3dd932116346c61b8783d9', 'Wrong clean ROM')
check(sha(base) == manifest['baseSha1'], 'Stale foundation/manifest')
check(sha(probe) == manifest['romSha1'], 'Stale probe/manifest')
check(len(base) == len(probe) == 0x02000000, 'Unexpected ROM size')

# Independently reconstruct the permitted byte changes, detecting unlisted
# edits and overlapping/reused allocations rather than trusting the ledger.
expected = bytearray(base)
occupied = set()
for allocation in manifest['allocations']:
    start, size = allocation['offset'], allocation['bytes']
    check(0x1020000 <= start < start + size <= 0x1100000, 'Allocation bounds')
    check(start % 4 == 0, 'Allocation alignment')
    check(all(value == 255 for value in base[start:start + size]), 'Occupied allocation')
    check(not any(i in occupied for i in range(start, start + size)), 'Allocation overlap')
    occupied.update(range(start, start + size))
    payload = probe[start:start + size]
    check(sha(payload) == allocation['sha1'], 'Allocation digest')
    expected[start:start + size] = payload
for change in manifest['changes']:
    offset = change['offset']
    check(offset % 4 == 0 and offset < 0x1000000, 'Pointer patch outside native area')
    check(word(base, offset) == change['original'], 'Wrong original pointer')
    struct.pack_into('<I', expected, offset, change['address'])
check(bytes(expected) == probe, 'Unlisted ROM mutation')

addresses = {key: rom_offset(value) for key, value in manifest['addresses'].items()}
jobtable, permissions, requirements, names = [addresses[k] for k in
                                            ['jobs', 'permissions', 'requirements', 'names']]
check(probe[jobtable:jobtable + 116 * 52] == clean[0x521A14:0x521A14 + 116 * 52],
      'Original job records changed')
check(probe[names:names + 753 * 4] == base[0x526680:0x526680 + 753 * 4],
      'Original name pointers changed')
for literal in [0xCAC40, 0xCB488, 0xCB5F4]:
    check(word(probe, literal) == permissions + ROM, 'Equipment pointer not relocated')
check(word(probe, 0xC8598) == jobtable + ROM, 'Getter job pointer')
check(word(probe, 0xC8B18) == requirements + ROM, 'Prerequisite pointer')

original, foundation, expanded = ARM(clean), ARM(base), ARM(probe)
valid_fallbacks = [job for job in range(116) if clean[0x521A14 + job * 52 + 5] == 0]
for job in range(116):
    alias = clean[0x521A14 + job * 52 + 5]
    fallbacks = valid_fallbacks if alias == 0xFF else [job]
    for fallback in fallbacks:
        for selector in range(48):
            wanted = original.job(job, fallback, selector)
            check(foundation.job(job, fallback, selector) == wanted,
                  f'Foundation bare getter changed {job:x}/{fallback:x}/{selector:x}', 'original_getter')
            check(expanded.job(job, fallback, selector) == wanted,
                  f'Original getter changed {job:x}/{fallback:x}/{selector:x}', 'original_getter')
    pindex = original.job(job, 2, 0x24)
    rindex = original.job(job, 2, 0x27)
    native_req = rom_offset(word(clean, 0xC8B18)) + rindex * 4
    check(probe[permissions + pindex * 4:permissions + pindex * 4 + 4] ==
          clean[0x51D0F4 + pindex * 4:0x51D0F4 + pindex * 4 + 4], 'Original permission data')
    check(probe[requirements + rindex * 4:requirements + rindex * 4 + 4] ==
          clean[native_req:native_req + 4], 'Original prerequisite data')
    # Exercise the real category-eligibility consumer on every native item.
    for machine in [original, expanded]:
        machine.unit(job, 2 if alias == 0xFF else job)
    foundation.unit(job, 2 if alias == 0xFF else job)
    for selector in range(48):
        check(expanded.call(0x080C92F0, UNIT, selector) ==
              foundation.call(0x080C92F0, UNIT, selector),
              f'Original unit getter changed {job:x}/{selector:x}', 'original_unit_getter')
    for item in range(1, 376):
        wanted = original.call(0x080CB450, UNIT, item)
        check(expanded.call(0x080CB450, UNIT, item) == wanted,
              f'Original equip predicate changed job={job:x}/item={item}', 'original_equipment')

rows = [[cell.strip() for cell in line.strip().strip('|').split('|')]
        for line in spec.splitlines() if line.startswith('|')]
race_ids = {'Human': 1, 'Bangaa': 2, 'Nu Mou': 3, 'Viera': 4, 'Moogle': 5}
native_names = {(clean[0x521A14 + j * 52 + 4],
                 decode_name(clean, 0x526680, int.from_bytes(clean[0x521A14 + j * 52:
                                                                        0x521A14 + j * 52 + 2], 'little'))): j
                for j in range(2, 44)}
weapon_types = {'Katanas': [9], 'Swords, greatswords, broadswords': [1, 5, 6],
                'New two-handed axes': [31], 'Rods, maces': [11, 12],
                'Knives, maces': [7, 12], 'Instruments, knives': [16, 7],
                'Knives, rapiers': [7, 8], 'Rapiers, sabers': [8, 3]}
profiles = manifest['profiles']
check(len(profiles) == 10 and {p['id'] for p in profiles} == set(range(116, 126)), 'New job IDs')
for profile in profiles:
    job, race, name = profile['id'], profile['raceName'], profile['name']
    title = f'{race} {name}'
    allocated = next(entry for entry in registry['jobs'] if entry['id'] == job)
    check(all(profile[key] == allocated[key] for key in ['id', 'name', 'race', 'raceName', 'nameId']),
          f'Profile identity differs from registry: {title}')
    check(profile['race'] == race_ids[race], 'Race label mismatch')
    matching = [row for row in rows if len(row) == 8 and row[0] == title]
    check(len(matching) == 2, f'Missing approved stats: {title}')
    gains, bases = [[float(x) for x in row[1:]] for row in matching]
    check(all(v.is_integer() for v in bases), 'Noninteger base template')
    hp, mp, wa, wd, ma, md, speed = map(int, bases)
    growth = [round(gains[i] * 10) for i in [0, 1, 6, 2, 3, 4, 5]]
    check(profile['stats'] == bases and profile['growth'] == gains and profile['nativeGrowth'] == growth,
          f'Profile metadata differs from approved stats: {title}')
    gear_name = ('Dark Knight, both races' if name == 'Dark Knight' else
                 f'Chemist, {race}' if name == 'Chemist' else name)
    gear_rows = [row for row in rows if len(row) == 7 and row[0] == gear_name]
    check(len(gear_rows) == 1, f'Missing approved equipment: {title}')
    gear = gear_rows[0]
    move, jump, evade = map(int, gear[1:4])
    types = set(weapon_types[gear[4]]) | {27, 28, 29}
    for text, category in [('clothing', 25), ('heavy armor', 24), ('robes', 26),
                           ('hats', 23), ('helmets', 21)]:
        if text in gear[5].lower():
            types.add(category)
    if gear[6].startswith('Yes'):
        types.add(20)
    mask = sum(1 << (category - 1) for category in types)
    progression = [row for row in rows if len(row) == 4 and row[:2] == [race, name]]
    check(len(progression) == 1, f'Missing approved progression: {title}')
    prereq = bytearray(4)
    if progression[0][3] != 'None':
        for i, branch in enumerate(progression[0][3].split(' + ')):
            match = re.fullmatch(r'(.+) (\d+)', branch)
            prereq[2 * i] = native_names[(race_ids[race], match[1])]
            prereq[2 * i + 1] = int(match[2])
    record = probe[jobtable + job * 52:jobtable + (job + 1) * 52]
    check(record.hex() == profile['recordHex'], f'Stale profile: {title}')
    check(clean[0x521A14 + profile['donor'] * 52 + 4] == race_ids[race], 'Cross-race donor')
    expected_selectors = {selector: original.job(profile['donor'], profile['donor'], selector)
                          for selector in range(48)}
    expected_selectors.update({0: profile['nameId'], 1: race_ids[race], 2: 0,
                               0xC: job, 0xD: 0, 0x16: 50, 0x17: hp,
                               0x18: mp, 0x19: speed, 0x1A: wa, 0x1B: wd,
                               0x1C: ma, 0x1D: md, 0x1E: move, 0x1F: jump,
                               0x20: evade, 0x21: 0, 0x22: 1, 0x23: 2,
                               0x24: record[0x2D], 0x27: record[0x30], 0x28: 0})
    expected_selectors.update({selector: 1 for selector in range(0xE, 0x16)})
    expected_selectors.update(dict(zip(range(0x29, 0x30), growth)))
    lesson_indices = [owner['abilityIndex'] for lesson in registry['lessons']
                      for owner in lesson['owners'] if owner['jobId'] == job]
    expected_selectors.update({0x25: min(lesson_indices), 0x26: max(lesson_indices)})
    unchanged_unit = expanded.unit(job)
    for selector, wanted in expected_selectors.items():
        check(expanded.job(job, job, selector) == wanted,
              f'New getter mismatch {title}/{selector:x}', 'new_getter')
        check(expanded.call(0x080C92F0, UNIT, selector) == wanted,
              f'New unit getter mismatch {title}/{selector:x}', 'new_getter')
        # Native special-job aliases must inherit the new record as completely
        # as they inherit vanilla jobs, except the alias selector itself.
        if selector != 2:
            for alias_job in [0x50, 0x51, 0x52, 0x55]:
                check(expanded.job(alias_job, job, selector) == wanted,
                      f'New alias fallback {alias_job:x}/{title}/{selector:x}', 'new_alias_getter')
    check(bytes(expanded.u.mem_read(UNIT, 264)) == unchanged_unit, 'Getter modified unit')
    check(decode_name(probe, names, expanded.job(job, job, 0)) == name, 'Wrong new job name')
    check(word(probe, permissions + expanded.job(job, job, 0x24) * 4) == mask, 'Equipment versus spec')
    req_address = requirements + expanded.job(job, job, 0x27) * 4
    check(probe[req_address:req_address + 4] == prereq, 'Prerequisites versus spec')
    # Synthetic category substitutions in the emulator only; no ROM file edit.
    for category in range(1, 33):
        expanded.u.mem_write(ROM + 0x51D1A0 + 8, bytes([category]))
        check(expanded.call(0x080CB450, UNIT, 1) == int(category in types),
              f'New native equip predicate {title}/category={category}', 'new_equipment')
    expanded.u.mem_write(ROM + 0x51D1A0 + 8, clean[0x51D1A0 + 8:0x51D1A0 + 9])

for species in range(9):
    unit = bytearray(264)
    unit[4] = 1
    unit[5] = unit[7] = 0x1A
    unit[0xEA] = 4
    unit[0xE6] = species
    for machine in [foundation, expanded]:
        machine.u.mem_write(UNIT, bytes(unit))
    for selector in range(48):
        check(expanded.call(0x080C92F0, UNIT, selector) ==
              foundation.call(0x080C92F0, UNIT, selector),
              f'Morpher behavior changed species={species}/selector={selector:x}', 'morpher_preservation')
    check(bytes(expanded.u.mem_read(UNIT, 264)) == bytes(unit), 'Morph getter modified unit')

report = {'passed': True, 'romSha1': sha(probe), 'baseSha1': sha(base),
          'checks': COUNTS, 'nativeCalls': sum(m.calls for m in [original, foundation, expanded]),
          'scope': '116 original jobs, all 48 selectors, all 112 terminating fallbacks for four special aliases; '
                   'all 375 native items per original job; ten approved profiles and 32 category bits; '
                   'special aliases with new jobs; nine foundation Morpher species; '
                   'register/stack ABI, allocation and pointer ledger checks.',
          'limitations': ['Bare getter aliases with cyclic fallback intentionally excluded',
                          'Equipment predicate excludes full shield/handedness validation',
                          'New job selection, commands, effects and graphical presentation remain untested']}
destination = ROOT / 'build/reports/job-data.json'
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
