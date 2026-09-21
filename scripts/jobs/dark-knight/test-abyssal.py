"""Abyssal Blade: installed line, evaluated previews, native multi-target costs/damage.

Fixed native executor fixtures and independently calculated falloff. This does
not certify rendered animation, a full AI turn or campaign acquisition.
"""
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/arm-python'));sys.path.insert(0,str(ROOT/'scripts'))
from unicorn import *
from unicorn.arm_const import *
from job_test_candidate import load_candidate
from native_battle_wrappers import from_memory
meta=load_candidate(ROOT/'build/expansion/probes/dark-knight/current.json')
OUT=pathlib.Path(meta['path']).parent;rom=pathlib.Path(meta['path']).read_bytes();S=meta['symbols']
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
fix=OUT/'executor';assert json.loads((fix/'manifest.json').read_text())['romSha1']==meta['romSha1']
ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes()
regs=struct.unpack_from('<17I',(fix/'execute-trap.state').read_bytes(),0x20)
UNIT,TARGET,EQUIPMENT,RETURN,STACK=0x02000080,0x020033e4,0x02002000,0x08000100,0x03006800
TARGETS=(TARGET,0x020032dc,0x020031d4)
GRID,DESC,OUTPUT,CTX=0x02026000,0x02027000,0x02028000,0x0200f3f0
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
raw=bytearray(rom);p=S['ffta_physical_final']-0x08000000;raw[p:p+2]=bytes.fromhex('7047')
m,n=ARM(rom,iw),ARM(raw,iw)
wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()}
checks=collections.Counter();outcomes=[];case=None;positions=[]
directions=((0,1),(-1,0),(0,-1),(1,0))
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())

def check(k,a,b):
    checks[k]+=1
    if a!=b:(OUT/'abyssal-failure.json').write_text(json.dumps(dict(check=k,actual=a,expected=b,case=case,positions=positions,outcomes=outcomes[-4:]),indent=2))
    assert a==b,(k,a,b,case)

def half(machine,p):return int.from_bytes(machine.read(p,2),'little')

def place(machine,unit,x,y,facing=0):
    machine.put(unit+0xf6,bytes((x,y,facing)))
    machine.put(wrappers[unit]+8,struct.pack('<3H',x*32+16,32,y*32+16))
    machine.put(wrappers[unit]+0x1f,bytes((facing,)))

def reset(machine,facing=3,race=1,seed=0,blood=False,friendly=False):
    machine.put(0x02000000,ram);machine.put(0x03000000,iw)
    machine.put(0x0203ff44,bytes(8));machine.put(0x02001e98,bytes(108))
    grid=bytes((16,0))*256;machine.put(GRID,grid)
    header=bytearray(16);struct.pack_into('<I',header,4,GRID);header[8]=header[13]=header[15]=16
    machine.put(0x02007f10,header)
    job=117 if race==1 else 119
    machine.put(UNIT+5,bytes((job,race,job)));machine.put(UNIT+0x35,bytes((job,)))
    for unit in (UNIT,*TARGETS):
        machine.put(unit+0x18,struct.pack('<4H',500,500,99,99))
        machine.put(unit+0x20,struct.pack('<4H',70,40,40,40))
        machine.put(unit+0x3a,bytes(2));machine.put(unit+0xe8,bytes(8))
        machine.put(unit+0x2a,struct.pack('<5H',384,0,0,0,0))
    place(machine,UNIT,6,6,facing)
    dx,dy=directions[facing];side=machine.read(UNIT+0x29,1)[0]&128
    for distance,unit in enumerate(TARGETS,1):
        place(machine,unit,6+dx*distance,6+dy*distance,(facing+2)&3)
        machine.put(unit+0x29,bytes((side if friendly and distance==2 else side^128,)))
    if blood:
        lesson=next(x for x in registry['lessons'] if x['id']=='DRK-S2')
        index=next(x['abilityIndex'] for x in lesson['owners'] if x['race']==race)
        machine.put(UNIT+0x3b,bytes((index,)))
        machine.put(0x02001b40+index-144 if race==1 else UNIT+0x40+index,b'\xff')
        check('actual_bloodcasting_lookup',machine.call(0x080cd50c,UNIT,stack=STACK),131)
    machine.put(0x030034b0,struct.pack('<I',seed))
    machine.put(regs[13],struct.pack('<4I',362,0,0,255))
    c=bytearray(52);struct.pack_into('<IIIHH',c,0,UNIT,TARGET,TARGET,362,384)
    struct.pack_into('<I',c,48,machine.word(0x0812f2a0)+63*4);machine.put(CTX,c)

