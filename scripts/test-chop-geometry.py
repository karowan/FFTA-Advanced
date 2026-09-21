"""Installed eight-argument geometry hook with native map data and readers.

No map-height/validity/geometry helpers are stubbed. Fixtures provide a16x16
native map grid. This is not a rendered battlefield or complete AI turn.
"""
import ast,ctypes as C,hashlib,importlib.util,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
s=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in s.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')],type_ignores=[]),'<native harness>','exec'))
out=ROOT/'build/expansion/probes';meta=json.loads((out/'combat.json').read_text());CHOP=424
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
MELEE=[l['globalAbilityId'] for l in registry['lessons'] if l['id'] in ('SLD-AX-A1','SLD-AX-A4','GLD-AX-A1','GLD-AX-A3','GLD-AX-A4') and l['globalAbilityId'] in meta['actions']]
rom=(out/'combat.gba').read_bytes();base=bytearray((out/'combat-input.gba').read_bytes());clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1'] and hashlib.sha1(base).hexdigest()==meta['baseSha1']
engine=(ROOT/'build/expansion/engine.bin').read_bytes();assert hashlib.sha1(engine).hexdigest()==meta['engineSha1']
assert rom[0x1100000:0x1100000+len(engine)]==engine
symbol_text=(ROOT/'build/expansion/engine.symbols').read_text();symbols={v.split()[2]:int(v.split()[0],16) for v in symbol_text.splitlines() if len(v.split())==3}
freeze=out/'chop-geometry-council'/meta['romSha1'];freeze.mkdir(parents=True,exist_ok=True)
for name,data in [('combat.gba',rom),('combat-input.gba',base),('engine.symbols',symbol_text.encode()),('combat.json',json.dumps(meta,indent=2).encode())]:(freeze/name).write_bytes(data)
assert any(c['offset']==0xa0014 and c['size']==12 and c['name']=='ffta_combat_geometry_entry' for c in meta['changes'])
assert base[0xa0014:0xa0020]==clean[0xa0014:0xa0020]
# Give the native comparison image the same Chop donor record, with no geometry
# hook, so it proves the old -3..+2 rule independently of extension metadata.
table=struct.unpack_from('<I',rom,0xccd84)[0]-0x08000000
for action in MELEE:base[table+action*28:table+(action+1)*28]=rom[table+action*28:table+(action+1)*28]
iwram=iwram_from_boot();m,n=ARM(rom,iwram),ARM(base,iwram);GRID=0x02026000;COPY=0x02027000
counts={};expected_args=None;entries=[]
def check(group,actual,expected):
    assert actual==expected,(group,actual,expected)
    counts[group]=counts.get(group,0)+1
def entry(u,address,size,data):
    sp=u.reg_read(UC_ARM_REG_SP)
    args=tuple(u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))+struct.unpack('<4I',bytes(u.mem_read(sp,16)))
    check('eight_arguments',args,expected_args)
    if address==(symbols['ffta_combat_geometry']&~1):check('C_alignment',sp%8,0)
    entries.append(address)
for symbol in ('ffta_combat_geometry','ffta_original_combat_geometry'):
    p=symbols[symbol]&~1;m.u.hook_add(UC_HOOK_CODE,entry,begin=p,end=p)
def no_rng(u,address,size,data):raise AssertionError('Geometry consumed RNG')
for machine in (m,n):machine.u.hook_add(UC_HOOK_CODE,no_rng,begin=0x08002804,end=0x08002804)
def readonly(u,access,address,size,value,data):
    assert 0x03005000<=address and address+size<=0x03007014,('geometry mutation',hex(address),size)
for machine in (m,n):machine.u.hook_add(UC_HOOK_MEM_WRITE,readonly)
def fixture(machine,delta=0,distance=1,actor=UNIT,flags=0):
    machine.fixture(2,[453]);unit=bytearray(machine.read(UNIT,264));unit[0xf6:0xf8]=bytes((2,13))
    machine.put(actor,unit)
    grid=bytearray(bytes((16,0))*256);grid[2*(6*16+6+distance)]=16+delta;grid[2*(6*16+6+distance)+1]=flags
    machine.put(GRID,grid)
    map_info=bytearray(16);struct.pack_into('<I',map_info,4,GRID);map_info[8]=16;map_info[13]=map_info[15]=16
    machine.put(0x02007f10,map_info)
