"""Bounded real menu transitions and native palette-DMA suspension.

Reuses the authenticated showcase input sequence. No player files are written.
Frame traces preserve failed fade endpoints and the exact native effect records.
"""
import ctypes as C
import datetime
import hashlib
import json
import runpy
import struct
from pathlib import Path
from native_art import ROOT, sha

meta = json.loads((ROOT / 'build/art/live-palette/poc.json').read_text())
BASE = meta['ramReservation'][0] - 0x02000000
seedpath = ROOT / 'build/showcase/20260917T160011.215713Z/showcase.sav'
seed = seedpath.read_bytes()
assert hashlib.sha1(seed).hexdigest() == '7831543efb239ef145764889214f8d83cd56eb14'
E = runpy.run_path(str(ROOT / 'scripts/emulator-test.py'))['Emulator']
out = ROOT / 'build/art/live-palette/transitions' / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True)
checks, inputs, observations = [], [], {}
e = None
case = 'setup'
colors = (ROOT / 'build/art/imagegen/human-dark-knight/march-v2-own-palette/palette.bin').read_bytes()
assert sha(colors) == meta['paletteSha256']


def check(ok, label):
    assert ok, case + '/' + label
    checks.append(case + '/' + label)


def region(address):
    return C.string_at(*e.maps[address])


def tap(key, wait=120):
    inputs.append([case, 8, key, wait])
    e.run(8, key)
    e.run(wait)


def sample(label):
    ram, iw = e.memory(), region(0x03000000)
    palette, oam = region(0x05000000), region(0x07000000)
    record = dict(label=label, nativeShadow=iw[0x3860:0x3c60].hex(), palette=palette.hex(),
                  oam=oam.hex(), suspended=struct.unpack_from('<H', iw, 0xe10)[0],
                  owned=sha(ram[0x80:0x1e70]), effects=[])
    pointer = struct.unpack_from('<I', iw, 0x3c64)[0]
    seen = set()
    while pointer and pointer not in seen and len(seen) < 32:
        seen.add(pointer)
        if 0x02000000 <= pointer <= 0x0203ffd4:
            data = ram[pointer - 0x02000000:pointer - 0x02000000 + 44]
        elif 0x03000000 <= pointer <= 0x03007fd4:
            data = iw[pointer - 0x03000000:pointer - 0x03000000 + 44]
        else:
            record['invalidEffectPointer'] = pointer
            break
        record['effects'].append(dict(address=pointer, data=data.hex()))
        pointer = struct.unpack_from('<I', data, 40)[0]
    if case == 'candidate':
        active, applied, restored, failed = struct.unpack_from('<4I', ram, BASE + 0xa0c)
        start, end = struct.unpack_from('<2H', ram, BASE + 0xa1c)
        display_line, display_flags = struct.unpack_from('<2H', ram, BASE + 0xab0)
        record['live'] = dict(active=active, applied=applied, restored=restored, failed=failed,
                              startLine=start, endLine=end, displayLine=display_line, displayFlags=display_flags)
        record['nativeBackup'] = ram[BASE + 0x80c:BASE + 0xa0c].hex()
        # Record both sides of each remapped body without assuming stable OAM indices.
        bank = iw[0x28] ^ 1
        count = struct.unpack_from('<I', iw, 0x20 + bank * 4)[0]
        bodies = []
        if bank < 2 and count <= 128:
            for index in range(128):
                a, b, c = struct.unpack_from('<3H', oam, index * 8)
                if a & 0x300 == 0x200 or not (active & (1 << (c >> 12))):
                    continue
                for j in range(count):
                    native = struct.unpack_from('<3H', iw, 0x30 + bank * 1024 + j * 8)
                    if native[:2] == (a, b) and native[2] & 0xfff == c & 0xfff:
                        oldbank = native[2] >> 12
                        bodies.append(dict(index=index, bank=c >> 12, nativeBank=oldbank,
                                           nativeColors=iw[0x3a60 + oldbank * 32:0x3a80 + oldbank * 32].hex()))
                        break
        record['bodies'] = bodies
    observations[case].append(record)
    return record


def snapshot(label):
    e.screenshot(out / (case + '-' + label + '.png'))
    for ext, address in [('iwram', 0x03000000), ('palette', 0x05000000), ('oam', 0x07000000)]:
        (out / (case + '-' + label + '.' + ext)).write_bytes(region(address))
    (out / (case + '-' + label + '.ram')).write_bytes(e.memory())


