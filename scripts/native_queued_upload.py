"""One observed native queued upload completes as the next command is decoded."""
import struct
from native_art import TILES,OAM,layout


def completed(rom,a,block,previous,elapsed,channel):
    if not previous or elapsed!=1 or channel not in (0,1):return None
    old=previous['actor']
    if not old['flags']&0x120000 or not a['flags']&0x120000:return None
    if (a['resource'],a['tile'],a['allocation'])!=previous['identity']:return None
    if old['first']!=a['first'] or old['mode']!=a['mode'] or a['index']!=old['index']+1:return None
    first=old['first'];q=first-0x08000000
    count=struct.unpack_from('<I',rom,q-4)[0]
    if not 0<old['index']<a['index']<count:return None
    if old['current']!=first+20*old['index'] or a['current']!=first+20*a['index']:return None
    table=struct.unpack_from('<I',rom,0x2102c)[0]-0x08000000
    desc=struct.unpack_from('<I',rom,table+a['resource']*4)[0]-0x08000000
    desc+=(a['mode']&~3)*6+(12 if a['mode']&3 in (1,2) else 0)+4*channel
    if struct.unpack_from('<I',rom,desc)[0]+4!=first:return None
    cursor=old['index']-1
    while cursor>=0 and rom[q+20*cursor+9] in (0,2,3,4,5,6,7,8):cursor-=1
    if cursor<0 or rom[q+20*cursor+9]!=1:return None
    source,shape=struct.unpack_from('<II',rom,q+20*cursor)
    if old['tileOffset']!=source or old['oam']!=0x08000000+OAM+shape:return None
    objects,_=layout(rom,OAM+shape);size=sum(x['width']*x['height']//64 for x in objects)*32
    if size!=old['tileCount']*32 or size>a['allocation']*32:return None
    next_command=q+20*(a['index']-1)
    if rom[next_command+9]!=1:return None
    new_source,new_shape=struct.unpack_from('<II',rom,next_command)
    if a['tileOffset']!=new_source or a['oam']!=0x08000000+OAM+new_shape:return None
    expected=rom[TILES+source:TILES+source+size]+previous['block'][size:]
    if len(expected)!=a['allocation']*32 or block!=expected:return None
    return 'exact preceding queued upload completes while next native graphics command is pending'
