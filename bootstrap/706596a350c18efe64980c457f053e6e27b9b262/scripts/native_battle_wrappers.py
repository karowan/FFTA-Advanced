"""Resolve battle objects with the game's allocator-aware enumerator on a clone.

Returns EWRAM-relative unit -> wrapper offsets. No live emulator state changes.
"""
import ctypes
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC


def from_memory(rom, ram, iwram):
    machine = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0, 0x4000), (0x02000000, 0x40000),
                          (0x03000000, 0x8000), (0x08000000, 0x2000000)):
        machine.mem_map(address, size)
    for address, data in ((0x02000000, ram), (0x03000000, iwram), (0x08000000, rom)):
        machine.mem_write(address, bytes(data))
    word = lambda address: struct.unpack('<I', machine.mem_read(address, 4))[0]
    for register, value in ((UC_ARM_REG_R0, word(0x0200f4b0)),
                            (UC_ARM_REG_R1, 0x02008000), (UC_ARM_REG_SP, 0x03007000),
                            (UC_ARM_REG_LR, 0x08000101)):
        machine.reg_write(register, value)
    machine.emu_start(0x08099cdd, 0x08000100, count=50000)
    assert machine.reg_read(UC_ARM_REG_PC) == 0x08000100, 'Enumerator did not return'
    count = machine.reg_read(UC_ARM_REG_R0)
    assert 1 <= count <= 36, ('Battle actor count', count)
    result = {}
    for index in range(count):
        wrapper = word(0x02008000 + 4 * index)
        assert 0x02000000 <= wrapper < 0x0203f770, ('Wrapper bounds', wrapper)
        unit = word(wrapper)
        assert 0x02000000 <= unit < 0x0203f6f8, ('Unit bounds', unit)
        assert unit - 0x02000000 not in result, ('Duplicate unit', unit)
        result[unit - 0x02000000] = wrapper - 0x02000000
    return result


def from_emulator(rom, emulator):
    return from_memory(rom, emulator.memory(), ctypes.string_at(*emulator.maps[0x03000000]))


def fixed_giza_formation(rom, emulator):
    """Fix scenario starting positions before inputs, never an action result.

    Native encounter placement depends on RNG consumed during title/travel.
    These coordinates/elevations are the declared original Giza replay layout.
    Other unit data and all subsequent movement use the actual game engine.
    """
    positions = ((0x32dc, 10, 5, 48, 0), (0x33e4, 5, 14, 32, 1),
                 (0x2fc4, 8, 11, 32, 1), (0x34ec, 8, 2, 80, 0),
                 (0x30cc, 7, 11, 32, 1), (0x31d4, 5, 8, 48, 0),
                 (0x188, 2, 14, 16, 3), (0x80, 2, 13, 32, 3),
                 (0x4a0, 1, 15, 16, 3), (0x398, 1, 14, 16, 3),
                 (0x290, 1, 13, 32, 3), (0x5a8, 0, 14, 16, 3))
    wrappers = from_emulator(rom, emulator)
    assert set(wrappers) == {p[0] for p in positions}, 'Unexpected encounter roster'
    for unit, x, y, height, facing in positions:
        wrapper = wrappers[unit]
        emulator.set_memory(unit + 0xf6, bytes((x, y)))
        emulator.set_memory(wrapper + 8, struct.pack('<3H', x * 32 + 16, height, y * 32 + 16))
        emulator.set_memory(wrapper + 0x1f, bytes((facing,)))