try:
    for case, path, digest in [('baseline', meta['source'], meta['baseRomSha1']), ('candidate', meta['path'], meta['romSha1'])]:
        check(hashlib.sha1(Path(path).read_bytes()).hexdigest() == digest, 'ROM authenticated')
        e = E(Path(path))
        e.set_memory(0, seed, 0)
        e.run(3600)
        observations[case] = []
        for key in (8, 256, 256, 256): tap(key, 300)
        check(e.memory()[0x80 + 2 * 264 + 6] == 1, 'same-race member selected')
        e.set_memory(0x80 + 2 * 264 + 4, bytes([1, 117, 1, 117]))
        inputs.append([case, 'isolated appearance profile', 2, [1, 117, 1, 117]])
        for key in (8, 256, 128, 128, 256, 32, 32, 256): tap(key, 600 if key == 256 else 120)
        sample('ready')
        # Exercise the actual native suspension branch on an otherwise unchanged
        # isolated machine. Restore the original flag before natural transitions.
        flag = region(0x03000000)[0xe10:0xe12]
        check(flag == b'\0\0', 'native suspension initially clear')
        inputs.append([case, 'isolated native palette-DMA suspension flag', 1, 3])
        for tick in range(3):
            # This is a one-frame request; the native VBlank tail clears it.
            C.memmove(e.maps[0x03000000][0] + 0xe10, b'\x01\0', 2)
            e.run(1)
            sample('suspended-' + str(tick))
        C.memmove(e.maps[0x03000000][0] + 0xe10, flag, 2)
        for tick in range(3):
            e.run(1)
            sample('resumed-' + str(tick))
        # Ordinary input drives the full wheel -> header -> roster -> world path.
        for phase, key in [('header', 1), ('roster', 1), ('world', 1)]:
            inputs.append([case, phase, key, 8, 180, 'sample every frame'])
            for tick in range(188):
                e.run(1, key if tick < 8 else 0)
                sample(phase + '-' + str(tick))
                if tick in (0, 8, 16, 32, 64, 187): snapshot(phase + '-' + str(tick))
        e.close()
        e = None
    baseline = {r['label']: r for r in observations['baseline']}
    endpoint_count = 0
    for record in observations['candidate']:
        label = record['label']
        before = baseline[label]
        check(record['owned'] == before['owned'], label + ' canonical units unchanged')
        check(record['nativeShadow'] == before['nativeShadow'], label + ' native palette shadow unchanged')
        native = bytearray.fromhex(before['palette'])
        actual = bytes.fromhex(record['palette'])
        live = record['live']
        if live['active']:
            check(160 <= live['startLine'] <= live['endLine'] < 228, label + ' every active transition overlay finishes within VBlank')
            if not live['displayFlags'] & 128:
                check(160 <= live['displayLine'] < 228, label + ' actual native display enable finishes within VBlank')
            if not record['effects']:
                for bank in range(16):
                    if live['active'] & (1 << bank):
                        check(actual[512 + bank * 32:544 + bank * 32] == colors, label + ' exact generated colors throughout unfaded transition')
        check(live['failed'] == 0, label + ' no ownership/allocation failure')
        for bank in range(16):
            if live['active'] & (1 << bank): native[512 + bank * 32:544 + bank * 32] = actual[512 + bank * 32:544 + bank * 32]
        check(bytes(native) == actual, label + ' all unowned hardware colors unchanged')
        if label.startswith('suspended-'):
            check(record['suspended'] == 0 and live['active'] != 0, label + ' native consumes skipped-DMA request while custom actor remains colored')
            check(live['applied'] > observations['candidate'][0]['live']['applied'], label + ' skipped native palette DMA still reapplies the visible custom phase')
        if label.startswith('resumed-'):
            check(record['suspended'] == 0 and live['active'] != 0, label + ' resume reapplies owned palette')
        for body in record['bodies']:
            native_colors = struct.unpack('<16H', bytes.fromhex(body['nativeColors']))
            # Native solid-color fade endpoints have an exact, model-free oracle.
            if len(set(native_colors)) == 1:
                endpoint_count += 1
                custom_colors = actual[512 + body['bank'] * 32:544 + body['bank'] * 32]
                check(custom_colors == bytes.fromhex(body['nativeColors']), label + ' custom actor follows native solid-color fade endpoint')
    check(seedpath.read_bytes() == seed, 'source save unchanged')
    result = dict(status='passed', checks=checks, inputs=inputs, observations=observations,
                  romSha1=meta['romSha1'], baseRomSha1=meta['baseRomSha1'], fadeEndpoints=endpoint_count,
                  scope='Three explicit native suspension/resume frames and every frame of natural wheel/header/roster/world transitions. Exact native shadow/unowned hardware/unit isolation and any observed solid-color fade endpoint. Intermediate fade colors and unseen transition types are not accepted.')
    (out / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status='passed', checks=len(checks), fadeEndpoints=endpoint_count, report=str(out / 'report.json'))))
except Exception as error:
    (out / 'failed.json').write_text(json.dumps(dict(status='failed', error=str(error), checks=checks, inputs=inputs,
                                                  observations=observations, romSha1=meta['romSha1']), indent=2) + '\n')
    print(str(out))
    raise
finally:
    if e: e.close()
