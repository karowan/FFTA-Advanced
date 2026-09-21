"""Host-only instruction observation for the pinned private mGBA test core.

This deliberately fails closed on another DLL. Selected Thumb dispatch entries
are observed through a private host-side table; the native run/event loop stays
unchanged. ROM, emulated memory and CPU state are never patched.
See notes/native-art-instruction-trace.md for provenance.
"""
import ctypes as C
import hashlib
from pathlib import Path

DLL_SHA256='b7008c1a834fef42c9c2b66594855f63924d419fb33af2863e86b1a032d03560'
VOID=C.CFUNCTYPE(None,C.c_void_p)
U32=C.CFUNCTYPE(C.c_uint32,C.c_void_p)
INSTRUCTION=C.CFUNCTYPE(None,C.c_void_p,C.c_uint32)


class InstructionTrace:
    def __init__(self,emulator,sites,snapshots=None):
        self.emulator=emulator;self.sites=sites;self.events=[];self.frames=[];self.error=None
        self.snapshots={}
        for pc,ranges in (snapshots or {}).items():
            assert pc in sites
            self.snapshots[pc]={}
            for name,(address,size) in ranges.items():
                assert 0<size<=4096
                matches=[(pointer+address-start,size) for start,(pointer,length) in emulator.maps.items()
                         if start<=address and address+size<=start+length]
                assert len(matches)==1,'Unambiguous bounded observed memory range'
                self.snapshots[pc][name]=matches[0]
        path=Path(__file__).resolve().parents[1]/'tools/mgba-test-core/mgba_libretro.dll'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==DLL_SHA256,'Unrecognized test-core ABI'
        base=emulator.core._handle
        # Authenticated x64 retro_run: load core, call core->runFrame at +500.
        assert C.cast(emulator.core.retro_run,C.c_void_p).value-base==0xbf600
        assert C.string_at(base+0xbf812,16).hex()=='488b05179020004889c1ff9000050000'
        self.core=C.c_void_p.from_address(base+0x2c8830).value
        assert self.core and self.core%8==0
        self.cpu=C.c_void_p.from_address(self.core).value
        self.timing=C.c_void_p.from_address(self.core+16).value
        assert self.cpu and self.timing
        self.registers=(C.c_uint32*21).from_address(self.cpu)
        assert C.c_void_p.from_address(self.timing+32).value==self.cpu+72
        assert C.c_void_p.from_address(self.timing+40).value==self.cpu+76
        self.master=C.c_uint32.from_address(self.timing+24)
        self.relative=C.c_int32.from_address(self.cpu+72)
        self.next_event=C.c_int32.from_address(self.cpu+76)
        run_frame=C.c_void_p.from_address(self.core+0x500).value
        def function(offset,signature):
            pointer=C.c_void_p.from_address(self.core+offset).value
            assert base+0x1000<=pointer<base+0x280000,'Function outside pinned DLL image'
            return signature(pointer)
        self.frame_counter=function(0x560,U32)
        self.frame_cycles=function(0x568,U32)
        assert self.frame_cycles(self.core)==280896
        size=function(0x518,C.CFUNCTYPE(C.c_size_t,C.c_void_p))(self.core)
        assert 0x60000<=size<=0x70000
        self.state_buffer=C.create_string_buffer(size)
        self.save_state=function(0x528,C.CFUNCTYPE(C.c_bool,C.c_void_p,C.c_void_p))
        self.iw=(C.c_uint8*0x8000).from_address(emulator.maps[0x03000000][0])
        self.io=(C.c_uint16*0x200).from_address(emulator.maps[0x04000000][0])
        # Pinned ARMRunLoop loads MinGW's _thumbTable reference at 2a7530,
        # then dispatches opcode>>6. Clone the host table; preserve every entry
        # except the opcode groups containing requested, verified Thumb sites.
        assert C.string_at(base+0x35da5,7).hex()=='488b1d84172700'
        assert C.string_at(base+0x35df0,3).hex()=='c1e806'
        assert C.string_at(base+0x35dfd,3).hex()=='ff14c3'
        self.slot=C.c_void_p.from_address(base+0x2a7530)
        self.original=self.slot.value
        assert base+0x1000<=self.original<base+0x2b0000
        self.original_entries=tuple((C.c_void_p*1024).from_address(self.original))
        assert all(base+0x1000<=p<base+0x280000 for p in self.original_entries)
        self.table=(C.c_void_p*1024)(*self.original_entries)
        self.callback=INSTRUCTION(self._instruction)
        self.handlers={}
        rom_address,rom_size=emulator.maps[0x08000000]
        for pc in sites:
            assert 0x08000000<=pc<0x08000000+rom_size and not pc&1
            opcode=C.c_uint16.from_address(rom_address+pc-0x08000000).value
            index=opcode>>6
            self.handlers[index]=INSTRUCTION(self.original_entries[index])
            self.table[index]=C.cast(self.callback,C.c_void_p).value
        self.protect=C.windll.kernel32.VirtualProtect
        self.protect.argtypes=[C.c_void_p,C.c_size_t,C.c_uint32,C.POINTER(C.c_uint32)]
        self.protect.restype=C.c_int
        self.host_rvas=dict(runFrame=run_frame-base,tableReference=0x2a7530,
                            thumbTable=self.original-base,observedOpcodeGroups=sorted(self.handlers))

    def cycles(self):
        return (self.master.value+self.relative.value)&0xffffffff

    def state(self):
        assert self.save_state(self.core,self.state_buffer)
        return self.state_buffer.raw

    def _instruction(self,cpu,opcode):
        try:
            assert cpu==self.cpu and self.registers[16]&32
            # ThumbStep has already advanced PC and its prefetch before calling
            # the handler. Observation precedes the actual instruction effects.
            pc=self.registers[15]-4
            if pc in self.sites:
                event=dict(site=self.sites[pc],pc=pc,cycle=self.cycles(),
                    videoFrame=self.frame_counter(self.core),scanline=self.io[3],
                    registers=list(self.registers[:17]),
                    frameFlag=self.iw[0xe10]|self.iw[0xe11]<<8,
                    nativeFrame=self.iw[0xeb4]|self.iw[0xeb5]<<8,
                    inputs=bytes(self.iw[:24]).hex())
                if pc in self.snapshots:
                    event['memory']={name:C.string_at(pointer,size).hex()
                                     for name,(pointer,size) in self.snapshots[pc].items()}
                self.events.append(event)
        except BaseException as error:
            self.error=repr(error)
        # Always execute the exact original instruction, even after an observer
        # assertion. The enclosing context reports the error after restoring.
        self.handlers[opcode>>6](cpu,opcode)

    def _set_table(self,pointer):
        old=C.c_uint32();ignored=C.c_uint32()
        address=C.addressof(self.slot)
        assert self.protect(address,8,4,C.byref(old)),'Host table reference protection'
        try:self.slot.value=pointer
        finally:assert self.protect(address,8,old.value,C.byref(ignored)),'Host page protection restored'

    def __enter__(self):
        assert self.slot.value==self.original
        self._set_table(C.addressof(self.table))
        return self

    def __exit__(self,*exc):
        self._set_table(self.original)
        assert tuple((C.c_void_p*1024).from_address(self.original))==self.original_entries
        if self.error and not exc[0]:raise AssertionError(self.error)
