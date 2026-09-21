"""Moon Blossom native damage results, Regen admission and one grant per action."""
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text());OUT=pathlib.Path(meta['path']).parent;rom=pathlib.Path(meta['path']).read_bytes();base=(OUT/'input.gba').read_bytes();symbols=meta['symbols'];assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
fix=ROOT/'build/expansion/probes/samurai-state'/meta['baseSha1'];ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes();regs=struct.unpack_from('<17I',(fix/'execute-trap.state').read_bytes(),0x20)
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000;TARGET=0x020033e4;CTX=0x0200f3f0
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m,n=ARM(rom,iw),ARM(base,iw);counts=collections.Counter();outcomes=[];grants=[]
def check(kind,a,b):counts[kind]+=1;assert a==b,(kind,a,b)
from native_battle_wrappers import from_memory
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()}
WRAPPER=wrappers[UNIT]

def reset(machine,packed=5):
 machine.put(0x02000000,ram);machine.put(0x03000000,iw)
 for unit in (UNIT,TARGET):machine.put(unit+0xe8,bytes(8));machine.put(unit+0x3a,bytes(2))
 machine.put(UNIT+5,bytes((116,1,116)));machine.put(UNIT+0x35,b'\x74');machine.put(UNIT+0x2a,struct.pack('<5H',383,0,0,0,0));machine.put(UNIT+0x18,struct.pack('<HHHH',100,100,50,50));machine.put(TARGET+0x18,struct.pack('<HHHH',250,250,50,50))
 machine.put(UNIT+0xf6,bytes((4,14)));machine.put(WRAPPER+8,struct.pack('<3H',4*32+16,32,14*32+16));machine.put(0x02001e98,bytes([packed])+bytes(35));machine.put(regs[13],struct.pack('<4I',354,0,0,255))
def grant_count(u,address,size,data):grants.append(u.reg_read(UC_ARM_REG_R0))
m.u.hook_add(UC_HOOK_CODE,grant_count,begin=symbols['ffta_samurai_regen'],end=symbols['ffta_samurai_regen'])
# Differential against the actual original native Regen stage.
for status,residue in itertools.product(range(-1,44),(0,4)):
 for machine in (m,n):
  reset(machine);machine.put(UNIT+0xe8,struct.pack('<Q',0 if status<0 else 1<<status))
  context=bytearray(0x34);struct.pack_into('<IIIHH',context,0,TARGET,UNIT,UNIT,1,0);struct.pack_into('<I',context,0x30,0x08553e70+195*4);machine.put(CTX,context)
 n.call(0x0813388c,stack=STACK+residue);m.call(symbols['ffta_samurai_regen'],UNIT,stack=STACK+residue)
 check('native_regen_complete_unit',m.read(UNIT,264),n.read(UNIT,264))
 check('regen_preserves_centered',m.read(0x02001e98,36),bytes([5])+bytes(35))
