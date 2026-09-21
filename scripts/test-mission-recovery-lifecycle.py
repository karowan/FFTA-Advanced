"""Native recovery construction, pub enumeration, assignment and retirement.

One deterministic cold boot provides original IWRAM functions and roster data.
Every native scenario resets that captured RAM, then changes only its declared
flags, mission queue and quest inventory. No stubs, test ROM patches or GUI.
Full reward dialog and save/cold-load playback are separate acceptance work.
"""
import atexit
import collections
import ctypes
import hashlib
import json
import pathlib
import runpy
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *

meta = json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text(encoding='utf-8'))
rom = pathlib.Path(meta['path']).read_bytes()
assert hashlib.sha1(rom).hexdigest() == meta['romSha1']
OUT = pathlib.Path(meta['path']).parent/'recovery-lifecycle'
OUT.mkdir(exist_ok=True)
private = OUT/'fixture.gba'; private.write_bytes(rom)
seedpath = ROOT/'build/test-lab/early-town.sav'; seed = seedpath.read_bytes()
h = runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
e = h['Emulator'](private)
try:
    e.set_memory(0, seed, 0); e.run(3600)
    for key, wait in ((8, 180), (256, 60), (256, 60), (256, 180)):
        e.run(8, key); e.run(wait)
    base = e.memory(); iwram = ctypes.string_at(*e.maps[0x03000000])
    assert any(base[0x80:0x1940]), 'Native roster did not load'
    e.save(OUT/'cold-world.state'); e.screenshot(OUT/'cold-world.png')
finally:
    e.close()
(OUT/'cold-world.ram').write_bytes(base); (OUT/'cold-world.iwram').write_bytes(iwram)
u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
for address, size in ((0x02000000, 0x40000), (0x03000000, 0x8000), (0x04000000, 0x1000), (0x08000000, 0x2000000)):
    u.mem_map(address, size)
u.mem_write(0x08000000, rom)
STACK = 0x03007000; RETURN = 0x08000100; CACHE = 0x020021c8
NODES = 0x020025c8; HEAD = 0x020028c8; BUFFER = 0x02030000
counts = collections.Counter(); observations = []; stops = set()

def report(passed=False):
    value = dict(passed=passed, romSha1=meta['romSha1'], seedSha1=hashlib.sha1(seed).hexdigest(),
                 cases=sum(counts.values()), counts=dict(counts), observations=observations,
                 scope=__doc__)
    (OUT/'report.json').write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')
    return value

atexit.register(report)
u.hook_add(UC_HOOK_CODE, lambda m, a, s, d: m.emu_stop() if a in stops else None)
ARG = (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)
SAVED = (UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7,
         UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11)

def call(address, *args, registers=None, stop=None):
    stops.clear(); stops.update(stop or (RETURN,))
    for i, r in enumerate(SAVED): u.reg_write(r, 0x11110000+i*16)
    for r, v in zip(ARG, args): u.reg_write(r, v)
    for r, v in (registers or {}).items(): u.reg_write(r, v)
    u.reg_write(UC_ARM_REG_SP, STACK); u.reg_write(UC_ARM_REG_LR, RETURN|1)
    u.emu_start(address|1, RETURN, count=5000000)
    assert u.reg_read(UC_ARM_REG_PC) in stops, ('escaped', hex(address), hex(u.reg_read(UC_ARM_REG_PC)))
    assert u.reg_read(UC_ARM_REG_SP) == STACK, ('stack', hex(address))
    if stop is None:
        for i, r in enumerate(SAVED): assert u.reg_read(r) == 0x11110000+i*16, ('preserved', hex(address), r)
    return u.reg_read(UC_ARM_REG_R0)

def flag(ram, mission):
    bit = mission+0x2ff
    ram[0x1f70+(bit>>3)] |= 1 << (bit & 7)

def reset(done=()):
    ram = bytearray(base)
    ram[0x1f70:0x2030] = bytes(0xc0)
    ram[0x21c8:0x28cc] = bytes(0x704)
    ram[0x2b08:0x2c08] = bytes(0x100)
    ram[0x30000:0x30104] = bytes(0x104)
    for mission in done: flag(ram, mission)
    u.mem_write(0x02000000, bytes(ram)); u.mem_write(0x03000000, iwram)
    return ram

def queue():
    ptr = struct.unpack('<I', u.mem_read(HEAD, 4))[0]
    seen = []; prev = 0
    while ptr:
        assert NODES <= ptr < HEAD and (ptr-NODES) % 12 == 0 and len(seen) < 64
        record, previous, nxt = struct.unpack('<III', u.mem_read(ptr, 12))
        assert previous == prev and CACHE <= record < NODES and (record-CACHE) % 16 == 0
        data = bytes(u.mem_read(record, 16))
        seen.append((data[0] | ((data[1] & 3) << 8), record))
        prev, ptr = ptr, nxt
    assert len({m for m, p in seen}) == len(seen), 'Duplicate native mission posting'
    return seen

def note(kind, **values):
    counts[kind] += 1; observations.append(dict(case=kind, **values))

