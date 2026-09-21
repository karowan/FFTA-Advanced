"""Stress native battle inventory allocation and wide-index consumers.

Runs real ARM7 Thumb routines in Unicorn, with the game's boot-installed
IWRAM helpers. Synthetic item records make every equipment ID a compatible
sword, so the test reaches the conservative 446-entry capacity. No user saves
or game windows are touched. This is not a rendered battle-playthrough test.
"""
import ctypes as C
import hashlib
import importlib.util
import json
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import *

OUT = ROOT / 'build/expansion/probes'
ROM = (OUT / 'inventory-menus.gba').read_bytes()
MENU, CONTEXT, UNIT = 0x02008000, 0x0200E000, 0x02000080
HEAP, HEAP_SIZE = 0x02010000, 0x18000
ORDER = list(range(1, 362)) + list(range(376, 461))


def native_iwram():
    spec = importlib.util.spec_from_file_location('harness', ROOT / 'scripts/emulator-test.py')
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    emulator = h.Emulator(ROOT / 'roms/clean/FFTA_US_clean.gba')
    try:
        emulator.run(120)
        return C.string_at(*emulator.maps[0x03000000])
    finally:
        emulator.close()


class ARM:
    def __init__(self, iwram):
        self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        for address, size in [(0, 0x4000), (0x02000000, 0x40000),
                              (0x03000000, 0x8000), (0x08000000, 0x2000000)]:
            self.u.mem_map(address, size)
        self.u.mem_write(0x08000000, ROM)
        self.u.mem_write(0x03000000, iwram)

    def put(self, address, data): self.u.mem_write(address, bytes(data))
    def get(self, address, size): return bytes(self.u.mem_read(address, size))
    def w32(self, address, value): self.put(address, struct.pack('<I', value))
    def w16(self, address, value): self.put(address, struct.pack('<H', value))
    def r32(self, address): return struct.unpack('<I', self.get(address, 4))[0]
    def r16(self, address): return struct.unpack('<H', self.get(address, 2))[0]

    def call(self, address, *args, stop=0x08000100):
        for reg, value in zip([UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3], args):
            self.u.reg_write(reg, value)
        saved = [UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7,
                 UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11]
        for i, reg in enumerate(saved): self.u.reg_write(reg, 0x55000000 + i)
        self.u.reg_write(UC_ARM_REG_SP, 0x03007000)
        self.u.reg_write(UC_ARM_REG_LR, 0x08000101)
        self.u.emu_start(address | 1, stop, count=3000000)
        assert self.u.reg_read(UC_ARM_REG_PC) == stop, f'No return: {address:x}'
        if stop == 0x08000100:
            assert self.u.reg_read(UC_ARM_REG_SP) == 0x03007000, f'Stack: {address:x}'
            for i, reg in enumerate(saved):
                assert self.u.reg_read(reg) == 0x55000000 + i, f'ABI: {address:x}/{reg}'
        return self.u.reg_read(UC_ARM_REG_R0)


def fixture(iwram, action, capacity):
    m = ARM(iwram)
    m.put(HEAP - 16, b'\xA5' * (HEAP_SIZE + 32))
    m.call(0x080070C8, HEAP, HEAP_SIZE)
    m.initial_heap_header = m.get(HEAP, 20)
    m.w32(0x02008FF0, 0x02008FF4)
    m.w32(0x02008FF4, HEAP)
    m.w32(0x0200F438, CONTEXT)
    m.w32(CONTEXT + 0x18, UNIT)
    unit = bytearray(264)
    unit[4] = 1
    unit[5] = unit[7] = 2
    m.put(UNIT, unit)
    m.put(0x02001941, bytes([1]) * 460)
    # One item is fully equipped; both native builders must disable its row.
    m.w16(UNIT + 0x2A, 460)
    table = m.r32(0x080CA7C4)
    sword = m.get(table + 32, 32)
    synthetic = bytearray(sword * 461)
    for item in range(461): struct.pack_into('<H', synthetic, item * 32, item)
    m.put(0x09B00000, synthetic)
    m.w32(0x080CA7C4, 0x09B00000)
    m.w32(0x08079AEC, 0x09B00000)
    if capacity is not None:
        for offset in (0x083914F8, 0x0839150C): m.w16(offset, capacity)
    m.put(CONTEXT + 4, [action])
    m.put(0x0203F7F0, b'\xDA' * 16)
    m.put(0x0203FF30, b'\xDB' * 16)
    return m


