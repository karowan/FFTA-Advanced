"""Native BFDB0 directional search, explicit facing and inverse positions.
Map readers, area lists, action metadata and coordinate-membership checks run
natively. Outer compatibility and score/path providers are controlled fixtures;
this is not a complete autonomous AI turn or rendered battle acceptance.
"""
import ast,ctypes as C,hashlib,importlib.util,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
source=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=1000000'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')],type_ignores=[]),'<native harness>','exec'))
P=ROOT/'build/expansion/probes';meta=json.loads((P/'combat.json').read_text());rom=(P/'combat.gba').read_bytes();clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
OUT=P/'arc-ai-direction'/meta['romSha1'];OUT.mkdir(parents=True,exist_ok=True);(OUT/'frozen.gba').write_bytes(rom)
assert rom[0xbfdb0:0xc01d0]==clean[0xbfdb0:0xc01d0], 'Native directional search changed'
m=ARM(rom,iwram_from_boot());TARGET,AW,TW,NODE,GRID,MOVE,AREA=0x0201f000,0x02020000,0x02020100,0x02021000,0x02023000,0x02024000,0x02025000
counts={};cases=[];wanted_origin=None;wanted_facing=None;calls=[];scores=[]
REGS=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)
forward=((0,1),(-1,0),(0,-1),(1,0))
def check(group,a,b):
 assert a==b,(group,a,b)
 counts[group]=counts.get(group,0)+1

def result(u,value):u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
def permit(u,address,size,data):result(u,1)
def score(u,address,size,data):
 sp=u.reg_read(UC_ARM_REG_SP);xy=tuple(m.read(sp+12,2));face=m.word(sp+20)
 scores.append((xy,face));result(u,100 if xy==wanted_origin and face==wanted_facing else 0)
def pathscore(u,address,size,data):result(u,1)
for address,hook in ((0x080bdf9c,permit),(0x080c48a4,permit),(0x080be494,score),(0x080be3b8,pathscore),(0x080be074,permit)):
 m.u.hook_add(UC_HOOK_CODE,hook,begin=address,end=address)
def area_entry(u,address,size,data):
 desc=u.reg_read(UC_ARM_REG_R0);face=u.reg_read(UC_ARM_REG_R1);mode=u.reg_read(UC_ARM_REG_R2)
 calls.append({'caller':hex(u.reg_read(UC_ARM_REG_LR)),'origin':list(m.read(desc+4,2)),'center':list(m.read(desc+6,2)),'facing':face,'mode':mode})
m.u.hook_add(UC_HOOK_CODE,area_entry,begin=0x080b4a1c,end=0x080b4a1c)
def no_rng(u,address,size,data):raise AssertionError('Directional geometry/search consumed RNG with controlled scorers')
m.u.hook_add(UC_HOOK_CODE,no_rng,begin=0x08002804,end=0x08002804)

def end_facing(u,address,size,data):result(u,(wanted_facing+2)&3)
m.u.hook_add(UC_HOOK_CODE,end_facing,begin=0x080be9f0,end=0x080be9f0)

def fragment(begin,end,values,stack=STACK):
 u=m.u
 for register,value in values.items():u.reg_write(register,value)
 u.reg_write(UC_ARM_REG_CPSR,0x30);u.reg_write(UC_ARM_REG_SP,stack)
 def stop(u,address,size,data):
  if address==end:u.emu_stop()
 hook=u.hook_add(UC_HOOK_CODE,stop)
 try:u.emu_start(begin|1,0,count=50000)
 finally:u.hook_del(hook)
 check('pipeline_continuation',u.reg_read(UC_ARM_REG_PC),end)

