"""Crushing Blow and Unholy Sacrifice: native damage then status, costs and queries."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools/arm-python'));sys.path.insert(0,str(ROOT/'scripts'))
from unicorn import *
from unicorn.arm_const import *
from native_battle_wrappers import from_memory
meta=_load_job_candidate(ROOT/'build/expansion/probes/dark-knight/current.json');ROM=pathlib.Path(meta['path']);OUT=ROM.parent;rom=ROM.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
fix=OUT/'executor';proof=json.loads((fix/'manifest.json').read_text());assert proof['romSha1']==meta['romSha1'] and proof['heapEnd']==meta['heapEnd']
ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes();regs=struct.unpack_from('<17I',(fix/'execute-trap.state').read_bytes(),0x20)
UNIT,TARGET,EQUIPMENT,RETURN,STACK,CTX=0x02000080,0x020033e4,0x02002000,0x08000100,0x03006800,0x0200f3f0
S=meta['symbols'];allS={**meta['priorSymbols'],**S}
exec(compile(ast.Module(body=[n for n in ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000')).body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
raw=bytearray(rom);p=S['ffta_physical_final']-0x08000000;raw[p:p+2]=bytes.fromhex('7047')
m,n=ARM(rom,iw),ARM(raw,iw);checks=collections.Counter();outcomes=[];stages=[]
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()}
def half(machine,p):return int.from_bytes(machine.read(p,2),'little')
def check(k,a,b):
 checks[k]+=1
 if a!=b:
  if isinstance(a,bytes):
   (OUT/'failure-actual.ram').write_bytes(a);(OUT/'failure-expected.ram').write_bytes(b);a=[(i,x,y) for i,(x,y) in enumerate(zip(a,b)) if x!=y][:20];b='equal bytes'
  (OUT/'sword-riders-failure.json').write_text(json.dumps(dict(check=k,actual=a,expected=b,stages=stages,outcomes=outcomes[-4:]),indent=2))
  raise AssertionError((k,a,b))
def reset(machine,action=361,job=117,race=1,seed=0,reaction=0,friend=False):
 machine.put(0x02000000,ram);machine.put(0x03000000,iw);machine.put(0x0203ff44,bytes(8));machine.put(0x02001e98,bytes(108))
 for unit,x in ((UNIT,4),(TARGET,5)):
  machine.put(unit+5,bytes((job,race,job)));machine.put(unit+0x3a,bytes(2));machine.put(unit+0xe8,bytes(8));machine.put(unit+0x18,struct.pack('<4H',500,500,99,99));machine.put(unit+0x2a,struct.pack('<5H',384,0,0,0,0));machine.put(unit+0xf6,bytes((x,14)));machine.put(wrappers[unit]+8,struct.pack('<3H',x*32+16,32,14*32+16))
 machine.put(TARGET+5,bytes((116,1,116)))
 machine.put(TARGET+0x29,bytes((machine.read(UNIT+0x29,1)[0] if friend else machine.read(UNIT+0x29,1)[0]^128,)))
 if reaction:
  bank=machine.word(machine.word(0x080cd538)+4);lesson=next(i for i in range(144) if struct.unpack_from('<H',machine.read(bank+8*i,8),4)[0]==reaction and machine.read(bank+8*i+6,1)[0]==2)
  machine.put(TARGET+0x3a,bytes([lesson]));machine.put(TARGET+0x40+lesson,b'\xff')
 machine.put(0x030034b0,struct.pack('<I',seed));machine.put(regs[13],struct.pack('<4I',action,0,0,255))
 ctx=bytearray(0x34);struct.pack_into('<IIIHH',ctx,0,UNIT,TARGET,TARGET,action,0);struct.pack_into('<I',ctx,0x30,0x0922c000+63*4);machine.put(CTX,ctx)
def observe(u,pc,size,data):
 c=u.reg_read(UC_ARM_REG_R0);r=m.read(c,0x34);actor,target,recipient=struct.unpack_from('<III',r);root=m.word(0x0203ff48)
 scope=m.read(root,820) if root else bytes(820);count=struct.unpack_from('<I',scope,12)[0]
 records={a:h for a,f,h,claims in (struct.unpack_from('<IIHH',scope,20+12*i) for i in range(count))}
 stages.append(dict(action=struct.unpack_from('<H',r,12)[0],stage=r[0x28],flags=struct.unpack_from('<H',r,0x26)[0],actor=actor,target=target,recipient=recipient,hp=half(m,target+0x18),phase=struct.unpack_from('<I',scope,800)[0],loss=records.get(target,0)))
m.u.hook_add(UC_HOOK_CODE,observe,begin=S['ffta_drk_rider_eligible'],end=S['ffta_drk_rider_eligible'])
for action,job,race,reaction,seed in itertools.product((361,363),(117,119),(1,), (0,13),range(64)):
 race=1 if job==117 else 2;pair=[];stages=[]
 for machine in (n,m):
  reset(machine,action,job,race,seed,reaction)
  machine.call(0x080a433c,regs[0],wrappers[UNIT],4 if action==363 else 5,14,stack=regs[13])
  pair.append(dict(hp=half(machine,TARGET+0x18),mp=half(machine,TARGET+0x1c),actorHP=half(machine,UNIT+0x18),actorMP=half(machine,UNIT+0x1c),status=int.from_bytes(machine.read(TARGET+0xe8,8),'little')))
  check('transient_roots_retired',machine.read(0x0203ff44,8),bytes(8))
 ref=500-pair[0]['hp'];damage=500-pair[1]['hp'];bit=23 if action==361 else 22
 check('native_P_coefficient',(action,damage),(action,ref*(115 if action==361 else 175)//100))
 check('actor_HP_paid_once',pair[1]['actorHP'],400 if action==363 else 500)
 check('actor_MP_paid_once',pair[1]['actorMP'],85 if action==363 else 89)
 if not damage:check('no_status_without_actual_HP',bool(pair[1]['status']&(1<<bit)),False)
 outcomes.append(dict(action=action,job=job,reaction=reaction,seed=seed,reference=ref,damage=damage,status=bool(pair[1]['status']&(1<<bit)),mp=pair[1]['mp'],stages=stages))
for action,job in itertools.product((361,363),(117,119)):
 rows=[r for r in outcomes if r['action']==action and r['job']==job]
 check('positive_damage_exercised',any(r['damage'] for r in rows),True)
 check('successful_status_exercised',any(r['status'] for r in rows),True)
 check('native_miss_exercised',any(not r['damage'] and r['reaction']==0 for r in rows),True)
 check('native_MP_only_exercised',any(r['reaction']==13 and r['mp']<99 and not r['damage'] for r in rows),True)
# The query gate predicts without consuming RNG, MP, status or live HP; the
# status rate uses native half-S26, preserving special forced100 interception.
for action,reaction,seed in itertools.product((361,363),(0,13),range(16)):
 reset(m,action,seed=seed,reaction=reaction);m.put(CTX+0x28,b'\x01');m.put(CTX+0x26,b'\x10\x00');m.put(CTX+0x30,struct.pack('<I',0x0922c000+(213 if action==361 else 214)*4))
 before=m.read(0x02000000,0x40000);rng=m.word(0x030034b0)
 eligible=m.call(S['ffta_drk_rider_eligible'],CTX,stack=STACK)
 check('query_rng_unchanged',m.word(0x030034b0),rng);check('query_live_state_unchanged',m.read(0x02000000,0x40000),before)
 if reaction:check('query_MP_interception_excluded',eligible,0)
 rate=m.call(0x08131220,CTX,stack=STACK);scaled=m.call(m.word(0x083a8678+26*4),CTX,stack=STACK);check('native_half_S_interception_preserved',scaled,rate if rate>=100 else rate//2)
# Explicit friendly-area admission and self exclusion for the cross.
for action,friend in itertools.product((361,363),(False,True)):
 reset(m,action,friend=friend);check('area_friendly_policy',m.call(S['ffta_drk_eligibility'],CTX,stack=STACK),int(action==363 or not friend))
 m.put(CTX+4,struct.pack('<II',UNIT,UNIT));check('self_never_damaged',m.call(S['ffta_drk_eligibility'],CTX,stack=STACK),0)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),outcomes=outcomes,scope=__doc__,limits=['Full native law, AI and fixed UI acceptance pending','Abyssal Blade falloff and four DRK passives pending'])
(OUT/'sword-riders.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='outcomes'},indent=2))
