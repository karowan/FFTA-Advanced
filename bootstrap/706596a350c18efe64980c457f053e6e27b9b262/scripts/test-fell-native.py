"""Deterministic Fell/Exposed native composition, remedies and ownership checks."""
import ast, collections, hashlib, json, pathlib, struct, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT, EQUIPMENT, RETURN, STACK = 0x02000080, 0x02002000, 0x08000100, 0x03007000
ACTOR, TARGET, CTX = 0x02000398, 0x020033e4, 0x0200f3f0
AS, TS = 0x02001e9b, 0x02001eb4
from fell_test_context import load_context
meta = load_context('--current' in sys.argv)
ROM = pathlib.Path(meta['path']); OUT = ROM.parent; FIX = OUT/'fixture'
image, base = ROM.read_bytes(), (OUT/'base.gba').read_bytes()
sha = lambda b: hashlib.sha1(b).hexdigest()
assert sha(image) == meta['romSha1'] and sha(base) == meta['baseSha1']
assert sha((FIX/'frozen.gba').read_bytes()) == sha(image)
ram, iw = (FIX/'battle-ready.ram').read_bytes(), (FIX/'battle-ready.iwram').read_bytes()
symbols = meta['symbols']; counts = collections.Counter()
tree = ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ARM'], type_ignores=[]), '<ARM>', 'exec'))
native, expanded = ARM(base, iw), ARM(image, iw)
def check(group, got, want):
    assert got == want, (group, got, want)
    counts[group] += 1
def signed(n): return n-(1<<32) if n & (1<<31) else n
def reset(m): m.put(0x02000000, ram)

# Independent rational specification, signed truncation and one final rounding.
# Exposed belongs to the evaluated recipient; the actor's packed byte differs.
factors = {357:(95,100), 358:(75,100), 424:(11,10), 425:(9,10),
           426:(9,10), 427:(1,1), 428:(1,1), 429:(11,10), 431:(18,10)}
