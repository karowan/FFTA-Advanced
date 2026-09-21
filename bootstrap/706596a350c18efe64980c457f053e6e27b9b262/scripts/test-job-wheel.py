"""Bounded native job-wheel integration/ABI tests; no visible emulator or save writes."""
import ast
import ctypes as C
import hashlib
import importlib.util
import json
import pathlib
import struct
import sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
OUT=ROOT/'build/expansion/probes'
meta=json.loads((OUT/'job-ui.json').read_text())
probe=(OUT/'job-ui.gba').read_bytes()
assert hashlib.sha1(probe).hexdigest()==meta['romSha1']
base=bytearray(probe)
for change in meta['changes']:
    original=bytes.fromhex(change['expected'])
    base[change['offset']:change['offset']+len(original)]=original
base=bytes(base)
assert hashlib.sha1(base).hexdigest()==meta['baseSha1']
(OUT/'job-wheel-input.gba').write_bytes(probe)
(OUT/'job-wheel-input.json').write_text(json.dumps(meta,indent=2))
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
for filename,names in [('test-equipment-legality.py',('ARM','iwram_from_boot'))]:
    tree=ast.parse((ROOT/'scripts'/filename).read_text())
    nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in names]
    for node in nodes:
        for child in ast.walk(node):
            if isinstance(child,ast.Constant) and child.value==50000:child.value=500000
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'<native-harness>','exec'))
iwram=iwram_from_boot()
native,expanded=ARM(base,iwram),ARM(probe,iwram)
MENU,LIST=0x02008000,0x02007040
checks,failures={},[]
def check(group,case,ok,detail=None):
    checks[group]=checks.get(group,0)+1
    if not ok:failures.append({'group':group,'case':case,'detail':detail})
def w(machine,address,value):machine.put(address,struct.pack('<I',value))
def helper(site,saved=False):
    jump=(site+5)&~3 if saved else site
    entry=expanded.word(0x08000000+jump+4)&~1
    code=expanded.read(entry,96)
    for p in range(0,92,2):
        a,b=struct.unpack_from('<HH',code,p)
        if a&0xf800==0xf000 and b&0xf800==0xf800:
            off=((a&2047)<<12)|((b&2047)<<1)
            if off&0x400000:off-=0x800000
            return entry+p+4+off
    raise AssertionError(('no helper',hex(site)))
INITIAL=helper(0x85c90)
TURN=helper(0x8616c,True)
CONFIRM=helper(0x861be,True)
def setup(machine,race=1,job=2,identity=1,mastered=False):
    machine.put(0x02000000,bytes(0x40000))
    machine.put(0x02001e70,b'FFTAEXP1\x01')
    unit=bytearray(264);unit[4]=identity;unit[5]=job;unit[6]=race;unit[7]=job
    unit[0x34]={1:178,2:111,3:124,4:118,5:116}.get(race,1)
    unit[0x18]=100;unit[0x1a]=100
    if mastered:unit[0x40:0xd0]=bytes([0xe4])*144
    machine.put(UNIT,unit)
    if mastered:machine.put(0x02001b40,bytes([0xe4])*34)
    w(machine,0x03002818,MENU);w(machine,MENU+0x1d0c,UNIT)
    w(machine,0x03000e34,0x02006000)
    machine.put(LIST-16,b'\xa5'*44)
    machine.put(0x03000002,b'\x00\x00')
    return bytes(unit)

# Native C8A24 output/candidate ordering, protected identities, buffer guards.
for race,job in [(1,2),(2,13),(3,22),(4,28),(5,36)]:
    for mastered in (False,True):
        for residue in (0,4):
            for m in (native,expanded):setup(m,race,job,mastered=mastered)
            count=native.call(0x080c8a24,UNIT,LIST,stack=STACK+residue)
            old=native.read(LIST,count)
            actual=expanded.call(INITIAL,UNIT,LIST,stack=STACK+residue)
            shown=expanded.read(LIST,actual)
            check('wheel-buffer',(race,mastered,residue),expanded.read(LIST-16,16)==b'\xa5'*16 and expanded.read(LIST+12,16)==b'\xa5'*16)
            check('native-prefix',(race,mastered,residue),all(x in old for x in shown if (x&127)<116),(list(old),list(shown)))
            check('bounded-page',(race,mastered,residue),actual<=12 and actual>0,actual)

for identity in (9,10,94):
    for m in (native,expanded):setup(m,identity=identity,mastered=True)
    old=native.call(0x080c8a24,UNIT,LIST)
    new=expanded.call(INITIAL,UNIT,LIST)
    check('story-zero',identity,old==new==0,(old,new))
    check('story-cleared',identity,expanded.read(LIST,12)==bytes(12))

