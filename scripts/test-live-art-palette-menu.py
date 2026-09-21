"""Cold-loaded native Dark Knight menu palette, cancel/reopen and isolation."""
import argparse, ctypes as C, datetime, hashlib, json, runpy, struct
from pathlib import Path
from native_art import ROOT, sha
from actor_render_evidence import actors

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--candidate-manifest',type=Path,default=ROOT/'build/art/live-palette/poc.json')
parser.add_argument('--all-classes',action='store_true')
args=parser.parse_args()
meta = json.loads(args.candidate_manifest.read_text())
BASE = meta['ramReservation'][0] - 0x02000000
seedpath = ROOT / 'build/showcase/20260917T160011.215713Z/showcase.sav'
seed = seedpath.read_bytes()
assert hashlib.sha1(seed).hexdigest() == '7831543efb239ef145764889214f8d83cd56eb14'
E = runpy.run_path(str(ROOT / 'scripts/emulator-test.py'))['Emulator']
out = ROOT / 'build/art/live-palette/menu' / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True)
checks, inputs, observations = [], [], {}
e = None; case = 'setup'
colors = (ROOT / 'build/art/imagegen/human-dark-knight/march-v2-own-palette/palette.bin').read_bytes()
assert sha(colors) == meta['paletteSha256']
selected_job=117
class_meta=json.loads((ROOT/'build/art/generated-classes/595782ba32f4a20ff2053218f8722ab5e491112d/manifest.json').read_text())
candidate_rom=Path(meta['path']).read_bytes()
if args.all_classes:
    assert meta.get('allClasses') and meta['historySlots']==20
    assert struct.unpack_from('<I',candidate_rom,meta['symbols']['ffta_art_custom_mask']-0x08000000)[0]==1023

def check(ok, label):
    assert ok, case + '/' + label
    checks.append(case + '/' + label)

def tap(key, wait=120):
    inputs.append([case, 8, key, wait]); e.run(8, key); e.run(wait)

def capture(name, custom=False):
    name=str(selected_job)+'-'+name
    ram = e.memory(); iw = C.string_at(*e.maps[0x03000000])
    vram = C.string_at(*e.maps[0x06000000]); pal = C.string_at(*e.maps[0x05000000]); oam = C.string_at(*e.maps[0x07000000])
    stem = out / (case + '-' + name)
    e.screenshot(stem.with_suffix('.png'))
    for ext, data in [('ram', ram), ('iwram', iw), ('vram', vram), ('palette', pal), ('oam', oam)]: stem.with_suffix('.' + ext).write_bytes(data)
    obs = dict(owned=sha(ram[0x80:0x1e70]), frame=sha(e.frame[0]), palette=sha(pal), oam=sha(oam), vram=sha(vram))
    if case == 'candidate':
        magic = struct.unpack_from('<I', ram, BASE)[0]
        active, applied, restored, failed = struct.unpack_from('<4I', ram, BASE + 0xa0c)
        start, end = struct.unpack_from('<2H', ram, BASE + 0xa1c)
        obs['live'] = dict(magic=magic, active=active, applied=applied, restored=restored, failed=failed, startLine=start, endLine=end)
        check(magic == 0x50414c31, name + ' transient state initialized')
        check(failed == 0, name + ' no ownership/allocation failure')
        # Native palette shadow is never overwritten by the custom overlay.
        if custom:
            resource=256+(selected_job-116)*2
            bodies = [a for a in actors(rom, ram, vram) if a['resource'] == resource]
            check(len(bodies) == 1 and bodies[0]['displayedFrames'], name + ' real generated class actor')
            body = bodies[0]; tile = body['tile']; owners = []
            for i in range(128):
                a, b, c = struct.unpack_from('<3H', oam, i * 8)
                if a & 0x300 != 0x200 and not a & 0x2000 and b >> 14 == 2 and c & 1023 == tile: owners.append((i, a, b, c))
            check(len(owners) == 1, name + ' one hardware body owner')
            bank = owners[0][3] >> 12
            check(active == 1 << bank and applied > 0 and restored > 0, name + ' live overlay and restoration executed')
            check(pal[512 + bank * 32:544 + bank * 32] == colors, name + ' exact generated colors reach hardware')
            check(pal[512:1024] != iw[0x3a60:0x3c60], name + ' hardware overlay distinct from native shadow')
            check(160 <= start <= end < 228, name + ' observed palette work stays inside VBlank scanlines')
            obs['body'] = dict(resource=resource, tile=tile, paletteBank=bank, hardwareIndex=owners[0][0], allocation=body['allocation'],colors=colors.hex())
        else:
            check(active == 0 and pal == iw[0x3860:0x3c60], name + ' no custom actor leaves no overlay')
    observations[case][name] = obs