def carry_pipeline(action,origin,target,facing):
 manager,battle,event,obj=0x020101f8,0x02027000,0x02027400,0x02028000
 m.put(manager+0x5290,m.read(NODE,0x21c));m.put(manager+4,struct.pack('<I',TW))
 fragment(0x080c0b46,0x080c0bce,{UC_ARM_REG_R7:manager})
 check('published_action',m.read(manager+0x54be,2),struct.pack('<H',action))
 check('published_actor_target',m.read(manager+0x54b2,4),bytes((*target,*origin)))
 check('native_distinct_end_turn_facing',m.read(manager+0x54ba,1),bytes(((facing+2)&3,)))
 check('attack_facing_not_overwritten',m.read(manager+0x5440,1),bytes((facing,)))
 m.put(battle,bytes(0x300));m.put(battle+4,struct.pack('<I',AW));m.put(battle+0xa6,struct.pack('<H',action))
 # Begin with a deliberately different actual wrapper direction.
 m.put(AW+0x1f,bytes(((facing+1)&3,)))
 fragment(0x08093a66,0x08093a70,{UC_ARM_REG_R7:event,UC_ARM_REG_R8:battle})
 check('AI_carries_chosen_facing',m.read(AW+0x1f,1),bytes((facing,)))
 check('AI_schedules_same_actor',m.read(battle+8,4),struct.pack('<I',AW))
 fragment(0x08096a40,0x08096a4c,{UC_ARM_REG_R0:(facing+1)&3,UC_ARM_REG_R4:0,UC_ARM_REG_R8:battle})
 check('launch_preserves_chosen_facing',m.read(battle+0x88,1),bytes((facing,)))
 m.put(obj,bytes(0x300));m.put(STACK,struct.pack('<8I',*target,action,453,0,0,0,0))
 fragment(0x080a39f8,0x080a3ac8,{UC_ARM_REG_R0:obj,UC_ARM_REG_R1:0,UC_ARM_REG_R2:0,UC_ARM_REG_R3:AW})
 check('constructor_explicit_facing',m.read(obj+8,1),bytes((facing,)))
 check('constructor_actual_action',m.read(obj+0x10,2),struct.pack('<H',action))
 check('constructor_same_wrapper',m.read(obj,4),struct.pack('<I',AW))

def fixture(action,origin,facing,center_kind,flank,stored_xy):
 global wanted_origin,wanted_facing,calls,scores
 wanted_origin,wanted_facing=origin,facing;calls=[];scores=[]
 m.fixture(2,[453]);actor=bytearray(m.read(UNIT,264));actor[0xf6:0xf9]=bytes((*stored_xy,3));m.put(UNIT,actor)
 dx,dy=forward[facing];target=(origin[0]+dx-dy*flank,origin[1]+dy+dx*flank)
 data=bytearray(actor);data[6]=2;data[0xf6:0xf9]=bytes((*target,1));struct.pack_into('<H',data,0x28,0x8000);m.put(TARGET,data)
 m.put(AW,struct.pack('<I',UNIT)+bytes(252));m.put(TW,struct.pack('<I',TARGET)+bytes(252))
 grid=bytearray(bytes((16,0))*256);center=(origin[0]+dx,origin[1]+dy);at=2*(center[1]*16+center[0])
 if center_kind=='invalid':grid[at]=0
 elif center_kind=='height':grid[at]=19
 elif center_kind=='flag':grid[at+1]=1
 m.put(GRID,grid);header=bytearray(16);struct.pack_into('<I',header,4,GRID);header[8]=header[13]=header[15]=16;m.put(0x02007f10,header)
 node=bytearray(0x21c);struct.pack_into('<IIHH',node,0,AW,TW,action,0);struct.pack_into('<I',node,0x204,AREA);struct.pack_into('<I',node,0x214,MOVE);m.put(NODE,node);m.put(MOVE,bytes([2])*256);m.put(AREA-16,b'\xa5'*4128)
 return target,bytes(actor),bytes(data),bytes(grid)

for action,origin,facing,center_kind,flank,stored_xy,residue in itertools.product((426,429),((6,6),(9,9)),range(4),('clear','invalid','height','flag'),(-1,1),((2,13),(6,6)),(0,4)):
 target,actor,tdata,grid=fixture(action,origin,facing,center_kind,flank,stored_xy)
 m.call(0x080bfdb0,NODE,stack=STACK+residue)
 choice=m.read(NODE+0x1ac,6)
 check('selected_origin',tuple(choice[:2]),origin);check('selected_target',tuple(choice[2:4]),target);check('explicit_facing_retained',choice[4],facing);check('successful_node',choice[5],1)
 inverse=[c for c in calls if c['caller']=='0x80bfec1']
 check('four_inverse_rotations',sorted(c['facing'] for c in inverse),[0,1,2,3]);check('inverse_origins',[c['origin'] for c in inverse],[list(target)]*4)
 check('desired_candidate_scored',(origin,facing) in scores,True)
 check('actor_restored',m.read(UNIT,264),actor);check('target_unchanged',m.read(TARGET,264),tdata);check('grid_unchanged',m.read(GRID,512),grid);check('area_outer_guards',m.read(AREA-16,16)+m.read(AREA+4096,16),b'\xa5'*32)
 carry_pipeline(action,origin,target,facing)
 cases.append({'action':action,'origin':origin,'target':target,'facing':facing,'center':center_kind,'storedXY':stored_xy,'SPmod8':residue,'selected':list(choice),'areaCalls':len(calls)})
report={'passed':True,'romSha1':meta['romSha1'],'checks':sum(counts.values()),'groups':counts,'cases':cases,'scope':__doc__}
(OUT/'results.json').write_text(json.dumps(report,indent=2));(P/'arc-ai-direction-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='cases'},indent=2))
