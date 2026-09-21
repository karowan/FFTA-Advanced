"""Fixed-input recovery pub selection and acceptance diagnostics.

Original progress and inventory are fixture inputs. --gear also supplies
50000 gil so the ordinary displayed equipment-recovery fee can be paid.
The actual game constructs offers and owns all menu/controller transitions.
Bounded captures retain the exact UI state at every input for root review.
"""
import atexit
import hashlib
import json
import pathlib
import runpy
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
meta = json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text(encoding='utf-8'))
rom = pathlib.Path(meta['path']).read_bytes(); assert hashlib.sha1(rom).hexdigest() == meta['romSha1']
STALE = '--stale' in sys.argv
GEAR = int(sys.argv[sys.argv.index('--gear')+1]) if '--gear' in sys.argv else None
label=f'gear-pub-{GEAR}' if GEAR else 'recovery-pub'
OUT = pathlib.Path(meta['path']).parent/(label+'-stale' if STALE else label); OUT.mkdir(exist_ok=True)
ROM = OUT/'fixture.gba'; ROM.write_bytes(rom)
seedpath = ROOT/'build/test-lab/early-town.sav'; seed = seedpath.read_bytes()
h = runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
observations = []; checks = []

def check(value, label):
    assert value, label
    checks.append(label)

def report(passed=False):
    value = dict(passed=passed, romSha1=meta['romSha1'], seedSha1=hashlib.sha1(seed).hexdigest(),
                 checks=checks, observations=observations, scope=__doc__)
    (OUT/'report.json').write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')
    return value

atexit.register(report)

def word(ram, at): return struct.unpack_from('<I', ram, at)[0]

def capture(e, label):
    ram = e.memory(); ctx = word(ram, 0xf448)-0x02000000
    row = dict(label=label, gil=word(ram, 0x1f64))
    if 0 <= ctx < 0x3e000:
        row.update(context=hex(ctx+0x02000000), state=ram[ctx+0x1199:ctx+0x11aa].hex(),
                   selected=hex(word(ram, ctx+0x1450)), unit=hex(word(ram, ctx+0x1454)),
                   fee=struct.unpack_from('<H', ram, ctx+0x11a4)[0])
    observations.append(row)
    e.screenshot(OUT/(label+'.png')); e.save(OUT/(label+'.state'))
    (OUT/(label+'.ram')).write_bytes(ram)
    row['stateSha1'] = hashlib.sha1((OUT/(label+'.state')).read_bytes()).hexdigest()
    row['ramSha1'] = hashlib.sha1(ram).hexdigest()
    return ram, ctx

def tap(e, key, wait=120):
    e.run(8, key); e.run(wait)