# All four directions, mixed allegiance, independent real accuracy and one
# payment for three recipients. The reference bypasses only the final custom
# multiplier; native elemental/defense/accuracy/application remain identical.
for facing,race,blood,friendly,seed in itertools.product(range(4),(1,2),(False,True),(False,True),range(8)):
    case=('executor',facing,race,blood,friendly,seed);pair=[]
    for machine in (n,m):
        reset(machine,facing,race,seed,blood,friendly)
        dx,dy=directions[facing]
        machine.call(0x080a433c,regs[0],wrappers[UNIT],6+dx,6+dy,stack=regs[13])
        pair.append([500-half(machine,u+0x18) for u in TARGETS])
        check('once_HP_payment',half(machine,UNIT+0x18),405 if blood else 425)
        check('once_MP_payment',half(machine,UNIT+0x1c),99 if blood else 89)
        check('retired_roots',list(machine.read(0x0203ff44,8)),[0]*8)
    check('independent_native_P_falloff',pair[1],[p*factor//100 for p,factor in zip(pair[0],(140,125,110))])
    outcomes.append(dict(facing=facing,race=race,blood=blood,friendly=friendly,seed=seed,P=pair[0],damage=pair[1]))
for distance in range(3):
    check('actual_hit_each_distance',any(x['damage'][distance]>0 for x in outcomes),True)
    check('actual_miss_each_distance',any(x['damage'][distance]==0 for x in outcomes),True)
check('friendly_fire_exercised',any(x['friendly'] and x['damage'][1]>0 for x in outcomes),True)

# Paying the sacrifice can activate Desperation on this action. Incoming TBN
# is frozen per recipient and only halves hostile hits. Combine both with the
# distance coefficient before one division, including a friendly middle tile.
for facing,race,friendly,seed in itertools.product(range(4),(1,2),(False,True),range(8)):
    case=('sacrifice-desperation-barriers',facing,race,friendly,seed);pair=[]
    for machine in (n,m):
        reset(machine,facing,race,seed,friendly=friendly)
        machine.put(UNIT+0x18,struct.pack('<H',250))
        index=167 if race==1 else 86
        machine.put(UNIT+0x3b,bytes((index,)))
        machine.put(0x02001b40+index-144 if race==1 else UNIT+0x40+index,b'\xff')
        check('actual_desperation_lookup',machine.call(0x080cd50c,UNIT,stack=STACK),130)
        for unit in TARGETS:check('native_barrier_grant',machine.call(S['ffta_drk_grant_tbn'],unit,unit,stack=STACK),1)
        dx,dy=directions[facing]
        machine.call(0x080a433c,regs[0],wrappers[UNIT],6+dx,6+dy,stack=regs[13])
        pair.append([500-half(machine,u+0x18) for u in TARGETS])
        check('post_cost_desperation_boundary',half(machine,UNIT+0x18),175)
    check('falloff_cross_job_one_round',pair[1],[p*f*3//(200*(1 if friendly and i==1 else 2)) for i,(p,f) in enumerate(zip(pair[0],(140,125,110)))])

# The real native wrapper preview supplies position before the formula and
# restores it afterwards. Deliberately stale live positions must not choose
# the coefficient. No injected formula outputs or damage rolls are used.
preview_values=[]
def observe(u,pc,size,machine):
    a=machine.word(u.reg_read(UC_ARM_REG_R7));t=machine.word(u.reg_read(UC_ARM_REG_R6))
    preview_values.append(u.reg_read(UC_ARM_REG_R0))
    if machine is m:positions.append((tuple(m.read(a+0xf6,2)),tuple(m.read(t+0xf6,2))))
for machine in (n,m):machine.u.hook_add(UC_HOOK_CODE,observe,machine,begin=0x080b5730,end=0x080b5730)
for facing,distance,residue in itertools.product(range(4),(1,2,3),(0,4)):
    case=('moved-preview',facing,distance,residue);pair=[];positions=[];preview_values=[]
    dx,dy=directions[facing];target=TARGETS[distance-1]
    for machine in (n,m):
        reset(machine,facing)
        machine.put(UNIT+0xf6,bytes((1,1,0)));machine.put(target+0xf6,bytes((14,14,0)))
        before=machine.read(UNIT+0xf6,3)+machine.read(target+0xf6,3);rng=machine.word(0x030034b0)
        machine.put(STACK+residue,struct.pack('<2I',0,255))
        machine.call(0x080b55cc,wrappers[UNIT],wrappers[target],362,384,stack=STACK+residue)
        # B55CC is void; B5730 receives the actual native damage return before
        # its display writer. The function epilogue's R0 contains caller LR.
        check('one_native_preview_result',len(preview_values),len(pair)+1)
        pair.append(preview_values[-1])
        check('preview_restores_positions',list(machine.read(UNIT+0xf6,3)+machine.read(target+0xf6,3)),list(before))
        check('preview_preserves_rng',machine.word(0x030034b0),rng)
        check('preview_no_cost',half(machine,UNIT+0x18),500)
    check('preview_positive_native_reference',pair[0]>0,True)
    check('preview_falloff',pair[1],pair[0]*(155-15*distance)//100)
    check('preview_explicit_evaluated_positions',positions,[((6,6),(6+dx*distance,6+dy*distance))])

# Installed geometry/list use explicit coordinates even when actor F6/F7 is
# stale. Independent tile oracle covers stopping at height/terrain/map edges.
for origin,facing,block,height,flags,mode,residue in itertools.product(((0,0),(15,15),(6,6)),range(4),(1,2,3),(0,13,14,16,18,19),(0,1,8),(0,1),(0,4)):
    case=('line',origin,facing,block,height,flags,mode,residue);reset(m,facing)
    dx,dy=directions[facing];ax,ay=origin;bx,by=ax+dx*block,ay+dy*block
    if 0<=bx<16 and 0<=by<16:m.put(GRID+2*(by*16+bx),bytes((height,flags)))
    d=bytearray(16);struct.pack_into('<I',d,0,UNIT);d[4:8]=bytes((*origin,13,13));struct.pack_into('<HH',d,8,362,384)
    m.put(DESC,d);m.put(OUTPUT-16,b'\xa5'*64);want=[]
    for distance in (1,2,3):
        x,y=ax+dx*distance,ay+dy*distance
        if not(0<=x<16 and 0<=y<16):break
        h,f=m.read(GRID+2*(y*16+x),2)
        if not h or f&9 or abs(h-16)>2:break
        want.append((x,y,h))
    count=m.call(0x080b4a1c,DESC,facing,mode,OUTPUT,stack=STACK+residue)
    check('native_line_list',[tuple(m.read(OUTPUT+4*i,3)) for i in range(count)],want)
    check('area_write_guards',list(m.read(OUTPUT-16,16)+m.read(OUTPUT+4*count,16)),[165]*32)
    for distance in (1,2,3,4):
        x,y=ax+dx*distance,ay+dy*distance
        if min(x,y)<0:continue
        m.put(STACK+residue,struct.pack('<4I',y,362,384,0))
        check('native_line_geometry',m.call(0x080a0014,UNIT,ax,ay,x,stack=STACK+residue),int((x,y) in [row[:2] for row in want]))

# Weapon gate and elemental law input retain the primary weapon. No dark
# override, no offhand qualification, no silent weapon-proc inheritance.
for item in range(461):
    reset(m);m.put(UNIT+0x2a,struct.pack('<5H',item,0,0,0,0))
    category=m.call(0x080ca7a4,item,3,stack=STACK)
    check('sword_family_only',m.call(S['ffta_drk_eligibility'],CTX,stack=STACK),int(item>0 and category in (1,5,6)))
    check('weapon_element_retained',m.call(0x0812f8a4,UNIT,362,item,stack=STACK),m.call(0x0812f8a4,UNIT,0,item,stack=STACK))
for maximum,blood in itertools.product((1,2,7,99,199,200,201,999),(False,True)):
    cost=(maximum*15+99)//100+(20 if blood else 0)
    for hp in (cost,cost+1):
        reset(m,blood=blood);m.put(UNIT+0x18,struct.pack('<HH',hp,maximum))
        check('combined_rounded_cost',m.call(S['ffta_drk_hp_cost'],UNIT,362,stack=STACK),cost)
        check('must_leave_one_HP',m.call(0x08133e18,UNIT,362,255,stack=STACK),int(hp>cost))
        admitted=m.call(S['ffta_drk_paid'],UNIT,362,stack=STACK)
        check('commit_rechecks_HP',admitted,int(hp>cost))
        check('failed_cost_atomic',half(m,UNIT+0x18),1 if hp>cost else hp)
for blood,hp,mp in itertools.product((False,True),(74,75,76,94,95,96),(0,9,10)):
    case=('native-resource-admission',blood,hp,mp);reset(m,blood=blood)
    m.put(UNIT+0x18,struct.pack('<H',hp));m.put(UNIT+0x1c,struct.pack('<H',mp))
    allowed=hp>(95 if blood else 75) and (blood or mp>=10)
    m.call(0x080a433c,regs[0],wrappers[UNIT],7,6,stack=regs[13])
    check('native_atomic_HP',half(m,UNIT+0x18),hp-(95 if blood else 75) if allowed else hp)
    check('native_atomic_MP',half(m,UNIT+0x1c),mp-(0 if blood else 10) if allowed else mp)
    if not allowed:check('unaffordable_no_target_damage',[half(m,u+0x18) for u in TARGETS],[500]*3)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,scope=__doc__)
(OUT/'abyssal.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='outcomes'},indent=2))
