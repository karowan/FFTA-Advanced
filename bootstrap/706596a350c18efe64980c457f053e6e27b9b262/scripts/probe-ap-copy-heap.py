"""Council-only native heap reservation experiment; never distributes a ROM."""
import hashlib, json, pathlib, runpy, struct, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
h = runpy.run_path(str(ROOT / 'scripts/emulator-test.py'))
OUT = ROOT / 'build/expansion/probes/ap-heap'
OUT.mkdir(parents=True, exist_ok=True)
clean = (ROOT / 'roms/clean/FFTA_US_clean.gba').read_bytes()


def heap(ram):
    def word(offset): return struct.unpack_from('<H', ram, offset)[0]
    base = struct.unpack_from('<I', ram, 0xF434)[0]
    if not 0x02000000 <= base < 0x02040000: return {'base': base}
    off = base - 0x02000000
    size = 8 + word(off + 6) * 4
    blocks, cursor, seen = [], off + 8, set()
    while cursor and cursor not in seen:
        assert off <= cursor < off + size
        seen.add(cursor)
        marker = ram[cursor + 4:cursor + 6].decode('ascii', errors='replace')
        assert marker in ('la', 'ps'), (hex(cursor), marker)
        n = word(cursor + 6) * 4
        blocks.append({'address': 0x02000000 + cursor, 'marker': marker,
                       'payloadBytes': n - 12 if marker == 'la' else n})
        next_offset = word(cursor + 2)
        cursor = off + next_offset * 4 if next_offset else 0
    free = [b['payloadBytes'] for b in blocks if b['marker'] == 'ps']
    return {'base': base, 'end': base + size, 'blocks': len(blocks),
            'allocatedPayload': sum(b['payloadBytes'] for b in blocks if b['marker'] == 'la'),
            'freePayload': sum(free), 'largestFree': max(free, default=0),
            'highestAllocatedEnd': max((b['address'] + 12 + b['payloadBytes'] for b in blocks if b['marker'] == 'la'), default=base),
            'allocationBlocks': blocks}


def image(end):
    result = bytearray(clean)
    result.extend(b'\xFF' * (0x2000000 - len(result)))
    if end == 0x02040000: return result
    for index, (site, continuation) in enumerate([(0x227FC, 0x22804), (0x4CA14, 0x4CA1C), (0x13C078, 0x13C080)]):
        assert result[site:site+8].hex() == '8124a404641b0848'
        stub = 0x01F00000 + index * 24
        struct.pack_into('<HHI', result, site, 0x4B00, 0x4718, 0x08000001 + stub)
        struct.pack_into('<6H3I', result, stub, 0x4C02, 0x1B64, 0x4802, 0x4B03, 0x4718, 0x46C0,
                         end, 0x0836D4B8, 0x08000001 + continuation)
    return result


def run(end):
    rom = OUT / f'heap-{end:08x}.gba'
    rom.write_bytes(image(end))
    e = h['Emulator'](rom)
    snapshots, frames = [], []
    try:
        e.run(3600); e.run(8, 8); e.run(180)
        if end < 0x02040000: e.set_memory(end - 0x02000000, b'\xA5' * (0x02040000 - end))
        e.run(8, 256); e.run(1800)
        for step in range(71):
            if step:
                key = 8 if step == 31 else 64 if step == 32 else 256
                e.run(8, key); e.run(120)
            if step in (0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70):
                ram = e.memory()
                current = heap(ram)
                current['step'] = step
                if end < 0x02040000:
                    top = ram[end - 0x02000000:]
                    current['reservedChangedBytes'] = sum(v != 0xA5 for v in top)
                    current['reservedFirstChange'] = next((end + i for i, v in enumerate(top) if v != 0xA5), None)
                snapshots.append(current)
                frames.append(e.frame)
                e.screenshot(OUT / f'heap-{end:08x}-{step}.png')
        e.save(OUT / f'heap-{end:08x}.state')
    finally: e.close()
    return {'end': end, 'romSha1': hashlib.sha1(rom.read_bytes()).hexdigest(), 'snapshots': snapshots}, frames


if __name__ == '__main__':
    results = []
    reference = None
    ends = (0x02040000, 0x0203F000, 0x0203F800) if '--small' in sys.argv else (0x02040000, 0x02030000, 0x0203A000, 0x0203C000)
    for end in ends:
        try:
            report, frames = run(end)
            if reference is None: reference = frames
            report['matchesNativeFrames'] = [a == b for a, b in zip(reference, frames)]
            results.append(report)
        except Exception as error:
            results.append({'end': end, 'error': repr(error)})
    (OUT / ('small-report.json' if '--small' in sys.argv else 'report.json')).write_text(json.dumps(results, indent=2))
    print(json.dumps([{k: v for k, v in r.items() if k != 'snapshots'} | {'samples': [
        {k: v for k, v in s.items() if k != 'allocationBlocks'} for s in r.get('snapshots', [])]} for r in results], indent=2))