rules = meta['missionRecovery']['rules']
for rule in rules:
    reset(s['mission'] for s in rule['sources'])
    # Full native generator, including original predicates, constructor, reward
    # selection and linked insertion. Eligibility does not manufacture records.
    call(0x080cfcd0, 0)
    entries = dict(queue()); mission = rule['mission']
    assert mission in entries, ('not posted', mission, entries)
    record = entries[mission]; cached = bytes(u.mem_read(record, 16))
    assert cached[2] & 0x1c == 8 and cached[3] == 10
    assert struct.unpack_from('<HH', cached, 8) == (rule['item']+375, 0)
    assert cached[12:16] == bytes(4)
    call(0x080cfcd0, 0); assert dict(queue()) == entries, ('duplicate repost', mission)
    # Whole pub enumeration, including installed stale-offer pruning. Assert
    # output membership and write bound without assuming native sort order.
    u.mem_write(BUFFER+256, b'\xa5'*4)
    count = call(0x080d0590, BUFFER, 64, 0)
    listed = struct.unpack('<64I', u.mem_read(BUFFER, 256))
    assert record in listed and count <= 64, ('pub missing', mission, count, listed)
    assert u.mem_read(BUFFER+256, 4) == b'\xa5'*4
    note('native-construction-list', mission=mission, queue=len(entries), pubCount=count, cached=cached.hex())
    before = bytes(u.mem_read(0x02000000, 0x40000))
    # Use the first ordinary non-Marche roster slot from the cold native save.
    unit = 0x02000080+264
    call(0x080d0b48, record, unit, 0, 0)
    accepted = bytes(u.mem_read(record, 16))
    assert accepted[2] & 0x1c == 0 and accepted[3] == 255
    days = (accepted[1] >> 2) | ((accepted[2] & 3) << 6)
    assert days == 5 and accepted[8:16] == cached[8:16]
    assert struct.unpack('<H', u.mem_read(unit+0x16, 2))[0] == mission
    assert struct.unpack('<H', u.mem_read(unit+0x28, 2))[0] & 4
    assert queue()[-1] == (mission, record), 'Accepted mission not moved to tail'
    assert bytes(u.mem_read(0x02002b08, 256)) == before[0x2b08:0x2c08]
    note('native-assignment', mission=mission, days=days, quality=accepted[6])
    accepted_ram = bytes(u.mem_read(0x02000000, 0x40000))
    # A newly held copy must not make pruning retire an active dispatch.
    u.mem_write(0x02002b08, bytes((rule['item'], 0, 0, 0)))
    call(meta['symbols']['ffta_recovery_prune_offers'])
    assert mission in dict(queue()) and u.mem_read(record, 16) == accepted
    # Native cancel returns the unit and starts the one-day cooldown.
    call(0x080d0ed4, record)
    canceled = bytes(u.mem_read(record, 16))
    assert canceled[2] & 0x1c == 12 and canceled[3] == 1
    assert u.mem_read(unit+0x16, 2) == bytes(2)
    assert not struct.unpack('<H', u.mem_read(unit+0x28, 2))[0] & 4
    call(0x080cf51c)
    assert mission not in dict(queue()) and u.mem_read(record, 16) == bytes(16)
    note('native-cancel-cooldown', mission=mission)
    # Native day counter runs only when its caller reports an elapsed day.
    # Exercise both result branches from the identical actually accepted state.
    for success in (0, 1):
        u.mem_write(0x02000000, accepted_ram); u.mem_write(0x03000000, iwram)
        assert call(0x080d1c94, BUFFER, 64, 0) == 0
        assert u.mem_read(record, 16) == accepted
        for day in range(1, 6):
            u.mem_write(BUFFER, bytes(256))
            returned = call(0x080d1c94, BUFFER, 64, 1)
            now = bytes(u.mem_read(record, 16))
            assert ((now[1] >> 2) | ((now[2] & 3) << 6)) == 5-day
            assert returned == int(day == 5), ('return day', mission, day, returned)
            if day == 5: assert struct.unpack('<I', u.mem_read(BUFFER, 4))[0] == record
        before_flags = bytes(u.mem_read(0x02001f70, 0xc0))
        call(0x080d1e70, record, success)
        assert bytes(u.mem_read(0x02001f70, 0xc0)) == before_flags, ('recovery wrote flags', mission, success)
        assert u.mem_read(unit+0x16, 2) == bytes(2)
        assert not struct.unpack('<H', u.mem_read(unit+0x28, 2))[0] & 4
        result = bytes(u.mem_read(record, 16))
        assert result[2] & 0x1c == 12 and result[3] == 1
        call(0x080cf51c)
        assert mission not in dict(queue()) and u.mem_read(record, 16) == bytes(16)
        assert call(meta['symbols']['ffta_recovery_needed'], mission) == 1
        note('native-return-retirement', mission=mission, success=success, elapsedDays=5)

# Real consumption/release of bound requirements: both Magic Medals, ordinary
# consumed costs, and retained Wyrmstone. Unbound/foreign-bound copies survive.
for mission, item, copies, consumed in ((288, 7, 2, True), (183, 4, 1, True), (69, 22, 1, False)):
    for success in (0, 1):
        reset(); cached = bytearray(16); struct.pack_into('<H', cached, 0, mission)
        cached[4:4+copies] = bytes([item])*copies; u.mem_write(CACHE, bytes(cached))
        for i in range(copies): u.mem_write(0x02002b08+(63-i)*4, struct.pack('<BBH', item, 1, mission))
        u.mem_write(0x02002b08, struct.pack('<BBH', item, 0, 0))
        u.mem_write(0x02002b0c, struct.pack('<BBH', item, 1, 111))
        call(0x080cf118, CACHE, success)
        for i in range(copies):
            want = bytes(4) if success and consumed else bytes((item, 0, 0, 0))
            assert u.mem_read(0x02002b08+(63-i)*4, 4) == want
        assert u.mem_read(0x02002b08, 8) == struct.pack('<BBHBBH', item, 0, 0, item, 1, 111)
        assert u.mem_read(CACHE+4, 2) == bytes(2)
        note('native-consumption-release', mission=mission, success=success, copies=copies, consumed=bool(success and consumed))

assert seedpath.read_bytes() == seed
atexit.unregister(report)
result = report(True)
print(json.dumps({k: v for k, v in result.items() if k != 'observations'}, indent=2))
