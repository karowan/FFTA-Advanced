"""Two paid recoveries in one deterministic player-input timeline.

Initial fixture supplies original postgame/source eligibility, 50000 gil and
level50 Ford. Thereafter only controller input changes gameplay: first paid
pub acceptance, travel/collection, shop sale, cooldown, second payment/return,
and normal Save followed by a fresh Continue. No timer/outcome/reward writes.
"""
import ast
import atexit
import ctypes
import datetime
import hashlib
import json
import pathlib
import runpy
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
meta = json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
rom = pathlib.Path(meta['path']).read_bytes()
sha = lambda b: hashlib.sha1(b).hexdigest()
assert sha(rom) == meta['romSha1']
base = pathlib.Path(meta['path']).parent
OUT = base/('paid-recovery-cycle-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
OUT.mkdir()
private = OUT/'fixture.gba'; private.write_bytes(rom)
latest = base/'paid-recovery-cycle-latest.json'
seedpath = ROOT/'build/test-lab/early-town.sav'
seed = seedpath.read_bytes()
RETURN, STACK = 0x08000100, 0x03006800
source = (ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000', 'count=3000000')
tree = ast.parse(source)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ARM'], type_ignores=[]), '<native ARM>', 'exec'))
Emulator = runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
checks, observations, inputs, completed = [], [], [], []
values, retained = {}, {}
e = None


def word(ram, at): return struct.unpack_from('<I', ram, at)[0]
def half(ram, at): return struct.unpack_from('<H', ram, at)[0]
def gil(): return word(e.memory(), 0x1f64)
def item_count(): return e.memory()[0x1940+26]
def record():
    ram = e.memory()
    return next((ram[p:p+16] for p in range(0x21c8, 0x25c8, 16)
                 if (ram[p] | ((ram[p+1] & 3) << 8)) == 471), None)


def check(ok, label):
    assert ok, label
    checks.append(label)


def capture(label):
    ram = e.memory()
    e.save(OUT/(label+'.state')); e.screenshot(OUT/(label+'.png'))
    (OUT/(label+'.ram')).write_bytes(ram)
    row = dict(label=label, directory=str(OUT), gil=gil(), gear=item_count(),
               assigned=half(ram, 0x2a6), cached=record().hex() if record() else None,
               stateSha1=sha((OUT/(label+'.state')).read_bytes()), ramSha1=sha(ram))
    observations.append(row)
    return row


def report(passed=False, capture_failure=True):
    if not passed and capture_failure and e is not None:
        capture('failure')
    r = dict(passed=passed, romSha1=meta['romSha1'], seedSha1=sha(seed), assertions=len(checks),
             checks=checks, observations=observations, inputs=inputs, completed=completed,
             values=values, retained=retained, scope=__doc__)
    (OUT/'report.json').write_text(json.dumps(r, indent=2)+'\n', encoding='utf-8')
    latest.write_text(json.dumps(dict(report=str(OUT/'report.json')), indent=2)+'\n')
    return r


atexit.register(report)


def tap(key, wait=180):
    inputs.append([8, key, wait]); e.run(8, key); e.run(wait)


def native():
    m = ARM(rom, ctypes.string_at(*e.maps[0x03000000]))
    m.put(0x02000000, e.memory())
    return m


def world():
    for _ in range(4): tap(1)


def travel(area, label):
    m = native(); tile = m.call(0x08036330, area)
    check(0 < tile < 32, label+': placed destination')
    target = (m.call(0x08035a20, tile-1)+6, m.call(0x08035a44, tile-1)+4)
    route = []
    for _ in range(600):
        x, y = struct.unpack_from('<HH', e.memory(), 0x2c16)
        if abs(x-target[0]) <= 2 and abs(y-target[1]) <= 2: break
        key = (128 if x < target[0] else 64) if abs(x-target[0]) > 2 else (32 if y < target[1] else 16)
        e.run(1, key); route.append([x, y, key])
    else: raise AssertionError(label+': world cursor exceeded declared bound')
    inputs.append(dict(label=label, area=area, route=route))
    e.run(30); tap(256, 1200); capture(label)


def prepare():
    e.set_memory(0, seed, 0); e.run(3600)
    for key, wait in ((8, 180), (256, 60), (256, 60), (256, 180)): tap(key, wait)
    ram = e.memory()
    for bit in (54, 22+0x2ff):
        at = 0x1f70+(bit >> 3); e.set_memory(at, bytes((ram[at] | (1 << (bit & 7)),)))
    e.set_memory(0x1f64, struct.pack('<I', 50000))
    e.set_memory(0x1940+26, b'\0')
    e.set_memory(0x2b08, bytes(256))
    e.set_memory(0x299, bytes((50,)))
    values['initialGil'] = gil()


def accept(number):
    prefix = f'paid{number}'
    for key, wait in ((256, 240), (256, 180), (256, 120), (256, 120)): tap(key, wait)
    ram = e.memory(); ctx = word(ram, 0xf448)-0x02000000
    check(0 <= ctx < 0x3e000, prefix+': native pub context')
    count = ram[ctx+0x11a9]
    pointers = [word(ram, ctx+0x11ac+i*4)-0x02000000 for i in range(count)]
    check(0 < count <= 16 and all(0x21c8 <= p < 0x25c8 for p in pointers), prefix+': valid native list')
    ids = [ram[p] | ((ram[p+1] & 3) << 8) for p in pointers]
    check(471 in ids, prefix+': real recovery offer')
    for _ in range(ids.index(471)): tap(32)
    before = gil(); tap(256); capture(prefix+'-details')
    for key in (256, 256, 128, 128, 256): tap(key)
    ram = e.memory(); fee = half(ram, ctx+0x11a4)
    check(fee == 15000, prefix+': displayed Cyril fee')
    check(word(ram, ctx+0x1454) == 0x02000290, prefix+': actual Ford selection')
    for page in range(12):
        tap(256); capture(prefix+f'-confirm-{page}')
        if half(e.memory(), 0x2a6) == 471 and half(e.memory(), 0x2b8) & 4 and gil() == before-fee: break
    check(half(e.memory(), 0x2a6) == 471 and half(e.memory(), 0x2b8) & 4,
          prefix+': selected member actually dispatched')
    check(gil() == before-fee, prefix+': displayed fee charged exactly once')
    values[prefix+'Before'] = before; values[prefix+'After'] = gil()
    check(item_count() == 0, prefix+': no early reward')
    world()


def collect(number):
    prefix = f'return{number}'
    before = e.memory(); before_gil = gil()
    initial = record()
    check(initial is not None and ((initial[1] >> 2) | ((initial[2] & 3) << 6)) == 20,
          prefix+': original twenty-day accepted duration')
    elapsed = 0
    for leg in range(1, 13):
        travel(8 if leg % 2 else 2, prefix+f'-travel-{leg}')
        rec = record(); check(rec is not None, prefix+': dispatch retained during travel')
        days = (rec[1] >> 2) | ((rec[2] & 3) << 6)
        check(days < 20-elapsed, prefix+': travel advances native days')
        elapsed = 20-days
        if not days: break
        tap(1); tap(1)
    check(elapsed == 20, prefix+': full native duration elapsed')
    for page in range(10):
        tap(256, 240); capture(prefix+f'-reward-{page}')
        if item_count() == 1 and half(e.memory(), 0x2a6) == 0: break
    after = e.memory()
    check(item_count() == 1, prefix+': exactly one native reward collected')
    expected = bytearray(before[0x1940:0x1b40]); expected[26] = 1
    check(after[0x1940:0x1b40] == expected, prefix+': other equipment counts preserved')
    check(half(after, 0x2a6) == 0 and not half(after, 0x2b8) & 4, prefix+': Ford returned')
    check(gil() == before_gil, prefix+': no additional charge')
    check(all(((after[0x1f70+((mid+0x2ff) >> 3)] ^ before[0x1f70+((mid+0x2ff) >> 3)]) &
               (1 << ((mid+0x2ff) & 7))) == 0 for mid in range(512)), prefix+': no borrowed mission receipts')
    check(native().call(meta['symbols']['ffta_recovery_needed'], 471) == 0, prefix+': held copy suppresses recovery')
    world()


def sell():
    # Return to Cyril, then use the original Sell weapon list and quantity UI.
    travel(2, 'sell-travel-cyril'); world()
    for key, wait in ((256,240),(32,40),(256,180),(256,120),(1,120),(32,40),(256,120)):
        tap(key, wait)
    ram=e.memory(); ctx=word(ram, 0xf428)-0x02000000
    check(0 <= ctx < 0x35000, 'Native shop context exists')
    # Empty categories are skipped by the native UI. Select from its current
    # list instead of assuming that two Right presses always mean weapons.
    for tab in range(6):
        ram=e.memory();count=half(ram,ctx+0xa338)
        check(count < 461, 'Native Sell list is bounded')
        ids=[half(ram,ctx+0x9c08+i*4) for i in range(count)]
        if 26 in ids:break
        tap(128,120)
    check(26 in ids, 'Recovered Materia Blade is in actual Sell list')
    for _ in range(ids.index(26)): tap(32,40)
    check(half(e.memory(),ctx+0x44ec)==26, 'Actual Sell selection is Materia Blade')
    before=e.memory(); before_gil=gil()
    for _ in range(3): tap(256,180)
    after=e.memory(); capture('sold-first-reward')
    expected=bytearray(before[0x1940:0x1b40]); expected[26]=0
    check(after[0x1940:0x1b40]==expected, 'Native sale removes only the recovered copy')
    check(gil()>before_gil, 'Native sale pays gil')
    values['saleGil']=gil()-before_gil
    check(native().call(meta['symbols']['ffta_recovery_needed'],471)==1, 'Sold copy requalifies for paid recovery')
    world()


def cooldown():
    # Shop exit has an A-confirmed farewell after the four menu cancellations.
    tap(256, 240); world()
    for leg in range(1,21):
        rec=record()
        if rec is None or rec[2]&0x1c in (4,8): break
        check(rec[2]&0x1c==12, 'Unfinished repeat has native cooldown')
        travel(8 if leg%2 else 2, f'cooldown-travel-{leg}')
        world()
    else: raise AssertionError('Native recovery cooldown exceeds declared travel bound')
    # Ensure the same known pub/town/menu origin for the second actual payment.
    travel(2, 'second-pub-cyril'); world()
    check(item_count()==0, 'Cooldown grants no free replacement')


def cold():
    global e
    saved=e.memory()
    for key,wait in ((8,40),(16,40),(256,40),(256,60),(256,60),(64,20),(256,300)):tap(key,wait)
    sram=e.memory(0);(OUT/'twice-recovered.srm').write_bytes(sram)
    values['finalSramSha1']=sha(sram)
    e.close(); e=Emulator(private); e.set_memory(0,sram,0);e.run(3600)
    for key,wait in ((8,180),(256,60),(256,60),(256,180)):tap(key,wait)
    after=e.memory()
    for name,lo,hi in (('roster/AP',0x80,0x1940),('inventory/AP',0x1940,0x1f40),
                       ('gil',0x1f64,0x1f68),('quest items/gift receipts',0x2b08,0x2c10)):
        check(after[lo:hi]==saved[lo:hi], 'Cold Continue retains exact '+name)
    check(item_count()==1 and native().call(meta['symbols']['ffta_recovery_needed'],471)==0,
          'Second collected copy suppresses recovery after cold Continue')
    check(gil()==50000-30000+values['saleGil'], 'Exactly two fees survive both returns and cold Continue')
    check(seedpath.read_bytes()==seed, 'Original seed remains unchanged')


stages=[('prepared',prepare),('paid1',lambda:accept(1)),('returned1',lambda:collect(1)),
        ('sold',sell),('cooled',cooldown),('paid2',lambda:accept(2)),
        ('returned2',lambda:collect(2)),('cold',cold)]
try:
    e=Emulator(private)
    if '--resume' in sys.argv:
        prior_path=pathlib.Path(json.loads(latest.read_text())['report'])
        prior_bytes=prior_path.read_bytes();prior=json.loads(prior_bytes)
        assert prior['romSha1']==meta['romSha1'] and prior['seedSha1']==sha(seed)
        checks.extend(prior['checks']);completed.extend(prior['completed']);values.update(prior['values'])
        retained.update(report=str(prior_path), reportSha1=sha(prior_bytes), completed=list(completed))
        anchor=next(r for r in reversed(prior['observations']) if r['label']==completed[-1])
        observations.append(anchor)
        folder=pathlib.Path(anchor['directory'])
        for ext,key in (('state','stateSha1'),('ram','ramSha1')):
            assert sha((folder/(anchor['label']+'.'+ext)).read_bytes())==anchor[key]
        e.load(folder/(anchor['label']+'.state'));e.run(1)
    for label,fn in stages:
        if label in completed:continue
        fn(); capture(label);completed.append(label)
        report(False, capture_failure=False)
finally:
    if e is not None:
        if len(completed)!=len(stages):report(False)
        e.close();e=None
report(True);atexit.unregister(report)
print(json.dumps(dict(passed=True,assertions=len(checks),completed=completed,values=values,report=str(OUT/'report.json'))))
