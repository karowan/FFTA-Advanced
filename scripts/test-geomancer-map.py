"""Field geometry/overlap and native quarter-plane differential, no display claim.

Native1D624 runs until its final1D130 submission, whose arguments are observed
without drawing. Production projection is compared with that independent
native result on every valid tile in all162 captured campaign map components.
No game window, player save or generated visual fixture is involved.
"""
import collections,hashlib,itertools,json,pathlib,struct
from ffta_maps import COUNT,CLEAN_SHA1,tile_center
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-geomancer-fields.py'
ns={'__file__':str(source),'__name__':'geometry_fixture'}
exec(compile(source.read_text(encoding='utf-8').split('for action,seed in itertools.product')[0],str(source),'exec'),ns)
m,meta,OUT,A,T,STACK=(ns[k] for k in ('m','meta','OUT','A','T','STACK'))
call,fresh,field,state=(ns[k] for k in ('call','fresh','field','state'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
checks=collections.Counter();case=None;output=0x0203f000

def check(label,got,want=True):
 checks[label]+=1
 if got!=want:
  compact=lambda v:('bytes',len(v),hashlib.sha1(v).hexdigest()) if isinstance(v,bytes) and len(v)>512 else v
  raise AssertionError((label,case,compact(got),compact(want)))

def board(owner=A):
 m.put(output-4,b'\x9a'*4);m.put(output+256,b'\xa9'*4)
 before=m.read(0x02000000,0x40000)
 count=call('ffta_geo_field_board',owner,output)
 got=m.read(output,256);after=m.read(0x02000000,0x40000)
 check('board-count-deduplicates',count,sum(bool(v) for v in got))
 check('board-bounded-output',after[:0x3f000]+after[0x3f100:],before[:0x3f000]+before[0x3f100:])
 return got

def expected(fields):
 grid=int.from_bytes(m.read(0x02007f14,4),'little');width=m.read(0x02007f18,1)[0]
 heights=m.read(grid,512);result=bytearray(256)
 for kind,cx,cy in fields:
  for x,y in itertools.product(range(16),repeat=2):
   h=heights[2*(width*y+x)];ch=heights[2*(width*cy+cx)]
   if h and abs(x-cx)+abs(y-cy)<=1 and abs(h-ch)<=2:result[16*y+x]|=1<<(kind-1)
 return bytes(result)

for first,second,center in itertools.product((1,2),(0,1,2),((5,14),(4,14))):
 for grounded,faction in itertools.product((True,False),(0,128)):
  case=('field-union',first,second,center,grounded,faction);fresh(380)
  field(A,first);fields=[(first,5,14)]
  if second:field(T,second,*center);fields.append((second,*center))
  m.put(T+0x29,bytes((faction,)));m.put(T+0xfc,bytes((0 if grounded else 3,)))
  check('union-independent-of-viewer-applicability',board(T),expected(fields))

for condition in ('none','KO','Petrify','expired','invalid-kind','invalid-timer','invalid-center','foreign'):
 case=('stale-field',condition);fresh(380);field(A,1)
 if condition=='KO':m.put(A+0x18,bytes(2))
 if condition=='Petrify':m.put(A+0xe8,b'\x40')
 if condition=='expired':m.put(state(A)+17,b'\x01')
 if condition=='invalid-kind':m.put(state(A)+17,b'\x1b')
 if condition=='invalid-timer':m.put(state(A)+17,b'\x1d')
 if condition=='invalid-center':m.put(state(A)+15,b'\xff\xff')
 owner=0x02030000 if condition=='foreign' else A
 check('stale-or-foreign-field-excluded',board(owner),expected([(1,5,14)]) if condition=='none' else bytes(256))

for owns in (False,True):
 case=('owned-copy',owns);fresh(380);field(T if owns else A,2)
 copy=0x03007300
 check('owned-copy-created',call('ffta_snapshotted_evaluated_init',copy,T),1)
 check('copy-never-borrows-live-fields',board(copy),expected([(2,5,14)]) if owns else bytes(256))
 call('ffta_snapshotted_evaluated_close',copy)
 check('retired-copy-has-no-fields',board(copy),bytes(256))

case='all36 canonical casters';fresh(380);fields=[]
for i in range(36):
 unit=0x02000080+i*264 if i<24 else 0x02002fc4+(i-24)*264
 m.put(unit+0x18,struct.pack('<H',500));m.put(unit+0xe8,bytes(8))
 kind=i%2+1;x=4+i%3;y=13+i%2;field(unit,kind,x,y);fields.append((kind,x,y))
check('all36-fields-deduplicate',board(),expected(fields))

# Native map captures have their own clean-ROM provenance. Reusing these
# immutable inputs does not imply any earlier expansion image is under test.
native=ROOT/'build/expansion/terrain'/CLEAN_SHA1/'native-loader'
loader=json.loads((native/'report.json').read_text(encoding='utf-8'))
assert loader['passed'] and loader['cleanRomSha1']==CLEAN_SHA1 and len(loader['maps'])==COUNT
fresh(380);base_ram=m.read(0x02000000,0x40000);project=meta['symbols']['ffta_geo_project_tile']
project_output=0x03007e00;observed=[];planes=collections.Counter();maps=[]

def observe(u,address,size,data):
 sp=u.reg_read(UC_ARM_REG_SP)
 flags=int.from_bytes(u.mem_read(sp,4),'little')
 observed.append((u.reg_read(UC_ARM_REG_R2),u.reg_read(UC_ARM_REG_R3),bytes(u.mem_read(flags,4))))
 # Observe exactly the native projection/occlusion contract without allowing
 # its final tilemap writer to replace any target highlights.
 u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))

