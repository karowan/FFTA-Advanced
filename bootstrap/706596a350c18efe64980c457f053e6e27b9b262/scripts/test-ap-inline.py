"""Execute installed AP interior hooks and complete native equipment setters.

Uses an immutable in-memory snapshot of both probes and checks their manifest
hashes before execution. No game window or user save is touched.
"""
import ast
import ctypes as C
import hashlib
import importlib.util
import json
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *

UNIT, EQUIPMENT, RETURN, STACK = 0x02000080, 0x02002000, 0x08000100, 0x03007000
# Reuse only the audited native execution/boot definitions; importing the
# equipment test normally would run its unrelated full matrix.
source = ast.parse((ROOT / 'scripts/test-equipment-legality.py').read_text())
definitions = [n for n in source.body if isinstance(n, (ast.ClassDef, ast.FunctionDef))
               and n.name in ('ARM', 'iwram_from_boot')]
exec(compile(ast.Module(body=definitions, type_ignores=[]), '<equipment-harness>', 'exec'))

def load_probe(name):
    prefix = ROOT / 'build/expansion/probes' / name
    data = prefix.with_suffix('.gba').read_bytes()
    metadata = json.loads(prefix.with_suffix('.json').read_text())
    assert hashlib.sha1(data).hexdigest() == metadata['romSha1'], 'Probe changed during read'
    return data, metadata

base, base_meta = load_probe('content-inventory')
probe, metadata = load_probe('ability-core')
assert metadata['baseSha1'] == hashlib.sha1(base).hexdigest(), 'AP probe has a different baseline'
registry = json.loads((ROOT / 'build/expansion/registry.json').read_text())
iwram = iwram_from_boot()
native, expanded = ARM(base, iwram), ARM(probe, iwram)
registers = [UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3,
             UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7,
             UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11]
failures, checks = [], {}

def check(group, case, condition, details=None):
    checks[group] = checks.get(group, 0) + 1
    if not condition:
        failures.append({'group': group, 'case': case, 'details': details})

def setup(machine, job=2, index=1, value=0, gear=()):
    machine.put(0x02000000, bytes(0x40000))
    machine.put(0x02001E70, b'FFTAEXP1\x01')
    machine.fixture(job, gear)
    # Mark counts explicitly: constructor/load normalization is separate work.
    race = machine.read(UNIT + 6, 1)[0]
    count = next(r['totalCount'] for r in registry['races'] if r['id'] == race)
    machine.put(UNIT + 0x34, bytes([count]))
    address = 0x02001B40 + index - 144 if race == 1 and index >= 144 else UNIT + 0x40 + index
    machine.put(address, bytes([value]))
    machine.put(UNIT + 0xD0, bytes([0x6D]) * (0x108 - 0xD0))
    machine.put(0x02001941, bytes([99]) * 460)
    return address

# start, continuation, unit register, index register, live registers compared.
sites = [
    (0xCAFEA, 0xCAFF6, 7, 5, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),
    (0xCB148, 0xCB154, 7, 5, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),
    (0xCAEC4, 0xCAED0, 8, 5, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),
    (0x49032, 0x4903E, 8, 6, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),
    (0xCCF7E, 0xCCF8C, 5, 1, [3, 4, 5, 6, 7, 8, 9, 10, 11]),
    (0xCB036, 0xCB044, 7, 5, [3, 4, 5, 6, 7, 8, 9, 10, 11]),
    (0xCB192, 0xCB1A0, 7, 5, [3, 4, 5, 6, 7, 8, 9, 10, 11]),
    (0xCD072, 0xCD07E, 8, 1, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),
    (0xCD19E, 0xCD1AA, 8, 2, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),
]

helper_visits, helper_addresses = [], set()
def helper_alignment(u, address, size, data):
    helper_visits.append((address, u.reg_read(UC_ARM_REG_SP)))

# Resolve helper calls from the frozen ROM rather than concurrent build symbols.
for start, _, _, _, _ in sites:
    jump = (start + 5) & ~3
    entry = expanded.word(0x08000000 + jump + 4) & ~1
    code = expanded.read(entry, 160)
    for offset in range(0, 156, 2):
        a, b = struct.unpack_from('<HH', code, offset)
        if a & 0xF800 == 0xF000 and b & 0xF800 == 0xF800:
            displacement = ((a & 2047) << 12) | ((b & 2047) << 1)
            if displacement & 0x400000: displacement -= 0x800000
            address = entry + offset + 4 + displacement
            if address not in helper_addresses:
                expanded.u.hook_add(UC_HOOK_CODE, helper_alignment, begin=address, end=address)
                helper_addresses.add(address)
            break
    else: raise AssertionError(f'Cannot resolve helper for {start:x}')

