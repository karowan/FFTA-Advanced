"""New projectile LOS policy vs independent Fraction edge-intersection oracle.

Compiles only projectile-los.c into a disposable image; --current instead tests
that symbol in the current compiled engine. Uses actual native map readers.
"""
import ast,ctypes as C,hashlib,importlib.util,json,pathlib,random,struct,subprocess,sys
from fractions import Fraction
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
s=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in s.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')],type_ignores=[]),'<native harness>','exec'))
out=ROOT/'build/expansion/probes/projectile-los-council';out.mkdir(parents=True,exist_ok=True)
source=ROOT/'src/engine/projectile-los.c';source_hash=hashlib.sha1(source.read_bytes()).hexdigest()
rom=bytearray((ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes());rom.extend(bytes(0x2000000-len(rom)))
if '--current' in sys.argv:
    binary=(ROOT/'build/expansion/engine.bin').read_bytes();symbol_text=(ROOT/'build/expansion/engine.symbols').read_text();load=0x09100000
else:
    prefix=ROOT/'tools/arm-gnu/bin/arm-none-eabi-';elf=out/'los.elf';raw=out/'los.bin'
    subprocess.run([str(prefix)+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-mthumb-interwork','-Os','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x091f0000','-Wl,-e,ffta_projectile_los',str(source),'-o',str(elf)],check=True,capture_output=True)
    subprocess.run([str(prefix)+'objcopy.exe','-O','binary',str(elf),str(raw)],check=True,capture_output=True)
    symbol_text=subprocess.check_output([str(prefix)+'nm.exe','-n',str(elf)],text=True);binary=raw.read_bytes();load=0x091f0000
symbols={l.split()[2]:int(l.split()[0],16) for l in symbol_text.splitlines() if len(l.split())==3};HELPER=symbols['ffta_projectile_los']
rom[load-0x08000000:load-0x08000000+len(binary)]=binary;m=ARM(bytes(rom),iwram_from_boot());GRID=0x02026000
counts={};reads=[]
def check(group,actual,expected):
    assert actual==expected,(group,actual,expected)
    counts[group]=counts.get(group,0)+1

def observe(u,address,size,data):
    x=u.reg_read(UC_ARM_REG_R0);y=u.reg_read(UC_ARM_REG_R1)
    assert 0<=x<16 and 0<=y<16,('unsafe native coords',hex(address),x,y)
    reads.append((address,x,y))
for pc in (0x0801cc18,0x0801cc7c):m.u.hook_add(UC_HOOK_CODE,observe,begin=pc,end=pc)
def no_rng(u,address,size,data):raise AssertionError('LOS consumed RNG')
m.u.hook_add(UC_HOOK_CODE,no_rng,begin=0x08002804,end=0x08002804)
def readonly(u,access,address,size,value,data):
    assert 0x03005000<=address and address+size<=STACK+4,('LOS writes outside stack',hex(address),size)
m.u.hook_add(UC_HOOK_MEM_WRITE,readonly)

def oracle(a,b,heights,bounds):
    def valid(p):return 0<=p[0]<16 and 0<=p[1]<16 and bounds[0]<=p[0]<bounds[0]+bounds[2] and bounds[1]<=p[1]<bounds[1]+bounds[3] and heights[p[1]*16+p[0]]!=0
    if not valid(a) or not valid(b):return 0
    p=(Fraction(a[0])+Fraction(1,2),Fraction(a[1])+Fraction(1,2));d=(b[0]-a[0],b[1]-a[1]);z0=heights[a[1]*16+a[0]]+1;dz=heights[b[1]*16+b[0]]+1-z0
    # Oracle intersects the line with each square's four edges. It does not
    # use the implementation's interval clipping or rational comparison code.
    for y in range(min(a[1],b[1]),max(a[1],b[1])+1):
      for x in range(min(a[0],b[0]),max(a[0],b[0])+1):
        if (x,y) in (a,b):continue
        intersections=[]
        for axis,lo in ((0,x),(1,y)):
          if not d[axis]:continue
          for edge in (lo,lo+1):
            t=(edge-p[axis])/d[axis];other=p[1-axis]+t*d[1-axis];other_lo=(y,x)[axis]
            if 0<=t<=1 and other_lo<=other<=other_lo+1:intersections.append(t)
        if not intersections:continue
        if not valid((x,y)):return 0
        low_z=min(z0+dz*min(intersections),z0+dz*max(intersections))
        if heights[y*16+x]>=low_z:return 0
    return 1

cases=0
def case(a,b,heights=None,flags=0,bounds=(0,0,16,16),expected=None,residues=(0,4)):
    global reads,cases
    if heights is None:heights=[16]*256
    grid=bytearray(512)
    for i,h in enumerate(heights):grid[i*2:i*2+2]=bytes((h,flags))
    header=bytearray(16);struct.pack_into('<I',header,4,GRID);header[8]=16;header[10],header[12],header[13],header[15]=bounds
    m.put(GRID,grid);m.put(0x02007f10,header)
    want=oracle(a,b,heights,bounds)
    if expected is not None:check('independent_named_expectation',want,expected)
    for residue in residues:
      stack=STACK+residue;m.put(stack-0x1000,b'\xa5'*16);m.put(stack,b'\xa5'*32);reads=[]
      actual=m.call(HELPER,*(n&0xffffffff for n in (*a,*b)),stack=stack)
      check('native_vs_fraction_oracle',actual,want)
      check('caller_stack',m.read(stack,32),b'\xa5'*32);check('low_guard',m.read(stack-0x1000,16),b'\xa5'*16)
      check('map_immutable',m.read(GRID,512),bytes(grid));check('header_immutable',m.read(0x02007f10,16),bytes(header))
      if any(n<0 or n>15 for n in (*a,*b)):check('invalid_coords_no_read',reads,[])
    cases+=1
    return want

# Exhaustive in-bounds origins with short cardinal/diagonal/fractional slopes.
for y in range(16):
 for x in range(16):
  for dx,dy in ((0,0),(1,0),(0,1),(1,1),(2,1),(-1,2)):
   b=(x+dx,y+dy)
   if 0<=b[0]<16 and 0<=b[1]<16:case((x,y),b,expected=1)
# Each potential touched cell independently blocks at contact-height, or is an
# invalid zero-height hole. Include corner-only cells, off-ray nonblockers,
# extreme heights, endpoint clearance, and forward/reverse symmetry.
for a,b in (((4,4),(8,4)),((4,4),(6,6)),((4,4),(7,5)),((4,4),(5,7)),((0,0),(15,15)),((1,14),(14,1))):
 for start,end in ((16,16),(16,19),(19,16),(1,255),(255,1),(255,255)):
  for x,y in ((5,4),(4,5),(5,5),(6,5),(6,6),(7,4),(7,7),(2,13)):
   if (x,y) in (a,b):continue
   for top in (0,1,16,17,18,19,20,255):
    h=[1]*256;h[a[1]*16+a[0]]=start;h[b[1]*16+b[0]]=end;h[y*16+x]=top
    first=case(a,b,h);second=case(b,a,h);check('reverse_symmetry',first,second)
# Exact named corner: both side-touch squares matter, not only diagonal cells.
for blocker in ((5,4),(4,5),(5,5)):
 h=[16]*256;h[blocker[1]*16+blocker[0]]=17;case((4,4),(6,6),h,expected=0)
# Entry/exit minimum catches a slope before the midpoint rises over the tile.
h=[1]*256;h[4*16+4]=10;h[4*16+8]=18;h[4*16+5]=13
case((4,4),(8,4),h,expected=0);case((8,4),(4,4),h,expected=0)
# Validity honors native map offsets/dimensions; flags/occupants are not LOS.
for flags in (0,1,2,8,9,255):case((4,4),(8,4),flags=flags,expected=1)
for a,b,want in (((2,2),(8,8),1),((1,2),(8,8),0),((2,2),(14,8),0)):
 case(a,b,bounds=(2,2,12,10),expected=want)
for a,b in (((-1,4),(4,4)),((16,4),(4,4)),((4,4),(256,4)),((0xffffffff,4),(4,4)),((4,4),(4,0x10004))):case(a,b,expected=0)
for endpoint in ((4,4),(8,4)):
 h=[16]*256;h[endpoint[1]*16+endpoint[0]]=0;case((4,4),(8,4),h,expected=0)
rng=random.Random(425)
for _ in range(250):
 a=(rng.randrange(16),rng.randrange(16));b=(rng.randrange(16),rng.randrange(16));h=[rng.choice((0,1,8,16,17,20,32,255)) for _ in range(256)]
 forward=case(a,b,h);reverse=case(b,a,h);check('random_symmetry',forward,reverse)
report={'passed':True,'sourceSha1':source_hash,'binarySha1':hashlib.sha1(binary).hexdigest(),'mode':'current engine' if '--current' in sys.argv else 'isolated compile','cases':cases,'checks':sum(counts.values()),'groups':counts,'scope':'Pure new-policy LOS against independent Fraction edge oracle, actual native map readers, both stack residues, mutation/RNG/coordinate guards; no rendered/installed action claim'}
(out/'results.json').write_text(json.dumps(report,indent=2)+'\n');(out.parent/'projectile-los-tests.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
