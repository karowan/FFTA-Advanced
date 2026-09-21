"""Execute native equipment legality against the expansion content probe.

Uses the bundled Python runtime (Pillow required by the headless boot harness).
No game window, user save, or ROM file is changed. Fails while approved new
equipment rules remain unimplemented; --allow-incomplete writes diagnostics
without a failing process exit code.
"""
import argparse
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

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--rom', default='build/expansion/probes/content-inventory.gba')
parser.add_argument('--allow-incomplete', action='store_true')
args = parser.parse_args()
probe_path = ROOT / args.rom
clean = (ROOT / 'roms/clean/FFTA_US_clean.gba').read_bytes()
probe = probe_path.read_bytes()
registry = json.loads((ROOT / 'build/expansion/registry.json').read_text())
UNIT, EQUIPMENT, RETURN, STACK = 0x02000080, 0x02002000, 0x08000100, 0x03007000


def iwram_from_boot():
    spec = importlib.util.spec_from_file_location('equipment_harness', ROOT / 'scripts/emulator-test.py')
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    emulator = harness.Emulator(ROOT / 'roms/clean/FFTA_US_clean.gba')
    try:
        emulator.run(120)
        return C.string_at(*emulator.maps[0x03000000])
    finally:
        emulator.close()


class ARM:
    def __init__(self, rom, iwram):
        self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        for address, size in [(0, 0x4000), (0x02000000, 0x40000),
                              (0x03000000, 0x8000), (0x08000000, 0x02000000)]:
            self.u.mem_map(address, size)
        self.put(0x08000000, rom)
        self.put(0x03000000, iwram)
        self.calls = 0

    def put(self, address, data): self.u.mem_write(address, bytes(data))
    def read(self, address, size): return bytes(self.u.mem_read(address, size))
    def word(self, address): return struct.unpack('<I', self.read(address, 4))[0]

    def call(self, address, *values, stack=STACK):
        for reg, value in zip([UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3], values):
            self.u.reg_write(reg, value)
        preserved = [UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7,
                     UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11]
        for i, reg in enumerate(preserved): self.u.reg_write(reg, 0x55000000 + i)
        self.u.reg_write(UC_ARM_REG_SP, stack)
        self.u.reg_write(UC_ARM_REG_LR, RETURN | 1)
        self.u.emu_start(address | 1, RETURN, count=50000)
        assert self.u.reg_read(UC_ARM_REG_PC) == RETURN, f'No return: {address:x}/{values}'
        assert self.u.reg_read(UC_ARM_REG_SP) == stack, f'Stack changed: {address:x}'
        for i, reg in enumerate(preserved):
            assert self.u.reg_read(reg) == 0x55000000 + i, f'ABI failure: {address:x}/{reg}'
        self.calls += 1
        return self.u.reg_read(UC_ARM_REG_R0)

    def fixture(self, job, equipment=(), support=0, alias=False):
        race = self.call(0x080C8570, job, job, 1)
        data = bytearray(264)
        data[4] = 2 if alias else 1
        data[5], data[7], data[6] = 0x50 if alias else job, job, race
        for slot, item in enumerate(equipment): struct.pack_into('<H', data, 0x2A + 2 * slot, item)
        if support:
            # Inject only a support record in emulator RAM, without depending
            # on the race owning a particular original lesson index.
            pointers = self.word(0x080CD538)
            original_table = self.word(pointers + race * 4)
            synthetic = bytearray(self.read(original_table, 0x800))
            synthetic[0x80 * 8:0x81 * 8] = struct.pack('<HHHBB', 0, 0, support, 3, 1)
            self.put(0x02022000, synthetic)
            synthetic_pointers = bytearray(self.read(pointers, 28))
            struct.pack_into('<I', synthetic_pointers, race * 4, 0x02022000)
            self.put(0x02021800, synthetic_pointers)
            self.put(0x080CD538, struct.pack('<I', 0x02021800))
            data[0x3B] = 0x80
        self.put(UNIT, data)
        return bytes(data)

    def can_equip(self, item, slot):
        before = self.read(UNIT, 264)
        result = self.call(0x080CB48C, UNIT, item, slot)
        assert self.read(UNIT, 264) == before, 'Legality query changed unit'
        return result

    def layout(self, equipment, invalid_slot=255, flags=0):
        payload = struct.pack('<5H', *(list(equipment) + [0] * (5 - len(equipment))))
        self.put(EQUIPMENT, payload)
        return self.call(0x080CABA8, UNIT, EQUIPMENT, invalid_slot, flags)


iwram = iwram_from_boot()
native, expanded = ARM(clean, iwram), ARM(probe, iwram)
original_support_pointers = {machine: machine.word(0x080CD538) for machine in [native, expanded]}


def fixture(machine, job, equipment=(), support=0, alias=False):
    machine.put(0x080CD538, struct.pack('<I', original_support_pointers[machine]))
    return machine.fixture(job, equipment, support, alias)


