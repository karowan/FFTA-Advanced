"""Deterministic recovery entitlement, linked pub queues and native consumers.

No player saves, GUI agent, or modified test ROM. Every case uses the installed
image with explicit RAM inputs; native boundaries are observed, never replaced.
"""
import collections
import atexit
import hashlib
import itertools
import json
import pathlib
import struct
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *

meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text(encoding='utf-8'))
rom=pathlib.Path(meta['path']).read_bytes()
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
catalog=meta['missionRecovery'];rules=catalog['rules'];symbols=meta['symbols']
u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
for address,size in ((0x02000000,0x40000),(0x03000000,0x8000),(0x04000000,0x1000),(0x08000000,0x2000000)):
    u.mem_map(address,size)
u.mem_write(0x08000000,rom)
STACK=0x03007000;RETURN=0x08000100;CACHE=0x020021c8;NODES=0x020025c8;HEAD=0x020028c8
stops=set();observations=[];counts=collections.Counter()
def preserve_progress():
    (ROOT/'build/reports/mission-recovery-progress.json').write_text(json.dumps(dict(romSha1=meta['romSha1'],counts=dict(counts),observations=observations),indent=2)+'\n',encoding='utf-8')
atexit.register(preserve_progress)
u.hook_add(UC_HOOK_CODE,lambda m,a,s,d:m.emu_stop() if a in stops else None)
regs=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
preserved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]

def call(name,*args,registers=None,stop=None,stack=STACK):
    stops.clear();stops.update(stop or [RETURN])
    for i,r in enumerate(preserved):u.reg_write(r,0x12340000+i*16)
    for r,v in zip(regs,args):u.reg_write(r,v)
    for r,v in (registers or {}).items():u.reg_write(r,v)
    u.reg_write(UC_ARM_REG_SP,stack);u.reg_write(UC_ARM_REG_LR,RETURN|1)
    address=symbols[name] if isinstance(name,str) else name
    u.emu_start(address|1,RETURN,count=2000000)
    pc=u.reg_read(UC_ARM_REG_PC)
    assert pc in stops,('escaped',name,hex(pc))
    if stop is None:
        assert u.reg_read(UC_ARM_REG_SP)==stack,('unbalanced stack',name)
        for i,r in enumerate(preserved):assert u.reg_read(r)==0x12340000+i*16,('callee-saved',name,r)
    return u.reg_read(UC_ARM_REG_R0)

def flag(ram,mission,done=True):
    bit=mission+0x2ff;at=0x1f70+(bit>>3);mask=1<<(bit&7)
    ram[at]=(ram[at]|mask) if done else (ram[at]&~mask)

def saved_flag(ram,mission):
    bit=mission+0x2ff
    return bool(ram[0x1f70+(bit>>3)]&(1<<(bit&7)))

def seed(rule,completed=(),held=0,bound=False):
    ram=bytearray(0x40000)
    for mission in completed:flag(ram,mission)
    # Include the last inventory slot; held copies can be bound to dispatch.
    for i in range(held):struct.pack_into('<BBH',ram,0x2b08+(63-i)*4,rule['item'],int(bound),288 if bound else 0)
    return ram

def note(kind,**data):
    counts[kind]+=1;observations.append(dict(case=kind,**data))

