"""Native Forbidden Dance menu, cast transport and four real status effects.

Fixed fixtures and native executor only. Full AI choice search and rendered
selection/playback are separate gates; this does not claim those are covered.
"""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-dancer.py';ns={'__file__':str(source),'__name__':'choice_fixture'}
exec(compile(source.read_text().split('# The two separate native formula terms')[0],str(source),'exec'),ns)
from unicorn.arm_const import UC_ARM_REG_R2,UC_ARM_REG_R4,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R9,UC_ARM_REG_SP,UC_ARM_REG_PC
m,S,meta,OUT,A,T,C,STACK,regs=(ns[k] for k in ('m','S','meta','OUT','A','T','C','STACK','regs'))
fixture,run,half,status=(ns[k] for k in ('fixture','run','half','status'))
checks=collections.Counter();case=None;executions=[]
def check(k,a,b):checks[k]+=1;assert a==b,(k,a,b,case)
# Approved ranged crosses share native selected-center metadata. Direct
# executor fixtures cannot detect a mistaken caster-center selector; the
# player playback separately proves the actual center and two recipients.
for action in (387,394,395,396,397,400,401,402,403,406):
    case=('selected-cross',action)
    for field,wanted in ((4,3),(6,1),(7,5),(8,2)):
        check('native-selected-cross-field',m.call(0x080ccd50,action,field,stack=STACK),wanted)
for action in (351,354,398,441):
    check('native-deliberate-self-center',m.call(0x080ccd50,action,6,stack=STACK),3)
MENU,DESC,IDS,FLAGS=0x02028000,0x02028200,0x02028400,0x02028500
def text(pointer):
    data=m.read(pointer,96);return data[:data.index(0)]
def menu(entry,sp,mp=99,learned=True):
    fixture(406);m.put(A+0x35,bytes((124,124,0)));m.put(A+0x40,(b'\xff' if learned else b'\x00')*0x90)
    m.put(A+0x1c,struct.pack('<H',mp));manager=m.word(0x0200f438)
    m.put(manager+4,b'\x06');m.put(manager+24,struct.pack('<I',A))
    m.put(MENU,bytes(0xa4));m.put(MENU+10,b'\x04');m.put(MENU+0x94,struct.pack('<II',IDS,FLAGS))
    m.put(IDS-16,b'\xa5'*(16+88+16));m.put(FLAGS-16,b'\xa6'*(16+22+16));m.put(FLAGS,b'\x01'*22)
    bank=m.call(0x080cce60,A,1,DESC+4,DESC+5,stack=sp)
    m.put(DESC,struct.pack('<I',bank));m.put(DESC+6,bytes((124,0,0,0,0,0)))
    before=m.read(A,264);m.call(entry,MENU,DESC,stack=sp);count=m.read(DESC+9,1)[0]
    check('native-capacity',count<=22,True);m.put(MENU+0x84,struct.pack('<H',count))
    check('AP-read-only',m.read(A,264),before)
    for p,n,value in ((IDS-16,16,165),(IDS+88,16,165),(FLAGS-16,16,166),(FLAGS+22,16,166)):
        check('menu-guard',m.read(p,n),bytes((value,))*n)
    rows=list(struct.unpack('<'+'I'*count,m.read(IDS,count*4)))
    actions=[half(bank+i*8+4) for i in rows]
    return manager,rows,actions
