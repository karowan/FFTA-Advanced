"""Frozen installed Chop hooks and complete native physical-formula audit."""
import ast,ctypes as C,hashlib,importlib.util,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
OUT=ROOT/'build/expansion/probes';FROZEN=OUT/'chop-native-council';FROZEN.mkdir(exist_ok=True)
meta=json.loads((OUT/'combat.json').read_text());probe=(OUT/'combat.gba').read_bytes()
CHOP=424
TOMA=CHOP+1
SHATTER,ARMOR=CHOP+3,CHOP+4
FACTORS={CHOP:11,TOMA:9,CHOP+2:9,SHATTER:10,ARMOR:10,CHOP+5:11,CHOP+6:11,431:18}
assert set(FACTORS).issubset(meta['actions']), 'Await dual-action build'
sha=lambda b:hashlib.sha1(b).hexdigest()
assert sha(probe)==meta['romSha1']
base=bytearray(probe)
for c in meta['changes']:
    if 'expected' in c:base[c['offset']:c['offset']+c['size']]=bytes.fromhex(c['expected'])
base=bytes(base) # Same new action data, only three code hooks removed.
(FROZEN/'combat.gba').write_bytes(probe);(FROZEN/'combat.json').write_text(json.dumps(meta,indent=2))
symbols={p[2]:int(p[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=l.split())==3}
engine=(ROOT/'build/expansion/engine.bin').read_bytes()
assert sha(engine)==meta['engineSha1'] and probe[0x1100000:0x1100000+len(engine)]==engine
(FROZEN/'engine.symbols').write_text((ROOT/'build/expansion/engine.symbols').read_text())
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')],type_ignores=[]),'<harness>','exec'))
iwram=iwram_from_boot();native,expanded=ARM(base,iwram),ARM(probe,iwram)
# Independent scalar oracle for Armor, leaving the unhooked native formula
# intact everywhere except its already-capped defense input.
def armor_oracle(u,pc,size,_):
 if u.reg_read(UC_ARM_REG_R10)==ARMOR:u.reg_write(UC_ARM_REG_R1,u.reg_read(UC_ARM_REG_R1)*3//4)
native.u.hook_add(UC_HOOK_CODE,armor_oracle,begin=0x0812fea8,end=0x0812fea8)
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
TARGET=UNIT+264;CONTEXT=0x02002800
checks,failures={},[]
nonvacuous={'nativeDrainDetected':0,'ChopDrainBlocked':0,'nativeEffectMutation':0,'ChopEffectMutationPrevented':0}
def check(group,case,ok,detail=None):
    checks[group]=checks.get(group,0)+1
    if not ok:failures.append(dict(group=group,case=case,detail=detail))
def s32(x):return x-0x100000000 if x&0x80000000 else x
def callers(target):
    found=[]
    for off in range(0x100,0x144400,2):
        a,b=struct.unpack_from('<HH',probe,off)
        if a&0xf800==0xf000 and b&0xf800==0xf800:
            delta=((a&0x7ff)<<12)|((b&0x7ff)<<1)
            if delta&0x400000:delta-=0x800000
            if off+4+delta==target:found.append(0x08000000+off+5)
    return found
drain_callers=callers(0x130654);effect_callers=callers(0x130688)
assert drain_callers==[0x080a2b11,0x080a30af,0x081300c1],drain_callers
assert effect_callers==[0x080a270b,0x080a2dcd,0x08133959],effect_callers
items=native.word(0x08130684)
segments=0
def invoke(machine,start,args,caller,residue):
    global segments
    u=machine.u;sp=STACK+residue
    u.reg_write(UC_ARM_REG_CPSR,0xf0000030)
    for n,r in enumerate(REGS):u.reg_write(r,0x55000000+n)
    for n,v in args.items():u.reg_write(REGS[n],v)
    u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,caller)
    machine.put(sp,bytes([0xa5])*64)
    u.emu_start(start|1,caller&~1,count=50000)
    assert u.reg_read(UC_ARM_REG_PC)==caller&~1
    assert u.reg_read(UC_ARM_REG_SP)==sp
    segments+=1
    return dict(regs=[u.reg_read(r) for r in REGS],flags=u.reg_read(UC_ARM_REG_CPSR)&0xf0000000,
                frame=machine.read(sp,64).hex(),unit=machine.read(TARGET,264).hex())

# All observed callers; each of the three effect slots, drain/heal/3E/no effect.
for residue in (0,4):
 for item in (0,1,52,453,460):
  for effect in (0,0x3d,0x3e,0x3f):
   for slot in range(3):
    for action in (0,1,112,346,423,CHOP,TOMA,426,SHATTER,ARMOR,429,430,431,65535,0x10000+CHOP):
     for machine in (native,expanded):
      machine.put(TARGET,bytes(264))
      machine.put(items+item*32+26,bytes(3));machine.put(items+item*32+26+slot,bytes([effect]))
      machine.put(CONTEXT+16,struct.pack('<H',action&65535))
     for caller in drain_callers+[RETURN|1]:
      a=invoke(native,0x08130654,{0:item,9:CONTEXT,10:action},caller,residue)
      b=invoke(expanded,0x08130654,{0:item,9:CONTEXT,10:action},caller,residue)
      blocked=(caller==0x081300c1 and action in FACTORS) or (caller==0x080a30af and action&65535 in FACTORS)
      case=(item,effect,slot,action,hex(caller),residue)
      check('drain-value',case,b['regs'][0]==(0 if blocked else a['regs'][0]))
      if a['regs'][0]:
       nonvacuous['nativeDrainDetected']+=1
       if blocked and not b['regs'][0]:nonvacuous['ChopDrainBlocked']+=1
      check('drain-callee-frame',case,b['regs'][4:]==a['regs'][4:] and b['frame']==a['frame'])
      if not blocked:check('drain-original-register-flags',case,a==b,(a,b) if a!=b else None)
     for caller in effect_callers:
      for machine in (native,expanded):
       unit=bytearray(264);struct.pack_into('<HHHH',unit,0x18,75,25,100,50)
       unit[0xea]=0x5a;unit[0xd9]=7 # Native3E clears EA bit10 and D9.
       machine.put(TARGET,unit)
      a=invoke(native,0x08130688,{0:item,1:action,2:TARGET},caller,residue)
      b=invoke(expanded,0x08130688,{0:item,1:action,2:TARGET},caller,residue)
      case=(item,effect,slot,action,hex(caller),residue)
      if a['unit']!=bytes(unit).hex():
       nonvacuous['nativeEffectMutation']+=1
       if action&65535 in FACTORS and b['unit']==bytes(unit).hex():nonvacuous['ChopEffectMutationPrevented']+=1
      if action&65535 in FACTORS:
       check('effect-Chop-no-mutation',case,b['unit']==bytes(unit).hex())
       check('effect-Chop-callee-frame',case,b['regs'][4:]==a['regs'][4:] and b['frame']==a['frame'])
      else:check('effect-original-register-flags-memory',case,a==b,(a,b) if a!=b else None)

# Reset item records before full formula tests.
for machine in (native,expanded):machine.put(items,probe[items-0x08000000:items-0x08000000+461*32])
ram=(OUT/'battle-fixture/battle-ready.ram').read_bytes()
for machine in (native,expanded):machine.put(0x02000000,ram)
def units(machine,gear):
    actor=bytearray(ram[0x80:0x80+264]);target=bytearray(ram[0x188:0x188+264])
    actor[4:8]=bytes([1,2,1,2]);target[4:8]=bytes([1,2,1,2])
    actor[0x38:0x40]=bytes(8);target[0x38:0x40]=bytes(8)
    actor[0xe8:0xf0]=bytes(8);target[0xe8:0xf0]=bytes(8)
    for data in (actor,target):struct.pack_into('<HHHH',data,0x18,250,50,250,50)
    struct.pack_into('<5H',actor,0x2a,*(list(gear)+[0]*(5-len(gear))))
    struct.pack_into('<5H',target,0x2a,0,0,0,0,0)
    machine.put(UNIT,actor);machine.put(TARGET,target)

formula_events=[];final_events=[]
c_entries=[]
def c_capture(u,address,size,data):c_entries.append((address,u.reg_read(UC_ARM_REG_SP)))
for name in ('ffta_physical_magnitude','ffta_physical_final','ffta_primary_weapon'):
 expanded.u.hook_add(UC_HOOK_CODE,c_capture,begin=symbols[name]&~1,end=symbols[name]&~1)
def formula_capture(u,address,size,data):
    sp=u.reg_read(UC_ARM_REG_SP)
    args=list(u.reg_read(r) for r in REGS[:4])
    if args[2]==SHATTER:
        expected=bytearray(expanded.read(TARGET,264));expected[0xeb]&=~2;expected[0xde]=0
        check('private-target-copy',args[1],args[1]!=TARGET and expanded.read(args[1],264)==bytes(expected))
        args[1]=TARGET
    formula_events.append(tuple(args)+struct.unpack('<III',u.mem_read(sp,12)))
def final_capture(u,address,size,data):final_events.append(s32(u.reg_read(UC_ARM_REG_R5)))
expanded.u.hook_add(UC_HOOK_CODE,formula_capture,begin=0x0812fe38,end=0x0812fe38)
expanded.u.hook_add(UC_HOOK_CODE,final_capture,begin=0x081300e2,end=0x081300e2)
formula_samples=[]
for physical,factor in FACTORS.items():
 for residue in (0,4):
  for axe in range(453,461):
   prior=None
   for offhand in (0,1,52,252,460):
    for machine in (native,expanded):units(machine,(axe,offhand))
    context=bytearray(48);struct.pack_into('<IIHH',context,0,UNIT,TARGET,0,0)
    struct.pack_into('<HH',context,12,physical,offhand);struct.pack_into('<H',context,0x26,0x10)
    expanded.put(CONTEXT,context);formula_events.clear();final_events.clear()
    before=expanded.read(UNIT,528)
    actual=s32(expanded.call(symbols['ffta_physical_magnitude_entry'],CONTEXT,stack=STACK+residue))
    check('one-primary-formula',(axe,offhand,residue),formula_events==[(UNIT,TARGET,physical,axe,0,2,0)],formula_events)
    check('one-final-factor',(axe,offhand,residue),len(final_events)==1 and actual==max(-999,min(999,(-1 if final_events[0]<0 else 1)*(abs(final_events[0])*factor//10))),final_events)
    check('formula-unit-isolation',(axe,offhand,residue),expanded.read(UNIT,528)==before)
    if prior is not None:check('offhand-independent',(axe,offhand,residue),actual==prior,(prior,actual))
    prior=actual;formula_samples.append((axe,offhand,residue,actual,final_events[:]))
    # Same native formula / action / primary, without multiplier or new drain hook.
    native.put(STACK+residue,struct.pack('<III',0,2,0))
    original=s32(native.call(0x0812fe38,UNIT,TARGET,physical,axe,stack=STACK+residue))
    check('native-reference',(axe,offhand,residue),len(final_events)==1 and original==max(-999,min(999,final_events[0])),(original,final_events))

# Original descriptors that share the magnitude callback retain its complete
# native path. All original action IDs are tested, not only Rush's donor row.
for residue in (0,4):
 for action in range(347):
   for machine in (native,expanded):units(machine,(1,52))
   context=bytearray(48);struct.pack_into('<II',context,0,UNIT,TARGET)
   struct.pack_into('<HH',context,12,action,0);struct.pack_into('<H',context,0x26,0x10)
   for machine in (native,expanded):machine.put(CONTEXT,context)
   a=native.call(0x0813189c,CONTEXT,stack=STACK+residue)
   b=expanded.call(symbols['ffta_physical_magnitude_entry'],CONTEXT,stack=STACK+residue)
   check('all-original-full-callback',(action,residue),a==b,(a,b))
   check('all-original-callback-units',(action,residue),native.read(UNIT,528)==expanded.read(UNIT,528))

# Explicit synthetic weapon-effect perturbation remains confined to the test
# emulator. Offhand3D/3E/3F must not affect Chop; primary3F retains native sign.
effect_samples=[]
for physical,factor in FACTORS.items():
 for residue in (0,4):
  native.put(items,probe[items-0x08000000:items-0x08000000+461*32]);units(native,(453,52))
  native.put(STACK+residue,struct.pack('<III',0,2,0))
  baseline_reference=s32(native.call(0x0812fe38,UNIT,TARGET,physical,453,stack=STACK+residue))
  for effect in (0,0x3d,0x3e,0x3f):
   for slot in range(3):
    for on_primary in (False,True):
     expanded.put(items,probe[items-0x08000000:items-0x08000000+461*32])
     item=453 if on_primary else 52
     expanded.put(items+item*32+26,bytes(3));expanded.put(items+item*32+26+slot,bytes([effect]))
     units(expanded,(453,52))
     context=bytearray(48);struct.pack_into('<II',context,0,UNIT,TARGET)
     struct.pack_into('<HH',context,12,physical,52);struct.pack_into('<H',context,0x26,0x10)
     expanded.put(CONTEXT,context);formula_events.clear();final_events.clear()
     got=s32(expanded.call(symbols['ffta_physical_magnitude_entry'],CONTEXT,stack=STACK+residue))
     expected=-(baseline_reference*factor//10) if on_primary and effect==0x3f else baseline_reference*factor//10
     check('primary-only-weapon-effects',(residue,effect,slot,on_primary),got==expected,(got,expected,final_events))
     check('effect-single-formula',(residue,effect,slot,on_primary),formula_events==[(UNIT,TARGET,physical,453,0,2,0)])
     effect_samples.append((residue,effect,slot,on_primary,got))

# Real native restorative metadata plus controlled elemental affinities. Item
# element lives at+9; unit fire affinity at+0D (native getter selector0B).
restorative_ids=[i for i in range(1,347) if 0x3f in probe[items-0x08000000+i*32+26:items-0x08000000+i*32+29]]
check('native-restorative-metadata',124,restorative_ids==[124],restorative_ids)
for machine in (native,expanded):
 machine.put(items,probe[items-0x08000000:items-0x08000000+461*32])
 check('native-restorative-getter',124,machine.call(0x08130620,124)==1)
healing_samples=[]
for physical,factor in FACTORS.items():
 for residue in (0,4):
  for affinity in (0,1,2,3,4):
   for where in ('none','primary','offhand'):
    for machine in (native,expanded):
     machine.put(items,probe[items-0x08000000:items-0x08000000+461*32])
     machine.put(items+453*32+9,bytes([1]))
     for item in (453,52):machine.put(items+item*32+26,bytes(3))
     if where!='none':machine.put(items+(453 if where=='primary' else 52)*32+26,bytes([0x3f]))
     units(machine,(453,52));machine.put(TARGET+0x0d,bytes([affinity]))
     machine.put(CONTEXT,struct.pack('<IIIHH',UNIT,TARGET,0,physical,453)+bytes(22)+struct.pack('<H',0x10)+bytes(8))
    expanded_before=expanded.read(UNIT,528)
    final_events.clear();formula_events.clear()
    got=s32(expanded.call(symbols['ffta_physical_magnitude_entry'],CONTEXT,stack=STACK+residue))
    native.put(STACK+residue,struct.pack('<III',0,2,0))
    plain=s32(native.call(0x0812fe38,UNIT,TARGET,physical,453,stack=STACK+residue))
    expect=(abs(plain)*factor//10)*(-1 if plain<0 or where=='primary' else 1)
    check('restorative-element-formula',(residue,affinity,where),got==expect,(got,plain,expect))
    check('restorative-element-single-call',(residue,affinity,where),len(formula_events)==1 and len(final_events)==1)
    check('restorative-element-isolation',(residue,affinity,where),expanded.read(UNIT,528)==expanded_before)
    if where=='primary':check('restorative-never-damaging',(residue,affinity),got<=0)
    if affinity==3 and where=='primary':check('native-double-negation-positive',residue,plain>0 and got<0,(plain,got))
    if affinity==2:check('native-null-remains-zero',(residue,where),plain==0 and got==0,(plain,got))
    healing_samples.append((residue,affinity,where,plain,got))

for name,count in nonvacuous.items():check('nonvacuous',name,count>0,count)
check('all-C-entries-aligned',len(c_entries),bool(c_entries) and all(sp%8==0 for _,sp in c_entries),[x for x in c_entries if x[1]%8])
result=dict(status='PASS' if not failures else 'FAIL',romSha1=sha(probe),engineSha1=meta['engineSha1'],checks=checks,failures=failures,
            segments=segments,completeCalls=native.calls+expanded.calls,drainCallers=[hex(x) for x in drain_callers],effectCallers=[hex(x) for x in effect_callers],formulaSamples=formula_samples,effectSamples=effect_samples,healingSamples=healing_samples,nonvacuous=nonvacuous,alignedCEntries=len(c_entries))
(OUT/'chop-native-tests.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({**result,'failures':failures[:5],'formulaSamples':formula_samples[:4],'effectSamples':effect_samples[:4]},indent=2))
if failures:raise SystemExit(1)
