"""Frozen native Chop eligibility/geometry comparisons; no user game or saves.

Invokes the installed descriptor pointer, not a Python replacement. Geometry
uses native range routines with controlled map height/validity providers; this
is not a rendered battle or a real map integration test.
"""
import ast, ctypes as C, hashlib, importlib.util, itertools, json, pathlib, struct, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
UNIT, EQUIPMENT, RETURN, STACK = 0x02000080, 0x02002000, 0x08000100, 0x03007000
source = ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')],type_ignores=[]),'<native harness>','exec'))
out = ROOT/'build/expansion/probes'
meta = json.loads((out/'combat.json').read_text())
CHOP=424
rom = (out/'combat.gba').read_bytes()
base = (out/'combat-input.gba').read_bytes()
symbols_text = (ROOT/'build/expansion/engine.symbols').read_text()
symbols = {v.split()[2]:int(v.split()[0],16) for v in symbols_text.splitlines() if len(v.split())==3}
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
assert hashlib.sha1(base).hexdigest()==meta['baseSha1']
engine = (ROOT/'build/expansion/engine.bin').read_bytes()
assert hashlib.sha1(engine).hexdigest()==meta['engineSha1']
assert rom[0x1100000:0x1100000+len(engine)]==engine
freeze = out/'chop-eligibility-council'/meta['romSha1']
freeze.mkdir(parents=True,exist_ok=True)
for name,data in [('combat.gba',rom),('input.gba',base),('engine.symbols',symbols_text.encode()),('combat.json',json.dumps(meta,indent=2).encode())]:
    (freeze/name).write_bytes(data)
iwram = iwram_from_boot()
m,n = ARM(rom,iwram),ARM(base,iwram)
callback = m.word(0x083a8624)
assert callback==(symbols['ffta_physical_eligibility_entry']|1)
assert n.word(0x083a8624)==0x08130a95
CTX,TARGET,BUFFER = 0x02024000,0x02025000,0x02026000
counts = {}
def check(group, actual, expected):
    assert actual==expected,(group,actual,expected)
    counts[group]=counts.get(group,0)+1
def forbid_write(u,access,address,size,value,data):
    assert 0x03006000<=address and address+size<=0x03007008,('query mutation',hex(address),size)
def alignment(u,address,size,data):
    assert u.reg_read(UC_ARM_REG_SP)%8==0,('C stack alignment',hex(address))
    counts['aligned_C_entries']=counts.get('aligned_C_entries',0)+1
def no_rng(u,address,size,data):
    raise AssertionError('Eligibility consumed RNG')
for addr in (symbols['ffta_physical_eligibility'],symbols['ffta_primary_weapon']):
    m.u.hook_add(UC_HOOK_CODE,alignment,begin=addr&~1,end=addr&~1)
m.u.hook_add(UC_HOOK_CODE,no_rng,begin=0x08002804,end=0x08002804)
writehook=m.u.hook_add(UC_HOOK_MEM_WRITE,forbid_write)
def unit_data(equipment=(453,),side=0,charm=0,confusion=0,hp=100,xy=(4,4)):
    data=bytearray(264);data[4]=1;data[5]=data[7]=2;data[6]=1
    struct.pack_into('<H',data,0x18,hp);struct.pack_into('<H',data,0x28,side<<15)
    for slot,item in enumerate(equipment):struct.pack_into('<H',data,0x2a+slot*2,item)
    data[0xeb]=(charm<<5)|(confusion<<4);data[0xf6]=xy[0]&255;data[0xf7]=xy[1]&255
    return data
def fixture(machine, action=CHOP, actor=UNIT,target=TARGET,ad=None,td=None):
    if actor:machine.put(actor,ad if ad is not None else unit_data())
    if target and target!=actor:machine.put(target,td if td is not None else unit_data(side=1,xy=(5,4)))
    context=bytearray(64);struct.pack_into('<II',context,0,actor,target);struct.pack_into('<H',context,12,action)
    machine.put(CTX,context)
def invoke(stack=STACK): return m.call(callback,CTX,stack=stack)
# Original callbacks remain bit-for-bit equivalent, including native null-target
# oddity (the original predicate treats null as not dead).
for action,hp,target_null,residue in itertools.product(range(347),(0,100),(False,True),(0,4)):
    for machine in (m,n):fixture(machine,action,target=0 if target_null else TARGET,td=unit_data(side=0,hp=hp,xy=(4,4)))
    check('original_action_differential',invoke(STACK+residue),n.call(0x08130a95,CTX,stack=STACK+residue))
# Exhaustive allegiance flags on both participants. Native target Charm does
# not reverse its base side for actor-side target selection.
for a_side,t_side,a_charm,t_charm,confusion,hp,residue in itertools.product((0,1),repeat=7):
    ad=unit_data(side=a_side,charm=a_charm,confusion=confusion)
    td=unit_data(side=t_side,charm=t_charm,hp=100*hp,xy=(5,4))
    fixture(m,ad=ad,td=td)
    check('hostility_status',invoke(STACK+4*residue),int(bool(hp) and not confusion and (a_side^a_charm)!=t_side))
