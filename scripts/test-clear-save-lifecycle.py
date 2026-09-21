"""Original ending save controller, selected-slot rewrite and cold continuation.

A private one-shot flag-reader shim starts the original ending save task in
an active New Game story scene, retaining the previously saved slot selector.
This isolates the ending's save operation; it does not claim to have played
the final battle or credits. Flash reads/writes, clear-state preparation,
save-dialog dismissal and cold loading remain native. Returning to the real
ending's parent scene is outside this isolated setup's coverage.
"""
import ast
import datetime
import hashlib
import json
import pathlib
import runpy
import struct
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
sha = lambda b: hashlib.sha1(b).hexdigest()
meta = json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
ROM = pathlib.Path(meta['path']); image = ROM.read_bytes()
assert sha(image) == meta['romSha1']
clean = (ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
assert sha(clean) == '4ac05441f4de70a4ec3dd932116346c61b8783d9'
assert image[0xc9540:0xc9574] == clean[0xc9540:0xc9574]
assert image[0xc95d8:0xc9644] == clean[0xc95d8:0xc9644]
assert image[0x12c170:0x12c530] == clean[0x12c170:0x12c530]
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
OUT = ROM.parent/('clear-save-'+stamp); OUT.mkdir()
E = runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
LOG = 0x3ff50
COPY, SHIM = 0x09fff000, 0x09fff100
assert image[COPY-0x08000000:] == b'\xff'*(len(image)-(COPY-0x08000000))
source = r'''
#include <stdint.h>
unsigned clear_save_probe(unsigned flag) {
    volatile uint32_t *log=(volatile uint32_t *)0x0203ff50u;
    if(log[0]==0x434c4541u) {
        log[0]=0;
        log[1]++;
        log[2]=((unsigned (*)(void *))0x0812c511u)((void *)0x0203ff80u);
    }
    return ((unsigned (*)(unsigned))0x09fff001u)(flag);
}
unsigned clear_task_observer(void *task,void *context,void *state) {
    volatile uint32_t *log=(volatile uint32_t *)0x0203ff50u;
    log[3]++;log[4]=*(uint16_t *)context;log[5]=(unsigned)context;log[6]=(unsigned)state;
    return ((unsigned (*)(void *,void *,void *))0x0812c2b9u)(task,context,state);
}
'''
(OUT/'probe.c').write_text(source)
prefix = ROOT/'tools/arm-gnu/bin/arm-none-eabi-'
def command(tool, args):
    result = subprocess.run([str(prefix)+tool+'.exe', *map(str, args)], capture_output=True, text=True)
    (OUT/(tool+'.log')).write_text(result.stdout+result.stderr)
    assert result.returncode == 0, result.stderr
command('gcc', ['-mcpu=arm7tdmi', '-mthumb', '-Os', '-ffreestanding', '-fno-builtin', '-nostdlib',
                '-Wl,-Ttext=0x09fff100', '-Wl,-e,clear_save_probe', OUT/'probe.c', '-o', OUT/'probe.elf'])
command('objcopy', ['-O', 'binary', OUT/'probe.elf', OUT/'probe.bin'])
command('nm', ['--defined-only', OUT/'probe.elf'])
symbols={line.split()[2]:int(line.split()[0],16) for line in (OUT/'nm.log').read_text().splitlines()
         if len(line.split()) == 3}
blob = (OUT/'probe.bin').read_bytes(); assert len(blob) < 0xe00
instrumented = bytearray(image)
instrumented[COPY-0x08000000:COPY-0x08000000+52] = image[0xc9540:0xc9574]
instrumented[SHIM-0x08000000:SHIM-0x08000000+len(blob)] = blob
instrumented[0xc9540:0xc9548] = struct.pack('<HHI', 0x4b00, 0x4718, symbols['clear_save_probe'] | 1)
struct.pack_into('<I',instrumented,0x12c52c,symbols['clear_task_observer'] | 1)
TEST_ROM = OUT/'fixture.gba'; TEST_ROM.write_bytes(instrumented)
seedpath = ROOT/'build/test-lab/early-town.sav'; seed = seedpath.read_bytes()
checks, inputs, captures, profiles = [], [], [], {}
e = None

def check(value, label):
    assert value, label
    checks.append(label)

def tap(key, wait=180):
    inputs.append([8, key, wait]); e.run(8, key); e.run(wait)

def capture(label):
    e.save(OUT/(label+'.state'))
    if e.frame is not None: e.screenshot(OUT/(label+'.png'))
    r=e.memory(); (OUT/(label+'.ram')).write_bytes(r)
    captures.append(dict(label=label, ramSha1=sha(r), stateSha1=sha((OUT/(label+'.state')).read_bytes()),
                         liveCleared=bool(r[0x1f76]&64), stagingCleared=bool(r[0x3cb0+0x1f76]&64),
                         probe=struct.unpack_from('<7I', r, LOG), parentDone=r[0x3ff86],
                         sramSha1=sha(e.memory(0))))

# Reuse only the established profile/owned helpers, never execute their suite.
tree = ast.parse((ROOT/'scripts/test-independent-save-slots.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)
                             and n.name in ('owned', 'profile')], type_ignores=[]), '<save profile helpers>', 'exec'))

