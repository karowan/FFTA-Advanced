"""Native Capture admission, monster-bank storage and Soul inventory awards.

Reuse a hashed cold-world fixture from the equipment recovery test. Units are
declared inputs with original species/job metadata, not captured battle actors.
Execute original accuracy, slot selection, application, disposal and release;
do not replace game callbacks or grant the expected Soul directly. Static formation witnesses are
separate from encounter reachability and full battle/menu acceptance.
"""
import atexit
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
source = pathlib.Path(meta['path']).parent/'gear-recovery'
provenance = json.loads((source/'report.json').read_text(encoding='utf-8'))
assert provenance['romSha1'] == meta['romSha1']
for name, expected in provenance['files'].items():
    assert hashlib.sha1((source/name).read_bytes()).hexdigest() == expected, name
ram = (source/'cold-world.ram').read_bytes()
iwram = (source/'cold-world.iwram').read_bytes()
ARM = runpy.run_path(str(ROOT/'scripts/test-battle-inventory.py'))['ARM']
m = ARM(iwram)
m.put(0x08000000, rom)
OUT = pathlib.Path(meta['path']).parent/'soul-sources'
OUT.mkdir(exist_ok=True)
A, T, C, BANK = 0x02000080, 0x020033e4, 0x02008000, 0x02002e78
checks, species, awards, releases = [], [], [], []


def check(ok, label):
    assert ok, label
    checks.append(label)


