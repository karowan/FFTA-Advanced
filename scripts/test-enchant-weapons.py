"""Native checks for Mystic Knight enchantments on every weapon.

Runs the installed code of the enchant-weapons candidate and its parent in the
ARM harness: weapon/blade gates for every item record, native outer geometry
A0014 (map providers are a flat controlled map, as in the Chop test) against
native Fight for one weapon of every category, the targeting mode word's
self-tile bit (B42E4), Spell Parry's blade rule, and
the declared action-range and help-text data.
"""
import ast, ctypes as C, datetime, hashlib, importlib.util, itertools, json, struct, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,TARGET,RETURN,STACK=0x02000080,0x02000188,0x08000100,0x03007000
GEOMETRY,TARGET_MODE,ITEM_FIELD=0x080a0014,0x080b42e4,0x080ca7a4
MYK_A1,MYK_A11,MYK_A12,MYK_A13,MYK_A14=410,420,421,422,423
meta=json.loads(Path(json.loads((ROOT/'build/expansion/enchant-weapons/current.json').read_text())['manifest']).read_text())
rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
change=meta['enchantWeapons']
parent=Path(json.loads(Path(change['parent']).read_text())['path']).read_bytes()
assert hashlib.sha1(parent).hexdigest()==change['baseSha1']
installed={k:v['address'] for k,v in change['installed'].items()}
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')],type_ignores=[]),'<native-harness>','exec'))
iw=iwram_from_boot();new,old=ARM(rom,iw),ARM(parent,iw)
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)

# Flat, valid map: every tile height 16, no blocking flags.
def flat(u,address,size,data):
    value={0x0801cc18:16,0x0801cd08:0}.get(address,1)
    u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
for m in (new,old):
    for address in (0x0801cc18,0x0801cc7c,0x0801cd08,0x0809d79c):m.u.hook_add(UC_HOOK_CODE,flat,begin=address,end=address)

def unit(item,side=0,xy=(6,6)):
    data=bytearray(264);data[4]=1;data[5]=data[7]=35;data[6]=4
    struct.pack_into('<H',data,0x18,100);struct.pack_into('<H',data,0x28,side<<15)
    struct.pack_into('<H',data,0x2a,item);data[0xf6],data[0xf7]=xy
    return data
def category(m,item):return m.call(ITEM_FIELD,item,3)

# 1. Weapon gates over every item record.
weapons=[];blades=[]
for item in range(461):
    kind=category(new,item) if item else 0
    weapon=item>0 and (1<=kind<=19 or kind==31);blade=item>0 and kind in (3,8)
    check(bool(new.call(installed['ffta_myk_weapon'],item))==weapon,f'item {item} category {kind} enchantable')
    check(bool(new.call(change['symbols']['ffta_myk_blade'],item))==blade,f'item {item} blade')
    check(bool(old.call(installed['ffta_myk_weapon'],item))==blade,f'parent item {item} rapier/saber only')
    if weapon:weapons.append(item)
samples={}
for item in weapons:samples.setdefault(category(new,item),item)
check(sorted(samples)==[*range(1,20),31],'one sample weapon for every category')

# 2. Geometry: strikes use the weapon's Fight range; enchantments also allow self.
def geometry(m,action,item,dx,dy,entry=GEOMETRY):
    m.put(UNIT,unit(item));m.put(STACK,struct.pack('<IIII',6+dy,action,item,0))
    return m.call(entry,UNIT,6,6,6+dx)
