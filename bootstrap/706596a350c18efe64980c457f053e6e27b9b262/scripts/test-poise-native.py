"""Native Poise arithmetic and explicit action/copy snapshot contracts."""
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text());ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
FIX=ROOT/'build/expansion/probes/samurai-state'/meta['baseSha1'];ram=(FIX/'execute-trap.ram').read_bytes();iw=(FIX/'execute-trap.iwram').read_bytes()
UNIT,TARGET,RETURN,STACK,CTX=0x02000080,0x020033e4,0x08000100,0x03006800,0x0200f3f0
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
symbols=meta['symbols'];old={p[2]:int(p[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=l.split())==3}
control=bytearray(rom);p=symbols['ffta_poise_factor']-0x08000000;control[p:p+4]=bytes.fromhex('04207047')
m,n=ARM(rom,iw),ARM(control,iw);counts=collections.Counter();samples=[]
alignment=[]
for name in ('ffta_exposed_preview','ffta_exposed_combo'):
 pc=symbols[name];m.u.hook_add(UC_HOOK_CODE,lambda u,p,s,d:alignment.append(u.reg_read(UC_ARM_REG_SP)%8),begin=pc,end=pc)
def check(k,a,b):counts[k]+=1;assert a==b,(k,a,b)
def signed(x):return x-(1<<32) if x>>31 else x
def reset(machine,job=1,status=3,exposed=0):
 machine.put(0x02000000,ram);machine.put(0x03000000,iw);machine.put(0x0203ff48,bytes(4))
 machine.put(UNIT+5,bytes((job,1,job)));machine.put(UNIT+0x3b,bytes([154]));machine.put(0x02001b4a,b'\xff')
 machine.put(UNIT+0xe8,bytes(8));machine.put(UNIT+0x18,struct.pack('<4H',250,500,50,50));machine.put(TARGET+0x18,struct.pack('<4H',250,250,50,50))
 machine.put(0x02001e98,bytes([exposed]));machine.put(0x02001eb4,b'\x00')
 if status>=0:machine.put(UNIT+0xe8+status//8,bytes([1<<(status%8)]))
def call(name,*args):return m.call(symbols[name],*args,stack=STACK)
for job,status in itertools.product((1,2,3,116),range(-1,64)):
 reset(m,job,status);check('native_cross_job_support',m.call(0x080cd50c,UNIT),129)
 check('explicit_beneficial_tags',call('ffta_poise_factor',UNIT),3 if status in (3,12,21,24,25) else 4)
for packed in range(16):
 reset(m,status=-1);m.put(0x02001e98,bytes([packed]));check('Centered_status_not_consumed_snapshot',call('ffta_poise_factor',UNIT),3 if 1<=((packed>>1)&3)<=2 else 4)
scope,child,copy=0x03007400,0x03007000,0x03007800
for initial in (-1,3):
 reset(m,status=initial);check('scope_admitted_even_without_buff',call('ffta_snapshot_begin',scope,TARGET,UNIT,0),1)
 m.put(UNIT+0xe8,bytes((8 if initial==-1 else 0,)))
 expected=4 if initial==-1 else 3
 check('gain_or_loss_cannot_change_snapshot',call('ffta_poise_factor',UNIT),expected)
 check('nested_query_opens',call('ffta_snapshot_begin',child,TARGET,UNIT,0),1)
 check('nested_query_inherits',call('ffta_poise_factor',UNIT),expected)
 call('ffta_snapshot_end',child);check('child_is_cleared',m.read(child,532),bytes(532))
 check('native_owned_evaluated_copy',m.call(symbols['ffta_snapshotted_evaluated_init'],copy,UNIT,stack=STACK),1)
 check('copy_receives_original_snapshot',call('ffta_poise_factor',copy),expected)
 m.put(copy+0xe8,bytes([8 if initial==-1 else 0]));check('copy_mutation_cannot_change_snapshot',call('ffta_poise_factor',copy),expected)
 call('ffta_snapshotted_evaluated_close',copy);check('closed_copy_is_not_an_alias',call('ffta_poise_factor',copy),4)
 # Exercise the installed native copy call sites, including real heap free.
 heap=m.call(old['ffta_evaluated_allocate'],264,stack=STACK);check('native_heap_allocated',heap>=0x02000000 and heap<0x0203f800,True)
 m.call(old['ffta_native_copy_entry'],heap,UNIT,264,stack=STACK)
 check('installed_native_copy_snapshot',call('ffta_poise_factor',heap),expected)
 m.call(0x08022854,heap,stack=STACK);check('freed_copy_is_not_an_alias',call('ffta_poise_factor',heap),4)
 # An actor copy continues its original action; a different actor starts anew.
 check('actor_copy_initialized',call('ffta_snapshotted_evaluated_init',copy,TARGET),1)
 check('copied_actor_query_opens',call('ffta_snapshot_begin',child,copy,UNIT,0),1)
 check('copied_actor_retains_action',call('ffta_poise_factor',UNIT),expected);call('ffta_snapshot_end',child)
 check('different_actor_query_opens',call('ffta_snapshot_begin',child,UNIT,TARGET,0),1)
 check('different_actor_takes_fresh_snapshot',call('ffta_poise_factor',UNIT),3 if initial==-1 else 4);call('ffta_snapshot_end',child)
 call('ffta_snapshot_end',scope);check('root_retired',m.word(0x0203ff48),0);check('scope_is_cleared',m.read(scope,532),bytes(532))
 check('after_scope_reads_current_status',call('ffta_poise_factor',UNIT),3 if initial==-1 else 4)
# Complete native preview routes. Regen has no direct defense input, allowing
# an independent no-Poise reference; Exposed and Poise must round together.
for action,exposed,residue in itertools.product((0,1,23,90,112,125,148,211,266),(0,1),(0,4)):
 values=[]
 for machine in (n,m):
  reset(machine,exposed=0 if machine is n else exposed);sp=STACK+residue;machine.put(sp,struct.pack('<II',0,2))
  values.append(signed(machine.call(0x08130200,TARGET,UNIT,action,0,stack=sp)))
 physical=action in (0,90,112,125,148,211,266);damage=values[0]
 expected=min(999,damage*(6 if exposed and physical else 5)*3//20) if damage>0 and action!=1 else damage
 check('native_preview_combines_once',(action,exposed,values[1]),(action,exposed,expected))
 check('preview_root_retired',m.word(0x0203ff48),0)
 if damage>0:samples.append(dict(action=action,exposed=exposed,base=damage,poise=values[1]))
check('physical_and_magic_covered',all(any(s['action']==a for s in samples) for a in (0,23)),True)
for exposed,residue in itertools.product((0,1),(0,4)):
 values=[]
 for machine in (n,m):
  reset(machine,exposed=0 if machine is n else exposed)
  values.append(signed(machine.call(0x08130454,TARGET,UNIT,5,stack=STACK+residue)))
 expected=min(999,values[0]*(6 if exposed else 5)*3//20) if values[0]>0 else values[0]
 check('native_combo_incoming_only',values[1],expected)
check('C_preview_and_combo_alignment',set(alignment),{0})
# New Iaido coefficients, Centered, Poise and Exposed form one rational product
# before the native final cap. Wound's captured P remains before this phase.
for action,reference,centered,exposed in itertools.product((347,355),(-250,0,1,37,999,25218),(False,True),(0,1)):
 reset(m,exposed=exposed);m.put(TARGET+0x2a,struct.pack('<5H',383,0,0,0,0));m.put(0x02001eb4,bytes([4 if centered else 0]))
 num=110 if action==347 else 80;cf=5 if centered and action==355 else 4;pf=3 if reference>0 else 4;xf=6 if reference>0 and exposed else 5
 expected=abs(reference)*num*cf*pf*xf//(100*80)
 if reference<0:expected=-expected
 check('all_custom_factors_single_round',signed(call('ffta_physical_final',reference&0xffffffff,action,TARGET,UNIT)),expected)
call('ffta_snapshot_end',0);check('null_close_is_inert',m.word(0x0203ff48),0)
# Native reaction restrictions are an independent oracle outside the damage
# callback. Cover every status bit without inventing a reaction-disable mask.
reset(m)
bank=m.word(m.word(0x080cd538)+4)
reaction=next(i for i in range(144) if struct.unpack_from('<H',m.read(bank+8*i,8),4)[0]==13 and m.read(bank+8*i+6,1)[0]==2)
for action,status in itertools.product((0,23,90,112,125,266,347,355),range(-1,64)):
 values=[];admission=[]
 for machine in (n,m):
  reset(machine,status=-1);machine.put(UNIT+0xe8,(8|(0 if status<0 else 1<<status)).to_bytes(8,'little'))
  machine.put(UNIT+0x3a,bytes([reaction]));machine.put(UNIT+0x40+reaction,b'\xff');machine.put(TARGET+0x2a,struct.pack('<5H',383,0,0,0,0))
  admitted=machine.call(0x0812e6a4,UNIT)==13 and bool(machine.call(0x0812e6e0,TARGET,UNIT,action,13,stack=STACK))
  admission.append(admitted);machine.put(STACK,struct.pack('<II',0,2))
  values.append(signed(machine.call(0x08130200,TARGET,UNIT,action,0,stack=STACK)))
 check('status_reaction_admission_preserved',admission[1],admission[0])
 expected=values[0]*3//4 if values[0]>0 and not admission[0] else values[0]
 check('status_restricted_HP_or_MP_magnitude',(action,status,values[1]),(action,status,expected))
# The executor's actual per-recipient reaction takes precedence over an
# otherwise eligible assigned reaction. Exact copies inherit that decision.
reset(m);m.put(UNIT+0x3a,bytes([reaction]));m.put(UNIT+0x40+reaction,b'\xff')
call('ffta_snapshot_begin',scope,TARGET,UNIT,0)
frame,rows,wrapper=0x02022000,0x02023000,0x02023800
m.put(frame+0x304,struct.pack('<I',1));m.put(frame+0x33c,struct.pack('<I',rows));m.put(rows+44,struct.pack('<I',wrapper));m.put(wrapper,struct.pack('<I',UNIT))
for native_reaction,expected in ((0,3),(13,4),(8,3),(13,4)):
 m.put(frame+0x30c,struct.pack('<I',native_reaction));call('ffta_snapshot_native_reaction',frame)
 check('resolved_reaction_overrides_assignment',call('ffta_poise_hp_factor',TARGET,UNIT,355),expected)
 call('ffta_snapshotted_evaluated_init',copy,UNIT)
 check('resolved_reaction_copy_provenance',call('ffta_poise_hp_factor',TARGET,copy,355),expected)
 call('ffta_snapshotted_evaluated_close',copy)
call('ffta_snapshot_end',scope);check('reaction_scope_retired',m.word(0x0203ff48),0)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(counts),samples=samples,scope=__doc__,remaining=['Native Float/custom positive statuses when implemented','Actual gameplay and AI/law acceptance','Complete action-category audit and full regression'])
(ROM.parent/'poise-native.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
