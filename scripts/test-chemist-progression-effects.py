"""Deterministic ARM tests of the new job effects and coordinated state ABI.

Uses the existing captured native battle as input. No expected effect is
injected. This is a function-level gate, not a full playable-class claim.
"""
import ast, collections, hashlib, itertools, json, struct, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
from chemist_candidate import candidate
meta=candidate();rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
out=Path(meta['path']).parent/'effects';out.mkdir(exist_ok=True)
integrated=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
fixture=Path(integrated['path']).parent/'executor'
assert json.loads((fixture/'manifest.json').read_text())['romSha1']==integrated['romSha1']
ram=(fixture/'execute-trap.ram').read_bytes();iw=(fixture/'execute-trap.iwram').read_bytes()
UNIT,OTHER,TARGET=0x020033e4,0x020034ec,0x02000080
EQUIPMENT,RETURN,STACK,CTX=0x02002000,0x08000100,0x03006800,0x0200f3f0
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m=ARM(rom,iw);checks=collections.Counter();case=None
trace=[]
def observe(machine,pc,size,name):
 root=m.word(0x0203ff78)
 trace.append(dict(function=name,args=[machine.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)],root=root,
  frame=m.read(root+788,32).hex() if 0x02000000<=root<=0x03007ccc else None))
for name in ('ffta_snapshot_begin','ffta_cp_direct_hit','ffta_cp_hp_loss','ffta_cp_queue','ffta_action_cp_claim'):
 m.u.hook_add(UC_HOOK_CODE,observe,user_data=name,begin=meta['symbols'][name],end=meta['symbols'][name])
from native_battle_wrappers import from_memory
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()}
regs=struct.unpack_from('<17I',(fixture/'execute-trap.state').read_bytes(),0x20)
def call(n,*v):return m.call(meta['symbols'][n],*v,stack=STACK)
def check(n,a,b):
 checks[n]+=1
 assert a==b,(case,n,a,b)
def hp(u,n=100,maximum=500):m.put(u+0x18,struct.pack('<4H',n,maximum,100,100))
def record(u):
 p=call('ffta_job_state',u);assert p;return p
def reset():
 m.put(0x02000000,ram);m.put(0x03000000,iw);m.put(0x0203ff60,bytes(40));call('ffta_job_reset')
 # Retain the captured battle and its native containers, but allocate the
 # larger current manager through the game heap. An old 0x440 allocation is
 # correctly rejected by the new ownership validator; editing its size tag
 # would hide precisely the allocation bug this test needs to detect.
 old=m.word(0x0200f4b0);manager=m.call(0x08022840,0x450,stack=STACK);assert manager
 m.put(manager,m.read(old,0x3b4));m.put(manager+0x3b4,bytes(0x450-0x3b4))
 m.put(0x0200f4b0,struct.pack('<I',manager));call('ffta_battle_workspace_register',manager)
 assert call('ffta_additional_workspace_prepare')==1
 for u,job,race,side in ((UNIT,126,3,0),(TARGET,127,5,0),(OTHER,127,5,128)):
  m.put(u+5,bytes((job,race,job)));m.put(u+0x35,bytes((job,)));hp(u)
  m.put(u+0x28,bytes((0,side)));m.put(u+0x2a,bytes(10));m.put(u+0x3a,bytes(2));m.put(u+0xe8,bytes(8))
  m.put(record(u),bytes(27));m.put(u+0xf6,bytes((4 if u==UNIT else 7,10)))
def context(id,query=False):
 c=bytearray(0x34);struct.pack_into('<IIIHH',c,0,UNIT,TARGET,TARGET,id,1);c[0x26]=16 if query else 0
 m.put(CTX,c)
def passive(u,index,reaction=False):
 m.put(u+(0x3a if reaction else 0x3b),bytes((index,)));m.put(u+0x40+index,b'\xff')
 return m.call(0x080cd4d4 if reaction else 0x080cd50c,u,stack=STACK)

