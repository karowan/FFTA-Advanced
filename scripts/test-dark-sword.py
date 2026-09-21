"""Private Dark Knight native formula, actual-resource rider and original controls."""
import ast,collections,hashlib,itertools,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
P=ROOT/'build/expansion/probes'
meta,OUT,rom,base=runpy.run_path(str(ROOT/'scripts/dark-sword-test-input.py'))['load_input']('--current' in sys.argv)
symbols=meta['symbols'];UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=1000000'));exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
SNAP=P/'chop-preview-council/9f773e96fa6f98ceb9fc443ee96c56a8a64c4adc-break-exec-seed0'
ram=(SNAP/'after.ram').read_bytes();iwram=(SNAP/'after.iwram').read_bytes();regs=struct.unpack_from('<17I',(SNAP/'after.state').read_bytes(),0x20)
ACTOR,TARGET,OBJ,SP=UNIT,0x020033e4,regs[9],regs[13];items=struct.unpack_from('<I',rom,0x130684)[0]
old,new=ARM(base,iwram),ARM(rom,iwram);counts=collections.Counter()
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();unscaled=bytearray(rom);unscaled[0x1300e2:0x1300f2]=clean[0x1300e2:0x1300f2];reference=ARM(bytes(unscaled),iwram)
def check(group,actual,expected):
 counts[group]+=1;assert actual==expected,(group,actual,expected)
for m in (old,new):m.put(0x02000000,ram)
alignment=[]
for name in ('ffta_dark_sword_apply','ffta_dark_law_weapons','ffta_physical_final','ffta_combat_geometry'):
 def aligned(u,pc,size,_):alignment.append(u.reg_read(UC_ARM_REG_SP)%8)
 new.u.hook_add(UC_HOOK_CODE,aligned,begin=symbols[name]&~1,end=symbols[name]&~1)
for action in list(range(347))+[357,358,424,430,431]:
 for item in (0,1,52,389,390,453):
  for residue in (0,4):
   expected=0 if action in (357,358) else old.call(0x0812f8a4,ACTOR,action,item,stack=STACK+residue)
   check('native-element',new.call(0x0812f8a4,ACTOR,action,item,stack=STACK+residue),expected)
