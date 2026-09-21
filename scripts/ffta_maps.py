"""Read-only USA map decoding for terrain authoring; no game bytes are emitted to Git.

Format references: notes/geomancer-arts.md and the native USA map loader.
All offsets, lengths and back-references are checked before use.
"""
import hashlib, struct
from dataclasses import dataclass
from functools import lru_cache

CLEAN_SHA1='4ac05441f4de70a4ec3dd932116346c61b8783d9'
TABLE=0x569104
COUNT=162

def u16(b,p=0):return struct.unpack_from('<H',b,p)[0]
def u32(b,p=0):return struct.unpack_from('<I',b,p)[0]

def tile_center(x,y,height):
 return 256+16*(x-y),264+8*(x+y-height)

class MapError(ValueError):pass

def require(condition,message):
 if not condition:raise MapError(message)

@dataclass(frozen=True)
class Stream:
 data:bytes
 address:int
 end:int
 codec:str

def lz77(rom,address,limit=0x20000):
 require(0<=address<=len(rom)-4,'LZ77 header outside ROM')
 header=u32(rom,address);size=header>>8
 require(header&255==0x10 and 0<size<=limit,'Invalid LZ77 header')
 p=address+4;out=bytearray()
 while len(out)<size:
  require(p<len(rom),'Truncated LZ77 flags');flags=rom[p];p+=1
  for bit in range(7,-1,-1):
   if len(out)==size:break
   require(p<len(rom),'Truncated LZ77 token')
   if flags&(1<<bit):
    require(p+1<len(rom),'Truncated LZ77 reference')
    token=rom[p]*256+rom[p+1];p+=2;length=(token>>12)+3;offset=(token&4095)+1
    require(offset<=len(out),'LZ77 reference before output')
    for _ in range(min(length,size-len(out))):out.append(out[-offset])
   else:out.append(rom[p]);p+=1
 return Stream(bytes(out),address,p,'lz77')

def lzss(rom,address,limit=0x20000):
 require(0<=address<=len(rom)-4,'LZSS header outside ROM')
 size=int.from_bytes(rom[address:address+4],'big');p=address+4;out=bytearray()
 require(0<size<=limit,'Invalid LZSS size')
 def take(n):
  nonlocal p
  require(p+n<=len(rom),'Truncated LZSS token');value=rom[p:p+n];p+=n;return value
 while len(out)<size:
  t=take(1)[0];offset=0;fill=None;literal=None
  if t&128:length=((t>>3)&15)+3;offset=((t&7)<<8)+take(1)[0]+1
  elif t&64:length=(t&63)+1;literal=take(length)
  elif t&32:length=(t&31)+2;fill=0
  elif t&16:
   b,c=take(2);length=((b>>2)&48)+(t&15)+4;offset=((b&63)<<8)+c+1
  elif t in (1,2):length=take(1)[0]+3;fill=255 if t==1 else 0
  elif t==0:
   a,b,c=take(3);length=a+5;offset=(b<<8)+c+1
  else:raise MapError(f'Unknown LZSS token {t:02x}')
  require(len(out)+length<=size,'LZSS output overflow')
  if literal is not None:out.extend(literal)
  elif fill is not None:out.extend(bytes((fill,))*length)
  else:
   require(0<offset<=len(out),'LZSS reference before output')
   for _ in range(length):out.append(out[-offset])
 return Stream(bytes(out),address,p,'lzss')

