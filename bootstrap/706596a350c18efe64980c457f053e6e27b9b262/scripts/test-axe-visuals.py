"""Native differential audit of axe switches and scoped new-job knife poses."""
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
meta=json.loads((OUT/'axe-visual.json').read_text())
probe=(OUT/'axe-visual.gba').read_bytes()
assert hashlib.sha1(probe).hexdigest()==meta['romSha1']
base=bytearray(probe)
for change in meta['changes']:
    data=bytes.fromhex(change['expected']);base[change['offset']:change['offset']+len(data)]=data
base=bytes(base)
assert hashlib.sha1(base).hexdigest()==meta['baseSha1']
(OUT/'axe-visual-test-input.gba').write_bytes(probe)
(OUT/'axe-visual-test-input.json').write_text(json.dumps(meta,indent=2))
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'<native-harness>','exec'))
iwram=iwram_from_boot()
native,expanded=ARM(base,iwram),ARM(probe,iwram)
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,
      UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,
      UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12]
STATE=0x02004000
SITES=[(0x986DA,0x986E6,0x98758,5,0x9875A),
       (0xA58A0,0xA58AC,0xA597C,0,0xA5982),
       (0xA7EDC,0xA7EE8,0xA7FB8,0,0xA7FBE),
       (0xB3C64,0xB3C70,0xB3D88,0,0xB41BC)]
checks,failures={},[]
segments=0
def check(group,case,condition,detail=None):
    checks[group]=checks.get(group,0)+1
    if not condition:failures.append({'group':group,'case':case,'detail':detail})
events={native:[],expanded:[]}
for machine in (native,expanded):
    def sound(u,address,size,data,m=machine):
        events[m].append(u.reg_read(UC_ARM_REG_R0))
        u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    machine.u.hook_add(UC_HOOK_CODE,sound,begin=0x08141520,end=0x08141520)

def segment(machine,begin,ends,values,residue,flags=0,unitdata=None):
    global segments
    u=machine.u;u.reg_write(UC_ARM_REG_CPSR,flags|0x30)
    for n,reg in enumerate(REGS):u.reg_write(reg,values.get(n,0x55000000+n))
    u.reg_write(UC_ARM_REG_SP,STACK+residue);u.reg_write(UC_ARM_REG_LR,RETURN|1)
    machine.put(STACK-32,bytes([0xa5])*128)
    machine.put(STATE,bytes(0x2000));events[machine].clear()
    if unitdata is not None:
        machine.put(UNIT,unitdata);machine.put(STATE,struct.pack('<I',UNIT))
    writes=[]
    def stop(u,address,size,data):
        if address in ends:u.emu_stop()
    def written(u,access,address,size,value,data):writes.append((address,size))
    h=u.hook_add(UC_HOOK_CODE,stop);w=u.hook_add(UC_HOOK_MEM_WRITE,written)
    try:u.emu_start(begin|1,0,count=50000)
    finally:u.hook_del(h);u.hook_del(w)
    pc=u.reg_read(UC_ARM_REG_PC)
    assert pc in ends,('no continuation',hex(begin),hex(pc))
    assert u.reg_read(UC_ARM_REG_SP)==STACK+residue,('SP',hex(begin),residue)
    segments+=1
    return {'pc':pc,'regs':[u.reg_read(r) for r in REGS],
            'flags':u.reg_read(UC_ARM_REG_CPSR)&0xf0000000,
            'frame':machine.read(STACK+residue,64).hex(),
            'state':machine.read(STATE,0x2000).hex(),'sounds':list(events[machine]),'writes':writes}

types=list(range(256))+[0xffffffff]
for start,continuation,fallback,source,finish in SITES:
    for residue in (0,4):
        for value in types:
            for flags in (0,0xf0000000):
                args={source:value,4:453,6:STATE,7:453,10:6}
                # r5 is the true type at the actor switch, not r0. Assign after
                # generic fixture fields so the raw type is never overwritten.
                args[source]=value
                old_args=dict(args);old_args[source]=5 if value==31 else value
                a=segment(native,0x08000000+start,{0x08000000+continuation,0x08000000+fallback},old_args,residue,flags)
                b=segment(expanded,0x08000000+start,{0x08000000+continuation,0x08000000+fallback},args,residue,flags)
                if value==31 and source==5:a['regs'][5]=31
                for key in ('pc','regs','flags','frame','state','sounds'):
                    check('dispatch-'+key,(hex(start),value,residue,flags),a[key]==b[key],(a[key],b[key]) if a[key]!=b[key] else None)
                check('stack-only-switch',(hex(start),value,residue,flags),all(STACK+residue-4<=p and p+n<=STACK+residue for p,n in b['writes']),b['writes'])
            # Follow all19 native case families and original fallback bodies.
            a=segment(native,0x08000000+start,{0x08000000+finish},old_args,residue)
            b=segment(expanded,0x08000000+start,{0x08000000+finish},args,residue)
            for key in ('pc','regs','flags','frame','state','sounds'):
                check('case-body-'+key,(hex(start),value,residue),a[key]==b[key],(a[key],b[key]) if a[key]!=b[key] else None)
            if start==0x986DA and value==31:
                check('actor-derived-class',residue,b['regs'][5]==1,b['regs'][5])

