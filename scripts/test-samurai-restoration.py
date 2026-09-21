"""Murasame/Kiyomori formula, native execution and unchanged donor dispatch."""
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
P=ROOT/'build/expansion/probes';meta=json.loads((P/'samurai/current.json').read_text());OUT=pathlib.Path(meta['path']).parent
rom=pathlib.Path(meta['path']).read_bytes();base=(OUT/'input.gba').read_bytes();symbols=meta['symbols'];assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
fix=P/'samurai-state'/meta['baseSha1'];ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes();regs=struct.unpack_from('<17I',(fix/'execute-trap.state').read_bytes(),0x20)
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000;TARGET=0x020033e4;CTX=0x0200f3f0
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
native,expanded=ARM(base,iw),ARM(rom,iw);counts=collections.Counter();outcomes=[]
def check(kind,a,b):counts[kind]+=1;assert a==b,(kind,a,b)
from native_battle_wrappers import from_memory
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()}
WRAPPER=wrappers[UNIT]

def reset(m,action=350,state=5):
 m.put(0x02000000,ram);m.put(0x03000000,iw)
 for unit in (UNIT,TARGET):m.put(unit+0xe8,bytes(8));m.put(unit+0x18,struct.pack('<HHHH',100,100,50,50))
 m.put(UNIT+5,bytes([116,1,116]));m.put(UNIT+0x35,b'\x74');m.put(UNIT+0x3a,bytes(2));m.put(UNIT+0x2a,struct.pack('<5H',379,0,0,0,0));m.put(UNIT+0xf6,bytes([4,14]))
 allegiance=struct.unpack_from('<H',ram,0x33e4+0x28)[0]&0x7fff;m.put(TARGET+0x28,struct.pack('<H',allegiance))
 m.put(0x02001e98,bytes([state])+bytes(35));m.put(WRAPPER,struct.pack('<I',UNIT));m.put(WRAPPER+8,struct.pack('<H',4<<5));m.put(WRAPPER+12,struct.pack('<H',14<<5))
 context=bytearray(0x34);struct.pack_into('<IIIHH',context,0,UNIT,TARGET,TARGET,action,0);struct.pack_into('<I',context,0x30,0x08553e70+90*4);m.put(CTX,context)
 m.put(regs[13],struct.pack('<4I',action,0,0,255));m.put(0x030034b0,struct.pack('<I',0))
