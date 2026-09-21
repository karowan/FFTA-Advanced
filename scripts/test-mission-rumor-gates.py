"""Native rumor enumeration, reading and persistent mission prerequisites.

Controlled original progress flags, real cold-world IWRAM and unchanged native
rumor functions. This is predicate/constructor coverage, not menu playback.
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
clean = (ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
for start, end in ((0xd1b80, 0xd1c94), (0x6130c, 0x61350), (0x5573f4, 0x5577ec)):
    assert rom[start:end] == clean[start:end], ('Original rumor consumer changed', hex(start))
source = pathlib.Path(meta['path']).parent/'recovery-return'
prior = json.loads((source/'report.json').read_text(encoding='utf-8'))
assert prior['passed'] and prior['romSha1'] == meta['romSha1']
anchor = next(row for row in prior['observations'] if row.get('label') == '99-finished')
assert hashlib.sha1((source/'99-finished.state').read_bytes()).hexdigest() == anchor['stateSha1']
OUT = pathlib.Path(meta['path']).parent/'mission-rumor-gates'; OUT.mkdir(exist_ok=True)
h = runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
a = runpy.run_path(str(ROOT/'scripts/test-battle-inventory.py'))
e = h['Emulator'](meta['path'])
try:
    e.load(source/'99-finished.state'); base = e.memory(); iwram = ctypes.string_at(*e.maps[0x03000000])
finally: e.close()
m = a['ARM'](iwram); m.put(0x08000000, rom)
checks = []; observations = []

def check(ok, label):
    assert ok, label
    checks.append(label)

def report(passed=False):
    r = dict(passed=passed, romSha1=meta['romSha1'], assertions=len(checks), checks=checks,
             observations=observations, acceptedStateSha1=anchor['stateSha1'], scope=__doc__)
    (OUT/'report.json').write_text(json.dumps(r, indent=2)+'\n', encoding='utf-8')
    return r

atexit.register(report)
def flag(index, value):
    at = 0x02001f70+(index>>3); mask = 1 << (index&7); old = m.get(at, 1)[0]
    m.put(at, bytes((old|mask if value else old&~mask,)))

def bit(index): return bool(m.get(0x02001f70+(index>>3), 1)[0] & (1 << (index&7)))

def reset():
    m.put(0x02000000, base); m.put(0x03000000, iwram)
    m.put(0x02001f70, bytes(0xc0)); m.put(0x020021c8, bytes(0x704))

def rumors():
    m.put(0x02030100, b'\xa5'*4)
    count = m.call(0x080d1b80, 0x02030000, 64, 2)
    check(count <= 64 and m.get(0x02030100, 4) == b'\xa5'*4, 'Native rumor list stays in its64-slot bound')
    return [m.r32(0x02030000+i*4) for i in range(count)]

def mission_ids():
    ram = m.get(0x020021c8, 1024)
    return [ram[i] | ((ram[i+1]&3)<<8) for i in range(0,1024,16) if any(ram[i:i+16])]

ledger = json.loads((ROOT/'build/reports/mission-item-dependencies.json').read_text(encoding='utf-8'))
assert ledger['candidateSha1'] == meta['romSha1']
needed = sorted({c['selector']-0x500 for row in ledger['originalRecords'] if row['pubEnabled']
                 for c in row['unlock'] if 0x500 < c['selector'] < 0x580 and c['value'] == 1})
for identity in needed:
    reset(); ptr = 0x085573f4+(identity-1)*8
    rid, town, required, reqvalue, excluded, exvalue = struct.unpack('<BBHBHB', m.get(ptr,8))
    check(rid == identity and town == 0, f'Rumor{identity}: original identity and town gate')
    assert 0 < required < 0x600 and excluded < 0x600
    flag(required, reqvalue)
    if excluded: flag(excluded, not exvalue)
    check(ptr in rumors(), f'Rumor{identity}: offered under its actual prerequisites')
    inventory = m.get(0x02002b08,256)
    m.call(0x0806130c, ptr)
    check(bit(0x500|identity), f'Rumor{identity}: native acknowledgment sets its history flag')
    m.call(0x0806130c, ptr)
    check(bit(0x500|identity), f'Rumor{identity}: reading again keeps history')
    check(m.get(0x02002b08,256) == inventory, f'Rumor{identity}: no quest-item consumption')
    if excluded:
        flag(excluded, exvalue)
        check(ptr not in rumors(), f'Rumor{identity}: original exclusion hides the topic')
        check(bit(0x500|identity), f'Rumor{identity}: history survives topic retirement')
    observations.append(dict(rumor=identity, historyFlag=0x500|identity, required=required,
                             excluded=excluded, nativePointer=hex(ptr)))

# The previously unresolved Spiritstone gate is specifically rumor43, whose
# prerequisites are Free Baguba!81 complete and The Spiritstone213 incomplete.
reset(); flag(14+0x2ff,1); flag(81+0x2ff,1)
ptr = 0x085573f4+42*8
check(ptr in rumors(), 'Rumor43 follows Free Baguba completion')
m.call(0x080cfcd0,0)
check(not set((211,212,213)) & set(mission_ids()), 'Ceffyl/Spiritstone recipes remain locked before reading')
m.call(0x0806130c,ptr); m.call(0x080cfcd0,0)
check(set((211,212,213)) <= set(mission_ids()), 'Actual generator posts all three recipes after native rumor acknowledgment')
flag(213+0x2ff,1)
check(ptr not in rumors() and bit(1323), 'Completing Spiritstone retires rumor but preserves repeat gate')
m.put(0x020021c8, bytes(0x704)); m.call(0x080cfcd0,0)
check(set((211,212,213)) <= set(mission_ids()), 'Completed Spiritstone retains original repeatable recipe access')
atexit.unregister(report); print(json.dumps(report(True), indent=2))
