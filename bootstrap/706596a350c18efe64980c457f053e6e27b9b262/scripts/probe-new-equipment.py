"""Disposable native UI fixture for the allocated teaching equipment."""
import hashlib, importlib.util, json, pathlib, struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('harness',ROOT/'scripts/emulator-test.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
OUT=ROOT/'build/expansion/probes';ROM=OUT/'content-inventory.gba'
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
def tap(e,key,wait=40):e.run(8,key);e.run(wait)
e=h.Emulator(ROM)
try:
    e.set_memory(0,(ROOT/'build/test-lab/early-town.sav').read_bytes(),0);e.run(3600)
    tap(e,8,180);tap(e,256,60);tap(e,256,60);tap(e,256,180)
    assert e.memory()[0x1e70:0x1e78]==b'FFTAEXP1'
    for item in registry['items']:e.set_memory(0x1940+item['romItemId'],b'\x01')
    # Disposable fixture: Marche starts with a shield. A two-handed axe must
    # be rejected until it is removed; this path tests the empty offhand.
    e.set_memory(0x80+0x2e,b'\x00\x00')
    e.save(OUT/'new-equipment-world.state')
    tap(e,8);tap(e,256,120);tap(e,8,120);tap(e,128,120)
    ram=e.memory();count=struct.unpack_from('<I',ram,0x3c000)[0]
    ids=[struct.unpack_from('<I',ram,0x3c234+20*i)[0] for i in range(count)]
    assert len(ids)==90 and set(range(376,461)).issubset(ids)
    # The first five entries are the native starting weapons.
    for _ in range(5):tap(e,32)
    e.screenshot(OUT/'new-equipment-list.png')
    e.save(OUT/'new-equipment-list.state')
    # Return to world, then primary weapon equipment selector.
    e.load(OUT/'new-equipment-world.state')
    tap(e,8);tap(e,256,120);tap(e,256,120);tap(e,256,120);tap(e,256,120)
    tap(e,128,120)
    ram=e.memory();count=struct.unpack_from('<I',ram,0x3c000)[0]
    ids=[struct.unpack_from('<I',ram,0x3c234+20*i)[0] for i in range(count)]
    axe=next(a['romItemId'] for a in registry['items'] if a['name']=='Recruit Axe')
    e.screenshot(OUT/'new-equipment-select.png');e.save(OUT/'new-equipment-select.state')
    assert axe in ids,(count,ids)
    index=ids.index(axe)
    forbidden=struct.unpack_from('<H',ram,0x3c232+20*index)[0]
    assert forbidden==0,'Axe remains disabled with empty offhand'
    for _ in range(index):tap(e,32,12)
    e.screenshot(OUT/'new-equipment-axe-selected.png')
    tap(e,256,120)
    assert struct.unpack_from('<H',e.memory(),0x80+0x2a)[0]==axe
    e.screenshot(OUT/'new-equipment-axe-equipped.png')
    print(json.dumps({'romSha1':hashlib.sha1(ROM.read_bytes()).hexdigest(),'count':count,'axe':axe,'index':index,'forbidden':forbidden}))
    e.screenshot(OUT/'new-equipment-select.png');e.save(OUT/'new-equipment-select.state')
finally:e.close()
