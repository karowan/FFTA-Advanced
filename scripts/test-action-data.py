"""Native CCD50 differential/ABI audit of the isolated inert action-data stage."""
import hashlib
import json
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *

OUT = ROOT / 'build/expansion/probes'
meta = json.loads((OUT / 'action-data.json').read_text())
base = (OUT / 'action-data-input.gba').read_bytes()
probe = (OUT / 'action-data.gba').read_bytes()
clean = (ROOT / 'roms/clean/FFTA_US_clean.gba').read_bytes()
sha = lambda b: hashlib.sha1(b).hexdigest()
assert sha(base) == meta['baseSha1'] and sha(probe) == meta['romSha1']
assert sha(clean) == '4ac05441f4de70a4ec3dd932116346c61b8783d9'
ROM, OLD, COUNT, STRIDE = 0x08000000, 0x55187C, 347, 28
TOTAL=432
NEW = meta['addresses']['actions'] - ROM
USERS = [0x23320,0x236AC,0x25998,0x26C9C,0x26D3C,0x26E18,0x27048,0x27170,
         0x279A0,0x27A94,0xA784C,0xB5D18,0xC3080,0xC3474,0xCCD84,0x133E70,0x13416C]
checks = {}

def check(group, condition, detail):
    assert condition, (group, detail)
    checks[group] = checks.get(group, 0) + 1

def word(data, p):
    return struct.unpack_from('<I', data, p)[0]

check('layout', len(probe) == len(base), 'ROM size preserved')
check('layout', OLD+COUNT*STRIDE==0x553E70, 'complete native table ends at descriptor0')
check('layout', clean[OLD+346*STRIDE:OLD+347*STRIDE].hex()=='1e02006400000000024000008f010101400214005501900110022800', 'native Blank Card346 record')
check('layout', meta['originalCount']==COUNT and meta['totalCount']==TOTAL, 'complete action domain metadata')
check('layout', NEW % 4 == 0 and 0x1020000 <= NEW and NEW + TOTAL*28 <= 0x1100000, 'allocation bounds')
check('layout', all(x == 255 for x in base[NEW:NEW+TOTAL*28]), 'allocation previously erased')
check('layout', probe[NEW:NEW+COUNT*STRIDE] == clean[OLD:OLD+COUNT*STRIDE], 'original records preserved')
check('layout', probe[NEW+COUNT*STRIDE:NEW+TOTAL*STRIDE] == bytes(85*28), 'new records inert')
check('layout', probe[OLD:OLD+COUNT*STRIDE] == clean[OLD:OLD+COUNT*STRIDE], 'old table untouched')
check('layout', probe[0x553E70:0x553E74] == bytes(4), 'descriptor0 is no-op')
actual = [p for p in range(0,0x1000000,4) if word(base,p) == ROM+OLD]
check('references', actual == USERS, 'exact 17 native references')
for p in USERS:
    check('references', word(probe,p) == ROM+NEW, hex(p))
    # Direct consumers calculate 28*ID themselves; test each original/new row
    # through each installed literal, independently of the getter result.
    for action in range(TOTAL):
        ptr = word(probe,p)-ROM+action*28
        expected = clean[OLD+action*28:OLD+(action+1)*28] if action<COUNT else bytes(28)
        check('direct-records', probe[ptr:ptr+28] == expected, (hex(p),action))
expected_image = bytearray(base)
expected_image[NEW:NEW+TOTAL*28] = clean[OLD:OLD+COUNT*28] + bytes(85*28)
for p in USERS:
    struct.pack_into('<I', expected_image, p, ROM+NEW)
check('scope', probe == expected_image, 'only allocation and 17 literal writes')

PRESERVED = [UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,
             UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]

class ARM:
    def __init__(self, data):
        self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        self.u.mem_map(ROM, 0x2000000)
        self.u.mem_map(0x03000000, 0x8000)
        self.u.mem_write(ROM, data)
        self.calls = 0

    def call(self, action, selector, residue):
        u = self.u
        sp = 0x03007000 + residue
        u.reg_write(UC_ARM_REG_R0, action)
        u.reg_write(UC_ARM_REG_R1, selector)
        for n, reg in enumerate(PRESERVED):
            u.reg_write(reg, 0x77100000+n)
        u.reg_write(UC_ARM_REG_SP, sp)
        u.reg_write(UC_ARM_REG_LR, 0x03000001)
        u.emu_start(0x080CCD51, 0x03000000, count=200)
        assert u.reg_read(UC_ARM_REG_PC) == 0x03000000
        assert u.reg_read(UC_ARM_REG_SP) == sp
        assert all(u.reg_read(reg) == 0x77100000+n for n, reg in enumerate(PRESERVED))
        self.calls += 1
        return u.reg_read(UC_ARM_REG_R0)

native, expanded = ARM(clean), ARM(probe)
# All documented fields/flags, boundary/default cases and byte truncation.
selectors = list(range(36)) + [0x7F,0xFF,0x100,0x109,0x120,0x121,0x1FF]
for residue in (0,4):
    for action in range(TOTAL):
        for selector in selectors:
            result = expanded.call(action, selector, residue)
            if action < COUNT:
                expected = native.call(action, selector, residue)
                if selector & 255 == 9:
                    expected += NEW-OLD
            else:
                expected = ROM+NEW+28*action+12 if selector & 255 == 9 else 0
            check('native-getter', result == expected, (action,selector,residue,result,expected))
    for action in (0,1,345,346,347,424,431):
        for selector in selectors:
            check('id-truncation', expanded.call(action+0x10000,selector,residue) ==
                  expanded.call(action,selector,residue), (action,selector,residue))

result = {'status':'PASS: inert data/getter stage only; no new effect accepted',
          'romSha1':sha(probe),'baseSha1':sha(base),'checks':checks,
          'nativeCalls':native.calls,'expandedCalls':expanded.calls,
          'actionAddress':hex(ROM+NEW)}
(OUT / 'action-data-test.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
