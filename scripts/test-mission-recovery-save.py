"""Normal native save and cold load of accepted recovery dispatches.

Fixed inputs use the real world-map Save/Continue menus. Native posting and
assignment create the controlled scenarios; only source flags and inventory
are fixture inputs. No player save, GUI automation or test ROM modification.
"""
import atexit
import ctypes
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

meta = json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text(encoding='utf-8'))
image = pathlib.Path(meta['path']).read_bytes()
assert hashlib.sha1(image).hexdigest() == meta['romSha1']
OUT = pathlib.Path(meta['path']).parent/'recovery-save'; OUT.mkdir(exist_ok=True)
ROM = OUT/'fixture.gba'; ROM.write_bytes(image)
SEED = ROOT/'build/test-lab/early-town.sav'; seed = SEED.read_bytes()
h = runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
checks = []; observations = []

def check(value, label):
    assert value, label
    checks.append(label)

def report(passed=False):
    value = dict(passed=passed, romSha1=meta['romSha1'], seedSha1=hashlib.sha1(seed).hexdigest(),
                 assertions=len(checks), checks=checks, observations=observations, scope=__doc__)
    (OUT/'report.json').write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')
    return value

atexit.register(report)

def tap(e, key, wait=40):
    e.run(8, key); e.run(wait)

def cold(sram):
    e = h['Emulator'](ROM); e.set_memory(0, sram, 0); e.run(3600)
    for key, wait in ((8, 180), (256, 60), (256, 60), (256, 180)): tap(e, key, wait)
    return e

def save(e):
    for key, wait in ((8, 40), (16, 40), (256, 40), (256, 60), (256, 60), (64, 20), (256, 300)):
        tap(e, key, wait)
    return e.memory(0)

class Native:
    def __init__(self, ram, iwram):
        self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        for address, size in ((0x02000000, 0x40000), (0x03000000, 0x8000), (0x04000000, 0x1000), (0x08000000, 0x2000000)):
            self.u.mem_map(address, size)
        self.u.mem_write(0x08000000, image)
        self.u.mem_write(0x02000000, bytes(ram)); self.u.mem_write(0x03000000, iwram)

    def call(self, address, *args):
        saved = (UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7,
                 UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11)
        for i, reg in enumerate(saved): self.u.reg_write(reg, 0x12340000+i*16)
        for reg, value in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3), args):
            self.u.reg_write(reg, value)
        self.u.reg_write(UC_ARM_REG_SP, 0x03007000); self.u.reg_write(UC_ARM_REG_LR, 0x08000101)
        self.u.emu_start(address|1, 0x08000100, count=5000000)
        assert self.u.reg_read(UC_ARM_REG_PC) == 0x08000100, ('native escaped', hex(address))
        assert self.u.reg_read(UC_ARM_REG_SP) == 0x03007000
        for i, reg in enumerate(saved): assert self.u.reg_read(reg) == 0x12340000+i*16
        return self.u.reg_read(UC_ARM_REG_R0)

    def ram(self): return bytes(self.u.mem_read(0x02000000, 0x40000))

def record(ram, mission):
    found = [i for i in range(64) if (ram[0x21c8+i*16] | ((ram[0x21c9+i*16] & 3) << 8)) == mission]
    assert len(found) == 1, ('cached mission absent/duplicated', mission, found)
    at = 0x21c8+found[0]*16
    return at, ram[at:at+16]

def validate_queue(ram):
    ptr = struct.unpack_from('<I', ram, 0x28c8)[0]; previous = 0; seen = []
    while ptr:
        assert 0x020025c8 <= ptr < 0x020028c8 and (ptr-0x020025c8) % 12 == 0 and len(seen) < 64
        rec, prev, nxt = struct.unpack_from('<III', ram, ptr-0x02000000)
        assert prev == previous and 0x020021c8 <= rec < 0x020025c8 and (rec-0x020021c8) % 16 == 0
        seen.append(rec); previous, ptr = ptr, nxt
    assert len(seen) == len(set(seen))
    return seen