for actor,target in ((0,TARGET),(UNIT,0),(0,0),(UNIT,UNIT)):
    fixture(m,actor=actor,target=target);check('null_self',invoke(),0)
# Check every original and appended weapon in each slot, native ordered getter
# equivalence, and support/copy independence. The deliberately two-weapon cases
# below isolate ordering and do not assert those loadouts are legal to equip.
for item,slot in itertools.product(range(461),range(5)):
    items=[0]*5;items[slot]=item;fixture(m,ad=unit_data(equipment=items))
    m.put(BUFFER,b'\0'*4)
    m.u.hook_del(writehook)
    count=m.call(0x0812e4f4,UNIT,BUFFER)
    writehook=m.u.hook_add(UC_HOOK_MEM_WRITE,forbid_write)
    primary=struct.unpack('<H',m.read(BUFFER,2))[0] if count else 0
    check('native_primary_order',m.call(symbols['ffta_primary_weapon'],UNIT),primary)
    expected=int(bool(primary) and m.call(0x080ca7a4,primary,3)==31)
    assert invoke()==expected,('item slot eligibility',item,slot,primary,expected)
    counts['all_items_slots']=counts.get('all_items_slots',0)+1
for items,wanted in [((453,52),1),((52,453),0),((253,453),1),((0,265,453),1),((461,453),1),((65535,453),1),((0,0,0,0,0),0)]:
    fixture(m,ad=unit_data(equipment=items));check('mixed_primary_order',invoke(),wanted)
for axe,actor,stack in itertools.product(range(453,461),(UNIT,0x02027000,0x02028000),(STACK,STACK+4)):
    ad=unit_data(equipment=(axe,));ad[0x3b]=255
    fixture(m,actor=actor,ad=ad);check('axes_copies_support',invoke(stack),1)
for ax,ay,tx,ty in itertools.product((-128,-1,0,4,15,127),repeat=4):
    fixture(m,ad=unit_data(xy=(ax,ay)),td=unit_data(side=1,xy=(tx,ty)))
    # These unit fields can lag Move previews. The descriptor must not use
    # them; explicit evaluated geometry coordinates own range enforcement.
    check('stored_coordinate_invariance',invoke(),1)

# All enabled axes use the same primary/hostility descriptor policy.
TOMA=next(l['globalAbilityId'] for l in json.loads((ROOT/'build/expansion/registry.json').read_text())['lessons'] if l['id']=='SLD-AX-A2')
ENABLED_AXES=[l['globalAbilityId'] for l in json.loads((ROOT/'build/expansion/registry.json').read_text())['lessons'] if l['id'] in ('SLD-AX-A1','SLD-AX-A2','SLD-AX-A4','GLD-AX-A1','GLD-AX-A3') and l['globalAbilityId'] in meta['actions']]
if ENABLED_AXES:
    for action,side,charm,target_side,confusion,hp,items,residue in itertools.product(
        ENABLED_AXES,(0,1),(0,1),(0,1),(0,1),(0,100),((453,),(52,),(453,52),(52,453)),(0,4)):
        fixture(m,action=action,actor=0x02027000,
            ad=unit_data(side=side,charm=charm,confusion=confusion,equipment=items,xy=(2,13)),
            td=unit_data(side=target_side,hp=hp,xy=(15,0)))
        check('enabled_axe_descriptor_policy',invoke(STACK+residue),
            int(items[0]==453 and hp>0 and not confusion and (side^charm)!=target_side))

# Both arcs include allies but exclude the actor, KO targets, and Confusion.
ARC_ACTIONS=[l['globalAbilityId'] for l in json.loads((ROOT/'build/expansion/registry.json').read_text())['lessons'] if l['id'] in ('SLD-AX-A3','GLD-AX-A2') and l['globalAbilityId'] in meta['actions']]
for action,side,charm,target_side,confusion,hp,items,residue in itertools.product(ARC_ACTIONS,(0,1),(0,1),(0,1),(0,1),(0,100),((453,),(52,),(453,52),(52,453)),(0,4)):
    fixture(m,action=action,actor=0x02027000,
        ad=unit_data(side=side,charm=charm,confusion=confusion,equipment=items,xy=(2,13)),
        td=unit_data(side=target_side,hp=hp,xy=(15,0)))
    check('arc_friendly_fire_descriptor_policy',invoke(STACK+residue),int(items[0]==453 and hp>0 and not confusion))
for action,actor,target,residue in itertools.product(ARC_ACTIONS,(0,UNIT),(0,UNIT),(0,4)):
    fixture(m,action=action,actor=actor,target=target)
    check('arc_null_self_exclusion',invoke(STACK+residue),0)

