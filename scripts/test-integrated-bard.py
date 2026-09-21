"""Eight native Bard songs, exact timed buffs, snapshot copies and shared factors."""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-synergies.py';ns={'__file__':str(source),'__name__':'bard_fixture'}
exec(compile(source.read_text().split('reset()\nkatana=')[0],str(source),'exec'),ns)
tree=ns['ast'].parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ns['ast'].Module(body=[x for x in tree.body if isinstance(x,ns['ast'].ClassDef) and x.name=='ARM'],type_ignores=[]),'<ARM>','exec'),ns)
m=ns['ARM'](ns['rom'],ns['iw']);ns['m']=m
S,meta,OUT,ram,iw=(ns[k] for k in ('S','meta','OUT','ram','iw'))
ENEMY,ACTOR,CTX,STACK=(ns[k] for k in ('UNIT','TARGET','CTX','STACK'))
reset,call,context,equip=(ns[k] for k in ('reset','call','context','equip'))
from native_battle_wrappers import from_memory
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(ns['rom'],ram,iw).items()}
regs=struct.unpack_from('<17I',(OUT/'executor/execute-trap.state').read_bytes(),0x20)
checks=collections.Counter();samples=[];case=None
half=lambda p:int.from_bytes(m.read(p,2),'little')
def check(k,a,b):checks[k]+=1;assert a==b,(k,a,b,case)
def hp(u,current=1,maximum=307,mp=50):m.put(u+0x18,struct.pack('<4H',current,maximum,mp,100))
def job(u,r,j):m.put(u+5,bytes((j,r,j)));m.put(u+0x35,bytes((j,)))
def setup(action,seed=0):
    reset();job(ACTOR,5,123);job(ENEMY,1,2);hp(ACTOR,300,307);hp(ENEMY)
    m.put(ACTOR+0x20,struct.pack('<4H',70,40,80,40));m.put(ENEMY+0x20,struct.pack('<4H',70,40,40,30))
    # The original monster fixture absorbs Holy. Declare neutral affinity for
    # the ordinary damage control; exercise all five native affinities below.
    m.put(ENEMY+0x13,b'\x01')
    for u,w in wrappers.items():
        x,y=(4,14) if u==ACTOR else (5,14) if u==ENEMY else (0,0)
        m.put(u+0xf6,bytes((x,y)));m.put(w+8,struct.pack('<3H',x*32+16,32,y*32+16))
    m.put(ENEMY+0x29,bytes((128 if action==396 else 0,)))
    if action==396:hp(ENEMY,307,307);m.put(ENEMY+0xe9,b'\x08')
    m.put(0x030034b0,struct.pack('<I',seed));m.put(regs[13],struct.pack('<4I',action,0,0,255))
    context(action);m.put(CTX,struct.pack('<III',ACTOR,ENEMY,ENEMY))
def execute(action):
    return m.call(0x080a433c,regs[0],wrappers[ACTOR],4 if action==398 else 5,14,stack=regs[13])