def interior(machine, site, index, value, stack):
    start, end, unit_reg, index_reg, live = site
    setup(machine, index=index, value=value)
    values = [0x33000000 + n for n in range(12)]
    values[unit_reg], values[index_reg] = UNIT, index
    if start in (0xCB036, 0xCB192): values[6] = UNIT + 0x34
    for register, content in zip(registers, values): machine.u.reg_write(register, content)
    machine.u.reg_write(UC_ARM_REG_CPSR, 0x20000030)
    machine.u.reg_write(UC_ARM_REG_SP, stack)
    machine.u.reg_write(UC_ARM_REG_LR, RETURN | 1)
    if start == 0xCD19E and value == 0: end = 0xCD1BC
    machine.u.emu_start(0x08000001 + start, 0x08000000 + end, count=20000)
    assert machine.u.reg_read(UC_ARM_REG_PC) == 0x08000000 + end, f'Continuation {start:x}'
    assert machine.u.reg_read(UC_ARM_REG_SP) == stack, f'Interior stack {start:x}'
    return ([machine.u.reg_read(r) for r in registers], machine.read(0x02000000, 0x40000),
            machine.u.reg_read(UC_ARM_REG_CPSR) & 0xF0000000)

for site in sites:
    for index in (1, 20, 141):
        for value in (0, 1, 30, 100, 128, 158, 228, 255):
            for stack in (STACK, STACK - 4):
                old = interior(native, site, index, value, stack)
                new = interior(expanded, site, index, value, stack)
                different = [(r, old[0][r], new[0][r]) for r in site[4] if old[0][r] != new[0][r]]
                check('original_interior', [hex(site[0]), index, value, stack % 8],
                      not different and old[1] == new[1], different)
                if site[0] in (0xCAFEA, 0xCB148, 0xCAEC4, 0xCD072):
                    # The following native instructions establish carry before
                    # using it; only the reproduced AND's N/Z are meaningful.
                    check('result_nz_flags', [hex(site[0]), value, stack % 8],
                          old[2] & 0xC0000000 == new[2] & 0xC0000000, [old[2], new[2]])

for site in sites:
    for index in (144, 160, 177):
        for value in (0, 30, 100, 128, 158, 228):
            for stack in (STACK, STACK - 4):
                regs, ram, flags = interior(expanded, site, index, value, stack)
                wanted = value
                if site[0] == 0xCCF7E: wanted |= 128
                if site[0] in (0xCB036, 0xCB192): wanted &= 127
                actual = ram[0x1B40 + index - 144]
                unchanged = ram[0x80 + 0xD0:0x80 + 0x108] == bytes([0x6D]) * 56
                result_ok = True
                if site[0] in (0xCAFEA, 0xCB148, 0xCAEC4): result_ok = regs[4] == value & 127
                if site[0] == 0x49032: result_ok = regs[7] == 0x02001B40 + index - 144 and regs[4] == value and regs[0] == 1
                if site[0] == 0xCD072: result_ok = regs[0] == value & 128
                if site[0] == 0xCD19E: result_ok = regs[0] == value
                check('extended_interior', [hex(site[0]), index, value, stack % 8],
                      actual == wanted and unchanged and result_ok, {'ap': actual, 'wanted': wanted, 'unitTailUnchanged': unchanged, 'resultCorrect': result_ok})

# Full native equipment calls verify that deliberately dead scratch registers
# in grant/revoke trampolines really are dead through the function return.
for job in (2, 16, 20, 28, 36):
    for item in (1, 32, 52, 88, 150, 200, 253, 288):
        for value in (0, 30, 228):
            for function in (0x080CCF44, 0x080CAF78, 0x080CB0D8):
                for machine in (native, expanded):
                    setup(machine, job=job, gear=(item,))
                    machine.put(UNIT + 0x41, bytes([value]) * 141)
                    machine.call(function, UNIT, item if function == 0x080CCF44 else 0, 0)
                check('original_whole_equipment', [job, item, value, hex(function)],
                      native.read(0x02000000, 0x40000) == expanded.read(0x02000000, 0x40000))