offsets=[(dx,dy) for dx,dy in itertools.product(range(-6,7),repeat=2)]
ranges={}
for kind,item in sorted(samples.items()):
    reach=set()
    for dx,dy in offsets:
        fight=geometry(new,0,item,dx,dy)
        if fight:reach.add(abs(dx)+abs(dy))
        for action in range(MYK_A1,MYK_A12+1):
            expected=1 if (dx,dy)==(0,0) and action<=MYK_A11 else fight
            check(bool(geometry(new,action,item,dx,dy))==bool(expected),f'{action} category {kind} offset {dx},{dy} matches Fight')
        for action in (MYK_A13,MYK_A14):
            check(geometry(new,action,item,dx,dy)==geometry(old,action,item,dx,dy),f'{action} category {kind} offset {dx},{dy} unchanged')
    # Targeting UI mode word: weapon ranges exclude the actor's tile (0x100)
    # except for the enchantments; everything else is the native value.
    fight_mode=new.call(TARGET_MODE,0,item)
    check(fight_mode==old.call(TARGET_MODE,0,item) and fight_mode&0x100,f'category {kind} Fight mode native, no self')
    for action in range(MYK_A1,MYK_A12+1):
        mode=new.call(TARGET_MODE,action,item)
        check(mode==(fight_mode&~0x100 if action<=MYK_A11 else fight_mode),f'{action} category {kind} targeting mode')
    for action in (MYK_A13,MYK_A14):
        check(new.call(TARGET_MODE,action,item)==old.call(TARGET_MODE,action,item),f'{action} category {kind} mode unchanged')
    ranges[kind]=sorted(reach)
bow=samples[14]
check(geometry(old,MYK_A1,bow,1,0) and not geometry(old,MYK_A1,bow,3,0),'parent strike range was one tile')
check(max(ranges[14])>=3 and geometry(new,MYK_A1,bow,max(ranges[14]),0),'greatbow strike reaches its Fight range')

# 3. Spell Parry needs a rapier or saber; enchantments no longer imply one.
values={'ffta_action_unit_extension_reaction_flags':0x200,'ffta_action_origin':1,'ffta_action_reaction_forecast_enabled':1}
def stub(u,address,size,data):
    name=stubs[address]
    value=values.get(name,0x80 if u.reg_read(UC_ARM_REG_R0)==TARGET else 0)
    u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
stubs={installed[n]:n for n in values}|{installed['ffta_action_unit_flags']:'ffta_action_unit_flags'}
hooks=[m.u.hook_add(UC_HOOK_CODE,stub,begin=a,end=a) for m in (new,old) for a in stubs]
for kind,item in sorted(samples.items()):
    for m in (new,old):m.put(UNIT,unit(0,0,(1,1)));m.put(TARGET,unit(item,1,(2,1)))
    factor=new.call(installed['ffta_myk_parry_factor'],UNIT,TARGET,0)
    check(factor==(1 if kind in (3,8) else 2),f'Spell Parry category {kind}')
    check(old.call(installed['ffta_myk_parry_factor'],UNIT,TARGET,0)==1,f'parent Spell Parry category {kind} without weapon check')

# 4. Declared data: strike range/height bytes and help text.
actions=struct.unpack_from('<I',rom,0xccd84)[0]-0x08000000
for action in range(MYK_A1,MYK_A14+1):
    at=actions+action*28
    expected=b'\x80\x80' if action<=MYK_A12 else parent[at+6:at+8]
    check(rom[at+6:at+8]==expected and rom[at:at+6]==parent[at:at+6] and rom[at+8:at+28]==parent[at+8:at+28],f'action {action} record')
table=struct.unpack_from('<I',rom,0x36d6c4)[0]-0x08000000
script="import('./src/rom-builder.mjs').then(m=>process.stdout.write(m.encodeHelp(process.argv[1]).toString('hex')))"
for row in change['help']:
    text=bytes.fromhex(subprocess.check_output(['node','-e',script,row['text']],cwd=ROOT,text=True))
    pointer=struct.unpack_from('<I',rom,table+(row['helpId']-0x1de)*4)[0]-0x08000000
    check(rom[pointer:pointer+len(text)]==text,row['lesson']+' help text')
out=Path(meta['path']).parent/('native-enchant-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir()
report=dict(status='passed',romSha1=meta['romSha1'],parentSha1=change['baseSha1'],checks=len(checks),
    enchantableItems=len(weapons),sampleWeapons=samples,fightReach={str(k):v for k,v in ranges.items()})
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status='passed',romSha1=meta['romSha1'],checks=len(checks),enchantableItems=len(weapons),report=str(out/'report.json'))))