for rule in rules:
    ids=sorted({s['mission'] for s in rule['sources']}|{s['mission'] for s in rule['uses']})
    # Enumerate source/consumer combinations, including inconsistent imported
    # saves: no underflow, early source entitlement or duplicate bound supply.
    for bits in itertools.product((0,1),repeat=len(ids)):
        done={m for m,b in zip(ids,bits) if b}
        earned=sum(s['copies'] for s in rule['sources'] if s['mission'] in done)
        spent=sum(s['consumed'] for s in rule['uses'] if s['mission'] in done)
        required=max([s['required'] for s in rule['uses'] if s['mission'] not in done or s['repeatable']]+[0])
        for held,bound in itertools.product(range(4),(False,True)):
            ram=seed(rule,done,held,bound);u.mem_write(0x02000000,bytes(ram))
            want=int(held<min(max(earned-spent,0),required))
            result=call('ffta_recovery_needed',rule['mission'])
            assert result==want,(rule['mission'],done,held,bound,result,want)
            assert u.mem_read(0x02000000,0x40000)==ram,'Eligibility wrote saved memory'
            note('entitlement',mission=rule['mission'],completed=sorted(done),held=held,bound=bound,offer=result)
    # Complete native posting predicates and duration consumers for each route.
    for earned,held in ((False,0),(True,0),(True,1),(True,2)):
        done=[s['mission'] for s in rule['sources']] if earned else []
        ram=seed(rule,done,held);u.mem_write(0x02000000,bytes(ram))
        want=call('ffta_recovery_needed',rule['mission'])
        u.mem_write(STACK,struct.pack('<I',1))
        call(0x080cfd00,registers={UC_ARM_REG_R5:0x0855ae4c+70*rule['mission'],UC_ARM_REG_R6:rule['mission']},stop=[0x080cff40,0x080d056e])
        assert (u.reg_read(UC_ARM_REG_PC)==0x080cff40)==bool(want)
        assert u.reg_read(UC_ARM_REG_SP)==STACK
        note('native-posting',mission=rule['mission'],earned=earned,held=held,offer=want)
    for selector,want in ((1,0),(2,0),(4,1),(0x10,0),(0x11,1),(0x12,5),(0x1e,0),(0x36,200),(0x38,1)):
        result=call(0x080ce4dc,rule['mission'],selector)
        assert result==want,('mission-field',rule['mission'],hex(selector),result,want)
    assert rom[0x55ae4c+rule['mission']*70+0x41]==8
    note('native-fields',mission=rule['mission'])
    # The actual mission-description decoder, not a test-side text decoder.
    ram=seed(rule);struct.pack_into('<H',ram,0x20dc,rule['mission'])
    u.mem_write(0x02000000,bytes(ram));call(0x08013c20,0x80)
    body=bytes(u.mem_read(0x020078b0,512))
    encoded=[]
    for ch in rule['description']:
        if ch.isupper():encoded.extend((0x80,0xb0+ord(ch)-65))
        elif ch.islower():encoded.extend((0x80,0xca+ord(ch)-97))
        elif ch.isdigit():encoded.extend((0x80,0xa6+ord(ch)-48))
        else:encoded.extend({' ':(0x40,0x73),'\n':(0x40,0x6e),'.':(0x80,0xe4),"'":(0x80,0xf4),'-':(0x81,0x0b)}[ch])
    assert body.startswith(bytes(encoded)+bytes.fromhex('4077406300')),('native-description',rule['mission'],body[:32].hex())
    note('native-description',mission=rule['mission'])

# Original text entries remain byte-identical within the relocated second bank.
bank=catalog['descriptionBank'];installed=bank['installed'];old=bank['original']
new_indices={r['mission']-201 for r in catalog['records']}
for i in range(311):
    if i in new_indices:continue
    start=struct.unpack_from('<H',clean,old+i*2)[0]
    end=struct.unpack_from('<H',clean,old+(i+1)*2)[0] if i<310 else bank['originalEnd']-old
    assert rom[installed+start:installed+end]==clean[old+start:old+end]
    assert rom[installed+i*2:installed+i*2+2]==clean[old+i*2:old+i*2+2]
note('original-description-preservation',entries=311-len(new_indices))

# Recovery cannot evict original missions from a full64-record native cache.
# The last free slot remains usable; active and posted originals both count.
for rule in rules:
    for occupied in (63,64):
        ram=seed(rule,[s['mission'] for s in rule['sources']])
        for i in range(occupied):
            struct.pack_into('<H',ram,0x21c8+i*16,i+1)
            ram[0x21ca+i*16]=8 if i%2 else 0
        u.mem_write(0x02000000,bytes(ram));u.mem_write(STACK,struct.pack('<I',1))
        call(0x080cfd00,registers={UC_ARM_REG_R5:0x0855ae4c+70*rule['mission'],UC_ARM_REG_R6:rule['mission']},stop=[0x080cff40,0x080d056e])
        assert (u.reg_read(UC_ARM_REG_PC)==0x080cff40)==(occupied==63)
        assert u.mem_read(0x02000000,0x40000)==ram
        note('native-recovery-capacity',mission=rule['mission'],occupied=occupied,allowed=occupied==63)

