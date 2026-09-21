"""Native Fight/spell/art barriers and real queued Dark Knight reactions.

Zero-rounded eligibility also has declared phase fixtures; those do not stand
in for native accuracy, AI, menu or visible-animation acceptance.
"""
import pathlib, json, struct, itertools, collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-synergies.py'
ns={'__file__':str(source),'__name__':'dark_reaction_fixture'}
exec(compile(source.read_text().split('reset()\nkatana=')[0].replace('count=50000','count=3000000'),str(source),'exec'),ns)
# ARM is extracted from its own file by the reused header; raise its complete
# executor instruction budget explicitly, without changing computed outputs.
tree=ns['ast'].parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ns['ast'].Module(body=[n for n in tree.body if isinstance(n,ns['ast'].ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'),ns)
m=ns['ARM'](ns['rom'],ns['iw']);ns['m']=m
S,meta,OUT,ram,iw=(ns[k] for k in ('S','meta','OUT','ram','iw'))
UNIT,TARGET,CTX,FRAME,STACK=(ns[k] for k in ('UNIT','TARGET','CTX','FRAME','STACK'))
reset,equip,call,record,context=(ns[k] for k in ('reset','equip','call','record','context'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0
from native_battle_wrappers import from_memory
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(ns['rom'],ram,iw).items()}
regs=struct.unpack_from('<17I',(OUT/'executor/execute-trap.state').read_bytes(),0x20)
checks=collections.Counter();samples=[];objects=[];stages=[];injuries=[];case=None
def half(p):return int.from_bytes(m.read(p,2),'little')
def check(k,a,b):
    checks[k]+=1
    if a!=b:(OUT/'dark-reactions-failure.json').write_text(json.dumps(dict(check=k,actual=a,expected=b,case=case,objects=objects,stages=stages,samples=samples[-3:]),indent=2))
    assert a==b,(k,a,b,case)
def observe(u,pc,size,data):
    obj=u.reg_read(UC_ARM_REG_R0)
    objects.append(dict(action=half(obj+0x10),actor=m.word(m.word(obj)),address=obj))
m.u.hook_add(UC_HOOK_CODE,observe,begin=S['ffta_snapshot_result'],end=S['ffta_snapshot_result'])
def magnitude_trace(u,pc,size,name):
    from unicorn.arm_const import UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR
    c=u.reg_read(UC_ARM_REG_R0)
    if half(c+12)!=434:return
    root=m.word(0x0203ff48);frames=[]
    for i in range(4):
        if not 0x03000000<=root<=0x03008000-820:break
        count=m.word(root+12)
        frames.append(dict(address=root,action=m.word(root+788),origin=m.word(root+792),phase=m.word(root+800),metadata=m.word(root+16),actor=m.word(root+812),units=[struct.unpack('<IIHH',m.read(root+20+12*j,12)) for j in range(min(count,64))]))
        root=m.word(root+8)
    item=dict(name=name,args=[u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)],context=m.read(c,52).hex(),frames=frames);stages.append(item)
    pending={}
    def returned(machine,pc,size,data):
        item['returned']=machine.reg_read(UC_ARM_REG_R0);machine.hook_del(pending['hook'])
    ret=u.reg_read(UC_ARM_REG_LR)&~1
    pending['hook']=u.hook_add(UC_HOOK_CODE,returned,begin=ret,end=ret)
for name in ('ffta_drk_reaction_magnitude','ffta_drk_zero_magnitude','ffta_integrated_eligibility'):
    m.u.hook_add(UC_HOOK_CODE,magnitude_trace,user_data=name,begin=S[name],end=S[name])
def injury_trace(u,pc,size,data):
    from unicorn.arm_const import UC_ARM_REG_R1,UC_ARM_REG_R2
    root=m.word(0x0203ff48)
    injuries.append(dict(unit=u.reg_read(UC_ARM_REG_R0),before=u.reg_read(UC_ARM_REG_R1),after=u.reg_read(UC_ARM_REG_R2),origin=m.word(root+792)))
m.u.hook_add(UC_HOOK_CODE,injury_trace,begin=S['ffta_integrated_hp_loss'],end=S['ffta_integrated_hp_loss'])

def setup(action,seed,race=1,barrier=False,poise=False,reaction=None):
    reset();objects.clear();stages.clear();injuries.clear()
    for unit in wrappers:
        xy=(4,14) if unit==UNIT else (5,14) if unit==TARGET else (0,0)
        m.put(unit+0xf6,bytes(xy));m.put(wrappers[unit]+8,struct.pack('<3H',xy[0]*32+16,32,xy[1]*32+16))
    for unit in (UNIT,TARGET):m.put(unit+0x18,struct.pack('<4H',500,500,999,999))
    m.put(UNIT+0x2a,struct.pack('<5H',384 if action in (357,361) else 399,0,0,0,0))
    if action==427:
        m.put(UNIT+5,bytes([2,1,2]));m.put(UNIT+0x35,b'\x02')
    m.put(TARGET+5,bytes([117 if race==1 else 119,race,117 if race==1 else 119]));m.put(TARGET+0x35,bytes([117 if race==1 else 119]))
    if poise:equip(TARGET,'SAM-S2');call('ffta_viking_grant_war_cry',TARGET,0)
    if reaction:equip(TARGET,reaction)
    if barrier:check('native-owned-barrier-grant',call('ffta_drk_grant_tbn',TARGET,TARGET),1)
    m.put(0x030034b0,struct.pack('<I',seed));m.put(regs[13],struct.pack('<4I',action,0,0,255))
    # Deliberately unrelated global context: Fight must use its own path.
    context(391)
def execute():
    m.call(0x080a433c,regs[0],wrappers[UNIT],5,14,stack=regs[13])
    for obj in objects:
        p=obj['address'];obj['rows']=[m.read(p+0x20+i*44,44).hex() for i in range(min(m.read(p+0x2c0,1)[0],15))]
    return dict(targetHP=half(TARGET+0x18),actorHP=half(UNIT+0x18),targetMP=half(TARGET+0x1c),
        actorMP=half(UNIT+0x1c),barrier=call('ffta_drk_tbn',TARGET),status=m.read(TARGET+0xe8,8).hex(),
        rng=m.read(0x030034b0,4).hex(),objects=list(objects),directLoss=sum(e['before']-e['after'] for e in injuries if e['unit']==TARGET and e['origin']==1))

for action,race,poise,seed in itertools.product((0,23,357,361,365,370),(1,2),(False,True),range(8)):
    if poise and race!=1:continue
    case=('barrier',action,race,poise,seed)
    setup(action,seed,race,False,poise);plain=execute()
    setup(action,seed,race,True,poise);actual=execute()
    damage=500-plain['targetHP'];warded=500-actual['targetHP']
    check('successful-damage-consumes-barrier',actual['barrier'],int(damage==0))
    check('barrier-does-not-change-accuracy-RNG',actual['rng'],plain['rng'])
    check('barrier-does-not-change-MP-price',actual['actorMP'],plain['actorMP'])
    check('barrier-never-increases-direct-injury',0<=warded<=damage,True)
    # Critical Fight retains native critical-stage rounding, separately from
    # the one-product finalizer already covered by the synergy matrix.
    if action!=0:check('ordinary-stage-halving',warded,damage//2)
    samples.append(dict(case=case,plain=plain,actual=actual))
check('nonvacuous-native-hit',any(s['plain']['targetHP']<500 for s in samples),True)
check('nonvacuous-native-miss',any(s['plain']['targetHP']==500 for s in samples),True)

# Fixed input grid varies ordinary native attack/magic stats before execution,
# never a calculated magnitude or RNG result. Run every zero/one/two-damage
# boundary found by the unwarded native control on the same warded setup.
zero_native=collections.Counter()
for action,power,seed in itertools.product((0,23,361,365,427),range(1,161,3),range(8)):
    case=('native-rounding-boundary',action,power,seed)
    setup(action,seed);m.put(UNIT+(0x24 if action in (23,365) else 0x20),struct.pack('<H',power));plain=execute()
    damage=plain['directLoss']
    if damage>2:continue
    setup(action,seed,barrier=True);m.put(UNIT+(0x24 if action in (23,365) else 0x20),struct.pack('<H',power));actual=execute()
    check('native-boundary-ward-consumption',actual['barrier'],int(damage==0))
    if damage==1:
        check('native-one-rounded-to-zero',actual['directLoss'],0)
        zero_native[action]+=1
    samples.append(dict(case=case,plain=plain,actual=actual))
for action in (0,23,361,365,427):check('nonvacuous-native-zero-rounded-hit',zero_native[action]>0,True)

# Native Damage-to-MP uses a vanilla mastered reaction found in the real racial
# table. No barrier claim or reduced MP amount is permitted on this route.
for action,seed in itertools.product((0,23,361,365),range(8)):
    case=('MP-interception',action,seed);pair=[]
    for barrier in (False,True):
        setup(action,seed,barrier=barrier)
        bank=m.word(m.word(0x080cd538)+4)
        index=next(i for i in range(142) if m.read(bank+8*i+4,3)==bytes([13,0,2]))
        m.put(TARGET+0x3a,bytes([index]));m.put(TARGET+0x40+index,b'\xff')
        pair.append(execute())
    check('MP-only-leaves-HP',pair[1]['targetHP'],500)
    check('MP-only-preserves-barrier',pair[1]['barrier'],1)
    check('MP-only-amount-unscaled',pair[1]['targetMP'],pair[0]['targetMP'])

for reaction,action,race,seed in itertools.product(('DRK-R1','DRK-R2'),(0,23,361,365),(1,2),range(8)):
    case=('queued-reaction',reaction,action,race,seed)
    setup(action,seed,race);plain=execute()
    setup(action,seed,race,reaction=reaction);actual=execute()
    loss=actual['directLoss'];magical=action in (23,365)
    eligible=loss>0 and actual['targetHP']>0 and (magical or reaction=='DRK-R2')
    hidden=433 if reaction=='DRK-R1' else 434
    check('one-actual-native-reaction-object',sum(o['action']==hidden for o in actual['objects']),int(eligible))
    if reaction=='DRK-R1':
        check('native-Shell-after-survival',bool(int.from_bytes(bytes.fromhex(actual['status']),'little')&(1<<24)),eligible)
    elif eligible:
        # Resolve affinity using the same native attribute/equipment sources;
        # arithmetic itself is the specified fixed-loss oracle.
        amount=min(loss//2,125);affinity=m.call(0x080c7ea4,UNIT,0x12,stack=STACK)
        equipment=m.call(0x0812fa90,UNIT,8,0,stack=STACK)
        if equipment:affinity=m.call(0x0812fc74,equipment,stack=STACK)
        amount={0:amount*3//2,1:amount,2:0,3:-amount,4:amount//2}[affinity]
        check('fixed-retaliation-from-actual-loss',plain['actorHP']-actual['actorHP'],amount)
    samples.append(dict(case=case,plain=plain,actual=actual))

# The return is queued once after a complete two-weapon Fight; a native
# Counter on the original attacker must not answer the custom reaction.
double_hits=0
for seed in range(16):
    case=('two-weapons-no-reaction-recursion',seed)
    setup(0,seed,reaction='DRK-R2')
    m.put(UNIT+5,bytes([117,1,117]));m.put(UNIT+0x35,b'\x75')
    m.put(UNIT+0x2a,struct.pack('<5H',383,383,0,0,0))
    bank=m.word(m.word(0x080cd538)+4)
    for kind,value,slot in ((3,7,0x3b),(2,8,0x3a)):
        index=next(i for i in range(142) if m.read(bank+8*i+4,3)==bytes([value,0,kind]))
        m.put(UNIT+slot,bytes([index]));m.put(UNIT+0x40+index,b'\xff')
    actual=execute();hits=[e for e in injuries if e['unit']==TARGET and e['origin']==1]
    double_hits+=int(len(hits)>1)
    eligible=bool(actual['directLoss'] and actual['targetHP'])
    check('two-weapons-one-return',sum(o['action']==434 for o in actual['objects']),int(eligible))
    check('queued-return-cannot-trigger-native-Counter',[(o['action'],o['actor']) for o in actual['objects']],
        [(0,UNIT),(0,UNIT)]+([(434,TARGET)] if eligible else []))
check('nonvacuous-two-direct-hit-action',double_hits>0,True)

for distance,lethal,affinity,seed in itertools.product((3,4),(False,True),range(5),range(4)):
    case=('range-survival-element',distance,lethal,affinity,seed)
    setup(23,seed,reaction='DRK-R2')
    m.put(UNIT+0x14,bytes([affinity]));m.put(UNIT+0x2a,bytes(10))
    m.put(UNIT+0xf6,bytes([5-distance,14]));m.put(wrappers[UNIT]+8,struct.pack('<H',(5-distance)*32+16))
    if lethal:m.put(TARGET+0x18,b'\x01\x00')
    actual=execute();eligible=bool(actual['directLoss'] and actual['targetHP'] and distance<=3)
    check('native-retaliation-range-and-survival',sum(o['action']==434 for o in actual['objects']),int(eligible))
    if eligible:
        amount=min(actual['directLoss']//2,125)
        expected={0:amount*3//2,1:amount,2:0,3:-amount,4:amount//2}[affinity]
        # The caster is outside the spell area; absorption caps at its full HP.
        check('native-retaliation-affinity',500-actual['actorHP'],max(0,expected))

# Exact transient flag and successful native HP writer contract at rounding
# boundaries. Poison/MP/fall routes use other writers and cannot claim this.
for raw,poise,phase in itertools.product((0,1,2,3,7),(False,True),(0,2)):
    case=('zero-rounding-API',raw,poise,phase);reset();context(0)
    if poise:equip(TARGET,'SAM-S2')
    call('ffta_drk_grant_tbn',TARGET,TARGET)
    call('ffta_snapshot_begin',FRAME,UNIT,TARGET,1);call('ffta_action_started',UNIT,0,1,1)
    m.put(FRAME+800,struct.pack('<I',phase))
    amount=call('ffta_integrated_exposed_native_stage',raw,CTX)
    expected=raw*(3 if poise else 4)//8
    check('rounded-damage',amount,expected)
    if phase==2:
        call('ffta_integrated_direct_hp_apply',TARGET,amount)
        check('positive-before-barrier-consumption',call('ffta_action_claimed',TARGET,32),int(raw*(3 if poise else 4)//4>0))
    else:check('query-cannot-mark-consumption',call('ffta_action_unit_flags',TARGET)&(1<<24),0)
    call('ffta_snapshot_end',FRAME)
report=dict(passed=True,romSha1=meta['romSha1'],scope=__doc__,checks=dict(checks),samples=samples,zeroRoundedNative=dict(zero_native),
    limitations=['Visible playback and full voluntary multi-subcast grouping remain separate obligations','Zero rounding is additionally exercised as a declared API-phase contract'])
(OUT/'dark-reactions.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
