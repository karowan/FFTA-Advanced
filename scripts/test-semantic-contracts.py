"""Focused approved-contract corrections, using one exact-ROM native capture.

Selectors keep the medicine and Spellblade checks independently resumable.
Declared inputs never inject paid, hit, damage or reaction outcomes.
"""
import collections, datetime, hashlib, itertools, json, pathlib, struct, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
source = ROOT/'scripts/test-integrated-bard.py'
ns = {'__file__': str(source), '__name__': 'semantic_fixture'}
exec(compile(source.read_text(encoding='utf-8').split('# Native command flags')[0], str(source), 'exec'), ns)
m, S, meta, OUT, A, T, C, STACK, regs, setup, call, job, hp, half, equip = (
    ns[k] for k in ('m', 'S', 'meta', 'OUT', 'ACTOR', 'ENEMY', 'CTX', 'STACK',
                   'regs', 'setup', 'call', 'job', 'hp', 'half', 'equip'))
wrappers = ns['ns']['wrappers'] if 'wrappers' in ns['ns'] else ns['wrappers']
selector = sys.argv[1] if len(sys.argv)>1 else 'all'
assert selector in ('all', 'medicine', 'spellblade', 'parry')
counts, failures, cases = collections.Counter(), [], []
case = None
result = OUT/('semantic-contracts-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
result.mkdir()


def check(name, actual, expected=True):
    counts[name] += 1
    if actual != expected:
        failures.append(dict(case=case, check=name, actual=actual, expected=expected))


def protected():
    return (m.read(A,264)+m.read(T,264)+m.read(call('ffta_job_state',A),22)
            +m.read(call('ffta_job_state',T),22)+m.read(0x02001940,512)+m.read(0x030034b0,4))


def execute(action, actor=A, target=T, choice=0):
    m.put(regs[13],struct.pack('<4I',action,choice,0,255))
    x,y=m.read(target+0xf6,2)
    return m.call(0x080a433c,regs[0],wrappers[actor],x,y,stack=regs[13])


def medicine():
    global case
    # Base floor precedes combined multipliers; test both sides of each clamp,
    # fractional bases and missing-HP saturation with legal separate supports.
    for maximum, missing, pharm, recup in itertools.product(
            (249,250,251,257,301,307,499,500,501), (1,200), (False,True), (False,True)):
        case=('Healing Mist',maximum,missing,pharm,recup)
        setup(387);job(A,5,122);job(T,1,2);hp(T,maximum-min(missing,maximum-1),maximum)
        for item in (362,363):m.put(0x02001940+item,b'\x03')
        if pharm:equip(A,'CHM-S1')
        if recup:equip(T,'SLD-AX-S1')
        expected=min(missing,maximum-1,max(50,min(100,maximum//5))*(3 if pharm else 2)*(3 if recup else 2)//4)
        before=protected()
        check('recipe-floor-and-combined-supports',call('ffta_integrated_item_healing',C),expected)
        check('formula-query-pure',protected(),before)
        row=0x0202f000;m.put(row,bytes(20));m.put(STACK,bytes(8))
        m.put(m.word(0x0200f438)+4,b'\0')
        m.call(0x080c2618,row,wrappers[A],wrappers[T],387,stack=STACK)
        value=struct.unpack_from('<h',m.read(row,20),12)[0]
        check('AI-recipient-score',value,-2*expected)
        check('AI-row-pure',protected(),before)
        m.put(0x02015488,struct.pack('<IIHH',wrappers[A],wrappers[T],387,0))
        score=m.call(0x080bdecc,wrappers[A],wrappers[T],387,0,stack=STACK)
        check('AI-placement-score',score if score<0x80000000 else score-0x100000000,-2*expected)
        check('AI-placement-pure',protected(),before)
    # Real native result execution consumes the two ingredients once and sends
    # the corrected magnitude to HP, with no result or hit supplied by the test.
    for maximum,pharm,recup in itertools.product((257,307,499,501),(False,True),(False,True)):
        case=('medicine execution',maximum,pharm,recup)
        setup(387);job(A,5,122);job(T,1,2);hp(T,1,maximum)
        for item in (362,363):m.put(0x02001940+item,b'\x03')
        if pharm:equip(A,'CHM-S1')
        if recup:equip(T,'SLD-AX-S1')
        expected=max(50,min(100,maximum//5))*(3 if pharm else 2)*(3 if recup else 2)//4
        execute(387)
        check('actual-recipient-HP',half(T+0x18),1+expected)
        check('atomic-two-item-payment',list(m.read(0x02001940+362,2)),[2,2])
        check('transients-retired',m.read(0x0203ff44,8)==bytes(8))
        cases.append(dict(case=case,restored=expected))


def spellblade():
    global case
    setup(410)
    table=m.word(0x08079aec)
    for item in range(461):
        case=('all-item-categories',item)
        category=m.read(table+32*item+8,1)[0]
        check('rapier-saber-only',bool(call('ffta_myk_weapon',item)),bool(item and category in (3,8)))
    for weapon,action,silenced in itertools.product((35,74,88,440),range(410,424),(False,True)):
        case=('Spellblade access',weapon,action,silenced)
        setup(action);job(A,4,125);m.put(A+0x2a,struct.pack('<H',weapon));m.put(T+0x29,b'\x80')
        hp(A,300,500,99);hp(T,500,500,99)
        if action==421:m.put(T+0xeb,b'\x02');m.put(C+14,struct.pack('<H',8))
        if action==422:call('ffta_myk_grant',A,1)
        if silenced:m.put(A+0xeb,b'\x08')
        expected=weapon!=74 and not silenced
        before=protected()
        check('command-recipient-admission',bool(call('ffta_myk_eligibility',C)),expected)
        check('native-command-admission',bool(m.call(0x08133e18,A,action,128,stack=STACK)),expected)
        check('admission-pure',protected(),before)
    for weapon,kind in itertools.product((35,74,88,440),range(1,12)):
        case=('Spellblade state',weapon,kind)
        setup(410);job(A,4,125);m.put(A+0x2a,struct.pack('<H',weapon))
        call('ffta_myk_grant',A,kind)
        check('enchantment-weapon-family',call('ffta_myk_enchantment',A),kind if weapon!=74 else 0)
        m.put(A+0xeb,b'\x08')
        check('Silence-keeps-prepared-Fight',call('ffta_myk_enchantment',A),kind if weapon!=74 else 0)
        m.put(A+0x2a,struct.pack('<H',88 if weapon!=88 else 35))
        call('ffta_myk_event',A,8)
        check('primary-replacement-clears-fuel',call('ffta_myk_enchantment',A),0)
    # Native committed command paths with both approved families, covering
    # preparation, independent Spellbreak, Release and status-only Break.
    positive=collections.Counter()
    for weapon,action,seed in itertools.product((35,88),range(410,424),(0,3)):
        case=('Spellblade execution',weapon,action,seed)
        setup(action,seed);job(A,4,125);m.put(A+0x2a,struct.pack('<H',weapon));m.put(T+0x29,b'\x80')
        hp(A,300,500,99);hp(T,500,500,99)
        if action==421:m.put(T+0xeb,b'\x02')
        if action==422:call('ffta_myk_grant',A,1)
        execute(action,choice=8 if action==421 else 0)
        cost=(6,6,6,6,10,8,12,20,12,8,12,10,14,24)[action-410]
        siphon=99-half(T+0x1c) if action==419 else 0
        check('native-single-command-payment',half(A+0x1c),99-cost+siphon)
        check('native-enchantment-result',call('ffta_myk_enchantment',A),action-409 if action<=420 else 0)
        if half(T+0x18)<500:positive[weapon]+=1
        check('transients-retired',m.read(0x0203ff44,8)==bytes(8))
        cases.append(dict(case=case,loss=500-half(T+0x18),mp=half(A+0x1c)))
    for weapon in (35,88):check('native-damage-nonvacuous',positive[weapon]>0)


def parry():
    global case
    from unicorn import UC_HOOK_CODE
    from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2
    hits=[];positive=collections.Counter();misses=0
    def observe(u,pc,size,data):
        hits.append(tuple(u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)))
    address=S['ffta_myk_parry_hit']
    observer=m.u.hook_add(UC_HOOK_CODE,observe,begin=address,end=address)
    for weapon,seed in itertools.product((35,74,88),range(8)):
        pair=[]
        for reaction in (False,True):
            case=('Spell Parry',weapon,seed,reaction)
            setup(0,seed);job(A,1,2);job(T,4,125)
            m.put(T+0x2a,struct.pack('<H',weapon));m.put(T+0x29,b'\x80')
            hp(T,500,500,99);m.put(A+0x2a,struct.pack('<H',1))
            if reaction:equip(T,'MYK-R2')
            call('ffta_myk_grant',T,1)
            check('parry-ready-approved-family',bool(call('ffta_additional_extension_reaction_flags',T)),reaction and weapon!=74)
            hits.clear();execute(0)
            hit=(A,T,0) in hits
            check('hit-spends-miss-preserves',call('ffta_myk_enchantment',T),0 if weapon==74 or reaction and hit else 1)
            pair.append(500-half(T+0x18))
            if reaction:
                if hit:positive[weapon]+=1
                else:misses+=1
        check('actual-Parry-reduction',pair[1],pair[0]//2 if weapon!=74 else pair[0])
        cases.append(dict(case=case,baseLoss=pair[0],parriedLoss=pair[1]))
    m.u.hook_del(observer)
    for weapon in (35,74,88):check('native-hit-nonvacuous',positive[weapon]>0)
    check('native-miss-nonvacuous',misses>0)


try:
    if selector in ('all','medicine'):medicine()
    if selector in ('all','spellblade'):spellblade()
    if selector in ('all','spellblade','parry'):parry()
except Exception as exc:
    failures.append(dict(case=case,exception=repr(exc)))
report=dict(passed=not failures,selector=selector,romSha1=meta['romSha1'],
            capture={p.name:hashlib.sha1(p.read_bytes()).hexdigest() for p in
                     (OUT/'executor').glob('execute-trap.*')},checks=dict(counts),
            total=sum(counts.values()),cases=cases,failures=failures,
            limits=['Native controlled-input consumers; final player UI/campaign acceptance remains separate.'])
(result/'report.json').write_text(json.dumps(report,indent=2,default=lambda x:x.hex() if isinstance(x,bytes) else str(x)),encoding='utf-8')
print(json.dumps(dict(passed=report['passed'],total=report['total'],report=str(result/'report.json'),failures=failures),indent=2,default=str))
assert not failures
