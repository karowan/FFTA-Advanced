"""Disposable native-clamp integration test for the unused Chop multiplier.

Does not modify any pipeline ROM or install combat in a playable build.
"""
import ast
import ctypes as C
import hashlib
import importlib.util
import json
import pathlib
import random
import struct
import sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
OUT=ROOT/'build/expansion/probes'
CHOP=next(l['globalAbilityId'] for l in json.loads((ROOT/'build/expansion/registry.json').read_text())['lessons'] if l['id']=='SLD-AX-A1')
TOMA=next(l['globalAbilityId'] for l in json.loads((ROOT/'build/expansion/registry.json').read_text())['lessons'] if l['id']=='SLD-AX-A2')
SHATTER,ARMOR=CHOP+3,CHOP+4
FACTORS={CHOP:11,TOMA:9,CHOP+2:9,SHATTER:10,ARMOR:10,CHOP+5:11,CHOP+6:11,431:18}
FACTORS.update({357:95,358:75})
DENOMINATORS={357:100,358:100}
metadata=json.loads((OUT/'axe-visual.json').read_text())
base=(OUT/'axe-visual.gba').read_bytes()
engine=(ROOT/'build/expansion/engine.bin').read_bytes()
sha=lambda b:hashlib.sha1(b).hexdigest()
assert sha(base)==metadata['romSha1']
upstream_sha=sha(base)
engine_overlay=base[0x1100000:0x1100000+len(engine)]!=engine
if engine_overlay:
    # A requested fresh engine can be tested before every upstream probe is
    # rebuilt. This disposable image is not a composed/playable pipeline ROM:
    # unrelated old hook bindings may no longer match the overlaid engine.
    assert len(engine)<0x100000
    updated=bytearray(base);updated[0x1100000:0x1100000+len(engine)]=engine;base=bytes(updated)
symbols={}
for line in (ROOT/'build/expansion/engine.symbols').read_text().splitlines():
    fields=line.split()
    if len(fields)==3:symbols[fields[2]]=int(fields[0],16)
HELPER=symbols['ffta_physical_final']
ENTRY=symbols['ffta_physical_final_entry']
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
START,END=0x1300E2,0x1300F2
assert base[START:END]==clean[START:END]
patched=bytearray(base)
for p in range(START,END,2):struct.pack_into('<H',patched,p,0x46c0)
struct.pack_into('<H',patched,START,0xb408)
jump=(START+5)&~3
assert jump+8<=END
struct.pack_into('<HHI',patched,jump,0x4b00,0x4718,ENTRY|1)
patched=bytes(patched)
(OUT/'physical-final-test-only.gba').write_bytes(patched)
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'<native-harness>','exec'))
iwram=iwram_from_boot()
native,expanded=ARM(base,iwram),ARM(patched,iwram)
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,
      UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,
      UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
TARGET=UNIT+3*264
checks,failures={},[]
def u32(value):return value&0xffffffff
def s32(value):return value-0x100000000 if value&0x80000000 else value
def check(group,case,condition,detail=None):
    checks[group]=checks.get(group,0)+1
    if not condition:failures.append({'group':group,'case':case,'detail':detail})
def reference(value,action):
    if action not in FACTORS:return value
    magnitude=min(abs(value)*FACTORS[action]//DENOMINATORS.get(action,10),0x7fffffff)
    return -magnitude if value<0 else magnitude

# The helper now legitimately inspects ordered primary equipment for restorative
# effects. Keep these arithmetic fixtures valid and explicitly unequipped.
for machine in (native,expanded):machine.put(UNIT,bytes(1056))

# Exhaustive16-bit action-ID passthrough plus the one selected action.
for residue in (0,4):
    for action in range(65536):
        value=-137 if action&1 else 137
        result=s32(expanded.call(HELPER,u32(value),action,UNIT,TARGET,stack=STACK+residue))
        check('all-action-IDs',(action,residue),result==reference(value,action),result)

rng=random.Random(0x1300E2)
values=sorted(set(range(-1200,1201))|{-2147483648,-2147483647,-1952257862,-1952257861,
              1952257861,1952257862,2147483646,2147483647}|{rng.randrange(-2147483648,2147483648) for _ in range(512)})
for action in (0,423,CHOP,TOMA,426,SHATTER,ARMOR,429,430,431,65535,65536+CHOP,0xffffffff):
    for value in values:
        actual=s32(expanded.call(HELPER,u32(value),action,UNIT,TARGET))
        check('signed-helper',(value,action),actual==reference(value,action),actual)

observed=[]
def capture(u,address,size,data):
    observed.append(tuple(u.reg_read(r) for r in REGS[:4])+(u.reg_read(UC_ARM_REG_SP),))
expanded.u.hook_add(UC_HOOK_CODE,capture,begin=HELPER&~1,end=HELPER&~1)
segments=0
def segment(machine,value,action,residue,flags,gear=(),vitals=(250,250)):
    global segments
    u=machine.u
    u.reg_write(UC_ARM_REG_CPSR,flags|0x30)
    initial=[0x55000000+n for n in range(12)]
    initial[5]=u32(value);initial[8]=UNIT;initial[10]=action
    for reg,v in zip(REGS,initial):u.reg_write(reg,v)
    sp=STACK+residue
    u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,RETURN|1)
    frame=bytearray([0xa5]*128)
    # Decoys on both sides catch off-by-one-word argument recovery. The target
    # belongs to original formula SP+0x18, not the shim's current stack base.
    struct.pack_into('<III',frame,0x14,UNIT+264,TARGET,UNIT+528)
    fixture=bytearray([0x6d]*1056)
    fixture[0x2a:0x34]=bytes(10)
    struct.pack_into('<5H',fixture,0x2a,*(list(gear)+[0]*(5-len(gear))))
    struct.pack_into('<HH',fixture,TARGET-UNIT+0x18,*vitals)
    machine.put(sp,frame);machine.put(UNIT,fixture)
    observed.clear();writes=[]
    def written(u,access,address,size,value,data):writes.append((address,size))
    hook=u.hook_add(UC_HOOK_MEM_WRITE,written)
    try:u.emu_start(0x081300e3,0x081300f2,count=50000)
    finally:u.hook_del(hook)
    assert u.reg_read(UC_ARM_REG_PC)==0x081300f2
    assert u.reg_read(UC_ARM_REG_SP)==sp
    segments+=1
    return {'regs':[u.reg_read(r) for r in REGS], 'flags':u.reg_read(UC_ARM_REG_CPSR)&0xf0000000,
            'frame':machine.read(sp,128)==bytes(frame),'units':machine.read(UNIT,1056)==bytes(fixture),
            'writes':writes,'args':list(observed)}

