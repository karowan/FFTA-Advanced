"""Fresh native arc UI, actual recipient lists, damage and suspend lifecycle."""
import ast,ctypes as C,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];FIX=ROOT/'build/expansion/probes/battle-fixture'
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
RETURN,STACK=0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native actor enumeration>','exec'))
rom=(FIX/'frozen.gba').read_bytes();sha=hashlib.sha1(rom).hexdigest();meta=json.loads((ROOT/'build/expansion/probes/combat.json').read_text())
assert sha==meta['romSha1'] and {426,429}.issubset(meta['actions'])
FAMILY=ROOT/'build/expansion/probes/arcs-in-game';OUT=FAMILY/sha;OUT.mkdir(parents=True,exist_ok=True)
ROM=OUT/'frozen.gba';ROM.write_bytes(rom);START=OUT/'initial.state';START.write_bytes((FIX/'battle-ready.state').read_bytes())
Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];heap=runpy.run_path(str(ROOT/'scripts/probe-ap-copy-heap.py'))['heap']
checks={};cases=[];guard=b'\xd7'*0xbc
def check(group,value,want):
 assert value==want,(group,value,want)
 checks[group]=checks.get(group,0)+1
def u16(b,p):return struct.unpack_from('<H',b,p)[0]
def u32(b,p):return struct.unpack_from('<I',b,p)[0]
def native_wrappers(e):
 # Enumerate on a detached clone. Only the native returned addresses are
 # used; no scratch output, target list or calculated result enters gameplay.
 machine=ARM(rom,C.string_at(*e.maps[0x03000000]));machine.put(0x02000000,e.memory())
 count=machine.call(0x08099cdc,machine.word(0x0200f4b0),0x02008000)
 check('native_actor_count',count,12);result={}
 for i in range(count):
  wrapper=machine.word(0x02008000+4*i)
  check('native_wrapper_bounds',0x02000000<=wrapper<=0x0203ff70 and wrapper%4==0,True)
  unit=machine.word(wrapper)-0x02000000
  check('native_wrapper_unique_unit',unit not in result,True);result[unit]=wrapper-0x02000000
 return result
def tap(e,k,wait=180):e.run(8,k);e.run(wait)
def shot(e,d,label):
 b=e.memory();e.screenshot(d/(label+'.png'));e.save(d/(label+'.state'));(d/(label+'.ram')).write_bytes(b)
 check('reserved_guard',b[0x3ff44:],guard);check('heap_boundary',heap(b)['end'],0x0203f800)
 return b
def persistent(b):return b[0x1940:0x1e98]
def member_control(d):
 # Diagnostic image pauses before the native per-recipient executor. The
 # unmodified production image separately completes the same confirmation.
 trial=bytearray(rom);trial[0xa24a8:0xa24aa]=b'\xfe\xe7';p=d/'member-trap.gba';p.write_bytes(trial);e=Emulator(p)
 try:
  e.load(d/'confirmation.state');tap(e,256,300);shot(e,d,'member-trap')
  regs=struct.unpack_from('<17I',(d/'member-trap.state').read_bytes(),0x20);check('executor_breakpoint',regs[15],0x080a24aa)
  b=e.memory();obj=regs[9]-0x02000000;count=u32(b,obj+0x2c0);assert count<=15
  return [u32(b,u32(b,obj+0x20+i*0x2c)-0x02000000) for i in range(count)]
 finally:e.close()
def execute(d,image,seed,label):
 p=d/(label+'.gba');p.write_bytes(image);e=Emulator(p)
 try:
  e.load(d/'confirmation.state');C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4)
  tap(e,256,2400);b=shot(e,d,label);return b
 finally:e.close()