def stress(iwram, action, capacity=None, negative=False):
    m = fixture(iwram, action, capacity)
    allocations, overflows, headers = [], [], {}
    pending = []

    def code(u, address, size, data):
        if address == 0x08005B28:
            pending.append(u.reg_read(UC_ARM_REG_R0))
        elif address == 0x08005B36:
            request = pending.pop()
            pointer = u.reg_read(UC_ARM_REG_R0)
            assert HEAP <= pointer < HEAP + HEAP_SIZE and pointer + request <= HEAP + HEAP_SIZE
            allocations.append({'bytes': request, 'pointer': pointer})
        elif address in (0x0802777A, 0x08027832):
            for allocation in allocations:
                pointer = allocation['pointer']
                headers[pointer - 12] = m.get(pointer - 12, 12)
        elif address in (0x080277EA, 0x08027900):
            for pointer, before in headers.items():
                assert m.get(pointer, 12) == before, 'Native list overwrote heap block header'

    def write(u, access, address, size, value, data):
        pc = u.reg_read(UC_ARM_REG_PC)
        if pc in (0x080277AC, 0x080278AE, 0x080277C0, 0x080278D4):
            allocation = allocations[0 if size == 4 else 1]
            if not (allocation['pointer'] <= address and address + size <= allocation['pointer'] + allocation['bytes']):
                overflows.append({'pc': pc, 'address': address, 'value': value})
                u.emu_stop()

    hooks = [m.u.hook_add(UC_HOOK_CODE, code), m.u.hook_add(UC_HOOK_MEM_WRITE, write)]
    if negative:
        try: m.call(0x08027DA0, MENU)
        except AssertionError:
            if not overflows: raise
        assert len(overflows) == 1 and overflows[0]['value'] == ORDER[252]
        return {'action': action, 'capacity': capacity, 'firstOverflow': overflows[0]}
    m.call(0x08027DA0, MENU)
    for hook in hooks: m.u.hook_del(hook)
    assert not overflows
    assert [a['bytes'] for a in allocations[:3]] == [446 * 4, 446, 192]
    assert len(allocations) == 4
    assert m.r16(MENU + 0x84) == 446
    ids, flags = m.r32(MENU + 0x94), m.r32(MENU + 0x98)
    assert list(struct.unpack('<446I', m.get(ids, 446 * 4))) == ORDER
    # Compare Draw's flags with the real equipment legality predicate. This
    # checks byte-array indexing independently from correctness of that shared
    # predicate; the explicit differential below reports its ID-range behavior.
    expected_flags = bytes(int(m.call(0x080CB48C, UNIT, item, 1) == 0)
                           for item in ORDER[:-1]) + b'\0' if action == 14 else bytes([1]) * 445 + b'\0'
    assert m.get(flags, 446) == expected_flags
    legality = {'originalSword': m.call(0x080CB48C, UNIT, 1, 1),
                'expandedSword': m.call(0x080CB48C, UNIT, 376, 1)}
    assert m.get(HEAP - 16, 16) == m.get(HEAP + HEAP_SIZE, 16) == b'\xA5' * 16
    assert m.get(0x0203F7F0, 16) == b'\xDA' * 16 and m.get(0x0203FF30, 16) == b'\xDB' * 16

    # Native global index and text selection use 16-bit indices. The signed
    # bytes here hold only the six local rows, never the full inventory index.
    scroll = MENU + 0x38
    m.w16(scroll + 0x18, 446)
    m.put(scroll + 0x16, [6])
    m.put(MENU + 9, [6])
    assert m.call(0x08017BE8, scroll) == 445
    index_cases = 0
    name_table = m.r32(0x080258A0)
    for top in (0, 250, 254, 255, 256, 300, 440):
        m.w16(scroll + 0x1A, top)
        for local in range(6):
            index = m.call(0x08017B68, scroll, local)
            assert index == min(top + local, 445)
            expected_name = m.r32(name_table + ORDER[index] * 4)
            assert m.call(0x08025758, MENU, index) == expected_name
            m.w16(CONTEXT, index + 1)
            assert m.call(0x080287C4, MENU) == int(expected_flags[index] == 0)
            # Execute the native Throw/Draw selection store through its sound
            # boundary: the chosen item ID must survive both indices >255 and
            # item IDs >255. The surrounding UI dispatch is not simulated.
            for reg, value in [(UC_ARM_REG_R1, action), (UC_ARM_REG_R3, CONTEXT),
                               (UC_ARM_REG_R4, MENU), (UC_ARM_REG_R5, action),
                               (UC_ARM_REG_R6, index)]: m.u.reg_write(reg, value)
            m.u.emu_start(0x08028A9D, 0x08028AD0, count=100)
            assert m.u.reg_read(UC_ARM_REG_PC) == 0x08028AD0
            assert m.r16(CONTEXT + 0x10) == ORDER[index]
            index_cases += 1
        assert m.call(0x08017A90, scroll, 0x80) == int(top + 6 < 446)
        assert m.call(0x08017A90, scroll, 0x40) == int(top > 0)
    navigation = []
    # Execute native page movement through its persistent-position stores,
    # stopping immediately before sound/render, which are outside this test.
    for top, direction, expected_top in [(254, 0x80, 260), (260, 0x40, 254),
                                          (439, 0x80, 440), (440, 0x80, 440)]:
        m.w16(scroll + 0x1A, top)
        m.put(MENU + 0x69, [0])
        m.call(0x080284A0, MENU, direction, stop=0x0802853C)
        assert m.r16(CONTEXT + 0x444) == expected_top
        expected_local = 5 if top == 440 else 0
        assert m.r16(CONTEXT + 0x446) == expected_local
        navigation.append({'from': top, 'direction': direction, 'to': expected_top, 'local': expected_local})
    m.call(0x0802800C, MENU)
    assert m.get(HEAP, 20) == m.initial_heap_header, 'Native free did not coalesce heap'
    return {'action': action, 'count': 446, 'allocations': allocations, 'expandedWeaponLegality': legality,
            'indexCases': index_cases, 'navigation': navigation, 'heapFreed': True}