def status(u,bit):return bool(m.read(u+0xe8+bit//8,1)[0]&(1<<(bit%8)))
def give(u,magic,own=False):
    p=call('ffta_job_state',u);v=m.read(p+10,1)[0];shift=3 if magic else 0
    m.put(p+10,bytes(((v&~(7<<shift))|((6 if own else 2)<<shift),)))

# Native command flags, zero weapon requirement, exact costs, recipients and
# all eight real effect paths. Every fixed seed is retained, including misses.
costs={393:8,394:12,395:12,396:8,397:12,398:0,399:0,400:24}
for action,seed in itertools.product(range(393,401),range(8)):
    case=('native-song',action,seed);setup(action,seed)
    if action==393:
        for bit in (9,10,27,28):m.put(ENEMY+0xe8+bit//8,bytes((m.read(ENEMY+0xe8+bit//8,1)[0]|(1<<(bit%8)),)))
    before=half(ACTOR+0x1c);execute(action)
    check('native-once-MP-payment',before-half(ACTOR+0x1c),costs[action])
    if action==393:
        check('Soul-Etude-healing',half(ENEMY+0x18),123)
        for bit in (9,10,27,28):check('Soul-Etude-cure',status(ENEMY,bit),False)
    if action in (394,400):check('ordinary-Protect',status(ENEMY,25),True)
    if action in (395,400):check('ordinary-Shell',status(ENEMY,24),True)
    if action in (397,400):check('ordinary-Regen',status(ENEMY,3),True)
    if action in (394,395):check('timed-song-buff',call('ffta_bard_buff',ENEMY,action==395),1)
    if action==397:check('Angelsong-healing',half(ENEMY+0x18),62)
    if action==398:check('native-Invisible',status(ACTOR,12),True)
    if action==399:check('Magick-Ballad-MP',half(ENEMY+0x1c),70)
    if action==396:
        samples.append(dict(seed=seed,requiemHP=half(ENEMY+0x18),result=m.read(regs[0],80).hex()))
        (OUT/'bard-damage-samples.json').write_text(json.dumps(samples,indent=2))
    check('retired-transient-roots',m.read(0x0203ff44,8),bytes(8))
    for flag in (18,19,26):check('no-Reflect-Doublecast-ReturnMagic',m.call(0x080ccd50,action,flag,stack=STACK),0)
check('Requiem-actual-positive-damage',any(x['requiemHP']<307 for x in samples),True)

for affinity,seed in itertools.product(range(5),range(8)):
    case=('Requiem-affinity',affinity,seed);setup(396,seed);hp(ENEMY,150,307)
    m.put(ENEMY+0x13,bytes((affinity,)));execute(396)
    amount=struct.unpack('<h',m.read(regs[0]+0x20+0x1e,2))[0]
    if affinity==2:check('Holy-immunity',half(ENEMY+0x18),150)
    elif amount:
        check('native-Holy-affinity-sign',amount<0,affinity==3)
        check('native-Holy-HP-application',half(ENEMY+0x18),150-amount)

# Exact eligibility for ordinary party targeting and Silence, including Hide
# exception and Requiem's undead-enemy restriction. No law/AI result injection.
for action,silenced,self_target,enemy,undead in itertools.product(range(393,401),*( (False,True),)*4):
    case=('eligibility',action,silenced,self_target,enemy,undead);setup(action)
    t=ACTOR if self_target else ENEMY;m.put(CTX+4,struct.pack('<II',t,t))
    if silenced:m.put(ACTOR+0xeb,b'\x08')
    m.put(t+0x29,bytes((128 if enemy else 0,)));m.put(t+0xe9,bytes((8 if undead else 0,)))
    hostile=(m.read(ACTOR+0x29,1)[0]>>7)!=(m.read(t+0x29,1)[0]>>7)
    expected=self_target if action==398 else (not silenced and (hostile and undead if action==396 else not hostile and (not undead if action in (393,397) else True) and (not self_target if action==399 else True)))
    check('song-eligibility',call('ffta_bard_eligibility',CTX),int(expected))

# Rational healing and incoming Recuperation, missing HP and no item boost.
for action,maximum,missing,recup in itertools.product((393,397),(101,307,399,400,401,999),(1,30,300),(False,True)):
    case=('healing',action,maximum,missing,recup);setup(action);hp(ENEMY,max(1,maximum-missing),maximum)
    if recup:
        lesson=next(l for l in ns['registry']['lessons'] if l['id']=='SLD-AX-S1');index=lesson['owners'][0]['abilityIndex']
        m.put(ENEMY+0x3b,bytes((index,)));m.put(0x02001b40+index-144 if index>=144 else ENEMY+0x40+index,b'\xff')
    base=min(maximum*(40 if action==393 else 20),16000 if action==393 else 8000)
    expected=min(maximum-half(ENEMY+0x18),base*(3 if recup else 2)//200)
    before=m.read(0x02000000,0x40000);rng=m.read(0x030034b0,4)
    check('rational-healing',call('ffta_integrated_technique_healing',CTX),expected)
    check('preview-purity',m.read(0x02000000,0x40000)==before and m.read(0x030034b0,4)==rng,True)

# Freeze both buffs independently for a whole action; exact copies preserve
# the tag, and a nested query cannot observe later changes. Full820-byte
# retirement and nonoverlapping declared frames exercise the new storage.
for initial in range(4):
    case=('snapshot',initial);setup(394)
    for magic in (0,1):
        if initial&(1<<magic):give(ACTOR,magic)
    frame,child,copy=0x03007500,0x03006f00,0x02028000
    m.put(call('ffta_integrated_snapshot_storage'),bytes(2080));m.put(call('ffta_additional_extension_snapshot_storage'),bytes(1024));m.put(0x0203f220,b'\xd7'*0x1e0)
    call('ffta_snapshot_begin',frame,ACTOR,ENEMY,1);call('ffta_action_started',ACTOR,0,1,1)
    check('frozen-extra-flags',call('ffta_action_unit_extra_flags',ACTOR),initial)
    give(ACTOR,0);give(ACTOR,1)
    check('new-status-no-same-action-bonus',call('ffta_action_unit_extra_flags',ACTOR),initial)
    m.put(copy,m.read(ACTOR,264));call('ffta_snapshot_copy',copy,ACTOR)
    check('copied-extra-flags',call('ffta_action_unit_extra_flags',copy),initial)
    call('ffta_snapshot_begin',child,copy,ENEMY,0)
    check('nested-extra-flags',call('ffta_action_unit_extra_flags',copy),initial)
    call('ffta_snapshot_end',child);check('child-retirement',m.read(child,820),bytes(820))
    call('ffta_snapshot_end',frame);check('parent-retirement',m.read(frame,820),bytes(820))
    check('external-slots-retired',m.read(call('ffta_integrated_snapshot_storage'),2080),bytes(2080))
    check('extension-slots-retired',m.read(call('ffta_additional_extension_snapshot_storage'),1024),bytes(1024))
    check('external-bank-boundary',m.read(0x0203f220,0x1e0),b'\xd7'*0x1e0)
    check('next-action-sees-new-buffs',call('ffta_action_unit_extra_flags',ACTOR),3)

for own,event in itertools.product((False,True),range(1,9)):
    case=('lifecycle',own,event);setup(394);give(ENEMY,0,own);give(ENEMY,1,own)
    record=call('ffta_job_state',ENEMY);m.put(record+11,b'\xa5')
    call('ffta_bard_event',ENEMY,event)
    check('lifecycle-clear-domain',call('ffta_bard_snapshot_flags',ENEMY),0 if event in (2,3,4,5,7) else 3)
    check('adjacent-state-preserved',m.read(record+11,1),b'\xa5')
for own in (False,True):
    case=('timers',own);setup(394);give(ENEMY,0,own);give(ENEMY,1,own)
    for turn in range(1,4):
        call('ffta_drk_lifecycle_turn_end',ENEMY)
        check('one-composed-T2-tick',call('ffta_bard_snapshot_flags',ENEMY),3 if turn<(3 if own else 2) else 0)

# Buffs on any recipient combine with its legal support and enemy reductions.
for magic,boost,poise,raw in itertools.product((False,True),(False,True),(False,True),(1,3,17,99,511)):
    case=('factors',magic,boost,poise,raw);reset();context(23 if magic else 0)
    if boost:give(ns['UNIT'],magic)
    if poise:equip(ns['TARGET'],'SAM-S2');give(ns['TARGET'],0)
    expected=raw*(6 if boost else 5)*(3 if poise else 4)//20
    check('combined-damage-one-round',call('ffta_integrated_exposed_native_stage',raw,CTX),expected)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),samples=samples,
    limits=['Bard supports/reactions have their own test. Full visual playback, AI, teaching/acquisition and cold-save song scenarios remain separate.'])
(OUT/'bard-native.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
