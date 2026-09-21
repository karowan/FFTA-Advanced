"""Installed Wind Draw line geometry, untouched native lists and element rules."""
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text());OUT=pathlib.Path(meta['path']).parent
rom=pathlib.Path(meta['path']).read_bytes();base=(OUT/'input.gba').read_bytes();symbols=meta['symbols'];assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
fix=ROOT/'build/expansion/probes/samurai-state'/meta['baseSha1'];ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes()
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m,n=ARM(rom,iw),ARM(base,iw);counts=collections.Counter();GRID,DESC,OUTPUT=0x02026000,0x02027000,0x02028000
directions=((0,1),(-1,0),(0,-1),(1,0))
def check(kind,a,b):counts[kind]+=1;assert a==b,(kind,a,b)
def reset(machine,origin=(6,6),obstacle=None):
 machine.put(0x02000000,ram);machine.put(0x03000000,iw);machine.put(UNIT+0x2a,struct.pack('<5H',377,0,0,0,0))
 grid=bytearray(bytes((16,0))*256)
 if obstacle:
  x,y,height,flags=obstacle
  if 0<=x<16 and 0<=y<16:grid[2*(y*16+x):2*(y*16+x)+2]=bytes((height,flags))
 machine.put(GRID,grid);header=bytearray(16);struct.pack_into('<I',header,4,GRID);header[8]=header[13]=header[15]=16;machine.put(0x02007f10,header)
 return grid
def invoke(machine,action,origin,facing,mode,residue):
 d=bytearray(16);struct.pack_into('<I',d,0,UNIT);d[4:8]=bytes((*origin,13,13));struct.pack_into('<HH',d,8,action,377);machine.put(DESC,d);machine.put(OUTPUT-16,b'\xa5'*1056)
 before=machine.read(UNIT,264);grid=machine.read(GRID,512)
 count=machine.call(0x080b4a1c,DESC,facing,mode,OUTPUT,stack=STACK+residue);check('bounded_count',count<=256,True)
 rows=[tuple(machine.read(OUTPUT+4*i,3)) for i in range(count)]
 check('output_bounds',machine.read(OUTPUT-16,16)+machine.read(OUTPUT+4*count,16),b'\xa5'*32)
 check('preserved_unit',machine.read(UNIT,264),before);check('preserved_grid',machine.read(GRID,512),grid);check('preserved_descriptor',machine.read(DESC,16),bytes(d))
 check('unused_fourth_bytes',[machine.read(OUTPUT+4*i+3,1)[0] for i in range(count)],[0xa5]*count)
 return rows
for action,mode,residue in itertools.product(list(range(347))+[357,358,424,425,426,427,428,429,430,431],(0,1),(0,4)):
 reset(m);reset(n);check('prior_action_area_lists',invoke(m,action,(6,6),3,mode,residue),invoke(n,action,(6,6),3,mode,residue))
for origin,facing,block_at,height,flags,mode,residue in itertools.product(((0,0),(15,15),(6,6)),range(4),(1,2,3),(0,13,14,16,18,19),(0,1,2,8),(0,1),(0,4)):
 ax,ay=origin;dx,dy=directions[facing];grid=reset(m,origin,(ax+dx*block_at,ay+dy*block_at,height,flags));want=[]
 for distance in (1,2,3):
  x,y=ax+dx*distance,ay+dy*distance
  if not(0<=x<16 and 0<=y<16):break
  h,f=grid[2*(y*16+x):2*(y*16+x)+2]
  if not h or f&9 or abs(h-16)>2:break
  want.append((x,y,h))
 check('line_stop_height_edges',invoke(m,348,origin,facing,mode,residue),want)
 for distance in range(1,5):
  x,y=ax+dx*distance,ay+dy*distance
  if min(x,y)<0:continue
  m.put(STACK+residue,struct.pack('<4I',y,348,377,0))
  check('installed_line_geometry',m.call(0x080a0014,UNIT,ax,ay,x,stack=STACK+residue),int(any((x,y)==r[:2] for r in want)))
reset(m)
for item,residue in itertools.product(range(461),(0,4)):
 check('wind_not_weapon_element',m.call(0x0812f8a4,UNIT,348,item,stack=STACK+residue),2)
for target in ((6,6),(7,7),(10,6),(6,10),(16,6)):
 check('no_self_diagonal_long_or_outside',m.call(symbols['ffta_samurai_line_geometry'],6,6,*target),0)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(counts),total=sum(counts.values()),scope='Installed native area and geometry, prior action differentials, primary-independent Wind element; actual UI/damage tests separate')
(OUT/'wind-native-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
