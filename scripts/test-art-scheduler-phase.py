"""Bounded input-arrival experiment on one authenticated mixed battle.

Only zero-input video frames vary. The original control bypasses composition;
the optional preferred-assignment control retains composition and forces the
full planner. Both are diagnostics, never replacement playable candidates.
"""
import argparse
import ctypes as C
import datetime
import hashlib
import json
import runpy
import struct
from pathlib import Path
from native_art import ROOT, sha
from native_battle_wrappers import from_emulator

SOURCE = ROOT / 'build/art/live-palette/battle/20260918T171708.832178Z'
PIN = {
    'observed.json': 'd57cb156d3a5561450fcf994451fffc446a99b468434c623407809c4fc5b79e6',
    'candidate-ready.state': '579a6c324f42819b7e70d1d4393057d712a3d4c63a32e83fa0e69b519d6a3358',
    'candidate-ready.ram': '9f072141d166f8b6eb4aada3ebf74adc9a8ab498970fb9e674d381d24c0a38be',
    'candidate-ready.iwram': '19dff5a59ac9904c2beb12976f587830ed201a089bf73e555a02393a85950f79',
}
META = ROOT / 'build/art/connected/7b966543796975a6dea474d0a360495b57d8e6a3/live-palette-view.json'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--candidate-manifest',type=Path)
parser.add_argument('--retained-report',type=Path)
parser.add_argument('--preferred-bypass',action='store_true')
args=parser.parse_args()
assert bool(args.candidate_manifest)==bool(args.retained_report)==args.preferred_bypass
if args.preferred_bypass:
    SOURCE=args.retained_report.parent;META=args.candidate_manifest
    PIN={name:sha((SOURCE/name).read_bytes()) for name in
         (args.retained_report.name,'candidate-ready.state','candidate-ready.ram','candidate-ready.iwram')}
E = runpy.run_path(str(ROOT / 'scripts/emulator-test.py'))['Emulator']
out = ROOT / 'build/art/scheduler-phase' / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True)
checks, records = [], []
e = None


def check(ok, label):
    assert ok, label
    checks.append(label)


def summary(rows, start, target):
    moved = [i for i, row in enumerate(rows) if row['position'][0] != start]
    arrived = [i for i, row in enumerate(rows) if row['position'][0] == target]
    assert moved and arrived, 'Native movement must begin and finish'
    changes = [i for i in range(1, len(rows)) if rows[i]['position'] != rows[i-1]['position']]
    return dict(start=moved[0], end=arrived[0], elapsed=arrived[0]-moved[0],
                positionChanges=changes, positions=[rows[i]['position'] for i in changes],
                changeGaps=[b-a for a, b in zip(changes, changes[1:])])


