"""Cold native entry with grouped approved sprites; actual in-game captures.

Reuse the declared early-town/Giza procedure. This does not load any older-ROM
savestate, touch player SRAM, accept nonmovement placeholders, or prove timing.
"""
import ctypes as C
import argparse
import datetime
import hashlib
import json
import runpy
import struct
import subprocess
import sys
from pathlib import Path
from native_art import ROOT, sha
from native_battle_wrappers import from_emulator
from actor_render_evidence import actors
from live_palette_evidence import observe


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--actions',action='store_true',help='Use the private explicit-action candidate and its separate evidence pointer')
    parser.add_argument('--complete',action='store_true',help='Use the combined actions, portraits, miniatures and badge candidate')
    parser.add_argument('--native',action='store_true',help='Use existing shared palettes with no runtime overrides')
    parser.add_argument('--manifest',type=Path)
    parser.add_argument('--entry-index',type=Path)
    args=parser.parse_args()
    manifest=args.manifest or ROOT/'build/art/reviewed-integration'/('native-complete-candidate.json' if args.native else 'complete-candidate.json' if args.complete else 'action-candidate.json' if args.actions else 'grouped-palette-pilot.json');meta=json.loads(manifest.read_text())
    assert not args.manifest or args.entry_index, 'Isolated candidates need an isolated evidence pointer'
    if args.actions or args.complete:assert 'reviewedActions' in meta['components']
    rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
    live=meta['components']['livePalette'];profile_path=ROOT/'scripts/fixtures/reviewed-palette-entry.json'
    profile=json.loads(profile_path.read_text());seed=ROOT/'build/test-lab/early-town.sav';seed_hash=sha(seed.read_bytes())
    out=ROOT/'build/art/reviewed-integration/runtime'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    fixture=out/'cold-entry';checks=[];e=None;failure=None;observations={}
    def check(ok,label):
        assert ok,label
        checks.append(label)
    try:
        command=[sys.executable,str(ROOT/'scripts/create-battle-fixture.py'),'--rom',meta['path'],
                 '--out',str(fixture),'--heap-end',hex(live['heapEnd']),'--party-profile',str(profile_path),'--confirm-pub-exit']
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=180)
        (out/'cold-entry.log').write_text(result.stdout+result.stderr)
        result.check_returncode()
        proof=json.loads((fixture/'report.json').read_text())
        check(proof['passed'] and proof['romSha1']==meta['romSha1'],'Native cold route completed on the exact candidate')
        check(proof['actors']==12,'Twelve native actors allocated')
        check(sha(seed.read_bytes())==seed_hash,'Read-only starting SRAM unchanged')
        E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];e=E(meta['path'])
        check(hashlib.sha1((fixture/'frozen.gba').read_bytes()).hexdigest()==meta['romSha1'],'Own-ROM ready state only')
        e.load(fixture/'battle-ready.state');e.run(2)
        r=e.memory();wrappers=from_emulator(rom,e);vram=C.string_at(*e.maps[0x06000000])
        word=lambda p:struct.unpack_from('<I',r,p)[0]
        bodies={u:word(w+0x44)-0x02000000 for u,w in wrappers.items()}
        figures={a['address']:a for a in actors(rom,r,vram,set(bodies.values()))}
        for row in profile['units']:
            unit=0x80+264*row['slot'];job=row['job'];actor=figures[bodies[unit]]
            check(r[unit+7]==job and actor['resource']==256+2*(job-116),'Allocated approved class resource '+str(job))
            check(actor['declaredSequence'] and bool(actor['displayedFrames']),'Actual native graphics upload '+str(job))
        for name,address in [('ram',0x02000000),('iwram',0x03000000),('vram',0x06000000),('palette',0x05000000),('oam',0x07000000)]:
            (out/('ready.'+name)).write_bytes(C.string_at(*e.maps[address]))
        e.screenshot(out/'battle-approved-sprite-pilot.png');e.save(out/'ready.state')
        if args.native:
            from native_shared_palette_evidence import observe as native_observe
            owners={row['job']-116 for row in profile['units']}
            observations=native_observe(rom,r,C.string_at(*e.maps[0x05000000]),C.string_at(*e.maps[0x07000000]),wrappers,check,owners)
            check(set(observations['owners'])==owners,'Every declared native-palette class actually visible')
        else:
            observations=observe(live,rom,r,C.string_at(*e.maps[0x05000000]),C.string_at(*e.maps[0x07000000]),check,{0,1,2})
            check(set(observations['owners'])=={0,1,2},'All three palette groups actually visible')
    except BaseException as error:
        failure=repr(error)
        if e and e.frame:e.screenshot(out/'failed.png')
    finally:
        if e:e.close()
        report=dict(status='failed' if failure else 'passed',romSha1=meta['romSha1'],manifestSha256=sha(manifest.read_bytes()),
                    profileSha256=sha(profile_path.read_bytes()),seedSha256=seed_hash,checks=checks,observations=observations,
                    failure=failure,scope=__doc__,directory=str(out))
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(dict(status=report['status'],checks=len(checks),failure=failure,report=str(out/'report.json'))))
    assert failure is None,failure
    pointer=dict(report=str((out/'report.json').relative_to(ROOT)),sha256=sha((out/'report.json').read_bytes()))
    pointer_name='native-entry-latest.json' if args.native else 'complete-entry-latest.json' if args.complete else 'action-entry-latest.json' if args.actions else 'entry-latest.json'
    pointer_path=args.entry_index or ROOT/'build/art/reviewed-integration'/pointer_name
    pointer_path.parent.mkdir(parents=True,exist_ok=True);pointer_path.write_text(json.dumps(pointer,indent=2)+'\n')


if __name__=='__main__':main()
