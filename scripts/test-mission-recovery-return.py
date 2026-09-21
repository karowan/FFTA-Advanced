"""Fixed-input world travel and recovery return from verified pub acceptance.

Uses the retained native acceptance capture with matching ROM/RAM/state hashes.
Native coordinate readers only locate placed areas; ordinary key inputs own
travel, dispatch day advancement, return dialogs and reward collection.
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
source = pathlib.Path(meta['path']).parent/'recovery-pub'
prior = json.loads((source/'report.json').read_text(encoding='utf-8'))
assert prior['passed'] and prior['romSha1'] == meta['romSha1']
anchor = next(r for r in prior['observations'] if r.get('label') == '18-accepted-world')
for ext, key in (('state', 'stateSha1'), ('ram', 'ramSha1')):
    assert hashlib.sha1((source/('18-accepted-world.'+ext)).read_bytes()).hexdigest() == anchor[key]
OUT = pathlib.Path(meta['path']).parent/'recovery-return'; OUT.mkdir(exist_ok=True)
ROM = OUT/'fixture.gba'; ROM.write_bytes(rom)
h = runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
a = runpy.run_path(str(ROOT/'scripts/test-battle-inventory.py'))
checks = []; observations = []; inputs = []

def check(value, label):
    assert value, label
    checks.append(label)

def report(passed=False):
    result = dict(passed=passed, romSha1=meta['romSha1'], acceptedStateSha1=anchor['stateSha1'],
                  assertions=len(checks), checks=checks, observations=observations, inputs=inputs, scope=__doc__)
    (OUT/'report.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return result

atexit.register(report)
def tap(e, key, wait=180):
    inputs.append([8, key, wait]); e.run(8, key); e.run(wait)

def capture(e, label):
    ram = e.memory()
    records = []
    for i in range(64):
        row = ram[0x21c8+i*16:0x21d8+i*16]
        if (row[0] | ((row[1]&3)<<8)) == 407: records.append(row.hex())
    units = [{'slot':i, 'mission':struct.unpack_from('<H', ram, 0x80+i*264+0x16)[0],
              'flags':struct.unpack_from('<H', ram, 0x80+i*264+0x28)[0]} for i in range(6)]
    row = dict(label=label, records=records, units=units,
                             gil=struct.unpack_from('<I', ram, 0x1f64)[0],
                             questItems=list(ram[0x2b08:0x2c08:4]))
    observations.append(row)
    e.screenshot(OUT/(label+'.png')); e.save(OUT/(label+'.state'))
    (OUT/(label+'.ram')).write_bytes(ram)
    row['stateSha1'] = hashlib.sha1((OUT/(label+'.state')).read_bytes()).hexdigest()
    row['ramSha1'] = hashlib.sha1(ram).hexdigest()
    return ram

e = h['Emulator'](ROM)
try:
    e.load(source/'18-accepted-world.state'); e.run(1)
    before = capture(e, '00-accepted')
    check(struct.unpack_from('<H', before, 0x290+0x16)[0] == 407, 'Pub-selected Ford starts assigned')
    # Four fixed journeys exceed the five-day dispatch duration. No forced
    # success, day-counter write, reward injection or native retirement call.
    for leg, area in enumerate((8, 2, 8, 2), 1):
        m = a['ARM'](ctypes.string_at(*e.maps[0x03000000]))
        m.put(0x08000000, rom); m.put(0x02000000, e.memory())
        tile = m.call(0x08036330, area)
        check(0 < tile < 32, f'Leg{leg} destination is placed')
        target = (m.call(0x08035a20, tile-1)+6, m.call(0x08035a44, tile-1)+4)
        route = []
        for frame in range(600):
            x, y = struct.unpack_from('<HH', e.memory(), 0x2c16)
            if abs(x-target[0]) <= 2 and abs(y-target[1]) <= 2: break
            key = (128 if x < target[0] else 64) if abs(x-target[0]) > 2 else (32 if y < target[1] else 16)
            e.run(1, key); route.append([x, y, key])
        else: raise AssertionError(('World cursor did not reach destination', leg, area, target, x, y))
        observations.append(dict(leg=leg, area=area, tile=tile, target=target, route=route))
        e.run(30); tap(e, 256, 1200); ram = capture(e, f'{leg:02}-arrive')
        rec = next(ram[0x21c8+i*16:0x21d8+i*16] for i in range(64)
                   if (ram[0x21c8+i*16] | ((ram[0x21c9+i*16]&3)<<8)) == 407)
        if (rec[1] >> 2) | ((rec[2]&3) << 6): continue
        for page in range(10):
            tap(e, 256, 240); ram = capture(e, f'{leg:02}-dialog-{page:02}')
            if struct.unpack_from('<H', ram, 0x2a6)[0] == 0 and 4 in ram[0x2b08:0x2c08:4]: break
        for _ in range(4): tap(e, 1, 180)
        capture(e, f'{leg:02}-world')
        if struct.unpack_from('<H', e.memory(), 0x2a6)[0] == 0: break
    after = capture(e, '99-finished')
    check(struct.unpack_from('<H', after, 0x290+0x16)[0] == 0, 'Actual world travel returns Ford')
    check(not struct.unpack_from('<H', after, 0x290+0x28)[0] & 4, 'Returned member is no longer away')
    check(list(after[0x2b08:0x2c08:4]).count(4) == 1, 'Native reward confirmation collects one Elda Cup')
    check(struct.unpack_from('<I', after, 0x1f64)[0] == 4700, 'Return charges no additional gil')
    check(all(((after[0x1f70+((mission+0x2ff)>>3)] ^ before[0x1f70+((mission+0x2ff)>>3)])
               & (1 << ((mission+0x2ff)&7))) == 0 for mission in range(512)),
          'Recovery writes no original or service mission-completion flags')
    # Characterize both decisions at the actual native reward boundary. Only
    # the inventory is a fixture write; native dialogs own all item changes.
    stock = b''.join(bytes((item, 0, 0, 0)) for item in range(1, 66) if item != 4)
    assert len(stock) == 256
    for case, keys in (('full-accept', (256, 256, 256, 256, 32, 256, 64, 256)),
                       ('full-reject', (256, 256, 32, 256, 64, 256))):
        e.load(OUT/'02-dialog-01.state'); e.set_memory(0x2b08, stock)
        e.run(1); capture(e, case+'-00')
        for page, key in enumerate(keys, 1):
            tap(e, key, 240); ram = capture(e, f'{case}-{page:02}')
            if struct.unpack_from('<H', ram, 0x2a6)[0] == 0: break
        check(struct.unpack_from('<H', ram, 0x2a6)[0] == 0, case+': native result retires dispatch')
        check(not struct.unpack_from('<H', ram, 0x2b8)[0]&4, case+': Ford is available again')
        expected = bytes((4, 0, 0, 0))+stock[4:] if case == 'full-accept' else stock
        check(ram[0x2b08:0x2c08] == expected, case+': exact chosen inventory survives')
        check(struct.unpack_from('<I', ram, 0x1f64)[0] == 4700, case+': no extra fee')
        # Save through the normal menu, then start a fresh core with SRAM only.
        for key, wait in ((8, 40), (16, 40), (256, 40), (256, 60), (256, 60), (64, 20), (256, 300)):
            tap(e, key, wait)
        sram = e.memory(0); (OUT/(case+'.srm')).write_bytes(sram)
        e.close(); e = h['Emulator'](ROM); e.set_memory(0, sram, 0); e.run(3600)
        for key, wait in ((8, 180), (256, 60), (256, 60), (256, 180)): tap(e, key, wait)
        cold = capture(e, case+'-cold')
        check(cold[0x2b08:0x2c08] == expected, case+': exact collection/discard survives cold Continue')
        check(cold[0x80:0x1940] == ram[0x80:0x1940], case+': returned roster survives cold Continue')
        check(struct.unpack_from('<I', cold, 0x1f64)[0] == 4700, case+': fee survives cold Continue')
finally:
    e.close()
atexit.unregister(report); print(json.dumps(report(True), indent=2))