for action,removed,undead,hp,mp,target_mp in itertools.product((357,358,346),(0,1,2,4,5,9,10,79,80,99,999),(0,1),(1,50,100),(0,47,50),(0,3,49)):
 actor=bytearray(264);target=bytearray(264);struct.pack_into('<HHHH',actor,0x18,hp,100,mp,50);struct.pack_into('<H',target,0x1c,target_mp);struct.pack_into('<H',target,0x28,0x8000);target[0xe9]=8*undead
 new.put(ACTOR,actor);new.put(TARGET,target)
 if action==357:
  amount=min(removed//2,20);amount=amount if undead else min(amount,100-hp);expected=((amount if undead else -amount)&0xffff)<<16
 elif action==358:
  loss=min(removed//5,16,target_mp);amount=min(loss,mp if undead else 50-mp);expected=loss|(((amount if undead else -amount)&0xffff)<<16)
 else:expected=0
 check('resource-plan',new.call(symbols['ffta_dark_sword_plan'],action,ACTOR,TARGET,removed),expected)
 check('plan-isolation',new.read(ACTOR,264)+new.read(TARGET,264),bytes(actor+target))
# Job-independent weapon gating, including legitimate secondary Dark Arts.
context=0x0200f3f0
for action,job,category in itertools.product((357,358),range(126),range(32)):
 new.put(0x02000000,ram);new.put(ACTOR+5,bytes([job]));new.put(ACTOR+7,bytes([job]));new.put(ACTOR+0x2a,struct.pack('<5H',389,52,0,0,0))
 new.put(items+389*32+8,bytes([category]));new.put(items+389*32+11,b'\x01');new.put(context,struct.pack('<II',ACTOR,TARGET));new.put(context+12,struct.pack('<H',action))
 # Category20 is a shield and is skipped by ordered-primary selection; the
 # genuine second weapon52 then becomes primary (native greatsword5).
 check('cross-job-primary-weapon',new.call(symbols['ffta_physical_eligibility_entry'],context),int(category in (1,5,6,20)))
new.put(items,rom[items-0x08000000:items-0x08000000+461*32])
GRID=0x02026000
def geometry(m,action,dx,dy,height,residue=0):
 m.put(0x02000000,ram);grid=bytearray(bytes([16,0])*256);grid[2*((6+dy)*16+6+dx)]=16+height;m.put(GRID,grid)
 info=bytearray(16);struct.pack_into('<I',info,4,GRID);info[8]=info[13]=info[15]=16;m.put(0x02007f10,info)
 stack=STACK+residue;m.put(stack,struct.pack('<4I',6+dy,action,389,0))
 before=m.read(ACTOR,264);value=m.call(0x080a0014,ACTOR,6,6,6+dx,stack=stack);check('geometry-unit-isolation',m.read(ACTOR,264),before);return value
for action,dx,dy,height,residue in itertools.product((357,358),range(-3,4),range(-3,4),range(-5,6),(0,4)):
 check('r2-height3-native-geometry',geometry(new,action,dx,dy,height,residue),int(0<abs(dx)+abs(dy)<=2 and abs(height)<=3))
for action,residue in itertools.product(range(347),(0,4)):
 check('original-native-geometry',geometry(new,action,1,0,0,residue),geometry(old,action,1,0,0,residue))
def formula(action,element,affinity,restorative,residue):
 new.put(0x02000000,ram);new.put(0x03000000,iwram);new.put(items,rom[items-0x08000000:items-0x08000000+461*32]);new.put(ACTOR+0x2a,struct.pack('<5H',389,52,0,0,0))
 new.put(items+389*32+9,bytes([element]));new.put(TARGET+0x0d,bytes([affinity]));new.put(items+389*32+26,b'\0'*3);new.put(items+52*32+26,b'\0'*3)
 if restorative:new.put(items+(389 if restorative==1 else 52)*32+26,b'\x3f')
 new.put(context,struct.pack('<II',ACTOR,TARGET));new.put(context+12,struct.pack('<H',action));new.put(context+0x26,b'\x10\0')
 before=new.read(ACTOR,264)+new.read(TARGET,264);v=new.call(symbols['ffta_physical_magnitude_entry'],context,stack=STACK+residue)
 check('formula-unit-isolation',new.read(ACTOR,264)+new.read(TARGET,264),before)
 return v-0x100000000 if v&0x80000000 else v
for action,residue in itertools.product((357,358),(0,4)):
 reference_p=formula(action,0,0,0,residue)
 for element,affinity,restorative in itertools.product((0,1),range(5),range(3)):
  check('non-elemental-restorative-P',formula(action,element,affinity,restorative,residue),-reference_p if restorative==1 else reference_p)
R=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12,UC_ARM_REG_SP,UC_ARM_REG_LR]
traces=[]
def components(u,pc,size,_):
 if pc==0x0812fe38:traces.append((pc,u.reg_read(UC_ARM_REG_R3),new.word(u.reg_read(UC_ARM_REG_SP)+4)))
 elif pc in (0x080a25a2,0x080a29e8):traces.append((pc,0,0))
new.u.hook_add(UC_HOOK_CODE,components)
def execute(m,action,hp=250,mp=49,effect=0,undead=0,seed=0,residue=0):
 m.put(0x02000000,ram);m.put(0x03000000,iwram);m.put(items,rom[items-0x08000000:items-0x08000000+461*32])
 m.put(ACTOR+0x2a,struct.pack('<5H',389,52,0,0,0));m.put(ACTOR+0x18,struct.pack('<HHHH',10,100,20,50));m.put(TARGET+0x18,struct.pack('<HHHH',hp,250,mp,49))
 m.put(TARGET+0xe9,bytes([(ram[TARGET-0x02000000+0xe9]&~8)|8*undead]));m.put(items+389*32+26,bytes([effect,0,0]))
 m.put(OBJ+0x10,struct.pack('<HH',action,389));m.put(0x030034b0,struct.pack('<I',seed));sp=SP+residue;m.put(sp,iwram[SP-0x03000000:SP-0x03000000+0x370])
 m.u.reg_write(UC_ARM_REG_CPSR,regs[16])
 for register,value in zip(R,regs):m.u.reg_write(register,value)
 m.u.reg_write(UC_ARM_REG_SP,sp);traces.clear()
 try:m.u.emu_start(0x080a24a9,0x080a3762,count=1000000)
 except UcError:
  print('Native execution fault',action,hp,mp,effect,undead,seed,residue,hex(m.u.reg_read(UC_ARM_REG_PC)),hex(m.u.reg_read(UC_ARM_REG_CPSR)));raise
 assert m.u.reg_read(UC_ARM_REG_PC)==0x080a3762
 if m is new and action in (357,358):
  check('single-primary-no-Fight',len(traces)<=1 and all(p==0x0812fe38 and item==389 and mode!=1 for p,item,mode in traces),True)
 return m.read(0x02000000,0x40000),[m.u.reg_read(r) for r in R],m.u.reg_read(UC_ARM_REG_CPSR)&0xf0000000
for action in list(range(347))+list(range(424,431)):
 for residue in (0,4):check('original-full-executor',execute(new,action,residue=residue),execute(old,action,residue=residue))
for action,seed,residue in itertools.product((357,358),range(8),(0,4)):
 p=execute(reference,action,seed=seed,residue=residue)[0];q=execute(new,action,seed=seed,residue=residue)[0]
 p=250-struct.unpack_from('<H',p,TARGET-0x02000000+0x18)[0];q=250-struct.unpack_from('<H',q,TARGET-0x02000000+0x18)[0]
 check('independent-native-P-coefficient',q,p*(95 if action==357 else 75)//100)
# Full original law selector, with real heap allocation/copies for status laws.
# Kind10 is the native weapon-category law. Custom arts use only primary389
# (category1); a stronger offhand52 (category5) must not alter this decision.
LAW=0x0203e000
def law(m,action,kind,value,residue=0):
 m.put(0x02000000,ram);m.put(0x03000000,iwram);m.put(ACTOR+0x2a,struct.pack('<5H',389,52,0,0,0))
 m.put(ACTOR+0x18,struct.pack('<HHHH',10,100,20,50));m.put(TARGET+0x18,struct.pack('<HHHH',250,250,49,49))
 m.put(LAW,bytes([0,0,0,0,kind,value,0,0,0,0,0,0]));sp=STACK+residue;m.put(sp,struct.pack('<4I',0,389,0,LAW))
 before=m.read(0x02000000,0x40000);v=m.call(0x081343c8,ACTOR,TARGET,action,0,stack=sp);after=m.read(0x02000000,0x40000)
 check('law-live-source-isolation',after[:0x1940]+after[TARGET-0x02000000:TARGET-0x02000000+264]+after[0x3c000:],before[:0x1940]+before[TARGET-0x02000000:TARGET-0x02000000+264]+before[0x3c000:])
 return v,after
for action in range(347):
 for kind in range(1,21):check('original-all-law-kinds',law(new,action,kind,25),law(old,action,kind,25))
for action,kind,value,residue in itertools.product((357,358),(2,10,15,16),(1,5,25),(0,4)):
 v,_=law(new,action,kind,value,residue)
 if kind==10:check('primary-only-weapon-law',v,int(value==1))
 elif kind==2:check('non-elemental-law',v,0)
 elif kind in (15,16):check('no-status-law-rider',v,0)
outcomes=[]
for action,hp,mp,effect,undead,seed,residue in itertools.product((357,358),(3,250),(0,3,49),(0,0x3d,0x3e,0x3f),(0,1),(0,1),(0,4)):
 result=execute(new,action,hp,mp,effect,undead,seed,residue)[0];ao=ACTOR-0x02000000;to=TARGET-0x02000000;oo=OBJ-0x02000000
 left=struct.unpack_from('<H',result,to+0x18)[0];removed=max(0,hp-left)
 if action==357:
  gain=min(removed//2,20);gain=gain if undead else min(gain,90);expected=gain if undead else -gain
  check('HP-drain-bookkeeping',struct.unpack_from('<h',result,oo+6)[0],expected)
  check('HP-art-no-MP-rider',struct.unpack_from('<H',result,to+0x1c)[0],mp)
 else:
  loss=min(removed//5,16,mp);recovery=min(loss,20 if undead else 30)
  check('MP-actual-target-loss',struct.unpack_from('<H',result,to+0x1c)[0],mp-loss)
  check('MP-actual-actor-recovery',struct.unpack_from('<H',result,ao+0x1c)[0],20+(recovery if not undead else -recovery))
 if effect==0x3f:check('restorative-no-drain',removed,0)
 if hp==250 and mp==49 and not effect and not residue:outcomes.append(dict(action=action,undead=undead,seed=seed,removed=removed))
check('aligned-C-entries',set(alignment),{0})
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(counts),total=sum(counts.values()),outcomes=outcomes,scope='Private resource/native executor/geometry/law regression; fresh actual UI acceptance is separate')
(OUT/'native-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
