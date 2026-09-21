"""Actual pub availability after cold-loaded reward collection or rejection.

Reuses verified native reward/cold-Continue captures. No gameplay RAM writes:
ordinary travel advances cooldown and native pub menus construct offers.
"""
import atexit
import ctypes
import hashlib
import json
import pathlib
import runpy
import struct

ROOT = pathlib.Path(__file__).resolve().parents[1]
meta = json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text(encoding='utf-8'))
rom = pathlib.Path(meta['path']).read_bytes()
assert hashlib.sha1(rom).hexdigest() == meta['romSha1']
source = pathlib.Path(meta['path']).parent/'recovery-return'
prior = json.loads((source/'report.json').read_text(encoding='utf-8'))
assert prior['passed'] and prior['romSha1'] == meta['romSha1']
OUT = pathlib.Path(meta['path']).parent/'recovery-repeat'; OUT.mkdir(exist_ok=True)
ROM = OUT/'fixture.gba'; ROM.write_bytes(rom)
h = runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
a = runpy.run_path(str(ROOT/'scripts/test-battle-inventory.py'))
checks = []; observations = []; inputs = []

def check(value, label):
    assert value, label
    checks.append(label)

def report(passed=False):
    result = dict(passed=passed, romSha1=meta['romSha1'], assertions=len(checks),
                  checks=checks, observations=observations, inputs=inputs, scope=__doc__)
    (OUT/'report.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return result

atexit.register(report)
def tap(e, key, wait=180):
    inputs.append([8, key, wait]); e.run(8, key); e.run(wait)

def capture(e, label):
    ram = e.memory(); e.screenshot(OUT/(label+'.png')); e.save(OUT/(label+'.state'))
    (OUT/(label+'.ram')).write_bytes(ram)
    observations.append(dict(label=label, stateSha1=hashlib.sha1((OUT/(label+'.state')).read_bytes()).hexdigest(),
                             ramSha1=hashlib.sha1(ram).hexdigest()))
    return ram

for case, expected in (('full-accept', False), ('full-reject', True)):
    anchor = next(r for r in prior['observations'] if r.get('label') == case+'-cold')
    for ext, key in (('state', 'stateSha1'), ('ram', 'ramSha1')):
        check(hashlib.sha1((source/(case+'-cold.'+ext)).read_bytes()).hexdigest() == anchor[key], case+': verified '+ext)
    e = h['Emulator'](ROM)
    try:
        e.load(source/(case+'-cold.state')); e.run(1); before = e.memory()
        for area in (8, 2):
            m = a['ARM'](ctypes.string_at(*e.maps[0x03000000]))
            m.put(0x08000000, rom); m.put(0x02000000, e.memory())
            tile = m.call(0x08036330, area); assert 0 < tile < 32
            target = (m.call(0x08035a20, tile-1)+6, m.call(0x08035a44, tile-1)+4)
            route = []
            for _ in range(600):
                x, y = struct.unpack_from('<HH', e.memory(), 0x2c16)
                if abs(x-target[0]) <= 2 and abs(y-target[1]) <= 2: break
                key = (128 if x < target[0] else 64) if abs(x-target[0]) > 2 else (32 if y < target[1] else 16)
                e.run(1, key); route.append([x, y, key])
            else: raise AssertionError(('World navigation exceeded bound', case, area))
            observations.append(dict(case=case, area=area, route=route))
            e.run(30); tap(e, 256, 1200); capture(e, case+f'-travel-{area}')
        for i in range(4): tap(e, 256); ram = capture(e, case+f'-pub-{i}')
        ctx = struct.unpack_from('<I', ram, 0xf448)[0]-0x02000000
        check(0 <= ctx < 0x3e000, case+': native pub context')
        count = ram[ctx+0x11a9]
        pointers = [struct.unpack_from('<I', ram, ctx+0x11ac+i*4)[0]-0x02000000 for i in range(count)]
        check(0 < count <= 16 and all(0x21c8 <= p < 0x25c8 for p in pointers), case+': valid native pub list')
        ids = [ram[p] | ((ram[p+1]&3)<<8) for p in pointers]
        observations.append(dict(case=case, pubMissionIds=ids))
        check((407 in ids) == expected, case+': offer follows held versus rejected reward after native cooldown')
        check(ram[0x2b08:0x2c08] == before[0x2b08:0x2c08], case+': no item lost on returning to pub')
        check(struct.unpack_from('<I', ram, 0x1f64)[0] == 4700, case+': no automatic charge')
    finally: e.close()
atexit.unregister(report); print(json.dumps(report(True), indent=2))