for item in registry['items']:
    for owner in item['teaching']:
        job, index = owner['jobId'], owner['abilityIndex']
        for stack in (STACK, STACK - 4):
            for function in (0x080CAF78, 0x080CB0D8):
                address = setup(expanded, job=job, index=index, value=1, gear=(item['romItemId'],))
                expanded.call(0x080CCF44, UNIT, item['romItemId'], stack=stack)
                granted = expanded.read(address, 1)[0]
                expanded.call(function, UNIT, 0, 0, stack=stack)
                revoked = expanded.read(address, 1)[0]
                check('extended_whole_equipment', [job, item['romItemId'], index, hex(function), stack % 8],
                      granted == 129 and revoked == 1 and expanded.read(UNIT + 0x2A, 2) == b'\0\0',
                      {'grant': granted, 'remove': revoked})

for function, availability in [(0x080CCFB8, True), (0x080CD0EC, False)]:
    for value in (0, 1, 128, 129, 228):
        for ability_type in (1, 2, 3, 4, 5):
            for stack in (STACK, STACK - 4):
                setup(expanded, job=116)
                expanded.put(0x02001B40, bytes([value]) * 34)
                wanted = []
                for index in range(144, 178):
                    record = expanded.call(0x080CD480, 1, index)
                    if expanded.read(record + 6, 1)[0] == ability_type and (value & 128 if availability else value):
                        wanted.append(index)
                count = expanded.call(function, UNIT, EQUIPMENT, ability_type, stack=stack)
                actual = list(expanded.read(EQUIPMENT, count))
                check('extended_whole_typed_lists', [hex(function), value, ability_type, stack % 8],
                      actual == wanted, {'actual': actual, 'wanted': wanted})

# Run native result awarding from the installed pointer hook all the way
# through cost comparison, gain, clamp, notification and final byte write.
for index in range(144, 178):
    record = expanded.call(0x080CD480, 1, index)
    cost = expanded.read(record + 7, 1)[0]
    for low in (0, cost - 1, cost):
        for high in (0, 128):
            for gain in (1, 5, 50):
                for stack in (STACK, STACK - 4):
                    old_byte = low | high
                    address = setup(expanded, index=index, value=old_byte)
                    expanded.put(0x03002810, struct.pack('<I', 0x02022000))
                    expanded.put(0x0201F514, bytes([gain]))
                    expanded.put(stack, bytes(0x80))
                    expanded.put(stack + 0x64, struct.pack('<I', index))
                    for n, register in enumerate(registers): expanded.u.reg_write(register, 0)
                    expanded.u.reg_write(UC_ARM_REG_R8, UNIT)
                    expanded.u.reg_write(UC_ARM_REG_R6, index)
                    expanded.u.reg_write(UC_ARM_REG_SP, stack)
                    expanded.u.reg_write(UC_ARM_REG_LR, RETURN | 1)
                    expanded.u.emu_start(0x08049033, 0x080490A6, count=20000)
                    assert expanded.u.reg_read(UC_ARM_REG_PC) == 0x080490A6
                    assert expanded.u.reg_read(UC_ARM_REG_SP) == stack
                    wanted = old_byte if low >= cost else ((cost | 128) if low + gain >= cost else (low + gain) | high)
                    actual = expanded.read(address, 1)[0]
                    mastered = low < cost and low + gain >= cost
                    notification = expanded.read(0x02022000 + 0x696, 1)[0]
                    check('extended_results_award', [index, old_byte, gain, stack % 8],
                          actual == wanted and notification == (index if mastered else 0)
                          and expanded.read(UNIT + 0xD0, 56) == bytes([0x6D]) * 56,
                          {'actual': actual, 'wanted': wanted, 'notification': notification})

ui_sites = [(0x7B9AA, 0x7B9B6, 0x7B9FE), (0x7B9CC, 0x7B9D8, None),
            (0x7C362, 0x7C36E, 0x7C410), (0x7C49C, 0x7C4A8, 0x7C53A),
            (0x7C5D6, 0x7C5E6, None), (0x7C694, 0x7C6A4, None),
            (0x7C770, 0x7C780, None), (0xC8F76, 0xC8F82, None),
            (0x7C4D8, 0x7C50E, None)]
# The primary preview counterpart was found during this review. Include it
# automatically once the next probe installs the preserving push-r3 stub.
primary_preview_installed = struct.unpack_from('<H', probe, 0x7C392)[0] == 0xB408
if primary_preview_installed: ui_sites.append((0x7C392, 0x7C3D6, None))

