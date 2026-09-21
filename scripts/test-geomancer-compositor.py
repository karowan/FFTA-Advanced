"""Deterministic detached ARM compositor checks, not a live display claim.

Compile the production module, compare every emitted tile pixel against a
separate canvas oracle, and exercise ring wrapping, occlusion, field overlap,
palette selection, flips, animation replacement and refusal on overflow.
No gameplay capture or full expansion rebuild is needed for this pure module.
"""
import collections,hashlib,json,pathlib,random,re,struct,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
source=ROOT/'src/engine/geomancer-compositor.c'
inputs=[source,source.with_suffix('.h'),ROOT/'src/engine/geomancer-map.h',
 ROOT/'src/engine/geomancer-animation.c',ROOT/'src/engine/geomancer-animation.h',ROOT/'src/engine/runtime.c']
digest=hashlib.sha1(b''.join(p.read_bytes() for p in inputs)).hexdigest()
OUT=ROOT/'build/expansion/probes/geomancer-compositor'/digest;OUT.mkdir(parents=True,exist_ok=True)
prefix=ROOT/'tools/arm-gnu/bin/arm-none-eabi-'
def tool(name,*args):
 return subprocess.check_output([str(prefix)+name,*map(str,args)],text=True)
elf=OUT/'compositor.elf';binary=OUT/'compositor.bin'
tool('gcc','-mcpu=arm7tdmi','-mthumb','-O2','-ffreestanding','-fno-builtin',
 '-fno-unwind-tables','-fno-asynchronous-unwind-tables','-nostdlib',
 '-Wall','-Wextra','-Werror','-Wl,-Ttext=0x09e00000',
 '-Wl,--entry=ffta_geo_compose',source,ROOT/'src/engine/geomancer-animation.c',ROOT/'src/engine/runtime.c','-lgcc','-o',elf)
tool('objcopy','-O','binary',elf,binary)
symbols={line.split()[2]:int(line.split()[0],16) for line in tool('nm','-n',elf).splitlines() if len(line.split())==3}
code=binary.read_bytes();u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
for address,size in ((0x02000000,0x40000),(0x03000000,0x8000),(0x08000000,0x2000000),(0x06000000,0x18000)):
 u.mem_map(address,size)
u.mem_write(0x09e00000,code)
SCENE,ARR,GRAPH,PROJ,BOARD,PAL,FRAME=0x02002000,0x02003000,0x02008000,0x0200e000,0x0200e800,0x0200ea00,0x02018000
header=source.with_suffix('.h').read_text(encoding='utf-8')
CACHE=int(re.search(r'#define FFTA_GEO_CACHE_TILES (\d+)u',header)[1])
HASH=int(re.search(r'#define FFTA_GEO_HASH_SIZE (\d+)u',header)[1])
FRAME_SIZE=4+4096+4+HASH*2+2*31*32+2*31*2+16+1024+256+4+16+CACHE*2+2*31*6+8
OUTPUT=FRAME+0x4000
checks=collections.Counter();samples=[];case=None
def check(label,got,want=True):
 checks[label]+=1
 if got!=want:raise AssertionError((case,label,got if not isinstance(got,bytes) else hashlib.sha1(got).hexdigest(),want if not isinstance(want,bytes) else hashlib.sha1(want).hexdigest()))
def call(name,*args):
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
 for i,r in enumerate(saved):u.reg_write(r,0x55000000+i)
 for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,0x03007000);u.reg_write(UC_ARM_REG_LR,0x08000101)
 u.emu_start(symbols[name]|1,0x08000100,count=12000000)
 check('bounded-native-return',u.reg_read(UC_ARM_REG_PC),0x08000100)
 check('native-stack-preserved',u.reg_read(UC_ARM_REG_SP),0x03007000)
 check('native-callee-registers-preserved',[u.reg_read(r) for r in saved],[0x55000000+i for i in range(8)])
 return u.reg_read(UC_ARM_REG_R0)
