"""Desperation threshold, native execution and rational-product rounding controls."""
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
raw=bytearray(rom);p=S['ffta_drk_outgoing_numerator']-0x08000000;raw[p:p+4]=bytes.fromhex('08207047')
unscaled=bytearray(raw);p=S['ffta_physical_final']-0x08000000;unscaled[p:p+2]=bytes.fromhex('7047')
m,n,q=ARM(rom,iw),ARM(raw,iw),ARM(unscaled,iw);checks=collections.Counter();outcomes=[];stages=[]
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()}
def half(machine,p):return int.from_bytes(machine.read(p,2),'little')
paid_observations={id(machine):[] for machine in (m,n,q)}
def observe_paid(u,pc,size,machine):
 actor=u.reg_read(UC_ARM_REG_R0)
 if actor==UNIT:paid_observations[id(machine)].append(half(machine,actor+0x18))
for machine in (m,n,q):
 machine.u.hook_add(UC_HOOK_CODE,observe_paid,user_data=machine,begin=allS['ffta_action_paid'],end=allS['ffta_action_paid'])
def check(k,a,b):
 checks[k]+=1
 if a!=b:
  if isinstance(a,bytes):
   (OUT/'failure-actual.ram').write_bytes(a);(OUT/'failure-expected.ram').write_bytes(b);a=[(i,x,y) for i,(x,y) in enumerate(zip(a,b)) if x!=y][:20];b='equal bytes'
  (OUT/'desperation-failure.json').write_text(json.dumps(dict(check=k,actual=a,expected=b,stages=stages,outcomes=outcomes[-4:]),indent=2))
  raise AssertionError((k,a,b))
def reset(machine,action=361,job=117,race=1,seed=0,reaction=0,friend=False):
 paid_observations[id(machine)].clear()
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
def factors(u,pc,size,data):
 root=m.word(0x0203ff48);scope=m.read(root,820) if root else bytes(820);count=struct.unpack_from('<I',scope,12)[0]
 units={a:f for a,f,h,c in (struct.unpack_from('<IIHH',scope,20+12*i) for i in range(count))}
 actor,target,action=[u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
 stages.append(dict(factorAction=action,actor=actor,target=target,actorHP=half(m,actor+0x18),actorFlags=units.get(actor,0),targetFlags=units.get(target,0),phase=struct.unpack_from('<I',scope,800)[0],origin=struct.unpack_from('<I',scope,792)[0]))
m.u.hook_add(UC_HOOK_CODE,factors,begin=S['ffta_drk_outgoing_numerator'],end=S['ffta_drk_outgoing_numerator'])
def provider(u,pc,size,data):
 unit=u.reg_read(UC_ARM_REG_R0)
 stages.append(dict(provider=unit,HP=half(m,unit+0x18),support=m.read(unit+0x3b,1)[0],AP=m.read(0x02001b57,1)[0]))
m.u.hook_add(UC_HOOK_CODE,provider,begin=S['ffta_drk_snapshot_flags'],end=S['ffta_drk_snapshot_flags'])
# Native support lookup and complete execution, with the same exact native RNG.
for action,job,reaction,hp,seed in itertools.product((0,23,356,357,361,363),(117,119),(0,13),(175,176,225,226,275,276),range(4)):
 pair=[];stages=[];race=1 if job==117 else 2
 for machine in (q,n,m):
  reset(machine,action,job,race,seed,reaction)
  machine.put(UNIT+0x18,struct.pack('<H',hp));lesson=167 if race==1 else 86
  machine.put(UNIT+0x3b,bytes((lesson,)))
  machine.put((0x02001b40+lesson-144) if race==1 else UNIT+0x40+lesson,b'\xff')
  check('native_mastered_support',machine.call(0x080cd50c,UNIT,stack=STACK),130)
  check('direct_provider',machine.call(S['ffta_drk_snapshot_flags'],UNIT,stack=STACK),8192|(16384 if hp<=175 else 0))
  machine.call(0x080a433c,regs[0],wrappers[UNIT],4 if action==363 else 5,14,stack=regs[13])
  paid=paid_observations[id(machine)]
  check('one_native_payment_boundary',len(paid),0 if action==0 else 1)
  pair.append(dict(hp=half(machine,TARGET+0x18),mp=half(machine,TARGET+0x1c),actorHP=half(machine,UNIT+0x18),actorMP=half(machine,UNIT+0x1c),paidHP=paid[0] if paid else hp))
  check('roots_retired',machine.read(0x0203ff44,8),bytes(8))
 raw_p=500-pair[0]['hp'];ref=500-pair[1]['hp'];damage=500-pair[2]['hp'];cost=100 if action==363 else 50 if action==356 else 0
 active=hp-cost<=175
 coefficient={356:150,357:95,361:115,363:175}.get(action,100)
 expected=raw_p*coefficient*(3 if active else 2)//200 if action in (356,357,361,363) and not reaction else ref*(3 if active else 2)//2
 check('post_cost_threshold_damage',(action,damage),(action,min(500,expected)))
 check('MP_interception_unchanged',pair[2]['mp'],pair[1]['mp'])
 check('MP_price_unchanged',pair[2]['actorMP'],pair[1]['actorMP'])
 # Native area spells may hit their caster. Verify price at the actual paid
 # boundary instead of confusing later self/friendly-fire damage with a cost.
 check('no_added_HP_price',(pair[2]['paidHP'],pair[1]['paidHP']),(hp-cost,hp-cost))
 outcomes.append(dict(action=action,job=job,reaction=reaction,hp=hp,seed=seed,active=active,rawReference=raw_p,reference=ref,damage=damage))
# Pure preview predicts the explicit sacrifice; no live HP/MP or RNG changes.
for action,hp in itertools.product((0,23,356,363),(175,176,225,226,275,276)):
 reset(m,action);m.put(UNIT+0x18,struct.pack('<H',hp));m.put(UNIT+0x3b,b'\xa7');m.put(0x02001b57,b'\xff')
 before=m.read(0x02000000,0x40000);rng=m.word(0x030034b0)
 factor=m.call(S['ffta_drk_outgoing_numerator'],UNIT,TARGET,action,int(action!=23),stack=STACK)
 cost=100 if action==363 else 50 if action==356 else 0
 check('pure_preview_post_cost_factor',factor,12 if hp-cost<=175 else 8)
 check('pure_preview_EWRAM',m.read(0x02000000,0x40000),before);check('pure_preview_RNG',m.word(0x030034b0),rng)
for action in (0,23,356,357,361,363):
 rows=[r for r in outcomes if r['action']==action and not r['reaction']]
 check('positive_active_damage_coverage',any(r['active'] and r['damage']>r['reference'] for r in rows),True)
 check('inactive_native_damage_coverage',any(not r['active'] and r['damage']>0 for r in rows),True)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),outcomes=outcomes,
 limits=['Full legal secondary-command UI/AP and other-job lookup, reactions/fixed/item exclusions pending'])
(OUT/'desperation.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='outcomes'},indent=2))