class Maps:
 def __init__(self,rom):
  require(hashlib.sha1(rom).hexdigest()==CLEAN_SHA1,'Expected clean USA ROM')
  self.rom=rom
 def record(self,index):
  require(type(index) is int and 0<=index<COUNT,'Invalid map ID')
  return self.rom[TABLE+index*88:TABLE+(index+1)*88]
 def pointer(self,index,field):
  address=TABLE+struct.unpack_from('<i',self.record(index),field)[0]
  require(0<=address<len(self.rom)-4,'Map component pointer outside ROM')
  return address
 @lru_cache(maxsize=None)
 def component(self,index,field):
  require(field in (4,8,16),'Unsupported aliased map component')
  p=self.pointer(index,field);kind=self.rom[p]
  if kind==0x10:return lz77(self.rom,p)
  require(kind in (1,0x11),'Unsupported component type')
  if kind==0x11:return lz77(self.rom,p+4)
  n=min(0x10000,len(self.rom)-p-4)
  return Stream(self.rom[p+4:p+4+n],p+4,p+4+n,'packed')
 def components(self,index,field):
  # Native 1F1A8/1F2EC/1F438 recursively load the parent and THEN apply
  # this entry's packed delta. The alias is not a complete substitution.
  visited=set();chain=[];rom=self.rom
  while True:
   require(index not in visited,'Map alias cycle');visited.add(index)
   p=self.pointer(index,field);kind=rom[p]
   chain.append((kind,self.component(index,field)))
   if kind==0x10 or u32(rom,p)>>8==0xffffff:break
   index=u32(rom,p)>>8
  return tuple(reversed(chain))
 @lru_cache(maxsize=None)
 def heights(self,index):
  return self.unpack_runs(index,16,0x200)
 @lru_cache(maxsize=None)
 def clipping(self,index):
  return self.unpack_runs(index,8,0x2000)
 def unpack_runs(self,index,field,size):
  out=bytearray(size)
  for kind,stream in self.components(index,field):
   b=stream.data;p=0;seen=set()
   if kind==0x10:
    require(len(b)==len(out),'Invalid direct component length');out[:]=b;continue
   while True:
    require(p+4<=len(b),'Missing component run');offset,n=u16(b,p),u16(b,p+2);p+=4
    require(not(offset&1 or n&1) and offset+n<=len(out) and p+n<=len(b),'Invalid component run')
    for i in range(offset,offset+n):
     require(i not in seen,'Overlapping component runs');seen.add(i)
    out[offset:offset+n]=b[p:p+n];p+=n
    require(p+2<=len(b),'Missing component terminator')
    if not u16(b,p):break
  return bytes(out)
 @lru_cache(maxsize=None)
 def palette(self,index):
  r=self.record(index);kind=r[0x54]&3
  if kind in (1,2):
   base=u32(self.rom,0x1a4f8 if kind==1 else 0x1a514)-0x08000000
   p=base+u16(self.rom,base+2*r[0x56]);return lzss(self.rom,p)
  p=self.pointer(index,12)
  if self.rom[p]==0x10:return lz77(self.rom,p)
  n=((u32(self.rom,p)>>8)&0x3fffff)>>1
  require(0<n<=512 and p+4+n<=len(self.rom),'Invalid raw palette')
  return Stream(self.rom[p+4:p+4+n],p+4,p+4+n,'raw')
 @lru_cache(maxsize=None)
 def graphics(self,index):
  p=self.pointer(index,0);kind=self.rom[p]
  require(kind in (0x20,0x22),'Unsupported graphics compression')
  return lzss(self.rom,p+(8 if kind==0x22 else 4))
 def tiles(self,index,frame=0):
  raw=self.graphics(index).data;r=self.record(index);p=self.pointer(index,0)
  require(len(raw)%32==0,'Partial graphics tile')
  # Native1A6A8 places static type22 output at the header's explicit byte
  # offset. Animation count is not an additional prefix allocation.
  prefix=(u32(self.rom,p)>>8)&0xffff if self.rom[p]==0x22 else 0
  out=bytearray(prefix)+bytearray(raw)
  animation=struct.unpack_from('<i',r,0x14)[0]
  if animation<=0:return bytes(out)
  base=TABLE+animation;control,frames=u16(self.rom,base),u16(self.rom,base+2)
  require(0<frames<=1024,'Invalid animation frame count')
  require(type(frame) is int and 0<=frame<frames,'Invalid animation frame')
  length=control&0xffe0;skip=u32(r,0x1c)&0xffffff
  offset=u16(self.rom,base+6+frame*4)*32
  address=self.pointer(index,0x18)+offset
  require(length and address+length<=len(self.rom) and skip+length<=len(out),'Invalid first animation frame')
  out[skip:skip+length]=self.rom[address:address+length]
  return bytes(out)
 @lru_cache(maxsize=None)
 def arrangement(self,index):
  combined={}
  for kind,stream in self.components(index,4):
   require(kind!=0x10,'Direct planar arrangement is not implemented')
   runs,pairs=self.arrangement_delta(stream.data)
   for address,strip in runs:combined[address]=pairs[strip]
  pairs=list(combined.values());runs=[(address,i) for i,address in enumerate(combined)]
  return runs,pairs
 @staticmethod
 def arrangement_delta(b):
  dictionary=u32(b)&0xffffff;p=4;runs=[]
  require(b[3]&128,'Non-dictionary arrangement is not implemented')
  require(4<=dictionary<len(b)-3,'Invalid strip dictionary offset')
  while True:
   require(p+2<=len(b),'Missing arrangement terminator');address=u16(b,p);p+=2
   if not address:break
   require(p<len(b),'Truncated arrangement run');n=b[p];p+=1
   width=2 if b[3]&64 else 1
   require(n and p+n*width<=len(b),'Invalid arrangement run')
   for i in range(n):
    strip=u16(b,p) if width==2 else b[p];p+=width
    require(address%4==0 and address<0x4000,'Arrangement outside two layers')
    runs.append((address,strip));address+=4
  pairs=[];p=dictionary
  while True:
   require(p+4<=len(b),'Missing strip terminator')
   if not u32(b,p):break
   a=u16(b,p);pairs.append((a&0x7fff,(u16(b,p+2)&0x7fff) if a&0x8000 else a+1));p+=2
  require(all(strip<len(pairs) for _,strip in runs),'Undefined arrangement strip')
  return runs,pairs
 def planar(self,index):
  out=bytearray(0x4000);runs,pairs=self.arrangement(index)
  for address,strip in runs:struct.pack_into('<HH',out,address,*pairs[strip])
  return bytes(out)
 def render(self,index):
  from PIL import Image,ImageDraw
  tiles=self.tiles(index);pal=self.palette(index).data
  require(len(pal)%32==0,'Partial palette bank')
  colors=[((v&31)*8,((v>>5)&31)*8,((v>>10)&31)*8,0 if i%16==0 else 255) for i,v in enumerate(struct.unpack('<'+'H'*(len(pal)//2),pal))]
  @lru_cache(maxsize=None)
  def tile(word):
   number=word&4095;bank=(word>>12)&7
   require(number*32+32<=len(tiles),'Tile reference outside graphics')
   require(bank*16+15<len(colors),'Tile reference outside palette')
   pixels=[]
   for b in tiles[number*32:(number+1)*32]:pixels.extend((colors[bank*16+(b&15)],colors[bank*16+(b>>4)]))
   im=Image.new('RGBA',(8,8));im.putdata(pixels);return im
  layers=[Image.new('RGBA',(512,512)) for _ in range(2)]
  runs,pairs=self.arrangement(index)
  # Some native lower-layer references exceed the supplied graphics bank.
  # Accept them ONLY when their entire 8x8 rectangle is hidden by the already
  # rendered opaque foreground. Never substitute pixels for visible failures.
  for address,strip in sorted(runs):
   x=(address%128)*4;y=(address//128)*8;layer=y//512;y%=512
   for side,word in enumerate(pairs[strip]):
    px=x+8*side
    if layer==1 and (word&4095)*32+32>len(tiles):
     require(layers[0].getchannel('A').crop((px,y,px+8,y+8)).getextrema()==(255,255),'Visible tile reference outside graphics')
     continue
    layers[layer].paste(tile(word),(px,y))
  result=Image.alpha_composite(layers[1],layers[0]);grid=result.copy();draw=ImageDraw.Draw(grid);h=self.heights(index)
  for y in range(16):
   for x in range(16):
    height=h[2*(y*16+x)]
    if not height:continue
    cx,cy=tile_center(x,y,height)
    draw.polygon(((cx-16,cy),(cx,cy-8),(cx+16,cy),(cx,cy+8)),outline=(255,220,80,230))
    draw.text((cx-9,cy-4),f'{x},{y}',fill=(255,255,255,255),stroke_width=1,stroke_fill=(0,0,0,255))
  return result,grid,layers