# Native effective AI side block, with its real status getters; random provider
# is controlled only for Confusion, to demonstrate why eligibility rejects it.
ai=ARM(base,iwram);wrapper=0x02026000;ai.put(wrapper,struct.pack('<I',UNIT))
state={'rng':0,'calls':0}
def rng(u,address,size,data):
    state['calls']+=1;u.reg_write(UC_ARM_REG_R0,state['rng']);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
ai.u.hook_add(UC_HOOK_CODE,rng,begin=0x08002804,end=0x08002804)
for side,charm,confusion,random in itertools.product((0,1),repeat=4):
    ai.put(UNIT,unit_data(side=side,charm=charm,confusion=confusion));ai.put(STACK+0x9c,struct.pack('<I',wrapper))
    ai.u.reg_write(UC_ARM_REG_SP,STACK);ai.u.reg_write(UC_ARM_REG_R2,wrapper)
    state.update(rng=random,calls=0)
    ai.u.emu_start(0x080c1ed3,0x080c1f12,count=1000)
    check('native_AI_side',ai.u.reg_read(UC_ARM_REG_R4),(random if confusion else side)^charm)
    check('native_AI_rng_condition',state['calls'],confusion)

# Native geometry, only map service functions are synthetic. Other logic,
# weapon categories, distance and directional height limits remain native.
m.u.hook_del(writehook)
geo={'target':(5,4),'delta':0,'valid':1,'flags':0}
def map_service(u,address,size,data):
    xy=(u.reg_read(UC_ARM_REG_R0)&255,u.reg_read(UC_ARM_REG_R1)&255)
    value=(16+geo['delta'] if xy==geo['target'] else 16) if address==0x0801cc18 else (geo['flags'] if address==0x0801cd08 else geo['valid'])
    u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
for address in (0x0801cc18,0x0801cc7c,0x0801cd08,0x0809d79c):
    m.u.hook_add(UC_HOOK_CODE,map_service,begin=address,end=address)
for item,delta,distance in itertools.product((52,453,460),range(-8,9),range(4)):
    geo.update(target=(4+distance,4),delta=delta,valid=1,flags=0)
    fixture(m,ad=unit_data(equipment=(item,)))
    m.put(STACK,struct.pack('<III',4,item,0))
    result=m.call(0x0809fef0,UNIT,4,4,4+distance)
    expected=int(distance==1 and -3<=delta<=2)
    check('native_weapon_geometry',result,expected)
    # Actual outer action geometry, with real Chop range selector dispatch.
    m.put(STACK,struct.pack('<IIII',4,CHOP,item,0))
    check('native_Chop_outer_geometry',m.call(0x080a0014,UNIT,4,4,4+distance),int(distance==1 and abs(delta)<=2))
for valid,flags in ((0,0),(1,1),(1,8)):
    geo.update(target=(5,4),delta=0,valid=valid,flags=flags)
    fixture(m);m.put(STACK,struct.pack('<IIII',4,CHOP,453,0))
    check('invalid_map_target',m.call(0x080a0014,UNIT,4,4,5),0)
# The native shared target-list API used by player/AI callers carries evaluated
# X/Y separately from the unit. Retain deliberately stale unit fields here.
for actor,delta in itertools.product((UNIT,0x02027000),(-4,-3,0,2,3)):
    fixture(m,actor=actor,ad=unit_data(xy=(2,13)))
    geo.update(target=(5,4),delta=delta,valid=1,flags=0)
    descriptor=bytearray(16);struct.pack_into('<I',descriptor,0,actor)
    descriptor[4:6]=bytes((4,4));struct.pack_into('<HH',descriptor,8,CHOP,453)
    m.put(BUFFER,descriptor);m.put(0x02029000-8,b'\xa5'*1040)
    before=m.read(actor,264)
    amount=m.call(0x080b4a1c,BUFFER,0,0,0x02029000)
    assert amount<=256
    tiles={tuple(m.read(0x02029000+i*4,2)) for i in range(amount)}
    expected={(3,4),(4,3),(4,5)}|({(5,4)} if abs(delta)<=2 else set())
    check('native_shared_target_list',tiles,expected)
    check('target_list_copy_unchanged',m.read(actor,264),before)
    check('target_list_output_guard',m.read(0x02029000-8,8)+m.read(0x02029000+amount*4,8),b'\xa5'*16)
report={'passed':True,'romSha1':meta['romSha1'],'baseSha1':meta['baseSha1'],'engineSha1':meta['engineSha1'],'checks':sum(counts.values()),'groups':counts,
        'scope':'Installed callback and native geometry with controlled map providers. No rendered battle, application damage, or real-map integration claim.'}
(freeze/'results.json').write_text(json.dumps(report,indent=2)+'\n')
(out/'chop-eligibility-tests.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
