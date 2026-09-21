"""Native Shara dispatch return and arrival selection with declared campaign inputs.

Original game completion, calendar, map placements and ordinary roster are inputs.
Dispatch outcome is controlled; all completion flags, queue transitions and
arrival selection are native outputs. No rendered cutscene or campaign claim.
"""
import ast
import atexit
import datetime
import hashlib
import json
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
meta = json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
rom = pathlib.Path(meta['path']).read_bytes()
sha = lambda b: hashlib.sha1(b).hexdigest()
assert sha(rom) == meta['romSha1']
base = pathlib.Path(meta['path']).parent
FIX = base/'fixture-two-geomancers'
proof = json.loads((FIX/'prepare-cache.json').read_text())
assert proof['inputs']['romSha1'] == meta['romSha1']
ram, iw = [(FIX/name).read_bytes() for name in ('battle-ready.ram', 'battle-ready.iwram')]
for name, value in (('battle-ready.ram', ram), ('battle-ready.iwram', iw)):
    assert sha(value) == proof['outputs'][name]
records = json.loads((ROOT/'build/reports/mission-item-dependencies.json').read_text())
assert records['candidateSha1'] == meta['romSha1']
records = records['installedRecords']
RETURN, STACK = 0x08000100, 0x03006800
tree = ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000', 'count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ARM'], type_ignores=[]), '<native ARM>', 'exec'))
m = ARM(rom, iw)
OUT = base/('shara-arrival-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
OUT.mkdir()
BUFFER, VIEW = 0x02030000, 0x02010000
checks, cases = [], []
retained = {}


def check(ok, label):
    assert ok, label
    checks.append(label)


def report(passed=False):
    if not passed:
        (OUT/'failure.ram').write_bytes(m.read(0x02000000, 0x40000))
    (OUT/'report.json').write_text(json.dumps(dict(passed=passed, romSha1=meta['romSha1'],
        assertions=len(checks), checks=checks, cases=cases, scope=__doc__,
        fixture=proof['outputs'], retained=retained), indent=2)+'\n')


atexit.register(report)
put32 = lambda p, v: m.put(p, struct.pack('<I', v))


def set_flag(index):
    p = 0x02001f70+(index >> 3)
    m.put(p, bytes((m.read(p, 1)[0] | (1 << (index & 7)),)))


def flag(index):
    return bool(m.read(0x02001f70+(index >> 3), 1)[0] & (1 << (index & 7)))


def reset():
    m.put(0x02000000, bytes(0x40000))
    m.put(0x02000080, ram[0x80:0x1940])
    m.put(0x03000000, iw)
    put32(0x03002810, VIEW)
    put32(VIEW, 0x02002c10)
    put32(VIEW+4, 0x02002c10)
    for location in range(1, 31):
        m.put(0x02002cc3+(location-1)*12, bytes((location,)))
    m.put(0x02002e58, b'\x03')
    m.put(0x02002fba, b'\x04')  # Original Shara dispatch month.
    set_flag(54)
    put32(0x030034b0, 0)


def queue():
    node, previous, result = m.word(0x020028c8), 0, {}
    while node:
        assert 0x020025c8 <= node < 0x020028c8 and (node-0x020025c8) % 12 == 0 and len(result) < 64
        ptr, prev, nxt = struct.unpack('<III', m.read(node, 12))
        assert prev == previous and 0x020021c8 <= ptr < 0x020025c8 and (ptr-0x020021c8) % 16 == 0
        mission = int.from_bytes(m.read(ptr, 2), 'little') & 1023
        assert mission and mission not in result
        result[mission] = ptr
        previous, node = node, nxt
    return result


def pub(ptr):
    towns = []
    for town in range(8):
        m.put(BUFFER+256, b'\xa5'*4)
        count = m.call(0x080d0590, BUFFER, 64, town)
        check(count <= 64 and m.read(BUFFER+256, 4) == b'\xa5'*4, f'Pub buffer bound:{town}')
        if ptr in struct.unpack('<64I', m.read(BUFFER, 256))[:count]:
            towns.append(town)
    return towns


UNIT = 0x02000080+264
for success in (() if '--arrival-only' in sys.argv else (False, True)):
    reset()
    m.call(0x080cfcd0, 0)
    entries = queue()
    check(381 in entries and 400 not in entries, f'Dispatch precedes hidden arrival:{success}')
    ptr = entries[381]
    check(bool(pub(ptr)), f'Original dispatch visible:{success}')
    m.call(0x080d0b48, ptr, UNIT, 0, 0)
    accepted = m.read(ptr, 16)
    days = (accepted[1] >> 2) | ((accepted[2] & 3) << 6)
    check(days == 10 and accepted[2] & 0x1c == 0, f'Native ten-day assignment:{success}')
    for day in range(1, days+1):
        m.put(BUFFER, bytes(256))
        count = m.call(0x080d1c94, BUFFER, 64, 1)
        returned = struct.unpack('<64I', m.read(BUFFER, 256))[:count]
        check((ptr in returned) == (day == days), f'Original countdown:{success}/{day}')
    m.call(0x080d1e70, ptr, int(success))
    check(flag(1148) == success and not flag(603), f'Completion unlock only after success:{success}')
    check(int.from_bytes(m.read(UNIT+0x16, 2), 'little') == 0, f'Dispatched member returned:{success}')
    cooldown = m.read(ptr+3, 1)[0]
    for day in range(cooldown):
        m.call(0x080cf51c)
    m.call(0x080cfcd0, 0)
    entries = queue()
    check((381 in entries) != success and (400 in entries) == success, f'Failure retries dispatch, success enables arrival:{success}')
    row = dict(success=success, days=days, cooldown=cooldown, missions=list(entries))
    if success:
        hidden = entries[400]
        check(not pub(hidden) and m.read(hidden+2, 1)[0] & 0x1c == 0, 'Arrival is automatic, not a pub offer')
        (OUT/'arrival-ready.ram').write_bytes(m.read(0x02000000, 0x40000))
        cases.append(row)
    else:
        check(bool(pub(entries[381])), 'Failed dispatch offers another original attempt')
        cases.append(row)
# Targeted continuation keeps the completed dispatch cases from the failed
# initial run. Full reproduction above creates the same native arrival state.
if '--arrival-only' in sys.argv:
    previous = base/'shara-arrival-20260917T041342.878958Z'
    input_bytes = (previous/'failure.ram').read_bytes()
    check(sha(input_bytes) == 'aff7444a6251d468576b4455dfffb8723daaf5ca', 'Retained native dispatch output SHA1')
    prior = (previous/'report.json').read_bytes()
    check(hashlib.sha256(prior).hexdigest() == '0ff83bdb34d2150cdb0ad5317735fed14a03eae54daf319f5a33103e354b12f5', 'Retained failed report SHA256')
    retained.update(report=str(previous/'report.json'), ramSha1=sha(input_bytes),
                    completedDispatchCases=json.loads(prior)['cases'])
    m.put(0x02000000, input_bytes)
    m.put(0x03000000, iw)
arrival = m.read(0x02000000, 0x40000)
# Native scene group31 (event217) invokes the postgame town condition program.
# Current position1 maps to original town location1 in our declared placements.
# A prior unaccepted exit sets621; script129 clears it before offering400 again.
for previous_exit in (False, True):
    m.put(0x02000000, arrival)
    m.put(0x03000000, iw)
    m.put(0x02001f69, b'\x01')
    if previous_exit:
        check(rom[0x9ba9a5:0x9ba9a9] == bytes.fromhex('1a 6d 02 01'), 'Original temporary-exit instruction')
        m.call(0x08122e90, 0, 0x089ba9a5)
        check(flag(621) and not flag(603), 'Unaccepted exit is not acceptance')
    m.call(0x08009c18, 0x08563a70+12*217, 30)
    result = m.call(0x080d17c4, 1, 1, BUFFER)
    count = m.read(0x0200219c, 1)[0]
    pending = list(struct.unpack('<4H', m.read(0x02002194, 8)))
    row = dict(previousUnacceptedExit=previous_exit, worldSelection=result,
               worldType=m.read(BUFFER, 1)[0], pendingCount=count, pendingScripts=pending)
    cases.append(row)
    check(result == 400 and row['worldType'] == 1, f'Native town arrival chooses Shara400:{previous_exit}')
    check(129 in pending, f'Native conditions enqueue Shara scene129:{previous_exit}')
    check(rom[0x9ba688:0x9ba68c] == bytes.fromhex('1a 6d 02 00'), 'Original arrival clears temporary gate')
    m.call(0x08122e90, 0, 0x089ba688)
    check(not flag(621) and not flag(603), f'Arrival clears temporary gate only:{previous_exit}')
    # Decode the actual scene129 recruit instruction through its native opcode
    # handler, then follow its continuation through D241C. Stop before UI launch.
    ctx = 0x02031000
    m.put(ctx, bytes(32))
    check(rom[0x9ba91d:0x9ba91f] == bytes.fromhex('36 0c'), 'Original scene129 requests Shara recruitment')
    check(m.call(0x08123294, ctx, 0x089ba91d) == 0x11c and
          m.read(ctx+4, 3) == bytes.fromhex('0c 00 07'), 'Original opcode schedules type12 offer continuation')
    m.u.reg_write(UC_ARM_REG_R5, ctx)
    m.u.reg_write(UC_ARM_REG_SP, STACK)
    m.u.emu_start(0x081222c9, 0x0812232c, count=3000000)
    check(m.u.reg_read(UC_ARM_REG_PC) == 0x0812232c and m.u.reg_read(UC_ARM_REG_SP) == STACK, 'Native recruit bridge reaches UI boundary')
    check(m.read(0x02003b20, 1) == b'\x0c', f'Actual Shara candidate produced:{previous_exit}')
    check(not flag(603), 'Generating candidate does not accept her')
report(True)
atexit.unregister(report)
print(json.dumps(dict(passed=True, assertions=len(checks), cases=cases, report=str(OUT/'report.json'))))