failure = None
try:
    e=E(TEST_ROM); e.set_memory(0,seed,0); e.run(3600)
    for key,wait in ((8,180),(256,60),(256,60),(256,180)): tap(key,wait)
    check(not e.memory()[0x1f76]&64, 'Opening is not a cleared game')
    profile(0)
    saved_profile=owned(e.memory())
    for key,wait in ((8,180),(16,180),(256,180),(256,180),(256,180),(64,60),(256,300)):
        tap(key,wait)
    capture('ordinary-saved')
    before_clear=e.memory(0); (OUT/'before-clear.sav').write_bytes(before_clear)
    check(before_clear != seed, 'Native ordinary save creates the selected profile')
    for _ in range(4): tap(1)
    capture('world-after-save')
    selector=e.memory()[0x72:0x74]
    # The event-task scheduler exists inside native story scenes, not an idle
    # world menu. Start a disposable New Game scene while retaining the actual
    # previously written SRAM; restore only its original selected-slot input.
    e.close(); e=E(TEST_ROM); e.set_memory(0,before_clear,0); e.run(3600)
    tap(8); capture('title-menu'); tap(16); tap(256,1800)
    capture('native-story-scene')
    e.set_memory(0x72,selector)
    e.set_memory(LOG, struct.pack('<I',0x434c4541))
    for _ in range(12):
        tap(256,180)
        if struct.unpack_from('<I',e.memory(),LOG+12)[0]: break
    capture('clear-task-started')
    check(struct.unpack_from('<I',e.memory(),LOG+4)[0] == 1, 'Original clear-save task started exactly once')
    check(struct.unpack_from('<I',e.memory(),LOG+12)[0] > 0, 'Native ending controller actually executes')
    for step in range(12):
        tap(256,300); capture('clear-input-'+str(step))
        if e.memory(0) != before_clear:
            break
    cleared=e.memory(0); (OUT/'cleared.sav').write_bytes(cleared)
    check(cleared != before_clear, 'Original ending controller rewrites native flash')
    for _ in range(12):
        tap(256,300)
        if struct.unpack_from('<I',e.memory(),LOG+16)[0] == 0x106: break
    capture('clear-dialog-dismissed')
    check(struct.unpack_from('<I',e.memory(),LOG+16)[0] == 0x106,
          'Native save-complete dialog advances to the final transition state')
    check(e.memory(0) == cleared, 'Completion dialog leaves the cleared flash unchanged')
    e.close(); e=E(ROM); e.set_memory(0,cleared,0); e.run(3600)
    for key,wait in ((8,180),(256,60),(256,60),(256,180)): tap(key,wait)
    capture('cold-cleared')
    check(bool(e.memory()[0x1f76]&64), 'Cold Continue loads native cleared-game flag')
    check(owned(e.memory()) == saved_profile, 'Clear-save/cold load preserves the selected saved expansion profile')
    check(e.memory()[0x3f410:0x3f728] == bytes(792), 'Cold Continue resets battle-only expansion state')
    check(seedpath.read_bytes() == seed, 'Reusable source save unchanged')
except BaseException as error:
    import traceback
    traceback.print_exc(); failure=repr(error)
    if e is not None: capture('failure')
finally:
    if e is not None: e.close()
report=dict(passed=failure is None,romSha1=meta['romSha1'],instrumentedSha1=sha(instrumented),
            sourceSha1=sha(pathlib.Path(__file__).read_bytes()),seedSha1=sha(seed),
            checks=checks,assertions=len(checks),failure=failure,inputs=inputs,captures=captures,
            profiles=profiles,scope=__doc__)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
(OUT/'script.py').write_bytes(pathlib.Path(__file__).read_bytes())
print(json.dumps(dict(passed=report['passed'],checks=len(checks),failure=failure,report=str(OUT/'report.json'))))
assert failure is None,failure