def invoke(machine,args,residue=0):
    global expected_args,entries
    expected_args=tuple(args);entries=[];stack=STACK+residue
    before=machine.read(args[0],264);map_before=machine.read(GRID,512)
    machine.put(stack-0x400,b'\xa5'*16);machine.put(stack+16,b'\xa5'*16)
    machine.put(stack,struct.pack('<4I',*args[4:]));original_stack=machine.read(stack,32)
    result=machine.call(0x080a0014,*args[:4],stack=stack)
    check('argument_stack_unchanged',machine.read(stack,32),original_stack)
    check('stack_low_guard',machine.read(stack-0x400,16),b'\xa5'*16)
    check('unit_unchanged',machine.read(args[0],264),before)
    check('map_unchanged',machine.read(GRID,512),map_before)
    if machine is m:check('single_native_delegate',entries,[symbols['ffta_combat_geometry']&~1,symbols['ffta_original_combat_geometry']&~1])
    return result
for lesson,mp in (('SLD-AX-A1',0),('SLD-AX-A4',6),('GLD-AX-A1',8),('GLD-AX-A3',10),('GLD-AX-A4',16)):
    action=next(l['globalAbilityId'] for l in registry['lessons'] if l['id']==lesson)
    if action not in MELEE:continue
    for selector,value in ((2,mp),(3,1),(4,128)):
        check('native_melee_record_fields',m.call(0x080ccd50,action,selector),value)
    check('physical_no_knockback_stages',rom[table+action*28+12:table+action*28+16],bytes((63,1,1,1)))
for action,delta,residue in itertools.product(range(347),(-3,0,3),(0,4)):
    for machine in (m,n):fixture(machine,delta)
    args=(UNIT,6,6,7,6,action,453,0)
    check('all_original_geometry',invoke(m,args,residue),invoke(n,args,residue))
for action,delta,distance,residue,actor in itertools.product(MELEE,range(-6,7),range(4),(0,4),(UNIT,COPY)):
    for machine in (m,n):fixture(machine,delta,distance,actor)
    args=(actor,6,6,6+distance,6,action,453,0)
    check('new_melee_symmetric_height',invoke(m,args,residue),int(distance==1 and abs(delta)<=2))
    check('native_asymmetric_control',invoke(n,args,residue),int(distance==1 and -3<=delta<=2))
for action,high,residue,delta in itertools.product(MELEE,(0,0x10000,0xabcd0000),(0,4),(-3,-2,2,3)):
    for machine in (m,n):fixture(machine,delta)
    args=(UNIT,6|high,6|high,7|high,6|high,action|high,453|high,high)
    check('native_argument_truncation',invoke(m,args,residue),int(abs(delta)<=2))
for action,flags in itertools.product(MELEE,(1,8,9)):
    fixture(m,flags=flags);check('native_impassable_preserved',invoke(m,(UNIT,6,6,7,6,action,453,0)),0)
for action,(tx,ty) in itertools.product(MELEE,((-1,6),(16,6),(6,-1),(6,16))):
    fixture(m);check('native_bounds_preserved',invoke(m,(UNIT,6,6,tx&0xffffffff,ty&0xffffffff,action,453,0)),0)
report={'passed':True,'romSha1':meta['romSha1'],'engineSha1':meta['engineSha1'],'actions':MELEE,'checks':sum(counts.values()),'groups':counts,
        'scope':'Installed8-argument A0014 wrapper, actual native map readers/grid and geometry, all347 originals, copied/moved origin, bothSPresidues, guards/noRNG. Not a rendered battle.'}
(freeze/'results.json').write_text(json.dumps(report,indent=2)+'\n');(out/'chop-geometry-tests.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
