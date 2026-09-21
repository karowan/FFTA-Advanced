"""Blade Ward: native restrictions, whole-action snapshots and combined HP factors."""
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text());ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
FIX=ROOT/'build/expansion/probes/samurai-state'/meta['baseSha1'];ram=(FIX/'execute-trap.ram').read_bytes();iw=(FIX/'execute-trap.iwram').read_bytes()
UNIT,TARGET,RETURN,STACK=0x02000080,0x020033e4,0x08000100,0x03006800
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
symbols=meta['symbols'];control=bytearray(rom)
for name,value in (('ffta_poise_factor',4),('ffta_blade_ward_factor',20)):
 p=symbols[name]-0x08000000;control[p:p+4]=bytes((value,0x20,0x70,0x47))
m,n=ARM(rom,iw),ARM(control,iw);checks=collections.Counter();samples=[]
def check(k,a,b):checks[k]+=1;assert a==b,(k,a,b)
def signed(x):return x-(1<<32) if x>>31 else x
def call(name,*args):return m.call(symbols[name],*args,stack=STACK)
def reset(machine,weapons=(383,),status=-1,poise=False,exposed=0):
 machine.put(0x02000000,ram);machine.put(0x03000000,iw);machine.put(0x0203ff44,bytes(8));machine.put(0x02001e98,bytes(108))
 for unit in (UNIT,TARGET):
  machine.put(unit+5,bytes((116,1,116)));machine.put(unit+0xe8,bytes(8));machine.put(unit+0x3a,bytes(2));machine.put(unit+0x18,struct.pack('<4H',500,500,49,49));machine.put(unit+0x2a,struct.pack('<5H',383,0,0,0,0))
 machine.put(UNIT+0x2a,struct.pack('<5H',*(tuple(weapons)+(0,)*(5-len(weapons)))))
 machine.put(UNIT+0x3a,bytes((155,154 if poise else 0)));machine.put(0x02001b4a,b'\xff\xff')
 machine.put(UNIT+0xe8,((8 if poise else 0)|(0 if status<0 else 1<<status)).to_bytes(8,'little'));machine.put(0x02001e98,bytes((exposed,)))
reset(m);bank=m.word(m.word(0x080cd538)+4)
reflex=next(i for i in range(144) if struct.unpack_from('<H',m.read(bank+8*i,8),4)[0]==5 and m.read(bank+8*i+6,1)[0]==2)
reference=0x02024000
for weapons,status in itertools.product(((),(383,),(460,),(460,383),(383,460)),range(-1,64)):
 reset(m,weapons,status);check('native_equipped_reaction',m.call(0x080cd4d4,UNIT),128)
 m.put(reference,m.read(UNIT,264));m.put(reference+0x3a,bytes((reflex,)));m.put(reference+0x40+reflex,b'\xff')
 available=m.call(0x0812e6a4,reference)==5
 ready=bool(weapons and weapons[0]==383 and available)
 check('native_Reflex_status_and_primary_weapon_contract',bool(call('ffta_blade_ward_ready',UNIT)),ready)
 check('physical_factor_when_ready',call('ffta_blade_ward_factor',TARGET,UNIT),13 if ready else 20)
 # The native high-ID guard must still block out-of-range table indexing.
 check('native_reaction_dispatch_remains_guarded',m.call(0x0812e6a4,UNIT),0)
