"""Static ROM-delta audit against the retained pre-recovery candidate.

The linker may reorder ARM/Thumb interworking veneers when adding an isolated
section. Resolve both versions to their final destination rather than treating
changed call displacements as changed combat behavior. No game is executed.
"""
import collections
import hashlib
import json
import pathlib
import struct

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASELINE = '5a01c78e45a32768a7568617a931c50a7b5300f3'
meta = json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text(encoding='utf-8'))
current = pathlib.Path(meta['path']).read_bytes()
prior = (pathlib.Path(meta['path']).parent.parent/BASELINE/'integrated.gba').read_bytes()
assert hashlib.sha1(prior).hexdigest() == BASELINE
assert hashlib.sha1(current).hexdigest() == meta['romSha1']
assert len(prior) == len(current)
allowed = [(0x1340000, 0x1360000), (0xcfd00, 0xcfd0c), (0xd0590, 0xd059c),
           (0x5ee20, 0x5ee2c), (0xd0fb2, 0xd0fc4), (0xd1e9c, 0xd1eac), (0x13cc0, 0x13cc4),
           (0x55a64c+407*4, 0x55a64c+477*4), (0x55ae4c+407*70, 0x55ae4c+477*70)]
VSTART, VEND = 0x11e7cf0, 0x11e7d40

def signed(value, bits):
    return value-(1 << bits) if value & (1 << (bits-1)) else value

def veneers(data):
    found = {}
    at = VSTART
    while at < VEND:
        a, b = struct.unpack_from('<II', data, at)
        if a == 0xe7fd4778:  # Thumb bx pc; padding; ARM b destination
            assert b >> 24 == 0xea
            found[at] = (at+12+signed(b & 0xffffff, 24)*4, 0)
            at += 8
        elif a == 0xe59fc000 and b == 0xe12fff1c:  # ARM ldr ip; bx ip
            target = struct.unpack_from('<I', data, at+8)[0]
            found[at] = ((target & ~1)-0x08000000, target & 1)
            at += 12
        else:
            assert not any(data[at:VEND]), ('Unexpected veneer bytes', hex(at))
            break
    return found

old_veneers, new_veneers = veneers(prior), veneers(current)
assert collections.Counter(old_veneers.values()) == collections.Counter(new_veneers.values())
accounted = set(range(VSTART, VEND))
calls = []
for at in range(0x11e0000, VSTART, 2):
    a, b = struct.unpack_from('<HH', prior, at)
    c, d = struct.unpack_from('<HH', current, at)
    if a & 0xf800 == c & 0xf800 == 0xf000 and b & 0xf800 == d & 0xf800 == 0xf800:
        old = at+4+(signed(a & 0x7ff, 11) << 12)+((b & 0x7ff) << 1)
        new = at+4+(signed(c & 0x7ff, 11) << 12)+((d & 0x7ff) << 1)
        if (a, b) != (c, d):
            assert old in old_veneers and new in new_veneers and old_veneers[old] == new_veneers[new]
            accounted.update(range(at, at+4)); calls.append(at)
    if at % 4 == 0:
        old_word, new_word = a | (b << 16), c | (d << 16)
        if old_word >> 24 == new_word >> 24 and old_word >> 24 in (0xea, 0xeb) and old_word != new_word:
            old = at+8+signed(old_word & 0xffffff, 24)*4
            new = at+8+signed(new_word & 0xffffff, 24)*4
            assert old in old_veneers and new in new_veneers and old_veneers[old] == new_veneers[new]
            accounted.update(range(at, at+4)); calls.append(at)
changes = [i for i, (a, b) in enumerate(zip(prior, current)) if a != b]
unexpected = [i for i in changes if i not in accounted and not any(a <= i < b for a, b in allowed)]
assert not unexpected, [hex(i) for i in unexpected[:32]]
report = dict(passed=True, baselineSha1=BASELINE, romSha1=meta['romSha1'],
              changedBytes=len(changes), preservedCallDestinations=len(calls),
              veneers=len(old_veneers), scope='Only recovery content/hooks and equivalent linker veneer relocation; no runtime certification.')
(ROOT/'build/reports/recovery-rom-delta.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
print(json.dumps(report, indent=2))
