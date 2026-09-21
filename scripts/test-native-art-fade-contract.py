"""Compare generated-palette interpolation against real native fade callbacks."""
import ast, datetime, hashlib, json, struct, subprocess, sys
from pathlib import Path
from native_art import ROOT, sha
sys.path.insert(0, str(ROOT / 'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
UNIT, EQUIPMENT, RETURN, STACK = 0x02000080, 0x02002000, 0x08000100, 0x03007000
tree = ast.parse((ROOT / 'scripts/test-equipment-legality.py').read_text().replace('count=50000', 'count=300000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ARM'], type_ignores=[]), '<native ARM>', 'exec'))
out = ROOT / 'build/art/palette-fade' / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True)
meta = json.loads((ROOT / 'build/art/live-palette/19c8d9e05546607ad12d76be27fab1be6a4f9dbf/manifest.json').read_text())
rom = bytearray(Path(meta['path']).read_bytes())
assert hashlib.sha1(rom).hexdigest() == meta['romSha1']
retained = ROOT / 'build/art/live-palette/menu/20260918T024914.965413Z/candidate-wheel0.iwram'
iwram = retained.read_bytes()
assert sha(iwram) == '20248810a26e32f8aca144315d39aa608f4a95bd8a108ab7aa5827bf384b8d66'
clean = (ROOT / 'roms/clean/FFTA_US_clean.gba').read_bytes()
assert hashlib.sha1(clean).hexdigest() == '4ac05441f4de70a4ec3dd932116346c61b8783d9'
assert rom[0x1465e8:0x148788] == clean[0x1465e8:0x148788]
prefix = str(ROOT / 'tools/arm-gnu/bin/arm-none-eabi-')
elf, binary = out / 'fade.elf', out / 'fade.bin'
entry = 0x09fd0000
compiled = subprocess.run([prefix + 'gcc.exe', '-mcpu=arm7tdmi', '-mthumb', '-O2', '-ffreestanding', '-fno-builtin', '-nostdlib', '-Wall', '-Wextra', '-Werror', '-Wl,-Ttext=' + hex(entry), '-Wl,-e,ffta_art_fade_start', 'src/engine/art-palette-fade.c', '-o', str(elf)], cwd=ROOT, capture_output=True, text=True)
(out / 'compile.log').write_text(compiled.stdout + compiled.stderr)
compiled.check_returncode()
subprocess.run([prefix + 'objcopy.exe', '-O', 'binary', str(elf), str(binary)], check=True, capture_output=True)
symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output([prefix + 'nm.exe', str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
code = binary.read_bytes()
assert len(code) < 4096
assert rom[entry - 0x08000000:entry - 0x08000000 + len(code)] == b'\xff' * len(code)
rom[entry - 0x08000000:entry - 0x08000000 + len(code)] = code
colors = (ROOT / 'build/art/imagegen/human-dark-knight/march-v2-own-palette/palette.bin').read_bytes()
assert sha(colors) == meta['paletteSha256']
checks, cases = [], []
STATE, SOURCE, TARGET = 0x02010000, 0x02010200, 0x02010300
FIRST = 288
PAL = 0x03003860 + FIRST * 2
TWEEN = 0x03003e68 + FIRST * 12


def check(ok, label):
    assert ok, label
    checks.append(label)


try:
    for name, source, target in [('black', colors, bytes(32)), ('white', colors, b'\xff\x7f' * 16),
                                 ('from-black', bytes(32), colors), ('from-white', b'\xff\x7f' * 16, colors),
                                 ('mixed', colors, colors[16:] + colors[:16])]:
        for duration in (0, 1, 2, 3, 8, 17, 255):
            for flags in (0, 16):
                label = str((name, duration, flags))
                a = ARM(rom, iwram)
                a.put(PAL, source)
                a.put(SOURCE, source)
                a.put(TARGET, target)
                a.put(STATE - 4, b'\xd7' * 4)
                a.put(STATE, b'\xa5' * 212)
                a.put(STATE + 212, b'\xe9' * 4)
                for i in range(16): a.put(TWEEN + i * 12, target[i * 2:i * 2 + 2])
                # Real native task allocation/accumulator setup, not synthesized
                # task records. Original menu palette pool is retained intact.
                task = a.call(0x08146e55, FIRST, FIRST + 15, duration, flags)
                check(0x03003c68 <= task < 0x03003e68, label + ' native fade task allocated from retained pool')
                check(a.call(symbols['ffta_art_fade_start'], STATE, SOURCE, TARGET, duration) == 1, label + ' sidecar initialized')
                initial = a.read(STATE, 212)
                for i in range(16):
                    native = a.read(TWEEN + i * 12, 12)
                    check(initial[64 + i * 6:70 + i * 6] == native[2:8] and initial[160 + i * 3:163 + i * 3] == native[8:11], label + '/' + str(i) + ' exact native accumulator and signed delta')
                frames = []
                for tick in range(max(1, duration)):
                    a.call(0x08148741, task)
                    check(a.call(symbols['ffta_art_fade_step'], STATE, bool(flags & 16)) == 1, label + '/' + str(tick) + ' sidecar advances')
                    actual = a.read(STATE, 32)
                    check(actual == a.read(PAL, 32), label + '/' + str(tick) + ' all sixteen colors match native callback exactly')
                    frames.append(actual.hex())
                check(a.read(STATE, 32) == target and a.read(task, 2) == b'\0\0', label + ' exact final target and native retirement')
                finished = a.read(STATE, 212)
                check(a.call(symbols['ffta_art_fade_step'], STATE, bool(flags & 16)) == 0 and a.read(STATE, 212) == finished, label + ' finished sidecar is stable')
                check(a.read(STATE - 4, 4) == b'\xd7' * 4 and a.read(STATE + 212, 4) == b'\xe9' * 4, label + ' caller bounds preserved')
                # Native callback may change its task, palette and DDA. The
                # independent sidecar owns only STATE and ordinary call stack.
                before = a.read(0x03000000, 0x8000)
                a.call(symbols['ffta_art_fade_start'], STATE, SOURCE, TARGET, duration)
                a.call(symbols['ffta_art_fade_step'], STATE, bool(flags & 16))
                after = a.read(0x03000000, 0x8000)
                check(before[:0x6e00] == after[:0x6e00] and before[0x7000:] == after[0x7000:], label + ' sidecar leaves native palette and effect state untouched')
                cases.append(dict(name=name, duration=duration, flags=flags, task=task, frames=frames))
    a = ARM(rom, iwram)
    for duration in (256, 257, 65535, 0xffffffff):
        a.put(STATE, b'\xa5' * 212)
        check(a.call(symbols['ffta_art_fade_start'], STATE, SOURCE, TARGET, duration) == 0 and a.read(STATE, 212) == b'\xa5' * 212, str(duration) + ' unsupported native eight-bit duration refused without writes')
    report = dict(status='passed', checks=checks, cases=cases, romSha1=meta['romSha1'], oracleRomSha1=hashlib.sha1(rom).hexdigest(),
                  compiledBytes=len(code), compiledSha256=sha(code), retainedIWRAMSha256=sha(iwram),
                  sources={p: sha((ROOT / p).read_bytes()) for p in ('src/engine/art-palette-fade.c', 'src/engine/art-palette-fade.h')},
                  scope='Exact native 146E54 setup and 148740/1465E8 callbacks versus caller-owned RGB555 sidecar for 70 black/white/mixed/transparent-skip cases. No installed hook, native effect target/ownership interception, blink/cycle/color-mode or live fade acceptance.')
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status='passed', checks=len(checks), cases=len(cases), report=str(out / 'report.json'))))
except Exception as error:
    (out / 'failed.json').write_text(json.dumps(dict(status='failed', error=str(error), checks=checks, cases=cases, romSha1=meta['romSha1']), indent=2) + '\n')
    print(str(out))
    raise