checks = {}
failures = []


def expect(group, label, result, allowed):
    checks[group] = checks.get(group, 0) + 1
    if bool(result & 1) == allowed:
        failures.append({'group': group, 'case': label, 'expectedAllowed': allowed, 'result': result})


# Differential preservation: original job/item behavior, plus representative
# legal and illegal multi-item layouts with the native support IDs 6/7/8/15.
for job in range(2, 44):
    for machine in [native, expanded]: fixture(machine, job)
    for item in range(1, 362):
        old = native.can_equip(item, 0)
        actual = expanded.can_equip(item, 0)
        checks['original_single_item'] = checks.get('original_single_item', 0) + 1
        if actual != old:
            failures.append({'group': 'original_single_item', 'case': [job, item], 'expected': old, 'result': actual})
    for support in [0, 6, 7, 8, 15]:
        for machine in [native, expanded]: fixture(machine, job, support=support)
        for layout in [[1, 253], [253, 1], [1, 52], [52, 1], [52, 253],
                       [253, 52], [1, 1], [52, 52], [265, 288, 253, 1]]:
            old, actual = native.layout(layout), expanded.layout(layout)
            checks['original_layout'] = checks.get('original_layout', 0) + 1
            if actual != old:
                failures.append({'group': 'original_layout', 'case': [job, support, layout], 'expected': old, 'result': actual})

items = registry['items']
for item in items:
    owners = sorted({owner['jobId'] for owner in item['teaching']})
    for job in owners:
        fixture(expanded, job)
        for slot in [0, 4]:
            expect('new_single_item', [job, item['romItemId'], slot],
                   expanded.can_equip(item['romItemId'], slot), True)

axes = [item['romItemId'] for item in items if item['category'] == 'Axe']
for job in [2, 16, 118]:
    for support in [0, 6, 7, 8, 15]:
        for axe in axes:
            fixture(expanded, job, support=support)
            expect('axe_alone', [job, support, axe], expanded.can_equip(axe, 0), True)
            # Both native shields and weapons, plus another new axe and a
            # new one-handed sword; race/category rejection cannot make an
            # invalid combination legal even with Monkey Grip/Double Sword.
            for other in [1, 52, 253, 384, axe]:
                for layout in [[axe, other], [other, axe]]:
                    expect('axe_no_second_hand', [job, support, layout], expanded.layout(layout), False)
            fixture(expanded, job, [253], support=support)
            expect('axe_menu_with_shield', [job, support, axe], expanded.can_equip(axe, 1), False)
            fixture(expanded, job, [axe], support=support)
            expect('shield_menu_with_axe', [job, support, axe], expanded.can_equip(253, 1), False)

# New shield-using jobs need both slot orders. Native one-handed donors test
# the hardcoded allowlists separately from the new-item identity cutoff.
for job, weapons in [(117, [1, 384]), (119, [1, 384]), (125, [32, 88, 400])]:
    fixture(expanded, job)
    for weapon in weapons:
        for layout in [[weapon, 253], [253, weapon]]:
            expect('new_job_shield', [job, layout], expanded.layout(layout), True)

for job in [117, 119]:
    for support in [0, 6]:
        fixture(expanded, job, support=support)
        for layout in [[52, 253], [253, 52]]:
            expect('new_job_native_monkey_grip', [job, support, layout],
                   expanded.layout(layout), support == 6)
        expect('new_job_excess_hands', [job, support, [253, 253, 52]],
               expanded.layout([253, 253, 52]), False)

# Preserve r2's selected-invalid-slot encoding and all native r3 ability-loss
# flags through an entry wrapper. These flags affect equipment validation.
for job in [2, 3, 16, 30]:
    for support in [0, 6, 7, 8, 15]:
        for machine in [native, expanded]: fixture(machine, job, support=support)
        for layout in [[1, 253], [253, 52], [1, 1], [52, 52], [265, 288, 253, 1]]:
            for selected in [0, 1, 2, 3, 4, 255]:
                for flags in [0, 2, 4, 8, 14]:
                    old = native.layout(layout, selected, flags)
                    actual = expanded.layout(layout, selected, flags)
                    checks['original_error_and_flags'] = checks.get('original_error_and_flags', 0) + 1
                    if actual != old:
                        failures.append({'group': 'original_error_and_flags',
                                         'case': [job, support, layout, selected, flags],
                                         'expected': old, 'result': actual})

for job in [2, 16, 118]:
    fixture(expanded, job, support=6)
    # Shoes are not a second hand and must remain legal alongside an axe.
    boots = next(item for item in range(1, 362)
                 if expanded.call(0x080CA7A4, item, 3) == 27)
    expect('axe_with_armor', [job, 453, boots], expanded.layout([453, boots]), True)

