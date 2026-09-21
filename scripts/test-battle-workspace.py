"""Owned battle pools: native allocation, bounded lookup, retirement and reuse."""
import ast,collections,hashlib,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
OUT=pathlib.Path(meta['path']).parent;rom=pathlib.Path(meta['path']).read_bytes();S=meta['symbols']
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
iw=(OUT/'executor/execute-trap.iwram').read_bytes();ram=(OUT/'executor/execute-trap.ram').read_bytes()
STACK,RETURN=0x03007000,0x08000100
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m=ARM(rom,iw);checks=collections.Counter();case=None;records=[]
def check(k,v):checks[k]+=1;assert v,(k,case)
def w(p,v):m.put(p,struct.pack('<I',v))
providers={'ffta_integrated_result_storage':(0x10,6592),'ffta_integrated_snapshot_storage':(0x19e0,2080),'ffta_additional_extension_snapshot_storage':(0x2210,1024)}
providers.update(doublecast=(0x2610,16),fight_laws=(0x2620,64))
def lookup(name):
 return m.call(S['ffta_battle_workspace'],providers[name][0]) if name in ('doublecast','fight_laws') else m.call(S[name])
def reset():m.put(0x02000000,ram);m.put(0x03000000,iw)
reset();manager=m.word(0x0200f4b0);pool=m.word(manager+0x438);assert pool
check('actual-captured-manager-native-allocation',m.call(0x0800717c,0,manager)==0x440)
check('global-heap-limit',meta['heapEnd']==0x0203f000)
for mutation in ('valid','owner-magic','unregistered','detached','copied-header','manager-capacity','manager-allocation','header-magic','header-self','pool-magic','pool-owner','pool-self','pool-allocation','heap-replaced','unaligned','out-of-bounds','retired'):
 case=('lookup',mutation);reset()
 if mutation=='owner-magic':w(0x0203ff30,0)
 if mutation=='unregistered':w(0x0203ff38,0)
 if mutation=='detached':w(0x0200f4b0,0)
 if mutation=='copied-header':
  other=0x02008000;m.put(other,m.read(manager,0x440));w(other+0x434,other);w(0x0200f4b0,other)
 if mutation=='header-magic':w(manager+0x430,0)
 if mutation=='header-self':w(manager+0x434,manager+4)
 if mutation=='manager-capacity':m.put(manager-6,struct.pack('<H',(0x430+12)//4))
 if mutation=='manager-allocation':m.put(manager-8,b'ps')
 if mutation=='pool-magic':w(pool,0)
 if mutation=='pool-owner':w(pool+4,manager+4)
 if mutation=='pool-self':w(pool+8,pool+4)
 if mutation=='pool-allocation':m.put(pool-8,b'ps')
 if mutation=='heap-replaced':w(0x0200f434,0)
 if mutation=='unaligned':w(0x0203ff38,manager+1);w(0x0200f4b0,manager+1)
 if mutation=='out-of-bounds':w(0x0203ff38,0x0203e000);w(0x0200f4b0,0x0203e000)
 if mutation=='retired':m.call(0x08007170,m.word(manager),manager)
 before=m.read(0x02000000,0x40000);rng=m.read(0x030034b0,4)
 for name,(off,size) in providers.items():check('only-exact-live-owned-pool',lookup(name)==(pool+off if mutation=='valid' else 0))
 check('prepare-never-repairs-foreign-state',m.call(S['ffta_additional_workspace_prepare'])==int(mutation=='valid'))
 check('lookup-pure-no-repair',m.read(0x02000000,0x40000)==before and m.read(0x030034b0,4)==rng)

# A shared-layer430-byte manager is a legitimate copy owner, but cannot own
# an integrated header. Reject it before even reading beyond its allocation.
reset();small=m.call(0x08022840,0x430);m.call(S['ffta_manager_register'],small);w(0x0200f4b0,small)
reads=[]
def outside(u,access,address,size,value,data):reads.append(address)
hook=m.u.hook_add(UC_HOOK_MEM_READ,outside,begin=small+0x430,end=small+0x43f)
for name in providers:check('standalone-manager-no-integrated-pool',lookup(name)==0)
check('standalone-manager-no-prepare',m.call(S['ffta_additional_workspace_prepare'])==0)
m.u.hook_del(hook);check('no-read-past-small-manager',not reads)

# Full parent and child constructors with fixed resource-size providers. Native
# allocation/clear/containers/registration execute; no workspace pointer injected.
for stack in (0x03007000,0x03006ffc):
 case=('native constructor',stack);m=ARM(rom,iw);m.put(0x02000000,bytes(0x40000))
 m.put(0x02001e70,b'FFTAEXP1\x01');m.call(S['ffta_job_reset'])
 heap=0x02018000;m.call(0x080070c8,heap,0x27000);w(0x0200f434,heap);initial=m.read(heap,20)
 for address,value in ((0x08022080,0x400),(0x0814913c,0x40),(0x08021a3c,0),(0x0814914c,0),(0x0808f79c,0),(0x081493c0,0)):
  def stub(u,a,n,data,value=value):u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  m.u.hook_add(UC_HOOK_CODE,stub,begin=address,end=address)
 aligned=[]
 def observe(u,a,n,data):aligned.append(u.reg_read(UC_ARM_REG_SP))
 m.u.hook_add(UC_HOOK_CODE,observe,begin=S['ffta_battle_workspace_register'],end=S['ffta_battle_workspace_register'])
 for iteration in range(4):
  m.call(0x08096ed4,stack=stack);manager=m.word(0x0200f4b0);parent=m.word(0x0200f4b8)
  parent_expected=((0x400+0x40+0x1668)&~31)+0x4c0
  check('native-parent-capacity-includes-workspace',m.call(0x0800717c,0,parent)==parent_expected)
  check('native-child-exact-capacity',m.call(0x0800717c,0,manager)==0x440)
  check('native-owner-registered',m.word(0x0203ff38)==manager)
  check('existing-copy-tail-clear',m.read(manager+0x3b4,122)==bytes(122))
  for name in providers:check('constructor-does-not-allocate-combat-pools',lookup(name)==0)
  if iteration==3:
   m.call(0x08022854,parent,stack=stack)
   check('unused-parent-retires-manager-owner',m.call(S['ffta_owned_battle_manager'])==0)
   check('unused-freed-parent-cannot-create-pool',m.call(S['ffta_additional_workspace_prepare'])==0)
   check('unused-parent-fully-reclaimed',m.read(heap,20)==initial)
   continue
  check('explicit-prepare-succeeds',m.call(S['ffta_additional_workspace_prepare'])==1)
  pool=m.word(manager+0x438)
  check('native-workspace-exact-capacity',m.call(0x0800717c,0,pool)==0x2660)
  before=m.read(0x02000000,0x40000)
  check('repeated-prepare-reuses-allocation',m.call(S['ffta_additional_workspace_prepare'])==1 and m.read(0x02000000,0x40000)==before)
  for name,(off,size) in providers.items():
   p=lookup(name);check('pool-exact-offset',p==pool+off)
   check('new-or-reused-pool-empty',m.read(p,size)==bytes(size));m.put(p,b'\x95'*size)
  records.append(dict(stack=stack,iteration=iteration,manager=manager,parent=parent,parentBytes=parent_expected))
  if iteration==1:
   m.call(0x08022854,pool,stack=stack)
   for name in providers:check('independent-pool-free-retires-workspace',lookup(name)==0)
   check('live-manager-can-reallocate-freed-pool',m.call(S['ffta_additional_workspace_prepare'])==1)
   for name,(off,size) in providers.items():check('reallocated-pool-empty',m.read(lookup(name),size)==bytes(size))
  if iteration!=2:
   m.call(0x08007170,m.word(manager),manager,stack=stack)
   for name in providers:check('native-free-retires-workspace',lookup(name)==0)
  m.call(0x08022854,parent,stack=stack)
  check('parent-free-retires-manager-owner',m.call(S['ffta_owned_battle_manager'])==0)
  check('freed-parent-cannot-recreate-workspace',m.call(S['ffta_additional_workspace_prepare'])==0)
  check('parent-and-children-fully-reclaimed',m.read(heap,20)==initial)
 check('both-incoming-stack-residues-align-C',len(aligned)==4 and all(not p%8 for p in aligned))

# Use the real allocator's unsplittable remainder branch for every legal slack
# size, rather than forging a supposedly allocated block's size field.
m.call(0x08096ed4);manager=m.word(0x0200f4b0);parent=m.word(0x0200f4b8)
for slack in (0,4,8,12):
 case=('native allocation slack',slack);tiny=0x02010000
 m.call(0x080070c8,tiny,0x2660+20+slack);w(0x0200f434,tiny);empty=m.read(tiny,20)
 check('unsplittable-allocation-prepare',m.call(S['ffta_additional_workspace_prepare'])==1)
 pool=m.word(manager+0x438)
 check('native-slack-capacity',m.call(0x0800717c,0,pool)==0x2660+slack)
 for name,(off,size) in providers.items():check('native-slack-pool-accepted',lookup(name)==pool+off)
 m.call(0x08022854,pool);check('native-slack-heap-reclaimed',m.read(tiny,20)==empty)
w(0x0200f434,heap);m.call(0x08022854,parent)
check('slack-owner-fully-retired',m.call(S['ffta_owned_battle_manager'])==0 and m.read(heap,20)==initial)

for start in (0x020159d0,0x0201f550,0x0200f3c4):
 for end in (0x0203f000,0x0203f400):
  case=('scene clear',start,end);reset()
  m.call(S['ffta_job_clear'],start,end-start)
  check('scene-clear-retires-copy-owners',m.read(0x0203ff30,20)==bytes(20))
  for name in providers:check('scene-clear-retires-workspace',lookup(name)==0)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),records=records)
(OUT/'battle-workspace.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