for maximum,packed,residue in itertools.product((1,2,3,5,17,100,399,400,401,999,65535),range(256),(0,4)):
 reset(expanded,state=packed)
 value=(packed>>1)&7;factor=5 if value in (1,2,5,6,7) else 4
 for hp in sorted({0,1,maximum,max(1,maximum-1),max(1,maximum-5)}):
  expanded.put(TARGET+0x18,struct.pack('<HH',hp,maximum));before=expanded.read(0x02000000,0x40000)
  want=min(maximum-hp,min(35*maximum,14000)*factor//400) if hp and hp<maximum else 0
  check('rational_heal_and_caps',expanded.call(symbols['ffta_murasame_magnitude_entry'],CTX,stack=STACK+residue),want)
  check('heal_query_no_writes',expanded.read(0x02000000,0x40000)==before,True)
# Native selector25 retains every original descriptor/user's result.
table=struct.unpack_from('<I',base,0xccd84)[0]-0x08000000
for action in range(347):
 for slot,stage in enumerate(base[table+action*28+12:table+action*28+15]):
  if base[0x553e70+stage*4+3]!=25:continue
  for m in (native,expanded):
   reset(m,action);m.put(CTX+0x28,bytes([slot]));m.put(CTX+0x30,struct.pack('<I',0x08553e70+stage*4))
  check('original_selector25',expanded.call(symbols['ffta_murasame_magnitude_entry'],CTX),native.call(0x08131838,CTX))
for action,item in itertools.product((350,351),range(461)):
 reset(expanded,action);expanded.put(UNIT+0x2a,struct.pack('<5H',item,0,0,0,0))
 expected=item!=0 and expanded.call(0x080ca7a4,item,3)==9
 check('primary_katana_admission',expanded.call(symbols['ffta_physical_eligibility_entry'],CTX),int(expected))
for action,silenced,residue in itertools.product((350,351),(0,1),(0,4)):
 reset(expanded,action);expanded.put(UNIT+0xeb,bytes([8 if silenced else 0]))
 check('native_menu_usable_under_silence',expanded.call(0x08133e18,UNIT,action,255,stack=STACK+residue),1)
 check('native_no_return_magic',expanded.call(0x0812e6e0,UNIT,TARGET,action,11,stack=STACK+residue),0)
 check('native_no_counter',expanded.call(0x0812e6e0,UNIT,TARGET,action,8,stack=STACK+residue),0)
 check('support_technique_not_reflect_flag',expanded.call(0x080ccd50,action,18),0)
 check('no_doublecast_selector',expanded.call(0x080ccd50,action,19),0)
# Donor controls make the Silence/Return Magic checks non-vacuous.
reset(expanded);expanded.put(UNIT+0xeb,b'\x08')
check('native_cure_blocked_by_silence',expanded.call(0x08133e18,UNIT,1,255),0)
check('native_fire_return_magic',expanded.call(0x0812e6e0,UNIT,TARGET,23,11),1)
check('native_cure_doublecast_selector',expanded.call(0x080ccd50,1,19),1)
for action,actor_side,target_side,charm,confusion,hp,undead in itertools.product((350,351),(0,1),(0,1),(0,1),(0,1),(0,100),(0,1)):
 reset(expanded,action);expanded.put(UNIT+0x28,struct.pack('<H',actor_side<<15));expanded.put(TARGET+0x28,struct.pack('<H',target_side<<15))
 expanded.put(UNIT+0xeb,bytes([(charm<<5)|(confusion<<4)]));expanded.put(TARGET+0x18,struct.pack('<H',hp))
 expanded.put(TARGET+0xe9,bytes([undead<<3]))
 before=expanded.read(0x02000000,0x40000)
 want=int(bool(hp) and not confusion and (actor_side^charm)==target_side and not (action==350 and undead))
 check('ally_charm_confusion_ko_undead_admission',expanded.call(symbols['ffta_physical_eligibility_entry'],CTX),want)
 check('eligibility_does_not_mutate',expanded.read(0x02000000,0x40000),before)
for packed,residue in itertools.product(range(256),(0,4)):
 reset(expanded,state=packed);expanded.put(TARGET+0x18,struct.pack('<HH',1,999));expanded.put(TARGET+0xe9,b'\x08')
 check('undead_magnitude_zero',expanded.call(symbols['ffta_murasame_magnitude_entry'],CTX,stack=STACK+residue),0)
for packed,seed in itertools.product((1,5,13),(0,1)):
 reset(expanded,state=packed);expanded.put(TARGET+0x18,struct.pack('<HH',100,250));expanded.put(TARGET+0xe9,b'\x08');expanded.put(0x030034b0,struct.pack('<I',seed))
 before=expanded.read(TARGET,264)
 expanded.call(0x080a433c,regs[0],WRAPPER,5,14,stack=regs[13])
 check('native_executor_undead_recipient_unchanged',expanded.read(TARGET,264),before)
# Kiyomori uses the complete native Barrier effect pipeline. Compare each
# recipient byte, including conflicting statuses and their timer cleanup.
for status,residue in itertools.product(range(-1,44),(0,4)):
 for machine,action in ((native,12),(expanded,351)):
  reset(machine,action);machine.put(TARGET+0xe8,struct.pack('<Q',0 if status<0 else 1<<status))
  for slot,stage in enumerate((45,78)):
   machine.put(CTX+0x28,bytes([slot]));machine.put(CTX+0x30,struct.pack('<I',0x08553e70+stage*4))
   machine.call(0x0813388c,stack=STACK+residue)
 check('kiyomori_native_barrier_status_cleanup',expanded.read(TARGET,264),native.read(TARGET,264))
 check('kiyomori_native_barrier_actor_unchanged',expanded.read(UNIT,264),native.read(UNIT,264))
 check('kiyomori_native_barrier_custom_state',expanded.read(0x02001e98,36),bytes([5])+bytes(35))
# Enumerate the real native cross against an independently constructed map.
# Mode1 uses the chosen center, not the actor's old pre-Move unit position.
GRID,DESC,OUTPUT=0x02026000,0x02027000,0x02028000
for action,center,delta,residue in itertools.product((350,351),((0,0),(15,15),(7,6)),range(-3,4),(0,4)):
 reset(expanded,action);cx,cy=center;grid=bytearray(bytes((16,0))*256)
 neighbor=(cx+1,cy) if cx<15 else (cx-1,cy);grid[2*(neighbor[1]*16+neighbor[0])]=16+delta;expanded.put(GRID,grid)
 header=bytearray(16);struct.pack_into('<I',header,4,GRID);header[8]=header[13]=header[15]=16;expanded.put(0x02007f10,header)
 descriptor=bytearray(16);struct.pack_into('<I',descriptor,0,UNIT);descriptor[4:8]=bytes((6,6,cx,cy));struct.pack_into('<HH',descriptor,8,action,379);expanded.put(DESC,descriptor)
 expanded.put(OUTPUT-16,b'\xa5'*1056);before=expanded.read(UNIT,264)
 count=expanded.call(0x080b4a1c,DESC,0,1,OUTPUT,stack=STACK+residue);check('cross_count_bound',count<=5,True)
 actual={tuple(expanded.read(OUTPUT+i*4,3)) for i in range(count)}
 wanted={(x,y,grid[2*(y*16+x)]) for x,y in ((cx,cy),(cx-1,cy),(cx,cy-1),(cx+1,cy),(cx,cy+1)) if 0<=x<16 and 0<=y<16 and abs(grid[2*(y*16+x)]-16)<=2}
 check('cross_edges_center_height',actual,wanted);check('cross_no_duplicate',len(actual),count)
 check('cross_output_guard',expanded.read(OUTPUT-16,16)+expanded.read(OUTPUT+4*count,16),b'\xa5'*32)
 check('cross_preserves_unit',expanded.read(UNIT,264),before)
 check('cross_preserves_grid',expanded.read(GRID,512),bytes(grid))
 check('cross_preserves_descriptor',expanded.read(DESC,16),bytes(descriptor))
check('kiyomori_native_self_selection',expanded.call(0x080ccd50,351,6),3)
for dx,dy,delta,residue in itertools.product(range(-3,4),range(-3,4),range(-3,4),(0,4)):
 reset(expanded);grid=bytearray(bytes((16,0))*256);grid[2*((6+dy)*16+6+dx)]=16+delta
 expanded.put(GRID,grid);expanded.put(0x02007f10,header);expanded.put(STACK+residue,struct.pack('<4I',6+dy,350,379,0))
 want=int(abs(dx)+abs(dy)<=2 and (abs(delta)<=2 or (dx,dy)==(0,0)))
 check('murasame_center_range_and_height',expanded.call(0x080a0014,UNIT,6,6,6+dx,stack=STACK+residue),want)
for action,packed,seed in itertools.product((350,351),(1,5,13),(0,1)):
 reset(expanded,action,packed);expanded.put(TARGET+0x18,struct.pack('<HHHH',100,250,49,49));expanded.put(0x030034b0,struct.pack('<I',seed))
 before=expanded.read(0x02000000,0x40000)
 expanded.call(0x080a433c,regs[0],WRAPPER,5 if action==350 else 4,14,stack=regs[13]);r=expanded.read(0x02000000,0x40000)
 hp=struct.unpack_from('<H',r,0x33fc)[0];mp=struct.unpack_from('<H',r,0x9c)[0]
 if action==350:
  expected=100+min(150,8750*(5 if packed&6 else 4)//400)
  check('actual_murasame_heal',(packed,seed,hp),(packed,seed,expected));check('murasame_consumption',r[0x1e98],1)
 else:
  check('kiyomori_hp_unchanged',hp,100);check('kiyomori_does_not_consume',r[0x1e98],packed)
  for unit in (0x80,0x33e4):check('native_protect_shell',(r[unit+0xeb]&3,r[unit+0xdd],r[unit+0xde]),(3,3,3))
 check('one_action_payment',mp,42 if action==350 else 40)
 check('inventory_ap_preserved',r[0x1940:0x1e70]==before[0x1940:0x1e70],True)
 outcomes.append(dict(action=action,state=packed,seed=seed,targetHP=hp,actorMP=mp))
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(counts),total=sum(counts.values()),outcomes=outcomes,scope='Rational healing caps/all packed states, original selector25, all461 primary items and complete native two-ally execution; UI/geometry/status edge cases still separate')
(OUT/'restoration-native-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