for physical,action in ((True,0),(False,1),(False,23),(True,90),(True,112),(True,125),(True,148),(True,211),(True,266)):
 for poise,exposed,residue in itertools.product((False,True),(0,1),(0,4)):
  values=[]
  for machine in (n,m):
   reset(machine,poise=poise,exposed=0 if machine is n else exposed);sp=STACK+residue;machine.put(sp,struct.pack('<II',0,2))
   values.append(signed(machine.call(0x08130200,TARGET,UNIT,action,0,stack=sp)))
  damage=values[0];pf=3 if poise else 4;wf=13 if physical else 20;xf=6 if physical and exposed else 5
  expected=min(999,damage*pf*wf*xf//400) if damage>0 else damage
  check('native_preview_single_round',(action,poise,exposed,residue,values[1]),(action,poise,exposed,residue,expected))
  check('preview_root_retired',m.word(0x0203ff48),0)
  if damage>0:samples.append(dict(action=action,poise=poise,exposed=exposed,base=damage,ward=values[1]))
check('positive_native_categories_exercised',all(any(x['action']==a for x in samples) for a in (0,23,90,112,125,148,211,266)),True)
for action,reference_damage,poise,exposed,centered in itertools.product((347,355),(-20,0,1,7,20,37,999,25218),(False,True),(0,1),(False,True)):
 reset(m,poise=poise,exposed=exposed);m.put(0x02001eb4,bytes((4 if centered else 0,)))
 num=110 if action==347 else 80;cf=5 if action==355 and centered else 4;pf=3 if poise and reference_damage>0 else 4;xf=6 if exposed and reference_damage>0 else 5;wf=13 if reference_damage>0 else 20
 expected=abs(reference_damage)*num*cf*pf*xf*wf//160000
 if reference_damage<0:expected=-expected
 check('custom_centered_poise_exposed_single_round',signed(call('ffta_physical_final',reference_damage&0xffffffff,action,TARGET,UNIT)),expected)
# A reaction cannot apply to ally/self harm or a reaction/combination action.
for actor_side,target_side,charm in itertools.product((0,1),(0,1),(False,True)):
 reset(m);m.put(TARGET+0x28,struct.pack('<H',actor_side<<15));m.put(UNIT+0x28,struct.pack('<H',target_side<<15));m.put(TARGET+0xeb,bytes((32 if charm else 0,)))
 check('hostility_with_native_Charm',call('ffta_blade_ward_factor',TARGET,UNIT),13 if actor_side^charm!=target_side else 20)
check('self_damage_excluded',call('ffta_blade_ward_factor',UNIT,UNIT),20)
for poise in (False,True):
 values=[]
 for machine in (n,m):
  reset(machine,poise=poise);values.append(signed(machine.call(0x08130454,TARGET,UNIT,5,stack=STACK)))
 check('combo_excludes_Ward',values[1],values[0]*3//4 if poise and values[0]>0 else values[0])
scope,child,copy=0x03007500,0x03006f00,0x03007a00
for initial_weapons,later_weapons,expected in (((383,),(460,),13),((460,),(383,),20)):
 reset(m,initial_weapons);check('assigned_Ward_opens_snapshot_even_if_unready',call('ffta_snapshot_begin',scope,TARGET,UNIT,0),1)
 m.put(UNIT+0x2a,struct.pack('<5H',later_weapons[0],0,0,0,0))
 check('whole_action_weapon_snapshot',call('ffta_blade_ward_factor',TARGET,UNIT),expected)
 call('ffta_snapshotted_evaluated_init',copy,UNIT);check('copied_recipient_keeps_snapshot',call('ffta_blade_ward_factor',TARGET,copy),expected);call('ffta_snapshotted_evaluated_close',copy)
 m.put(scope+16,bytes(4));check('native_disabled_reactions_exclude_Ward',call('ffta_blade_ward_factor',TARGET,UNIT),20)
 call('ffta_snapshot_begin',child,TARGET,UNIT,0);check('nested_query_retains_disabled_reactions',call('ffta_blade_ward_factor',TARGET,UNIT),20);call('ffta_snapshot_end',child)
 call('ffta_snapshot_end',scope);check('scope_retired',m.read(scope,820),bytes(820))
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),samples=samples,scope=__doc__,remaining=['Actual game ordinary physical, magic, Counter and combo scenarios','Multi-hit and multi-cast action timing','Law/AI and legal cross-job equipment menu acceptance','Full expansion regression'])
(ROM.parent/'blade-ward-native.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
