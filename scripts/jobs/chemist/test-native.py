"""Native executor differential and independent approved medicine outcomes."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
from job_test_candidate import normalize_native_context,initialize_inactive_turn_domain
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT/'tools/arm-python'),str(ROOT/'scripts')]
from unicorn import *
from unicorn.arm_const import *
P=ROOT/'build/expansion/probes';meta=_load_job_candidate(P/'chemist/current.json');OUT=pathlib.Path(meta['path']).parent
rom=pathlib.Path(meta['path']).read_bytes();base=(OUT/'input.gba').read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
up=meta['upstream'];fix=OUT/'executor';ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes();regs=struct.unpack_from('<17I',(fix/'execute-trap.state').read_bytes(),0x20)
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000;TARGET=0x020033e4;CTX=0x0200f3f0
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
from native_battle_wrappers import from_memory
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()};WRAPPER=wrappers[UNIT]
native,expanded=ARM(base,iw),ARM(rom,iw);counts=collections.Counter();samples=[]
payment_trace=[]
def trace(m,address,size,data):
 if address in (meta['symbols']['ffta_chemist_payment_gate'],meta['symbols']['ffta_chemist_consumption'],meta['symbols']['ffta_chemist_pay'],0x080ca9e8):
  payment_trace.append(dict(pc=hex(address),args=[m.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)],lr=hex(m.reg_read(UC_ARM_REG_LR)),hp=bytes(m.mem_read(TARGET+0x18,2)).hex(),ctx=bytes(m.mem_read(CTX,52)).hex()))
expanded.u.hook_add(UC_HOOK_CODE,trace)
def check(kind,a,b):
 counts[kind]+=1
 if isinstance(a,bytes) and isinstance(b,bytes) and a!=b:
  differences=[(hex(i),a[i],b[i]) for i in range(min(len(a),len(b))) if a[i]!=b[i]]
  raise AssertionError((kind,differences[:30],len(differences)))
 assert a==b,(kind,a,b)
def load(m):
 m.put(0x02000000,ram);m.put(0x03000000,iw)
 # Original-action comparisons start with the new movement domain inactive
 # in both images; every output byte remains compared.
 if 'ffta_turn_event' in meta['symbols']:
  initialize_inactive_turn_domain(m)
def normalized(m):
 return normalize_native_context(m.read(0x02000000,0x40000),rom,base)
# Break423 is now a Mystic command in the integrated image, covered by its
# own native matrix; independent Chemist builds still compare the empty row.
unchanged=list(range(356))+[357,358,424,425,426,427,428,429,430,431]
if "ffta_myk_magnitude" not in meta["symbols"]:unchanged.append(423)
for action in unchanged:
 for m in (native,expanded):load(m);m.put(regs[13],struct.pack('<I',action));m.call(0x080a433c,*regs[:4],stack=regs[13])
 check('all-native-and-accepted-executors',normalized(expanded),normalized(native))
def reset(m,action,selected=0,pharmacology=False,hp=1,maximum=300):
 load(m)
 m.put(UNIT+5,bytes([120,3,120]));m.put(UNIT+0x35,b'\x78');m.put(UNIT+0x3a,bytes(2));m.put(UNIT+0x2a,bytes(10));m.put(UNIT+0xe8,bytes(8))
 m.put(UNIT+0x18,struct.pack('<4H',100,100,50,50));m.put(UNIT+0xf6,bytes([4,14]));m.put(WRAPPER+8,struct.pack('<H',4<<5));m.put(WRAPPER+12,struct.pack('<H',14<<5))
 if pharmacology:
  registry=json.loads((ROOT/'build/expansion/registry.json').read_text());lesson=next(l for l in registry['lessons'] if l['id']=='CHM-S1');owner=next(o for o in lesson['owners'] if o['race']==3);m.put(UNIT+0x3b,bytes([owner['abilityIndex']]))
 m.put(TARGET+0xe8,bytes(8));m.put(TARGET+0x18,struct.pack('<4H',hp,maximum,1,300));m.put(TARGET+0x28,struct.pack('<H',struct.unpack_from('<H',ram,0x33e4+0x28)[0]&0x7fff))
 m.put(0x02001940+362,bytes([5])*14);m.put(regs[13],struct.pack('<4I',action,selected,0,255));m.put(0x030034b0,bytes(4))
def execute(m,residue=None):
 if residue is None:sp=regs[13]
 else:
  sp=regs[13]+((residue-regs[13])&7);m.put(sp,m.read(regs[13],16))
 m.call(0x080a433c,regs[0],WRAPPER,5,14,stack=sp);return m.read(0x02000000,0x40000)
for action,selected,amount,ingredients in [(383,0,25,[362]),(386,363,50,[363]),(386,364,150,[364]),(387,0,60,[362,363]),(388,0,80,[365])]:
 for boosted in (False,True):
  reset(expanded,action,selected,boosted);payment_trace.clear();r=execute(expanded);offset=0x3400 if action==388 else 0x33fc
  (OUT/'payment-trace.json').write_text(json.dumps(payment_trace,indent=2))
  check('actual-native-recovery',struct.unpack_from('<H',r,offset)[0],1+amount*(3 if boosted else 2)//2)
  check('zero-MP-cost',struct.unpack_from('<H',r,0x9c)[0],50)
  check('exact-atomic-recipe',r[0x1940+362:0x1940+376],bytes(4 if i in ingredients else 5 for i in range(362,376)))
  samples.append(dict(action=action,selected=selected,pharmacology=boosted,HP=struct.unpack_from('<H',r,0x33fc)[0],MP=struct.unpack_from('<H',r,0x3400)[0]))
# Payment helper is independently exercised for all stock patterns, including
# zero first/second ingredient; rejected recipes must preserve every byte.
for action,selected,ingredients in [(383,0,[362]),(384,367,[367]),(384,368,[368]),(384,369,[369]),(384,371,[371]),(385,0,[375]),(386,363,[363]),(386,364,[364]),(387,0,[362,363]),(388,0,[365]),(389,0,[374]),(390,0,[364,375]),(391,0,[362,374]),(392,0,[362,371])]:
 for missing,residue in itertools.product([None]+ingredients,(0,4)):
  reset(expanded,action,selected)
  if missing:expanded.put(0x02001940+missing,b'\x00')
  before=expanded.read(0x02000000,0x40000);result=expanded.call(meta['symbols']['ffta_chemist_pay'],action,selected,stack=STACK+residue)
  check('recipe-admission',result,int(missing is None))
  if missing:check('recipe-failure-atomicity',expanded.read(0x02000000,0x40000),before)
for action,selected in ((384,0),(384,362),(384,374),(386,0),(386,362),(386,365)):
 reset(expanded,action,selected);before=expanded.read(0x02000000,0x40000)
 check('never-substitute-choice',expanded.call(meta['symbols']['ffta_chemist_pay'],action,selected),0)
 check('invalid-choice-preserves-inventory',expanded.read(0x02000000,0x40000),before)
for action,maximum,boost,residue in itertools.product((385,390),(1,2,399,400,401,999),(False,True),(0,4)):
 reset(expanded,action,pharmacology=boost,hp=0,maximum=maximum);r=execute(expanded,residue)
 check('native-revival-half-max-no-cap',struct.unpack_from('<H',r,0x33fc)[0],max(1,maximum//2))
 check('revival-no-MP-gain',struct.unpack_from('<H',r,0x3400)[0],1)
 check('revival-exact-cost',r[0x1940+362:0x1940+376],bytes(4 if i in ([375] if action==385 else [364,375]) else 5 for i in range(362,376)))
for selected,donor in ((367,261),(368,262),(369,257),(371,259),(374,264)):
 for status in range(44):
  action=389 if selected==374 else 384
  reset(expanded,action,selected);expanded.put(TARGET+0xe8,struct.pack('<Q',1<<status));before=expanded.read(TARGET,264);r=execute(expanded)
  reset(native,donor,selected);native.put(TARGET+0xe8,struct.pack('<Q',1<<status));reference=execute(native)
  if action==384 and status==12:
   check('Field-Remedy-not-a-reveal-action',r[0x33e4:0x34da],before[:0xf6]);check('Field-Remedy-no-useless-payment',r[0x1940+selected],5)
  else:check(f'selected-cure-native-status-effect-{selected}-{status}',r[0x33e4:0x34da],reference[0x33e4:0x34da])
# Public payment entry consumes only after execution-time selected-target
# validation. This fixture supplies the native frame, not a guessed live root.
frame=0x02027000
for selected,status in ((367,9),(368,10),(369,27),(371,6)):
 for residue in (0,4):
  reset(expanded,384,selected);expanded.put(TARGET+0xe8,struct.pack('<Q',1<<status));expanded.put(frame,bytes(0xb8));expanded.put(frame+0x44,struct.pack('<II',5,14))
  expanded.put(CTX,struct.pack('<IIIHH',UNIT,TARGET,TARGET,384,selected)+bytes(36))
  check('Field-preview-valid-before-status-change',expanded.call(meta['symbols']['ffta_chemist_eligibility'],CTX),1)
  expanded.put(TARGET+0xe8,bytes(8));before=expanded.read(0x02001940,0x530)
  check('Field-invalidated-before-payment',expanded.call(meta['symbols']['ffta_chemist_payment_gate'],UNIT,384,selected,frame,stack=STACK+residue),0)
  check('Field-invalidated-stock-preserved',expanded.read(0x02001940,0x530),before)
for action in range(383,393):
 reset(expanded,action,367 if action==384 else 363);expanded.put(TARGET+5,expanded.read(UNIT+5,3));before=expanded.read(0x02001940,0x530)
 check('enemy-active-medicine-cannot-pay',expanded.call(meta['symbols']['ffta_chemist_payment_gate'],TARGET,action,367 if action==384 else 363,frame),0)
 check('enemy-active-medicine-stock-preserved',expanded.read(0x02001940,0x530),before)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(counts),total=sum(counts.values()),samples=samples)
(OUT/'native-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
