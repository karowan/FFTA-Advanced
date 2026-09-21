"""Council audit of frozen AP copy constructors and native snapshot rollback.

No rebuilds or user saves. Uses native heap/copy/clear/free and snapshot code;
only battle enumeration and simulation are fixture callbacks. Run after freezing
ability-core.gba/.json and engine.symbols in probes/copy-council.
"""
import ast
import argparse
import ctypes as C
import hashlib
import importlib.util
import json
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/expansion/probes/copy-council'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--current', action='store_true',
                    help='Freeze and test current ability-core ROM, manifest and matching symbols in a per-hash directory.')
parser.add_argument('--job-state', action='store_true', help='Use the private enlarged job-state candidate and its explicit size contract.')
args = parser.parse_args()
assert not (args.current and args.job_state)
if args.job_state:
    candidate=json.loads((ROOT/'build/expansion/probes/job-state/current.json').read_text())
    OUT=pathlib.Path(candidate['path']).parent/'copy-constructors';OUT.mkdir(exist_ok=True)
    (OUT/'ability-core.gba').write_bytes(pathlib.Path(candidate['path']).read_bytes())
    (OUT/'ability-core.json').write_text(json.dumps(candidate))
    merged={p[2]:int(p[0],16) for line in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=line.split())==3}
    merged.update(candidate['symbols'])
    (OUT/'engine.symbols').write_text('\n'.join(f'{value:08x} T {name}' for name,value in merged.items()))
if args.current:
    probe_dir = ROOT / 'build/expansion/probes'
    current_meta_bytes = (probe_dir / 'ability-core.json').read_bytes()
    current_meta = json.loads(current_meta_bytes)
    current_rom = (probe_dir / 'ability-core.gba').read_bytes()
    current_engine = (ROOT / 'build/expansion/engine.bin').read_bytes()
    current_symbols = (ROOT / 'build/expansion/engine.symbols').read_bytes()
    assert hashlib.sha1(current_rom).hexdigest() == current_meta['romSha1'], 'Current ROM changed during freeze'
    assert hashlib.sha1(current_engine).hexdigest() == current_meta['engineSha1'], 'Current engine differs from probe'
    assert current_rom[0x1100000:0x1100000 + len(current_engine)] == current_engine, 'Probe contains different engine'
    OUT = OUT / 'runs' / current_meta['romSha1']
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in [('ability-core.gba', current_rom), ('ability-core.json', current_meta_bytes),
                       ('engine.symbols', current_symbols)]:
        (OUT / name).write_bytes(data)
