"""Deterministic benchmark input at the native candidate-construction boundary.

The game advances its RNG once per main-loop iteration (caller 0800047b).
A video-frame sample of phase zero can fall on either side of that call when
hook costs change. Pinning only at that sample therefore changes the candidate
set, even with identical unit bytes. Apply the declared seed immediately before
080c1eb4 instead. Execute every native instruction; never patch a ROM, skip work,
freeze subsequent RNG, or exclude setup frames from the timing interval.

This is an explicitly mutating test-input controller, unlike InstructionTrace.
It changes only the four-byte RNG input, once per observed constructor call.
The caller requires exactly one call. Replays use this same controller.
"""
import ctypes as C
import struct
from mgba_instruction_trace import InstructionTrace

BOUNDARY = 'native-candidate-constructor-v2'
ENTRY = 0x080c1eb4


class PlannerSeed(InstructionTrace):
    def __init__(self, emulator, seed, sites=None, snapshots=None):
        super().__init__(emulator, {**(sites or {}), ENTRY: 'planner-seed'}, snapshots)
        self.seed = seed
        self.pins = []
        self.rng = emulator.maps[0x03000000][0] + 0x34b0

    def _instruction(self, cpu, opcode):
        try:
            if self.registers[15] - 4 == ENTRY:
                self.pins.append(dict(frame=self.frame_counter(self.core),
                                      before=C.c_uint32.from_address(self.rng).value,
                                      seed=self.seed))
                C.memmove(self.rng, struct.pack('<I', self.seed), 4)
        except BaseException as error:
            self.error = repr(error)
        # The observer must execute the native instruction even if pinning
        # fails; its context restores the host dispatch table and raises.
        super()._instruction(cpu, opcode)
