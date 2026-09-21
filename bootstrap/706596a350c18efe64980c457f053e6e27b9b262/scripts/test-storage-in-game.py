"""Migration and extension persistence through real mGBA/native save menus.

The probe ROM intentionally has no inventory UI port. Only load/save menus are
used. It is isolated under build/, and no user-facing game/save is modified.
"""
import hashlib, importlib.util, json, pathlib, random, struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('harness',ROOT/'scripts/emulator-test.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
OUT=ROOT/'build/expansion/probes'
ROM=OUT/'storage-only.gba'
FOUNDATION=ROOT/'build/foundation/FFTA_vanillaplus_dev.gba'
SEED=ROOT/'build/test-lab/early-town.sav'

def tap(e,key,wait=40):e.run(8,key);e.run(wait)
def cold_load(rom,seed):
    e=h.Emulator(rom);e.set_memory(0,seed,0);e.run(3600)
    tap(e,8,180);tap(e,256,60);tap(e,256,60);tap(e,256,180)
    return e
def save(e):
    tap(e,8);tap(e,16);tap(e,256);tap(e,256,60);tap(e,256,60)
    tap(e,64,20);tap(e,256,300)
    return e.memory(0)

seed=SEED.read_bytes()
e=cold_load(FOUNDATION,seed)
try:original=e.memory()
finally:e.close()
expected=bytearray(512)
for i in range(375):
    item,owned,equipped=struct.unpack_from('<HBB',original,0x1940+i*4)
    if item:
        assert item<=375 and owned<=99 and equipped<=owned
        expected[item]=owned

e=cold_load(ROM,seed)
try:
    migrated=e.memory()
    assert migrated[0x1940:0x1b40]==expected,'Load hook did not preserve inventory totals'
    assert migrated[0x1e70:0x1e79]==b'FFTAEXP1\x01','Missing version marker after load'
    assert migrated[0x1b40:0x1e70]==bytes(816),'New AP storage not initialized'
    assert migrated[0x80:0x1940]==original[0x80:0x1940],'Migration damaged roster'
    assert migrated[0x1f1c:0x1f30]==original[0x1f1c:0x1f30],'Migration damaged names'
    assert migrated[0x2b08:0x2b80]==original[0x2b08:0x2b80],'Migration damaged quest items'
    e.screenshot(OUT/'migration-loaded.png')
    # Test all sidecar bytes with AP/equipped encodings, including maximum127.
    extension=random.Random(0x3434).randbytes(816)
    e.set_memory(0x1b40,extension)
    e.set_memory(0x1940+460,b'\x05')
    e.set_memory(0x1e80,bytes([0,1])*12)
    expected[460]=5
    saved=save(e)
    e.screenshot(OUT/'extension-saved.png')
    assert saved!=seed,'Save menu did not update SRAM'
finally:e.close()
e=cold_load(ROM,saved)
try:
    loaded=e.memory()
    assert loaded[0x1940:0x1b40]==expected,'Expanded inventory failed native save/reload'
    assert loaded[0x1b40:0x1e70]==extension,'Human AP extension failed native save/reload'
    assert loaded[0x1e80:0x1e98]==bytes([0,1])*12,'Per-unit preference lost'
    assert loaded[0x80:0x1940]==original[0x80:0x1940],'Roster failed native save/reload'
    e.screenshot(OUT/'extension-cold-loaded.png')
finally:e.close()
assert SEED.read_bytes()==seed,'Original seed was modified'
report={'passed':True,'romSha1':hashlib.sha1(ROM.read_bytes()).hexdigest(),
        'nativeSaveSha1':hashlib.sha1(saved).hexdigest(),
        'checks':['Normal gameplay load migrates original inventory exactly once',
                  'Native game save and cold load retain all816 extra AP bytes',
                  'Item460 count and all24 potion preferences survive native save/load',
                  'Roster, names, quest items and original seed are preserved'],
        'limitations':['Suspend branch not yet exercised by a real battle suspend',
                       'Inventory UI and AP learning hooks are not installed in this test-only ROM']}
(OUT/'storage-in-game.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
