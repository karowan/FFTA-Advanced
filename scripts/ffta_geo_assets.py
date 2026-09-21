"""Checked original terrain graphics and all native graphics-animation streams.

The four auxiliary streams at record20h are graphics writers too (19FC8 ->
20DA0), not replacement maps. They share the native four-entry animation pool.
No ROM-derived graphics are stored in source control.
"""
import struct
from dataclasses import dataclass
from ffta_maps import TABLE,require,u16,u32

@dataclass(frozen=True)
class GraphicsAnimation:
 control:int
 source:int
 destination:int
 length:int
 frames:tuple
 durations:tuple

def static_tiles(maps,index):
 p=maps.pointer(index,0);raw=maps.graphics(index).data
 prefix=(u32(maps.rom,p)>>8)&0xffff if maps.rom[p]==0x22 else 0
 result=bytes(prefix)+raw
 require(len(result)%32==0 and len(result)<=0x5000,'Invalid static terrain atlas')
 return result

def graphics_animations(maps,index):
 r=maps.record(index);rom=maps.rom;result=[]
 records=[]
 primary=struct.unpack_from('<i',r,20)[0]
 if primary>0:records.append((TABLE+primary,maps.pointer(index,24),u32(r,28)&0xffffff))
 for j in range(4):
  control=struct.unpack_from('<i',r,32+4*j)[0]
  if control:
   source=TABLE+struct.unpack_from('<i',r,48+4*j)[0]
   destination=u32(r,64+4*j)-0x06000000
   records.append((TABLE+control,source,destination))
 require(len(records)<=4,'Native animation pool overflow')
 capacity=len(static_tiles(maps,index))
 for control,source,destination in records:
  require(0<=control<len(rom)-4,'Animation control outside ROM')
  length,count=u16(rom,control),u16(rom,control+2)
  require(length>0 and length%32==0 and destination>=0 and destination%32==0 and
          destination+length<=capacity and destination+length<=4096,'Animation outside owned terrain prefix')
  require(0<count<256 and control+4+4*count<=len(rom),'Invalid native animation frame count')
  frames=[];durations=[]
  for f in range(count):
   duration=u16(rom,control+4+4*f);start=source+32*u16(rom,control+6+4*f)
   require(duration>0 and 0<=start<=len(rom)-length,'Invalid animation frame/duration')
   frames.append(rom[start:start+length]);durations.append(duration)
  require(all(destination+length<=a.destination or destination>=a.destination+a.length for a in result),
          'Overlapping independent terrain animations require ordering analysis')
  result.append(GraphicsAnimation(control,source,destination,length,tuple(frames),tuple(durations)))
 # Native map initialization separately preloads the complete primary frame.
 # Auxiliary streams fit a single native1024-byte transfer after becoming active.
 require(all(a.length<=1024 for a in result[(1 if primary>0 else 0):]),'Auxiliary initial frame needs multi-transfer initialization analysis')
 return tuple(result)

def tile_variants(maps,index):
 """Independent original-tile choices also bound partial native DMA progress.

 Native pool initialization20F34 fixes its chunk budget at1024 bytes. Lengths,
 destinations and frame offsets above are32-byte aligned, so each transferred
 tile is complete even when one atlas contains old and new animation frames.
 The primary stream is preloaded by1A8C8. Auxiliary streams are single-transfer
 and source binding refuses untouched controllers. Uninitialized prefix zeros
 are not a rendered battlefield animation frame.
 """
 raw=static_tiles(maps,index)
 result=[{raw[i:i+32]} for i in range(0,len(raw),32)]
 for a in graphics_animations(maps,index):
  for offset in range(0,a.length,32):result[(a.destination+offset)//32]=set()
  for frame in a.frames:
   for offset in range(0,a.length,32):result[(a.destination+offset)//32].add(frame[offset:offset+32])
 return tuple(tuple(sorted(v)) for v in result)