e = cold(seed)
try:
    base = e.memory(); iwram = ctypes.string_at(*e.maps[0x03000000])
    e.save(OUT/'world.state')
finally: e.close()

for mission, stock in ((407, 'empty'), (409, 'one-medal'), (470, 'full')):
    rule = next(r for r in meta['missionRecovery']['rules'] if r['mission'] == mission)
    label = f'{mission}-{stock}'
    ram = bytearray(base)
    ram[0x21c8:0x28cc] = bytes(0x704); ram[0x2b08:0x2c08] = bytes(256)
    for source in rule['sources']:
        bit = source['mission']+0x2ff; ram[0x1f70+(bit>>3)] |= 1 << (bit & 7)
    if stock == 'one-medal': ram[0x2b08+63*4] = 7
    if stock == 'full':
        for slot in range(64): ram[0x2b08+slot*4] = 1
    n = Native(ram, iwram)
    check(n.call(meta['symbols']['ffta_recovery_needed'], mission) == 1, label+' entitled before save')
    n.call(0x080cfcd0, 0)
    at, posted = record(n.ram(), mission)
    unit = 0x02000080+264*2  # First ordinary member, eligible for real dispatch.
    n.call(0x080d0b48, 0x02000000+at, unit, 0, 0)
    prepared = n.ram(); _, accepted = record(prepared, mission)
    check((accepted[2] & 0x1c) == 0 and accepted[3] == 255, label+' actual native acceptance')
    check(((accepted[1] >> 2) | ((accepted[2] & 3) << 6)) == 5, label+' five days before save')
    e = h['Emulator'](ROM)
    try:
        e.load(OUT/'world.state')
        # Transfer only native persistent fixture ranges into the unchanged
        # world UI. Heap, renderer, executable IWRAM and world controllers stay.
        for start, end in ((0x80, 0x1940), (0x1f70, 0x2030), (0x21c8, 0x28cc), (0x2b08, 0x2c08)):
            e.set_memory(start, prepared[start:end])
        expected = e.memory(); old_sram = e.memory(0)
        sram = save(e)
        check(sram != old_sram, label+' native Save wrote SRAM')
        e.screenshot(OUT/(label+'-saved.png'))
        (OUT/(label+'.sav')).write_bytes(sram)
        (OUT/(label+'-expected.ram')).write_bytes(expected)
    finally: e.close()
    e = cold(sram)
    try:
        loaded = e.memory(); (OUT/(label+'-loaded.ram')).write_bytes(loaded)
        e.screenshot(OUT/(label+'-loaded.png'))
        at, restored = record(loaded, mission)
        check(restored == accepted, label+' complete accepted mission record survived cold load')
        check(0x02000000+at in validate_queue(loaded), label+' native linked cache restored')
        check(loaded[0x80:0x1940] == expected[0x80:0x1940], label+' all24 roster records including assignment preserved')
        check(loaded[0x1940:0x1f1c] == expected[0x1940:0x1f1c], label+' equipment AP and sidecar preferences preserved')
        check(loaded[0x1f70:0x2030] == expected[0x1f70:0x2030], label+' original completion flags preserved')
        check(loaded[0x2b08:0x2c08] == expected[0x2b08:0x2c08], label+' all64 quest slots preserved')
        after = Native(loaded, ctypes.string_at(*e.maps[0x03000000]))
        check(after.call(meta['symbols']['ffta_recovery_needed'], mission) == 1, label+' earned missing-copy entitlement survives cold load')
        observations.append(dict(mission=mission, inventory=stock, accepted=accepted.hex(),
                                 sramSha1=hashlib.sha1(sram).hexdigest()))
    finally: e.close()

check(SEED.read_bytes() == seed, 'source fixture save unchanged')
atexit.unregister(report); result = report(True)
print(json.dumps(result, indent=2))