reset(m);bank=m.word(m.word(0x080cd538)+4)
reaction=next(i for i in range(144) if struct.unpack_from('<H',m.read(bank+8*i,8),4)[0]==13 and m.read(bank+8*i+6,1)==b'\x02')
check('native_damage_to_MP_assignment_exists',reaction>0,True)
plain=bytearray(rom);plain[0x1300e2:0x1300f2]=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()[0x1300e2:0x1300f2];reference=ARM(plain,iw)
for packed,seed,redirect,mp in itertools.product((1,5,13),range(8),(False,True),(0,50)):
 results=[]
 for machine in (reference,m):
  reset(machine,packed);machine.put(0x030034b0,struct.pack('<I',seed));machine.put(TARGET+0x1c,struct.pack('<HH',mp,50))
  if redirect:
   machine.put(TARGET+5,bytes((2,1,2)));machine.put(TARGET+0x35,b'\x02');machine.put(TARGET+0x3a,bytes([reaction]));machine.put(TARGET+0x40+reaction,b'\xff')
   check('native_damage_to_MP_equipped',machine.call(0x080cd4d4,TARGET),13)
  if machine is m:
   law=0x0203e000;machine.put(law,bytes((0,0,0,0,15,3,0,0,0,0,0,0)));machine.put(STACK,struct.pack('<4I',0,383,0,law))
   live_before=(machine.read(UNIT,264),machine.read(TARGET,264),machine.read(0x02001e98,36))
   predicted=machine.call(0x081343c8,UNIT,TARGET,354,0,stack=STACK)
   check('native_regen_law_respects_MP_redirect',predicted,int(not redirect or mp==0))
   check('law_no_live_mutation',(machine.read(UNIT,264),machine.read(TARGET,264),machine.read(0x02001e98,36)),live_before)
   # Native law evaluation samples RNG; the following execution has its own
   # fixed seed so its native-P comparison is independent of previewing.
   machine.put(0x030034b0,struct.pack('<I',seed))
  grants.clear();machine.call(0x080a433c,regs[0],WRAPPER,4,14,stack=regs[13]);r=machine.read(0x02000000,0x40000);results.append(r)
 ref,r=results;removed=250-struct.unpack_from('<H',r,0x33fc)[0];p=250-struct.unpack_from('<H',ref,0x33fc)[0]
 check('moon_native_P_one_round',removed,p*135*(5 if packed&6 else 4)//400)
 check('one_regen_on_actual_HP_damage',len(grants),int(removed>0))
 check('regen_matches_actual_HP_damage',bool(r[0x168]&8),removed>0)
 check('one_cost_and_centered',(struct.unpack_from('<H',r,0x9c)[0],r[0x1e98]),(34,1))
 check('AP_inventory_preserved',r[0x1940:0x1e70],ram[0x1940:0x1e70])
 outcomes.append(dict(packed=packed,seed=seed,redirect=redirect,MP=mp,removed=removed,regen=bool(r[0x168]&8),targetMP=struct.unpack_from('<H',r,0x3400)[0]))
check('positive_HP_coverage',any(o['removed']>0 for o in outcomes),True)
check('miss_coverage',any(not o['removed'] and not o['redirect'] for o in outcomes),True)
check('MP_redirect_coverage',any(o['redirect'] and o['MP']>o['targetMP'] and not o['removed'] for o in outcomes),True)
multi=[]
for seed in range(4):
 reset(m);grid=m.word(0x02007f14)
 for x,y in ((4,14),(5,14),(4,13),(4,15)):m.put(grid+2*(y*16+x),bytes((2,0)))
 for unit,wrapper,xy in ((TARGET,wrappers[TARGET],(5,14)),(0x020032dc,wrappers[0x020032dc],(4,13)),(0x020031d4,wrappers[0x020031d4],(4,15))):
  check('multi_wrapper_identity',m.word(wrapper),unit);m.put(unit+0x18,struct.pack('<HH',250,250));m.put(unit+0xf6,bytes(xy));m.put(unit+0xe8,bytes(8));m.put(unit+0x3a,bytes(2));m.put(wrapper+8,struct.pack('<3H',xy[0]*32+16,32,xy[1]*32+16))
 grants.clear();m.put(0x030034b0,struct.pack('<I',seed));m.call(0x080a433c,regs[0],WRAPPER,4,14,stack=regs[13])
 damaged=sum(int.from_bytes(m.read(u+0x18,2),'little')<250 for u in (TARGET,0x020032dc,0x020031d4));multi.append(damaged)
 check('one_grant_for_multiple_damaged_enemies',len(grants),int(damaged>0))
check('multiple_positive_recipients_exercised',max(multi)>1,True)
for status in range(-1,44):
 reset(n);n.put(UNIT+0xe8,struct.pack('<Q',0 if status<0 else 1<<status));old=n.read(UNIT,264)
 context=bytearray(0x34);struct.pack_into('<IIIHH',context,0,TARGET,UNIT,UNIT,1,0);struct.pack_into('<I',context,0x30,0x08553e70+195*4);n.put(CTX,context);n.call(0x0813388c);after=n.read(UNIT,264)
 for queried in range(44):
  reset(m);m.put(UNIT+0xe8,struct.pack('<Q',0 if status<0 else 1<<status))
  ca,ct=0x02022000,0x02022200;m.put(ca,m.read(UNIT,264));m.put(ct,m.read(TARGET,264));m.put(STACK,struct.pack('<II',queried,1))
  before_live=m.read(UNIT,264)+m.read(TARGET,264)+m.read(0x02001e98,36)
  # Native outer kind16 means harmful-status addition, not removal. Test
  # the real inner removal ABI on disposable actor/target evaluation copies.
  actual=m.call(0x081342cc,ca,ct,354,383,stack=STACK)
  bit=1<<(queried&7);offset=0xe8+(queried>>3)
  wanted=int(bool(old[offset]&bit) and not(after[offset]&bit) and status not in (6,28,29))
  check('moon_law_self_native_removal_mask',(status,queried,actual),(status,queried,wanted))
  check('moon_removal_law_live_isolation',m.read(UNIT,264)+m.read(TARGET,264)+m.read(0x02001e98,36),before_live)
# The extra damage prediction must preserve the native law RNG footprint.
control=bytearray(rom);off=symbols['ffta_samurai_law_hit']-0x08000000;control[off:off+4]=bytes.fromhex('00207047');law_control=ARM(control,iw)
for seed in range(8):
 states=[]
 for machine in (m,law_control):
  reset(machine);machine.put(0x030034b0,struct.pack('<I',seed));law=0x0203e000;machine.put(law,bytes((0,0,0,0,15,3,0,0,0,0,0,0)));machine.put(STACK,struct.pack('<4I',0,383,0,law));machine.call(0x081343c8,UNIT,TARGET,354,0,stack=STACK);states.append(machine.read(0x030034b0,4))
 check('no_extra_law_RNG_samples',states[0],states[1])
items=struct.unpack_from('<I',rom,0x130684)[0];original_effect=m.read(items+383*32+26,3)
for effect in (0,0x3d,0x3e,0x3f):
 reset(m);m.put(items+383*32+26,bytes((effect,0,0)));m.put(UNIT+0x18,struct.pack('<H',20));m.put(TARGET+0x18,struct.pack('<H',100));m.put(TARGET+0xea,b'\x10');m.put(TARGET+0xd9,b'\x11')
 grants.clear();m.put(0x030034b0,struct.pack('<I',1));m.call(0x080a433c,regs[0],WRAPPER,4,14,stack=regs[13]);hp=int.from_bytes(m.read(TARGET+0x18,2),'little')
 check('weapon_effects_do_not_drain_actor',int.from_bytes(m.read(UNIT+0x18,2),'little'),20)
 check('weapon_effects_do_not_remove_Doom',m.read(TARGET+0xea,1)[0]&0x10,0x10)
 check('Regen_only_on_HP_loss_with_weapon_effects',len(grants),int(hp<100))
 if effect==0x3f:check('restorative_weapon_healing_exercised',hp>100,True)
 m.put(items+383*32+26,original_effect)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(counts),total=sum(counts.values()),outcomes=outcomes,scope='Native Regen full-unit differential, actual damage/miss/MP interception and healing, Centered, native P, one grant for multiple enemies, proc/drain exclusion, added-status law and inner removal queries; UI separate')
(OUT/'moon-native-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