try:
    for name, digest in PIN.items():
        check(sha((SOURCE/name).read_bytes()) == digest, 'Authenticated input ' + name)
    meta = json.loads(META.read_text())
    prior = json.loads((args.retained_report if args.preferred_bypass else SOURCE/'observed.json').read_text())
    rom = Path(meta['path']).read_bytes()
    check(hashlib.sha1(rom).hexdigest() == prior['romSha1'] == meta['romSha1'] and
          prior['status'] in (('passed','failed') if args.preferred_bypass else ('passed',)), 'Exact ROM and serialized actor pointers')
    # Preserve the historical keyboard-only comparison without requiring that
    # its old target still occupy the mutable current-candidate index.
    current = json.loads((ROOT/'build/art/connected/d9acd7234186a77561a2fb4ee91fdae2197c197d/manifest.json').read_text()) if not args.preferred_bypass else meta
    current_rom = Path(current['path']).read_bytes()
    check(hashlib.sha1(current_rom).hexdigest() == current['romSha1'], 'Comparison candidate identity')
    if not args.preferred_bypass:
        check(meta['romSha1']=='7b966543796975a6dea474d0a360495b57d8e6a3' and current['romSha1']=='d9acd7234186a77561a2fb4ee91fdae2197c197d','Pinned historical scheduler comparison')
        check(len(rom) == len(current_rom) and
          [i for i, (a, b) in enumerate(zip(rom, current_rom)) if a != b] == [0x12a15e]
          and rom[0x12a15e] == 0xc6 and current_rom[0x12a15e] == 0x42,
          'Only historical comparison difference is the separate US keyboard allocation')
    change = next(x for x in meta['changes'] if x['offset'] == 0x12bc)
    check(rom[0x12bc:0x12c4].hex() == change['after'] and
          change['before'] == 'f0b557464e464546', 'Authenticated compositor entry')
    bypass = bytearray(rom)
    if args.preferred_bypass:
        check(meta['historySlots']==20,'Twenty-slot ABI: 32-byte plan immediately precedes tags; request at plan+4')
        site=meta['symbols']['preferred']-0x08000000
        check(meta['used'][0]<=site<site+4<=meta['used'][1] and
              struct.unpack_from('<H',rom,site)[0]&0xfe00==0xb400,
              'Preferred Thumb entry begins with its authenticated register push')
        patch=dict(offset=site,before=rom[site:site+4].hex(),after='00207047')
        bypass[site:site+4]=bytes.fromhex(patch['after'])
        check(bypass[:site]==rom[:site] and bypass[site+4:]==rom[site+4:],
              'Only preferred validator returns zero; native compositor and full planner stay enabled')
    else:
        patch=dict(offset=0x12bc,before=change['after'],after=change['before'])
        bypass[0x12bc:0x12c4] = bytes.fromhex(change['before'])
        check(bypass[:0x12bc] == rom[:0x12bc] and bypass[0x12c4:] == rom[0x12c4:],
              'Control changes only the original eight-byte compositor entry')
    control = out/'compositor-bypass.gba'
    control.write_bytes(bypass)
    for name, path in [('active', Path(meta['path'])), ('bypass', control)]:
        for delay in range(6):
            label = name + '/idle-' + str(delay)
            e = E(path)
            e.load(SOURCE/'candidate-ready.state')
            check(e.memory() == (SOURCE/'candidate-ready.ram').read_bytes() and
                  C.string_at(*e.maps[0x03000000]) == (SOURCE/'candidate-ready.iwram').read_bytes(),
                  label + ' exact initial RAM/IWRAM')
            cpu = C.create_string_buffer(e.core.retro_serialize_size())
            assert e.core.retro_serialize(cpu, len(cpu))
            check(struct.unpack_from('<I', cpu, 0x5c)[0] == 0x0800042a,
                  label + ' initial CPU waits in unchanged native foreground code')
            wrapper = from_emulator(rom, e)[0x290]
            canonical = e.memory()[0x80:0x1e70]
            inputs = [[8, key, 180] for key in (256, 128, 128, 128)]
            for press, key, wait in inputs:
                e.run(press, key)
                e.run(wait)
            e.run(delay)
            actions = {}
            for action, key, initial, target in [('move', 256, 48, 144), ('cancel', 1, 144, 48)]:
                e.run(8, key)
                rows = []
                for tick in range(600):
                    e.run(1)
                    ram = e.memory()
                    iw = C.string_at(*e.maps[0x03000000])
                    rows.append(dict(position=list(struct.unpack_from('<3H', ram, wrapper+8)),
                        skippedDMA=struct.unpack_from('<H', iw, 0xe10)[0],
                        nativeFrame=struct.unpack_from('<H', iw, 0xeb4)[0],
                        inputWords=list(struct.unpack_from('<6I', iw, 0)),
                        cycleHead=struct.unpack_from('<I', iw, 0x3c64)[0],
                        shadowCycles=iw[0x39a4:0x39c0].hex(),
                        paletteRequested=struct.unpack_from('<I',ram,meta['ramReservation'][0]-0x02000000+meta['tagOffset']-28)[0] if args.preferred_bypass else None,
                        profile=list(struct.unpack_from('<4H', ram,
                            meta['ramReservation'][0]-0x02000000+meta['profileOffset']))))
                check(rows[-1]['position'] == [target, 32, 432], label+'/'+action+' final native position')
                check(ram[0x80:0x1e70] == canonical, label+'/'+action+' canonical roster inventory AP unchanged')
                if args.preferred_bypass:
                    check(all(row['paletteRequested'].bit_count()>1 for row in rows),
                          label+'/'+action+' sampled scene remains a multi-owner full-planner control')
                actions[action] = dict(motion=summary(rows, initial, target), observations=rows)
            e.close()
            e = None
            records.append(dict(case=name, idleFramesBeforeMove=delay, inputs=inputs,
                                actionInputs=[[8, 256, 600], [8, 1, 600]], actions=actions))
            print(json.dumps(dict(case=label, motion={k:{f:v['motion'][f] for f in
                ('start', 'end', 'elapsed')} for k,v in actions.items()})), flush=True)
    # Each case must preserve the same ordered logical positions. Cadence,
    # arrival time and native color phases are reported without normalization.
    for action in ('move', 'cancel'):
        reference = records[0]['actions'][action]['motion']['positions']
        for record in records:
            check(record['actions'][action]['motion']['positions'] == reference,
                  str((record['case'], record['idleFramesBeforeMove'], action))+' same ordered logical motion')
    for name, digest in PIN.items():
        check(sha((SOURCE/name).read_bytes()) == digest, 'Source remains unchanged '+name)
    report = dict(status='passed', checks=checks, romSha1=meta['romSha1'],
        currentSha1=current['romSha1'], controlSha1=hashlib.sha1(bypass).hexdigest(),
        source=str(SOURCE), sourceStatus=prior['status'], inputHashes=PIN,
        controlPatch=patch, preferredBypass=args.preferred_bypass, records=records,
        scope='Six fixed idle offsets before identical Move/cancel inputs on one exact retained mixed battle; paired compositor bypass. No memory/state edits, new deployment fixture or source change. Same logical motion and player records required. Absolute color phases and timing are retained, not normalized or accepted; control omits class composition. Separate historical keyboard-only ROM delta authenticated.')
    if args.preferred_bypass:
        report['scope']='Six fixed idle offsets, exact matched candidate ROM/state and inputs; control bypasses only preferred assignment validation and retains full native/custom composition. Sampled active/control frames must retain multiple owners. Ordered motion/player records required. Raw timing and native phases reported without normalization; no gameplay timing acceptance or all-scene claim.'
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(status='passed', checks=len(checks), report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed', error=str(error),
        checks=checks, records=records), indent=2)+'\n')
    print('Artifacts: '+str(out))
    raise
finally:
    if e:
        e.close()