try:
    for case, path, digest in [('baseline', meta['source'], meta['baseRomSha1']), ('candidate', meta['path'], meta['romSha1'])]:
        rom = Path(path).read_bytes(); check(hashlib.sha1(rom).hexdigest() == digest, 'ROM authenticated')
        observations[case] = {}
        for selected_job in (range(116,126) if args.all_classes else (117,)):
            record=next(j for j in class_meta['classResources']['jobs'] if j['job']==selected_job)
            race=record['race'];slot={1:2,2:3,3:4,5:1,4:5}[race]
            p=meta['symbols']['ffta_art_custom_colors']-0x08000000+(selected_job-116)*32
            colors=candidate_rom[p:p+32]
            e=E(Path(path));e.set_memory(0,seed,0);e.run(3600)
            for key in (8,256,256,256):tap(key,300)
            check(e.memory()[0x80+slot*264+6]==race,'same-race member selected')
            profile=bytes([1,selected_job,race,selected_job])
            e.set_memory(0x80+slot*264+4,profile);inputs.append([case,'isolated appearance profile',slot,list(profile)])
            for key in (8,256):tap(key)
            if slot>=4:tap(32)
            for _ in range(slot%4):tap(128)
            tap(256);tap(32);tap(32);tap(256,600)
            capture('wheel0', True)
            for i in range(1,5):e.run(16);capture('wheel'+str(i),True)
            tap(1,180);capture('cancelled',True)
            tap(256,600);capture('reopened',True)
            tap(1,180);capture('cancelled-again',True)
            tap(1,180);tap(1,180);capture('world-return')
            e.close();e=None
    for name in observations['baseline']:
        check(observations['baseline'][name]['owned'] == observations['candidate'][name]['owned'], name + ' canonical unit state unchanged')
        before_iw = (out / ('baseline-' + name + '.iwram')).read_bytes()
        after_iw = (out / ('candidate-' + name + '.iwram')).read_bytes()
        check(before_iw[0x3860:0x3c60] == after_iw[0x3860:0x3c60], name + ' full native palette shadow unchanged from parent')
        before_pal = bytearray((out / ('baseline-' + name + '.palette')).read_bytes())
        after_pal = (out / ('candidate-' + name + '.palette')).read_bytes()
        body = observations['candidate'][name].get('body')
        if body: before_pal[512 + body['paletteBank'] * 32:544 + body['paletteBank'] * 32] = bytes.fromhex(body['colors'])
        check(bytes(before_pal) == after_pal, name + ' hardware colors differ only in exact owned bank')
    check(seedpath.read_bytes() == seed, 'source save unchanged')
    result = dict(status='passed', checks=checks, inputs=inputs, observations=observations, romSha1=meta['romSha1'], baseRomSha1=meta['baseRomSha1'],
                  jobs=list(range(116,126)) if args.all_classes else [117],
                  scope='Paired cold-load selected class native wheels, five idle samples each, header on cancel/reopen, second cancel and full world return. Exact generated hardware palette, complete paired native shadow/hardware isolation and restoration, observed VBlank scanline bounds and canonical unit isolation. Unaccepted drafts; no fades, simultaneous mixed-class battle coexistence, worst-case cycles or production/package acceptance.')
    (out / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status='passed', checks=len(checks), report=str(out / 'report.json'))))
except Exception as error:
    (out / 'failed.json').write_text(json.dumps(dict(status='failed', error=str(error), checks=checks, inputs=inputs, observations=observations, romSha1=meta['romSha1']), indent=2) + '\n')
    print(str(out)); raise
finally:
    if e: e.close()
