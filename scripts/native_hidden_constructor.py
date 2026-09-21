"""Observe a native action constructor while its retained body is hidden."""
import struct
from native_oam_evidence import native_tiles_hidden
word=lambda r,p:struct.unpack_from('<I',r,p)[0]
half=lambda r,p:struct.unpack_from('<H',r,p)[0]

def observe(rom,ram,iw,vram,oam,body,anchor,clock,check):
    if not anchor or not anchor['direct'] or not 0<clock-anchor['frame']<=4:return None
    old=anchor['actor'];flags,resource,mode,timer,index,count=struct.unpack_from('<I2x5H',ram,body)
    native_flags=0x65 if mode&3 in (2,3) else 0x45
    if flags!=native_flags or timer or index or word(ram,body+0x20)!=0xffffffff or word(ram,body+0x2c):return None
    tile,alternate,allocation=struct.unpack_from('<3H',ram,body+0x12)
    first,current=struct.unpack_from('<II',ram,body+0x34)
    if first!=current or not 0x08000004<=first<=0x08000000+len(rom)-4 or not 0<count<100:return None
    if (resource,tile,allocation)!=anchor['identity'] or half(ram,body+0x24)!=old['tileCount'] or word(ram,body+0x28)!=old['oam']:return None
    table=word(rom,0x2102c)-0x08000000;desc=word(rom,table+resource*4)-0x08000000+(mode&~3)*6+(12 if mode&3 in (1,2) else 0)
    if word(rom,desc)+4!=first or word(rom,first-0x08000004)!=count:return None
    p=0x10000+tile*32
    if vram[p:p+allocation*32]!=anchor['block']:return None
    hidden=native_tiles_hidden(rom,iw,oam,tile,allocation,check)
    return dict(old,flags=flags,mode=mode,timer=timer,index=index,first=first,current=current,
                displayedFrames=[],exactUpload=False,configured=False,displayProof='Exact native hidden constructor retains prior verified tiles',hiddenProof=hidden)
