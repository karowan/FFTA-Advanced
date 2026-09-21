"""Installed Tomahawk geometry and native shared player/AI target-list tests.
Uses a real16x16 native grid and independent rational LOS oracle, no map stubs.
"""
import ast,ctypes as C,hashlib,importlib.util,itertools,json,pathlib,random,struct,sys
from fractions import Fraction
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
# A complete list evaluates up to256 cells; allow more than the single-query harness budget.
s=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=300000')); exec(compile(ast.Module(body=[n for n in s.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')],type_ignores=[]),'<native>','exec'))
s=ast.parse((ROOT/'scripts/test-projectile-los.py').read_text());exec(compile(ast.Module(body=[n for n in s.body if isinstance(n,ast.FunctionDef) and n.name=='oracle'],type_ignores=[]),'<independent oracle>','exec'))
out=ROOT/'build/expansion/probes';meta=json.loads((out/'combat.json').read_text());registry=json.loads((ROOT/'build/expansion/registry.json').read_text());TOMA=next(l['globalAbilityId'] for l in registry['lessons'] if l['id']=='SLD-AX-A2');CHOP=next(l['globalAbilityId'] for l in registry['lessons'] if l['id']=='SLD-AX-A1')
rom=(out/'combat.gba').read_bytes();base=bytearray((out/'combat-input.gba').read_bytes());symbols_text=(ROOT/'build/expansion/engine.symbols').read_text();symbols={l.split()[2]:int(l.split()[0],16) for l in symbols_text.splitlines() if len(l.split())==3}
assert hashlib.sha1(rom).hexdigest()==meta['romSha1'] and hashlib.sha1(base).hexdigest()==meta['baseSha1'];engine=(ROOT/'build/expansion/engine.bin').read_bytes();assert hashlib.sha1(engine).hexdigest()==meta['engineSha1'] and rom[0x1100000:0x1100000+len(engine)]==engine
assert TOMA in meta['actions']
freeze=out/'tomahawk-geometry-council'/meta['romSha1'];freeze.mkdir(parents=True,exist_ok=True)
for name,data in [('combat.gba',rom),('input.gba',base),('engine.symbols',symbols_text.encode()),('combat.json',json.dumps(meta,indent=2).encode())]:(freeze/name).write_bytes(data)
table=struct.unpack_from('<I',rom,0xccd84)[0]-0x08000000
for action in (CHOP,TOMA):base[table+action*28:table+(action+1)*28]=rom[table+action*28:table+(action+1)*28]
iwram=iwram_from_boot();m,n=ARM(rom,iwram),ARM(base,iwram);GRID,COPY,DESC,OUTPUT=0x02026000,0x02027000,0x02028000,0x02029000
counts={};expected_args=None;delegates=[];los_calls=[]
def check(group,a,b):
 assert a==b,(group,a,b)
 counts[group]=counts.get(group,0)+1

def entry(u,address,size,data):
 sp=u.reg_read(UC_ARM_REG_SP)
 args=tuple(u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))+struct.unpack('<4I',bytes(u.mem_read(sp,16)))
 if expected_args is not None:check('exact_eight_args',args,expected_args)
 if address==(symbols['ffta_combat_geometry']&~1):check('C_alignment',sp%8,0)
 delegates.append((address,args))
for name in ('ffta_combat_geometry','ffta_original_combat_geometry'):
 p=symbols[name]&~1;m.u.hook_add(UC_HOOK_CODE,entry,begin=p,end=p)
def los_entry(u,address,size,data):
 check('LOS_C_alignment',u.reg_read(UC_ARM_REG_SP)%8,0)
 los_calls.append(tuple(u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)))
p=symbols['ffta_projectile_los']&~1;m.u.hook_add(UC_HOOK_CODE,los_entry,begin=p,end=p)
def no_rng(u,address,size,data):raise AssertionError('geometry RNG')
def writes(u,access,address,size,value,data):
 assert (0x03005000<=address and address+size<=STACK+4) or (OUTPUT<=address and address+size<=OUTPUT+1024),('unexpected geometry write',hex(address),size)
