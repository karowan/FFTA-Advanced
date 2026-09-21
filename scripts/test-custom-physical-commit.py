"""Frozen native commit-frame weapon-effect differential; no production edits."""
import ast,hashlib,json,pathlib,struct,sys,collections
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
OUT=ROOT/'build/expansion/probes/custom-physical-commit';OUT.mkdir(exist_ok=True)
P=ROOT/'build/expansion/probes'
rom=(P/'combat.gba').read_bytes();meta=json.loads((P/'combat.json').read_text())
if '--fell' in sys.argv:
 from fell_test_context import load_context
 private=load_context('--current' in sys.argv);rom=pathlib.Path(private['path']).read_bytes()
 meta={**meta,'romSha1':private['romSha1'],'actions':[*meta['actions'],431],
       'changes':[c for c in meta['changes'] if 'expected' in c and 'size' in c]}
 OUT=pathlib.Path(private['path']).parent/'weapon-effects';OUT.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha1(b).hexdigest()
assert sha(rom)==meta['romSha1'];CHOP=424
TOMA=CHOP+1;SHATTER,ARMOR=CHOP+3,CHOP+4
FACTORS={CHOP:11,TOMA:9,CHOP+2:9,SHATTER:10,ARMOR:10,CHOP+5:11,CHOP+6:11}
if '--fell' in sys.argv:FACTORS={431:18}
assert set(FACTORS).issubset(meta['actions']), 'Await dual-action build'
snapshot=P/'chop-preview-council/9f773e96fa6f98ceb9fc443ee96c56a8a64c4adc-break-exec-seed0'
ram=(snapshot/'after.ram').read_bytes();iwram=(snapshot/'after.iwram').read_bytes();state=(snapshot/'after.state').read_bytes()
old=bytearray((snapshot/'frozen.gba').read_bytes());old[0xa2e70:0xa2e72]=bytes.fromhex('4d46')
regs0=struct.unpack_from('<17I',state,0x20);ACTOR=0x02000080;TARGET=0x020033e4;OBJ=regs0[9];OLDSP=regs0[13]
assert struct.unpack_from('<H',ram,OBJ-0x02000000+16)[0]==CHOP
# The captured frame is at a native address before the ordinary executor.
# Data pointers it will consume must retain their original allocations/bytes.
for literal in (0xcd538,0xccd84,0x130684):
 assert rom[literal:literal+4]==old[literal:literal+4],hex(literal)
for ptr in struct.unpack_from('<II',ram,0xf41c):
 assert rom[ptr-0x08000000:ptr-0x08000000+4]==old[ptr-0x08000000:ptr-0x08000000+4]
base=bytearray(rom)
for change in meta['changes']:
 if 'expected' in change:base[change['offset']:change['offset']+change['size']]=bytes.fromhex(change['expected'])
for name,data in [('frozen.gba',rom),('native-control.gba',base),('frame.ram',ram),('frame.iwram',iwram),('frame.state',state)]:
 (OUT/name).write_bytes(data)
(OUT/'combat.json').write_text(json.dumps(meta,indent=2))
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
native,custom=ARM(bytes(base),iwram),ARM(rom,iwram)
items=struct.unpack_from('<I',rom,0x130684)[0]
R=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12,UC_ARM_REG_SP,UC_ARM_REG_LR]
checks=collections.Counter();failures=[];calls=0;positive=collections.Counter();examples=[]
for machine in (native,custom):
 machine.events=[];machine.writes=[];machine.modes=[];machine.selectors=[];machine.references=[]
 def code(u,pc,size,m):
  if pc in (0x080a25a2,0x080a29e8,0x080a2dc8,0x080a2e70,0x0812fe38,0x0813388c,0x08130688,0x0812e55c):
   args=list(u.reg_read(r) for r in R[:4])
   if pc==0x0812e55c:
    # Native weapon selection writes its result at caller SP+4. A wrapper
    # can deepen that caller's stack without changing its output contract.
    # Assert the exact relationship before normalizing this scratch pointer.
    assert args[1]==u.reg_read(UC_ARM_REG_SP)+4,('weapon selector output frame',args)
    args[1]=4
   if pc==0x0812fe38 and args[2]==SHATTER and m is custom:
    expected=bytearray(m.read(TARGET,264));expected[0xeb]&=~2;expected[0xde]=0
    assert args[1]!=TARGET and m.read(args[1],264)==bytes(expected)
    args[1]=TARGET
   m.events.append((pc,tuple(args)))
  if pc==0x0812fe38:m.modes.append(m.word(u.reg_read(UC_ARM_REG_SP)+4))
  if pc==0x0812e55c:m.selectors.append(u.reg_read(UC_ARM_REG_LR))
  if pc==0x081300e2:
   v=u.reg_read(UC_ARM_REG_R5);m.references.append(v-0x100000000 if v&0x80000000 else v)
 def write(u,access,p,size,value,m):
  if u.reg_read(UC_ARM_REG_PC)==0x080a2298:m.writes.append((p,value))
 machine.u.hook_add(UC_HOOK_CODE,code,user_data=machine)
 machine.u.hook_add(UC_HOOK_MEM_WRITE,write,user_data=machine)