def execute_damage(action,seed=0,ward=False,triage=False,dressing=False,immune=False,setup=None,choice=1):
 reset();trace.clear()
 # Recipient is a Physician so its real equipped reaction can be tested.
 m.put(TARGET+5,bytes((126,3,126)));m.put(TARGET+0x35,b'\x7e')
 m.put(TARGET+0x29,b'\x80');hp(TARGET,200,500)
 for u in (UNIT,TARGET):m.put(u+0x20,struct.pack('<4H',70,40,80,40));m.put(u+0x0c,bytes([1]*8))
 if immune:m.put(TARGET+0x0d,b'\x02')
 for u,w in wrappers.items():
  x,y=(4,14) if u==UNIT else (5,14) if u==TARGET else (0,0)
  m.put(u+0xf6,bytes((x,y)));m.put(w+8,struct.pack('<3H',x*32+16,32,y*32+16))
 m.put(record(TARGET)+22,bytes(((16 if ward else 0)|(2 if triage else 0),)))
 if dressing:passive(TARGET,132,True)
 if setup:setup()
 m.put(0x030034b0,struct.pack('<I',seed));m.put(regs[13],struct.pack('<4I',action,choice if action==453 else 0,0,255))
 m.call(0x080a433c,regs[0],wrappers[UNIT],5,14,stack=regs[13])
 return int.from_bytes(m.read(TARGET+0x18,2),'little'),m.read(record(TARGET)+22,1)[0]
