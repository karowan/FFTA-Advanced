"""Soldier Recuperation/Haft Guard: rational healing, native execution and mixing."""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-synergies.py';ns={'__file__':str(source),'__name__':'soldier_fixture'}
exec(compile(source.read_text().split('reset()\nkatana=')[0],str(source),'exec'),ns)
tree=ns['ast'].parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ns['ast'].Module(body=[x for x in tree.body if isinstance(x,ns['ast'].ClassDef) and x.name=='ARM'],type_ignores=[]),'<ARM>','exec'),ns)
m=ns['ARM'](ns['rom'],ns['iw']);ns['m']=m
S,meta,OUT,ram,iw=(ns[k] for k in ('S','meta','OUT','ram','iw'))
UNIT,TARGET,CTX,STACK=(ns[k] for k in ('UNIT','TARGET','CTX','STACK'))
reset,call,context=(ns[k] for k in ('reset','call','context'))
from native_battle_wrappers import from_memory
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(ns['rom'],ram,iw).items()}
regs=struct.unpack_from('<17I',(OUT/'executor/execute-trap.state').read_bytes(),0x20)
checks=collections.Counter();samples=[];case=None
half=lambda p:int.from_bytes(m.read(p,2),'little')
def check(k,a,b):checks[k]+=1;assert a==b,(k,a,b,case)
def equip(u,ident):
    l=next(x for x in ns['registry']['lessons'] if x['id']==ident);race=m.read(u+6,1)[0]
    index=next(x['abilityIndex'] for x in l['owners'] if x['race']==race);support=l['type']=='Support'
    m.put(u+(0x3b if support else 0x3a),bytes((index,)))
    m.put(0x02001b40+index-144 if race==1 and index>=144 else u+0x40+index,b'\xff')
    check('real-equipped-lesson',m.call(0x080cd50c if support else 0x080cd4d4,u,stack=STACK),l['globalAbilityId'])
def race(u,r,j):m.put(u+5,bytes((j,r,j)));m.put(u+0x35,bytes((j,)))
def hp(u,current,maximum):m.put(u+0x18,struct.pack('<4H',current,maximum,999,999))

