"""Read-only graphics input lifetimes for the pinned native instruction observer.

Observe Thumb word/halfword stores, and exact bytes at native OAM completion.
ARM stores, BIOS transfers and deferred DMA are not inferred from Thumb stores.
Full-core equivalence is required by the enclosing deterministic runtime test.
"""
import ctypes as C
import struct
from native_art import sha
from mgba_instruction_trace import InstructionTrace,INSTRUCTION
GRAPHICS_SITES={0x08001480:'native-oam-ready',0x08000828:'queued-dma-start',
                0x080004bc:'vblank-upload-begin',0x080004c4:'vblank-upload-end'}

class GraphicsTrace(InstructionTrace):
    def __init__(self,emulator,sites,snapshots=None):
        sites=dict(sites)
        sites.update(GRAPHICS_SITES)
        super().__init__(emulator,sites,snapshots)
        self.previous_obj=None;self.previous_oam=None;self.previous_visible=None
        self.pending_writes=[]
        self.obj_pointer=emulator.maps[0x06000000][0]+0x10000
        self.oam_pointer=emulator.maps[0x07000000][0]
        self.dirty_cache_pointer=None
        # STR immediate/register; STRH immediate/register. No emulated write
        # or handler replacement: each original handler still runs once.
        groups=set(range(0x6000>>6,0x6800>>6))|set(range(0x8000>>6,0x8800>>6))
        groups|=set(range(0x5000>>6,0x5400>>6))
        for index in groups:
            self.handlers[index]=INSTRUCTION(self.original_entries[index])
            self.table[index]=C.cast(self.callback,C.c_void_p).value

    def _ready(self):
        obj=C.string_at(self.obj_pointer,32768)
        oam=C.string_at(self.oam_pointer,1024)
        visible=[];objects=[]
        widths=(8,16,32,64,16,32,32,64,8,8,16,32)
        heights=(8,16,32,64,8,8,16,32,16,32,32,64)
        for index in range(128):
            a,b,c=struct.unpack_from('<3H',oam,index*8)
            if a&0x300==0x200 or not a&0x2000:continue
            shape=a>>14;size=b>>14
            assert shape<3
            width=widths[shape*4+size];height=heights[shape*4+size]
            start=(c&1022)*32;assert start+width*height<=32768
            x=b&511;y=a&255
            if x>=256:x-=512
            if y>=160:y-=256
            tiles=[]
            for row in range(0,height,8):
                for col in range(0,width,8):
                    px=x+(width-8-col if b&0x1000 else col)
                    py=y+(height-8-row if b&0x2000 else row)
                    if not a&0x1100 and (px>=240 or px+8<=0 or py>=160 or py+8<=0):continue
                    tile=(start+row*width+col*8)//64;tiles.append(tile)
                    visible.append((tile,obj[tile*64:tile*64+64]))
            objects.append(dict(index=index,attributes=[a,b,c],tiles=tiles))
        # Exact comparisons drive the conclusions; hashes only identify inputs.
        changed=[] if self.previous_obj is None else [i for i in range(512)
                    if obj[i*64:i*64+64]!=self.previous_obj[i*64:i*64+64]]
        row=dict(site='graphics-inputs',pc=0x08001480,videoFrame=self.frame_counter(self.core),
                 cycle=self.cycles(),frameFlag=self.iw[0xe10]|self.iw[0xe11]<<8,
                 mainBank=self.iw[0x28],uiBank=self.iw[0x2f58],
                 counts={hex(p):struct.unpack('<2I',bytes(self.iw[p:p+8])) for p in (0x20,0x2c50,0x2f60,0x3168)},
                 objSha256=sha(obj),oamSha256=sha(oam),changedObjTiles=changed,
                 previousExists=self.previous_obj is not None,
                 objUnchanged=self.previous_obj==obj,oamUnchanged=self.previous_oam==oam,
                 visible8bppUnchanged=self.previous_visible==visible,objects8bpp=objects,
                 writesSincePrevious=self.pending_writes)
        if self.dirty_cache_pointer is not None:
            cache=C.string_at(self.dirty_cache_pointer,2124)
            mode=struct.unpack_from('<I',cache,2120)[0]
            marker=cache[2112:2116]==bytes.fromhex('54443159')
            valid=int.from_bytes(cache[:64],'little') if marker and mode==0x44545931 else 0
            for tile in range(512):
                if valid&(1<<tile):
                    expected=0
                    for pixel in obj[tile*64:tile*64+64]:
                        if pixel:expected|=1<<(pixel//16)
                    actual=struct.unpack_from('<H',cache,64+tile*2)[0]
                    assert actual==expected,('stale dirty cache',tile,actual,expected,row['videoFrame'])
            row['dirtyCache']=dict(marker=marker,mode=mode,validatedTiles=valid.bit_count())
        self.events.append(row)
        self.pending_writes=[]
        self.previous_obj=obj;self.previous_oam=oam;self.previous_visible=visible

    def _instruction(self,cpu,opcode):
        try:
            assert cpu==self.cpu and self.registers[16]&32
            pc=self.registers[15]-4
            size=0
            if opcode&0xf800==0x6000:size=4;offset=((opcode>>6)&31)*4
            elif opcode&0xf800==0x8000:size=2;offset=((opcode>>6)&31)*2
            elif opcode&0xfe00 in (0x5000,0x5200):
                size=4 if opcode&0xfe00==0x5000 else 2
                offset=self.registers[(opcode>>6)&7]
            if size:
                address=(self.registers[(opcode>>3)&7]+offset)&0xffffffff
                value=self.registers[opcode&7]&((1<<(size*8))-1)
                event=None
                if 0x06010000<=address<0x06018000:
                    event=dict(kind='thumb-obj-store',address=address,bytes=size,value=value)
                elif 0x040000b0<=address<0x040000e0:
                    channel=(address-0x040000b0)//12;offset=(address-0x040000b0)%12
                    if (size==4 and offset==8 and value&0x80000000) or (size==2 and offset==10 and value&0x8000):
                        registers=bytes((C.c_uint8*12).from_address(C.addressof(self.io)+0xb0+channel*12))
                        source,destination,prior=struct.unpack('<3I',registers)
                        control=value if size==4 else (prior&65535)|(value<<16)
                        count=control&(65535 if channel==3 else 16383)
                        count=count or (65536 if channel==3 else 16384)
                        width=4 if control&0x04000000 else 2
                        mode=(control>>21)&3;timing=(control>>28)&3
                        if mode==1:lo,hi=destination-(count-1)*width,destination+width
                        elif mode==2:lo,hi=destination,destination+width
                        else:lo,hi=destination,destination+count*width
                        if lo<0x06018000 and hi>0x06010000:
                            event=dict(kind='thumb-obj-dma',source=source,destination=destination,
                                       control=control,channel=channel,timing=timing,
                                       destinationMode=mode,low=lo,high=hi)
                if event:
                    event.update(pc=pc,lr=self.registers[14],cycle=self.cycles(),videoFrame=self.frame_counter(self.core))
                    self.pending_writes.append(event)
            if pc==0x08001480:self._ready()
        except BaseException as error:self.error=repr(error)
        super()._instruction(cpu,opcode)
