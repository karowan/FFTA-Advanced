"""Native setter hooks: palette ownership, unsupported targets and fourth args."""
import ast, datetime, hashlib, json, struct, sys
from pathlib import Path
from native_art import ROOT, sha
sys.path.insert(0, str(ROOT / 'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
UNIT, EQUIPMENT, RETURN, STACK = 0x02000080, 0x02002000, 0x08000100, 0x03007000
tree = ast.parse((ROOT / 'scripts/test-equipment-legality.py').read_text().replace('count=50000', 'count=500000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ARM'], type_ignores=[]), '<native ARM>', 'exec'))
meta = json.loads((ROOT / 'build/art/live-palette/poc.json').read_text())
rom = Path(meta['path']).read_bytes()
assert hashlib.sha1(rom).hexdigest() == meta['romSha1']
source = ROOT / 'build/art/live-palette/battle/20260918T075021.733381Z'
assert sha((source/'failed.json').read_bytes())=='35b26fea1f86929b3d0a98ac34d28badf4be82631aa165ac30b97664a201bc76'
# This report failed phase equality, not state identity. Reuse its authenticated
# idle binding input; do not relabel the retained battle as passed.
ram = (source / 'candidate-ready.ram').read_bytes()
iw = (source / 'candidate-ready.iwram').read_bytes()
assert sha(ram) == 'a7fa401e99806ad8b6c9be5004b98aaaa716194fc71e121f661fd2bfceaa4dad'
assert sha(iw) == 'd7250d07c74b2ece6ea6ba4151a82b28d8b2657f720920e21683aa5812570280'
BASE, LIMIT = meta['ramReservation']
BIND = BASE + meta['bindingOffset']
ENTRY = BIND + meta['bindingEntryBytes']
COUNTERS = BIND + 2840
TEMP = 0x02008000
out = ROOT / 'build/art/palette-binding' / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True)
checks, cases = [], []


def check(ok, label):
    assert ok, label
    checks.append(label)


def machine():
    a = ARM(rom, iw)
    a.put(0x02000000, ram)
    return a


def state(a):
    return dict(task=a.word(ENTRY + 244), bank=a.word(ENTRY + 248),
                colors=a.read(ENTRY, 32).hex(), target=a.read(ENTRY + 32, 32).hex(),
                counters=list(struct.unpack('<3I', a.read(COUNTERS, 12))))


try:
    a = machine()
    original = state(a)
    native_baseline = a.read(ENTRY + 212, 32)
    check(original['bank'] == 0 and original['task'] == 0 and original['counters'] == [0, 0, 0], 'Authenticated active Dark Knight bank before scenarios')
    for first, count in ((0, 16), (272, 16), (496, 16)):
        a = machine()
        before = a.read(BIND, 2852)
        task = a.call(0x08147a7d, first, count, 8)
        check(0x03003c68 <= task < 0x03003e68, str(first) + ' original native unowned-range task allocated')
        check(a.read(BIND, 2852) == before, str(first) + ' unowned native range changes no generated binding or color')
        cases.append(dict(name='unowned', first=first, task=task))
    for first, count in ((257, 15), (256, 15), (255, 16)):
        a = machine()
        a.call(0x08147a7d, first, count, 8)
        result = state(a)
        check(result['task'] == 0 and result['counters'] == [0, 0, 1] and result['colors'] == original['colors'], str((first, count)) + ' partial bank fade is explicit unsupported and does not corrupt custom colors')
        cases.append(dict(name='partial', first=first, count=count, result=result))
    for name, values, supported in [('original', bytes.fromhex(original['colors']), False),
                                     ('native baseline', native_baseline, True),
                                     ('uniform color', struct.pack('<16H', *([0x3def] * 16)), True)]:
        a = machine()
        a.put(TEMP, values)
        task = a.call(0x08147d2d, 256, 16, 8, TEMP)
        result = state(a)
        native_targets = b''.join(a.read(0x03003e68 + (256 + i) * 12, 2) for i in range(16))
        check(native_targets == values, name + ' fourth-argument table pointer preserved through hook and trampoline')
        check(result['task'] == (task if supported else 0), name + ' binding support matches authenticated target kind')
        check(result['counters'] == ([1, 0, 0] if supported else [0, 0, 1]), name + ' explicit acceptance/refusal counters')
        if supported:
            expected = bytes.fromhex(original['colors']) if name == 'native baseline' else values
            check(a.read(ENTRY + 32, 32) == expected, name + ' exact generated target')
        cases.append(dict(name=name, result=result))
    # Central setup interception also covers native effects whose target
    # operation is not yet implemented. It must retire a preceding binding.
    a = machine()
    oldtask = a.call(0x08147a7d, 256, 16, 17)
    a.call(0x08148741, oldtask)
    partial = a.read(ENTRY, 32)
    a.call(0x08146e55, 256, 271, 8, 0)  # Unrecognized direct native setup.
    result = state(a)
    check(result['task'] == 0 and result['counters'] == [1, 0, 1], 'Unrecognized overlapping target retires old custom task and reports unsupported')
    check(a.read(ENTRY, 32) == partial, 'Unsupported target does not invent a replacement custom palette')
    cases.append(dict(name='unrecognized direct native setup', result=result))
    for flags in (0, 16, 32, 0x780):
        a = machine()
        task = a.call(0x08146e55, 256, 271, 8, flags)
        check(struct.unpack('<H', a.read(task + 2, 2))[0] == flags, str(flags) + ' fourth-argument native flags preserved')
        check(state(a)['counters'] == [0, 0, 1], str(flags) + ' direct unknown setup explicitly unsupported')
    # The native setup hook invalidates by returned task address even if a
    # recycled object now belongs to another palette range. Exercise that
    # sidecar registration case without changing an actual native task record.
    a = machine()
    task = a.call(0x08147a7d, 272, 16, 8)
    a.put(ENTRY + 244, struct.pack('<I', task))
    before = a.read(ENTRY, 244)
    a.put(STACK, struct.pack('<I', 1))  # Fifth AAPCS argument: recognized.
    a.call(meta['symbols']['ffta_art_binding_invalidate'], BIND, 272, 287, task)
    check(a.word(ENTRY + 244) == 0 and a.read(ENTRY, 244) == before, 'Recycled task identity is retired even outside the original palette range')
    report = dict(status='passed', checks=checks, cases=cases, romSha1=meta['romSha1'],
                  retainedReport=str(source / 'failed.json'), retainedRamSha256=sha(ram), retainedIWRAMSha256=sha(iw),
                  scope='Actual native setters on authenticated retained idle battle binding input: unowned/partial/unknown target behavior, supported baseline/uniform targets, fourth-argument preservation and task-address invalidation. No multi-variant or complete battle acceptance.')
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status='passed', checks=len(checks), report=str(out / 'report.json'))))
except Exception as error:
    (out / 'failed.json').write_text(json.dumps(dict(status='failed', error=str(error), checks=checks, cases=cases, romSha1=meta['romSha1']), indent=2) + '\n')
    print(str(out))
    raise