def graphics_bytes(g):return bytes(g[i]|g[i+1]<<4 for i in range(0,len(g),2))
def fixture(seed=1):
 rng=random.Random(seed)
 # Mixed transparent/opaque terrain and all eight palette banks.
 graphics=[bytes(64)]+[bytes(rng.randrange(16) if i%3 else rng.randrange(1,16) for _ in range(64)) for i in range(1,96)]
 arrangement=[[((x+y*7+p*11)%96)|((x%4)<<10)|(((x+y)%8)<<12) for y in range(64) for x in range(64)] for p in range(2)]
 palette=[rng.randrange(32768) for _ in range(128)]
 projection=[(0,0,0,0,0,0)]*256;board=bytearray(256)
 return graphics,arrangement,palette,projection,board
def oracle(g,a,pal,projection,board,cx,cy,retained):
 x0,y0=cx//8,cy//8;planes=[]
 light=[];dark=[]
 def intensity(c):return 3*(c&31)+6*((c>>5)&31)+((c>>10)&31)
 for bank in range(8):
  light.append(max(range(1,16),key=lambda i:intensity(pal[16*bank+i])))
  dark.append(min(range(1,16),key=lambda i:intensity(pal[16*bank+i])))
 for plane in range(2):
  pixels=bytearray(248*168)
  for py in range(168):
   wy=y0*8+py
   for px in range(248):
    wx=x0*8+px
    if not(0<=wx<512 and 0<=wy<512):continue
    word=a[plane][(wy//8)*64+wx//8]
    lx=(7-wx%8) if word&1024 else wx%8;ly=(7-wy%8) if word&2048 else wy%8
    number=word&1023
    if number<len(g):tile=g[number]
    elif number in retained:tile=retained[number]
    else:
     upper=a[0][(wy//8)*64+wx//8]&1023
     assert plane==1 and upper<len(g) and all(g[upper]),'Missing visible reference'
     tile=bytes(64)
    pixels[py*248+px]=tile[ly*8+lx]
  planes.append(pixels)
 # Independent full-canvas edge set, then clip to the viewport.
 shadows=[set(),set()];cores=[set(),set()]
 for i,kind in enumerate(board):
  if not kind:continue
  px,py,*sides=projection[i]
  for dy in range(16):
   if not(kind&2) and dy%8 in (2,3,6,7):continue
   left=14-2*dy if dy<8 else 2*(dy-8)
   right=16+2*dy if dy<8 else 30-2*(dy-8)
   for x,quarter in ((left,0 if dy<8 else 2),(right,1 if dy<8 else 3)):
    for width in (-1,0,1,2):
     if (quarter%2)*16<=x+width<(quarter%2+1)*16:shadows[sides[quarter]].add((px+x+width,py+dy))
    for width in (0,1):cores[sides[quarter]].add((px+x+width,py+dy))
 for plane in range(2):
  for wx,wy in shadows[plane]:
   sx,sy=wx-x0*8,wy-y0*8
   if not(0<=wx<512 and 0<=wy<512 and 0<=sx<248 and 0<=sy<168):continue
   bank=(a[plane][wy//8*64+wx//8]>>12)&7
   planes[plane][sy*248+sx]=light[bank] if (wx,wy) in cores[plane] else dark[bank]
 return planes
def run(data,camera=(123,259),overflow=False,animated=False,retained=None,refresh=None,expect_refresh=None,prepared=True,shift=None):
 g,a,pal,projection,board=data;cx,cy=camera
 retained=retained or {}
 u.mem_write(0x02000000,b'\x9d'*0x40000)
 u.mem_write(ARR,struct.pack('<8192H',*(a[0]+a[1])))
 u.mem_write(GRAPH,b''.join(graphics_bytes(t) for t in g))
 u.mem_write(PROJ,b''.join(struct.pack('<hh4B',*p) for p in projection))
 u.mem_write(BOARD,bytes(board));u.mem_write(PAL,struct.pack('<128H',*pal))
 u.mem_write(SCENE,struct.pack('<7I2i5I',ARR,ARR+8192,GRAPH,PAL,PROJ,BOARD,len(g),cx,cy,0,0,0,0,0))
 if animated:
  u.mem_write(0x02011000,b''.join(graphics_bytes(t) for t in g[:32]))
  u.mem_write(GRAPH,b'\x99'*(32*32))
  u.mem_write(SCENE+36,struct.pack('<2I',0x02011000,32))
 if retained:
  u.mem_write(0x02012000,struct.pack('<'+'H'*len(retained),*retained))
  u.mem_write(0x02012100,b''.join(graphics_bytes(t) for t in retained.values()))
  u.mem_write(SCENE+44,struct.pack('<3I',0x02012000,0x02012100,len(retained)))
 u.mem_write(0x06000000,b'\x57'*0x18000)
 sources=0
 if prepared:
  sources=0x09d00000;pixels=bytearray();descriptors=bytearray()
  for flip in range(4):
   for original in g:
    rows=[original[y*8:(y+1)*8] for y in range(8)]
    if flip&1:rows=[row[::-1] for row in rows]
    if flip&2:rows=rows[::-1]
    tile=graphics_bytes(b''.join(rows));h=2166136261
    for word in struct.unpack('<8I',tile):h=((h^word)*16777619)&0xffffffff
    h^=h>>16;h=h*0x7feb352d&0xffffffff;h^=h>>15;h=h*0x846ca68b&0xffffffff;h^=h>>16
    descriptors.extend(struct.pack('<IHH',0x09d10000+len(pixels),h&1023,int(all(b&15 and b>>4 for b in tile))))
    pixels.extend(tile)
  u.mem_write(sources,bytes(descriptors));u.mem_write(0x09d10000,bytes(pixels))
 u.mem_write(FRAME+4100,struct.pack('<I',OUTPUT))
 before=bytes(u.mem_read(0x02000000,0x40000));result=call('ffta_geo_compose',SCENE,FRAME,sources)
 if refresh is not None:
  check('refresh-starts-from-complete-frame',result,1)
  g[:32]=refresh
  u.mem_write(0x02011000,b''.join(graphics_bytes(t) for t in refresh))
  before=bytes(u.mem_read(0x02000000,0x40000))
  old_maps=bytes(u.mem_read(FRAME,4100));old_cache=bytes(u.mem_read(OUTPUT,CACHE*32))
  accepted=call('ffta_geo_refresh_animation',SCENE,FRAME)
  check('refresh-admission',accepted,expect_refresh)
  check('refresh-preserves-cache-map-and-readiness',bytes(u.mem_read(FRAME,4100)),old_maps)
  if not accepted:
   check('refused-refresh-does-not-partially-write-pixels',bytes(u.mem_read(OUTPUT,CACHE*32)),old_cache)
   result=call('ffta_geo_compose',SCENE,FRAME,sources)
 if shift is not None:
  check('shift-starts-from-complete-frame',result,1)
  path=shift if isinstance(shift,list) else [shift]
  for camera in path:
   cx,cy=camera;u.mem_write(SCENE+28,struct.pack('<2i',cx,cy))
   before=bytes(u.mem_read(0x02000000,0x40000))
   result=call('ffta_geo_shift',SCENE,FRAME,sources)
   check('overlapping-camera-shift-admitted',result,1)
   verify(data,camera,result,False,retained)
 after=bytes(u.mem_read(0x02000000,0x40000));off=FRAME-0x02000000
 end=OUTPUT-0x02000000
 check('only-owned-frame-and-cache-written',before[:off]+before[off+FRAME_SIZE:end]+before[end+CACHE*32:],after[:off]+after[off+FRAME_SIZE:end]+after[end+CACHE*32:])
 check('no-hardware-writes',bytes(u.mem_read(0x06000000,0x18000)),b'\x57'*0x18000)
 return verify(data,camera,result,overflow,retained)

def verify(data,camera,result,overflow,retained):
 g,a,pal,projection,board=data;cx,cy=camera
 raw=bytes(u.mem_read(FRAME,FRAME_SIZE));count,ready=struct.unpack_from('<HH',raw)
 check('published-only-on-success',ready,result)
 if overflow:
  check('capacity-failure-not-published',result,0);check('capacity-exactly-bounded',count,CACHE);return
 check('complete-frame',result,1);check('cache-capacity',1<=count<=CACHE)
 pixels=bytes(u.mem_read(OUTPUT,CACHE*32))
 check('transparent-slot-reserved',pixels[:32],bytes(32))
 maps=[struct.unpack_from('<1024H',raw,4+p*2048) for p in range(2)]
 expected=oracle(g,a,pal,projection,board,cx,cy,retained)
 decoded=[bytearray(248*168),bytearray(248*168)]
 x0,y0=cx//8,cy//8
 for y in range(21):
  for x in range(31):
   pos=((y0+y)&31)*32+((x0+x)&31)
   for p in range(2):
    word=maps[p][pos];physical=word&1023
    index=physical if physical<640 else physical-192 if 832<=physical<896 else -1
    check('graphics-avoid-native-overlay-and-map-blocks',0<=index<count)
    tx,ty=x0+x,y0+y
    bank=(a[p][ty*64+tx]&0xf000) if 0<=tx<64 and 0<=ty<64 else 0
    check('native-palette-bank-preserved',word&0xf000,bank)
    tile=pixels[index*32:(index+1)*32]
    for yy in range(8):
     for xx in range(8):decoded[p][(y*8+yy)*248+x*8+xx]=(tile[yy*4+xx//2]>>(4*(xx%2)))&15
   upper=[expected[0][(y*8+yy)*248+x*8+xx] for yy in range(8) for xx in range(8)]
   if all(upper):
    for yy in range(8):expected[1][(y*8+yy)*248+x*8:(y*8+yy)*248+x*8+8]=bytes(8)
 for p in range(2):check('exact-independent-plane-pixels',bytes(decoded[p]),bytes(expected[p]))
 used={((y0+y)&31)*32+((x0+x)&31) for y in range(21) for x in range(31)}
 check('unused-ring-cells-cleared',all(maps[p][i]==0 for p in range(2) for i in range(1024) if i not in used))
 keys=list(struct.unpack_from('<'+str(CACHE)+'H',raw,FRAME_SIZE-8-2*31*6-CACHE*2))
 referenced={0}
 for p in range(2):
  for pos in used:
   physical=maps[p][pos]&1023;referenced.add(physical if physical<640 else physical-192)
 check('cache-slot-liveness-matches-ring',all((keys[i]!=0xfffd)==(i in referenced) for i in range(CACHE)))
 samples.append(dict(case=case,camera=camera,tiles=count))
 return count

for kind,camera in ((0,(123,259)),(1,(123,259)),(2,(127,255)),(3,(128,256)),(3,(-7,-9)),(3,(503,505))):
 case=f'kind{kind}-camera{camera}';data=fixture();g,a,pal,projection,board=data
 for i in range(16):
  projection[i]=(112+32*(i%4),248+24*(i//4),*((i>>q)&1 for q in range(4)))
  board[i]=kind
 # Identical geometry with different field types must remain an idempotent union.
 projection[16]=projection[0];board[16]=2 if kind==3 else kind
 run(data,camera,prepared=False)
 run(data,camera,prepared=True)
for camera,shift in (((123,259),(131,259)),((123,259),(115,267)),((127,255),(135,263)),
                     ((-7,-9),(9,7)),((503,505),(487,489)),((257,249),(241,233)),
                     ((120,256),(360,416))):
 case=f'camera-shift-{camera}-{shift}';data=fixture()
 for i in range(16):
  data[3][i]=(112+32*(i%4),248+24*(i//4),*((i>>q)&1 for q in range(4)))
  data[4][i]=(i%3)+1
 run(data,camera,shift=shift)
 run(data,camera,shift=shift,prepared=False)
case='camera-repeated-cache-retirement';data=fixture(11)
for i in range(8):
 data[3][i]=(48+32*i,120+24*(i%2),*((i>>q)&1 for q in range(4)))
 data[4][i]=(i%3)+1
path=[(x,y) for y in (80,160,240,160,80) for x in (128,208,128,48)]
run(data,(48,80),shift=path)
check('repeated-shifts-reach-slot-reuse',samples[-1]['tiles'],CACHE)
case='camera-nonoverlap-fallback';data=fixture();run(data,(120,256))
old_frame=bytes(u.mem_read(FRAME,FRAME_SIZE));old_cache=bytes(u.mem_read(OUTPUT,CACHE*32))
u.mem_write(SCENE+28,struct.pack('<2i',-256,-256))
check('nonoverlapping-shift-requests-full-rebuild',call('ffta_geo_shift',SCENE,FRAME,0),0)
check('early-shift-refusal-preserves-frame',bytes(u.mem_read(FRAME,FRAME_SIZE)),old_frame)
check('early-shift-refusal-preserves-pixels',bytes(u.mem_read(OUTPUT,CACHE*32)),old_cache)
result=call('ffta_geo_compose',SCENE,FRAME,0)
verify(data,(-256,-256),result,False,{})
case='animation-frame-replacement';run(fixture(9))
case='owned-pristine-animation-prefix';run(fixture(9),animated=True)
# Exact animation refresh: unique keys are safe only while opacity is stable.
# Equal old pixels may alias static pixels, another source key or a field edge.
for scenario in ('unique','static-alias','animated-alias','opacity-loss','opacity-gain','outlined','clipped'):
 case='animation-refresh-'+scenario;data=fixture(9);g,a,pal,projection,board=data
 if scenario=='static-alias':g[50]=g[1]
 if scenario=='animated-alias':g[2]=g[1]
 if scenario=='outlined':
  a[0][:]=[1]*4096;projection[0]=(120,256,0,0,0,0);board[0]=2
 updated=[bytes((v%15)+1 if v else 0 for v in tile) for tile in g[:32]]
 if scenario=='opacity-loss':updated[3]=bytes([0])+updated[3][1:]
 if scenario=='opacity-gain':updated[1]=bytes(v if v else 1 for v in updated[1])
 run(data,(-7,-9) if scenario=='clipped' else (123,259),animated=True,refresh=updated,
     expect_refresh=1 if scenario in ('unique','clipped') else 0,
     shift=[(9,7),(1,-1)] if scenario=='clipped' else [(131,267),(123,259)])
case='opaque-upper-hides-lower';data=fixture();data[0][:]=[bytes([7])*64]*96;run(data)
case='opaque-upper-hides-unloaded-lower';data=fixture();data[0][:]=[bytes([7])*64]*96;data[1][1][:]=[600]*4096;run(data)
case='visible-original-tail-tile';data=fixture();data[1][0][:]=[0]*4096;data[1][1][:]=[600]*4096
run(data,retained={600:bytes(range(16))*4})
for camera in ((-7,-9),(503,505)):
 case=f'clipped-field{camera}';data=fixture()
 data[3][0]=(-8,-8,0,1,0,1);data[3][1]=(504,504,1,0,1,0)
 data[4][0]=data[4][1]=3;run(data,camera)
case='successful-extra-graphics-slots';data=fixture();rng=random.Random(812)
data[0][:]=[bytes(64)]+[bytes([0])+bytes(rng.randrange(16) for _ in range(63)) for i in range(639)]
data[1][0][:]=[((y-32)*31+x-15)%639+1 for y in range(64) for x in range(64)]
data[1][1][:]=[0]*4096
for i in range(4):data[3][i]=(120+32*i,256,0,0,0,0);data[4][i]=2
check('successful-frame-exercises-reclaimed-slots',run(data,(120,256))>640)
case='capacity-refusal';rng=random.Random(654);data=fixture()
data[0][:]=[bytes(64)]+[bytes(rng.randrange(1,16) if i%2 else rng.randrange(16) for _ in range(64)) for i in range(1,640)]
for plane in range(2):
 data[1][plane][:]=[((x+y*31+plane*271)%639)+1 for y in range(64) for x in range(64)]
for i in range(256):
 data[3][i]=(112+16*(i%16),248+8*(i//16),0,1,1,0);data[4][i]=2
run(data,overflow=True)
case='invalid-scene';u.mem_write(SCENE+24,struct.pack('<I',641));check('invalid-size-rejected',call('ffta_geo_compose',SCENE,FRAME,0),0)
check('invalid-size-unpublished',bytes(u.mem_read(FRAME+2,2)),bytes(2))
case='physical-slot-map'
for index,want in ((0,0),(639,639),(640,832),(671,863),(672,0xffffffff),(703,0xffffffff),(704,0xffffffff)):
 check('physical-slot-boundaries',call('ffta_geo_cache_index',index),want)
report=dict(passed=True,sourceSha1=digest,codeSha1=hashlib.sha1(code).hexdigest(),
 sources={str(p.relative_to(ROOT)):hashlib.sha1(p.read_bytes()).hexdigest() for p in inputs},
 compiler=tool('gcc','--version').splitlines()[0],frameBytes=FRAME_SIZE,checks=dict(checks),samples=samples,
 limits=['Detached compiled production module; no live hook, heap or VRAM ownership accepted',
 'Synthetic pixel oracle is not all-map capacity, animation timing or player UI acceptance'])
(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