try:
 blind_hits=0
 for seed in range(24):
  case=('Flash native Blind and Triage',seed)
  base,_=execute_damage(454,seed,setup=lambda:m.put(TARGET+0xe9,b'\x02'))
  blind=bool(m.read(TARGET+0xe9,1)[0]&4);blind_hits+=blind
  if blind:check('Flash-Blind-requires-positive-HP',base<200,True)
  healed,_=execute_damage(454,seed,triage=True,setup=lambda:m.put(TARGET+0xe9,b'\x02'))
  check('Triage-preserves-existing-Poison',m.read(TARGET+0xe9,1)[0]&2,2)
  check('Triage-removes-new-Blind',m.read(TARGET+0xe9,1)[0]&4,0)
  immune,_=execute_damage(454,seed,setup=lambda:m.put(TARGET+0x12,b'\x02'))
  check('Flash-Lightning-immunity',immune,200)
  check('Flash-no-Blind-without-damage',m.read(TARGET+0xe9,1)[0]&4,0)
 check('Flash-Blind-nonvacuous',0<blind_hits<24,True)
 # The same native attack and RNG with/without Spotter. Put another ally
 # beside the target before the action-start snapshot, not during damage.
 for action in (453,454):
  improved=0
  for seed in range(12):
   values=[]
   for enabled in (False,True):
    def setup_spotter():
     m.put(UNIT+5,bytes((127,5,127)));m.put(UNIT+0x35,b'\x7f')
     if enabled:check('Spotter-equipped',passive(UNIT,123),147)
     m.put(UNIT+0xf6,bytes((3,14)));m.put(wrappers[UNIT]+8,struct.pack('<H',3*32+16))
     m.put(OTHER+0x29,b'\0');m.put(OTHER+0xf6,bytes((5,13)))
     m.put(wrappers[OTHER]+8,struct.pack('<3H',5*32+16,32,13*32+16))
    case=('Spotter native attack',action,seed,enabled)
    values.append(execute_damage(action,seed,setup=setup_spotter)[0])
   if values[0]<200:
    improved+=values[1]<values[0]
    check('Spotter-single-target-only',values[1]<values[0],action==453)
   elif action==454:check('Spotter-area-miss-unchanged',values[1],values[0])
  check('Spotter-nonvacuous-'+str(action),improved>0,action==453)
 # Delayed Slow must use an ordinary native roll, never an unconditional bit.
 slow_outcomes=[]
 for seed in range(24):
  case=('Trap ordinary Slow',seed);reset();m.put(TARGET+0x29,b'\x80')
  for u in (UNIT,TARGET):m.put(u+0x20,struct.pack('<4H',70,40,80,40))
  m.put(0x030034b0,struct.pack('<I',seed));bank=m.read(0x0200f390,0x94)
  call('ffta_cp_trap_slow',UNIT,TARGET)
  slow_outcomes.append(bool(m.read(TARGET+0xea,1)[0]&64))
  check('Trap-status-preserves-query-bank',m.read(0x0200f390,0x94),bank)
 check('Trap-Slow-nonvacuous',any(slow_outcomes),True)
 check('Trap-Slow-not-guaranteed',all(slow_outcomes),False)
 for seed,hit in enumerate(slow_outcomes):
  case=('Trap Astra',seed);reset();m.put(TARGET+0x29,b'\x80')
  for u in (UNIT,TARGET):m.put(u+0x20,struct.pack('<4H',70,40,80,40))
  m.put(TARGET+0xe8,b'\x10');m.put(0x030034b0,struct.pack('<I',seed))
  # Astra changes native status admission/accuracy; do not borrow the roll
  # from a different no-Astra input. Ask the actual native accuracy and RNG
  # helpers for this target, then restore the query bank and RNG before test.
  bank=m.read(0x0200f390,0x94);context(464);m.put(CTX+14,bytes(2))
  m.put(CTX+0x30,struct.pack('<I',m.word(0x0812f348)+104*4));m.put(CTX+0x28,b'\x01')
  chance=m.call(0x08131378,stack=STACK)
  native_hit=bool(m.call(0x0812f1dc,chance,stack=STACK))
  m.put(0x0200f390,bank);m.put(0x030034b0,struct.pack('<I',seed))
  call('ffta_cp_trap_slow',UNIT,TARGET)
  check('Trap-Slow-Astra-blocks',bool(m.read(TARGET+0xea,1)[0]&64),False)
  check('Trap-Slow-Astra-only-consumed-on-hit',bool(m.read(TARGET+0xe8,1)[0]&16),not native_hit)
 for icon,native in ((56,5),(57,3),(58,2),(59,16)):
  case=('native status visual',icon);reset();sprite=0x02002000
  before=m.read(0x02000000,0x40000)
  check('native-atlas-visual',call('ffta_integrated_status_visual',sprite,icon),0x143+4*native)
  check('native-atlas-alias-no-extra-storage',m.read(0x02000000,0x40000),before)
 # Exercise the complete installed lifecycle composition. Component-local
 # import aliases must not make Chemist call Viking and recurse back into
 # itself. All timers tick once, not once per wrapper in the chain.
 case='complete lifecycle chain';reset();s=record(TARGET)
 m.put(s+22,bytes((18,2)))
 call('ffta_drk_lifecycle_turn_end',TARGET)
 check('complete-chain-single-Triage-Ward-tick',m.read(s+22,1)[0],9)
 check('complete-chain-single-Smoke-tick',m.read(s+23,1)[0],1)
 call('ffta_chemist_combined_event',TARGET,4)
 check('complete-chain-clear',m.read(s+22,5),bytes(5))
 # Delayed Fire uses its own stronger native formula. Its preview cannot
 # alter HP, timers or RNG and cannot earn a second MP/action payment.
 case='Fuse elemental forecast';execute_damage(459)
 before=m.read(0x02000000,0x40000);rng=m.read(0x030034b0,4)
 damage=call('ffta_cp_fuse_damage',UNIT,TARGET)
 check('Fuse-positive-fire-reference',0<damage<=999,True)
 check('Fuse-query-preserves-RAM',m.read(0x02000000,0x40000),before)
 check('Fuse-query-preserves-RNG',m.read(0x030034b0,4),rng)
 m.put(TARGET+0x0d,b'\x02')
 check('Fuse-native-Fire-immunity',call('ffta_cp_fuse_damage',UNIT,TARGET),0)
 for timer in (1,2):
  for moved in (False,True):
   case=('Fuse end-turn admission',timer,moved);execute_damage(459)
   s=record(TARGET);owner=call('ffta_job_origin',UNIT)
   m.put(s+23,bytes((timer<<6,owner,0,5|(14<<4))))
   m.put(0x0200f4ec,struct.pack('<I',wrappers[TARGET]))
   if moved:m.put(wrappers[TARGET]+8,struct.pack('<H',6*32+16))
   call('ffta_cp_fuse_prepare',TARGET,0x0200f4e8)
   pending=call('ffta_cp_fuse_next',0x0200f4e8)
   check('Fuse-next-carrier-turn',pending,int(timer==1 and not moved))
   check('Fuse-timer-clears-or-skips',m.read(s+23,1)[0]>>6,1 if timer==2 and not moved else 0)
   if pending:
    check('Fuse-native-periodic-owner',m.word(0x0200f544),0x0200f770)
    check('Fuse-native-periodic-state',int.from_bytes(m.read(0x0200f83c,2),'little'),42)
    check('Fuse-no-extra-MP',int.from_bytes(m.read(UNIT+0x1c,2),'little'),87)
 # Breach's operand removes only the chosen defense after a positive hit.
 # A legal miss or native elemental immunity must retain both defenses.
 for choice in (1,2):
  for immune in (False,True):
   hits=0
   for seed in range(8):
    case=('Breach selected defense',choice,immune,seed)
    remaining,_=execute_damage(453,seed,immune=immune,choice=choice,setup=lambda:m.put(TARGET+0xeb,b'\x03'))
    bits=m.read(TARGET+0xeb,1)[0]&3
    if remaining<200:
     hits+=1;check('Breach-only-selected-defense',bits,1 if choice==1 else 2)
    else:check('Breach-miss-immunity-retains-defenses',bits,3)
   check('Breach-selection-has-hits',hits>0,not immune)
 # Duck and Cover uses the recipient's real learned/equipped reaction.
 def duck():
  m.put(TARGET+5,bytes((127,5,127)));m.put(TARGET+0x35,b'\x7f')
  check('Duck-native-reaction',passive(TARGET,124,True),147)
 for action in (453,454):
  hits=0
  for seed in range(8):
   case=('Duck area admission',action,seed)
   base,_=execute_damage(action,seed)
   reduced,_=execute_damage(action,seed,setup=duck)
   if base<200:
    hits+=1;check('Duck-area-only',reduced>base,action==454)
   else:check('Duck-miss',reduced,base)
  check('Duck-nonvacuous-'+str(action),hits>0,True)
 # Original Fight and Fire exercise the shared physical/magical finalizers;
 # new commands alone do not cover deferred native Fight barrier publication.
 for action in (0,23,453,454,459):
  hits=0
  for seed in range(8):
   case=('native-damage-recovery',action,seed)
   base,_=execute_damage(action,seed)
   if base==200:
    reduced,state=execute_damage(action,seed,ward=True)
    check('native-miss-preserves-Ward',(reduced,state&56),(200,16))
    continue
   hits+=1
   reduced,state=execute_damage(action,seed,ward=True)
   check('Ward-reduces-native-hit',reduced>base,True)
   check('Ward-consumed-by-hit',state&56,0)
   healed,state=execute_damage(action,seed,triage=True)
   check('Triage-queued-native-healing',healed,min(500,base+125))
   check('Triage-consumed',state&7,0)
   healed,state=execute_damage(action,seed,dressing=True)
   check('Dressing-queued-native-healing',healed,min(500,base+100))
   check('Dressing-turn-lock',state&64,64)
  check('native-charge-positive-hit-'+str(action),hits>0,True)
 # Dark Knight's barrier has a separate ledger from Trauma Ward. Its real
 # consumption must survive removing discarded ledger calculations in AI.
 # This unchanged helper remains at its authenticated inherited entry, rather
 # than being exported by the new overlay. Its job-state call is redirected.
 tbn_entry=integrated['symbols']['ffta_drk_grant_tbn']
 tbn_offset=(tbn_entry&~1)-0x08000000
 assert rom[tbn_offset:tbn_offset+32]==Path(integrated['path']).read_bytes()[tbn_offset:tbn_offset+32]
 def tbn():check('TBN-native-grant',m.call(tbn_entry,TARGET,OTHER,stack=STACK),1)
 for action in (0,23,453):
  hits=0
  for seed in range(8):
   case=('native-TBN-ledger',action,seed)
   base,_=execute_damage(action,seed)
   reduced,_=execute_damage(action,seed,setup=tbn)
   if base<200:
    hits+=1
    check('TBN-reduces-native-hit',reduced>base,True)
    check('TBN-consumed-by-real-hit',m.read(record(TARGET)+2,1),b'\x00')
   else:check('TBN-miss-retains-barrier',m.read(record(TARGET)+2,1),b'\x01')
  check('TBN-nonvacuous-'+str(action),hits>0,True)
 for action in (453,459):
  case=('immune-Ward',action);remaining,state=execute_damage(action,ward=True,immune=True)
  check('immunity-no-HP-loss',remaining,200);check('immunity-preserves-Ward',state&56,16)
 # Use the real native executor, result records and MP writer. No replacement
 # result or injected callback stands in for the installed command tables.
 for action,cost in ((446,8),(447,10),(448,12),(449,12),(450,24),(451,18),(452,20),(457,12)):
  for seed in range(4):
   case=('native-command',action,seed);reset()
   for u,w in wrappers.items():
    x,y=(4,14) if u==UNIT else (5,14) if u==TARGET else (0,0)
    m.put(u+0xf6,bytes((x,y)));m.put(w+8,struct.pack('<3H',x*32+16,32,y*32+16))
   if action==448:m.put(TARGET+0xeb,b'\x0c')
   if action==450:
    hp(TARGET,0);m.put(TARGET+0xe8,b'\x40')
   m.put(0x030034b0,struct.pack('<I',seed));m.put(regs[13],struct.pack('<4I',action,0,0,255))
   m.call(0x080a433c,regs[0],wrappers[UNIT],5,14,stack=regs[13])
   check('executor-once-MP-payment',int.from_bytes(m.read(UNIT+0x1c,2),'little'),100-cost)
   if action in (446,449,451):check('executor-healing',int.from_bytes(m.read(TARGET+0x18,2),'little'),300 if action==446 else 225)
   if action==449:check('executor-native-Regen',m.read(TARGET+0xe8,1)[0]&8,8)
   if action==450:
    check('executor-Rescue-35-percent',int.from_bytes(m.read(TARGET+0x18,2),'little'),175)
    check('executor-Rescue-clears-KO',m.read(TARGET+0xe8,1)[0]&64,0)
   if action==448:check('executor-Purge-cures',m.read(TARGET+0xeb,1)[0]&12,0)
   if action in (447,452,457):
    byte,shift={447:(22,0),452:(22,3),457:(23,0)}[action]
    check('executor-custom-buff',(m.read(record(TARGET)+byte,1)[0]>>shift)&7,2)
   for field in (18,19,26):check('command-no-spell-routing',m.call(0x080ccd50,action,field,stack=STACK),0)
   check('command-Silence-independent',m.call(0x080ccd50,action,20,stack=STACK),1)
 # Native getters must see all four new passive rows, not a guessed index.
 for cured,own in itertools.product((False,True),(False,True)):
  case=('Follow-up actual cure',cured,own);reset()
  check('Follow-up-equipped',passive(UNIT,131),146)
  target=UNIT if own else TARGET
  for u,w in wrappers.items():
   x,y=(4,14) if u==UNIT else (5,14) if u==TARGET else (0,0)
   m.put(u+0xf6,bytes((x,y)));m.put(w+8,struct.pack('<3H',x*32+16,32,y*32+16))
  if cured:m.put(target+0xeb,b'\x0c')
  m.put(0x030034b0,struct.pack('<I',0));m.put(regs[13],struct.pack('<4I',448,0,0,255))
  m.call(0x080a433c,regs[0],wrappers[UNIT],4 if own else 5,14,stack=regs[13])
  check('Follow-up-only-other-actual-cure',int.from_bytes(m.read(target+0x18,2),'little'),225 if cured and not own else 100)
  check('Follow-up-no-second-MP-charge',int.from_bytes(m.read(UNIT+0x1c,2),'little'),88)
  if cured:check('Follow-up-native-ailments-cleared',m.read(target+0xeb,1)[0]&12,0)
 for u,index,r,want in ((UNIT,131,False,146),(UNIT,132,True,146),(TARGET,123,False,147),(TARGET,124,True,147)):
  reset();check('native-passive-lookup',passive(u,index,r),want)
 for action,maxhp,current in itertools.product((446,449,451),(1,101,307,999),(1,75,999)):
  case=('healing',action,maxhp,current);reset();hp(TARGET,min(current,maxhp),maxhp);context(action,True)
  missing=maxhp-min(current,maxhp);expected=(maxhp*4+missing*5)//20 if action==446 else maxhp//4
  before=m.read(0x02000000,0x40000);rng=m.read(0x030034b0,4)
  check('exact-healing',call('ffta_cp_healing',CTX),min(missing,expected))
  check('healing-query-pure',m.read(0x02000000,0x40000)==before and m.read(0x030034b0,4)==rng,True)
 for action,enemy,ko,undead,silence in itertools.product((446,447,448,449,451,452),*( (False,True),)*4):
  case=('recipient',action,enemy,ko,undead,silence);reset();context(action)
  m.put(TARGET+0x29,bytes((128 if enemy else 0,)));hp(TARGET,0 if ko else 100)
  if undead:m.put(TARGET+0xe9,b'\x08')
  if silence:m.put(UNIT+0xeb,b'\x08')
  check('living-allied-nonundead-silence-independent',call('ffta_cp_eligibility',CTX),int(not(enemy or ko or undead)))
 for action,byte,shift in ((447,22,0),(452,22,3),(457,23,0)):
  for own in (False,True):
   case=('duration',action,own);reset();context(action)
   manager=m.word(0x0200f438);m.put(manager+24,struct.pack('<I',TARGET if own else UNIT))
   call('ffta_cp_apply',CTX);p=record(TARGET)
   check('timer-grant',(m.read(p+byte,1)[0]>>shift)&7,6 if own else 2)
   expected=(2,1,0) if own else (1,0,0)
   for e in expected:
    call('ffta_cp_turn_end',TARGET);check('recipient-turn-duration',(m.read(p+byte,1)[0]>>shift)&7,e)
 for event in range(1,9):
  case=('lifecycle',event);reset();p=record(TARGET);m.put(p+22,bytes((82,82,1,0x43,0x75)))
  before=m.read(p,22);call('ffta_cp_event',TARGET,event)
  check('older-fields-preserved',m.read(p,22),before)
  if event in (2,3,4,5):check('owned-effects-clear',m.read(p+22,5),bytes(5))
  if event==6:check('remedy-clears-only-fuse',m.read(p+22,5),bytes((82,18,0,0x43,0x75)))
  if event==7:check('dispel-preserves-trap-and-fuse',m.read(p+22,5),bytes((64,80,1,0x43,0x75)))
 for moved in (False,True):
  reset();p=record(TARGET);m.put(p+23,bytes((64,1,0,0xA7)))
  call('ffta_cp_position_changed',TARGET,8 if moved else 7,10)
  check('movement-cancels-fuse',m.read(p+23,2),bytes(2) if moved else bytes((64,1)))
 result=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),
  limits=['Function-level effects gate. Native movement, delayed playback, UI, AI, laws and cold save are separate named gates in the same plan.'])
except BaseException as e:
 (out/'failure-trace.json').write_text(json.dumps(trace[-120:],indent=2)+'\n')
 result=dict(passed=False,romSha1=meta['romSha1'],checks=dict(checks),case=case,error=repr(e));raise
finally:
 (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
