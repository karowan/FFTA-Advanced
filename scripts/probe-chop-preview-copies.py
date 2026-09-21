"""Inspect captured failed preview copies and replay native copy contracts.

Reads the parent's frozen disposable lab snapshots. No live emulator or user
save is modified. Does not infer that a reaction-label failure is unit damage.
"""
import ast,ctypes as C,hashlib,importlib.util,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
s=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in s.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name=='ARM'],type_ignores=[]),'<copy harness>','exec'))
lab=ROOT/'build/expansion/probes/chop-game-lab'
rom=(lab/'frozen.gba').read_bytes();clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
romhash=hashlib.sha1(rom).hexdigest();assert romhash=='dc02c7b68c950a503441735b1a0d168c847784cd'
def word(b,p):return struct.unpack_from('<I',b,p)[0]
def ram_valid(p,size=264):return 0x02000000<=p<=0x02040000-size
def inspect(stem):
    ram=(lab/(stem+'.ram')).read_bytes();iw=(lab/(stem+'.iwram')).read_bytes()
    def w(p):return word(ram,p-0x02000000)
    units={UNIT:'roster_actor',0x020033e4:'target'}
    root=struct.unpack_from('<5I',ram,0x3ff30)
    if root[0]==0x31525041:
        manager,selection,party=root[2:]
        if ram_valid(manager,0x3fc):
            units[manager+0x40]='manager0';units[manager+0x148]='manager1'
        if ram_valid(selection,0x3824):units[selection+0xa4c]='selection'
        if ram_valid(party,0x7264):units[party+0x1be4]='party'
        p=root[1];seen=set()
        while p and p not in seen and ram_valid(p,0xff8):
            seen.add(p)
            if w(p+0xe20)!=0x31535041:break
            for j in range(13):units[p+4+j*264]=f'snapshot_{p:x}_{j}'
            p=w(p+0xe1c)
    names=[]
    for p,kind in units.items():
        if ram_valid(p):
            raw=ram[p-0x02000000:p-0x02000000+264]
            names.append({'address':hex(p),'kind':kind,'nameWord':hex(word(raw,0)),
                          'raceByte':raw[6],'reaction':raw[0x3a],'xy':list(raw[0xf6:0xf8])})
    bad=struct.pack('<I',0x0902d094)
    def matches(b,base):
        return [hex(base+i) for i in range(0,len(b)-3,4) if b[i:i+4]==bad]
    return {'snapshot':stem,'owners':[hex(v) for v in root],'units':names,
            'tablePointerInRAM':matches(ram,0x02000000),'tablePointerInIWRAM':matches(iw,0x03000000)}
stems=['prepreview','preview-frame-000','preview-frame-003','preview-frame-010','preview-frame-020','preview-frame-030','preview-frame-600']
rows=[inspect(stem) for stem in stems]
counts={}
def check(group,actual,expected):
    assert actual==expected,(group,actual,expected)
    counts[group]=counts.get(group,0)+1
for row in rows:
    for unit in row['units']:
        check('no_AP_table_as_unit_name',unit['nameWord']=='0x902d094',False)
    check('actor_name_preserved',next(u['nameWord'] for u in row['units'] if u['kind']=='roster_actor'),
          next(u['nameWord'] for u in rows[0]['units'] if u['kind']=='roster_actor'))

# Execute whole native copies on the captured RAM, comparing native result and
# destination bytes. AP tails may differ only for an owned destination.
for stem in ('prepreview','preview-frame-020','preview-frame-030'):
    ram=(lab/(stem+'.ram')).read_bytes();iw=(lab/(stem+'.iwram')).read_bytes()
    manager=word(ram,0x3ff38)
    destinations=[0x0203a000]+([manager+0x40] if ram_valid(manager,0x3fc) else [])
    for dispatch in ('iwram','library'):
        for length in (0,1,2,8,263,264,265,528):
            for destination in destinations:
                for stack in (STACK,STACK+4):
                    new,old=ARM(rom,iw),ARM(clean,iw)
                    for machine in (new,old):machine.put(0x02000000,ram)
                    before=new.read(UNIT,528)
                    newpc=new.word(0x0836d4bc) if dispatch=='iwram' else 0x081443fc
                    oldpc=0x03005ee9 if dispatch=='iwram' else 0x081443fc
                    result=new.call(newpc,destination,UNIT,length,stack=stack)
                    reference=old.call(oldpc,destination,UNIT,length,stack=stack)
                    check('copy_native_return',result,reference)
                    check('copy_native_bytes',new.read(destination,length),old.read(destination,length))
                    check('copy_source_unchanged',new.read(UNIT,528),before)
                    check('copy_name_word',new.read(destination,4),old.read(destination,4))
report={'passed':True,'romSha1':romhash,'checks':sum(counts.values()),'groups':counts,'snapshots':rows,
        'scope':'Captured unit name words and native whole-copy return/data contract. Reaction-label decoder investigated separately; no complete frame replay or causal exoneration of every AP hook.'}
(ROOT/'build/expansion/probes/chop-preview-copy-tests.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='snapshots'},indent=2))
for row in rows:print(row['snapshot'],len(row['units']),row['tablePointerInRAM'],row['tablePointerInIWRAM'])
