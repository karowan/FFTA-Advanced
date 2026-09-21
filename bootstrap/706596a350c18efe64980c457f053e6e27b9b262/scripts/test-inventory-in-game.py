"""Real native shop -> equipment -> save/reload flow on the menu probe."""
import hashlib, importlib.util, json, pathlib, struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('harness',ROOT/'scripts/emulator-test.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
OUT=ROOT/'build/expansion/probes'
ROM=OUT/'inventory-menus.gba'
SEED=ROOT/'build/test-lab/early-town.sav'
def tap(e,key,wait=40):e.run(8,key);e.run(wait)
def cold(seed):
    e=h.Emulator(ROM);e.set_memory(0,seed,0);e.run(3600)
    tap(e,8,180);tap(e,256,60);tap(e,256,60);tap(e,256,180)
    return e
def photo(e,name):e.screenshot(OUT/(name+'.png'))
seed=SEED.read_bytes();checks=[]
e=cold(seed)
try:
    initial=e.memory()
    extension=bytes((i*31+7)%256 for i in range(816))
    e.set_memory(0x1b40,extension)
    # Party and Item List, including the old sorting input: it must not invoke
    # native four-byte inventory writes against compressed state.
    tap(e,8);tap(e,256,120);tap(e,8,120)
    photo(e,'test-items-armor')
    before=e.memory()[0x1940:0x1f1c]
    tap(e,8,60)
    assert e.memory()[0x1940:0x1f1c]==before,'Old sort path damaged persistent storage'
    tap(e,128,120)
    ram=e.memory();count=struct.unpack_from('<I',ram,0x3c000)[0]
    ids=[struct.unpack_from('<I',ram,0x3c230+20*i+4)[0] for i in range(count)]
    assert count==5 and ids[0]==1,'Weapon list did not contain native starting weapons'
    photo(e,'test-items-weapons')
    checks.append('Native item menus render original armor/weapons; old sort input preserves storage')
    tap(e,1,60);tap(e,1,80)
    # Native Sprohm shop. Buy Bronze Helm for500 gil.
    tap(e,256,240);tap(e,32);tap(e,256,180);tap(e,256,120)
    photo(e,'test-shop-buy')
    tap(e,256,80);tap(e,256,120);tap(e,256,180)
    ram=e.memory()
    assert ram[0x1940+265]==1 and struct.unpack_from('<I',ram,0x1f64)[0]==4500
    tap(e,256,120);tap(e,1,120)
    e.save(OUT/'purchase-checkpoint.state')
    checks.append('Native shop purchase grants one Bronze Helm and charges exactly500 gil')
    # Independent sale branch from the purchased checkpoint.
    tap(e,32);tap(e,256,120)
    photo(e,'test-shop-sell')
    tap(e,256,80);tap(e,256,80);tap(e,256,180)
    ram=e.memory()
    assert ram[0x1940+265]==0 and struct.unpack_from('<I',ram,0x1f64)[0]==4750
    assert ram[0x1b40:0x1e70]==extension
    checks.append('Native sale removes the owned copy and refunds exactly250 gil')
    # Return to the actual purchased copy for equipment and save persistence.
    e.load(OUT/'purchase-checkpoint.state')
    tap(e,32);tap(e,32);tap(e,256,120);tap(e,1,120)
    tap(e,8);tap(e,256,120);tap(e,256,120);tap(e,256,120)
    tap(e,32,30);tap(e,32,30);tap(e,32,30);tap(e,256,120)
    photo(e,'test-equip-selection')
    tap(e,256,120)
    ram=e.memory()
    assert struct.unpack_from('<H',ram,0x80+0x30)[0]==265,'Purchased helmet was not equipped'
    assert ram[0x1940+265]==1,'Equipping consumed the total-owned copy'
    assert ram[0x1b40:0x1e70]==extension
    photo(e,'test-helmet-equipped')
    tap(e,1,60);tap(e,1,60);tap(e,1,80)
    tap(e,8);tap(e,16);tap(e,256);tap(e,256,60);tap(e,256,60)
    tap(e,64,20);tap(e,256,300)
    saved=e.memory(0)
    assert saved!=seed
    checks.append('Native equipment menu equips the purchased helmet without reducing owned quantity')
finally:e.close()
e=cold(saved)
try:
    ram=e.memory()
    assert struct.unpack_from('<H',ram,0x80+0x30)[0]==265
    assert ram[0x1940+265]==1 and struct.unpack_from('<I',ram,0x1f64)[0]==4500
    assert ram[0x1b40:0x1e70]==extension
    expected=bytearray(initial[0x1940:0x1b40]);expected[265]=1
    assert ram[0x1940:0x1b40]==expected,'Unrelated inventory changed during shop/equip/save'
    photo(e,'test-equipment-cold-loaded')
    checks.append('Cold native load restores purchased/equipped gear, gil and all816 extra AP bytes')
finally:e.close()
assert SEED.read_bytes()==seed
report={'passed':True,'romSha1':hashlib.sha1(ROM.read_bytes()).hexdigest(),
        'checks':checks,'originalSeedUnchanged':True,
        'limitations':['Original item sample; all85 new weapons and shop gates remain to integrate',
                       'Battle Item/Throw/Draw Weapon/feeding and special-stock coverage remains',
                       'Inventory sorting hint still needs UI adjustment']}
(OUT/'inventory-in-game.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