e = h['Emulator'](ROM)
try:
    e.set_memory(0, seed, 0); e.run(3600)
    for key, wait in ((8, 180), (256, 60), (256, 60), (256, 180)): tap(e, key, wait)
    ram = bytearray(e.memory())
    rule = next(r for r in meta['missionRecovery']['gear']['routes'] if r['mission']==GEAR) if GEAR else meta['missionRecovery']['rules'][0]
    bits = ([54]+([rule['originalMission']+0x2ff] if 'originalMission' in rule else [])) if GEAR else [s['mission']+0x2ff for s in rule['sources']]
    for bit in bits:
        at = 0x1f70+(bit>>3)
        ram[at] |= 1 << (bit & 7)
        e.set_memory(at, bytes(ram[at:at+1]))
    if GEAR:
        if 'originalGift' in rule:
            at=0x2c08+(rule['originalGift']>>3)
            e.set_memory(at,bytes((ram[at]|(1<<(rule['originalGift']&7)),)))
        e.set_memory(0x1f64,struct.pack('<I',50000))
        e.set_memory(0x1940+rule['item'],b'\x00')
    e.set_memory(0x2b08, bytes(256))
    gil = word(e.memory(), 0x1f64)
    for key, wait in ((256, 240), (256, 180), (256, 120), (256, 120)): tap(e, key, wait)
    ram, ctx = capture(e, '01-pub-list')
    check(0 <= ctx < 0x3e000, 'Native pub context exists')
    count = ram[ctx+0x11a9]
    pointers = [word(ram, ctx+0x11ac+i*4) for i in range(count)]
    check(0 < count <= 16 and all(0x020021c8 <= p < 0x020025c8 for p in pointers), 'Native16-row list is valid')
    ids = [(ram[p-0x02000000] | ((ram[p-0x02000000+1] & 3) << 8)) for p in pointers]
    check(rule['mission'] in ids, 'Earned missing item creates an actual visible recovery offer')
    index = ids.index(rule['mission'])
    observations.append(dict(pubMissionIds=ids, selectedIndex=index))
    for _ in range(index): tap(e, 32)
    capture(e, '02-recovery-row')
    tap(e, 256); ram, ctx = capture(e, '03-recovery-details')
    check(word(ram, ctx+0x1450) == pointers[index], 'Detail selection refers to the native recovery record')
    check(word(ram, 0x1f64) == gil, 'Viewing recovery details charges no fee')
    # The native first-time mission-item tutorial adds four dialog pages.
    # Its fixed inputs precede the normal equip-items OK and final confirmation.
    for i, key in enumerate((256, 256, 128, 128, 256, 256, 256, 256, 256, 256), 4):
        tap(e, key, 180); capture(e, f'{i:02}-input-{key}')
    fee = struct.unpack_from('<H', e.memory(), ctx+0x11a4)[0]
    chosen_unit = word(e.memory(), ctx+0x1454)-0x02000000
    expected_fee = 15000 if GEAR else 300
    check(fee == expected_fee, f'Native town-adjusted recovery fee is{expected_fee} gil')
    accepted = False
    for i in range(14, 18):
        tap(e, 256, 180); ram, ctx = capture(e, f'{i:02}-confirm')
        rec = pointers[index]-0x02000000
        if STALE and i == 14:
            # Fixed adverse scenario: acquire the missing copy after opening
            # final confirmation, before the Yes branch and any payment.
            if GEAR:e.set_memory(0x1940+rule['item'],b'\x01')
            else:e.set_memory(0x2b08+63*4, bytes((rule['item'], 0, 0, 0)))
        if STALE and i == 15:
            check(word(ram, 0x1f64) == gil, 'Stale offer charges no fee')
            check(ram[rec:rec+16] == bytes(16), 'Native list refresh removes rejected stale offer')
            check(all((ram[0x21c8+j*16] | ((ram[0x21c9+j*16]&3)<<8)) != rule['mission'] for j in range(64)),
                  'Rejected stale mission is absent from all64 cache records')
            check(struct.unpack_from('<H', ram, chosen_unit+0x16)[0] == 0, 'Stale offer assigns nobody')
            check(not struct.unpack_from('<H', ram, chosen_unit+0x28)[0] & 4, 'Stale offer never marks member away')
            check(ram[0x1940+rule['item']]==1 if GEAR else ram[0x2b08+63*4:0x2c08] == bytes((rule['item'], 0, 0, 0)), 'Stale offer preserves newly held copy')
            break
        if ram[rec+2] & 0x1c == 0:
            accepted = True
            break
    if not STALE:
        check(accepted, 'Actual pub confirmation accepts recovery')
        check(word(ram, 0x1f64) == gil-fee, 'Acceptance charges the displayed fee once')
        unit = chosen_unit
        check(0x80 <= unit < 0x1940 and (unit-0x80) % 264 == 0, 'Native member choice is a real roster unit')
        check(struct.unpack_from('<H', ram, unit+0x16)[0] == rule['mission'], 'Actual selected member assigned to recovery')
        check(struct.unpack_from('<H', ram, unit+0x28)[0] & 4, 'Selected member marked away')
    for _ in range(4): tap(e, 1, 180)
    capture(e, '18-accepted-world')
    check(seedpath.read_bytes() == seed, 'Original fixture save unchanged')
finally:
    e.close()
atexit.unregister(report); result = report(True)
print(json.dumps(result, indent=2))
