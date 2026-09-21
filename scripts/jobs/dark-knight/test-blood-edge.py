"""Blood Edge native price, admission and complete executor damage oracles."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
from job_test_candidate import normalize_native_context,initialize_inactive_turn_domain
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/arm-python'));sys.path.insert(0,str(ROOT/'scripts'))
from unicorn import *
from unicorn.arm_const import *
P=ROOT/'build/expansion/probes';meta=_load_job_candidate(P/'dark-knight/current.json')
OUT=pathlib.Path(meta['path']).parent;rom=pathlib.Path(meta['path']).read_bytes();base=(OUT/'input.gba').read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
fix=OUT/'executor'
proof=json.loads((fix/'manifest.json').read_text());assert proof['passed'] and proof['romSha1']==meta['romSha1'] and proof['heapEnd']==meta['heapEnd'];ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes()
regs=struct.unpack_from('<17I',(fix/'execute-trap.state').read_bytes(),0x20)
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
TARGET=0x020033e4;CTX=0x0200f3f0
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
from native_battle_wrappers import from_memory
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()};WRAPPER=wrappers[UNIT]
raw=bytearray(rom);address=meta['symbols']['ffta_physical_final']-0x08000000
raw[address:address+2]=bytes.fromhex('7047');reference,new=ARM(raw,iw),ARM(rom,iw)
checks=collections.Counter();outcomes=[]
def check(kind,got,want):checks[kind]+=1;assert got==want,(kind,got,want)
def reset(m,hp=100,maximum=200,seed=0,job=117,race=1):
 m.put(0x02000000,ram);m.put(0x03000000,iw)
 m.put(UNIT+5,bytes((job,race,job)));m.put(UNIT+0x35,bytes((job,)))
 m.put(UNIT+0x3a,bytes(2));m.put(UNIT+0xe8,bytes(8));m.put(TARGET+0xe8,bytes(8))
 m.put(UNIT+0x18,struct.pack('<HHHH',hp,maximum,50,50));m.put(TARGET+0x18,struct.pack('<HHHH',999,999,49,49))
 m.put(UNIT+0x2a,struct.pack('<5H',384,0,0,0,0));m.put(UNIT+0xf6,bytes((4,14)))
 m.put(WRAPPER,struct.pack('<I',UNIT));m.put(WRAPPER+8,struct.pack('<H',4<<5));m.put(WRAPPER+12,struct.pack('<H',14<<5))
 m.put(0x02001e98,bytes(36));m.put(0x0203ff44,bytes(8));m.put(0x030034b0,struct.pack('<I',seed))
 context=bytearray(0x34);struct.pack_into('<IIIHH',context,0,UNIT,TARGET,TARGET,356,0)
 struct.pack_into('<I',context,0x30,0x08553e70+63*4);m.put(CTX,context)
 m.put(regs[13],struct.pack('<4I',356,0,0,255))
for maximum,residue in itertools.product((1,2,9,10,11,199,200,201,999),(0,4)):
 cost=max(1,(maximum+9)//10)
 for hp in sorted({0,1,cost,cost+1,maximum}):
  reset(new,hp,maximum)
  check('round_up_hp_price',new.call(meta['symbols']['ffta_drk_hp_cost'],UNIT,356,stack=STACK+residue),cost)
  check('native_menu_price_gate',new.call(0x08133e18,UNIT,356,255,stack=STACK+residue),int(hp>cost))
  before=new.read(UNIT,264)
  admitted=new.call(meta['symbols']['ffta_drk_paid'],UNIT,356,stack=STACK+residue)
  check('commit_leaves_one_hp',admitted,int(hp>cost))
  check('exact_direct_hp_cost',struct.unpack('<H',new.read(UNIT+0x18,2))[0],hp-cost if hp>cost else hp)
  check('cost_never_touches_mp',new.read(UNIT+0x1c,4),before[0x1c:0x20])
for item in range(461):
 reset(new);new.put(UNIT+0x2a,struct.pack('<5H',item,0,0,0,0))
 category=new.call(0x080ca7a4,item,3)
 check('only_sword_greatsword_broadsword',new.call(meta['symbols']['ffta_drk_eligibility_entry'],CTX),int(item>0 and category in (1,5,6)))
for job,race in ((117,1),(119,2)):
 for seed,exposed in itertools.product(range(8),(0,1)):
  values=[]
  for m in (reference,new):
   reset(m,job=job,race=race,seed=seed);m.put(0x02001eb4,bytes((exposed,)))
   m.call(0x080a433c,regs[0],WRAPPER,5,14,stack=regs[13]);r=m.read(0x02000000,0x40000)
   values.append(999-struct.unpack_from('<H',r,0x33fc)[0])
   check('executor_sacrifice_once_even_miss',struct.unpack_from('<H',r,0x98)[0],80)
   check('executor_mp_unchanged',struct.unpack_from('<H',r,0x9c)[0],50)
  check('independent_native_P_one_round',values[1],min(999,values[0]*150*(6 if exposed else 5)//500))
  outcomes.append(dict(job=job,seed=seed,exposed=exposed,P=values[0],damage=values[1]))
for hp in (1,19,20):
 reset(new,hp=hp);before=new.read(TARGET,264)
 new.call(0x080a433c,regs[0],WRAPPER,5,14,stack=regs[13])
 check('unaffordable_no_hp_debit',struct.unpack('<H',new.read(UNIT+0x18,2))[0],hp)
 check('unaffordable_no_target_effect',new.read(TARGET,264),before)
reset(new)
check('native_dark_element',new.call(0x0812f8a4,UNIT,356,384),8)
check('native_zero_mp_cost',new.call(0x0812ed98,UNIT,356),0)
# Native selector geometry receives explicit evaluated Move coordinates.
GRID=0x02026000
for dx,dy,height,residue in itertools.product(range(-2,3),range(-2,3),range(-4,5),(0,4)):
 reset(new);grid=bytearray(bytes((16,0))*256);grid[2*((6+dy)*16+6+dx)]=16+height
 new.put(GRID,grid);header=bytearray(16);struct.pack_into('<I',header,4,GRID);header[8]=header[13]=header[15]=16;new.put(0x02007f10,header)
 new.put(STACK+residue,struct.pack('<4I',6+dy,356,384,0))
 got=new.call(0x080a0014,UNIT,6,6,6+dx,stack=STACK+residue)
 check('evaluated_range_height',got,int(abs(dx)+abs(dy)==1 and abs(height)<=2))
for first,second in ((384,376),(376,384),(0,384),(460,384),(384,0)):
 reset(new);new.put(UNIT+0x2a,struct.pack('<5H',first,second,0,0,0));new.put(EQUIPMENT,b'\xa5'*8)
 count=new.call(meta['symbols']['ffta_drk_law_weapons'],UNIT,EQUIPMENT,356)
 primary=first or second
 check('law_only_actual_primary',count,1)
 check('law_no_unused_offhand',struct.unpack('<H',new.read(EQUIPMENT,2))[0],primary)
# Exact complete native executor preservation for every previously enabled
# action; this also covers the replaced admission/payment/element/proc hooks.
old=ARM(base,iw)
for action in list(range(356))+[357,358,424,425,426,427,428,429,430,431]:
 results=[]
 for m in (old,new):
  m.put(0x02000000,ram);m.put(0x03000000,iw);m.put(regs[13],struct.pack('<I',action))
  # Match inactive new-domain inputs, never mask differing output bytes.
  if 'ffta_turn_event' in meta['symbols']:
   initialize_inactive_turn_domain(m)
  m.call(0x080a433c,*regs[:4],stack=regs[13]);results.append(m.read(0x02000000,0x40000))
 # Only the documented descriptor-pointer relocation is representation, not
 # behavior: require the exact same index and byte-identical native descriptor.
 results=[normalize_native_context(result,rom,base) for result in results]
 if results[0]!=results[1]:
  (OUT/'prior-diff.json').write_text(json.dumps(dict(action=action,differences=[(i,a,b) for i,(a,b) in enumerate(zip(*results)) if a!=b][:40]),indent=2))
 check('previous_actions_full_executor_preserved',results[0]==results[1],True)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),outcomes=outcomes)
(OUT/'blood-edge-native.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
