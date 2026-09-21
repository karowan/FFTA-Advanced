"""Native one-time equipment gift gates, separated from reward UI acceptance.

Every original gift is isolated by marking the other gift receipts claimed.
Declared clan levels test each required threshold, exact reward/quantity and
nonrepeatability. No award or return value is supplied by the fixture.
"""
import atexit
import ctypes
import hashlib
import json
import pathlib
import runpy

ROOT = pathlib.Path(__file__).resolve().parents[1]
meta = json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text(encoding='utf-8'))
rom = pathlib.Path(meta['path']).read_bytes()
clean = (ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
assert hashlib.sha1(rom).hexdigest() == meta['romSha1']
ledger = json.loads((ROOT/'build/reports/vanilla-teaching-sources.json').read_text(encoding='utf-8'))
assert ledger['candidateSha1'] == meta['romSha1']
for start, end in ((0x46910, 0x469f8), (0x528256, 0x528556)):
    assert rom[start:end] == clean[start:end], 'Original clan gift consumer changed'
source = pathlib.Path(meta['path']).parent/'recovery-return'
prior = json.loads((source/'report.json').read_text(encoding='utf-8'))
assert prior['passed'] and prior['romSha1'] == meta['romSha1']
anchor = next(row for row in prior['observations'] if row.get('label') == '99-finished')
assert hashlib.sha1((source/'99-finished.state').read_bytes()).hexdigest() == anchor['stateSha1']
h = runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
a = runpy.run_path(str(ROOT/'scripts/test-battle-inventory.py'))
e = h['Emulator'](meta['path'])
try:
    e.load(source/'99-finished.state')
    base = e.memory()
    iwram = ctypes.string_at(*e.maps[0x03000000])
finally:
    e.close()
m = a['ARM'](iwram)
m.put(0x08000000, rom)
OUT = pathlib.Path(meta['path']).parent/'vanilla-clan-gifts'
OUT.mkdir(exist_ok=True)
checks = []
observations = []


def check(ok, label):
    assert ok, label
    checks.append(label)


def report(passed=False):
    row = dict(passed=passed, romSha1=meta['romSha1'], assertions=len(checks),
               acceptedStateSha1=anchor['stateSha1'], checks=checks,
               observations=observations, scope=__doc__)
    (OUT/'report.json').write_text(json.dumps(row, indent=2)+'\n', encoding='utf-8')
    return row


atexit.register(report)
for gift in ledger['clanGifts']:
    # Leave only this row unclaimed. Bit63 is the empty sentinel and remains set.
    mask = ((1 << 64)-1) ^ (1 << gift['index'])
    for below in [None, *[r['skill'] for r in gift['requirements']]]:
        ram = bytearray(base)
        ram[0x2c08:0x2c10] = mask.to_bytes(8, 'little')
        for skill in range(8):
            ram[0x21b6+2*skill] = next((r['level'] for r in gift['requirements'] if r['skill'] == skill), 0)
        if below is not None:
            ram[0x21b6+2*below] -= 1
        ram[0x30000:0x30004] = b'\xa5'*4
        m.put(0x02000000, ram)
        m.put(0x03000000, iwram)
        result = m.call(0x08046910, 0x02030000)
        want = gift['item'] if below is None else 0
        check(result == want, f"Gift{gift['index']} threshold{below}: exact reward")
        expected = bytearray(ram)
        expected[0x30000] = gift['quantity'] if below is None else 0
        if below is None:
            expected[0x2c08:0x2c10] = ((1 << 64)-1).to_bytes(8, 'little')
        check(m.get(0x02000000, 0x40000) == expected,
              f"Gift{gift['index']} threshold{below}: only receipt and quantity change")
        if below is None:
            check(m.call(0x08046910, 0x02030000) == 0, f"Gift{gift['index']}: cannot claim twice")
            expected[0x30000] = 0
            check(m.get(0x02000000, 0x40000) == expected, f"Gift{gift['index']}: no repeat side effects")
        observations.append(dict(gift=gift['index'], belowSkill=below, item=result,
                                 quantity=gift['quantity'] if below is None else 0))
atexit.unregister(report)
r = report(True)
print(json.dumps({k: r[k] for k in ('passed', 'romSha1', 'assertions')}, indent=2))