for stack in (STACK, STACK+4):
    for hp in (125,126):
        for packed in (0,1,0x0a,0x0b,0xfe,0xff):
            reset(expanded); expanded.put(TARGET+0x18, struct.pack('<HH', hp,250))
            expanded.put(ACTOR+0x2a, struct.pack('<5H',460,0,0,0,0))
            expanded.put(AS,bytes([packed^1])); expanded.put(TS,bytes([packed]))
            before=expanded.read(0x02000000,0x40000)
            for action in [0,112,*factors,430]:
                n,d = (18 if hp==125 else 11,10) if action==430 else factors.get(action,(1,1))
                for reference in (-2147483648,-999,-37,-1,0,1,2,7,13,37,999,2147483647):
                    incoming=6 if packed&1 and reference>0 and action in [*factors,430] else 5
                    want=min(0x7fffffff,abs(reference)*n*incoming//(d*5))
                    if reference<0: want=-want
                    if action not in [*factors,430]: want=reference
                    got=signed(expanded.call(symbols['ffta_physical_final'],reference&0xffffffff,action,ACTOR,TARGET,stack=stack))
                    check('single_round_signed_coefficient',got,want)
            check('coefficient_no_state_writes',expanded.read(0x02000000,0x40000),before)

# All packed values: commit preserves other bits and native Immunity prevents
# application. Establish the actual support with the native racial getter.
for stack in (STACK,STACK+4):
    for support in (0,115):
        for packed in range(256):
            reset(expanded); expanded.put(UNIT+0x3b,bytes([support])); expanded.put(0x02001e98,bytes([packed]))
            check('native_immunity_assignment',expanded.call(0x080cd50c,UNIT),11 if support else 0)
            before=expanded.read(0x02000000,0x40000)
            check('can_apply',expanded.call(symbols['ffta_exposed_can_apply'],UNIT,stack=stack),0 if support else 1)
            check('eligibility_read_only',expanded.read(0x02000000,0x40000),before)
            check('paid_commit',expanded.call(symbols['ffta_exposed_paid_commit'],UNIT,431,stack=stack),0 if support else 1)
            want=bytearray(before)
            if not support: want[0x1e98]=packed|1
            check('packed_commit_isolation',expanded.read(0x02000000,0x40000),want)

# Full native broad-remedy dispatcher, using its original cures as the oracle.
# Enumerate every original action with either callback, not only Esuna/Cureall.
table=struct.unpack_from('<I',base,0xccd84)[0]-0x08000000
remedies=[]
for action in range(347):
    for slot,stage in enumerate(base[table+action*28+12:table+action*28+15]):
        effect=base[0x553e70+stage*4+1]
        if effect in (11,79): remedies.append((action,slot,stage,effect))
check('broad_remedy_actions',sorted({a for a,_,_,_ in remedies}),[4,68,76,87,104,138,264,270])
admitted=collections.Counter()
for stack in (STACK,STACK+4):
    for action,slot,stage,effect in remedies:
        for status in range(-1,44):
            for query in (0,0x10):
                for m in (native,expanded):
                    reset(m);m.put(0x02001e98,bytes([0xab])*36)
                    m.put(UNIT+0xe8,struct.pack('<Q',0 if status<0 else 1<<status))
                    context=bytearray(0x34)
                    struct.pack_into('<IIIHH',context,0,ACTOR,UNIT,UNIT,action,0)
                    struct.pack_into('<H',context,0x26,query);context[0x28]=slot
                    struct.pack_into('<I',context,0x30,0x08553e70+stage*4);m.put(CTX,context)
                allowed=native.call(0x08133a58,UNIT,effect)
                results=[m.call(0x0813388c,stack=stack) for m in (native,expanded)]
                want=bytearray(native.read(0x02000000,0x40000))
                if allowed and not query:
                    want[0x1e98]&=~1
                    if status<0: admitted[action]+=1
                check('remedy_original_return',results[1],results[0])
                check('remedy_full_memory_and_centered',expanded.read(0x02000000,0x40000),want)
for action in sorted({a for a,_,_,_ in remedies}):check('exposed_only_admitted',admitted[action],2)

# Explicit custom ownership: copied foreign bytes must not grant Exposed.
for stack in (STACK,STACK+4):
    reset(expanded); expanded.put(0x03007600,expanded.read(UNIT,264))
    before=expanded.read(0x02000000,0x40000)
    check('foreign_copy_rejected',expanded.call(symbols['ffta_exposed_can_apply'],0x03007600,stack=stack),0)
    check('foreign_commit_rejected',expanded.call(symbols['ffta_exposed_paid_commit'],0x03007600,431,stack=stack),0)
    check('foreign_no_persistent_writes',expanded.read(0x02000000,0x40000),before)

# Full native cleanup/status/job paths with both owned effects present. Native
# byte changes remain the oracle; KO/Petrify/job changes additionally clear the
# low nibble, while every other unit and reserved upper nibble stay intact.
units=[0x02000080+264*i for i in range(24)]+[0x02002fc4+264*i for i in range(12)]
for stack in (STACK,STACK+4):
    for index,unit in enumerate(units):
        cases=[(0x08097298,(unit,),True)]
        cases += [(0x080cd884,(unit,status,value),status==6 and value) for status in range(44) for value in (0,1)]
        for fn,arguments,clears in cases:
            results=[]
            for m in (native,expanded):
                reset(m);m.put(0x02001e98,bytes([0xab])*36)
                results.append(m.call(fn,*arguments,stack=stack))
            want=bytearray(native.read(0x02000000,0x40000))
            if clears:want[0x1e98+index]=0xa0
            check('native_lifecycle_return',results[1],results[0])
            check('native_lifecycle_ownership',expanded.read(0x02000000,0x40000),want)
    for unit,index in ((UNIT,0),(ACTOR,3)):
        for job in (ram[unit-0x02000000+7],2,3,10,116):
            results=[]
            for m in (native,expanded):
                reset(m);m.put(0x02001e98,bytes([0xab])*36)
                results.append(m.call(0x080c8c24,unit,job,stack=stack))
            want=bytearray(native.read(0x02000000,0x40000))
            if job!=ram[unit-0x02000000+7]:want[0x1e98+index]=0xa0
            check('native_job_change_return',results[1],results[0])
            check('native_job_change_ownership',expanded.read(0x02000000,0x40000),want)
report=dict(passed=True,romSha1=sha(image),baseSha1=sha(base),checks=sum(counts.values()),groups=dict(counts),remedies=remedies,
            scope='Private compiled Fell/Exposed: exact rational finalization, all packed commits/Immunity, eight native broad-remedy actions across all44 status bits, query isolation, independent ownership. Actual battle/payment are separate.')
(OUT/'native-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
