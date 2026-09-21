"""Resume the accepted clear-save dialog through native reset and Continue.

The retained producer started the ending-save task in a synthetic story scene.
This suffix verifies its real reset-to-title path, unchanged flash, Continue,
and postgame mission consumers of that loaded flag. It does not establish the
final battle, credits or natural campaign arrival at the ending-save opcode.
"""
import ast
import ctypes as C
import datetime
import hashlib
import json
import pathlib
import runpy
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *

sha = lambda b: hashlib.sha1(b).hexdigest()
meta = json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
ROM = pathlib.Path(meta['path']); image = ROM.read_bytes()
assert sha(image) == meta['romSha1']
clean = (ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
assert sha(clean) == '4ac05441f4de70a4ec3dd932116346c61b8783d9'
source = ROM.parent/'clear-save-20260917T091908.745148Z'
prior_bytes = (source/'report.json').read_bytes()
assert sha(prior_bytes) == 'caeea467c2af4b202ece2a4716335720c5129e23'
prior = json.loads(prior_bytes)
assert prior['passed'] and prior['romSha1'] == meta['romSha1']
checkpoint = next(c for c in prior['captures'] if c['label'] == 'clear-dialog-dismissed')
assert sha((source/'clear-dialog-dismissed.state').read_bytes()) == checkpoint['stateSha1']
assert sha((source/'clear-dialog-dismissed.ram').read_bytes()) == checkpoint['ramSha1']
cleared = (source/'cleared.sav').read_bytes()
assert sha(cleared) == checkpoint['sramSha1'] == '7171fd22d6e76a094375d12eca8c45441b6881c4'
instrumented = (source/'fixture.gba').read_bytes()
assert sha(instrumented) == prior['instrumentedSha1']
# Authenticate the producer's exact instrumentation and native return code.
assert all(a == b or 0xc9540 <= i < 0xc9548 or 0x12c52c <= i < 0x12c530 or i >= 0x1fff000
           for i, (a, b) in enumerate(zip(image, instrumented)))
NATIVE_RANGES = [(0x231c0, 0x231d8), (0x1224b8, 0x122598), (0x12c2b8, 0x12c4e4)]
assert all(image[a:b] == clean[a:b] for a,b in NATIVE_RANGES)
OUT = ROM.parent/('clear-continuation-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
OUT.mkdir()
E = runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
tree = ast.parse((ROOT/'scripts/test-independent-save-slots.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'owned'],
                       type_ignores=[]), '<owned profile>', 'exec'))
RETURN, STACK = 0x08000100, 0x03006800
tree = ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000', 'count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ARM'],
                       type_ignores=[]), '<native ARM>', 'exec'))
checks, captures, inputs, consumers = [], [], [], []
failure, e = None, None


def check(value, label):
    assert value, label
    checks.append(label)


