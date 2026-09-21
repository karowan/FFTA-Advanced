"""Actual native shop navigation, tail ownership and sale beyond row255."""
import hashlib, json, pathlib, runpy, struct
from PIL import Image

ROOT=pathlib.Path(__file__).resolve().parents[1]
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
OUT=ROOT/'build/expansion/probes/shop-wide'
OUT.mkdir(parents=True,exist_ok=True)
ROM=OUT/'frozen.gba'
ROM.write_bytes((ROOT/'build/expansion/probes/content-inventory.gba').read_bytes())
SEED=(ROOT/'build/test-lab/early-town.sav').read_bytes()

# Measure the actual game font. Native row padding wraps to a huge clear if
# any label exceeds eleven tiles, even when its character count looks short.
arm=runpy.run_path(str(ROOT/'scripts/test-battle-inventory.py'))
machine=arm['ARM'](arm['native_iwram']());machine.put(0x08000000,ROM.read_bytes())
table=machine.r32(0x0806e774);names=machine.r32(0x0806e770)
widths=[]
for item in range(1,461):
    pointer=machine.r32(names+machine.r16(table+item*32)*4)
    width=machine.call(0x080161bc,pointer);widths.append(width)
    assert width<=11,('Native shop name-padding underflow',item,width)

def tap(e,key,wait=24):e.run(8,key);e.run(wait)
def word(ram,offset):return struct.unpack_from('<H',ram,offset)[0]
def dword(ram,offset):return struct.unpack_from('<I',ram,offset)[0]
def cold(seed):
    e=h['Emulator'](ROM);e.set_memory(0,seed,0);e.run(3600)
    for key,wait in [(8,180),(256,60),(256,60),(256,180)]:tap(e,key,wait)
    return e
def state(e,label):
    ram=e.memory();base=dword(ram,0xf428)-0x02000000
    e.screenshot(OUT/(label+'.png'))
    return {'label':label,'base':base,'count':word(ram,base+0xa338),
            'index':word(ram,base+0xa33a),'item':word(ram,base+0x44ec),
            'scroll':word(ram,base+0x14da),
            'savedScroll':[word(ram,base+0xa33c+2*i) for i in range(6)]}

e=cold(SEED);samples=[]
try:
    # Native shop -> Sell -> weapon tab, with a disposable all-owned fixture.
    e.set_memory(0x1941,bytes([2])*460);e.set_memory(0x1940+460,b'\x01')
    expected=bytearray(e.memory()[0x1940:0x1b40])
    before_ap=e.memory()[0x1b40:0x1e70]
    for key,wait in [(256,240),(32,40),(256,180),(256,120),(1,120),(32,40),(256,120),(128,60),(128,120)]:tap(e,key,wait)
    first=state(e,'first');samples.append(first)
    assert first['count']==337,first
    assert first['index']==0 and first['item']==1,first
    base=first['base'];ram=e.memory()
    ids=[word(ram,base+0x9c08+i*4) for i in range(337)]
    assert ids==list(range(1,253))+list(range(376,461))
    guard=b'\xDA'*16;view_guard=b'\xDB'*0xbc
    e.set_memory(base+0xa350,guard);e.set_memory(0x3ff44,view_guard)
    header=Image.open(OUT/'first.png').crop((24,0,640,48)).tobytes()
    for index in range(1,337):
        tap(e,32,16)
        if index in (254,255,256,336):
            sample=state(e,'row-'+str(index));samples.append(sample)
            assert sample['index']==index and sample['item']==ids[index],sample
            rendered=Image.open(OUT/('row-'+str(index)+'.png')).crop((24,0,640,48)).tobytes()
            # The native scroll arrow blinks; disappearing panels do not.
            assert sum(a!=b for a,b in zip(header,rendered))<2000,('Shop background damaged',index)
    tap(e,128,100);tap(e,64,100)
    returned=state(e,'tab-return');samples.append(returned)
    assert returned['index']==336 and returned['item']==460,returned
    tap(e,512,100);tap(e,512,100)
    help_return=state(e,'info-return');samples.append(help_return)
    assert help_return['index']==336 and help_return['item']==460,help_return
    before_gil=dword(e.memory(),0x1f64)
    tap(e,256,80);tap(e,256,80);tap(e,256,180)
    sold=state(e,'sold');samples.append(sold)
    ram=e.memory();expected[460]=0
    assert ram[0x1940:0x1b40]==expected,'Sale changed the wrong item or amount'
    assert dword(ram,0x1f64)==before_gil+3250,'Titan Axe sale price changed'
    assert ram[0x1b40:0x1e70]==before_ap,'Shop changed AP'
    assert ram[base+0xa350:base+0xa360]==guard,'Shop metadata overflow'
    assert ram[0x3ff44:0x40000]==view_guard,'Compatibility view overflow'
    rebuilt=state(e,'last-sale-rebuild');samples.append(rebuilt)
    assert rebuilt['count']==336 and rebuilt['index']<=335,rebuilt
    for _ in range(5):tap(e,1,120)
    e.screenshot(OUT/'world-before-save.png')
    for key,wait in [(8,40),(16,40),(256,40),(256,60),(256,60),(64,20),(256,300)]:tap(e,key,wait)
    saved=e.memory(0);assert saved!=SEED,'Native save was not reached'
    after_gil=dword(e.memory(),0x1f64)
finally:e.close()
e=cold(saved)
try:
    ram=e.memory();e.screenshot(OUT/'cold-loaded.png')
    assert ram[0x1940:0x1b40]==expected,'Native cold load lost sale or other inventory'
    assert ram[0x1b40:0x1e70]==before_ap,'Native cold load changed AP'
    assert dword(ram,0x1f64)==after_gil,'Native cold load lost sale gil'
finally:e.close()
report={'passed':True,'romSha1':hashlib.sha1(ROM.read_bytes()).hexdigest(),'samples':samples,
        'maximumNativeNameTiles':max(widths),
        'checks':['All337 owned weapons listed in native Sell UI','Rows254/255/256/336 select correct item',
                  'Tab change and Info preserve wide saved scroll','Native last-row sale removes item460 only',
                  'List clamps after selling final owned item','Shop/view guards and AP preserved',
                  'Native save and cold-load retain full inventory and sale gil']}
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