# A mixed linked queue: prune every stale offer while preserving all native
# accepted/outcome/cooldown states and every ordinary entry, in either order.
rule=rules[0]
for reverse in (False,True):
    for state in (0,4,8,12,16,20,24,28):
        ram=seed(rule)
        order=list(range(64));order=order[::-1] if reverse else order
        keep=[]
        for pos,i in enumerate(order):
            mission=rules[i//2]['mission'] if i%2==0 else 138
            struct.pack_into('<H',ram,0x21c8+i*16,mission);ram[0x21ca+i*16]=state
            struct.pack_into('<III',ram,0x25c8+i*12,CACHE+i*16,NODES+order[pos-1]*12 if pos else 0,NODES+order[pos+1]*12 if pos<63 else 0)
            if state not in (4,8) or i%2:keep.append(i)
        struct.pack_into('<I',ram,0x28c8,NODES+order[0]*12)
        u.mem_write(0x02000000,bytes(ram));call('ffta_recovery_prune_offers')
        after=bytes(u.mem_read(0x02000000,0x40000))
        head=struct.unpack_from('<I',after,0x28c8)[0];seen=[];previous=0
        while head:
            assert NODES<=head<HEAD and (head-NODES)%12==0 and len(seen)<64
            index=(head-NODES)//12;seen.append(index)
            record,prev,nxt=struct.unpack_from('<III',after,head-0x02000000)
            assert record==CACHE+index*16 and prev==previous
            previous=head;head=nxt
        assert seen==keep,(reverse,state,seen,keep)
        for i in set(order)-set(keep):
            assert after[0x21c8+i*16:0x21d8+i*16]==bytes(16)
            assert struct.unpack_from('<I',after,0x25c8+i*12)[0]==0
        assert after[:0x21c8]==ram[:0x21c8] and after[0x28cc:]==ram[0x28cc:]
        note('linked-queue',reverse=reverse,state=state,retained=len(keep))

# Installed confirmation hook must reject before acceptance and its payment
# path. Probe both native stack alignments and preserve high registers.
for rule in rules:
    for wanted in (False,True):
        for alignment in (0,4):
            ram=seed(rule,[s['mission'] for s in rule['sources']] if wanted else [])
            struct.pack_into('<H',ram,0x21c8,rule['mission'])
            struct.pack_into('<I',ram,0x30000,0x02031000)
            struct.pack_into('<I',ram,0x32450,CACHE)
            ram[0x321a1]=0xa5
            u.mem_write(0x02000000,bytes(ram))
            call(0x0805ee20,registers={UC_ARM_REG_R5:0x02030000},stop=[0x08013364,0x0805ede8],stack=STACK-alignment)
            assert u.reg_read(UC_ARM_REG_PC)==(0x08013364 if wanted else 0x0805ede8)
            after=bytes(u.mem_read(0x02000000,0x40000))
            assert after==ram,('acceptance-side-effect',rule['mission'],wanted)
            assert u.reg_read(UC_ARM_REG_SP)==STACK-alignment
            note('native-acceptance-boundary',mission=rule['mission'],allowed=wanted,alignment=alignment)

# Execute the installed completion branch. Original success writes its native
# flag; recovery never borrows an unused story flag, even for repeated success.
for mission in [138,183,288,*[r['mission'] for r in rules]]:
    for outcome in (0,0xc8,0xc9,0xca):
        ram=bytearray(0x40000);u.mem_write(0x02000000,bytes(ram))
        call(0x080d0fb2,registers={UC_ARM_REG_R3:mission,UC_ARM_REG_R2:outcome},stop=[0x080d0fc4])
        after=bytes(u.mem_read(0x02000000,0x40000))
        if mission<407 and (outcome&0xfe)==0xc8:flag(ram,mission)
        assert after==ram,('completion-flag',mission,outcome)
        assert u.reg_read(UC_ARM_REG_SP)==STACK
        note('native-completion-branch',mission=mission,outcome=outcome,flag=saved_flag(after,mission))

# The actual cached-dispatch completion handler has a separate success writer.
# Any nonzero native success quality must preserve original mission completion.
for mission in [138,183,288,*[r['mission'] for r in rules]]:
    for quality in (0,1,5):
        ram=bytearray(0x40000);u.mem_write(0x02000000,bytes(ram))
        call(0x080d1e9c,registers={UC_ARM_REG_R3:mission,UC_ARM_REG_R10:quality},stop=[0x080d1eac])
        if mission<407 and quality:flag(ram,mission)
        assert u.mem_read(0x02000000,0x40000)==ram,('cached-completion-flag',mission,quality)
        note('native-cached-completion-branch',mission=mission,quality=quality)

report=dict(passed=True,romSha1=meta['romSha1'],cases=sum(counts.values()),counts=dict(counts),observations=observations,
    scope='Native entitlement, posting predicates, text decoding, linked pruning, acceptance and completion boundaries. Full dispatch, rendered UI and cold saves remain separate.')
out=ROOT/'build/reports/mission-recovery.json';out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='observations'},indent=2))