if __name__ == '__main__':
    iwram = native_iwram()
    # Temporary candidate mode lets review run before the parent rebuilds the
    # probe. Normal acceptance requires both installed descriptor patches.
    candidate = '--candidate' in sys.argv
    if not candidate:
        for offset in (0x3914F8, 0x39150C):
            assert struct.unpack_from('<H', ROM, offset)[0] == 446, f'Capacity patch missing: {offset:x}'
    result = {'passed': True, 'candidate': candidate, 'romSha1': hashlib.sha1(ROM).hexdigest(),
              'positive': [stress(iwram, action, 446 if candidate else None) for action in (13, 14)],
              'negative': [stress(iwram, action, 252, True) for action in (13, 14)],
              'scope': 'Real native alloc/init/free, Throw/Draw builders, compatibility checks, scroll index, text selection, usability lookup, selected-item store, page-position stores; all460 counts owned and446 synthetic swords.',
              'limitations': ['Synthetic item definitions are capacity fixtures, not expansion content validation.',
                              'No rendered battle, action execution, or in-game live heap occupancy tested.',
                              'Page navigation and selected-item store stop before sound and rendering.',
                              'Expanded weapon legality is recorded diagnostically; test-equipment-legality.py owns that acceptance contract.']}
    (OUT / 'battle-inventory.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
