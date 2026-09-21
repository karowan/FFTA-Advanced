"""Original Caravan Guard: native acceptance,20 travel days and both rewards.

Fixture uses original mission9 progress, a level50 generic member and the Cup
from verified recovery playback. Native construction/assignment owns quality
and dispatch counters; the required Cup binding is an explicit fixture input.
Real world inputs own the full20-day return, reward UI and consumption. No
result injection, timer writes, relocated mission or substitute battle.
"""
import atexit
import ctypes
import hashlib
import json
import pathlib
import runpy
import struct

ROOT = pathlib.Path(__file__).resolve().parents[1]
meta = json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text(encoding='utf-8'))
rom = pathlib.Path(meta['path']).read_bytes(); assert hashlib.sha1(rom).hexdigest() == meta['romSha1']
source = pathlib.Path(meta['path']).parent/'recovery-return'
prior = json.loads((source/'report.json').read_text(encoding='utf-8'))
assert prior['passed'] and prior['romSha1'] == meta['romSha1']
anchor = next(row for row in prior['observations'] if row.get('label') == '99-finished')
assert hashlib.sha1((source/'99-finished.state').read_bytes()).hexdigest() == anchor['stateSha1']
OUT = pathlib.Path(meta['path']).parent/'caravan-return'; OUT.mkdir(exist_ok=True)
ROM = OUT/'fixture.gba'; ROM.write_bytes(rom)
h = runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
a = runpy.run_path(str(ROOT/'scripts/test-battle-inventory.py'))
checks = []; observations = []; inputs = []

def check(ok, label):
    assert ok, label
    checks.append(label)

