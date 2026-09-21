"""Compile/test isolated physical rider primitives, without rebuilding pipeline."""
import ast,collections,hashlib,json,pathlib,struct,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
P=ROOT/'build/expansion/probes';OUT=P/'physical-riders-council';OUT.mkdir(exist_ok=True)
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
TARGET,COPY,CTX=0x020033e4,0x02021000,0x0200f3f0
SHATTER,ARMOR=427,428
CURRENT='--current' in sys.argv
sha=lambda b:hashlib.sha1(b).hexdigest()
rom=(P/'combat.gba').read_bytes() if CURRENT else ((OUT/'frozen-input.gba').read_bytes() if (OUT/'frozen-input.gba').exists() else (P/'combat.gba').read_bytes())
# Preserve the accepted input while the parent pipeline advances independently.
meta=json.loads((P/'combat.json').read_text())
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
if CURRENT:
 symbols={f[2]:int(f[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(f:=l.split())==3}
 code=(ROOT/'build/expansion/engine.bin').read_bytes();assert sha(code)==meta['engineSha1'] and sha(rom)==meta['romSha1']
 patched=bytearray(rom)
 for off,size,name in [(0x12fea8,8,'ffta_physical_defense_entry'),(0xa3072,10,'ffta_physical_success_entry'),(0x13434c,8,'ffta_physical_law_entry')]:
  assert struct.unpack_from('<I',rom,off+size-4)[0]==symbols[name]|1
else:
 prefix=ROOT/'tools/arm-gnu/bin/arm-none-eabi-'
 elf=OUT/'riders.elf';binary=OUT/'riders.bin'
 dependencies=['physical-riders.c','physical-riders.s','evaluated-units.c','battle-state.c','blade-wound.c','unit-copies.c','persistent.c','runtime.c']
 subprocess.run([str(prefix)+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-fno-common','-Wall','-Wextra','-Werror','-I',str(ROOT/'build/expansion'),'-nostdlib','-Wl,-Ttext=0x09180000,--entry=ffta_physical_defense_entry',*[str(ROOT/'src/engine'/name) for name in dependencies],'-lgcc','-o',str(elf)],check=True,cwd=ROOT)
 subprocess.run([str(prefix)+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True)
 symbol_text=subprocess.check_output([str(prefix)+'nm.exe','--defined-only','-n',str(elf)],text=True)
 (OUT/'riders.symbols').write_text(symbol_text)
 symbols={f[2]:int(f[0],16) for l in symbol_text.splitlines() if len(f:=l.split())==3}
 code=binary.read_bytes();assert set(rom[0x1180000:0x1180000+len(code)])=={255}
 patched=bytearray(rom);patched[0x1180000:0x1180000+len(code)]=code
 clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
 assert rom[0x12fea8:0x12feb0]==clean[0x12fea8:0x12feb0]
 assert rom[0xa3072:0xa307c]==clean[0xa3072:0xa307c]
 assert rom[0x13434c:0x134354]==clean[0x13434c:0x134354]
 struct.pack_into('<HHI',patched,0x12fea8,0x4800,0x4700,symbols['ffta_physical_defense_entry']|1)
 struct.pack_into('<HHHI',patched,0xa3072,0xb408,0x4b00,0x4718,symbols['ffta_physical_success_entry']|1)
 struct.pack_into('<HHI',patched,0x13434c,0x4800,0x4700,symbols['ffta_physical_law_entry']|1)
# Install inert test-only action data, not an enabled production command.
action=struct.unpack_from('<I',rom,0xccd84)[0]-0x08000000+424*28
for index in (() if CURRENT else (SHATTER,ARMOR)):
 off=action+(index-424)*28;patched[off:off+28]=rom[action:action+28]
patched=bytes(patched)
if not CURRENT:(OUT/'frozen-input.gba').write_bytes(rom);(OUT/'rider-test-only.gba').write_bytes(patched)
snapshot=P/'chop-preview-council/9f773e96fa6f98ceb9fc443ee96c56a8a64c4adc-break-exec-seed0'
ram=(snapshot/'after.ram').read_bytes();iwram=(snapshot/'after.iwram').read_bytes()
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=500000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
control=bytearray(patched);control[0x12fea8:0x12feb0]=clean[0x12fea8:0x12feb0];control[0xa3072:0xa307c]=clean[0xa3072:0xa307c]
control[0x13434c:0x134354]=clean[0x13434c:0x134354]
native,expanded=ARM(bytes(control),iwram),ARM(patched,iwram)
for m in (native,expanded):m.put(0x02000000,ram)
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
checks=collections.Counter();failures=[];segments=0;centry=[]
def check(group,case,ok,detail=None):
 checks[group]+=1
 if not ok:failures.append(dict(group=group,case=case,detail=detail))
def signed(x):return x-0x100000000 if x&0x80000000 else x
def trunc75(x):return (abs(x)*3//4)*(-1 if x<0 else 1)
def entry(u,pc,size,_):centry.append((pc,u.reg_read(UC_ARM_REG_SP)))
for name in ('ffta_physical_effective_defense','ffta_physical_before_hit','ffta_physical_rider_reference','ffta_physical_law_hit'):
 expanded.u.hook_add(UC_HOOK_CODE,entry,begin=symbols[name],end=symbols[name])
def defense(m,value,action,residue):
 global segments
 sp=STACK+residue;m.put(sp,bytes([0x93])*128)
 m.u.reg_write(UC_ARM_REG_CPSR,(0xf0000030 if residue else 0xe0000030))
 for n,r in enumerate(REGS):m.u.reg_write(r,0x55000000+n)
 m.u.reg_write(UC_ARM_REG_R1,value&0xffffffff);m.u.reg_write(UC_ARM_REG_R4,0xdead91f3);m.u.reg_write(UC_ARM_REG_R10,action)
 m.u.reg_write(UC_ARM_REG_SP,sp);m.u.reg_write(UC_ARM_REG_LR,RETURN|1)
 m.u.emu_start(0x0812fea9,0x0812feb0,count=10000);segments+=1
 return ([m.u.reg_read(r) for r in REGS],m.u.reg_read(UC_ARM_REG_CPSR)&0xf0000000,m.u.reg_read(UC_ARM_REG_SP),m.read(sp,128))
for residue in (0,4):
 for action_id in (0,SHATTER,ARMOR,65535):
  for value in range(1000):
   expected=trunc75(value) if action_id==ARMOR else value
   a=defense(native,expected,action_id,residue);b=defense(expanded,value,action_id,residue)
   check('effective-defense-inline-ABI',(value,action_id,residue),a==b,(a[:3],b[:3]) if value==0 else None)
 for action_id in range(347):check('original-action-defense',action_id,defense(native,713,action_id,residue)==defense(expanded,713,action_id,residue))

def context(m,action_id,recipient=TARGET,stage=0):
 data=bytearray(52);struct.pack_into('<IIIHH',data,0,UNIT,TARGET,recipient,action_id,453);data[0x28]=stage
 m.put(CTX,data)
def reset_units(m,protect=True,affinity=1,effect=0):
 m.put(0x02000000,ram)
 actor=bytearray(ram[0x80:0x188]);target=bytearray(ram[TARGET-0x02000000:TARGET-0x02000000+264])
 for u in (actor,target):u[0x38:0x40]=bytes(8);u[0xe8:0xf0]=bytes(8)
 struct.pack_into('<5H',actor,0x2a,453,0,0,0,0)
 target[0xeb]=2 if protect else 0;target[0xde]=13;target[0x0d]=affinity
 m.put(UNIT,actor);m.put(TARGET,target);m.put(COPY,target)
 items=struct.unpack_from('<I',rom,0x130684)[0]
 m.put(items+453*32,rom[items-0x08000000+453*32:items-0x08000000+454*32])
 m.put(items+453*32+9,b'\x01');m.put(items+453*32+26,bytes([effect,0,0]))
for residue in (0,4):
 for action_id in list(range(347))+[426,SHATTER,ARMOR,429,430,431]:
  for stage in (0,1,2):
   reset_units(expanded);context(expanded,action_id,COPY,stage)
   before=expanded.read(TARGET,264);copy=bytearray(expanded.read(COPY,264))
   expanded.call(symbols['ffta_physical_before_hit_entry'],CTX,stack=STACK+residue)
   if action_id==SHATTER and stage==0:copy[0xeb]&=~2;copy[0xde]=0
   check('hit-recipient-only',(action_id,stage,residue),expanded.read(TARGET,264)==before and expanded.read(COPY,264)==bytes(copy))

samples=[]
for residue in (0,4):
 for action_id in (112,424,425,426,SHATTER,ARMOR,429,430):
  for protect in (False,True):
   for affinity in (1,2,3):
    for effect in (0,0x3f):
     for m in (native,expanded):reset_units(m,protect,affinity,effect);context(m,action_id)
     # Independent oracle: only targetcopy changes; native live target is kept.
     golden=bytearray(native.read(COPY,264))
     if action_id==SHATTER:golden[0xeb]&=~2;golden[0xde]=0
     native.put(COPY,golden)
     before=expanded.read(0x02000000,0x40000)
     got=signed(expanded.call(symbols['ffta_physical_rider_reference_entry'],CTX,453,2,stack=STACK+residue))
     # Armor oracle changes only the already-capped scalar immediately before
     # native subtraction; it never edits stored WDef or invokes our helper.
     def oracle(u,pc,size,_):
      if action_id==ARMOR:u.reg_write(UC_ARM_REG_R1,trunc75(signed(u.reg_read(UC_ARM_REG_R1)))&0xffffffff)
     h=native.u.hook_add(UC_HOOK_CODE,oracle,begin=0x0812fea8,end=0x0812fea8)
     native.put(STACK+residue,struct.pack('<III',0,2,0))
     try:expected=signed(native.call(0x0812fe38,UNIT,COPY,action_id,453,stack=STACK+residue))
     finally:native.u.hook_del(h)
     check('native-P-oracle',(action_id,protect,affinity,effect,residue),got==expected,(got,expected))
     check('query-EWRAM-isolation',(action_id,protect,affinity,effect,residue),expanded.read(0x02000000,0x40000)==before)
     samples.append((action_id,protect,affinity,effect,residue,got))

# Installed successful-hit branch: compare original action callback execution
# and the two stage continuations, then prove removal precedes the formula.
def success(m,action_id,stage,residue):
 global segments
 m.put(0x03000000,iwram)
 reset_units(m);m.call(0x0812f2a4,action_id,453,0)
 m.put(CTX,struct.pack('<III',UNIT,TARGET,TARGET))
 # Force the ordinary physical descriptor for this ABI matrix; action identity
 # still traverses native getters/formula. Full nonphysical callbacks differ.
 vector=struct.unpack_from('<I',m.read(CTX+0x2c,4))[0]
 m.put(CTX+0x28,bytes([stage]));m.put(CTX+0x30,struct.pack('<I',0x08553f6c))
 sp=STACK+residue;m.put(sp,bytes([0x93])*128)
 m.u.reg_write(UC_ARM_REG_CPSR,0xf0000030)
 for n,r in enumerate(REGS):m.u.reg_write(r,0x55000000+n)
 m.u.reg_write(UC_ARM_REG_R4,stage);m.u.reg_write(UC_ARM_REG_SP,sp);m.u.reg_write(UC_ARM_REG_LR,0x0812f355)
 end=0x080a307c if stage<=1 else 0x080a3086
 events=[]
 def formula(u,pc,size,_):events.append((m.read(TARGET+0xeb,1)[0],m.read(TARGET+0xde,1)[0]))
 h=m.u.hook_add(UC_HOOK_CODE,formula,begin=0x0812fe38,end=0x0812fe38)
 try:m.u.emu_start(0x080a3073,end,count=100000)
 finally:m.u.hook_del(h)
 assert m.u.reg_read(UC_ARM_REG_PC)==end
 segments+=1
 return dict(regs=[m.u.reg_read(r) for r in REGS],flags=m.u.reg_read(UC_ARM_REG_CPSR)&0xf0000000,sp=m.u.reg_read(UC_ARM_REG_SP),frame=m.read(sp,128).hex(),target=m.read(TARGET,264).hex(),events=events)
for residue in (0,4):
 for action_id in range(347):
  for stage in (0,2):
   a=success(native,action_id,stage,residue);b=success(expanded,action_id,stage,residue)
   check('original-success-inline-ABI',(action_id,stage,residue),a==b,(a,b) if action_id==0 and not stage else None)
 for stage in (0,1,2):
  b=success(expanded,SHATTER,stage,residue)
  expected=(0,0) if stage==0 else (2,13)
  check('remove-before-P',(stage,residue),b['events']==[expected],b['events'])

# Resume a real committed recipient frame before native action dispatch and
# accuracy. This tests the installed hook's reachability, not a synthetic call
# that assumes a hit. A copied native physical record is used only in this ROM.
regs0=struct.unpack_from('<17I',(snapshot/'after.state').read_bytes(),0x20)
OBJ,OLDSP=regs0[9],regs0[13]
R=REGS+[UC_ARM_REG_R12,UC_ARM_REG_SP,UC_ARM_REG_LR]
for m in (native,expanded):
 m.commit_events=[]
 def observe(u,pc,size,m):
  if pc==0x0812fe38:
   target=u.reg_read(UC_ARM_REG_R1)
   event_target=m.word(CTX+4) if CURRENT and u.reg_read(UC_ARM_REG_R2)==SHATTER else target
   m.commit_events.append((event_target,m.read(target+0xeb,1)[0],m.read(target+0xde,1)[0]))
 m.u.hook_add(UC_HOOK_CODE,observe,user_data=m,begin=0x0812fe38,end=0x0812fe38)
 m.law_references=[]
 def reference(u,pc,size,m):m.law_references.append(signed(u.reg_read(UC_ARM_REG_R5)))
 m.u.hook_add(UC_HOOK_CODE,reference,user_data=m,begin=0x081300f2,end=0x081300f2)

def commit(m,action_id,residue,seed):
 global segments
 reset_units(m);m.put(0x03000000,iwram)
 m.put(OBJ+0x10,struct.pack('<HH',action_id,453))
 sp=OLDSP+residue;m.put(sp,iwram[OLDSP-0x03000000:OLDSP-0x03000000+0x370])
 m.put(sp+0x2f8,bytes(4));m.put(0x030034b0,struct.pack('<I',seed))
 m.u.reg_write(UC_ARM_REG_CPSR,regs0[16])
 for reg,value in zip(R,regs0):m.u.reg_write(reg,value)
 m.u.reg_write(UC_ARM_REG_SP,sp);m.commit_events=[]
 m.u.emu_start(0x080a24a9,0x080a3762,count=1000000)
 assert m.u.reg_read(UC_ARM_REG_PC)==0x080a3762
 segments+=1
 return dict(actor=m.read(UNIT,264).hex(),target=m.read(TARGET,264).hex(),result=m.read(OBJ,0x2c4).hex(),
             registers=[m.u.reg_read(r) for r in R],flags=m.u.reg_read(UC_ARM_REG_CPSR)&0xf0000000,events=m.commit_events)
commits=[]
for residue in (0,4):
 for seed in (0,1):
  for action_id in (0,112,424,425,ARMOR,SHATTER):
   a=commit(native,action_id,residue,seed);b=commit(expanded,action_id,residue,seed)
   if action_id not in (ARMOR,SHATTER):
    check('committed-native-differential',(action_id,residue,seed),a==b)
   target=bytes.fromhex(b['target']);initial=ram[TARGET-0x02000000:TARGET-0x02000000+264]
   if action_id==SHATTER:
    hit=bool(b['events'])
    expected=(0,0) if hit else (2,13)
    check('committed-Shatter-hit-or-miss',(residue,seed), (target[0xeb]&2,target[0xde])==expected,b)
    check('committed-Shatter-before-P',(residue,seed),all(event[1:]==(0,0) for event in b['events']))
    check('committed-Shatter-nonvacuous',(residue,seed),hit==(seed==0),b['events'])
   if action_id==ARMOR:
    check('committed-Armor-Protect-preserved',(residue,seed),(target[0xeb]&2,target[0xde])==(2,13))
    check('committed-Armor-no-stored-stat-change',(residue,seed),target[0x1c:0x2a]==initial[0x1c:0x2a])
   if action_id in (ARMOR,SHATTER):commits.append(dict(case=(action_id,residue,seed),out=b))

# Complete native law status evaluator, with explicitly separate source/live
# actor+target and simulated copies, matching native1343C8's allocation model.
LAW_ACTOR=0x02022000
def law(m,action_id,status,removal,residue,protect=True,effect=0,affinity=1):
 reset_units(m,protect,affinity,effect);m.put(0x03000000,iwram)
 m.put(LAW_ACTOR,m.read(UNIT,264));m.put(COPY-4,b'PRE!');m.put(COPY+264,b'POST')
 before=m.read(0x02000000,0x40000)
 sp=STACK+residue;m.put(sp,struct.pack('<II',status,removal));m.commit_events=[];m.law_references=[]
 value=m.call(0x081342cc,LAW_ACTOR,COPY,action_id,453,stack=sp)
 after=m.read(0x02000000,0x40000)
 return dict(value=value,copy=m.read(COPY,264).hex(),events=m.commit_events,references=m.law_references,
             registers=[m.u.reg_read(r) for r in R],flags=m.u.reg_read(UC_ARM_REG_CPSR)&0xf0000000,
             isolation=before[:0x1940]==after[:0x1940] and before[0x3c000:]==after[0x3c000:] and m.read(TARGET,264)==before[TARGET-0x02000000:TARGET-0x02000000+264]
             and m.read(LAW_ACTOR,264)==m.read(UNIT,264) and m.read(COPY-4,4)==b'PRE!' and m.read(COPY+264,4)==b'POST'),after
for residue in (0,4):
 for action_id in range(347):
  for removal in (0,1):
   for protect in (False,True):
    a,ar=law(native,action_id,25,removal,residue,protect);b,br=law(expanded,action_id,25,removal,residue,protect)
    check('original-law-full-evaluator',(action_id,removal,residue,protect),a==b and ar==br,(a,b) if a!=b else None)
law_samples=[]
for residue in (0,4):
 for status in range(64):
  for removal in (0,1):
   for protect in (False,True):
    b,_=law(expanded,SHATTER,status,removal,residue,protect)
    check('Shatter-law-status-result',(status,removal,residue,protect),b['value']==int(status==25 and removal and protect),b)
    check('Shatter-law-source-isolation',(status,removal,residue,protect),b['isolation'])
    check('Shatter-law-P-after-removal',(status,removal,residue,protect),all(e[1:]==(0,0) for e in b['events']),b['events'])
    if status==25:law_samples.append(dict(case=(status,removal,residue,protect),out=b))
for residue in (0,4):
 for effect in (0,0x3f):
  for affinity in (1,2,3):
   b,_=law(expanded,SHATTER,25,1,residue,True,effect,affinity)
   check('Shatter-law-null-absorb-3F',(residue,effect,affinity),b['value']==1 and b['isolation'] and b['events']==[(COPY,0,0)],b)
   expected=next(s[-1] for s in samples if s[:5]==(SHATTER,True,affinity,effect,residue))
   check('Shatter-law-preview-same-P',(residue,effect,affinity),b['references']==[expected],(b['references'],expected))

# Full native law selector, including its native heap allocate/copy/free path.
# A test-only law record type15 requests a single native status (Protect25).
LAW_RECORD=0x0203e000
for m in (native,expanded):
 m.outer_calls=[]
 def simulation(u,pc,size,m):
  sp=u.reg_read(UC_ARM_REG_SP)
  m.outer_calls.append([u.reg_read(r) for r in REGS[:4]]+[m.word(sp),m.word(sp+4)])
 m.u.hook_add(UC_HOOK_CODE,simulation,user_data=m,begin=0x081342cc,end=0x081342cc)
def outer_law(m,action_id,residue,protect=True,kind=15,status=25):
 reset_units(m,protect);m.put(0x03000000,iwram)
 m.put(LAW_RECORD,bytes([0,0,0,0,kind,status,0,0,0,0,0,0]))
 before=m.read(0x02000000,0x40000)
 sp=STACK+residue;m.put(sp,struct.pack('<IIII',0,453,0,LAW_RECORD))
 m.commit_events=[];m.law_references=[];m.outer_calls=[]
 value=m.call(0x081343c8,UNIT,TARGET,action_id,0,stack=sp)
 after=m.read(0x02000000,0x40000)
 return dict(value=value,events=m.commit_events,references=m.law_references,calls=m.outer_calls,
             sourceIsolation=before[:0x1940]==after[:0x1940] and before[0x3c000:]==after[0x3c000:] and m.read(TARGET,264)==before[TARGET-0x02000000:TARGET-0x02000000+264]),after
outer_samples=[]
outer_positive=[]
for residue in (0,4):
 for action_id in range(347):
  a,ar=outer_law(native,action_id,residue);b,br=outer_law(expanded,action_id,residue)
  check('outer-law-all-original-actions',(action_id,residue),a==b and ar==br,(a,b))
  if action_id and b['value']:outer_positive.append(action_id)
check('outer-law-native-positive-status',None,bool(outer_positive),outer_positive)
for residue in (0,4):
 for protect in (False,True):
  for action_id in (0,112,424,425,SHATTER,ARMOR):
   a,ar=outer_law(native,action_id,residue,protect);b,br=outer_law(expanded,action_id,residue,protect)
   if action_id not in (SHATTER,ARMOR):check('outer-law-native-differential',(action_id,residue,protect),a==b and ar==br,(a,b))
   check('outer-law-source-isolation',(action_id,residue,protect),b['sourceIsolation'],b)
   if action_id==SHATTER:
    check('outer-law-Shatter-no-added-Protect',(residue,protect),b['value']==0,b)
    check('outer-law-Shatter-native-copies',(residue,protect),len(b['calls'])==1 and all(p not in (UNIT,TARGET) for p in b['calls'][0][:2]),b)
    check('outer-law-Shatter-before-P',(residue,protect),len(b['events'])==1 and b['events'][0][1:]==(0,0),b)
    outer_samples.append(b)
 b,_=outer_law(expanded,SHATTER,residue,True,16)
 check('outer-law-no-harmful-status',(residue,16),b['value']==0 and b['sourceIsolation'] and len(b['calls'])==21,b)
check('C-stack-alignment',len(centry),all(sp%8==0 for _,sp in centry))
result=dict(status='PASS' if not failures else 'FAIL',inputRomSha1=sha(rom),testRomSha1=sha(patched),riderCodeSha1=sha(code),checks=dict(checks),segments=segments,completeCalls=native.calls+expanded.calls,failures=failures,samples=samples,commits=commits,
            lawSamples=law_samples,outerLawSamples=outer_samples,scope='Installed production rider probe' if CURRENT else 'Verified primitive probe including native law phase')
(OUT/('current-report.json' if CURRENT else 'report.json')).write_text(json.dumps(result,indent=2));print(json.dumps({**result,'samples':samples[:8],'commits':len(commits),'lawSamples':len(law_samples),'failures':failures[:6]},indent=2))
if failures:raise SystemExit(1)