def capture(label):
    e.save(OUT/(label+'.state'))
    if e.frame is not None: e.screenshot(OUT/(label+'.png'))
    (OUT/(label+'.ram')).write_bytes(e.memory())
    (OUT/(label+'.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
    captures.append(dict(label=label, files={p.name:sha(p.read_bytes()) for p in OUT.glob(label+'.*')}))


def tap(key, wait=180):
    inputs.append([8, key, wait]); e.run(8, key); e.run(wait)


def queue(m):
    node, previous, entries = m.word(0x020028c8), 0, {}
    while node:
        assert 0x020025c8 <= node < 0x020028c8 and (node-0x020025c8) % 12 == 0 and len(entries) < 64
        ptr, prev, nxt = struct.unpack('<III', m.read(node, 12))
        assert prev == previous and 0x020021c8 <= ptr < 0x020025c8 and (ptr-0x020021c8) % 16 == 0
        mid = int.from_bytes(m.read(ptr, 2), 'little') & 1023
        assert mid and mid not in entries
        entries[mid] = ptr
        previous, node = node, nxt
    return entries


try:
    # State restoration and SRAM are authenticated separately. Do not replay
    # the completed native save transaction merely to obtain this endpoint.
    e = E(source/'fixture.gba'); e.load(source/'clear-dialog-dismissed.state')
    e.set_memory(0, cleared, 0)
    check(struct.unpack_from('<I',e.memory(),0x3ff60)[0] == 0x106, 'Retained endpoint is native reset countdown')
    inputs.append([3600, 0, 0]); e.run(3600); capture('returned-title')
    check(e.memory(0) == cleared, 'Native reset-to-title leaves cleared flash unchanged')
    for key, wait in ((8,180),(256,60),(256,60),(256,180)): tap(key,wait)
    capture('continued-postgame')
    loaded = e.memory(); iw = C.string_at(*e.maps[0x03000000])
    check(bool(loaded[0x1f76]&64), 'Same-core Continue loads actual saved cleared flag')
    check(owned(loaded) == prior['profiles']['0'], 'Native reset and Continue preserve all24-slot expansion profile')
    check(loaded[0x3f410:0x3f728] == bytes(792), 'Native reset and Continue retire battle-only state')
    check(e.memory(0) == cleared, 'Continue does not rewrite cleared flash')
    m = ARM(image, iw)
    # Keep actual loaded history, placements, calendar, inventory and clan.
    # The paired negative removes only clear flag54 before native generation.
    # No postgame prerequisite, territory or mission receipt is manufactured.
    for is_cleared in (False, True):
        state = bytearray(loaded)
        if not is_cleared: state[0x1f76] &= ~64
        m.put(0x02000000, state); m.put(0x03000000, iw)
        m.call(0x080cfcd0, 0)
        entries = queue(m)
        for mid in (202, 378):
            check((mid in entries) == is_cleared, f'Actual loaded flag gates original postgame mission:{mid}/{is_cleared}')
        visible = set()
        for town in range(8):
            m.put(0x02030100, b'\xa5'*4)
            count = m.call(0x080d0590, 0x02030000, 64, town)
            check(count <= 64 and m.read(0x02030100,4) == b'\xa5'*4, f'Postgame native pub bounds:{is_cleared}/{town}')
            ptrs = struct.unpack('<64I', m.read(0x02030000,256))[:count]
            visible.update(mid for mid,p in entries.items() if p in ptrs)
        for mid in (202,378):
            check((mid in visible) == is_cleared, f'Postgame mission reaches native pub listing:{mid}/{is_cleared}')
        for route in meta['missionRecovery']['gear']['routes']:
            check(m.call(meta['symbols']['ffta_recovery_needed'], route['mission']) == 0,
                  f'Loaded clear alone cannot invent original rare-gear entitlement:{route["mission"]}/{is_cleared}')
        check(owned(m.read(0x02000000,0x40000)) == owned(loaded), f'Postgame listing preserves expansion profile:{is_cleared}')
        consumers.append(dict(cleared=is_cleared, missions=sorted(entries), visible=sorted(visible)))
    check(sha((source/'report.json').read_bytes()) == sha(prior_bytes), 'Accepted producer report unchanged')
    check((source/'cleared.sav').read_bytes() == cleared, 'Accepted cleared SRAM unchanged')
except BaseException as error:
    import traceback
    traceback.print_exc(); failure = repr(error)
    if e is not None: capture('failure')
finally:
    if e is not None: e.close()
report = dict(passed=failure is None, romSha1=meta['romSha1'], sourceSha1=sha(pathlib.Path(__file__).read_bytes()),
              producer=dict(report=str(source/'report.json'),sha1=sha(prior_bytes),checkpoint=checkpoint),
              instrumentedSha1=sha(instrumented), scope=__doc__, checks=checks, assertions=len(checks),
              inputs=inputs,captures=captures,consumers=consumers,nativeRanges=NATIVE_RANGES,failure=failure)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
(OUT/'script.py').write_bytes(pathlib.Path(__file__).read_bytes())
print(json.dumps(dict(passed=report['passed'],checks=len(checks),failure=failure,report=str(OUT/'report.json'))))
assert failure is None, failure