for entry,sp,mp,learned in itertools.product((0x08026d44,0x08026f9c),(STACK,STACK+4),(0,99),(False,True)):
    case=('menu',entry,sp,mp,learned);manager,rows,actions=menu(entry,sp,mp,learned)
    choices=[i for i,a in enumerate(actions) if a==406]
    # The restricted native constructor is the Doublecast domain. Dances
    # must remain absent even when learned and affordable.
    check('four-choices-or-restricted-unlearned',len(choices),4 if learned and entry==0x08026d44 else 0)
    if not choices:continue
    check('one-equipment-AP-lesson',len({rows[i] for i in choices}),1)
    labels=[]
    for choice,row in enumerate(choices,1):
        pointer=m.call(0x08025758,MENU,row,stack=sp);labels.append(text(pointer))
        width=m.call(0x080161bc,pointer,stack=sp)
        check('native-menu-width',width<=m.read(DESC+7,1)[0],True)
        check('compact-choice-label',width<=13,True)
        check('MP-grey-shared',m.read(FLAGS+row,1)[0],int(mp>=14))
        check('selected-action-identity',m.call(S['ffta_dancer_menu_selected'],MENU,row,406,stack=sp),406)
        check('selected-cast-extra-halfword',half(manager+16),choice)
        m.call(0x0812f230,C,406,choice,0,stack=sp)
        vector=m.word(C+0x2c);descriptor=(87,111,125,95)[choice-1]
        check('first-descriptor-vector',m.read(vector,4),bytes((descriptor,1,1,1)))
        check('initial-descriptor-agrees',m.word(C+0x30),m.word(0x0812f2a0)+4*descriptor)
    check('four-distinct-native-labels',len(set(labels)),4)

# Native cast execution retains the choice for each recipient. No status roll,
# immunity or application callback is replaced. Include misses and require a
# positive result for every option, both while Silenced and unsilenced.
positives=collections.Counter();X=0x020034ec;wrappers=ns['ns']['wrappers']
assert X in wrappers
for choice,seed,silenced in itertools.product(range(1,5),range(8),(False,True)):
    bit=(10,27,9,28)[choice-1];case=('execute',choice,seed,silenced)
    fixture(406,seed=seed)
    m.put(X+5,bytes((2,1,2)));m.put(X+0x35,b'\x02');m.put(X+0x29,b'\x80')
    m.put(X+0x18,struct.pack('<4H',500,500,99,100));m.put(X+0xe8,bytes(8));m.put(X+0x3a,bytes(2))
    m.put(X+0xf6,bytes((6,14)));m.put(wrappers[X]+8,struct.pack('<3H',6*32+16,32,14*32+16))
    if silenced:m.put(A+0xeb,b'\x08')
    m.put(regs[13]+4,struct.pack('<I',choice))
    inventory=m.read(0x02001940,461);health=m.read(T+0x18,8)
    run(406);applied=status(T,bit);second=status(X,bit)
    positives[choice,silenced,'first']+=applied;positives[choice,silenced,'second']+=second
    check('native-single-MP-payment',half(A+0x1c),85)
    check('no-HP-MP-target-change',m.read(T+0x18,8),health)
    check('no-item-debit',m.read(0x02001940,461),inventory)
    check('no-other-ailment',sum(status(T,b) for b in (10,27,9,28) if b!=bit),0)
    check('second-target-same-choice-only',sum(status(X,b) for b in (10,27,9,28) if b!=bit),0)
    check('second-target-no-damage',half(X+0x18),500)
    check('native-roots-retired',m.read(0x0203ff44,8),bytes(8))
    executions.append(dict(choice=choice,status=bit,seed=seed,silenced=silenced,applied=applied,second=second))
for choice,silenced,target in itertools.product(range(1,5),(False,True),('first','second')):
    check('nonvacuous-status-'+str((choice,silenced,target)),positives[choice,silenced,target]>0,True)
for selected in (0,5,255,65535):
    fixture(406);m.call(0x0812f230,C,406,selected,0,stack=STACK)
    check('invalid-choice-inert',m.read(m.word(C+0x2c),4),bytes((1,1,1,1)))