# Independent immutable input values supply r5. The expected native clamp is
# executed on the mathematical helper result, never on a post-hook register.
for residue in (0,4):
    for action in (0,423,CHOP,TOMA,426,SHATTER,ARMOR,429,430,431,65535,65536+CHOP,0xffffffff):
        for value in values:
            flags=0xf0000000 if value&1 else 0
            expected=reference(value,action)
            a=segment(native,expected,action,residue,flags)
            b=segment(expanded,value,action,residue,flags)
            case=(value,action,residue)
            check('native-registers',case,a['regs']==b['regs'],(a['regs'],b['regs']) if a['regs']!=b['regs'] else None)
            check('native-NZCV',case,a['flags']==b['flags'],(a['flags'],b['flags']))
            check('signed-clamp',case,s32(b['regs'][5])==max(-999,min(999,expected)),s32(b['regs'][5]))
            check('frame-units',case,b['frame'] and b['units'])
            check('original-arguments',case,len(b['args'])==1 and b['args'][0][:4]==(u32(value),action,UNIT,TARGET),b['args'])
            check('C-stack-alignment',case,len(b['args'])==1 and b['args'][0][4]%8==0,b['args'])
            check('stack-writes-only',case,all(sp>=STACK+residue-0x400 and sp+n<=STACK+residue for sp,n in b['writes']),b['writes'])

# Native item124 carries3F. Verify both signs and INT32 edges through the actual
# installed shim; a restorative offhand cannot change an ordinary primary.
for residue in (0,4):
 for gear in ((124,1),(1,124),(0,124)):
  for action in (423,CHOP,TOMA,426,SHATTER,ARMOR,429,430,431):
   for value in (-2147483648,-137,0,137,2147483647):
    expected=reference(value,action)
    if action in FACTORS and next(i for i in gear if i)==124:expected=-abs(expected)
    a=segment(native,expected,action,residue,0xf0000000,gear)
    b=segment(expanded,value,action,residue,0xf0000000,gear)
    case=(residue,gear,action,value)
    check('restorative-shim-registers',case,a['regs']==b['regs'])
    check('restorative-shim-NZCV',case,a['flags']==b['flags'])
    check('restorative-shim-frame',case,b['frame'] and b['units'])
    check('restorative-shim-arguments',case,len(b['args'])==1 and b['args'][0][:4]==(u32(value),action,UNIT,TARGET) and b['args'][0][4]%8==0)

for residue in (0,4):
 for maximum in (0,1,2,3,99,100,65535):
  for hp in sorted({0,maximum//2,min(65535,maximum//2+1),maximum}):
   factor=18 if maximum and hp*2<=maximum else 11
   for gear in ((),(124,1),(1,124)):
    for value in (-2147483648,-137,0,137,2147483647):
     expected=min(abs(value)*factor//10,0x7fffffff)*(-1 if value<0 or gear[:1]==(124,) else 1)
     a=segment(native,expected,430,residue,0xf0000000,gear,(hp,maximum))
     b=segment(expanded,value,430,residue,0xf0000000,gear,(hp,maximum))
     check('Executioner-exact-threshold-ABI',(residue,hp,maximum,gear,value),a['regs']==b['regs'] and a['flags']==b['flags'] and b['frame'] and b['units'],(a['regs'][5],b['regs'][5]))

result={'status':'PASS' if not failures else 'FAIL','engineSha1':sha(engine),'baseSha1':sha(base),
        'upstreamRomSha1':upstream_sha,'testOnlyEngineOverlay':engine_overlay,
        'testImageSha1':sha(patched),'helper':hex(HELPER),'entry':hex(ENTRY),'checks':checks,
        'failures':failures,'completeCalls':native.calls+expanded.calls,'inlineSegments':segments,
        'semantics':'Chop11/10, Tomahawk9/10, Shatter/Armor1/1; one absolute-magnitude truncation; restore sign or force restorative-primary negative; helper saturates +/-INT_MAX then native clamps +/-999',
        'scope':'Disposable shim/math test only. No combat pipeline image was changed or accepted.'}
(OUT/'physical-final-test.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({**result,'failures':failures[:10]},indent=2))
if failures:raise SystemExit(1)