def check(group,case,ok,detail=None):
 checks[group]+=1
 if not ok:failures.append(dict(group=group,case=case,detail=detail))
def run(m,action,effect,slot,critical,residue,seed=0,target_hp=250,target_max=250):
 global calls
 m.put(0x02000000,ram);m.put(0x03000000,iwram)
 m.put(items,rom[items-0x08000000:items-0x08000000+461*32])
 m.put(ACTOR+0x2a,struct.pack('<5H',453,52,0,0,0))
 # Keep every synthetic power-boost item case alive: native KO correctly
 # clears statuses and must not be mistaken for a forbidden weapon proc.
 m.put(TARGET+0x18,struct.pack('<HH',target_hp,target_max))
 # Force no passive status noise; native effect3E has a meaningful target.
 m.put(TARGET+0xd9,b'\x11');m.put(TARGET+0xea,bytes([ram[TARGET-0x02000000+0xea]|0x10]))
 for item in (453,52):m.put(items+item*32+26,bytes(3))
 m.put(items+(453 if slot==0 else 52)*32+26,bytes([effect]))
 m.put(OBJ+0x10,struct.pack('<H',action));m.put(OBJ+0x12,struct.pack('<H',453))
 # Resume before native action routing, retaining actual evaluated positions,
 # target handles and surrounding caller frame. Mode2 is a native special-hit
 # path; it must not make a custom action enter Fight's critical logic.
 sp=OLDSP+residue;m.put(sp,iwram[OLDSP-0x03000000:OLDSP-0x03000000+0x370])
 m.put(sp+0x2f8,struct.pack('<I',critical));m.put(0x030034b0,struct.pack('<I',seed))
 m.u.reg_write(UC_ARM_REG_CPSR,regs0[16])
 for reg,value in zip(R,regs0):m.u.reg_write(reg,value)
 m.u.reg_write(UC_ARM_REG_SP,sp)
 m.events=[];m.writes=[];m.modes=[];m.selectors=[];m.references=[]
 m.u.emu_start(0x080a24a9,0x080a3762,count=1000000)
 assert m.u.reg_read(UC_ARM_REG_PC)==0x080a3762
 calls+=1
 return dict(actor=m.read(ACTOR,264).hex(),target=m.read(TARGET,264).hex(),result=m.read(OBJ,0x2c4).hex(),events=m.events,hpWrites=m.writes,
             registers=[m.u.reg_read(r) for r in R],flags=m.u.reg_read(UC_ARM_REG_CPSR)&0xf0000000,formulaModes=m.modes,selectorCallers=m.selectors,references=m.references)
