"""Cross-job factors, custom prevention and coexisting owned status lifecycles.

Native ARM code, real equipped-lesson lookup and explicit pre-action fixtures.
Arithmetic references use the approved rational constants, not game helpers.
The custom-application phase fixtures test API contracts, not UI playback.
"""
import ast, collections, hashlib, itertools, json, pathlib, struct, sys
from fractions import Fraction

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
OUT=pathlib.Path(meta['path']).parent;rom=pathlib.Path(meta['path']).read_bytes();S=meta['symbols']
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
fix=OUT/'executor';assert json.loads((fix/'manifest.json').read_text())['romSha1']==meta['romSha1']
ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes()
UNIT,TARGET,OTHER=0x020033e4,0x02000080,0x020034ec
EQUIPMENT,RETURN,STACK,CTX=0x02002000,0x08000100,0x03006800,0x0200f3f0
FRAME,EXEC,OBJECT,WRAPPER=0x03007400,0x03007a00,0x02028000,0x02028300
stock=0x02001940+374
exec(compile(ast.Module(body=[n for n in ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000')).body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m=ARM(rom,iw);checks=collections.Counter();case=None
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())

def check(name,actual,expected):
    checks[name]+=1
    assert actual==expected,(name,actual,expected,case)

def call(name,*args):return m.call(S[name],*args,stack=STACK)
def put16(p,n):m.put(p,struct.pack('<H',n))
def record(unit):
    p=call('ffta_job_state',unit);assert p;return p
def equip(unit,lesson_id):
    lesson=next(l for l in registry['lessons'] if l['id']==lesson_id)
    race=m.read(unit+6,1)[0];owner=next(o for o in lesson['owners'] if o['race']==race)
    index=owner['abilityIndex'];kind=lesson['type'][0]
    m.put(unit+(0x3b if kind=='S' else 0x3a),bytes([index]))
    m.put((0x02001b40+index-144) if race==1 and index>=144 else unit+0x40+index,b'\xff')
    actual=m.call(0x080cd50c if kind=='S' else 0x080cd4d4,unit,stack=STACK)
    assert actual==lesson['globalAbilityId'],(lesson_id,index,actual,lesson['globalAbilityId'])

def reset():
    m.put(0x02000000,ram);m.put(0x03000000,iw);m.put(0x0203ff44,bytes(8));call('ffta_job_reset')
    for unit,side,job,race in ((UNIT,128,118,2),(TARGET,0,116,1),(OTHER,128,118,2)):
        m.put(unit+5,bytes([job,race,job]));m.put(unit+0x35,bytes([job]))
        m.put(unit+0x18,struct.pack('<4H',100,500,99,99));m.put(unit+0x28,bytes([0,side]))
        m.put(unit+0x2a,bytes(10));m.put(unit+0x3a,bytes(2));m.put(unit+0xe8,bytes(8))
        m.put(record(unit),bytes(16));m.put(call('ffta_owned_exposed',unit),bytes(1));m.put(call('ffta_owned_wound',unit),bytes(2))
    m.put(stock,b'\x03')

def context(action,query=False):
    row=m.word(0x080ccd84)+action*28
    descriptor=m.read(row+12,1)[0] if action else 63
    c=bytearray(0x34);struct.pack_into('<IIIH',c,0,UNIT,TARGET,TARGET,action)
    struct.pack_into('<I',c,0x30,m.word(0x0812f2a0)+descriptor*4);c[0x26]=16 if query else 0
    m.put(CTX,c)

reset()
katana=next(i for i in range(1,512) if m.call(0x080ca7a4,i,3,stack=STACK)==9)
# Real native stage with one legal support/reaction per unit. Last Resort,
# Challenged and TBN are granted separately, as by other party members.
for magic,support,actor_lr,target_lr,barrier,poise,ward,challenged in itertools.product(
        (False,True),('none','DRK-S1','VIK-S2'),*( (False,True),)*6):
    case=('factors',magic,support,actor_lr,target_lr,barrier,poise,ward,challenged)
    reset();action=23 if magic else 0;context(action,True)
    if support!='none':equip(UNIT,support)
    m.put(TARGET+0xe9,b'\x02') # Pre-existing Poison qualifies Opportunist.
    if actor_lr:call('ffta_drk_grant_last_resort',UNIT,0)
    if target_lr:call('ffta_drk_grant_last_resort',TARGET,0)
    if barrier:check('barrier-admission',call('ffta_drk_grant_tbn',TARGET,TARGET),1)
    if poise:equip(TARGET,'SAM-S2');call('ffta_viking_grant_war_cry',TARGET,0)
    if ward:
        equip(TARGET,'DRK-R1' if magic else 'SAM-R1');put16(TARGET+0x2a,katana)
    if challenged:call('ffta_viking_grant_challenge',UNIT,OTHER)
    factor=Fraction(1)
    if support=='DRK-S1':factor*=Fraction(3,2)
    if support=='VIK-S2':factor*=Fraction(13,10)
    if actor_lr and not magic:factor*=Fraction(5,4)
    if target_lr and not magic:factor*=Fraction(6,5)
    if barrier:factor*=Fraction(1,2)
    if poise:factor*=Fraction(3,4)
    if ward:factor*=Fraction(3,4) if magic else Fraction(13,20)
    if challenged:factor*=Fraction(7,10)
    before=m.read(0x02000000,0x40000);rng=m.read(0x030034b0,4)
    check('native-classification',call('ffta_integrated_direct_kind',CTX),2 if magic else 1)
    for raw in (0,1,3,17,99,511,997):
        expected=raw*factor.numerator//factor.denominator
        if not magic:expected=min(999,expected)
        check('one-rational-product',call('ffta_integrated_exposed_native_stage',raw,CTX),expected)
    check('preview-no-state-mutation',m.read(0x02000000,0x40000)==before,True)
    check('preview-no-rng',m.read(0x030034b0,4),rng)

# Cross-job harmful tags are frozen at action start, not recomputed after the
# current attack creates/removes its own wound. Beneficial statuses stay out.
for tag in ('wound','exposed','challenge','centered','warcry','inoculated','lastresort'):
    case=('tags',tag);reset();equip(UNIT,'VIK-S2')
    def grant_tag():
        if tag=='wound':call('ffta_wound_record_replace',call('ffta_owned_wound',TARGET),101)
        elif tag=='exposed':m.put(call('ffta_owned_exposed',TARGET),b'\x01')
        elif tag=='challenge':call('ffta_viking_grant_challenge',TARGET,UNIT)
        else:call({'centered':'ffta_centered_grant','warcry':'ffta_viking_grant_war_cry','inoculated':'ffta_inoculated_grant','lastresort':'ffta_drk_grant_last_resort'}[tag],TARGET,0)
    call('ffta_snapshot_begin',FRAME,UNIT,TARGET,1);call('ffta_action_started',UNIT,365,1,2)
    grant_tag();check('new-tag-cannot-qualify-current-hit',call('ffta_viking_outgoing_numerator',UNIT,TARGET,365),1000)
    call('ffta_snapshot_end',FRAME)
    check('next-action-tag-policy',call('ffta_viking_outgoing_numerator',UNIT,TARGET,365),1300 if tag in ('wound','exposed','challenge') else 1000)
    call('ffta_snapshot_begin',FRAME,UNIT,TARGET,1);call('ffta_action_started',UNIT,365,1,2)
    call('ffta_wound_record_clear',call('ffta_owned_wound',TARGET));m.put(call('ffta_owned_exposed',TARGET),b'\0');m.put(record(TARGET)+5,b'\0')
    check('existing-tag-remains-frozen',call('ffta_viking_outgoing_numerator',UNIT,TARGET,365),1300 if tag in ('wound','exposed','challenge') else 1000)
    call('ffta_snapshot_end',FRAME)

# Explicit query/result fixtures exercise the actual composed application and
# one-shot wound capture APIs. Stock is only spent after successful admission.
for ailment,inoculated,automatic,quantity,query,immune in itertools.product(
        ('challenge','wound'),(False,True),(False,True),(0,3),(False,True),(False,True)):
    if ailment=='wound' and query:continue # Commit has no preview entrypoint.
    case=('prevention',ailment,inoculated,automatic,quantity,query,immune)
    reset();m.put(TARGET+5,bytes([120,3,120]));m.put(TARGET+0x35,b'\x78')
    if automatic:equip(TARGET,'CHM-R2')
    if immune:
        # Ordinary native Immunity is a support, independent of reaction.
        bank=m.word(m.word(0x080cd538)+3*4)
        index=next(i for i in range(128) if int.from_bytes(m.read(bank+8*i+4,2),'little')==11 and m.read(bank+8*i+6,1)[0]==3)
        m.put(TARGET+0x3b,bytes([index]));m.put(TARGET+0x40+index,b'\xff')
        check('native-immunity-equipped',m.call(0x080cd50c,TARGET,stack=STACK),11)
    if inoculated:call('ffta_inoculated_grant',TARGET,0)
    m.put(stock,bytes([quantity]));action=373 if ailment=='challenge' else 355;context(action,query)
    call('ffta_snapshot_begin',FRAME,UNIT,TARGET,1);call('ffta_action_started',UNIT,action,1,2)
    # Declared API phase fixture. No native game output is replaced.
    m.put(FRAME+800,struct.pack('<I',0 if query else 2));m.put(FRAME+16,struct.pack('<I',1))
    if ailment=='challenge':call('ffta_integrated_challenged_apply',CTX)
    else:
        m.put(OBJECT,bytes(0x2c4));m.put(WRAPPER,struct.pack('<I',UNIT));m.put(OBJECT,struct.pack('<I',WRAPPER));put16(OBJECT+0x10,355)
        call('ffta_execution_open',EXEC,UNIT,355);call('ffta_execution_arm',OBJECT,OBJECT+0x20,CTX)
        call('ffta_execution_capture',101,355,UNIT,TARGET);call('ffta_execution_disarm')
        call('ffta_integrated_higanbana_commit',TARGET,150,OBJECT,OBJECT+0x20)
        call('ffta_execution_close',EXEC)
    blocked=immune or inoculated or automatic and quantity>0
    active=call('ffta_viking_challenger',TARGET) if ailment=='challenge' else call('ffta_wound_record_remaining',call('ffta_owned_wound',TARGET))
    check('cross-job-prevention',bool(active),not (blocked or query))
    spent=int(not query and not immune and not inoculated and automatic and quantity>0)
    check('precise-cureall-stock',m.read(stock,1),bytes([quantity-spent]))
    check('precise-cureall-claim',call('ffta_action_claimed',TARGET,1),spent)
    call('ffta_snapshot_end',FRAME)

# All five newly composed status keys coexist; a single turn boundary reaches
# each lifecycle exactly once rather than expiring double-chained providers.
case='coexisting-status-lifecycle';reset()
for name in ('ffta_drk_grant_last_resort','ffta_viking_grant_war_cry','ffta_inoculated_grant'):call(name,TARGET,1)
call('ffta_drk_grant_tbn',TARGET,TARGET);call('ffta_viking_grant_challenge',TARGET,UNIT)
for key in range(28,33):check('coexisting-status-key',call('ffta_integrated_status_icon',TARGET,key),key)
for expected in (2,1,0):
    call('ffta_drk_lifecycle_turn_end',TARGET)
    for offset in (0,4,8):check('one-tick-per-provider',m.read(record(TARGET)+offset,1)[0]&7,expected)
    check('challenge-expires-own-turn',call('ffta_viking_challenger',TARGET),0)
check('barrier-retained-until-source-start',call('ffta_drk_tbn',TARGET),1)
call('ffta_drk_lifecycle_event',TARGET,1);check('barrier-source-start-cleanup',call('ffta_drk_tbn',TARGET),0)
report=dict(passed=True,romSha1=meta['romSha1'],scope=__doc__,checks=dict(checks),total=sum(checks.values()),
    limitations=['Custom-prevention and lifecycle API fixtures are not actual UI/queued playback acceptance','Direct-vs-fall HP provenance and zero-rounded TBN consumption require separate implementation'])
(OUT/'synergies.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
