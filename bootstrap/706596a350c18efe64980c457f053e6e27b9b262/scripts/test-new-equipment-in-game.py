"""Actual normal shop purchase/equipment/save of approved new opening stock."""
import hashlib, importlib.util, json, pathlib, struct, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('harness',ROOT/'scripts/emulator-test.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
OUT=ROOT/'build/expansion/probes'
ABILITIES='--abilities' in sys.argv
ROM=OUT/('ability-core.gba' if ABILITIES else 'content-inventory.gba')
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
axe=next(item for item in registry['items'] if item['romItemId']==453)
lesson=next(owner['abilityIndex'] for owner in axe['teaching'] if owner['jobId']==2)
ap_offset=0x1b40+lesson-144
SEED=ROOT/'build/test-lab/early-town.sav'
def tap(e,key,wait=40):e.run(8,key);e.run(wait)
def cold(seed):
    e=h.Emulator(ROM);e.set_memory(0,seed,0);e.run(3600)
    tap(e,8,180);tap(e,256,60);tap(e,256,60);tap(e,256,180)
    return e
seed=SEED.read_bytes();e=cold(seed);checks=[]
try:
    initial=e.memory()
    # Test fixture leaves the offhand empty; separate native legality tests
    # require rejection with a shield in either order, including Monkey Grip.
    e.set_memory(0x80+0x2e,b'\x00\x00')
    tap(e,256,240);tap(e,32);tap(e,256,180);tap(e,256,120)
    tap(e,128,100);tap(e,128,100)
    ram=e.memory()
    context=struct.unpack_from('<I',ram,0xf428)[0]-0x02000000
    count=struct.unpack_from('<H',ram,context+0xa338)[0]
    ids=[struct.unpack_from('<H',ram,context+0x9c08+i*4)[0] for i in range(count)]
    e.screenshot(OUT/'test-new-shop-stock.png')
    assert ram[context+0x4bfb]==3
    assert [item for item in ids if item>=376]==[384,385,392,393,453,454]
    index=ids.index(453)
    assert index<50,(index,ids[:50])
    # New higher-stage Soldier/Viking weapons must not appear in opening stock.
    assert 455 not in ids
    for _ in range(index):tap(e,32,20)
    e.screenshot(OUT/'test-new-shop-selected.png')
    tap(e,256,80);tap(e,256,120);tap(e,256,180)
    ram=e.memory()
    assert ram[0x1940+453]==1,'Native checkout did not grant Recruit Axe'
    assert struct.unpack_from('<I',ram,0x1f64)[0]==4700,'Opening axe price should be300'
    checks.append('Normal Sprohm opening shipment sells Recruit Axe453 for300 gil')
    tap(e,256,120);tap(e,1,120)
    tap(e,32);tap(e,32);tap(e,256,120);tap(e,1,120)
    tap(e,8);tap(e,256,120);tap(e,256,120);tap(e,256,120);tap(e,256,120)
    tap(e,128,120)
    ram=e.memory();count=struct.unpack_from('<I',ram,0x3c000)[0]
    equip_ids=[struct.unpack_from('<I',ram,0x3c234+i*20)[0] for i in range(count)]
    index=equip_ids.index(453)
    assert struct.unpack_from('<H',ram,0x3c232+index*20)[0]==0
    for _ in range(index):tap(e,32,20)
    tap(e,256,120)
    assert struct.unpack_from('<H',e.memory(),0x80+0x2a)[0]==453
    if ABILITIES:
        assert e.memory()[ap_offset]==128,'Equipping Recruit Axe must grant its Human extension lesson'
        checks.append('Native equipment teaching grants the new Soldier lesson in its sidecar')
    e.screenshot(OUT/'test-new-axe-equipped.png')
    checks.append('Native equipment menu equips purchased axe with empty offhand')
    tap(e,1,60);tap(e,1,60);tap(e,1,80)
    tap(e,8);tap(e,16);tap(e,256);tap(e,256,60);tap(e,256,60);tap(e,64,20);tap(e,256,300)
    saved=e.memory(0);assert saved!=seed
finally:e.close()
e=cold(saved)
try:
    ram=e.memory()
    assert struct.unpack_from('<H',ram,0x80+0x2a)[0]==453
    assert ram[0x1940+453]==1 and struct.unpack_from('<I',ram,0x1f64)[0]==4700
    expected=bytearray(initial[0x1940:0x1b40]);expected[453]=1
    assert ram[0x1940:0x1b40]==expected
    expected_ap=bytearray(initial[0x1b40:0x1e70])
    if ABILITIES:expected_ap[ap_offset-0x1b40]=128
    assert ram[0x1b40:0x1e70]==expected_ap
    e.screenshot(OUT/'test-new-axe-cold-loaded.png')
    checks.append('Native save/coldload preserves purchased equipped axe, gil and allotherinventory/AP')
finally:e.close()
if ABILITIES:
    cost=next(lesson['ap']//10 for lesson in registry['lessons'] if lesson['id']=='SLD-AX-A1')
    original_weapon=struct.unpack_from('<H',initial,0x80+0x2a)[0]
    for progress in (0,cost-1,cost):
        e=cold(saved)
        try:
            # Isolate native equipment-removal behavior at the three AP
            # thresholds. Results earning is tested at its native hook.
            e.set_memory(ap_offset,bytes((128|progress,)))
            tap(e,8);tap(e,256,120);tap(e,256,120);tap(e,256,120);tap(e,256,120)
            tap(e,128,120)
            ram=e.memory();count=struct.unpack_from('<I',ram,0x3c000)[0]
            ids=[struct.unpack_from('<I',ram,0x3c234+i*20)[0] for i in range(count)]
            for _ in range(ids.index(original_weapon)):tap(e,32,20)
            tap(e,256,120)
            ram=e.memory()
            assert struct.unpack_from('<H',ram,0x80+0x2a)[0]==original_weapon
            assert ram[ap_offset]==progress+(128 if progress>=cost else 0),('Removal AP',progress,ram[ap_offset])
            checks.append(f'Native weapon removal preserves {progress*10}AP and '+('mastered usability' if progress>=cost else 'removes equipment-only usability'))
        finally:e.close()
assert SEED.read_bytes()==seed
report={'passed':True,'romSha1':hashlib.sha1(ROM.read_bytes()).hexdigest(),'checks':checks,
        'fixture':'Original early-town native seed with Marche shield removed in disposable RAM',
        'remaining':['Axe artwork/battle animations','Equipment AP learning/commands/effect integration',
                     'Full story-gate native town visit coverage']}
(OUT/('ability-equipment-in-game.json' if ABILITIES else 'new-equipment-in-game.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