for machine in (m,n):
 machine.u.hook_add(UC_HOOK_CODE,no_rng,begin=0x08002804,end=0x08002804);machine.u.hook_add(UC_HOOK_MEM_WRITE,writes)
def fixture(machine,heights=None,flags=None,actor=UNIT,xy=(2,13)):
 if heights is None:heights=[16]*256
 if flags is None:flags=[0]*256
 machine.fixture(2,[453]);unit=bytearray(machine.read(UNIT,264));unit[0xf6:0xf8]=bytes(xy);machine.put(actor,unit)
 grid=bytes(v for pair in zip(heights,flags) for v in pair);machine.put(GRID,grid);header=bytearray(16);struct.pack_into('<I',header,4,GRID);header[8]=header[13]=header[15]=16;machine.put(0x02007f10,header)
 return heights,flags

def invoke(machine,args,residue=0):
 global expected_args,delegates,los_calls
 expected_args=tuple(args);delegates=[];los_calls=[];stack=STACK+residue
 before=machine.read(args[0],264);grid=machine.read(GRID,512);machine.put(stack,struct.pack('<4I',*args[4:]));machine.put(stack+16,b'\xa5'*16);machine.put(stack-0x1000,b'\xa5'*16);frame=machine.read(stack,32)
 value=machine.call(0x080a0014,*args[:4],stack=stack)
 check('unit_immutable',machine.read(args[0],264),before);check('map_immutable',machine.read(GRID,512),grid);check('caller_frame',machine.read(stack,32),frame);check('low_guard',machine.read(stack-0x1000,16),b'\xa5'*16)
 if machine is m:
  check('one_native_delegate',[x[0] for x in delegates],[symbols['ffta_combat_geometry']&~1,symbols['ffta_original_combat_geometry']&~1])
  if los_calls:check('LOS_evaluated_coords',los_calls,[(args[1]&255,args[2]&255,args[3]&255,args[4]&255)])
 return value

def expected(a,b,h,f):
 if not all(0<=v<16 for v in (*a,*b)):return 0
 distance=abs(a[0]-b[0])+abs(a[1]-b[1])
 return int(1<=distance<=4 and abs(h[a[1]*16+a[0]]-h[b[1]*16+b[0]])<=3 and not(f[b[1]*16+b[0]]&9) and oracle(a,b,h,(0,0,16,16)))

# Verify installed record fields through the actual native selector API.
for selector,value in ((0,885),(1,0),(2,4),(3,1),(4,4),(5,3),(6,1),(7,1),(8,0),(32,145)):
 check('native_Tomahawk_fields',m.call(0x080ccd50,TOMA,selector),value)
check('secondary_preview_message',struct.unpack_from('<H',rom,table+TOMA*28+22)[0],0)
check('physical_effect_stages',rom[table+TOMA*28+12:table+TOMA*28+16],bytes((63,1,1,1)))

# Preserve all original actions at actual A0014, including a blocking map.
for action,delta,residue in itertools.product(range(347),(-3,0,3),(0,4)):
 h=[16]*256;h[6*16+7]=16+delta;h[7*16+7]=255
 for machine in (m,n):fixture(machine,h)
 args=(UNIT,6,6,7,6,action,453,0)
 actual=invoke(m,args,residue)
 check('original_no_LOS',los_calls,[])
 check('all_original_geometry',actual,invoke(n,args,residue))
# Range/height and diagonal/copy/Move coordinates, real map data.
for dx,dy,delta,residue,actor in itertools.product(range(-5,6),range(-5,6),(-4,-3,0,3,4),(0,4),(UNIT,COPY)):
 a=(6,6);b=(6+dx,6+dy);h=[1]*256;h[6*16+6]=16;h[b[1]*16+b[0]]=16+delta
 fixture(m,h,actor=actor)
 check('range_height_copy_Move',invoke(m,(actor,*a,*b,TOMA,453,0),residue),expected(a,b,h,[0]*256))