for physical,factor in FACTORS.items():
 for residue in (0,4):
  for critical in (0,2):
   for slot in (0,1):
    baseline=bytes.fromhex(run(custom,physical,0,slot,critical,residue)['target'])
    for effect in range(66):
     case=(physical,effect,slot,critical,residue)
     a=run(native,0,effect,slot,critical,residue);b=run(custom,0,effect,slot,critical,residue)
     check('Fight-native-differential',case,a==b)
     if 1 in b['formulaModes']:positive['FightCritical']+=1
     if bytes.fromhex(b['target'])[0xd9]!=0x11:positive['FightTargetMutation']+=1
     if struct.unpack_from('<h',bytes.fromhex(b['result']),6)[0]:positive['FightDrainBookkeeping']+=1
     c=run(custom,physical,effect,slot,critical,residue)
     obj=bytes.fromhex(c['result']);target=bytes.fromhex(c['target'])
     check('custom-no-Fight-route',case,not any(0x080a2500<=pc<0x080a2e70 for pc,_ in c['events']))
     check('custom-no-critical',case,not(struct.unpack_from('<H',obj,0x2c)[0]&0x20))
     check('custom-one-primary-formula',case,[args for pc,args in c['events'] if pc==0x0812fe38]==[(ACTOR,TARGET,physical,453)])
     check('custom-no-critical-formula-mode',case,c['formulaModes']==[0])
     check('custom-no-3E-cleanup',case,target[0xd9]==0x11 and target[0xea]&0x10)
     check('custom-status-isolation',case,target[0xe8:0xf0]==baseline[0xe8:0xf0])
     ref=c['references'][0];scaled=abs(ref)*factor//10
     expected=-scaled if ref<0 or (slot==0 and effect==0x3f) else scaled
     check('custom-committed-coefficient',case,struct.unpack_from('<h',obj,0x3e)[0]==max(-999,min(999,expected)))
     check('custom-no-drain-bookkeeping',case,struct.unpack_from('<h',obj,6)[0]==0)
     if slot==1 and effect in (0x3d,0x3e,0x3f):check('custom-offhand-special-no-HP-effect',case,target[0x18:0x1a]==baseline[0x18:0x1a])
     check('custom-single-target-HP-write',case,len(c['hpWrites'])<=1 and all(p==TARGET+0x18 for p,_ in c['hpWrites']))
     if effect in (0,0x2b,0x3d,0x3e,0x3f) and not residue and not critical:examples.append(dict(case=case,Fight=a,Chop=c))

for seed in range(256):
 a=run(native,0,0,0,0,0,seed);b=run(custom,0,0,0,0,0,seed)
 check('Fight-critical-seed-differential',seed,a==b)
 if struct.unpack_from('<H',bytes.fromhex(b['result']),0x2c)[0]&0x20:
  positive['FightCritical']+=1
  for physical in FACTORS:
   c=run(custom,physical,0,0,0,0,seed)
   check('custom-same-critical-seed-excluded',(physical,seed),not(struct.unpack_from('<H',bytes.fromhex(c['result']),0x2c)[0]&0x20) and 1 not in c['formulaModes'])
   examples.append(dict(criticalSeed=seed,action=physical,Fight=b,custom=c))
  break
check('nonvacuous-Fight-critical',None,positive['FightCritical']>0,dict(positive))
check('nonvacuous-Fight-target-mutation',None,positive['FightTargetMutation']>0,dict(positive))
check('nonvacuous-Fight-drain',None,positive['FightDrainBookkeeping']>0,dict(positive))
for residue in (0,4):
 for action in (0,223,112,CHOP,CHOP+1,CHOP+2,SHATTER,ARMOR,CHOP+5,CHOP+6,65535):
  sp=0x03007000+residue;custom.put(sp+0x4c,struct.pack('<I',action));custom.u.reg_write(UC_ARM_REG_SP,sp)
  end=0x080a4958 if action in (0,223) else 0x080a4968
  custom.u.emu_start(0x080a494f,end,count=20)
  check('outer-second-weapon-gate',(action,residue),custom.u.reg_read(UC_ARM_REG_PC)==end and custom.u.reg_read(UC_ARM_REG_SP)==sp)
for residue in (0,4):
 for hp_value in (124,125,126):
  for effect in (0,0x3f):
   c=run(custom,430,effect,0,0,residue,0,hp_value,250)
   obj=bytes.fromhex(c['result']);ref=c['references'][0];factor=18 if hp_value<=125 else 11
   expected=abs(ref)*factor//10*(-1 if ref<0 or effect==0x3f else 1)
   check('Executioner-committed-threshold',(residue,hp_value,effect),struct.unpack_from('<h',obj,0x3e)[0]==max(-999,min(999,expected)),(ref,expected,obj.hex()))
result=dict(status='PASS' if not failures else 'FAIL',romSha1=sha(rom),engineSha1=meta['engineSha1'],privateOverlay=('--fell' in sys.argv and '--current' not in sys.argv),sourceFrameSha1=sha(state),checks=dict(checks),calls=calls,positive=dict(positive),failures=failures,examples=examples)
(OUT/'report.json').write_text(json.dumps(result,indent=2))
print(json.dumps({**{k:v for k,v in result.items() if k not in ('examples','failures')},'failures':failures[:10]},indent=2))
if failures:raise SystemExit(1)
