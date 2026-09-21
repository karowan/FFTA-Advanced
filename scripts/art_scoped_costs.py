"""Read-only scoped ARM copy/execution costs on the pinned mGBA core.

Only unconditional ROM boundaries are observed. Conditional ARM instructions
that fail their condition never reach the dispatch table and are not counted.
"""
import ctypes as C
import struct
from art_fused_trace import FusedTrace
from mgba_instruction_trace import INSTRUCTION
from native_art import sha


def boundaries(meta, rom):
    assert meta.get('fusedCompose') and not meta['scopedFrame'].get('compactLeaves')
    sites = {}; proofs = []; executions = {}
    fixed = {
        0x00:0xe92d41f0, 0x04:0xe1a04000, 0x08:0xe1a05001, 0x0c:0xe1a06002,
        0x10:0xe59f806c, 0x14:0xe15d0008, 0x18:0x3a000013,
        0x1c:0xe59f8064, 0x20:0xe15d0008, 0x24:0x8a000010,
        0x2c:0xe04dd007, 0x30:0xe1a0000d, 0x34:0xe59f1050,
        0x3c:0xe8b15108, 0x40:0xe8a05108, 0x44:0xe2522001, 0x48:0x1afffffb,
        0x4c:0xe1a0800d, 0x50:0xe1a00004, 0x54:0xe1a01005, 0x58:0xe1a02006,
        0x5c:0xe28fe000, 0x60:0xe12fff18, 0x64:0xe08dd007, 0x68:0xea000003,
        0x6c:0xe1a00004, 0x70:0xe1a01005, 0x74:0xe1a02006,
        0x78:0xeb000004, 0x7c:0xe8bd41f0, 0x80:0xe12fff1e, 0x88:0x03008000,
    }
    for leaf in meta['scopedFrame']['leaves']:
        name = leaf['name'].removesuffix('_leaf'); pc = meta['symbols'][name]
        address = meta['symbols'][leaf['name']]; size = leaf['bytes']
        assert address == pc + 0x90 and not pc & 3
        raw = rom[pc-0x08000000:address-0x08000000]
        assert len(raw) == 0x90
        for offset, word in fixed.items():
            assert struct.unpack_from('<I', raw, offset)[0] == word, (name, hex(offset))
        size_word = struct.unpack_from('<I', raw, 0x28)[0]
        assert size_word & 0xfffff000 == 0xe3a07000
        shift = ((size_word >> 8) & 15) * 2; immediate = size_word & 255
        assert ((immediate >> shift) | (immediate << (32-shift))) & 0xffffffff == size
        assert struct.unpack_from('<I', raw, 0x38)[0] == 0xe3a02000 | (size//16)
        assert struct.unpack_from('<I', raw, 0x84)[0] == leaf['minimumWrapperSP']
        assert struct.unpack_from('<I', raw, 0x8c)[0] == address
        blob = rom[address-0x08000000:address-0x08000000+size]
        assert sha(blob) == leaf['sha256']
        for phase, start, end in (('copy',0x28,0x4c), ('execute',0x60,0x64), ('fallback',0x78,0x7c)):
            key = name+'/'+phase+'@'+hex(pc+start)
            assert pc+start not in sites and pc+end not in sites
            sites[pc+start] = 'cost:'+key+':call'; sites[pc+end] = 'cost:'+key+':return'
        executions[pc+0x60] = dict(blob=blob, minimum=leaf['minimumWrapperSP'], returnPC=pc+0x64)
        proofs.append(dict(name=name, address=pc, bytes=size, wrapperSha256=sha(raw), leaf=leaf))
    return sites, proofs, executions


class ScopedTrace(FusedTrace):
    def __init__(self, emulator, sites, snapshots, meta, arm_sites, executions):
        super().__init__(emulator, sites, snapshots, meta)
        self.arm_sites = arm_sites; self.executions = executions
        base = emulator.core._handle
        # Authenticated ARMRunLoop table reference, index calculation and call.
        assert C.string_at(base+0x35cc0,7).hex() == '488b1da9172700'
        assert C.string_at(base+0x35ce0,26).hex() == '89d089d1c1e810c1e90483e10f25f00f000009c84c89e1ff14c3'
        self.arm_slot = C.c_void_p.from_address(base+0x2a7470)
        self.arm_original = self.arm_slot.value
        assert base+0x1000 <= self.arm_original < base+0x2b0000
        self.arm_entries = tuple((C.c_void_p*4096).from_address(self.arm_original))
        assert all(base+0x1000 <= p < base+0x280000 for p in self.arm_entries)
        self.arm_table = (C.c_void_p*4096)(*self.arm_entries)
        self.arm_callback = INSTRUCTION(self._arm_instruction); self.arm_handlers = {}
        pointer, length = emulator.maps[0x08000000]
        for pc in arm_sites:
            assert 0x08000000 <= pc <= 0x08000000+length-4 and not pc & 3
            opcode = C.c_uint32.from_address(pointer+pc-0x08000000).value
            assert opcode >> 28 == 14, 'Only unconditional ARM boundaries'
            index = ((opcode >> 16) & 0xff0) | ((opcode >> 4) & 15)
            self.arm_handlers[index] = INSTRUCTION(self.arm_entries[index])
            self.arm_table[index] = C.cast(self.arm_callback,C.c_void_p).value
        self.host_rvas.update(armTableReference=0x2a7470, armTable=self.arm_original-base,
                              observedArmOpcodeGroups=sorted(self.arm_handlers))

    def _arm_instruction(self, cpu, opcode):
        try:
            assert cpu == self.cpu and not self.registers[16] & 32
            pc = self.registers[15] - 8
            if pc in self.arm_sites:
                event = dict(site=self.arm_sites[pc], pc=pc, cycle=self.cycles(),
                    videoFrame=self.frame_counter(self.core), scanline=self.io[3],
                    registers=list(self.registers[:17]), instructionSet='arm')
                if pc in self.executions:
                    proof = self.executions[pc]; sp = self.registers[13]; size = len(proof['blob'])
                    assert proof['minimum'] <= sp+size <= 0x03008000
                    assert self.registers[8] == sp and self.registers[7] == size
                    assert self.registers[14] == proof['returnPC']
                    assert bytes.fromhex(self.read(sp,size)) == proof['blob'], 'Exact copied ARM leaf at actual branch target'
                    event['copiedLeafSha256'] = sha(proof['blob'])
                self.events.append(event)
        except BaseException as error:
            self.error = repr(error)
        self.arm_handlers[((opcode >> 16) & 0xff0) | ((opcode >> 4) & 15)](cpu,opcode)

    def _set_arm_table(self, pointer):
        old=C.c_uint32(); ignored=C.c_uint32(); address=C.addressof(self.arm_slot)
        assert self.protect(address,8,4,C.byref(old))
        try:self.arm_slot.value=pointer
        finally:assert self.protect(address,8,old.value,C.byref(ignored))

    def __enter__(self):
        assert self.arm_slot.value == self.arm_original
        super().__enter__()
        try:self._set_arm_table(C.addressof(self.arm_table))
        except BaseException:
            self._set_arm_table(self.arm_original)
            super().__exit__(None,None,None)
            raise
        return self

    def __exit__(self,*exc):
        try:
            self._set_arm_table(self.arm_original)
            assert tuple((C.c_void_p*4096).from_address(self.arm_original)) == self.arm_entries
        finally:super().__exit__(*exc)
