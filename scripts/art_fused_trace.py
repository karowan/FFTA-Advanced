"""Capture same-call palette demands before their native consumer executes.

Dynamic reads are bounded to mapped emulated memory. No emulated state changes;
the base observer still executes the original instruction exactly once.
"""
import ctypes as C
from mgba_instruction_trace import InstructionTrace


class FusedTrace(InstructionTrace):
    def __init__(self, emulator, sites, snapshots, meta):
        self.fused_site = meta['symbols']['ffta_art_palette_live_apply_fused'] & ~1
        super().__init__(emulator, sites, snapshots)

    def read(self, address, size):
        ranges = [(pointer + address - start, size)
                  for start, (pointer, length) in self.emulator.maps.items()
                  if start <= address and address + size <= start + length]
        assert len(ranges) == 1, 'Unambiguous bounded dynamic memory read'
        return C.string_at(*ranges[0]).hex()

    def _instruction(self, cpu, opcode):
        captured = None
        index = len(self.events)
        try:
            if self.registers[15] - 4 == self.fused_site:
                captured = dict(demands=self.read(self.registers[3], 140),
                                extent=self.read(self.registers[13], 4),
                                frame=self.read(self.registers[0], 32))
        except BaseException as error:
            self.error = repr(error)
        super()._instruction(cpu, opcode)
        if captured is not None:
            try:
                assert len(self.events) == index + 1
                assert self.events[index]['pc'] == self.fused_site
                self.events[index]['memory'].update(captured)
            except BaseException as error:
                self.error = repr(error)
