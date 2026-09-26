"""Compare a regular mission's post-acceptance screen in clean and modified FFTA.

The original early-town SRAM is loaded into an isolated emulator. The sole
progress input is the original Herb Picking completion flag, which posts the
ordinary Dueling Sub dispatch. No user save or
ROM is modified.
"""
import hashlib
import json
from pathlib import Path
import runpy
import struct
import ctypes
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
Emulator = runpy.run_path(str(ROOT / 'scripts/emulator-test.py'))['Emulator']
ARM = runpy.run_path(str(ROOT / 'scripts/test-battle-inventory.py'))['ARM']
seed_path = ROOT / 'build/test-lab/early-town.sav'
seed = seed_path.read_bytes()
out = ROOT / 'build/expansion/probes/pub-return'
out.mkdir(parents=True, exist_ok=True)
candidate = json.loads((ROOT / 'build/expansion/probes/pub-return/candidate/manifest.json').read_text())
cases = (
    ('clean', ROOT / 'roms/clean/FFTA_US_clean.gba', True),
    ('previous', ROOT / 'build/play-cache/4b972fc6d4c6db712c1c026e4c951228cf89bb8b6c6d54bd3411f11c87033eb3/FFTA_Reviewed_All_Classes.gba', False),
    ('fixed', Path(candidate['path']), False),
)
report = {'seedSha1': hashlib.sha1(seed).hexdigest(), 'cases': []}

for name, rom_path, missions_second in cases:
    case_out = out / name
    case_out.mkdir(exist_ok=True)
    rom = rom_path.read_bytes()
    row = {'name': name, 'romSha1': hashlib.sha1(rom).hexdigest(), 'inputs': [], 'captures': []}
    with Emulator(rom_path) as game:
        game.set_memory(0, seed, 0)
        game.run(3600)

        def tap(key, wait=180):
            game.run(8, key)
            game.run(wait)
            row['inputs'].append([8, key, wait])

        for key, wait in ((8, 180), (256, 60), (256, 60), (256, 180)):
            tap(key, wait)  # finish the ordinary Continue/Load before fixture setup
        ram = game.memory()
        flag = 770  # original Herb Picking completion, prerequisite of Dueling Sub 130
        at = 0x1f70 + (flag >> 3)
        game.set_memory(at, bytes((ram[at] | (1 << (flag & 7)),)))
        game.set_memory(0x1f64, struct.pack('<I', 5000))
        native = ARM(ctypes.string_at(*game.maps[0x03000000]))
        native.put(0x08000000, rom)
        native.put(0x02000000, game.memory())
        for _ in range(20):
            native.call(0x080cf51c)  # native days retire the already-cleared opening offer
        native.call(0x080cfcd0, 0)  # original offer generator, before rendered pub entry
        generated = native.get(0x02000000, 0x40000)
        game.set_memory(0, native.get(0x02000000, 0x40000))

        def capture(label):
            game.screenshot(case_out / (label + '.png'))
            row['captures'].append(label)

        def assignments():
            data = game.memory()
            return [struct.unpack_from('<H', data, 0x80 + 264 * i + 0x16)[0]
                    for i in range(24)]

        def gil():
            return struct.unpack_from('<I', game.memory(), 0x1f64)[0]

        tap(256, 240)
        tap(256, 180)
        capture('00-pub-menu')
        if missions_second:
            tap(32, 60)
        tap(256, 240)
        capture('01-mission-list')
        data = game.memory()
        ctx = struct.unpack_from('<I', data, 0xf448)[0] - 0x02000000
        assert 0 <= ctx < 0x3e000, (name, 'pub context')
        count = data[ctx + 0x11a9]
        pointers = [struct.unpack_from('<I', data, ctx + 0x11ac + 4 * i)[0] - 0x02000000
                    for i in range(count)]
        ids = [data[p] | ((data[p + 1] & 3) << 8) for p in pointers]
        row['pubMissionIds'] = ids
        assert 130 in ids, (name, 'Dueling Sub dispatch absent', ids)
        for _ in range(ids.index(130)):
            tap(32, 180)
        capture('02-dispatch-row')
        tap(256)
        capture('03-dispatch-details')
        for index, key in enumerate((256, 256, 128, 128, 256) + (256,) * 20):
            tap(key)
            capture(f'{index + 4:02d}-input')
            if 130 in assignments() and gil() < 5000:
                row['acceptedAtInput'] = index
                break
        assert 130 in assignments() and gil() < 5000, (name, 'Dueling Sub mission not accepted')
        row['gilAfterAccept'] = gil()
        capture('accepted-dialog')
        game.run(240)
        capture('idle-after-accept')
        tap(256)
        capture('next-a')
        with Image.open(case_out / 'next-a.png') as im:
            # Native LIST/PRICE header versus Rumors' differently placed LIST bar.
            row['returnHeaderSha256'] = hashlib.sha256(im.crop((100, 90, 620, 118)).tobytes()).hexdigest()
    report['cases'].append(row)

assert seed_path.read_bytes() == seed
assert report['cases'][0]['returnHeaderSha256'] != report['cases'][1]['returnHeaderSha256'], 'v0.7.3 regression did not reproduce'
assert report['cases'][0]['returnHeaderSha256'] == report['cases'][2]['returnHeaderSha256'], 'fixed return did not show native mission list'
assert report['cases'][1]['gilAfterAccept'] == report['cases'][2]['gilAfterAccept'] == 4700
assert report['cases'][2]['romSha1'] == candidate['romSha1']
report['status'] = 'passed'
(out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'report': str(out / 'report.json'),
                  'cases': [{'name': r['name'], 'romSha1': r['romSha1'],
                             'gilAfterAccept': r['gilAfterAccept']} for r in report['cases']]}))