def report(passed=False):
    result = dict(passed=passed, romSha1=meta['romSha1'], assertions=len(checks),
                  checks=checks, species=species, awards=awards, releases=releases,
                  fixtureFiles=provenance['files'], scope=__doc__)
    (OUT/'report.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return result


atexit.register(report)
for start, end in ((0x12edf0, 0x12ee98), (0x12f124, 0x12f154),
                   (0x13347c, 0x1334cc), (0x12d99c, 0x12da0c)):
    check(rom[start:end] == clean[start:end], f'Original Capture consumer preserved:{start:x}')

# Match the original Capture record through the installed action table.
action_table = struct.unpack_from('<I', rom, 0xccd84)[0]-0x08000000
check(rom[action_table+188*28:action_table+189*28] == clean[0x55187c+188*28:0x55187c+189*28],
      'Original Capture action preserved')
check(clean[0x553e70+0xbd*4:0x553e70+0xbd*4+4] == bytes((23,74,19,0)), 'Capture descriptor provenance')

# Native full formation domain. Event/missions are candidates, not a claim
# that every dynamic branch or story-dependent roaming offer is accessible.
events = {}
for event in range(1,256):
    primary, secondary = struct.unpack_from('<HH', rom, 0x563a70+event*12+2)
    formation = secondary or primary
    if not 1 <= formation <= 442:
        continue
    repeat = [i for i in range(1,407) if rom[0x55ae4c+i*70+69] == event
              and rom[0x55ae4c+i*70+0x41] & 8]
    if event > 225 or repeat:
        events.setdefault(formation, []).append(dict(event=event, roamingClan=event-225 if event>225 else None,
                                                   repeatableMissions=repeat))
sources = {}
for formation, links in events.items():
    p = 0x54cd54+formation*40
    count, units = rom[p], struct.unpack_from('<I', rom, p+4)[0] & 0x1ffffff
    if not count:
        continue
    check(count <= 13 and 0x52a4d0 <= units and units+48*count <= 0x54bb30,
          f'Full formation bounds:{formation}')
    for slot in range(count):
        template = units+48*slot
        sources.setdefault(rom[template+1], []).append(dict(formation=formation, slot=slot,
                            templateOffset=template, templateType=rom[template], events=links))


def target(job):
    unit = bytearray(ram[0x80:0x188])
    unit[4] = 1
    unit[5] = unit[7] = job
    unit[6] = rom[0x521a14+job*52+4]
    unit[9] = 30
    unit[0x28:0x2a] = b'\0\x80'
    unit[0x2a:0x34] = bytes(10)
    unit[0x3a:0x3d] = bytes(3)
    unit[0xe8:0xf0] = bytes(8)
    struct.pack_into('<4H', unit, 0x18, 1, 100, 20, 20)
    m.put(T, unit)
    context = bytearray(52)
    struct.pack_into('<IIIH', context, 0, A, T, T, 188)
    context[0x24] = 30
    m.put(C, context)


m.put(0x02000000, ram)
m.put(BANK, bytes(20*16))
m.put(0x02001940+229, bytes(9))
for job in range(44,68):
    target(job)
    slot = m.call(0x080c9428, T)
    soul = m.call(0x0812edf0, T)
    if slot == 0xffffffff:
        check(soul == 0, f'Uncapturable species has no Soul:{job}')
        continue
    check(0 <= slot < 20 and 229 <= soul <= 237, f'Capture mapping:{job}')
    check(bool(sources.get(job)), f'Repeatable formation witness:{job}')
    species.append(dict(job=job, race=rom[0x521a14+job*52+4], bankSlot=slot,
                        soul=soul, sourceCandidates=sources[job]))
    check(m.call(0x08130dcc, C) == 1, f'Living monster eligibility:{job}')
    check(m.call(0x0812d99c, T, 30) == 24, f'Original low-HP Capture chance:{job}')
    check(m.call(0x0812f124, T) == BANK+slot*16, f'Empty species-bank slot:{job}')
    # Preview must never grant equipment or store a captured monster.
    m.w16(C+0x26, 0x10)
    before = m.get(0x02000000, 0x40000)
    m.call(0x0813347c, C)
    check(m.get(0x02000000, 0x40000) == before, f'Capture preview is pure:{job}')
    m.w16(C+0x26, 0)
    before_bag = m.get(0x02001940, 512)
    before_bank = m.get(BANK, 20*16)
    # Exercise reacquisition after disposing the previous Soul when a second
    # species in its family remains uncaptured. CA9E8 is the real loss API.
    held = before_bag[soul]
    if held:
        m.call(0x080ca9e8, soul, held)
        check(m.get(0x02001940+soul, 1) == b'\0', f'Native Soul disposal:{job}')
        before_bag = m.get(0x02001940, 512)
    m.call(0x0813347c, C)
    expected = bytearray(before_bag)
    expected[soul] += 1
    check(m.get(0x02001940, 512) == expected, f'Exactly one native Soul award:{job}')
    bank = m.get(BANK, 20*16)
    check(bank[:slot*16] == before_bank[:slot*16] and bank[(slot+1)*16:] == before_bank[(slot+1)*16:],
          f'Other captured species preserved:{job}')
    check(bank[slot*16:slot*16+4] == m.get(T,4) and bank[slot*16+4] == 1, f'Native monster stored:{job}')
    check(m.call(0x0812f124, T) == 0, f'Occupied species bank has no new slot:{job}')
    awards.append(dict(job=job, soul=soul, bankSlot=slot, reacquisitionAfterDisposal=bool(held)))

check(len(species) == 20 and len({s['soul'] for s in species}) == 9, 'All20 species/all9 Soul families')
check(m.call(0x080ccbc4) == 20, 'Native bank reports all20 captured species')
check(m.call(0x0812d99c, T,30) == 0, 'Full monster bank blocks Capture')
for family in range(229,238):
    check(any(a['soul'] == family and a['reacquisitionAfterDisposal'] for a in awards),
          f'Native Soul reacquisition with another family member:{family}')

# The Monster Bank confirmation branch at5A6D4 calls CC510(selected slot).
# Follow that same release consumer, then recapture the same species even
# after every species has already been captured. No saved one-time grant gate.
check(rom[0x5a698:0x5a6ec] == clean[0x5a698:0x5a6ec], 'Original bank release caller preserved')
check(rom[0xcc510:0xcc598] == clean[0xcc510:0xcc598], 'Original bank release consumer preserved')
for row in species:
    job, soul, slot = row['job'], row['soul'], row['bankSlot']
    target(job)
    before_bank = m.get(BANK, 320)
    before_bag = m.get(0x02001940,512)
    m.call(0x080cc510, slot)
    bank = m.get(BANK,320)
    # CC510 clears the name pointer and every data byte except +4. Native
    # occupancy is the name pointer, so the retained marker is not a capture.
    empty = bytearray(16)
    empty[4] = before_bank[slot*16+4]
    check(bank[slot*16:slot*16+16] == empty, f'Exact native released bank record:{job}')
    check(bank[:slot*16] == before_bank[:slot*16] and bank[(slot+1)*16:] == before_bank[(slot+1)*16:],
          f'Release preserves other species:{job}')
    check(m.get(0x02001940,512) == before_bag, f'Release preserves owned Souls:{job}')
    check(m.call(0x080ccbc4) == 19 and m.call(0x0812f124,T) == BANK+slot*16,
          f'Released species regains its own native slot:{job}')
    check(m.call(0x0812d99c,T,30) == 24, f'Recapture has ordinary chance:{job}')
    m.call(0x080ca9e8,soul,before_bag[soul])
    before_bag = m.get(0x02001940,512)
    check(before_bag[soul] == 0, f'Soul really disposed before same-species recapture:{job}')
    m.call(0x0813347c,C)
    expected = bytearray(before_bag)
    expected[soul] = 1
    check(m.get(0x02001940,512) == expected, f'Same-species recapture restores missing Soul:{job}')
    check(m.get(BANK,320) == before_bank and m.call(0x080ccbc4) == 20,
          f'Recaptured native monster bank restored:{job}')
    releases.append(dict(job=job,soul=soul,bankSlot=slot))
atexit.unregister(report)
r = report(True)
print(json.dumps({k:r[k] for k in ('passed','romSha1','assertions')}, indent=2))
