"""Audit every live repeat fast path without altering native execution."""
import ctypes as C
import struct
from mgba_instruction_trace import InstructionTrace

class RepeatTrace(InstructionTrace):
    def __init__(self,emulator,sites,snapshots,meta):
        self.repeat_site=meta['symbols']['ffta_art_palette_apply_validated']&~1
        self.meta=meta
        self.ram_pointer=emulator.maps[0x02000000][0]
        self.obj_pointer=emulator.maps[0x06000000][0]+0x10000
        self.oam_pointer=emulator.maps[0x07000000][0]
        super().__init__(emulator,{**sites,self.repeat_site:'validated-repeat-apply'},snapshots)

    def _instruction(self,cpu,opcode):
        try:
            pc=self.registers[15]-4
            if pc==self.repeat_site:
                meta=self.meta;base=meta['ramReservation'][0]-0x02000000
                live=C.string_at(self.ram_pointer+base,meta['transientStateBytes'])
                key=live[meta['repeatOffset']:meta['repeatOffset']+928]
                objects=C.string_at(self.oam_pointer,1024);obj=C.string_at(self.obj_pointer,32768)
                assert struct.unpack_from('<I',key)[0]==1,'Invalid repeated-frame key used'
                tags=live[meta['tagOffset']:meta['tagOffset']+128]
                variants=live[meta['variantOffset']:meta['variantOffset']+40]
                if meta.get('repeatKeyVersion')==2:
                    iw=bytes(self.iw);bank=iw[0x28]^1;other=iw[0x2f58]^1
                    word=lambda p:struct.unpack_from('<I',iw,p)[0]
                    front,ui,main=word(0x2c50+bank*4),word(0x2f60+other*4),word(0x20+bank*4)
                    assert front<=48 and ui<=32 and main<=128
                    ui=0 if front+main>=128 else min(ui,128-main-front)
                    offset=front+ui;shown=min(main,128-offset);owners=[255]*128
                    for i in range(shown):
                        src=iw[0x30+bank*1024+i*8:0x36+bank*1024+i*8]
                        assert src==objects[(offset+i)*8:(offset+i)*8+6]
                        entry=live[4+bank*1024+i*8:12+bank*1024+i*8]
                        if entry[6]<10 and entry[:6]==src:owners[offset+i]=entry[6]
                    highlight=struct.unpack_from('<I',live,meta['nativeHighlightOffset'])[0]
                for index in range(128):
                    if meta.get('repeatKeyVersion')!=2:
                        assert key[12+index*4:16+index*4]==objects[index*8:index*8+4],('Changed repeat OAM',index)
                        assert key[524+index*2:526+index*2]==objects[index*8+4:index*8+6],('Changed repeat tile/bank',index)
                        continue
                    av,bv,cv,_=struct.unpack_from('<4H',objects,index*8);owner=owners[index]
                    if highlight and cv>>12==9:owner=255
                    if owner<10:
                        assert tags[index]<20 and variants[tags[index]]==owner*16+(cv>>12),('Fresh ownership remap',index)
                    else:assert tags[index]==255,('Unexpected cached owner',index)
                    if av&0x300==0x200:ab,kind=0,0x8000
                    elif owner<10:ab,kind=0,0x4000+owner*16+(cv>>12)
                    elif av&0x2000:ab,kind=(av&0xf3ff)|((bv&0xf1ff)<<16),cv&1022
                    else:ab,kind=0,0x2000+(cv>>12)
                    assert struct.unpack_from('<I',key,12+index*4)[0]==ab and struct.unpack_from('<H',key,524+index*2)[0]==kind,('Changed palette demand',index)
                assert key[780:820]==live[meta['variantOffset']:meta['variantOffset']+40],'Changed history mapping'
                # Compiled twenty-history plan follows the fixed profiling words.
                assert key[820:852]==live[2592:2624],'Changed repeated plan'
                count,mode,highlight=struct.unpack_from('<3I',key,916)
                assert count<=32 and mode==bool(self.iw[0x940]&64)
                assert highlight==struct.unpack_from('<I',live,meta['nativeHighlightOffset'])[0]
                expected_tiles=[];widths=(8,16,32,64,16,32,32,64,8,8,16,32);heights=(8,16,32,64,8,8,16,32,16,32,32,64)
                for index in range(128):
                    av,bv,cv,_=struct.unpack_from('<4H',objects,index*8)
                    if av&0x300==0x200 or not av&0x2000:continue
                    assert av>>14<3
                    dimensions=(av>>14)*4+(bv>>14);width,height=widths[dimensions],heights[dimensions]
                    start=(cv&1022)*32;assert start+width*height<=32768
                    x,y=bv&511,av&255
                    if x>=256:x-=512
                    if y>=160:y-=256
                    for row in range(0,height,8):
                        for col in range(0,width,8):
                            px=x+(width-8-col if bv&0x1000 else col);py=y+(height-8-row if bv&0x2000 else row)
                            if not av&0x1100 and (px>=240 or px+8<=0 or py>=160 or py+8<=0):continue
                            expected_tiles.append((start+row*width+col*8)//64)
                assert list(struct.unpack_from('<'+str(count)+'H',key,852))==expected_tiles,'Repeat footprint omits or misorders a consumed tile'
                cache=meta['visibleColorsOffset']+640
                valid=struct.unpack_from('<I',live,cache+2120)[0]
                assert valid&((1<<count)-1)==(1<<count)-1
                for index in range(count):
                    tile=struct.unpack_from('<H',key,852+index*2)[0]
                    assert tile<512 and obj[tile*64:tile*64+64]==live[cache+index*64:cache+index*64+64],('Changed repeat pixels',index,tile)
                self.events.append(dict(site='repeat-key-proof',pc=pc,videoFrame=self.frame_counter(self.core),cycle=self.cycles(),tiles=count,completeFootprint=True,freshOwners=meta.get('repeatKeyVersion')==2))
        except BaseException as error:self.error=repr(error)
        super()._instruction(cpu,opcode)
