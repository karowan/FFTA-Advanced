"""Native differential tests for AP loss, theft and prerequisite hooks."""
import ast
import ctypes as C
import hashlib
import importlib.util
import json
import pathlib
import re
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *
UNIT, EQUIPMENT, RETURN, STACK = 0x02000080, 0x02002000, 0x08000100, 0x03007000
for path, names in [('scripts/test-equipment-legality.py', ('ARM', 'iwram_from_boot')),
                    ('scripts/test-ap-inline.py', ('load_probe', 'setup'))]:
    tree = ast.parse((ROOT / path).read_text())
    nodes = [n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name in names]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<shared-native-harness>', 'exec'))
base, base_meta = load_probe('content-inventory')
probe, metadata = load_probe('ability-core')
assert metadata['baseSha1'] == hashlib.sha1(base).hexdigest()
registry = json.loads((ROOT / 'build/expansion/registry.json').read_text())
iwram = iwram_from_boot()
native, expanded = ARM(base, iwram), ARM(probe, iwram)
registers = [UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3,
             UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7,
             UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11]
checks, failures, aligned, helpers = {}, [], [], set()

def check(group, case, ok, detail=None):
    checks[group] = checks.get(group, 0) + 1
    if not ok: failures.append({'group': group, 'case': case, 'detail': detail})

def alignment(u, address, size, data):
    aligned.append((address, u.reg_read(UC_ARM_REG_SP)))

sites = [(0x1291AC, 0x1291B8, list(range(12))),
         (0x129224, 0x129230, list(range(12))),
         (0x129264, 0x129270, [0, 4, 5, 6, 7, 8, 9, 10, 11]),
         (0x132E62, 0x132E6E, list(range(12))),
         (0x132FC6, 0x132FD2, [1, 3, 4, 5, 6, 7, 8, 9, 10, 11]),
         (0x132FF8, 0x13300E, [0, 4, 5, 6, 7, 8, 9, 10, 11]),
         (0x133D30, 0x133D3C, list(range(12))),
         (0xC8B26, 0xC8B94, [2, 3, 8, 9, 10, 11])]
for start, _, _ in sites:
    jump = (start + 5) & ~3
    entry = expanded.word(0x08000000 + jump + 4) & ~1
    code = expanded.read(entry, 180)
    for offset in range(0, 176, 2):
        a, b = struct.unpack_from('<HH', code, offset)
        if a & 0xF800 == 0xF000 and b & 0xF800 == 0xF800:
            displacement = ((a & 2047) << 12) | ((b & 2047) << 1)
            if displacement & 0x400000: displacement -= 0x800000
            target = entry + offset + 4 + displacement
            if target not in helpers:
                helpers.add(target)
                expanded.u.hook_add(UC_HOOK_CODE, alignment, begin=target, end=target)
            break
    else: raise AssertionError(f'No helper at {start:x}')

def execute(machine, site, index, value, stack, written=0, gear=(), through=False, job=2):
    start, end, live = site
    address = setup(machine, job=job, index=index, value=value, gear=gear)
    values = [0x33100000 + n for n in range(12)]
    context = 0x02021000
    machine.put(context, struct.pack('<III', UNIT, 0, UNIT))
    if start == 0x1291AC:
        values[8], values[2], values[3], values[7] = UNIT, index, UNIT + 0x40, 0x7F
        if not value & 127: end = 0x1291BE
    elif start in (0x129224, 0x132E62): values[8], values[5] = UNIT, index
    elif start == 0x129264:
        values[8], values[5], values[6], values[4] = UNIT, index, UNIT + 0x40, written
        if through: end = 0x129298
    elif start == 0x132FC6: values[6], values[4] = context, index
    elif start == 0x132FF8:
        values[6], values[0], values[5] = context, index, written
        if through: end = 0x133024
    elif start == 0x133D30: values[6], values[8] = UNIT, index
    elif start == 0xC8B26:
        values[10], values[5], values[3] = UNIT, job, 0
        race = machine.read(UNIT + 6, 1)[0]
        count = next(r['totalCount'] for r in registry['races'] if r['id'] == race)
        for lesson in range(1, count):
            ap = 0x02001B40 + lesson - 144 if race == 1 and lesson >= 144 else UNIT + 0x40 + lesson
            # Added lessons absent for the original prerequisite differential.
            original_count = [0, 142, 77, 95, 85, 88][race]
            machine.put(ap, bytes([value if lesson < original_count or through else 0]))
    machine.put(stack, bytes(0x80))
    for register, content in zip(registers, values): machine.u.reg_write(register, content)
    machine.u.reg_write(UC_ARM_REG_CPSR, 0x20000030)
    machine.u.reg_write(UC_ARM_REG_SP, stack)
    machine.u.reg_write(UC_ARM_REG_LR, RETURN | 1)
    before = machine.read(0x02000000, 0x40000)
    machine.u.emu_start(0x08000001 + start, 0x08000000 + end, count=100000)
    assert machine.u.reg_read(UC_ARM_REG_PC) == 0x08000000 + end, f'end {start:x}'
    assert machine.u.reg_read(UC_ARM_REG_SP) == stack, f'SP {start:x}'
    after = machine.read(0x02000000, 0x40000)
    return [machine.u.reg_read(r) for r in registers], before, after, address

