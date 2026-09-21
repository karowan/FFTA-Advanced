"""Two native save slots, full roster data, and independent cold loads.

Declared initial world profiles carry distinct AP, inventory and preferences.
Only fixed controller input performs saving/loading. No flash page, checksum,
save descriptor or load result is constructed by this script.
"""
import datetime
import hashlib
import json
import pathlib
import runpy
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
meta = json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
ROM = pathlib.Path(meta['path'])
sha = lambda b: hashlib.sha1(b).hexdigest()
assert sha(ROM.read_bytes()) == meta['romSha1']
OUT = ROM.parent/('independent-save-slots-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
OUT.mkdir()
E = runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
seedpath = ROOT/'build/test-lab/early-town.sav'
seed = seedpath.read_bytes()
checks, inputs, captures, profiles = [], [], [], {}
retained = {}
e = None


def check(value, label):
    assert value, label
    checks.append(label)


def tap(key, wait=60):
    inputs.append([8, key, wait])
    e.run(8, key); e.run(wait)


def capture(label):
    e.save(OUT/(label+'.state'))
    if e.frame is not None: e.screenshot(OUT/(label+'.png'))
    ram = e.memory(); (OUT/(label+'.ram')).write_bytes(ram)
    captures.append(dict(label=label, ramSha1=sha(ram),
                         stateSha1=sha((OUT/(label+'.state')).read_bytes())))


def cold(saved, slot, selected=0):
    global e
    e = E(ROM); e.set_memory(0, saved, 0); e.run(3600)
    tap(8, 300); tap(256, 300); tap(256, 300)
    if slot != selected: tap(128, 120)
    capture('load-select-'+str(slot))
    tap(256, 300)


def owned(r):
    return {name: r[a:b].hex() for name, a, b in (
        ('roster', 0x80, 0x1940), ('inventory', 0x1940, 0x1b40),
        ('extendedAP', 0x1b40, 0x1e70), ('preferences', 0x1e80, 0x1e98),
        ('history', 0x1e79, 0x1e7a), ('gil', 0x1f64, 0x1f68))}


def profile(which):
    # Populate all24 exact roster slots with valid native generic records.
    # These are test inputs, not claims of campaign recruitment/earned AP.
    r = e.memory(); generic = r[0x188:0x290]
    for slot in range(24):
        unit = bytearray(generic)
        if slot == 0: unit = bytearray(r[0x80:0x188])
        unit[0x40:0x40+142] = bytes((slot*3+j+which*11) % 101 for j in range(142))
        e.set_memory(0x80+slot*264, bytes(unit))
    e.set_memory(0x1b40, bytes((i*13+which*17) % 101 for i in range(816)))
    e.set_memory(0x1e80, bytes((slot+which) % 3 for slot in range(24)))
    e.set_memory(0x1940+440, bytes([which+1]))
    e.set_memory(0x1f64, struct.pack('<I', 10000+which*1234))
    e.set_memory(0x3f410, bytes((i*19+which*23+1) & 255 for i in range(792)))
    check(all(e.memory()[0x84+slot*264] for slot in range(24)), 'Profile has24 occupied slots')
    profiles[str(which)] = owned(e.memory())
    capture('profile-'+str(which))


def save(slot):
    before = e.memory(); previous = e.memory(0)
    for key in (8, 16, 256, 256): tap(key)
    tap(128 if slot else 64)
    capture('save-select-'+str(slot))
    tap(256); tap(64, 20); tap(256, 300)
    capture('saved-'+str(slot))
    saved = e.memory(0)
    check(saved != previous, 'Slot'+str(slot)+' native flash transaction')
    check(owned(e.memory()) == owned(before), 'Slot'+str(slot)+' save preserves live profile')
    check(e.memory()[0x3f410:0x3f728] == before[0x3f410:0x3f728], 'Save preserves live transient bank')
    (OUT/('slot-'+str(slot)+'.sav')).write_bytes(saved)
    return saved


failure = None
try:
    cold_only = '--resume-cold' in sys.argv
    if cold_only:
        sources = sorted(ROM.parent.glob('independent-save-slots-*/report.json'), reverse=True)
        source = next(p for p in sources if 'Slot1 native flash transaction' in json.loads(p.read_text())['checks'] and
                      'Ordinary load resets battle-only records' in json.loads(p.read_text())['checks'])
        prior = json.loads(source.read_text())
        assert prior['romSha1'] == meta['romSha1'] and prior['seedSha1'] == sha(seed)
        checkpoint = next(c for c in prior['captures'] if c['label']=='saved-1')
        state = source.parent/'saved-1.state'
        assert sha(state.read_bytes()) == checkpoint['stateSha1']
        both = (source.parent/'slot-1.sav').read_bytes(); profiles = prior['profiles']
        retained = dict(report=str(source), sha1=sha(source.read_bytes()), through='cold-slot-0',
                        save=str(source.parent/'slot-1.sav'), saveSha1=sha(both))
    elif '--resume' in sys.argv or '--resume-latest' in sys.argv:
        source = (pathlib.Path(sys.argv[sys.argv.index('--resume')+1]) if '--resume' in sys.argv else
                  pathlib.Path(json.loads((ROM.parent/'independent-save-slots-latest.json').read_text())['report']))
        prior = json.loads(source.read_text())
        assert prior['romSha1'] == meta['romSha1'] and prior['seedSha1'] == sha(seed)
        assert 'First slot cold load' in prior['checks']
        checkpoint = next(c for c in prior['captures'] if c['label']=='profile-1')
        state = source.parent/'profile-1.state'; ramfile = source.parent/'profile-1.ram'
        assert sha(state.read_bytes()) == checkpoint['stateSha1']
        assert sha(ramfile.read_bytes()) == checkpoint['ramSha1']
        profiles = prior['profiles']; e = E(ROM); e.load(state)
        assert e.memory() == ramfile.read_bytes()
        assert owned(e.memory()) == profiles['1']
        retained = dict(report=str(source), sha1=sha(source.read_bytes()), through='profile-1')
    else:
        cold(seed, 0)
        profile(0); first = save(0)
        e.close(); e = None
        # Fresh boot prevents carrying a menu selection between the two saves.
        cold(first, 0)
        check(owned(e.memory()) == profiles['0'], 'First slot cold load')
        profile(1)
    if not cold_only:
        both = save(1)
        e.close(); e = None
    for slot in ((1, 0) if cold_only else (0, 1, 0)):
        cold(both, slot, selected=1)
        capture('cold-'+str(slot)+'-'+str(len(captures)))
        actual = owned(e.memory())
        for name, expected in profiles[str(slot)].items():
            check(actual[name] == expected, 'Cold slot'+str(slot)+' independent '+name)
        check(e.memory()[0x3f410:0x3f728] == bytes(792), 'Ordinary load resets battle-only records')
        e.close(); e = None
    check(seedpath.read_bytes() == seed, 'Seed save unchanged')
except BaseException as error:
    failure = repr(error)
    if e is not None: capture('failure')
finally:
    if e is not None: e.close()
report = dict(passed=failure is None, romSha1=meta['romSha1'], seedSha1=sha(seed),
              assertions=len(checks), checks=checks, inputs=inputs, captures=captures,
              profiles=profiles, retained=retained, failure=failure, scope=__doc__)
(OUT/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
if not retained and 'First slot cold load' in checks:
    (ROM.parent/'independent-save-slots-latest.json').write_text(json.dumps(dict(report=str(OUT/'report.json'))), encoding='utf-8')
print(json.dumps(dict(passed=report['passed'], assertions=len(checks), failure=failure, report=str(OUT/'report.json'))))
assert failure is None, failure
