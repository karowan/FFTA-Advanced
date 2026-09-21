"""Deterministic action-context API contracts and read-only native transaction observations.

Isolated API cases construct phase fixtures before executing a public function.
Full executor cases only observe RAM/registers; no hook changes game outcomes.
"""
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
from native_battle_wrappers import from_memory
meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text());ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
FIX=ROOT/'build/expansion/probes/samurai-state'/meta['baseSha1'];ram=(FIX/'execute-trap.ram').read_bytes();iw=(FIX/'execute-trap.iwram').read_bytes();regs=struct.unpack_from('<17I',(FIX/'execute-trap.state').read_bytes(),0x20)
UNIT,TARGET,RETURN,STACK=0x02000080,0x020033e4,0x08000100,0x03006800
scope,child,copy=0x03007500,0x03006f00,0x03007a00
S=meta['symbols'];ROOT_POINTER=0x0203ff48
exec(compile(ast.Module(body=[n for n in ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000')).body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m=ARM(rom,iw);checks=collections.Counter();observations=[];recording=False;events=[]
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()}
def check(k,a,b):
 checks[k]+=1
 if a!=b:(ROM.parent/'action-context-failure.json').write_text(json.dumps(dict(check=k,actual=a,expected=b,events=events),indent=2))
 assert a==b,(k,a,b)
def half(address):return int.from_bytes(m.read(address,2),'little')
def call(name,*args):return m.call(S[name],*args,stack=STACK)
def reset():
 m.put(0x02000000,ram);m.put(0x03000000,iw);m.put(0x0203ff44,bytes(8));m.put(0x02001e98,bytes(108))
 for unit,x in ((TARGET,4),(UNIT,5)):
  m.put(unit+5,bytes((116,1,116)));m.put(unit+0xe8,bytes(8));m.put(unit+0x3a,bytes(2));m.put(unit+0x18,struct.pack('<4H',500,500,999,999));m.put(unit+0x2a,struct.pack('<5H',383,0,0,0,0));m.put(unit+0xf6,bytes((x,14)));m.put(wrappers[unit]+8,struct.pack('<3H',x*32+16,32,14*32+16))
def snapshot():
 p=m.word(ROOT_POINTER)
 if not p:return None
 raw=m.read(p,820);magic,self,previous,count,reactions=struct.unpack_from('<5I',raw)
 assert magic==0x31534e41 and self==p and count<=64
 units={u:dict(flags=f,lost=h,claims=c) for u,f,h,c in (struct.unpack_from('<IIHH',raw,20+12*i) for i in range(count))}
 action,origin,category,phase,paid,spent,hp,mp,actor=struct.unpack_from('<4I4HI',raw,788)
 return dict(action=action,origin=origin,category=category,phase=phase,paid=paid,spent=spent,hp=hp,mp=mp,actor=actor,reactions=reactions,units=units,resultObject=struct.unpack_from("<I",raw,816)[0])
def observe(name):
 def hook(u,pc,size,data):
  if recording:
   snap=snapshot();obj=snap['resultObject'] if snap and snap['phase']==2 else 0
   events.append(dict(hook=name,args=[u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)],snapshot=snap,objectActor=m.word(m.word(obj)) if obj else 0))
 return hook
for name in ('ffta_action_paid','ffta_action_note_hp_loss','ffta_action_completed','ffta_additional_hp_loss'):
 m.u.hook_add(UC_HOOK_CODE,observe(name),begin=S[name],end=S[name])
for pc in (0x080a2210,0x080a315a,S['ffta_samurai_apply']):
 m.u.hook_add(UC_HOOK_CODE,observe(hex(pc)),begin=pc,end=pc)
# Isolated API fixtures; native copy observers are executed, never replaced.
for phase,origin in itertools.product(range(4),range(4)):
 reset();check('battle_scope_even_without_support',call('ffta_snapshot_begin',scope,UNIT,TARGET,1),1)
 call('ffta_action_started',UNIT,347,origin,1)
 check('unpaid_MP_getter_remains_zero',call('ffta_action_post_cost_mp'),0)
 check('unpaid_debit_zero',call('ffta_action_mp_spent'),0)
 for name,value in (('id',347),('origin',origin),('category',1),('actor',UNIT),('phase',1)):
  check('metadata_'+name,call('ffta_action_'+name),value)
 original=call('ffta_action_unit_flags',UNIT);call('ffta_action_set_actor_flags',0xffffffff,0xffffffff)
 check('flags_require_paid_event',call('ffta_action_unit_flags',UNIT),original)
 m.put(UNIT+0x18,struct.pack('<4H',231,500,87,999));call('ffta_action_paid',UNIT,347)
 check('post_cost_HP',call('ffta_action_post_cost_hp'),231);check('post_cost_MP',call('ffta_action_post_cost_mp'),87);check('paid_once',call('ffta_action_paid_count'),1)
 check('actual_debit_distinct_from_payment_count',call('ffta_action_mp_spent'),912)
 call('ffta_action_paid',TARGET,347);check('recipient_cannot_pay_actor_cost',call('ffta_action_paid_count'),1)
 call('ffta_action_set_actor_flags',0xffffffff,0xffffffff);check('native_flags_protected',call('ffta_action_unit_flags',UNIT),original|0xfffffe00)
 m.put(scope+800,struct.pack('<I',phase))
 for permission in (0,1):
  m.put(scope+16,struct.pack('<I',permission))
  check('reaction_permission_phase_origin',call('ffta_action_reactions_enabled'),int(phase==2 and origin!=0 and permission!=0))
 m.put(scope+16,struct.pack('<I',1))
 allowed=int(phase in (2,3) and origin!=0)
 check('claims_phase_and_origin_admission',call('ffta_action_claim',TARGET,1),allowed)
 check('claims_once_per_recipient',call('ffta_action_claim',TARGET,1),0)
 check('claim_read',call('ffta_action_claimed',TARGET,1),allowed)
 check('separate_claim',call('ffta_action_claim',TARGET,2),allowed)
 for invalid in (0,65536,0xffffffff):check('invalid_mask_rejected',call('ffta_action_claim',TARGET,invalid),0)
 call('ffta_action_note_hp_loss',TARGET,250,210)
 expected=40 if phase==2 and origin else 0
 check('HP_loss_commit_provenance',call('ffta_action_hp_lost',TARGET),expected)
 call('ffta_action_note_hp_loss',TARGET,210,250);call('ffta_action_note_hp_loss',TARGET,210,210);call('ffta_action_note_hp_loss',UNIT,250,200)
 check('healing_and_zero_do_not_subtract',call('ffta_action_hp_lost',TARGET),expected);check('self_cost_not_incoming_loss',call('ffta_action_hp_lost',UNIT),0)
 check('evaluated_copy_created',call('ffta_snapshotted_evaluated_init',copy,TARGET),1)
 check('copy_inherits_loss',call('ffta_action_hp_lost',copy),expected);check('copy_inherits_claim',call('ffta_action_claimed',copy,1),allowed)
 call('ffta_action_note_hp_loss',copy,250,210);check('copy_loss_independent',call('ffta_action_hp_lost',TARGET),expected)
 call('ffta_snapshotted_evaluated_close',copy);check('closed_copy_retired',call('ffta_action_hp_lost',copy),0);check('closed_claim_retired',call('ffta_action_claimed',copy,1),0)
 check('query_scope_opens',call('ffta_snapshot_begin',child,UNIT,TARGET,0),1)
 check('nested_query_hides_native_result_object',call('ffta_action_result_object'),0);check('nested_query_phase',call('ffta_action_phase'),0);check('nested_query_action',call('ffta_action_id'),347)
 check('nested_query_claim_denied',call('ffta_action_claim',TARGET,4),0);call('ffta_action_note_hp_loss',TARGET,250,210)
 check('nested_query_loss_inherited_immutable',call('ffta_action_hp_lost',TARGET),expected)
 call('ffta_snapshot_end',child);check('parent_restored',m.word(ROOT_POINTER),scope)
 call('ffta_action_note_hp_loss',TARGET,65535,0);check('HP_loss_saturates',call('ffta_action_hp_lost',TARGET),65535 if phase==2 and origin else 0)
 call('ffta_snapshot_end',scope);check('scope_zeroed',m.read(scope,820),bytes(820));check('root_retired',m.word(ROOT_POINTER),0)
# Packed request metadata must never turn native permission0 into true.
for permission,kind,payload,phase in itertools.product((0,1),(128,136,255),(0,362,65535),(0,1,2,3)):
 reset();call('ffta_snapshot_begin',scope,UNIT,TARGET,1);call('ffta_action_started',UNIT,251,2,4)
 m.put(scope+800,struct.pack('<I',phase));m.put(scope+16,struct.pack('<I',permission|(kind<<8)|(payload<<16)))
 check('packed_permission_low8_only',call('ffta_action_reactions_enabled'),int(phase==2 and permission!=0))
 check('packed_kind_authenticated_RESULT',call('ffta_action_reaction_kind'),kind if phase==2 else 0)
 check('packed_value_authenticated_RESULT',call('ffta_action_reaction_value'),payload if phase==2 else 0)
 count=m.word(scope+12)
 for i in range(count):check('exact_snapshot_unit_enumeration',call('ffta_action_unit_at',i),m.word(scope+20+12*i))
 for i in (count,64,0xffffffff):check('enumeration_no_fallback',call('ffta_action_unit_at',i),0)
# Read-only observation of complete native execution. Damage-to-MP assignment is
# resolved by the native racial lesson table, independently of the extension.
reset();bank=m.word(m.word(0x080cd538)+4)
mp_lesson=next(i for i in range(144) if struct.unpack_from('<H',m.read(bank+8*i,8),4)[0]==13 and m.read(bank+8*i+6,1)[0]==2)
for action,reaction,seed in itertools.product((0,23,347,352,355),('none','mp','counter'),range(8)):
 reset()
 if reaction!='none':
  lesson=mp_lesson if reaction=='mp' else 44;m.put(TARGET+0x3a,bytes([lesson]));m.put(TARGET+0x40+lesson,b'\xff')
  check('native_reaction_oracle',m.call(0x080cd4d4,TARGET),13 if reaction=='mp' else 8)
 events=[];recording=True;m.put(0x030034b0,struct.pack('<I',seed));m.put(regs[13],struct.pack('<4I',action,0,0,255))
 m.call(0x080a433c,regs[0],wrappers[UNIT],4,14,stack=regs[13]);recording=False
 completed=[e for e in events if e['hook']=='ffta_action_completed'];check('one_primary_completion',len(completed),1)
 s=completed[0]['snapshot'];check('native_frame_is_private_at_completion',s['resultObject']==0 or 0x03000000<=s['resultObject']<0x03008000,True);check('complete_actor',s['actor'],UNIT);check('complete_action',s['action'],action);check('complete_origin',s['origin'],1)
 check('actual_target_HP_loss',s['units'][TARGET]['lost'],500-half(TARGET+0x18))
 paid=[e for e in events if e['hook']=='ffta_action_paid'];check('native_paid_event_matches_cost_path',(action,len(paid)),(action,int(action!=0)));check('payment_recorded_once',s['paid'],int(action!=0))
 # Before payment this private field is the debit baseline; after payment it
 # holds actual remaining MP. The public post-cost getter stays zero unpaid.
 check('MP_baseline_or_payment_equals_actual',s['mp'],half(UNIT+0x1c));check('post_HP_payment_precedes_counter',s['hp'],500 if action else 0)
 check('native_actual_debit_record',s['spent'],999-half(UNIT+0x1c))
 for e in events:
  if e['hook']=='ffta_action_note_hp_loss' and e['args'][1]>e['args'][2]:
   t=e['snapshot'];check('actual_loss_has_native_result_phase',t['phase'],2)
   check('origin_derived_from_actor_wrapper',t['origin'],1 if t['actor']==UNIT else 2)
   check('acting_unit_is_known',t['actor'] in (UNIT,TARGET),True)
   if t['origin']==2:check('native_counter_disables_further_reactions',t['reactions'],0)
   check('native_result_object_exact_actor',e['objectActor'],t['actor'])
 for loss in (e for e in events if e['hook']=='ffta_additional_hp_loss'):
  check('positive_HP_observer_only',loss['args'][1]>loss['args'][2],True)
  check('observer_RESULT',loss['snapshot']['phase'],2)
  check('observer_actual_committed_counter',loss['snapshot']['units'][loss['args'][0]]['lost']>=loss['args'][1]-loss['args'][2],True)
 check('native_roots_retired',m.read(0x0203ff44,8),bytes(8))
 observations.append(dict(action=action,reaction=reaction,seed=seed,targetHP=half(TARGET+0x18),targetMP=half(TARGET+0x1c),actorHP=half(UNIT+0x18),events=events))
# Held two-weapon native Fight fixture establishes aggregate transaction scope
# across both PRIMARY result objects. Equipment
# legality is independently covered by the equipment suite, not claimed here.
for seed in range(8):
 reset();m.put(UNIT+0x2a,struct.pack('<5H',383,383,0,0,0))
 check('native_two_weapon_enumerator',m.call(0x0812f0d8,UNIT,0x02023000,stack=STACK),2)
 events=[];recording=True;m.put(0x030034b0,struct.pack('<I',seed));m.put(regs[13],struct.pack('<4I',0,0,0,255))
 m.call(0x080a433c,regs[0],wrappers[UNIT],4,14,stack=regs[13]);recording=False
 completed=[e for e in events if e['hook']=='ffta_action_completed'];check('two_weapon_single_completion',len(completed),1)
 check('two_weapon_aggregate_actual_HP',completed[0]['snapshot']['units'][TARGET]['lost'],500-half(TARGET+0x18))
 observations.append(dict(action=0,reaction='two-weapon',seed=seed,targetHP=half(TARGET+0x18),targetMP=half(TARGET+0x1c),actorHP=half(UNIT+0x18),events=events))
check('positive_HP_damage_exercised',any(o['targetHP']<500 for o in observations),True)
check('MP_only_interception_exercised',any(o['reaction']=='mp' and o['targetMP']<999 and o['targetHP']==500 for o in observations),True)
check('counter_origin_exercised',any(e['hook']=='ffta_action_note_hp_loss' and e['args'][1]>e['args'][2] and e['snapshot']['origin']==2 for o in observations for e in o['events']),True)
report=dict(passed=True,romSha1=meta['romSha1'],sourceSha1=hashlib.sha1(pathlib.Path(__file__).read_bytes()).hexdigest(),checks=dict(checks),observations=observations,scope=__doc__,limits=['A433C transaction is not proven whole voluntary Doublecast','Unclassified category requires precise job provider; raw loss is not proof of direct physical/magical eligibility'])
(ROM.parent/'action-context.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='observations'},indent=2))