for identity in range(116):
    for m in (native,expanded):setup(m,identity=identity,mastered=True)
    old=native.call(0x080c8a24,UNIT,LIST)
    new=expanded.call(INITIAL,UNIT,LIST)
    expected=0 if old==0 else (old+3)//2 if old+2>12 else old+2
    check('native-identity-restrictions',identity,new==expected,(old,new,expected))
    check('native-twelve-byte-ABI',identity,native.read(LIST-16,16)==b'\xa5'*16 and native.read(LIST+12,16)==b'\xa5'*16)

# Paging must use the list after native89BA4 sorts it. Stub only destructive
# sprite deletion and sound; record exact cleanup requests and retain real list/AP code.
events=[]
def ui_services(u,address,size,data):
    if address in (0x0804c7a0,0x08141540):
        events.append((address,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)))
        u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
expanded.u.hook_add(UC_HOOK_CODE,ui_services,begin=0x0804c7a0,end=0x0804c7a0)
expanded.u.hook_add(UC_HOOK_CODE,ui_services,begin=0x08141540,end=0x08141540)
pages=[]
for residue in (0,4):
    setup(expanded,mastered=True)
    count=expanded.call(INITIAL,UNIT,MENU+0x1278,stack=STACK+residue)
    expanded.call(0x08089ba4,MENU+0x1278,0,count-1,stack=STACK+residue)
    w(expanded,MENU+0x1270,count)
    first=expanded.read(MENU+0x1278,count)
    for turn in range(4):
        events.clear();expanded.put(0x03000002,struct.pack('<H',0x100 if turn%2==0 else 0x200))
        before=expanded.read(MENU+0x1278,count)
        count2=expanded.call(TURN,stack=STACK+residue)
        check('page-change',(residue,turn),count2>0 and expanded.read(MENU+0x1278,count2)!=before,(list(before),list(expanded.read(MENU+0x1278,count2))))
        check('sprite-cleanup',(residue,turn),[e[2] for e in events if e[0]==0x0804c7a0]==list(range(count))+[0x1a],events)
        expanded.call(0x08089ba4,MENU+0x1278,0,count2-1,stack=STACK+residue)
        w(expanded,MENU+0x1270,count2);count=count2
        pages.append(list(expanded.read(MENU+0x1278,count)))
    check('page-return',residue,expanded.read(MENU+0x1278,count)==first)

# Execute actual inline stubs and native list sorting/row initialization. Stop
# before85D70 starts graphics work, retaining the real arrays and selector code.
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,
      UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,
      UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
alignment=[]
def aligned(u,address,size,data):alignment.append((address,u.reg_read(UC_ARM_REG_SP)))
for address in (INITIAL,TURN,CONFIRM,helper(0xcb9e0),helper(0xcba14),helper(0x12e6a4)):
    expanded.u.hook_add(UC_HOOK_CODE,aligned,begin=address,end=address)
def segment(machine,begin,ends,values,residue):
    machine.u.reg_write(UC_ARM_REG_CPSR,0x20000030)
    for n,reg in enumerate(REGS):machine.u.reg_write(reg,values.get(n,0x55000000+n))
    machine.u.reg_write(UC_ARM_REG_SP,STACK+residue)
    machine.u.reg_write(UC_ARM_REG_LR,RETURN|1)
    def stop(u,address,size,data):
        if address in ends:u.emu_stop()
    hook=machine.u.hook_add(UC_HOOK_CODE,stop)
    try:machine.u.emu_start(begin|1,0,count=800000)
    except UcError as error:
        raise AssertionError((str(error),hex(machine.u.reg_read(UC_ARM_REG_PC)),[hex(machine.u.reg_read(r)) for r in REGS])) from error
    finally:machine.u.hook_del(hook)
    pc=machine.u.reg_read(UC_ARM_REG_PC)
    assert pc in ends,('segment return',hex(begin),hex(pc))
    assert machine.u.reg_read(UC_ARM_REG_SP)==STACK+residue
    return pc,[machine.u.reg_read(r) for r in REGS],machine.u.reg_read(UC_ARM_REG_CPSR)&0xf0000000

