"""Native Dark Mind execution, admission, costs and unchanged shared donors."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/arm-python'));sys.path.insert(0,str(ROOT/'scripts'))
from unicorn import *
from unicorn.arm_const import *
P=ROOT/'build/expansion/probes';meta=_load_job_candidate(P/'dark-knight/current.json')
OUT=pathlib.Path(meta['path']).parent;rom=pathlib.Path(meta['path']).read_bytes();base=(OUT/'input.gba').read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
fix=OUT/'executor'
proof=json.loads((fix/'manifest.json').read_text());assert proof['passed'] and proof['romSha1']==meta['romSha1'] and proof['heapEnd']==meta['heapEnd']
ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes()
regs=struct.unpack_from('<17I',(fix/'execute-trap.state').read_bytes(),0x20)
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
TARGET=0x020033e4;CTX=0x0200f3f0
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
from native_battle_wrappers import from_memory
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()}
WRAPPER=wrappers[UNIT];old,new=ARM(base,iw),ARM(rom,iw);checks=collections.Counter();outcomes=[]
trace=[]
def observe(u,address,size,user):
 if address in (meta['symbols']['ffta_drk_eligibility'],meta['symbols']['ffta_drk_healing']):
  context=u.reg_read(UC_ARM_REG_R0)
  a,t=struct.unpack('<II',u.mem_read(context,8))
  trace.append(dict(entry=hex(address),actor=hex(a),target=hex(t),action=struct.unpack('<H',u.mem_read(context+12,2))[0]))
def check(kind,got,want):
 checks[kind]+=1
 assert got==want,(kind,got if not isinstance(got,bytes) else 'bytes differ',want if not isinstance(want,bytes) else len(want))
def reset(m,action=359,job=117,race=1,hp=50,maximum=200,mp=50,weapon=0,status=0,seed=0):
 m.put(0x02000000,ram);m.put(0x03000000,iw)
 m.put(UNIT+5,bytes((job,race,job)));m.put(UNIT+0x35,bytes((job,)))
 m.put(UNIT+0x3a,bytes(2));m.put(UNIT+0xe8,struct.pack('<Q',status))
 m.put(UNIT+0x18,struct.pack('<HHHH',hp,maximum,mp,50));m.put(UNIT+0x2a,struct.pack('<5H',weapon,0,0,0,0))
 m.put(UNIT+0xf6,bytes((4,14)));m.put(WRAPPER,struct.pack('<I',UNIT))
 m.put(WRAPPER+8,struct.pack('<H',4<<5));m.put(WRAPPER+12,struct.pack('<H',14<<5))
 m.put(0x02001e98,bytes(36));m.put(0x0203ff44,bytes(8));m.put(0x030034b0,struct.pack('<I',seed))
 context=bytearray(0x34);struct.pack_into('<IIIHH',context,0,UNIT,UNIT,UNIT,action,0)
 struct.pack_into('<I',context,0x30,0x08553e70+90*4);m.put(CTX,context)
 m.put(regs[13],struct.pack('<4I',action,0,0,255))
for maximum,residue in itertools.product((1,2,4,5,6,199,200,499,500,501,999,65535),(0,4)):
 for hp in sorted({0,1,maximum,max(1,maximum-1),maximum+1}):
  if hp>65535:continue
  reset(new,hp=hp,maximum=maximum)
  before=new.read(0x02000000,0x40000)
  want=min(maximum-hp,maximum//5,100) if hp and hp<maximum else 0
  check('independent_heal_caps',new.call(meta['symbols']['ffta_drk_healing_entry'],CTX,stack=STACK+residue),want)
  check('query_read_only',new.read(0x02000000,0x40000),before)
for job,race in ((117,1),(119,2),(2,1),(16,2)):
 for weapon in range(461):
  reset(new,job=job,race=race,weapon=weapon)
  check('weapon_free_in_both_races_and_other_jobs',new.call(meta['symbols']['ffta_drk_eligibility_entry'],CTX),1)
for target,hp,confused in itertools.product((UNIT,TARGET),(0,50),(0,1)):
 reset(new,hp=hp,status=(1<<28) if confused else 0);new.put(CTX+4,struct.pack('<I',target))
 check('self_alive_unconfused',new.call(meta['symbols']['ffta_drk_eligibility_entry'],CTX),int(target==UNIT and hp>0 and not confused))
for action in list(range(347))+list(range(347,356))+[357,358,424,425,426,427,428,429,430,431]:
 for m in (old,new):reset(m,action=action,weapon=383)
 for offset,key in ((0x3a8604+8*4,'eligibility'),(0x3a86f8+25*4,'healing')):
  a=struct.unpack_from('<I',base,offset)[0];b=struct.unpack_from('<I',rom,offset)[0]
  check('unchanged_'+key+'_donor_dispatch',new.call(b,CTX),old.call(a,CTX))
for silenced,residue in itertools.product((0,1),(0,4)):
 reset(new,status=(1<<27) if silenced else 0)
 check('usable_while_silenced',new.call(0x08133e18,UNIT,359,255,stack=STACK+residue),1)
 check('not_reflect',new.call(0x080ccd50,359,18),0)
 check('not_doublecast',new.call(0x080ccd50,359,19),0)
 check('no_return_magic',new.call(0x0812e6e0,UNIT,TARGET,359,11,stack=STACK+residue),0)
for job,race,hp,maximum,seed in itertools.product((117,119),(1,2),(1,50,195),(200,999),(0,3)):
 if (job,race) not in ((117,1),(119,2)):continue
 reset(new,job=job,race=race,hp=hp,maximum=maximum,seed=seed)
 before=new.read(0x02000000,0x40000)
 trace.clear();hook=new.u.hook_add(UC_HOOK_CODE,observe)
 new.call(0x080a433c,regs[0],WRAPPER,4,14,stack=regs[13])
 new.u.hook_del(hook);(OUT/'dark-mind-callback-trace.json').write_text(json.dumps(trace,indent=2))
 after=new.read(0x02000000,0x40000)
 check('executor_actual_hp',struct.unpack_from('<H',after,0x98)[0],hp+min(maximum-hp,maximum//5,100))
 check('executor_one_native_mp_payment',struct.unpack_from('<H',after,0x9c)[0],42)
 check('executor_native_shell_and_timer',(after[0x16b]&1,after[0x15d]),(1,3))
 check('inventory_ap_unchanged',after[0x1940:0x1e70],before[0x1940:0x1e70])
 check('enemy_unit_unchanged',after[0x33e4:0x34ec],before[0x33e4:0x34ec])
 outcomes.append(dict(job=job,race=race,hp=hp,maximum=maximum,seed=seed,finalHP=struct.unpack_from('<H',after,0x98)[0]))
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,
 scope='Dark Mind native callbacks and complete native executor; in-game UI, laws and cold save separate')
(OUT/'dark-mind-native.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
