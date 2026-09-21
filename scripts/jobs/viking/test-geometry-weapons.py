"""Native Viking axe admission and symmetric melee geometry, without helper stubs."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
P=ROOT/'build/expansion/probes';meta=_load_job_candidate(P/'viking/current.json')
ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
parent=json.loads((P/'job-state/current.json').read_text());base=bytearray(pathlib.Path(parent['path']).read_bytes())
fix=pathlib.Path(meta['path']).parent/'executor';ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes()
UNIT,TARGET,EQUIPMENT,RETURN,STACK,GRID=0x02000080,0x020033e4,0x02002000,0x08000100,0x03007000,0x02026000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
table=struct.unpack_from('<I',rom,0xccd84)[0]-0x08000000
for action in (367,370):base[table+action*28:table+(action+1)*28]=rom[table+action*28:table+(action+1)*28]
m,n=ARM(rom,iw),ARM(base,iw);checks=collections.Counter()
def check(name,actual,expected):
 checks[name]+=1;assert actual==expected,(name,actual,expected,globals().get('case'))
def fixture(machine,job=118,weapon=399):
 machine.put(0x02000000,ram);machine.put(0x03000000,iw)
 actor=bytearray(ram[0x80:0x188]);actor[5]=actor[7]=actor[0x35]=job;actor[6]=2
 actor[0x3a:0x3c]=bytes(2);actor[0xe8:0xf0]=bytes(8);struct.pack_into('<4H',actor,0x18,100,100,50,50)
 struct.pack_into('<5H',actor,0x2a,weapon,0,0,0,0);actor[0xf6:0xf8]=bytes([6,6]);machine.put(UNIT,actor)
 target=bytearray(ram[0x33e4:0x34ec]);target[0xe8:0xf0]=bytes(8);struct.pack_into('<4H',target,0x18,250,250,49,49)
 target[0xf6:0xf8]=bytes([7,6]);machine.put(TARGET,target)
def geometry(machine,action,dx,dy,delta,residue):
 fixture(machine);grid=bytearray(bytes([16,0])*256);grid[2*((6+dy)*16+6+dx)]=16+delta;machine.put(GRID,grid)
 info=bytearray(16);struct.pack_into('<I',info,4,GRID);info[8]=info[13]=info[15]=16;machine.put(0x02007f10,info)
 stack=STACK+residue;machine.put(stack,struct.pack('<4I',6+dy,action,399,0))
 before=machine.read(UNIT,264)+machine.read(GRID,512);rng=machine.read(0x030034b0,4)
 value=machine.call(0x080a0014,UNIT,6,6,6+dx,stack=stack)
 check('native-geometry-isolation',machine.read(UNIT,264)+machine.read(GRID,512),before)
 check('geometry-no-rng',machine.read(0x030034b0,4),rng)
 return value
for action,dx,dy,delta,residue in itertools.product((367,370),range(-2,3),range(-2,3),range(-5,6),(0,4)):
 case=(action,dx,dy,delta,residue)
 check('r1-h2-symmetric',geometry(m,action,dx,dy,delta,residue),int(abs(dx)+abs(dy)==1 and abs(delta)<=2))
 # These use Nighthawk's explicit action range/height fields, whose native
 # geometry is symmetric. The ordinary Fight -3/+2 rule does not apply.
 check('native-donor-r1-h2-control',geometry(n,action,dx,dy,delta,residue),int(abs(dx)+abs(dy)==1 and abs(delta)<=2))
for action,residue in itertools.product(range(347),(0,4)):
 check('all-original-geometry',geometry(m,action,1,0,0,residue),geometry(n,action,1,0,0,residue))
context=0x0200f3f0
for action,job,item,residue in itertools.product((367,370),(13,14,15,16,17,18,117,118),range(461),(0,4)):
 fixture(m,job,item)
 m.put(context,struct.pack('<IIIHH',UNIT,TARGET,TARGET,action,0))
 before=m.read(UNIT,264)+m.read(TARGET,264)
 category=m.call(0x080ca7a4,item,3)
 check('all-items-cross-job-axe-admission',m.call(meta['symbols']['ffta_viking_physical_eligibility_entry'],context,stack=STACK+residue),int(category==31))
 check('admission-isolation',m.read(UNIT,264)+m.read(TARGET,264),before)
DESC,OUTPUT=0x02027000,0x02028000
for action,center,delta,residue in itertools.product((368,371),((0,0),(15,15),(7,6)),range(-3,4),(0,4)):
 fixture(m);cx,cy=center;grid=bytearray(bytes([16,0])*256)
 nx,ny=(cx+1,cy) if cx<15 else (cx-1,cy);grid[2*(ny*16+nx)]=16+delta;m.put(GRID,grid)
 info=bytearray(16);struct.pack_into('<I',info,4,GRID);info[8]=info[13]=info[15]=16;m.put(0x02007f10,info)
 descriptor=bytearray(16);struct.pack_into('<I',descriptor,0,UNIT);descriptor[4:8]=bytes([6,6,cx,cy]);struct.pack_into('<HH',descriptor,8,action,399);m.put(DESC,descriptor)
 m.put(OUTPUT-16,b'\xa5'*1056);before=m.read(UNIT,264)
 count=m.call(0x080b4a1c,DESC,0,1,OUTPUT,stack=STACK+residue)
 actual={tuple(m.read(OUTPUT+i*4,3)) for i in range(count)}
 expected={(x,y,grid[2*(y*16+x)]) for x,y in [(cx,cy),(cx-1,cy),(cx+1,cy),(cx,cy-1),(cx,cy+1)] if 0<=x<16 and 0<=y<16 and abs(grid[2*(y*16+x)]-16)<=2}
 check('real-native-cross-center-edges-height',actual,expected)
 check('no-duplicate-area-recipient',count,len(expected))
 check('cross-output-bounds',m.read(OUTPUT-16,16)+m.read(OUTPUT+4*count,16),b'\xa5'*32)
 check('cross-unit-and-map-isolation',m.read(UNIT,264)+m.read(GRID,512),before+bytes(grid))
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),scope=__doc__)
(ROM.parent/'geometry-weapons.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