for selected,ui_mode,owner_matches,action_matches in itertools.product((0,1,2,3,4,5,65535),(4,5,6,8,11,12),(False,True),(False,True)):
    fixture(406);manager=m.word(0x0200f438)
    m.put(manager+4,bytes((ui_mode,)));m.put(manager+16,struct.pack('<H',selected))
    m.put(manager+20,struct.pack('<II',406 if action_matches else 403,A if owner_matches else T))
    before=m.read(0x02000000,0x40000);rng=m.read(0x030034b0,4)
    wanted=selected if 6<=ui_mode<=11 and owner_matches and action_matches and 1<=selected<=4 else 0
    check('preview-choice-owner-and-lifetime',m.call(S['ffta_dancer_preview_choice'],A,406,416,stack=STACK),wanted)
    check('original-preview-primary-preserved',m.call(S['ffta_dancer_preview_choice'],A,403,416,stack=STACK),416)
    check('choice-query-read-only',m.read(0x02000000,0x40000)==before and m.read(0x030034b0,4)==rng,True)
    for action,extra in ((403,416),(406,wanted)):
        for sp in (STACK,STACK+4):
            for register,value in ((UC_ARM_REG_R4,action),(UC_ARM_REG_R6,416),(UC_ARM_REG_R7,T),(UC_ARM_REG_R9,A),(UC_ARM_REG_SP,sp)):
                m.u.reg_write(register,value)
            m.u.emu_start(0x080b4cf1,0x080b4cfc,count=30000)
            check('installed-target-adapter-return',m.u.reg_read(UC_ARM_REG_PC),0x080b4cfc)
            check('installed-target-adapter-SP',m.u.reg_read(UC_ARM_REG_SP),sp)
            check('installed-target-adapter-action',half(0x0200f3fc),action)
            check('installed-target-adapter-extra',half(0x0200f3fe),extra)
            check('installed-target-adapter-native-R4',m.u.reg_read(UC_ARM_REG_R4),0x0200f390)
            for entry,end in ((0x0812dbca,0x0812dbd6),(0x0813025c,0x08130268)):
                m.put(sp+0x10,struct.pack('<H',416))
                m.u.reg_write(UC_ARM_REG_R4,0x0200f3f0)
                m.u.reg_write(UC_ARM_REG_R6,A)
                m.u.reg_write(UC_ARM_REG_R7,action if entry==0x0812dbca else 416)
                m.u.reg_write(UC_ARM_REG_R2,action)
                m.u.reg_write(UC_ARM_REG_SP,sp)
                m.u.emu_start(entry|1,end,count=30000)
                check('installed-forecast-return',m.u.reg_read(UC_ARM_REG_PC),end)
                check('installed-forecast-SP',m.u.reg_read(UC_ARM_REG_SP),sp)
                check('installed-forecast-action',half(0x0200f3fc),action)
                check('installed-forecast-extra',half(0x0200f3fe),extra)
fixture(406)
forecast=[]
for choice in range(5):
    fixture(406);manager=m.word(0x0200f438)
    m.put(manager+4,b'\x06');m.put(manager+16,struct.pack('<H',choice))
    m.put(manager+20,struct.pack('<II',406,A))
    chance=m.call(0x0812dba8,A,T,406,0,stack=STACK)
    check('full-native-forecast-selected-extra',half(0x0200f3fe),choice)
    check('full-native-forecast-positive-or-inert',0<chance<=100 if choice else chance==0,True)
    forecast.append(dict(choice=choice,chance=chance))
fixture(406)
for action,sp in itertools.product(range(443),(STACK,STACK+4)):
    native=m.call(0x080ccd50,action,27,stack=STACK)
    destination=0x0809435a if action in (376,381,406,421) or native else 0x08094350
    m.put(0x02029000,struct.pack('<H',action));m.put(sp+0x64,struct.pack('<I',0x02029000))
    m.u.reg_write(UC_ARM_REG_SP,sp)
    m.u.emu_start(0x08094343,destination,count=30000)
    check('player-copy-native-branch',m.u.reg_read(UC_ARM_REG_PC),destination)
    check('player-copy-native-SP',m.u.reg_read(UC_ARM_REG_SP),sp)
    check('player-copy-native-action-pointer',m.u.reg_read(UC_ARM_REG_R4),0x02029000)
report=dict(passed=True,romSha1=meta['romSha1'],total=sum(checks.values()),checks=dict(checks),executions=executions,forecast=forecast,
            limits=['Full AI option search is unverified. Rendered player selection is covered by the separate playback report.'])
(OUT/'dancer-choice.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='executions'},indent=2))