def report(passed=False):
    r = dict(passed=passed, romSha1=meta['romSha1'], assertions=len(checks), checks=checks,
             observations=observations, inputs=inputs, sourceStateSha1=anchor['stateSha1'], scope=__doc__)
    (OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    return r

atexit.register(report)
def tap(e,key,wait=240):
    inputs.append([8,key,wait]); e.run(8,key); e.run(wait)

def cached(ram):
    return next((ram[at:at+16] for at in range(0x21c8,0x25c8,16)
                 if (ram[at]|((ram[at+1]&3)<<8)) == 183), None)

def capture(e,label):
    ram = e.memory(); row = cached(ram)
    e.save(OUT/(label+'.state')); e.screenshot(OUT/(label+'.png'))
    (OUT/(label+'.ram')).write_bytes(ram)
    observations.append(dict(label=label, cached=row.hex() if row else None,
        days=((row[1]>>2)|((row[2]&3)<<6)) if row else None,
        assigned=struct.unpack_from('<H',ram,0x2a6)[0], inventory=ram[0x2b08:0x2c08].hex(),
        stateSha1=hashlib.sha1((OUT/(label+'.state')).read_bytes()).hexdigest(),
        ramSha1=hashlib.sha1(ram).hexdigest()))
    return ram

e = h['Emulator'](ROM)
try:
    e.load(source/'99-finished.state'); e.run(1)
    ram = bytearray(e.memory()); check(list(ram[0x2b08:0x2c08:4]).count(4)==1,'Verified Cup available before dispatch')
    ram[0x21c8:0x28cc]=bytes(0x704)
    bit=9+0x2ff; ram[0x1f70+(bit>>3)] |= 1<<(bit&7)
    ram[0x299]=50  # Explicit level50 fixture, native job/stats/quality otherwise retained.
    slot = list(ram[0x2b08:0x2c08:4]).index(4); cup = 0x2b08+slot*4
    m=a['ARM'](ctypes.string_at(*e.maps[0x03000000])); m.put(0x08000000,rom); m.put(0x02000000,ram)
    m.call(0x080cfcd0,0)
    native=m.get(0x02000000,0x40000)
    at=next(at for at in range(0x21c8,0x25c8,16) if (native[at]|((native[at+1]&3)<<8))==183)
    check(struct.unpack_from('<HH',native,at+8)==(479,379),'Native constructor retains Musk plus Cup rewards')
    m.put(0x02000000+cup,struct.pack('<BBH',4,1,183))
    m.call(0x080d0b48,0x02000000+at,0x02000290,4,0)
    prepared=m.get(0x02000000,0x40000); accepted=cached(prepared)
    check(accepted is not None and accepted[2]&0x1c==0,'Native assignment accepts Caravan Guard')
    check((accepted[1]>>2)|((accepted[2]&3)<<6)==20,'Original dispatch duration is20 days')
    check(accepted[6]>0,'Declared level50 member succeeds under native quality/RNG calculation')
    for start,end in ((0x80,0x1940),(0x1f70,0x2030),(0x21c8,0x28cc),(0x2b08,0x2c08)):
        e.set_memory(start,prepared[start:end])
    capture(e,'00-accepted')
    elapsed=0
    for leg in range(1,13):
        area=8 if leg%2 else 2
        n=a['ARM'](ctypes.string_at(*e.maps[0x03000000])); n.put(0x08000000,rom); n.put(0x02000000,e.memory())
        tile=n.call(0x08036330,area); assert 0<tile<32
        target=(n.call(0x08035a20,tile-1)+6,n.call(0x08035a44,tile-1)+4); route=[]
        for _ in range(600):
            x,y=struct.unpack_from('<HH',e.memory(),0x2c16)
            if abs(x-target[0])<=2 and abs(y-target[1])<=2:break
            key=(128 if x<target[0] else 64) if abs(x-target[0])>2 else (32 if y<target[1] else 16)
            e.run(1,key);route.append([x,y,key])
        else:raise AssertionError(('World cursor bound',leg,area))
        observations.append(dict(leg=leg,area=area,route=route))
        e.run(30);tap(e,256,1200);ram=capture(e,f'travel-{leg:02}')
        row=cached(ram);check(row is not None,'Dispatch persists during travel')
        days=(row[1]>>2)|((row[2]&3)<<6)
        check(days<20-elapsed,'Ordinary travel advances native dispatch timer')
        elapsed=20-days
        check(ram[cup:cup+4]==struct.pack('<BBH',4,1,183),'Required Cup remains bound before reward confirmation')
        if not days:break
        # Town arrival opens its ordinary location menu; close it before the
        # next world-cursor journey. This does not advance dispatch time.
        tap(e,1,180);tap(e,1,180);capture(e,f'world-{leg:02}')
    check(elapsed==20,'Full20 native dispatch days elapsed')
    tap(e,256);capture(e,'return-list');tap(e,256);capture(e,'reward-screen')
    # Ordinary inventory first; then reuse this same real success screen for a
    # full-bag decision. Do not repeat20-day travel for the inventory variant.
    tap(e,256);ram=capture(e,'room-complete')
    check(struct.unpack_from('<H',ram,0x2a6)[0]==0,'Actual return releases assigned member')
    check(sorted(v for v in ram[0x2b08:0x2c08:4] if v)==[4,104],'Original Cup consumed; Musk and one returned Cup retained')
    check(all(ram[p+1:p+4]==bytes(3) for p in range(0x2b08,0x2c08,4) if ram[p]),'Collected rewards are unbound')
    bit=183+0x2ff
    check(ram[0x1f70+(bit>>3)]&(1<<(bit&7)),'Original Caravan Guard completion flag set')
    e.load(OUT/'reward-screen.state')
    stock=bytearray(b''.join(bytes((1,0,0,0)) for _ in range(64)))
    stock[:4]=struct.pack('<BBH',4,1,183);e.set_memory(0x2b08,bytes(stock));e.run(1)
    # Select Musk, swap inventory slot1; select Cup, swap slot2; confirm OK/Yes.
    keys=(256,256,256,32,256,32,256,32,32,256,32,256,64,256)
    for step,key in enumerate(keys,1):tap(e,key);ram=capture(e,f'full-{step:02}')
    check(struct.unpack_from('<H',ram,0x2a6)[0]==0,'Full-bag confirmation retires the actual dispatch')
    items=list(ram[0x2b08:0x2c08:4])
    check(items.count(4)==1 and items.count(104)==1 and items.count(1)==61 and items.count(0)==1,
          'Full bag keeps both selected rewards and consumes only the original bound Cup')
    check(all(ram[p+1:p+4]==bytes(3) for p in range(0x2b08,0x2c08,4) if ram[p]),'Full-bag retained items are unbound')
    check(ram[0x1f70+(bit>>3)]&(1<<(bit&7)),'Full-bag confirmation preserves original completion')
finally:e.close()
atexit.unregister(report);print(json.dumps(report(True),indent=2))
