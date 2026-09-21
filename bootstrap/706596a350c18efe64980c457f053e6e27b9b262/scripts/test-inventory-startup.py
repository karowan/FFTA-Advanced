"""Compare actual native new-game grants with the converted inventory engine."""
import importlib.util, json, pathlib, struct, hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('harness',ROOT/'scripts/emulator-test.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
OUT=ROOT/'build/expansion/probes'
rom=OUT/'inventory-startup.gba'
e=h.Emulator(rom)
try:
    for frames,keys in [(3600,0),(8,8),(300,0),(8,256),(300,0),
        (8,8),(60,0),(8,64),(30,0),(8,256),(180,0),
        (8,8),(60,0),(8,64),(30,0),(8,256),(300,0),
        (8,16),(60,0),(8,256),(120,0),
        (30,0),(40,128),(16,16),(30,0),(8,256),(120,0)]:e.run(frames,keys)
    actual=e.memory()
    e.screenshot(OUT/'inventory-new-game.png')
finally:e.close()
e=h.Emulator(ROOT/'build/foundation/FFTA_vanillaplus_dev.gba')
try:
    e.load(ROOT/'build/test-lab/early-town.state')
    original=e.memory()
finally:e.close()
expected=bytearray(512)
for i in range(375):
    item,owned,equipped=struct.unpack_from('<HBB',original,0x1940+i*4)
    if item:expected[item]=owned
assert actual[0x1940:0x1b40]==expected,'Native starting grants changed'
assert actual[0x1e70:0x1e79]==b'FFTAEXP1\x01','New game did not initialize current format'
assert actual[0x1b40:0x1e70]==bytes(816),'New game did not clear AP extension'
# Native saving adjusts transient unit flags. Compare identity/stats/equipment,
# not the post-save battle bookkeeping bytes at the end of each record.
for i in range(24):
    offset=0x80+i*264
    assert actual[offset:offset+0x40]==original[offset:offset+0x40],f'Starter unit {i} changed'
report={'passed':True,'romSha1':hashlib.sha1(rom.read_bytes()).hexdigest(),
        'checks':['Actual native new-game initialization creates compressed inventory',
                  'Every starting equipment/consumable total matches the original engine',
                  'All24 original starting unit identity/stat/equipment headers match',
                  'New Human AP storage starts empty'],
        'limitations':['Test-only quickstart skips story cutscenes',
                       'Inventory menus are not adapted in this probe']}
(OUT/'inventory-startup-test.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
