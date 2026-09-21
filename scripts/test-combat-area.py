"""Native arc lists, original differentials and installed geometry (--current)."""
import ast,ctypes as C,hashlib,importlib.util,itertools,json,pathlib,struct,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
selected=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')]
for n in selected:
 for node in ast.walk(n):
  if isinstance(node,ast.Constant) and node.value==50000:node.value=300000
exec(compile(ast.Module(body=selected,type_ignores=[]),'<native harness>','exec'))
OUT=ROOT/'build/expansion/probes/combat-area-council';OUT.mkdir(parents=True,exist_ok=True)
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=OUT/'area.elf';raw=OUT/'area.bin'
subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-I',str(ROOT/'build/expansion'),'-Wl,-Ttext=0x091f0000','-Wl,-e,ffta_area_list',str(ROOT/'src/engine/combat-area.c'),str(ROOT/'src/engine/combat-area.s'),'-o',str(elf)],check=True,capture_output=True)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(raw)],check=True,capture_output=True)
symbol_text=subprocess.check_output([prefix+'nm.exe','-n',str(elf)],text=True)
symbols={l.split()[2]:int(l.split()[0],16) for l in symbol_text.splitlines() if len(l.split())==3}
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();base=bytearray(clean+bytes(0x1000000));binary=raw.read_bytes();base[0x11f0000:0x11f0000+len(binary)]=binary
rom=bytearray(base);struct.pack_into('<HHHHI',rom,0xb4a1c,0xb408,0x46c0,0x4b00,0x4718,symbols['ffta_area_list_entry']|1)
current='--current' in sys.argv
if current:
 p=ROOT/'build/expansion/probes';meta=json.loads((p/'combat.json').read_text())
 rom=(p/'combat.gba').read_bytes();base=(p/'combat-input.gba').read_bytes();binary=(ROOT/'build/expansion/engine.bin').read_bytes()
 assert hashlib.sha1(rom).hexdigest()==meta['romSha1'] and hashlib.sha1(binary).hexdigest()==meta['engineSha1']
 assert {426,429}.issubset(meta['actions'])
 symbols={l.split()[2]:int(l.split()[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(l.split())==3}
iwram=iwram_from_boot();m,n=ARM(bytes(rom),iwram),ARM(bytes(base),iwram)
GRID,DESC,OUTPUT,COPY=0x02026000,0x02027000,0x02028000,0x02029000
counts={};expected_args=None
def check(group,value,want):
 assert value==want,(group,value,want)
 counts[group]=counts.get(group,0)+1
def boundary(u,address,size,data):
 check('C_alignment',u.reg_read(UC_ARM_REG_SP)%8,0)
 args=tuple(u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
 check('four_arguments',args,expected_args)
m.u.hook_add(UC_HOOK_CODE,boundary,begin=symbols['ffta_area_list'],end=symbols['ffta_area_list'])
def fixture(machine,heights=None,flags=None):
 machine.fixture(2,[52]);machine.put(COPY,machine.read(UNIT,264))
 h=heights or [16]*256;f=flags or [0]*256;grid=bytes(v for pair in zip(h,f) for v in pair)
 machine.put(GRID,grid);header=bytearray(16);struct.pack_into('<I',header,4,GRID);header[8]=header[13]=header[15]=16;machine.put(0x02007f10,header)
def invoke(machine,action,origin=(6,6),facing=0,mode=0,residue=0,unit=UNIT):
 global expected_args
 d=bytearray(16);struct.pack_into('<I',d,0,unit);d[4:8]=bytes((*origin,13,13));struct.pack_into('<HH',d,8,action,52)
 machine.put(DESC,d);machine.put(OUTPUT-16,b'\xa5'*1056)
 before=machine.read(unit,264);grid=machine.read(GRID,512);machine.put(STACK+residue,b'\xa5'*16)
 expected_args=(DESC,facing,mode,OUTPUT)
 count=machine.call(0x080b4a1c,DESC,facing,mode,OUTPUT,stack=STACK+residue)
 check('count_bound',count<=256,True)
 rows=[tuple(machine.read(OUTPUT+4*i,3)) for i in range(count)]
 check('output_guard',machine.read(OUTPUT-16,16)+machine.read(OUTPUT+4*count,16),b'\xa5'*32)
 check('fourth_byte_preserved',[machine.read(OUTPUT+4*i+3,1)[0] for i in range(count)],[0xa5]*count)
 check('unit_preserved',machine.read(unit,264),before);check('map_preserved',machine.read(GRID,512),grid);check('descriptor_preserved',machine.read(DESC,16),bytes(d))
 check('caller_guard',machine.read(STACK+residue,16),b'\xa5'*16)
 return rows
for action,mode,residue in itertools.product(range(347),(0,1),(0,4)):
 for machine in (m,n):fixture(machine)
 check('all_original_native_lists',invoke(m,action,mode=mode,residue=residue),invoke(n,action,mode=mode,residue=residue))
arcs={0:((0,1),(1,1),(-1,1)),1:((-1,0),(-1,1),(-1,-1)),2:((0,-1),(-1,-1),(1,-1)),3:((1,0),(1,-1),(1,1))}
for action,origin,facing,mode,residue,unit in itertools.product((426,429),((0,0),(0,15),(15,0),(15,15),(6,6)),range(4),(0,1),(0,4),(UNIT,COPY)):
 fixture(m);wanted=[(origin[0]+dx,origin[1]+dy,16) for dx,dy in arcs[facing] if 0<=origin[0]+dx<16 and 0<=origin[1]+dy<16]
 check('rotations_edges_copies',invoke(m,action,origin,facing,mode,residue,unit),wanted)
for facing,part,delta,flag,residue in itertools.product(range(4),range(3),range(-4,5),(0,1,2,4,8,9),(0,4)):
 h=[16]*256;f=[0]*256;dx,dy=arcs[facing][part];at=(6+dy)*16+6+dx;h[at]=16+delta;f[at]=flag;fixture(m,h,f)
 wanted=[(6+x,6+y,h[(6+y)*16+6+x]) for x,y in arcs[facing] if abs(h[(6+y)*16+6+x]-16)<=2 and not(f[(6+y)*16+6+x]&9)]
 check('height_independent_flags',invoke(m,426,facing=facing,residue=residue),wanted)
for facing in (4,255,256,257):
 fixture(m);wanted=[] if facing&255>3 else [(6+x,6+y,16) for x,y in arcs[facing&255]]
 check('native_byte_direction',invoke(m,426,facing=facing),wanted)
for actor_height,target_height in ((0,1),(1,0),(0,0),(1,1)):
 h=[16]*256;h[6*16+6]=actor_height;h[7*16+6]=target_height;fixture(m,h)
 wanted=[(6,7,target_height)] if actor_height and target_height else []
 check('native_zero_height_exclusion',invoke(m,426),wanted)
for facing,chosen,mode,caller,center_height in itertools.product(range(4),range(4),(0,1),(0x080b6909,0x080b59a5,0x080bff37,0x080c002d,0x08000101),(0,16,19)):
 h=[16]*256;dx,dy=arcs[facing][0];h[(6+dy)*16+6+dx]=center_height;fixture(m,h)
 evaluated=chosen if caller in (0x080b6909,0x080b59a5) else facing
 wanted=invoke(m,426,facing=evaluated,mode=mode)
 m.put(COPY+0x1f,bytes((chosen,)));m.put(0x0202a000,struct.pack('<I',COPY))
 m.put(OUTPUT-16,b'\xa5'*1056);m.put(STACK,struct.pack('<3I',caller,COPY,0x0202a000));m.put(STACK+12,b'\xa5'*16)
 expected_args=(DESC,evaluated,mode,OUTPUT)
 count=m.call(symbols['ffta_area_list_dispatch'],DESC,facing,mode,OUTPUT,stack=STACK)
 check('player_requested_facing_AI_explicit_direction',[tuple(m.read(OUTPUT+4*i,3)) for i in range(count)],wanted)
 check('facing_output_bound',count<=3,True);check('facing_fourth_bytes',[m.read(OUTPUT+4*i+3,1)[0] for i in range(count)],[0xa5]*count)
 check('facing_buffer_guards',m.read(OUTPUT-16,16)+m.read(OUTPUT+4*count,16),b'\xa5'*32)
 check('facing_stack_guard',m.read(STACK+12,16),b'\xa5'*16)
if current:
 def geometry(machine,action,xy,target,residue=0,unit=UNIT):
  machine.put(STACK+residue,struct.pack('<4I',target[1],action,453,0));machine.put(STACK+residue+16,b'\xa5'*16)
  saved=machine.read(unit,264);grid=machine.read(GRID,512)
  value=machine.call(0x080a0014,unit,*xy,target[0],stack=STACK+residue)
  check('geometry_unit_unchanged',machine.read(unit,264),saved);check('geometry_map_unchanged',machine.read(GRID,512),grid)
  check('geometry_caller_guard',machine.read(STACK+residue+16,16),b'\xa5'*16)
  return value
 for action,mode in itertools.product(range(347),(0,4)):
  for machine in (m,n):fixture(machine)
  check('all_original_full_geometry',geometry(m,action,(6,6),(7,6),mode),geometry(n,action,(6,6),(7,6),mode))
 for action,dx,dy,delta,flag,residue,unit in itertools.product((426,429),range(-2,3),range(-2,3),(-3,-2,0,2,3),(0,1,2,8),(0,4),(UNIT,COPY)):
  h=[16]*256;f=[0]*256;target=(6+dx,6+dy);h[target[1]*16+target[0]]=16+delta;f[target[1]*16+target[0]]=flag;fixture(m,h,f)
  wanted=int((dx or dy)!=0 and abs(dx)<=1 and abs(dy)<=1 and abs(delta)<=2 and not(flag&9))
  check('installed_geometry_shape_height_flags_copies',geometry(m,action,(6,6),target,residue,unit),wanted)
report={'passed':True,'isolated':not current,'checks':sum(counts.values()),'groups':counts,'binarySha1':hashlib.sha1(binary).hexdigest(),'romSha1':hashlib.sha1(rom).hexdigest(),'scope':'Native arc lists and all347 original mode0/1 differentials; --current additionally tests installed eight-argument geometry, copied units and independent height/flag oracle'}
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
