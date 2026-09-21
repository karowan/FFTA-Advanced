"""Automatic item admission and installed native ailment interception.
Phase fixtures exercise the public context API; native callbacks remain real.
"""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools/arm-python'));sys.path.insert(0,str(ROOT/'scripts'))
from unicorn import *
from unicorn.arm_const import *
P=ROOT/'build/expansion/probes';meta=_load_job_candidate(P/'chemist/current.json');OUT=pathlib.Path(meta['path']).parent
rom=pathlib.Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
fix=OUT/'executor';ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes()
UNIT,TARGET,RETURN,STACK=0x020033e4,0x02000080,0x08000100,0x03006800
scope=0x03007400;CTX=0x0200f3f0;stock=0x02001940+374
exec(compile(ast.Module(body=[n for n in ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000')).body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m=ARM(rom,iw);S={**meta['upstream']['symbols'],**meta['symbols']};counts=collections.Counter();registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
def check(k,a,b):counts[k]+=1;assert a==b,(k,a,b)
def call(n,*args,residue=0):return m.call(S[n],*args,stack=STACK+residue)
def reset(status=None,stocked=3,reaction='CHM-R2',race=3):
 m.put(0x02000000,ram);m.put(0x03000000,iw);m.put(0x0203ff48,bytes(4));call('ffta_job_reset')
 for u,side in ((UNIT,128),(TARGET,0)):
  m.put(u+0xe8,bytes(8));m.put(u+0x18,struct.pack('<4H',100,300,20,50));m.put(u+0x28,bytes([0,side]));m.put(u+0x3a,bytes(2));m.put(u+0x2a,bytes(10))
 m.put(TARGET+5,bytes([120 if race==3 else 122,race,120 if race==3 else 122]))
 lesson=next(l for l in registry['lessons'] if l['id']==reaction);index=next(o['abilityIndex'] for o in lesson['owners'] if o['race']==race)
 m.put(TARGET+0x3a,bytes([index]));m.put(TARGET+0x40+index,b'\xff')
 check('native-equipped-reaction',m.call(0x080cd4d4,TARGET),137 if reaction=='CHM-R2' else 136)
 if status is not None:m.put(TARGET+0xe8,struct.pack('<Q',1<<status))
 m.put(stock,bytes([stocked]));m.put(CTX,struct.pack('<IIIHH',UNIT,TARGET,TARGET,64,0)+bytes(36))
def begin(phase=2,origin=1,enabled=1):
 check('native-snapshot-begin',call('ffta_snapshot_begin',scope,UNIT,TARGET,1),1)
 call('ffta_action_started',UNIT,64,origin,2)
 # Declared API-phase fixture, not a gameplay result override.
 m.put(scope+800,struct.pack('<I',phase));m.put(scope+16,struct.pack('<I',enabled))
for status,race,reaction,residue in itertools.product([None]+list(range(44)),(3,5),('CHM-R1','CHM-R2'),(0,4)):
 reset(status,reaction=reaction,race=race)
 expected=int(status not in (0,6,31,32,43))
 check('all-existing-status-admission',call('ffta_chemist_reaction_admission',TARGET,residue=residue),expected)
 check('snapshot-provider-flags',call('ffta_chemist_snapshot_flags',TARGET,residue=residue),expected*(1<<(12 if reaction=='CHM-R1' else 11)))
 m.put(TARGET+0x18,bytes(2));check('KO-admission',call('ffta_chemist_snapshot_flags',TARGET,residue=residue),0)
for status,phase,origin,enabled,qty,residue in itertools.product((None,6,26),(0,1,2,3),(0,1,2,3),(0,1),(0,2),(0,4)):
 reset(status,qty);begin(phase,origin,enabled);before=m.read(stock,1);rng=m.read(0x030034b0,4)
 expected=int(status!=6 and qty and (phase==0 or (phase==2 and origin and enabled)))
 check('exact-query-result-permission',call('ffta_chemist_prevent_native',CTX,9,residue=residue),expected)
 spent=int(expected and phase==2)
 check('consume-only-authenticated-result',m.read(stock,1),bytes([qty-spent]));check('prevention-no-RNG',m.read(0x030034b0,4),rng)
 check('claim-only-after-consumption',call('ffta_action_claimed',TARGET,1),spent)
# Native setters: first successful incoming Petrify/Sleep is intercepted based
# on the pre-action snapshot. Later components retain the paid action latch.
for effect,status,residue in itertools.product((46,45,61),(6,26),(0,4)):
 reset();begin()
 fn=struct.unpack_from('<I',rom,0x1291000+effect*12)[0]
 m.call(fn,CTX,stack=STACK+residue)
 check('incoming-ailment-snapshot-consumes',m.read(stock,1),b'\x02')
 check('native-ailment-record-suppressed',m.read(CTX+16,8),bytes(8))
 call('ffta_chemist_prevent_custom',CTX,2,residue=residue);check('one-item-whole-action',m.read(stock,1),b'\x02')
# Inoculation prevents first and never acquires the Auto-Cureall claim.
for residue in (0,4):
 reset();begin();call('ffta_inoculated_grant',TARGET,0)
 check('Inoculated-first',call('ffta_chemist_prevent_native',CTX,9,residue=residue),1)
 check('Inoculated-no-item',m.read(stock,1),b'\x03');check('Inoculated-no-claim',call('ffta_action_claimed',TARGET,1),0)
 for status in (12,20,22,0,31):check('uncurable-not-intercepted',call('ffta_chemist_prevent_native',CTX,status,residue=residue),0)
# Explicit origin and hostility are separate axes. Hostile party members may
# use their stock; true enemy/foreign records must never consume player items.
for foreign in (UNIT,0x02028000):
 reset();m.put(foreign,m.read(TARGET,264));m.put(foreign+0x28,bytes(2));m.put(TARGET+0x28,b'\0\x80');m.put(UNIT+0x28,b'\0\x80')
 if foreign==UNIT:
  actor=TARGET;m.put(actor+0x28,b'\0\x80')
 else:actor=UNIT
 call('ffta_snapshot_begin',scope,actor,foreign,1);call('ffta_action_started',actor,64,1,2);m.put(scope+800,struct.pack('<I',2));m.put(CTX,struct.pack('<IIIHH',actor,foreign,foreign,64,0)+bytes(36))
 check('enemy-or-foreign-cannot-spend-player-stock',call('ffta_chemist_prevent_native',CTX,9),0);check('enemy-or-foreign-stock-unchanged',m.read(stock,1),b'\x03')
# Complete native primary spell execution; successful controls determine only
# whether the native accuracy succeeded, never replace a computed game result.
from native_battle_wrappers import from_memory
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()}
regs=struct.unpack_from('<17I',(fix/'execute-trap.state').read_bytes(),0x20)
n=ARM(rom,iw);native_success=collections.Counter()
def execute_spell(machine,action,seed,reaction):
 machine.put(0x02000000,ram);machine.put(0x03000000,iw)
 for unit in (UNIT,TARGET):
  machine.put(unit+0xe8,bytes(8));machine.put(unit+0x18,struct.pack('<4H',100,300,999,999));machine.put(unit+0x2a,bytes(10));machine.put(unit+0x3a,bytes(2))
 machine.put(UNIT+0x28,b'\0\x80');machine.put(TARGET+0x28,bytes(2))
 machine.put(TARGET+5,bytes([120,3,120]));machine.put(TARGET+0x35,b'\x78')
 if reaction:
  l=next(l for l in registry['lessons'] if l['id']=='CHM-R2');index=next(o['abilityIndex'] for o in l['owners'] if o['race']==3);machine.put(TARGET+0x3a,bytes([index]));machine.put(TARGET+0x40+index,b'\xff')
 machine.put(stock,b'\x05');machine.put(0x030034b0,struct.pack('<I',seed));machine.put(regs[13],struct.pack('<4I',action,0,0,255))
 xy=machine.read(TARGET+0xf6,2)
 machine.call(0x080a433c,regs[0],wrappers[UNIT],*xy,stack=regs[13])
 return machine.read(TARGET+0xe8,8)
for action,status,seed in itertools.product((14,32,64),(None,),range(32)):
 status={14:6,32:26,64:9}[action]
 original=execute_spell(n,action,seed,False);actual=execute_spell(m,action,seed,True)
 succeeded=bool(int.from_bytes(original,'little')&(1<<status));native_success[action]+=int(succeeded)
 check('whole-native-spell-prevents-curable',int.from_bytes(actual,'little')&(1<<status),0)
 check('whole-native-spell-consumes-on-success-only',m.read(stock,1),bytes([5-int(succeeded)]))
 check('whole-native-spell-same-RNG',m.read(0x030034b0,4),n.read(0x030034b0,4))
 check('whole-native-spell-same-damage',m.read(TARGET+0x18,8),n.read(TARGET+0x18,8))
for action in (14,32,64):check('positive-native-accuracy-control',native_success[action]>0,True)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(counts),total=sum(counts.values()),scope='Public phase fixtures and installed native callbacks; full battle reaction presentation pending')
(OUT/'reactions-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