def ui_interior(machine, site, index, value, stack, copied):
    start, end, zero = site
    setup(machine, index=index, value=73 if copied else value)
    menu, pointer, row = 0x02008000, 0x02021000, 0x02022000
    owner = menu + 0x1BE4 if copied or start in (0x7C4D8, 0x7C392) else UNIT
    if owner != UNIT:
        machine.put(owner, machine.read(UNIT, 264))
        machine.put(0x0203FF30, struct.pack('<5I', 0x31525041, 0, 0, 0, menu))
        machine.put(menu + 0x7240, bytes([0x59]) * 36)
    machine.put(0x03002818, struct.pack('<I', menu))
    address = owner + 0x40 + index
    if index >= 144 and machine is expanded:
        address = (menu + 0x7240 if owner != UNIT else 0x02001B40) + index - 144
    machine.put(address, bytes([value]))
    machine.put(pointer, struct.pack('<I', owner))
    machine.put(stack + 0x524, struct.pack('<I', index))
    values = [0x33000000 + n for n in range(12)]
    values[4], values[6] = row, index
    if start in (0x7B9AA, 0x7B9CC): values[1] = pointer
    elif start == 0x7C362: values[1], values[2] = 0x10, pointer - 0x10
    elif start == 0x7C49C: values[0] = pointer
    elif start in (0x7C5D6, 0x7C694): values[1] = owner
    elif start == 0x7C770: values[3] = owner
    elif start == 0xC8F76: values[7], values[4] = owner, index
    elif start == 0x7C4D8: values[3] = 0x03002818
    elif start == 0x7C392: values[1] = menu
    for register, content in zip(registers, values): machine.u.reg_write(register, content)
    machine.u.reg_write(UC_ARM_REG_CPSR, 0x20000030)
    machine.u.reg_write(UC_ARM_REG_SP, stack)
    machine.u.reg_write(UC_ARM_REG_LR, RETURN | 1)
    before = machine.read(0x02000000, 0x40000)
    if value == 0 and zero: end = zero
    machine.u.emu_start(0x08000001 + start, 0x08000000 + end, count=20000)
    assert machine.u.reg_read(UC_ARM_REG_PC) == 0x08000000 + end, f'UI continuation {start:x}'
    assert machine.u.reg_read(UC_ARM_REG_SP) == stack, f'UI stack {start:x}'
    after = machine.read(0x02000000, 0x40000)
    mutations = [] if before == after else [(i, a, b) for i, (a, b) in enumerate(zip(before, after)) if a != b]
    return [machine.u.reg_read(r) for r in registers], mutations

for site in ui_sites:
    for index in (1, 20, 141, 144, 160, 177):
        for value in (0, 1, 100, 128, 228):
            for stack in (STACK, STACK - 4):
                for copied in (False, True):
                    old = ui_interior(native, site, index, value, stack, copied)
                    new = ui_interior(expanded, site, index, value, stack, copied)
                    different = [(r, old[0][r], new[0][r]) for r in range(12) if old[0][r] != new[0][r]]
                    check('ui_original' if index < 142 else 'ui_extended',
                          [hex(site[0]), index, value, stack % 8, 'copy' if copied else 'live'],
                          not different and old[1] == new[1],
                          {'registers': different, 'nativeWrites': old[1], 'expandedWrites': new[1]})

check('c_boundary_alignment', len(helper_visits), bool(helper_visits) and all(sp % 8 == 0 for _, sp in helper_visits),
      [(hex(a), hex(sp)) for a, sp in helper_visits if sp % 8])
report = {'passed': not failures, 'romSha1': hashlib.sha1(probe).hexdigest(),
          'baseSha1': hashlib.sha1(base).hexdigest(), 'checks': checks,
          'measuredHelperEntries': len(helper_visits), 'failures': failures,
          'uiHookSites': [hex(site[0]) for site in ui_sites],
          'primaryPreviewInstalled': primary_preview_installed,
          'limitations': ['Live roster and registered party-copy UI reads; constructor/load/copy registration lifecycle is separate work',
                          'Original full equipment cases use synthetic AP bytes',
                          'Result award continuation executed; full mission result UI not exercised']}
(ROOT / 'build/reports/ap-inline.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({**report, 'failures': failures[:12], 'totalFailures': len(failures)}))
if failures: sys.exit(1)