# Explicit corner and wall cases with reversed start/target, native control.
for a,b,block in (((4,4),(8,4),(5,4)),((4,4),(6,6),(5,4)),((4,4),(6,6),(4,5)),((4,4),(7,5),(5,5))):
 for top in (0,16,17,255):
  h=[16]*256;h[block[1]*16+block[0]]=top
  for aa,bb in ((a,b),(b,a)):
   for machine in (m,n):fixture(machine,h,actor=COPY)
   args=(COPY,*aa,*bb,TOMA,453,0)
   check('wall_corner_reverse',invoke(m,args),expected(aa,bb,h,[0]*256));check('native_wall_ignoring_control',invoke(n,args),1)
for high,residue in itertools.product((0,0x10000,0xabcd0000),(0,4)):
 fixture(m);args=tuple(x|high for x in (6,6,10,6,TOMA,453,0));check('native_truncation',invoke(m,(UNIT,*args),residue),1)
for b in ((-1,6),(16,6),(6,-1),(6,16)):
 fixture(m);check('invalid_bounds',invoke(m,(UNIT,6,6,b[0]&0xffffffff,b[1]&0xffffffff,TOMA,453,0)),0)

# B4A1C is the native shared selection/candidate tile-list interface used by
# player and AI callers; exercise mode0 directly. This is not a full AI turn.
def target_list(machine,action,actor=UNIT,a=(6,6),facing=0,residue=0):
 global expected_args,delegates,los_calls
 expected_args=None;delegates=[];los_calls=[]
 descriptor=bytearray(16);struct.pack_into('<I',descriptor,0,actor);descriptor[4:8]=bytes((*a,*a));struct.pack_into('<HH',descriptor,8,action,453);machine.put(DESC,descriptor);machine.put(OUTPUT-8,b'\xa5'*1040)
 before=machine.read(actor,264);grid=machine.read(GRID,512);count=machine.call(0x080b4a1c,DESC,facing,0,OUTPUT,stack=STACK+residue)
 assert count<=256
 cells=[tuple(machine.read(OUTPUT+4*i,2)) for i in range(count)]
 check('list_no_duplicates',len(set(cells)),count);check('list_guard',machine.read(OUTPUT-8,8)+machine.read(OUTPUT+4*count,8),b'\xa5'*16);check('list_unit_immutable',machine.read(actor,264),before);check('list_map_immutable',machine.read(GRID,512),grid);check('list_descriptor_immutable',machine.read(DESC,16),bytes(descriptor))
 return set(cells)
for action,residue in itertools.product(range(347),(0,4)):
 for machine in (m,n):fixture(machine)
 check('all_original_shared_lists',target_list(m,action,residue=residue),target_list(n,action,residue=residue))
# All list outputs compare against an independently generated41-cell diamond,
# then validity/height/LOS filter. Actor/copy fields intentionally remain stale.
rng=random.Random(425)
for mode,actor,residue,facing in itertools.product(range(8),(UNIT,COPY),(0,4),range(4)):
 h=[16]*256;f=[0]*256
 if mode==1:h[6*16+7]=17
 if mode==2:h[6*16+7]=255
 if mode==3:h[6*16+7]=0
 if mode==4:h[5*16+7]=19
 if mode==5:h[5*16+7]=20
 if mode==6:f[6*16+7]=9
 if mode==7:
  for y in range(2,11):
   for x in range(2,11):h[y*16+x]=rng.choice((0,13,16,16,16,19,20))
  h[6*16+6]=16
 fixture(m,h,f,actor);wanted={(x,y) for y in range(16) for x in range(16) if expected((6,6),(x,y),h,f)}
 check('shared_player_AI_tiles',target_list(m,TOMA,actor,facing=facing,residue=residue),wanted)
report={'passed':True,'romSha1':meta['romSha1'],'engineSha1':meta['engineSha1'],'action':TOMA,'checks':sum(counts.values()),'groups':counts,'scope':'Installed A0014 plus actual B4A1C player/AI shared tile lists, all347 originals, real native grid/readers, independent Fraction LOS oracle, range/height/corner/wall/copies/staleMove/ABI/guards; no rendered or full AI turn claim'}
(freeze/'results.json').write_text(json.dumps(report,indent=2)+'\n');(out/'tomahawk-geometry-tests.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
