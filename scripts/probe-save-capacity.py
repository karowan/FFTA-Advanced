"""Test candidate persistent storage through the game's save/load menus.

This uses a disposable emulator and save, never the user's active game. The
inventory pattern is deliberately invalid inventory data: no inventory menu or
battle may use it. This probes serialization only, not an inventory migration.
"""
import hashlib, importlib.util, json, pathlib, random

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('harness', ROOT/'scripts/emulator-test.py')
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
OUT = ROOT/'build/expansion/probes'
OUT.mkdir(parents=True, exist_ok=True)
ROM = ROOT/'build/foundation/FFTA_vanillaplus_dev.gba'
SEED = ROOT/'build/test-lab/early-town.sav'

def tap(e, key, wait=40):
    e.run(8, key)
    e.run(wait)

def load(seed):
    e = h.Emulator(ROM)
    e.set_memory(0, seed, 0)
    e.run(3600)
    tap(e, 8, 180)
    tap(e, 256, 60)
    tap(e, 256, 60)
    tap(e, 256, 180)
    return e

seed = SEED.read_bytes()
rng = random.Random(0x46465441)
pattern = bytes(rng.randrange(256) for _ in range(0x5dc))
e = load(seed)
try:
    original = e.memory()
    e.set_memory(0x1940, pattern)
    tap(e, 8)
    tap(e, 16)
    tap(e, 256)
    tap(e, 256, 60)
    tap(e, 256, 60)
    tap(e, 64, 20)
    tap(e, 256, 300)
    saved = e.memory(0)
    assert saved != seed, 'Native save was not updated'
finally:
    e.close()
e = load(saved)
try:
    loaded = e.memory()
    assert loaded[0x1940:0x1f1c] == pattern, 'Inventory region is not serialized verbatim'
    assert loaded[0x80:0x1940] == original[0x80:0x1940], 'Roster changed'
    assert loaded[0x1f1c:0x1f30] == original[0x1f1c:0x1f30], 'Adjacent name data changed'
finally:
    e.close()
report = {
    'passed': True,
    'romSha1': hashlib.sha1(ROM.read_bytes()).hexdigest(),
    'seedSha1': hashlib.sha1(seed).hexdigest(),
    'region': {'start': '0x02001940', 'bytes': len(pattern)},
    'checks': ['All 1500 candidate inventory bytes survive native save and cold load',
               'All 24 roster records are unchanged', 'Adjacent name bytes are unchanged'],
    'limitations': ['Does not establish inventory implementation correctness or old-save migration']
}
(OUT/'save-capacity.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