for site in sites[:-1]:
    for index in (1, 20, 141):
        for value in (0, 1, 49, 100, 128, 177, 228, 255):
            for stack in (STACK, STACK - 4):
                for written in ((0, 25, 99) if site[0] in (0x129264, 0x132FF8) else (0,)):
                    old = execute(native, site, index, value, stack, written)
                    new = execute(expanded, site, index, value, stack, written)
                    diffs = [(r, old[0][r], new[0][r]) for r in site[2] if old[0][r] != new[0][r]]
                    check('original_interior', [hex(site[0]), index, value, written, stack % 8],
                          not diffs and old[2] == new[2], diffs)

for site in sites[:-1]:
    for index in (144, 160, 177):
        for value in (0, 1, 100, 128, 228):
            for stack in (STACK, STACK - 4):
                result, before, after, address = execute(expanded, site, index, value, stack, written=25)
                actual = expanded.read(address, 1)[0]
                desired = 228 if site[0] == 0x132FC6 else 25 if site[0] in (0x129264, 0x132FF8) else value
                correct = actual == desired and expanded.read(UNIT + 0xD0, 56) == bytes([0x6D]) * 56
                if site[0] == 0x1291AC: correct &= result[0] == value & 127 and result[1] == value
                elif site[0] in (0x129224, 0x132E62, 0x133D30): correct &= result[4] == value & 127 and result[0] == value
                check('human_extension', [hex(site[0]), index, value, stack % 8], correct,
                      {'actual': actual, 'wanted': desired, 'r0': result[0], 'r4': result[4]})

for job in range(2, 44):
    for value in (0, 1, 49, 99, 100, 127, 128, 228):
        for stack in (STACK, STACK - 4):
            old = execute(native, sites[-1], 1, value, stack, job=job)
            new = execute(expanded, sites[-1], 1, value, stack, job=job)
            diffs = [(r, old[0][r], new[0][r]) for r in sites[-1][2] if old[0][r] != new[0][r]]
            check('original_prerequisites', [job, value, stack % 8], not diffs and old[2] == new[2], diffs)

job_lists = {int(job): [int(i) for i in indices.split(',')]
             for job, indices in re.findall(r'ffta_lessons_(\d+)\[\]=\{([\d,]+)\}',
                                           (ROOT / 'build/expansion/job-lessons.h').read_text())}
for job, lessons in job_lists.items():
    for value in (0, 1, 49, 99, 100, 127, 128, 228):
        for stack in (STACK, STACK - 4):
            result = execute(expanded, sites[-1], 1, value, stack, job=job, through=True)
            race = expanded.read(UNIT + 6, 1)[0]
            wanted = 0
            for index in lessons:
                record = expanded.call(0x080CD480, race, index)
                row = expanded.read(record, 8)
                if row[6] == 1 and value & 127 >= row[7]: wanted += 1
            check('explicit_prerequisites', [job, value, stack % 8], result[0][2] == wanted,
                  {'actual': result[0][2], 'wanted': wanted})

# Full post-write native equipment-check branches, including availability
# restoration for a teaching item; native low registers after calls are scratch.
for site in (sites[2], sites[5]):
    for item in (0, 1, 14, 42):
        for index in (1, 2, 20):
            for written in (0, 25, 99):
                for stack in (STACK, STACK - 4):
                    gear = (item,) if item else ()
                    old = execute(native, site, index, 228, stack, written, gear, through=True)
                    new = execute(expanded, site, index, 228, stack, written, gear, through=True)
                    diffs = [(r, old[0][r], new[0][r]) for r in range(4, 12) if old[0][r] != new[0][r]]
                    check('original_post_write', [hex(site[0]), item, index, written, stack % 8],
                          not diffs and old[2] == new[2], diffs)

for site in (sites[2], sites[5]):
    for index in (26, 33):
        for written in (0, 25, 99):
            for stack in (STACK, STACK - 4):
                old = execute(native, site, index, 228, stack, written, through=True, job=28)
                new = execute(expanded, site, index, 228, stack, written, through=True, job=28)
                check('viera_cure_coupling', [hex(site[0]), index, written, stack % 8], old[2] == new[2])

human_teaching = {}
for item in registry['items']:
    for owner in item['teaching']:
        if owner['race'] == 1:
            human_teaching.setdefault(owner['abilityIndex'], (item['romItemId'], owner['jobId']))
for index, (item, job) in human_teaching.items():
    for site in (sites[2], sites[5]):
        for equipped in (False, True):
            for written in (0, 25):
                for stack in (STACK, STACK - 4):
                    result = execute(expanded, site, index, 228, stack, written,
                                     (item,) if equipped else (), through=True, job=job)
                    actual = expanded.read(result[3], 1)[0]
                    wanted = written | (128 if equipped else 0)
                    isolated = not equipped or expanded.read(UNIT + 0xD0, 56) == bytes([0x6D]) * 56
                    check('human_post_write', [hex(site[0]), index, item, equipped, written, stack % 8],
                          actual == wanted and isolated, {'actual': actual, 'wanted': wanted, 'statIsolation': isolated})

check('alignment', len(aligned), bool(aligned) and all(sp % 8 == 0 for _, sp in aligned),
      [(hex(a), hex(sp)) for a, sp in aligned if sp % 8])
report = {'passed': not failures, 'romSha1': hashlib.sha1(probe).hexdigest(),
          'baseSha1': hashlib.sha1(base).hexdigest(), 'checks': checks,
          'measuredHelperEntries': len(aligned), 'failures': failures,
          'limitations': ['Live owners only; actor/victim copy lifecycles tested separately',
                          'Native post-write continuations executed, full battle effect dispatch not exercised']}
(ROOT / 'build/reports/ap-writers.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({**report, 'failures': failures[:20], 'totalFailures': len(failures)}))
if failures: sys.exit(1)