# Only the four guarded hook ranges may differ from the composed baseline.
check('scope','exact hook ledger',[(c['offset'],c['size']) for c in meta['changes']]==[(s[0],12) for s in SITES])
expected=bytearray(base)
for change in meta['changes']:
    p,n=change['offset'],change['size'];expected[p:p+n]=probe[p:p+n]
check('scope','four switches only',bytes(expected)==probe)

# Native item descriptors and every supported getter selector remain real.
# This covers item0, all375 originals, and all85 added items, including8 axes.
for residue in (0,4):
    for item in range(461):
        for selector in list(range(20))+[255]:
            a=native.call(0x080ca7a4,item,selector,stack=STACK+residue)
            b=expanded.call(0x080ca7a4,item,selector,stack=STACK+residue)
            check('item-getter',(item,selector,residue),a==b,(a,b))
        if 453<=item<=460:
            check('real-axe-type',(item,residue),expanded.call(0x080ca7a4,item,3,stack=STACK+residue)==31)

# Whole native swing-sound function, including the real item getter. The
# baseline models only the desired visual switch input; item records stay31.
def baseline_map(u,address,size,data):
    if u.reg_read(UC_ARM_REG_R0)==31:u.reg_write(UC_ARM_REG_R0,5)
native.u.hook_add(UC_HOOK_CODE,baseline_map,begin=0x080a7edc,end=0x080a7edc)
for residue in (0,4):
    for item in range(461):
        events[native].clear();events[expanded].clear()
        native.call(0x080a7ec4,item,stack=STACK+residue)
        expanded.call(0x080a7ec4,item,stack=STACK+residue)
        check('whole-swing-sound',(item,residue),events[native]==events[expanded],(events[native],events[expanded]))
        if 453<=item<=460:check('axe-sound',(item,residue),events[expanded]==[0x7b],events[expanded])

# Follow actor selection beyond its first case, using actual axe graphics
# properties, every native action-animation switch6..17 and four facing values.
def baseline_actor_map(u,address,size,data):
    if u.reg_read(UC_ARM_REG_R5)==31:u.reg_write(UC_ARM_REG_R5,5)
native.u.hook_add(UC_HOOK_CODE,baseline_actor_map,begin=0x080986da,end=0x080986da)
for residue in (0,4):
    for item in range(453,461):
        for mode in range(6,18):
            for facing in range(4):
                values={0:0,4:0,5:31,6:STATE,7:item,8:facing,
                        9:expanded.call(0x080ca7a4,item,8),10:mode}
                original=dict(values);original[5]=5
                # Enter before all three native item getter calls. This reads
                # true type31, selector9 into SP+0C, and selector8 into r9.
                a=segment(native,0x080986b2,{0x080988a4},original,residue)
                b=segment(expanded,0x080986b2,{0x080988a4},values,residue)
                for key in ('regs','flags','frame','state'):
                    check('actor-animation-'+key,(item,mode,facing,residue),a[key]==b[key],(a[key],b[key]) if a[key]!=b[key] else None)

# The evaluated wrapper, not a global roster lookup, owns the pose selection.
# Compare each new knife exception against its supported native donor pose.
for race,job in [(r,j) for r in range(24) for j in range(126)]:
    data=bytearray(264);data[6]=race;data[5]=job
    wanted=12 if (race,job)==(3,120) else (8 if (race,job)==(4,124) else 7)
    for residue in (0,4):
        values={0:0,4:0,5:7,6:STATE,7:74,8:2,9:0,10:7}
        original=dict(values);original[5]=wanted
        a=segment(native,0x080986da,{0x080988a4},original,residue,unitdata=data)
        b=segment(expanded,0x080986da,{0x080988a4},values,residue,unitdata=data)
        for key in ('regs','flags','frame','state'):
            check('new-job-knife-scope-'+key,(race,job,residue),a[key]==b[key],(a[key],b[key]) if a[key]!=b[key] else None)
for race,job,donor_type in ((3,120,12),(4,124,8)):
    for category in range(32):
        for mode in range(6,18):
            data=bytearray(264);data[6]=race;data[5]=job
            values={0:0,4:0,5:category,6:STATE,7:74,8:2,9:0,10:mode}
            original=dict(values);original[5]=donor_type if category==7 else category
            a=segment(native,0x080986da,{0x080988a4},original,4,unitdata=data)
            b=segment(expanded,0x080986da,{0x080988a4},values,4,unitdata=data)
            for key in ('regs','flags','frame','state'):
                check('new-job-category-animation-'+key,(race,job,category,mode),a[key]==b[key],(a[key],b[key]) if a[key]!=b[key] else None)
    
result={'romSha1':meta['romSha1'],'baseSha1':meta['baseSha1'],'checks':checks,'failures':failures,
        'nativeCalls':native.calls,'expandedCalls':expanded.calls,'inlineSegments':segments,
        'scope':'Native switch/case ABI and resource/sound choices; no rendered battle acceptance'}
(OUT/'axe-visual-test.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({**result,'failures':failures[:20]},indent=2))
if failures:raise SystemExit(1)