fixture(expanded, 2, support=6)
for layout in [[453, 253], [253, 453], [288, 453, 0, 253]]:
    conflicting_slot = 3 if len(layout) == 4 else 1
    for selected in [0, 1, 2, 3, 4, 255]:
        result = expanded.layout(layout, selected)
        wanted = 0x81 if selected == conflicting_slot else 1
        checks['axe_error_index'] = checks.get('axe_error_index', 0) + 1
        if result != wanted:
            failures.append({'group': 'axe_error_index', 'case': [layout, selected],
                             'expected': wanted, 'result': result})

# Record the actual opening fixture: Marche's existing shield makes an axe
# rejection correct even after all new-item classification problems are fixed.
fixture(expanded, 2, [1, 288, 253], alias=True)
expect('starting_marche_shield', 'Recruit Axe while starter shield remains', expanded.can_equip(453, 0), False)
fixture(expanded, 2, [1, 288], alias=True)
expect('starting_marche_no_shield', 'Recruit Axe after shield removed', expanded.can_equip(453, 0), True)

# Exercise the actual native cleanup consumer, not only the returned error
# byte. It should preserve the first hand entry and unrelated armor.
for gear, wanted in [([453, 253], [453, 0, 0, 0, 0]),
                     ([253, 453], [253, 0, 0, 0, 0]),
                     ([1, 453], [1, 0, 0, 0, 0]),
                     ([453, 1], [453, 0, 0, 0, 0]),
                     ([1, 384, 453], [1, 0, 0, 0, 0]),
                     ([288, 453, 0, 253], [288, 453, 0, 0, 0])]:
    before = fixture(expanded, 2, gear, support=6)
    queried = expanded.call(0x080CB54C, UNIT, 0)
    unchanged = expanded.read(UNIT, 264) == before
    cleaned = expanded.call(0x080CB54C, UNIT, 1)
    actual = list(struct.unpack('<5H', expanded.read(UNIT + 0x2A, 10)))
    valid_afterward = expanded.call(0x080CB54C, UNIT, 0) == 0
    checks['native_cleanup'] = checks.get('native_cleanup', 0) + 1
    if queried != 1 or not unchanged or cleaned != 1 or actual != wanted or not valid_afterward:
        failures.append({'group': 'native_cleanup', 'case': gear, 'expected': wanted,
                         'result': actual, 'query': queried, 'clean': cleaned,
                         'queryUnchanged': unchanged, 'validAfterward': valid_afterward})

# Native callers can enter on either four- or eight-byte stack alignment.
# Assembly-to-C boundaries must normalize both to AAPCS's eight-byte rule.
# Resolve helper entry points from this immutable ROM's actual trampolines,
# not a potentially newer engine.symbols file during parallel development.
abi = ARM(probe, iwram)
helper_entries = {}
for literal, name in [(0x080CABB0, 'axe_guard'), (0x080CAD08, 'weapon_classifier')]:
    entry = abi.word(literal) & ~1
    code = abi.read(entry, 128)
    for offset in range(0, 124, 2):
        first, second = struct.unpack_from('<HH', code, offset)
        if first & 0xF800 == 0xF000 and second & 0xF800 == 0xF800:
            displacement = ((first & 2047) << 12) | ((second & 2047) << 1)
            if displacement & (1 << 22): displacement -= 1 << 23
            helper_entries[entry + offset + 4 + displacement] = name
            break
    else:
        raise AssertionError(f'Cannot locate C helper call for {name}')
abi_case = [None]


def check_helper_entry(u, address, size, data):
    actual = u.reg_read(UC_ARM_REG_SP)
    checks['c_helper_alignment'] = checks.get('c_helper_alignment', 0) + 1
    if actual % 8:
        failures.append({'group': 'c_helper_alignment', 'case': abi_case[0],
                         'helper': helper_entries[address], 'stack': hex(actual)})


for address in helper_entries:
    abi.u.hook_add(UC_HOOK_CODE, check_helper_entry, begin=address, end=address)
for stack in [STACK, STACK - 4]:
    for function in [0x080CB48C, 0x080CABA8]:
        abi_case[0] = [hex(function), hex(stack)]
        abi.fixture(117)
        abi.put(EQUIPMENT, struct.pack('<5H', 384, 0, 0, 0, 0))
        if function == 0x080CB48C:
            abi.call(function, UNIT, 384, 0, stack=stack)
        else:
            abi.call(function, UNIT, EQUIPMENT, 255, 0, stack=stack)

report = {'passed': not failures, 'rom': str(probe_path),
          'romSha1': hashlib.sha1(probe).hexdigest(), 'checks': checks,
          'nativeCalls': native.calls + expanded.calls + abi.calls, 'failures': failures,
          'limitations': ['Synthetic support records exercise engine support IDs, not AP mastery',
                          'Category31 attack/battle animation consumers not executed',
                          'Battle effects and rendering are not equipment-legality tests']}
destination = ROOT / 'build/reports/equipment-legality.json'
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({**report, 'failures': failures[:12], 'totalFailures': len(failures)}))
if failures and not args.allow_incomplete: sys.exit(1)