facings={0:((0,1),32),1:((-1,0),64),2:((0,-1),16),3:((1,0),128)}
final_change=next(c for c in meta['changes'] if c['name']=='ffta_physical_final_entry')
control=bytearray(rom);offset=final_change['offset'];control[offset:offset+final_change['size']]=bytes.fromhex(final_change['expected'])
hit_coverage=set();miss_coverage=set()
for facing,blocked,diagonal in [(d,False,False) for d in range(4)]+[(d,True,False) for d in range(4)]+[(d,'hole',False) for d in range(4)]+[(3,False,True)]:
 d=OUT/f'reaping-{facing}-blocked{blocked}-diagonal{diagonal}';d.mkdir(exist_ok=True);e=Emulator(ROM)
 try:
  e.load(START);e.run(1);r=e.memory();actor=0x398;check('original_Bangaa_race',r[actor+6],2);wrappers=native_wrappers(e)
  for off in (5,7,0x35):e.set_memory(actor+off,b'\x10')
  e.set_memory(actor+0x2a,struct.pack('<5H',458,0,0,0,0));e.set_memory(actor+0x40+106,b'\x99')
  grid=u32(r,0x7f14)-0x02000000
  for y in range(13,16):
   for x in range(3):e.set_memory(grid+2*(y*16+x),bytes((2,0)))
  def place(unit,x,y):
   # A fixture changes native coordinate fields together, before opening the
   # selector. No target list, hit flag or action result is directly supplied.
   wrapper=wrappers[unit]
   check('wrapper_identity',u32(e.memory(),wrapper),0x02000000+unit)
   e.set_memory(unit+0xf6,bytes((x,y)));e.set_memory(wrapper+8,struct.pack('<3H',x*32+16,32,y*32+16));e.set_memory(unit+0x18,struct.pack('<HH',999,999))
  for i,unit in enumerate((0x80,0x188,0x290,0x4a0,0x5a8)):place(unit,8,8+i)
  (dx,dy),key=facings[facing];tiles=[(1+dx,14+dy),(1+dx-dy,14+dy+dx),(1+dx+dy,14+dy-dx)]
  targets=(0x80,0x188,0x4a0)
  for unit,xy in zip(targets,tiles):place(unit,*xy)
  if blocked:e.set_memory(grid+2*(tiles[0][1]*16+tiles[0][0]),bytes((0 if blocked=='hole' else 5,0)))
  if blocked=='hole':place(0x80,8,13)
  before=shot(e,d,'seeded')
  for k in (32,256,32,256,32,256,key):tap(e,k)
  if diagonal:tap(e,16)
  shot(e,d,'target-selected');tap(e,256);preview=shot(e,d,'preview')
  check('preview_no_MP',u16(preview,actor+28),14);check('preview_no_HP',[u16(preview,t+24) for t in targets],[999]*3)
  tap(e,1);cancel=shot(e,d,'cancelled');check('cancel_no_cost',u16(cancel,actor+28),14)
  check('cancel_releases_preview',heap(cancel)['freePayload']>=heap(preview)['freePayload'],True)
  tap(e,256);again=shot(e,d,'repreview');check('repreview_no_heap_growth',heap(again)['freePayload'],heap(preview)['freePayload'])
  tap(e,256);shot(e,d,'confirmation')
 finally:e.close()
 members=member_control(d);wanted=[0x02000000+t for t in targets[(1 if blocked else 0):]]
 if diagonal:wanted=[0x020004a0]
 check('actual_native_recipient_set',sorted(members),sorted(wanted));check('caster_excluded',0x02000398 in members,False)
 for seed in (0,1):
  result=execute(d,rom,seed,f'seed-{seed}-executed');native=execute(d,control,seed,f'seed-{seed}-reference')
  check('native_reference_same_MP',u16(native,actor+28),6);check('MP_once_per_arc',u16(result,actor+28),6)
  check('caster_unchanged_HP',u16(result,actor+24),47);check('AP_inventory_preferences',persistent(result),persistent(before))
  check('axe_not_consumed',result[actor+0x2a:actor+0x34],before[actor+0x2a:actor+0x34])
  for target in targets:
   damage=999-u16(result,target+24);reference=999-u16(native,target+24)
   check('independent_native_P_factor',damage,reference*11//10)
   if reference:hit_coverage.add(target)
   elif target+0x02000000 in members:miss_coverage.add(target)
  e=Emulator(ROM)
  try:
   e.load(d/f'seed-{seed}-executed.state')
   for k in (32,32,256):tap(e,k)
   tap(e,256,900);next_turn=shot(e,d,f'seed-{seed}-next-turn')
   check('native_turn_advanced',u32(next_turn,u32(next_turn,0xf438)-0x02000000+0x18),0x020005a8)
  finally:e.close()
 cases.append({'action':429,'facing':facing,'blocked':blocked,'diagonal':diagonal,'members':members})
check('all_recipients_hit_coverage',hit_coverage,set((0x80,0x188,0x4a0)));check('nonvacuous_miss',bool(miss_coverage),True)

# Native Move first: original unit coordinates remain stale during selection.
d=OUT/'overpower-after-Move';d.mkdir(exist_ok=True);e=Emulator(ROM)
try:
 e.load(START);e.run(1);e.set_memory(0xaa,struct.pack('<H',455));e.set_memory(0xae,b'\0\0');e.set_memory(0x1b5e,b'\x94')
 e.set_memory(0x33fc,struct.pack('<HH',250,250))
 before=shot(e,d,'seeded')
 for turn in range(4):
  for key in (32,32,256):tap(e,key)
  tap(e,256,4500 if turn==3 else 900)
 for key in (256,128,128,32):tap(e,key)
 tap(e,256,600);moved=shot(e,d,'moved');check('stale_unit_coordinates',moved[0x176:0x178],bytes((2,13)))
 for key in (256,32,256,32,256,128):tap(e,key)
 tap(e,256);preview=shot(e,d,'preview');tap(e,1);cancel=shot(e,d,'cancelled');check('Move_cancel_no_cost',u16(cancel,0x9c),16)
 tap(e,256);tap(e,256);shot(e,d,'confirmation')
finally:e.close()
check('moved_origin_native_members',member_control(d),[0x020033e4])
outcomes=[]
for seed in (0,1):
 result=execute(d,rom,seed,f'seed-{seed}-executed');native=execute(d,control,seed,f'seed-{seed}-reference')
 check('Overpower_native_P_factor',250-u16(result,0x33fc),(250-u16(native,0x33fc))*9//10)
 check('Overpower_MP_once',u16(result,0x9c),12);check('Overpower_AP_inventory',persistent(result),persistent(before))
 outcomes.append(250-u16(result,0x33fc))
 e=Emulator(ROM)
 try:
  e.load(d/f'seed-{seed}-executed.state');tap(e,256,900);after=shot(e,d,f'seed-{seed}-next-turn')
  check('Move_Action_facing_advances',u32(after,u32(after,0xf438)-0x02000000+0x18),0x02000188)
  if seed==1:
   for key in (1,8,16,256,256):tap(e,key)
   old=e.memory(0);tap(e,256,300);saved=e.memory(0);check('suspend_written',saved!=old,True)
   (d/'suspended.sav').write_bytes(saved);expected=after
 finally:e.close()
check('Overpower_hit_and_miss',min(outcomes)==0 and max(outcomes)>0,True)
e=Emulator(ROM)
try:
 e.set_memory(0,saved,0);e.run(3600);e.set_memory(0x3ff44,guard)
 for key,wait in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):tap(e,key,wait)
 cold=shot(e,d,'cold-resumed')
 for offset in (0x98,0x9c,0x33fc):check('cold_HP_MP',u16(cold,offset),u16(expected,offset))
 check('cold_AP_inventory',persistent(cold),persistent(expected));check('cold_actor_position',cold[0x176:0x178],bytes((4,14)))
 tap(e,32);tap(e,256);shot(e,d,'cold-interactive-menu')
finally:e.close()
report={'passed':True,'romSha1':sha,'checks':sum(checks.values()),'groups':checks,'arcCases':cases,'OverpowerDamage':outcomes,'scope':'Actual fresh native UI/Move/recipient lists/friendlyfire/independent hit rolls/P factors/MP/cancel/turn/coldsave; AI geometry is tested separately, full AI turn not claimed'}
(OUT/'report.json').write_text(json.dumps(report,indent=2));(FAMILY/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