sys.path.insert(0, str(ROOT / 'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *

UNIT, EQUIPMENT, RETURN, STACK = 0x02000080, 0x02002000, 0x08000100, 0x03007000
source = ast.parse((ROOT / 'scripts/test-equipment-legality.py').read_text())
definitions = [n for n in source.body if isinstance(n, (ast.ClassDef, ast.FunctionDef))
               and n.name in ('ARM', 'iwram_from_boot')]
for definition in definitions:
    for node in ast.walk(definition):
        if isinstance(node, ast.Constant) and node.value == 50000:
            node.value = 500000
exec(compile(ast.Module(body=definitions, type_ignores=[]), '<native-harness>', 'exec'))
rom = (OUT / 'ability-core.gba').read_bytes()
metadata = json.loads((OUT / 'ability-core.json').read_text())
assert hashlib.sha1(rom).hexdigest() == metadata['romSha1']
symbols = {p[2]: int(p[0], 16) for line in (OUT / 'engine.symbols').read_text().splitlines()
           if len(p := line.split()) == 3}
entries = [(0x9de94, 'ffta_snapshot_entry'), (0x97000, 'ffta_manager_entry')]
if 'ffta_party_copy_entry' in symbols:
    entries += [(0x7109c, 'ffta_party_copy_entry'), (0x1443fc, 'ffta_library_copy_entry')]
for offset, name in entries:
    assert struct.unpack_from('<I', rom, offset + 4)[0] == symbols[name] | 1
iwram = iwram_from_boot()
checks = {}
owner_root_size = 20 if 'ffta_party_copy_register' in symbols else 16
EXTRA=61 if args.job_state else 38
SNAPSHOT=0x1140 if args.job_state else 0x1014
MANAGER=0x430 if args.job_state else 0x400
SELECTION=0x3840 if args.job_state else 0x3828
PARTY=0x7280 if args.job_state else 0x7268
HEAP_END=0x0203f400 if args.job_state else 0x0203f800


def check(group, condition, message):
    assert condition, f'{group}: {message}'
    checks[group] = checks.get(group, 0) + 1


def w32(m, address, value): m.put(address, struct.pack('<I', value))


def new_machine():
    m = ARM(rom, iwram)
    m.put(0x02000000, bytes(0x40000))
    m.put(0x02001e70, b'FFTAEXP1\x01')
    if args.job_state:m.call(symbols['ffta_job_reset'])
    m.heap = 0x02018000
    m.call(0x080070c8, m.heap, 0x27000)
    w32(m, 0x0200f434, m.heap)
    m.initial_heap = m.read(m.heap, 20)
    m.alignment = []
    def aligned(u, address, size, data):
        m.alignment.append((address, u.reg_read(UC_ARM_REG_SP)))
    for name in ['ffta_snapshot_register', 'ffta_manager_register', 'ffta_selection_register',
                 'ffta_copy_owner_free', 'ffta_on_unit_copy', 'ffta_party_copy_register']:
        if name not in symbols: continue
        m.u.hook_add(UC_HOOK_CODE, aligned, begin=symbols[name], end=symbols[name])
    return m


def seed_roster(m):
    expected = []
    for slot in range(13):
        data = bytearray((slot * 17 + i) & 255 for i in range(264))
        data[4], data[5], data[6], data[7] = 1, 2, 1, 2
        data[0x104] = 12 - slot  # Native snapshot sorts this field.
        ap = bytes((slot * 23 + i * 3) & 255 for i in range(34))
        m.put(UNIT + slot * 264, data)
        m.put(0x02001b40 + slot * 34, ap)
        m.put(0x02001e80 + slot, [slot % 3])
        m.put(0x02001ebc + slot * 2, struct.pack('<H',0x8000+slot*71))
        if args.job_state:m.put(0x0203f410+slot*22,bytes((slot*31+i*7+5)&255 for i in range(22)))
        expected.append((bytes(data), ap, slot % 3))
        w32(m, 0x02005000 + slot * 0x40, UNIT + slot * 264)
    return expected


def enumeration(m, count=13):
    def enumerate_units(u, address, size, data):
        out = u.reg_read(UC_ARM_REG_R1)
        for slot in range(count): w32(m, out + slot * 4, 0x02005000 + slot * 0x40)
        u.reg_write(UC_ARM_REG_R0, count)
        u.reg_write(UC_ARM_REG_PC, u.reg_read(UC_ARM_REG_LR))
    return m.u.hook_add(UC_HOOK_CODE, enumerate_units, begin=0x08099cdc, end=0x08099cdc)


def tail(m, unit):
    return m.call(symbols['ffta_owned_extra_ap'], unit, 144)


for stack in (STACK, STACK - 4):
    m = new_machine()
    original = seed_roster(m)
    enumeration(m)
    snapshots = []
    for generation in range(3):
        snapshot = m.call(0x08022840, SNAPSHOT)
        check('allocation', m.call(0x0800717c, 0, snapshot) == SNAPSHOT, 'snapshot capacity')
        control = ARM((ROOT / 'roms/clean/FFTA_US_clean.gba').read_bytes(), iwram)
        control.put(0x02000000, m.read(0x02000000, 0x40000))
        enumeration(control)
        control.call(0x0809de94, snapshot, 0x02006000, stack=stack)
        m.call(0x0809de94, snapshot, 0x02006000, stack=stack)
        snapshots.append(snapshot)
        check('constructor', m.read(snapshot, 0xe1c) == control.read(snapshot, 0xe1c),
              'complete native snapshot prefix changed')
        check('constructor', m.word(snapshot) == 13, 'unit count')
        check('constructor', m.word(snapshot + 0xe20) == 0x31535041, 'node magic')
        for position, slot in enumerate(reversed(range(13))):
            unit = snapshot + 4 + position * 264
            address = tail(m, unit)
            expected_native, ap, preference = original[slot]
            check('snapshot_rows', m.read(unit, 264) == expected_native, f'native unit {position}')
            check('snapshot_rows', address == snapshot + 0xe24 + position * EXTRA, 'tail identity')
            check('snapshot_rows', m.read(address, 34) == ap, f'AP unit {position}')
            check('snapshot_rows', m.read(address + 34, 1)[0] == preference, 'preference')
            check('snapshot_rows', m.read(address + 36, 2) == struct.pack('<H',0x8000+slot*71), 'wound follows sorted unit')
            if args.job_state:
                record=m.call(symbols['ffta_job_state'],unit)
                check('snapshot_jobs',m.read(record,22)==bytes((slot*31+i*7+5)&255 for i in range(22)),'record follows native sort')
                check('snapshot_jobs',m.call(symbols['ffta_job_origin'],unit)==slot+1,'exact source token follows native sort')
        check('constructor', m.word(0x0203ff34) == snapshot, 'head registration')
    # Free the middle, then head, then tail through the real native allocator.
    for position in (1, 2, 0):
        allocation = snapshots[position]
        m.call(0x08022854, allocation, stack=stack)
        check('free', tail(m, allocation + 4) == 0, 'freed node still owned')
        for remaining in [p for p in snapshots if p != allocation and m.word(p + 0xe20) == 0x31535041]:
            check('free', tail(m, remaining + 4) == remaining + 0xe24, 'live node lost')
    check('free', m.word(0x0203ff34) == 0, 'nonempty chain')
    check('free', m.read(m.heap, 20) == m.initial_heap, 'heap not fully reclaimed')
    check('abi', all(sp % 8 == 0 for _, sp in m.alignment), 'unaligned C entry')

    # Full native preview wrapper allocates, snapshots, restores, and frees.
    # Fixture simulation mutates live records and the external AP sidecars.
    def simulate(u, address, size, data):
        for slot in range(13):
            m.put(UNIT + slot * 264 + 0x20, [0xee])
            m.put(0x02001b40 + slot * 34, b'\xFA' * 34)
            m.put(0x02001e80 + slot, [9])
            if args.job_state:m.put(0x0203f410+slot*22,b'\xFE'*22)
        u.reg_write(UC_ARM_REG_R0, 0)
        u.reg_write(UC_ARM_REG_PC, u.reg_read(UC_ARM_REG_LR))
    m.u.hook_add(UC_HOOK_CODE, simulate, begin=0x0809e1e0, end=0x0809e1e0)
    preview_instructions = [0]
    def count_preview(u, address, size, data): preview_instructions[0] += 1
    counter = m.u.hook_add(UC_HOOK_CODE, count_preview)
    result = m.call(0x0809f850, 0x02006000, stack=stack)
    m.u.hook_del(counter)
    print('Native snapshot/rollback instruction count:', preview_instructions[0], flush=True)
    check('rollback', result == 0x02005000 + 12 * 0x40, 'chosen unit wrapper')
    for slot, (native, ap, preference) in enumerate(original):
        check('rollback', m.read(UNIT + slot * 264, 264) == native, 'native rollback')
        check('rollback', m.read(0x02001b40 + slot * 34, 34) == ap, 'AP rollback')
        check('rollback', m.read(0x02001e80 + slot, 1)[0] == preference, 'preference rollback')
        if args.job_state:check('job_rollback',m.read(0x0203f410+slot*22,22)==bytes((slot*31+i*7+5)&255 for i in range(22)),'job record rollback')
    check('rollback', m.word(0x0203ff34) == 0, 'preview leaked ownership')
    check('rollback', m.read(m.heap, 20) == m.initial_heap, 'preview leaked heap')
    check('abi', all(sp % 8 == 0 for _, sp in m.alignment), 'preview C alignment')

def stub_return(m, address, result):
    def callback(u, pc, size, data):
        u.reg_write(UC_ARM_REG_R0, result)
        u.reg_write(UC_ARM_REG_PC, u.reg_read(UC_ARM_REG_LR))
    return m.u.hook_add(UC_HOOK_CODE, callback, begin=address, end=address)


for stack in (STACK, STACK - 4):
    m = new_machine()
    seed_roster(m)
    # Resource sizing/loading is unrelated to AP ownership. The enclosing
    # manager allocation, subheaps, unit-container constructors and clears run.
    for address, result in [(0x08022080, 0x400), (0x0814913c, 0x40),
                            (0x08021a3c, 0), (0x0814914c, 0),
                            (0x0808f79c, 0), (0x081493c0, 0)]:
        stub_return(m, address, result)
    m.call(0x08096ed4, stack=stack)
    manager = m.word(0x0200f4b0)
    parent = m.word(0x0200f4b8)
    check('manager', m.word(0x0203ff38) == manager, 'registered manager differs from native global')
    check('manager', m.call(0x0800717c, 0, manager) == MANAGER, 'manager capacity')
    check('manager', m.read(manager + 0x3b4, 2*EXTRA) == bytes(2*EXTRA), 'tail not initialized')
    check('manager', tail(m, manager + 0x40) == manager + 0x3b4, 'first manager copy')
    check('manager', tail(m, manager + 0x148) == manager + 0x3b4+EXTRA, 'second manager copy')
    check('manager', tail(m, manager + 0x41) == 0, 'interior pointer accepted')
    w32(m, 0x0200f4b0, 0)
    check('manager', tail(m, manager + 0x40) == 0, 'detached manager still owns AP')
    w32(m, 0x0200f4b0, manager)
    m.call(0x08007170, m.word(manager), manager, stack=stack)
    check('manager', m.word(0x0203ff38) == 0, 'native free did not invalidate manager')
    check('manager', tail(m, manager + 0x40) == 0, 'freed manager still owns AP')
    check('abi', all(sp % 8 == 0 for _, sp in m.alignment), 'manager C alignment')

    m = new_machine()
    # Native selection lifecycle invokes these unrelated scheduler routines.
    for address in (0x08005c14, 0x08005a24, 0x08005b18, 0x08005c34):
        stub_return(m, address, 0)
    state = 0x02007000
    m.put(state, [0])
    m.call(0x08064ef8, 0, state, stack=stack)
    selection = m.word(0x0200f454)
    check('selection', m.word(0x0203ff3c) == selection, 'native selection registration')
    check('selection', m.call(0x0800717c, 0, selection) == SELECTION, 'selection allocation size')
    check('selection', m.read(selection + 0x3800, EXTRA) == bytes(EXTRA), 'selection tail')
    check('selection', tail(m, selection + 0xa4c) == selection + 0x3800, 'selection owner')
    check('selection', tail(m, selection + 0xa50) == 0, 'selection interior')
    m.put(state, [255])
    m.call(0x08064ef8, 0, state, stack=stack)
    check('selection', m.word(0x0203ff3c) == 0 and m.word(0x0200f454) == 0, 'native teardown')
    check('selection', tail(m, selection + 0xa4c) == 0, 'freed selection owner')
    check('selection', m.read(m.heap, 20) == m.initial_heap, 'selection heap leak')
    check('abi', all(sp % 8 == 0 for _, sp in m.alignment), 'selection C alignment')

for start in (0x020159d0, 0x0201f550, 0x0200f3c4):
    for adjust in (0, -4):
        m = new_machine()
        m.call(symbols['ffta_snapshot_register'], 0x02010000)
        if owner_root_size == 20:
            w32(m, 0x0203ff40, 0x02020000)
        m.put(0x0203ff30 + owner_root_size, b'\xDB' * 16)
        before = m.read(0x0203ff30, owner_root_size)
        m.call(symbols['ffta_job_clear' if args.job_state else 'ffta_on_unit_clear'], start, HEAP_END - start + adjust)
        check('heap_reset', m.read(0x0203ff30, owner_root_size) == (bytes(owner_root_size) if adjust == 0 else before),
              'heap reset extent')
        check('heap_reset', m.read(0x0203ff30 + owner_root_size, 16) == b'\xDB' * 16,
              'heap reset exceeded owner root')

if 'ffta_party_copy_register' in symbols:
    for mode in (0, 1):
        for stack in (STACK, STACK - 4):
            m = new_machine()
            original = seed_roster(m)
            # This constructor calls GBA BIOS CpuSet; emulate that firmware
            # primitive, not any game allocation/constructor/copy/free code.
            def cpu_set(u, pc, size, data):
                src, dest, control = [u.reg_read(reg) for reg in
                                     (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2)]
                width = 4 if control & (1 << 26) else 2
                count = control & 0x1fffff
                payload = m.read(src, width) * count if control & (1 << 24) else m.read(src, width * count)
                m.put(dest, payload)
                u.reg_write(UC_ARM_REG_PC, u.reg_read(UC_ARM_REG_LR))
            m.u.hook_add(UC_HOOK_CODE, cpu_set, begin=0x0814186c, end=0x0814186c)
            w32(m, 0x03002778, m.heap)
            w32(m, 0x03000e54, 0x27000)
            m.put(0x0203ff44, b'\xDA' * 16)
            m.call(0x0807109c, mode, stack=stack)
            party = m.word(0x03002818)
            preview = party + 0x1be4
            address = party + 0x7240
            check('party', m.call(0x0800717c, 0, party) == PARTY, 'party allocation')
            check('party', m.word(0x0203ff40) == party, 'party registration')
            check('party', tail(m, preview) == address, 'preview ownership')
            check('party', m.read(address, EXTRA) == bytes(EXTRA), 'party tail initialization')
            check('party', m.read(0x0203ff44, 16) == b'\xDA' * 16, 'root guard')
            for slot, (native, ap, preference) in enumerate(original):
                result = m.call(0x081443fc, preview, UNIT + slot * 264, 264, stack=stack)
                check('party_copy', result == preview and m.read(preview, 264) == native, 'library native copy/return')
                check('party_copy', m.read(address, 34) == ap, 'library AP snapshot')
                check('party_copy', m.read(address + 34, 1)[0] == preference, 'library preference')
                check('party_copy', m.read(address + 36, 2) == struct.pack('<H',0x8000+slot*71), 'library wound')
                if args.job_state:
                    record=m.call(symbols['ffta_job_state'],preview)
                    check('party_jobs',m.read(record,22)==bytes((slot*31+i*7+5)&255 for i in range(22)),'library job record')
                    check('party_jobs',m.call(symbols['ffta_job_origin'],preview)==slot+1,'library origin')
                m.put(0x02001b40 + slot * 34, b'\x99' * 34)
                check('party_copy', m.read(address, 34) == ap, 'preview aliases live AP')
                m.put(0x02001b40 + slot * 34, ap)
            before = m.read(address, EXTRA)
            m.call(0x081443fc, preview, UNIT, 260, stack=stack)
            check('party_copy', m.read(address, EXTRA) == before, 'partial copy touched tail')
            m.call(0x0814224c, preview, 264, m.word(0x0836d4b8), stack=stack)
            check('party_clear', m.read(preview, 264) == bytes(264), 'native unit clear')
            check('party_clear', m.read(address, EXTRA) == bytes(EXTRA), 'full clear retained AP or status')
            for slot, (_, ap, preference) in enumerate(original):
                check('party_clear', m.read(0x02001b40 + slot * 34, 34) == ap, 'clear changed live AP')
            w32(m, 0x03002818, 0)
            check('party', tail(m, preview) == 0, 'detached party owner')
            w32(m, 0x03002818, party)
            m.call(0x08071234, mode, stack=stack)
            check('party_free', m.word(0x0203ff40) == 0, 'native destructor did not retire party')
            check('party_free', tail(m, preview) == 0, 'freed party still owns AP')
            check('party_free', m.read(0x0203ff44, 16) == b'\xDA' * 16, 'destructor root guard')
            check('abi', all(sp % 8 == 0 for _, sp in m.alignment), 'party C alignment')

report = {'passed': True, 'romSha1': metadata['romSha1'], 'checks': checks,
          'frozenDirectory': str(OUT), 'partyOwnershipTested': 'party' in checks,
          'scope': 'Native13-unit snapshot construction/sorting/copy, three-node free order, '
                   'full9F850 allocation/snapshot/rollback/free, both Thumb stack residues, '
                   'AP and preference preservation; native manager allocation and selection '
                   'create/destroy, exact heap-reset extents. Enumeration, simulation, scheduler '
                   'and unrelated manager resources stubbed. When party ownership exists: '
                   'both native party constructor/destructor modes, generic library copy, '
                   'preview independence, full clear and20-byte root guard; BIOS CpuSet emulated.',
          'limitations': ['No real battle AI or rendering', 'No user save touched']}
(OUT / 'constructor-tests.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
