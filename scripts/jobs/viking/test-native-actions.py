"""Fixed native executor differential for Reaving magic and original gil theft."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ast
import collections
import hashlib
import itertools
import json
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'tools/arm-python'), str(ROOT / 'scripts')]
from unicorn import *
from unicorn.arm_const import *
from native_battle_wrappers import from_memory

P = ROOT / 'build/expansion/probes'
meta = _load_job_candidate(P / 'viking/current.json')
rom = pathlib.Path(meta['path']).read_bytes()
assert hashlib.sha1(rom).hexdigest() == meta['romSha1']
parent = json.loads((P / 'job-state/current.json').read_text())
fix = pathlib.Path(meta['path']).parent / 'executor'
ram = (fix / 'execute-trap.ram').read_bytes()
iw = (fix / 'execute-trap.iwram').read_bytes()
regs = struct.unpack_from('<17I', (fix / 'execute-trap.state').read_bytes(), 0x20)
UNIT, TARGET, EQUIPMENT, RETURN, STACK = 0x02000080, 0x020033e4, 0x02002000, 0x08000100, 0x03007000
tree = ast.parse((ROOT / 'scripts/test-equipment-legality.py').read_text().replace('count=50000', 'count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ARM'], type_ignores=[]), '<native ARM>', 'exec'))
wrappers = {0x02000000 + u: 0x02000000 + w for u, w in from_memory(rom, ram, iw).items()}
WRAPPER = wrappers[UNIT]
control = bytearray((pathlib.Path(meta['path']).parent / 'input.gba').read_bytes())
table = struct.unpack_from('<I', control, 0xccd84)[0] - 0x08000000
# Independently specified approved native controls: ordinary Thunder at power24,
# single target; ordinary Thundaga at power40/cross/range3/20MP; original Gil.
for donor, power, mp, radius, area in [(26, 24, 6, 4, 0), (28, 40, 20, 3, 2)]:
    q = table + donor * 28
    control[q + 4] = mp
    control[q + 6] = radius
    control[q + 9] = 1 if area == 0 else 5
    control[q + 10] = area
    control[q + 11] = power
    flags = struct.unpack_from('<I', control, q + 16)[0]
    struct.pack_into('<I', control, q + 16, flags & ~(1 << 8))
native, expanded = ARM(control, iw), ARM(rom, iw)
counts = collections.Counter()
samples = []

def check(group, actual, expected):
    counts[group] += 1
    if actual!=expected and isinstance(actual,bytes) and isinstance(expected,bytes):
        differences=[(i,a,b) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b]
        raise AssertionError((group,len(differences),differences[:20]))
    assert actual == expected, (group, actual, expected)

def setup(m, action, seed, status, weapon=400):
    m.put(0x02000000, ram)
    m.put(0x03000000, iw)
    actor = bytearray(ram[0x80:0x80 + 264])
    target = bytearray(ram[0x33e4:0x33e4 + 264])
    actor[5] = actor[7] = actor[0x35] = 118
    actor[6] = 2
    actor[0x3a] = actor[0x3b] = 0
    actor[0xe8:0xf0] = bytes(8)
    target[0xe8:0xf0] = bytes(8)
    if status >= 0:
        target[0xe8 + status // 8] = 1 << (status % 8)
    struct.pack_into('<HHHH', actor, 0x18, 100, 100, 50, 50)
    struct.pack_into('<HHHH', target, 0x18, 250, 250, 49, 49)
    struct.pack_into('<5H', actor, 0x2a, weapon, 0, 0, 0, 0)
    actor[0xf6:0xf8] = bytes([4, 14])
    m.put(UNIT, actor)
    m.put(TARGET, target)
    m.put(WRAPPER, struct.pack('<I', UNIT))
    m.put(WRAPPER + 8, struct.pack('<H', 4 << 5))
    m.put(WRAPPER + 12, struct.pack('<H', 14 << 5))
    m.put(0x02001e98, bytes(108))
    m.put(0x0203ff44, bytes(8))
    m.put(0x030034b0, struct.pack('<I', seed))
    m.put(regs[13], struct.pack('<4I', action, 0, 0, 255))

def run(m):
    m.call(0x080a433c, regs[0], WRAPPER, 5, 14, stack=regs[13])
    return m.read(0x02000000, 0x40000), m.read(0x030034b0, 4)

for action, donor in [(365, 26), (366, 168), (371, 28)]:
    for seed, status, weapon in itertools.product(range(8), [-1, 6, 9, 12, 21, 24, 25], [0, 400]):
        setup(native, donor, seed, status, weapon)
        nr, rng = run(native)
        setup(expanded, action, seed, status, weapon)
        er, actual_rng = run(expanded)
        check('native-party-enemy-inventory-and-AP', er[:0x3c24], nr[:0x3c24])
        check('native-rng-consumption', actual_rng, rng)
        check('transient-scope-retired', er[0x3ff44:0x3ff4c], bytes(8))
        samples.append(dict(action=action, donor=donor, seed=seed, status=status,
                            weapon=weapon, hp=struct.unpack_from('<H', er, 0x33fc)[0],
                            actorMP=struct.unpack_from('<H', er, 0x9c)[0]))

report = dict(passed=True, romSha1=meta['romSha1'], checks=dict(counts), samples=samples,
              scope=__doc__, gaps=['actual menu/law/save tests and remaining Viking lessons'])
(pathlib.Path(meta['path']).parent / 'native-actions.json').write_text(json.dumps(report, indent=2))
print(json.dumps({k: v for k, v in report.items() if k != 'samples'}, indent=2))