for residue in (0,4):
    for job in list(range(2,13))+[116,117]:
        setup(expanded,job=job,mastered=True)
        # Initial native code saved the current job here before85C90.
        expanded.put(MENU+0x1274,bytes([job]))
        expanded.put(MENU+0x1278,b'\xa5'*12)
        expanded.put(MENU+0x1278+12,b'\xa5'*4)
        expanded.put(MENU+0x1284+28*12,b'\xa5'*28)
        segment(expanded,0x08085c90,{0x08085d70},{0:UNIT,1:MENU+0x1278,4:0x1278,6:0x03002818},residue)
        count=expanded.word(MENU+0x1270)
        ids=[expanded.read(MENU+0x1287+28*i,1)[0] for i in range(count)]
        selected=expanded.read(MENU+0x1275,1)[0]
        check('initial-current',(job,residue),job in ids and selected<count and ids[selected]==job,(ids,selected))
        check('row-capacity',(job,residue),count in (6,7) and expanded.read(MENU+0x1284+28*12,28)==b'\xa5'*28,(count,ids))
        visited=set(ids)
        for turn in range(2):
            events.clear();expanded.put(0x03000002,struct.pack('<H',0x100))
            old_count=count
            segment(expanded,0x0808616c,{0x08085d70},{},residue)
            count=expanded.word(MENU+0x1270)
            ids=[expanded.read(MENU+0x1287+28*i,1)[0] for i in range(count)]
            check('installed-page',(job,residue,turn),count==13-old_count and 0 not in ids,(count,ids))
            check('installed-cleanup',(job,residue,turn),[e[2] for e in events if e[0]==0x0804c7a0]==list(range(old_count))+[0x1a],events)
            visited.update(ids)
        check('all-human-jobs',(job,residue),visited==set(range(2,13))|{116,117},sorted(visited))

# Non-paging fallthrough must replay the original live registers and flags.
for residue in (0,4):
    for race,job,keys,timer in [(1,2,0,0),(1,2,0x101,0),(1,2,0x102,0),(1,2,0x100,1),(2,13,0x100,0)]:
        for m in (native,expanded):
            setup(m,race,job,mastered=True);m.put(0x03000002,struct.pack('<H',keys));m.put(MENU+0x25,bytes([timer]))
        a=segment(native,0x0808616c,{0x08086178},{},residue)
        b=segment(expanded,0x0808616c,{0x08086178},{},residue)
        check('input-fallthrough',(race,keys,timer,residue),a==b,(a,b))

# Installed confirmation hook independently re-evaluates new prerequisite AP,
# even if a stale row remains marked selectable. Old jobs retain native replay.
for residue in (0,4):
    for job in [2,12,116,117]:
        for mastery in (False,True):
            for m in (native,expanded):
                setup(m,mastered=mastery);w(m,MENU+0x1270,1)
                m.put(MENU+0x1275,b'\x00');m.put(MENU+0x1287,bytes([job]));m.put(MENU+0x1284,b'\x01')
            a=segment(native,0x080861be,{0x080861c8},{2:MENU},residue)
            b=segment(expanded,0x080861be,{0x080861c8,0x08086230},{2:MENU},residue)
            allowed=job<116 or mastery
            check('confirmation',(job,mastery,residue),b[0]==(0x080861c8 if allowed else 0x08086230),hex(b[0]))
            if allowed:check('confirm-replay',(job,mastery,residue),a==b,(a,b))

# Donor wrappers: invoke the actual native resource-selection entry and inspect
# the resource decoder call contract, without simulating graphics decompression.
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
def ap_address(race,index):return 0x02001b40+index-144 if race==1 and index>=144 else UNIT+0x40+index
for new_job in [j for j in registry['jobs'] if 116<=j['id']<=125]:
    race,job=new_job['race'],new_job['id']
    groups=[]
    for requirement in new_job['prerequisites']:
        required=requirement['jobId']
        first=native.call(0x080c8570,required,required,0x25)
        last=native.call(0x080c8570,required,required,0x26)
        indices=list(range(first,last+1))
        indices += [o['abilityIndex'] for l in registry['lessons'] if l['nativeType']==1 for o in l['owners'] if o['jobId']==required and o['abilityIndex'] not in indices]
        actions=[]
        for index in indices:
            record=native.call(0x080cd480,race,index)
            row=native.read(record,8)
            if row[6]==1 and row[7]:actions.append((index,row[7]))
        assert len(actions)>=requirement['actions']
        groups.append((actions[:requirement['actions']],requirement))
    for residue in (0,4):
        for mode in ['mastered','equipment-only']+['short-'+str(i) for i in range(len(groups))]:
            setup(expanded,race,job)
            for n,(actions,requirement) in enumerate(groups):
                for k,(index,cost) in enumerate(actions):
                    value=cost
                    if mode=='equipment-only':value=128
                    elif mode=='short-'+str(n) and k==len(actions)-1:value=cost-1
                    expanded.put(ap_address(race,index),bytes([value]))
            unit_before=expanded.read(UNIT,264);ap_before=expanded.read(0x02001b40,816)
            _,registers,_=segment(expanded,0x08085c90,{0x08085c98},{0:UNIT,1:MENU+0x1278,4:0x1278,6:0x03002818},residue)
            page=expanded.read(MENU+0x1278,registers[2])
            row=next((v for v in page if v&127==job),None)
            check('new-prerequisites',(job,mode,residue),row is not None and bool(row&128)==(mode=='mastered' or not groups),list(page))
            check('AP-stat-isolation',(job,mode,residue),expanded.read(UNIT,264)==unit_before and expanded.read(0x02001b40,816)==ap_before)