# Both supports are on legally different racial owners. Include fractional
# Healing Mist bases, cap boundaries, tiny missing HP and complete purity.
for action,maximum,missing,pharm,recup in itertools.product((251,252,253,383,386,387),(249,250,251,301,307,499,500,777),(1,13,200),(False,True),(False,True)):
    case=('medicine',action,maximum,missing,pharm,recup);reset();race(UNIT,5,122)
    m.put(UNIT+0x29,b'\0');hp(TARGET,maximum-min(missing,maximum-1),maximum)
    if pharm:equip(UNIT,'CHM-S1')
    if recup:equip(TARGET,'SLD-AX-S1')
    context(action);m.put(CTX+14,struct.pack('<H',363))
    base=25 if action in (251,383) else 50 if action in (252,386) else 150
    base=min(100,max(50,maximum//5)) if action==387 else base
    amount=base*(3 if pharm else 2)*(3 if recup else 2)//4
    if action>253:amount=min(amount,min(missing,maximum-1))
    before=m.read(0x02000000,0x40000);rng=m.read(0x030034b0,4)
    value=call('ffta_integrated_item_healing',CTX)
    check('single-rational-healing',value,amount)
    check('pure-healing-preview',m.read(0x02000000,0x40000)==before and m.read(0x030034b0,4)==rng,True)

for maximum,centered,recup in itertools.product((101,307,399,400,401,999),(False,True),(False,True)):
    case=('Murasame',maximum,centered,recup);reset();race(UNIT,1,116);m.put(UNIT+0x29,b'\0');hp(TARGET,1,maximum)
    if recup:equip(TARGET,'SLD-AX-S1')
    if centered:call('ffta_centered_grant',UNIT,0)
    context(350)
    expected=min(maximum-1,min(35*maximum,14000)*(5 if centered else 4)*(3 if recup else 2)//800)
    check('Centered-and-Recuperation-one-round',call('ffta_integrated_technique_healing',CTX),expected)
for maximum in (101,307,499,500,501,999):
    case=('Dark-Mind',maximum);reset();race(UNIT,1,117);hp(UNIT,1,maximum);equip(UNIT,'SLD-AX-S1');context(359);m.put(CTX+4,struct.pack('<II',UNIT,UNIT))
    check('self-technique-healing',call('ffta_integrated_technique_healing',CTX),min(maximum-1,min(20*maximum,10000)*3//200))

# Native descriptor stage: cure versus drain, revival, MP, enemy and undead.
for action,selector,expected in ((1,35,-151),(17,18,-101),(5,41,-101),(6,40,-101),(254,34,-101)):
    case=('native-selector',action);reset();m.put(UNIT+0x29,b'\0');equip(TARGET,'SLD-AX-S1');context(action)
    check('native-restoration-classification',call('ffta_integrated_restoration_stage',-101 & 0xffffffff,CTX),expected & 0xffffffff)
    m.put(UNIT+0x29,b'\x80');check('enemy-healing-unboosted',call('ffta_integrated_restoration_stage',-101 & 0xffffffff,CTX),-101 & 0xffffffff)
    m.put(UNIT+0x29,b'\0');m.put(TARGET+0xe9,b'\x08');check('undead-unboosted',call('ffta_integrated_restoration_stage',-101 & 0xffffffff,CTX),-101 & 0xffffffff)

# Native complete original and custom physical actions, with one R slot and a
# legal weapon. Pure stage checks establish exact combined rounding; native
# critical Fight retains its original later critical-stage rounding.
for action,guard,poise,seed in itertools.product((0,1,23,361,365,427),(False,True),(False,True),range(8)):
    case=('native',action,guard,poise,seed);reset();race(TARGET,1,2)
    for u,w in wrappers.items():
        x,y=(4,14) if u==UNIT else (5,14) if u==TARGET else (0,0)
        m.put(u+0xf6,bytes((x,y)));m.put(w+8,struct.pack('<3H',x*32+16,32,y*32+16))
    for u in (UNIT,TARGET):hp(u,100 if action==1 and u==TARGET else 500,500);m.put(u+0x20,struct.pack('<4H',70,40,40,40))
    m.put(UNIT+0x2a,struct.pack('<5H',399 if action==427 else 384,0,0,0,0));m.put(TARGET+0x2a,struct.pack('<5H',399,0,0,0,0))
    if action==427:race(UNIT,1,2)
    if action==1:race(UNIT,1,5);m.put(UNIT+0x29,b'\0')
    if guard:equip(TARGET,'SLD-AX-R1')
    if poise:equip(TARGET,'SAM-S2');call('ffta_viking_grant_war_cry',TARGET,0)
    context(action)
    if action==1:
        if guard:equip(TARGET,'SLD-AX-S1')
    else:
        for raw in (1,3,17,99,511):
            physical=action in (0,361,427)
            expected=raw*(3 if poise else 4)*(3 if guard and physical else 4)//16
            # custom361/427 use the combined physical finalizer separately.
            if action in (0,23,365):check('native-one-product',call('ffta_integrated_exposed_native_stage',raw,CTX),expected)
    m.put(0x030034b0,struct.pack('<I',seed));m.put(regs[13],struct.pack('<4I',action,0,0,255))
    m.call(0x080a433c,regs[0],wrappers[UNIT],5,14,stack=regs[13])
    samples.append(dict(action=action,guard=guard,poise=poise,seed=seed,hp=half(TARGET+0x18)))
    check('native-transient-retirement',m.read(0x0203ff44,8),bytes(8))
for x in samples:
    if not x['guard']:continue
    plain=next(y for y in samples if y['action']==x['action'] and not y['guard'] and y['poise']==x['poise'] and y['seed']==x['seed'])
    if x['action'] in (23,365):check('Haft-no-magic-reduction',x['hp'],plain['hp'])
    elif x['action']==1:check('native-Cure-Recuperation',x['hp']-100,(plain['hp']-100)*3//2)
    else:check('Haft-native-physical-never-increases-loss',x['hp']>=plain['hp'],True)
check('native-Cure-nonvacuous',any(x['action']==1 and x['guard'] and x['hp']>100 for x in samples),True)
check('Haft-native-physical-nonvacuous',any(x['action']==361 and x['guard'] and x['hp']>next(y['hp'] for y in samples if y['action']==361 and not y['guard'] and y['poise']==x['poise'] and y['seed']==x['seed']) for x in samples),True)

# Weapon and native reaction eligibility, copied provenance and explicit
# reaction suppression use the same shared path as Blade Ward.
for weapon,disabled in itertools.product((0,384,399),(False,True)):
    case=('Haft-eligibility',weapon,disabled);reset();equip(TARGET,'SLD-AX-R1')
    m.put(TARGET+0x2a,struct.pack('<H',weapon))
    if disabled:m.put(TARGET+0xe8,b'\x40') # Native Petrify, not an invented status.
    factor=15 if weapon==399 and not disabled else 20
    check('weapon-and-incapacity',call('ffta_blade_ward_factor',UNIT,TARGET),factor)
    frame=ns['FRAME'];copy=ns['OBJECT']
    call('ffta_snapshot_begin',frame,UNIT,TARGET,1)
    m.put(copy,m.read(TARGET,0x108));call('ffta_snapshot_copy',copy,TARGET)
    check('copied-recipient-guard',call('ffta_blade_ward_factor',UNIT,copy),factor)
    m.put(frame+16,bytes(4));check('suppressed-reactions',call('ffta_blade_ward_factor',UNIT,copy),20)
    call('ffta_snapshot_end',frame)

# Actual native execution, with player-owned medicine stock, proves the
# combined values reach HP once. The explicit recipient is a Human; the
# pharmacist is a Moogle, each with only one support slot.
for action,boost,recup,seed in itertools.product((350,383,387),(False,True),(False,True),(0,3)):
    case=('native-restoration',action,boost,recup,seed);reset()
    actor,recipient=TARGET,UNIT
    race(actor,1 if action==350 else 5,116 if action==350 else 122);race(recipient,1,2)
    for u,w in wrappers.items():
        x,y=(4,14) if u==actor else (5,14) if u==recipient else (0,0)
        m.put(u+0xf6,bytes((x,y)));m.put(w+8,struct.pack('<3H',x*32+16,32,y*32+16))
    for u in (actor,recipient):m.put(u+0x29,b'\0');hp(u,1 if u==recipient else 300,307)
    if action==350:
        katana=next(i for i in range(1,461) if m.call(0x080ca7a4,i,3,stack=STACK)==9)
        m.put(actor+0x2a,struct.pack('<H',katana))
        if boost:call('ffta_centered_grant',actor,0)
    elif boost:equip(actor,'CHM-S1')
    if recup:equip(recipient,'SLD-AX-S1')
    for item in (362,363):m.put(0x02001940+item,b'\x03')
    if action==350:expected=35*307*(5 if boost else 4)*(3 if recup else 2)//800
    else:expected=(61 if action==387 else 25)*(3 if boost else 2)*(3 if recup else 2)//4
    m.put(0x030034b0,struct.pack('<I',seed));m.put(regs[13],struct.pack('<4I',action,0,0,255))
    m.call(0x080a433c,regs[0],wrappers[actor],5,14,stack=regs[13])
    check('native-combined-restoration',half(recipient+0x18)-1,expected)
    if action!=350:
        check('native-Potion-payment',m.read(0x02001940+362,1),b'\x02')
        check('native-HiPotion-payment',m.read(0x02001940+363,1),b'\x02' if action==387 else b'\x03')
    check('native-restoration-retirement',m.read(0x0203ff44,8),bytes(8))
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),samples=samples,
    limits=['Native menu/AP/equipment/acquisition, all healing command variants, forced-action and final save acceptance remain separate.'])
(OUT/'soldier-supports.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