hook=m.u.hook_add(UC_HOOK_CODE,observe,begin=0x0801d130,end=0x0801d130)
try:
 for entry in loader['maps']:
  index=entry['map'];m.put(0x02000000,base_ram)
  parts={}
  for name,address in (('height',0x02007cb0),('arrangement',0x020091a0),('clipping',0x0200d1a0)):
   data=(native/f'map-{index:03}-{name}.bin').read_bytes()
   assert hashlib.sha1(data).hexdigest()==entry[name+'Sha1'],(index,name,'changed native capture')
   parts[name]=data;m.put(address,data)
  m.put(0x02007f10,struct.pack('<H',index))
  m.put(0x02007f14,struct.pack('<I',0x02007cb0));m.put(0x02007f18,b'\x10\x10')
  # Test every nonzero-height canvas tile, including decorative perimeter
  # cells. Do not accidentally keep Giza's15-cell mission bounds for all maps.
  m.put(0x02007f1a,bytes((0,0,0,16,0,16)))
  m.put(0x02007f60,struct.pack('<2H',256,256));tiles=0;patterns=set()
  for y,x in itertools.product(range(16),repeat=2):
   h=parts['height'][2*(16*y+x)]
   if not h:continue
   case=('native-quarter',index,x,y,h);observed.clear()
   m.call(0x0801d624,x,y,1,stack=0x03007c00)
   check('one-native-submission',len(observed),1)
   before=m.read(0x02000000,0x40000)
   m.put(project_output-4,b'\x91'*16)
   check('projection-admitted',m.call(project,x,y,project_output,stack=0x03007c00),1)
   px,py,*flags=struct.unpack('<hh4B',m.read(project_output,8))
   nx,ny,nflags=observed[0]
   check('native-quarter-plane-match',bytes(flags),nflags)
   check('native-tilemap-coordinates',((px>>3)&255,(py>>3)&255),(nx,ny))
   cx,cy=tile_center(x,y,h)
   check('independent-canvas-projection',(px,py),(cx-16,cy-8))
   check('project-output-boundaries',m.read(project_output-4,4)+m.read(project_output+8,4),b'\x91'*8)
   check('projection-keeps-native-state',m.read(0x02000000,0x40000),before)
   patterns.add(''.join(map(str,flags)));planes.update([tuple(flags)]);tiles+=1
  maps.append(dict(map=index,tiles=tiles,planePatterns=sorted(patterns)))
finally:m.u.hook_del(hook)
check('both-map-planes-exercised',any(0 in p for p in planes) and any(1 in p for p in planes))
check('partial-quarter-occlusion-exercised',any(len(set(p))>1 for p in planes))
for x,y in ((-1,0),(0,-1),(16,0),(0,16),(255,255)):
 case=('invalid-project',x,y);m.put(project_output,b'\xa5'*8)
 check('invalid-project-rejected',m.call(project,x&0xffffffff,y&0xffffffff,project_output,stack=0x03007c00),0)
 check('invalid-project-no-output',m.read(project_output,8),b'\xa5'*8)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),maps=maps,
 planePatterns={''.join(map(str,p)):n for p,n in planes.items()},
 scope='Unconnected field-board/projection helpers only; no persistent display, camera or VRAM acceptance')
(OUT/'geomancer-map.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='maps'},indent=2))