graphics={native:[],expanded:[]}
for machine in (native,expanded):
    def resource(u,address,size,data,m=machine):
        graphics[m].append(tuple(u.reg_read(r) for r in REGS[:4]))
        u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    machine.u.hook_add(UC_HOOK_CODE,resource,begin=0x08005318,end=0x08005318)
donors=[6,3,13,15,25,27,41,36,29,30]
for residue in (0,4):
    for job in range(256):
        expected=donors[job-116] if 116<=job<=125 else job
        graphics[native].clear();graphics[expanded].clear()
        native.call(0x080cb9e0,LIST,expected,stack=STACK+residue)
        expanded.call(0x080cb9e0,LIST,job,stack=STACK+residue)
        check('icon-resource',(job,residue),graphics[native]==graphics[expanded],(graphics[native],graphics[expanded]))
        a=native.call(0x080cba14,expected,stack=STACK+residue)
        b=expanded.call(0x080cba14,job,stack=STACK+residue)
        check('palette',(job,residue),a==b,(a,b))

# Reaction guard: native0..15 behavior over no status, each44 native status
# bits, and all44 bits. New128..255 return0 before any native mask lookup.
mask_reads=[]
def mask_read(u,access,address,size,value,data):mask_reads.append((address,size))
expanded.u.hook_add(UC_HOOK_MEM_READ,mask_read,begin=0x08527d5c,end=0x08528a00)
patterns=[0]+[1<<i for i in range(44)]+[(1<<44)-1]
for residue in (0,4):
    for reaction in list(range(16))+list(range(128,256)):
        for pattern in patterns:
            for m in (native,expanded):
                setup(m)
                # Isolated synthetic assigned lesson1, using the real CD4D4.
                pointers=bytearray(28);struct.pack_into('<I',pointers,4,0x02022000)
                m.put(0x02021800,pointers);w(m,0x080cd500,0x02021800)
                m.put(0x02022008,struct.pack('<HHHBB',0,0,reaction,2,1))
                m.put(UNIT+0x3a,b'\x01');m.put(UNIT+0xe8,pattern.to_bytes(8,'little'))
            mask_reads.clear()
            unit_before=expanded.read(UNIT,264)
            b=expanded.call(0x0812e6a4,UNIT,stack=STACK+residue)
            check('reaction-unit-isolation',(reaction,pattern,residue),expanded.read(UNIT,264)==unit_before)
            if reaction<16:
                a=native.call(0x0812e6a4,UNIT,stack=STACK+residue)
                check('original-reactions',(reaction,pattern,residue),a==b,(a,b))
            else:
                check('inactive-reactions',(reaction,pattern,residue),b==0 and not mask_reads,(b,mask_reads))
check('C-entry-alignment','all installed entries',all(sp%8==0 for _,sp in alignment),[v for v in alignment if v[1]%8])
check('native-ABI-scope','C8A24 and C8C24 entries untouched',probe[0xc8a24:0xc8b26]==base[0xc8a24:0xc8b26] and probe[0xc8c24:0xc8d00]==base[0xc8c24:0xc8d00])
for change in meta['changes']:
    jump=(change['offset']+5)&~3 if change['savesR3'] else change['offset']
    entry=expanded.word(0x08000000+jump+4)&~1
    for offset in range(0,128,4):
        value=expanded.word(entry+offset)
        if 0x08000000<=value<0x09000000 and value&1:
            target=(value&~1)-0x08000000
            conflicts=[c['name'] for c in meta['changes'] if c['offset']<=target<c['offset']+c['size']]
            check('continuation-outside-hooks',(change['name'],hex(value)),not conflicts,conflicts)

result={'romSha1':meta['romSha1'],'baseSha1':meta['baseSha1'],'checks':checks,'failures':failures,'pages':pages,
        'alignedEntryCalls':len(alignment),
        'nativeCalls':native.calls,'expandedCalls':expanded.calls}
(OUT/'job-wheel-test.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
if failures:raise SystemExit(1)
