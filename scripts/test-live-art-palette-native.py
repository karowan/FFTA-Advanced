"""Private live-palette rebuild, table transport and native scene-clear contract."""
import argparse, ast, datetime, hashlib, importlib.util, json, struct, sys
from pathlib import Path
from native_art import ROOT, sha
sys.path.insert(0, str(ROOT / 'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
UNIT, EQUIPMENT, RETURN, STACK = 0x02000080, 0x02002000, 0x08000100, 0x03007000
arm_source=(ROOT / 'scripts/test-equipment-legality.py').read_text().replace('count=50000', 'count=3000000')
arm_source=arm_source.replace('self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
    'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree = ast.parse(arm_source)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ARM'], type_ignores=[]), '<native ARM>', 'exec'))
out = ROOT / 'build/art/live-palette/native' / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'); out.mkdir(parents=True)
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--candidate-manifest',type=Path,default=ROOT/'build/art/live-palette/poc.json')
args=parser.parse_args()
meta = json.loads(args.candidate_manifest.read_text())
slots=meta.get('historySlots',10)
rom = Path(meta['path']).read_bytes(); parent = Path(meta['source']).read_bytes()
BASE, LIMIT = meta['ramReservation']
RESERVED = LIMIT - BASE
checks = []

def check(ok, label):
    assert ok, label
    checks.append(label)

try:
    check(hashlib.sha1(rom).hexdigest() == meta['romSha1'], 'Exact private ROM')
    spec = importlib.util.spec_from_file_location('palette_builder', ROOT / 'scripts/build-live-art-palette.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    rebuilt = module.build(history_slots=slots,all_classes=meta.get('allClasses',False),
        workspace_low_address=meta.get('workspaceLowAddress',False),trace_target=meta.get('traceTarget',False),
        provisional_history=meta.get('provisionalHistory',False),fast_rotation=meta.get('fastRotation',False),
        separate_menu_ram=meta.get('separateMenuRam',False),owned_menu_buffer=meta.get('ownedMenuBuffer',False),
        shared_battle_menu_heap=meta.get('sharedBattleMenuHeap',False),compact_us_keyboard=meta.get('compactUsKeyboard',False),
        compact_battle_status=meta.get('compactBattleStatus',False))
    check(rebuilt['romSha1'] == meta['romSha1'] and Path(rebuilt['path']).read_bytes() == rom, 'Clean code/data/draft conversion assembly rebuild is byte-exact')
    if meta.get('separateMenuRam'):
        menu_lo,menu_hi=meta['menuRamReservation']
        check(BASE+meta['transientStateBytes']<=LIMIT<=menu_lo<menu_hi,'Palette state disjoint from fixed party item and ability lists')
        check(0x0200f3b8+struct.unpack_from('<I',rom,0x71228)[0]==menu_lo,'Native party-list pointer retains its original reservation')
    for change in meta['changes']:
        p, size = change['offset'], change['bytes']
        check(parent[p:p + size].hex() == change['before'] and rom[p:p + size].hex() == change['after'], 'Authenticated patch ' + hex(p))
    for record in meta['assignments']:
        old, new = record['source'], record['sequence']; count = struct.unpack_from('<I', parent, old)[0]
        check(count == len(record['frames']) == struct.unpack_from('<I', rom, new)[0], str(record['resource']) + '/' + str(record['slot']) + ' native frame count')
        for i, frame in enumerate(record['frames']):
            check(parent[old + 12 + i * 20:old + 24 + i * 20] == rom[new + 12 + i * 20:new + 24 + i * 20], str((record['resource'], record['slot'], i)) + ' exact native timing/commands/metadata')
            check(sha(rom[frame['tile']:frame['tile'] + 512]) == frame['tileSha256'], str((record['resource'], record['slot'], i)) + ' exact generated pixels')
    # Independent complete lookup check against explicit sets of nonzero pixels.
    address = meta['symbols']['ffta_art_pixel_banks'] - 0x08000000
    lookup = rom[address:address + 131072]
    expected = [sum(1 << bank for bank in {v // 16 for v in (pair & 255, pair >> 8) if v}) for pair in range(65536)]
    check(lookup == struct.pack('<65536H', *expected), 'All 65536 two-pixel lookup values exact')
    iw = (Path(meta['releaseSource']).parent / 'fixture/battle-ready.iwram').read_bytes()
    # Job-clear is a notification callback. The native dispatcher performs
    # that callback and then executes the actual IWRAM zero-fill routine.
    clear = struct.unpack_from('<I', rom, 0x36d4b8)[0]
    for start in (0x020159d0, 0x0201f550, 0x0200f3c4):
        for end in (BASE, 0x0203f000, 0x0203f400):
            a = ARM(rom, iw); a.u.mem_map(0x05000000, 0x1000)
            a.put(start, b'\xa5' * (end - start))
            a.put(BASE, bytes(RESERVED)); a.put(0x0203ff30, b'\xa5' * 20)
            a.put(start - 4, b'\xd7' * 4); a.put(end, b'\xe9' * 4)
            a.call(clear, start, end - start)
            check(a.read(start, end - start) == bytes(end - start), str((start, end)) + ' exact native clear span')
            check(a.read(0x0203ff30, 20) == bytes(20), str((start, end)) + ' existing copy owners retired')
            check(a.read(start - 4, 4) == b'\xd7' * 4, str((start, end)) + ' lower boundary preserved')
            if end == BASE:
                check(a.word(end) == 0x50414c31 and a.read(end + 2052, 8) == bytes(8), str((start, end)) + ' new reserved page initialized with invalidated OAM banks')
                size = meta['transientStateBytes']
                check(a.read(end + size, RESERVED - size) == bytes(RESERVED - size), str((start, end)) + ' reservation tail unchanged')
                if 'variantOffset' in meta:
                    check(a.read(end + meta['variantOffset'],slots*2)==bytes([255]*slots+[0]*slots),str(start)+' variant mapping reset')
                    check(a.read(end + meta['refusalOffset'],16)==bytes(16),str(start)+' refusal diagnostics reset')
                if meta.get('provisionalHistory'):
                    check(a.read(end+meta['confirmedOffset'],slots)==bytes([255]*slots),str(start)+' actor confirmations reset')
            else:
                check(a.read(end, 4) == b'\xe9' * 4, str((start, end)) + ' upper boundary preserved')
        a = ARM(rom, iw); a.u.mem_map(0x05000000, 0x1000)
        a.put(0x0203ff30, b'\xa5' * 20); a.put(BASE, b'\xd7' * RESERVED)
        a.call(clear, start, BASE - 0x1000 - start)
        check(a.read(0x0203ff30, 20) == b'\xa5' * 20 and a.read(BASE, RESERVED) == b'\xd7' * RESERVED, str(start) + ' unrelated clear does not reset owners or palette page')
    report = dict(status='passed', romSha1=meta['romSha1'], checks=checks,
                  scope='Byte-exact private rebuild, all declared patch bytes and class sequence metadata/pixels, exhaustive lookup values, native scene clear at three heap starts/new and legacy ends plus unrelated-clear controls. No worst-case heap capacity, battle/fade/color-mode or final-art acceptance.')
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status='passed', checks=len(checks), report=str(out / 'report.json'))))
except Exception as error:
    (out / 'failed.json').write_text(json.dumps(dict(status='failed', error=str(error), checks=checks, romSha1=meta['romSha1']), indent=2) + '\n')
    print(str(out)); raise
