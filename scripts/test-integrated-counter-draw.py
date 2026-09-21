"""Counter Draw native execution, 1P reference, Centered and recursion boundaries."""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-synergies.py'
ns={'__file__':str(source),'__name__':'counter_fixture'}
exec(compile(source.read_text().split('reset()\nkatana=')[0],str(source),'exec'),ns)
tree=ns['ast'].parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ns['ast'].Module(body=[x for x in tree.body if isinstance(x,ns['ast'].ClassDef) and x.name=='ARM'],type_ignores=[]),'<ARM>','exec'),ns)
m=ns['ARM'](ns['rom'],ns['iw']);ns['m']=m
S,meta,OUT,ram,iw=(ns[k] for k in ('S','meta','OUT','ram','iw'))
UNIT,TARGET,CTX,STACK=(ns[k] for k in ('UNIT','TARGET','CTX','STACK'))
reset,equip,call,context=(ns[k] for k in ('reset','equip','call','context'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R5,UC_ARM_REG_R10
from native_battle_wrappers import from_memory
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(ns['rom'],ram,iw).items()}
regs=struct.unpack_from('<17I',(OUT/'executor/execute-trap.state').read_bytes(),0x20)
checks=collections.Counter();samples=[];objects=[];references=[];events=[];case=None
half=lambda p:int.from_bytes(m.read(p,2),'little')

def check(k,a,b):
    checks[k]+=1
    if a!=b:(OUT/'counter-draw-failure.json').write_text(json.dumps(dict(check=k,actual=a,expected=b,case=case,objects=objects,references=references,events=events,positions={hex(p):list(m.read(p+0xf6,3)) for p in (UNIT,TARGET)},samples=samples[-3:]),indent=2))
    assert a==b,(k,a,b,case)

def observe(u,pc,size,data):
    if pc==0x080a23b8:
        obj=u.reg_read(UC_ARM_REG_R0)
        objects.append(dict(action=half(obj+0x10),actor=m.word(m.word(obj)),address=obj))
    elif u.reg_read(UC_ARM_REG_R10)==435:
        value=u.reg_read(UC_ARM_REG_R5)
        references.append(value if value<0x80000000 else value-0x100000000)
m.u.hook_add(UC_HOOK_CODE,observe,begin=0x080a23b8,end=0x080a23b8)
m.u.hook_add(UC_HOOK_CODE,observe,begin=0x081300e2,end=0x081300e2)

def trace_queue(u,pc,size,data):
    frame=m.word(0x0203ff48)
    events.append(dict(phase='queue',actorXY=list(m.read(UNIT+0xf6,3)),targetXY=list(m.read(TARGET+0xf6,3)),targetStatus=m.read(TARGET+0xe8,8).hex(),
        units=[dict(unit=hex(m.word(frame+20+i*12)),flags=hex(m.word(frame+24+i*12)),loss=half(frame+28+i*12),claims=half(frame+30+i*12)) for i in range(m.word(frame+12))]))
pc=S['ffta_counter_draw_queue'];m.u.hook_add(UC_HOOK_CODE,trace_queue,begin=pc,end=pc)

def trace_loss(u,pc,size,data):
    frame=m.word(0x0203ff48)
    events.append(dict(phase='direct-loss',unit=u.reg_read(UC_ARM_REG_R0),before=u.reg_read(UC_ARM_REG_R1),
        after=u.reg_read(UC_ARM_REG_R2),origin=m.word(frame+792)))
pc=S['ffta_counter_draw_hp_loss'];m.u.hook_add(UC_HOOK_CODE,trace_loss,begin=pc,end=pc)

def expected_counter():
    # Native critical displacement precedes reaction selection. A defender
    # knocked outside katana range cannot counter, even after positive damage.
    loss=sum(max(0,e['before']-e['after']) for e in events if e['phase']=='direct-loss' and e['unit']==TARGET and e['origin']==1)
    queue=next(e for e in events if e['phase']=='queue')
    a,t=queue['actorXY'],queue['targetXY']
    return int(loss>0 and abs(a[0]-t[0])+abs(a[1]-t[1])==1)

def setup(action=0,seed=0,distance=1,katana=True,centered=False,ally=False,hp=500,blocked=False,dual=False):
    global objects,references,events
    reset();objects=[];references=[];events=[]
    for unit,w in wrappers.items():
        x,y=(4,14) if unit==UNIT else (4+distance,14) if unit==TARGET else (0,0)
        m.put(unit+0xf6,bytes((x,y,0)));m.put(w+8,struct.pack('<3H',x*32+16,32,y*32+16));m.put(w+0x1f,b'\x03')
    for unit in (UNIT,TARGET):
        m.put(unit+0x18,struct.pack('<4H',500,500,99,99));m.put(unit+0x20,struct.pack('<4H',70,40,40,40))
        m.put(unit+0xe8,bytes(8));m.put(unit+0x3a,bytes(2))
    m.put(UNIT+0x2a,struct.pack('<5H',384,384 if dual else 0,0,0,0))
    m.put(TARGET+5,bytes((116,1,116)));m.put(TARGET+0x35,b'\x74')
    m.put(TARGET+0x2a,struct.pack('<5H',377 if katana else 384,0,0,0,0));m.put(TARGET+0x18,struct.pack('<H',hp))
    if ally:m.put(UNIT+0x29,b'\0')
    equip(TARGET,'SAM-R2')
    if centered:call('ffta_centered_grant',TARGET,0)
    if blocked:m.put(TARGET+0xe8,b'\x40') # Petrify; do not substitute native transient bit31.
    m.put(0x030034b0,struct.pack('<I',seed));m.put(regs[13],struct.pack('<4I',action,0,0,255))
    context(391)

for action,centered,seed in itertools.product((0,361),(False,True),range(64)):
    case=('ordinary',action,centered,seed);setup(action,seed,centered=centered)
    m.call(0x080a433c,regs[0],wrappers[UNIT],5,14,stack=regs[13])
    damage=500-half(UNIT+0x18);loss=500-half(TARGET+0x18)
    queue=[x for x in objects if x['action']==435]
    expected=expected_counter()
    check('queue_exactly_once_after_physical_loss',len(queue),expected)
    if queue:
        check('counter_actor_is_recipient',queue[0]['actor'],TARGET)
        check('counter_single_native_P',len(references)<=1,True)
    check('actual_non_elemental_1P',damage,max(0,min(999,references[-1])) if references else 0)
    check('counter_never_consumes_centered',call('ffta_centered_active',TARGET),int(centered or damage>0))
    check('no_recursive_reaction_objects',[x['action'] for x in objects],[action]+([435] if expected else []))
    check('counter_costs_no_MP',half(TARGET+0x1c),99)
    check('transient_roots_retired',list(m.read(0x0203ff44,8)),[0]*8)
    samples.append(dict(action=action,seed=seed,initialCentered=centered,incoming=loss,counter=damage,queued=bool(queue)))
check('positive_counter_damage',any(x['counter']>0 for x in samples),True)
check('native_counter_miss',any(x['queued'] and not x['counter'] for x in samples),True)
check('incoming_native_miss',any(not x['queued'] for x in samples),True)
check('native_knockback_out_of_range',any(x['incoming'] and not x['queued'] for x in samples),True)
for kind,seed in itertools.product(('magic','range','no-katana','ally','KO','blocked'),range(16)):
    case=(kind,seed)
    setup(365 if kind=='magic' else 361,seed,distance=2 if kind=='range' else 1,
        katana=kind!='no-katana',ally=kind=='ally',hp=1 if kind=='KO' else 500,blocked=kind=='blocked')
    m.call(0x080a433c,regs[0],wrappers[UNIT],6 if kind=='range' else 5,14,stack=regs[13])
    check('rejected_counter_'+kind,[x for x in objects if x['action']==435],[])
    check('no_false_centered_'+kind,call('ffta_centered_active',TARGET),0)
for seed in range(32):
    case=('two-weapon',seed);setup(seed=seed,dual=True)
    m.call(0x080a433c,regs[0],wrappers[UNIT],5,14,stack=regs[13])
    loss=500-half(TARGET+0x18)
    check('two_hits_only_one_counter',len([x for x in objects if x['action']==435]),expected_counter())
    check('two_original_weapon_results',len([x for x in objects if x['action']==0]),2)
setup();context(435,True)
check('hidden_counter_not_query_command',call('ffta_integrated_eligibility',CTX),0)
for status in range(44):
    setup();m.put(TARGET+0xe8+status//8,bytes((1<<(status%8),)))
    native=m.call(0x080c8280,TARGET,stack=STACK)==0 and m.call(0x08133adc,TARGET+0xe8,5,stack=STACK)!=0
    check('native_status_admission_'+str(status),bool(call('ffta_counter_draw_flags',TARGET)),native and status!=6)
for item in range(461):
    check('counter_element_never_inherited',m.call(0x0812f8a4,TARGET,435,item,stack=STACK),0)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),samples=samples,
    scope=__doc__,limits=['Rendered animation and complete menu/AP/save/AI acceptance remain separate'])
(OUT/'counter-draw.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
