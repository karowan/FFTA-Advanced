"""Deterministic isolation, private asset and native toolchain preflight."""
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

def sha(path, kind='sha1'):
    h = hashlib.new(kind)
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


seed = json.loads((ROOT / '.local/worktree-seed.json').read_text())
assert pathlib.Path(seed['worktree']).resolve() == ROOT
parent = pathlib.Path(seed['sourceRoot']).resolve()
assert ROOT != parent and (ROOT / '.git').is_file()
assert pathlib.Path(subprocess.check_output(
    ['git', 'rev-parse', '--show-toplevel'], cwd=ROOT, text=True).strip()).resolve() == ROOT
# Seed verification is an initial preflight, not a cache-validity claim after
# a job intentionally rebuilds its own generated files.
for item in seed['files']:
    path = ROOT / item['path']
    assert path.resolve().is_relative_to(ROOT) and not path.is_symlink(), path
    assert sha(path, 'sha256') == item['localSha256'], path
assert sha(ROOT / 'roms/clean/FFTA_US_clean.gba') == '4ac05441f4de70a4ec3dd932116346c61b8783d9'
meta = json.loads((ROOT / 'build/expansion/probes/combat.json').read_text())
assert sha(ROOT / 'build/expansion/probes/combat.gba') == meta['romSha1']
assert meta['romSha1'] == 'ba1c33ea4191abd74d346cc2d22dc39e5d1df1b7'
assert sha(ROOT / 'build/expansion/engine.bin') == meta['engineSha1']
subprocess.run([str(ROOT / 'tools/arm-gnu/bin/arm-none-eabi-gcc.exe'), '--version'], check=True,
               stdout=subprocess.DEVNULL)
subprocess.run(['node', '--version'], check=True, stdout=subprocess.DEVNULL)
sys.path.insert(0, str(ROOT / 'tools/arm-python'))
import unicorn
import capstone
import PIL
output = ROOT / 'build/worktree-preflight.json'
output.write_text(json.dumps(dict(passed=True, job=seed['job'], worktree=str(ROOT),
    checkedAssets=len(seed['files']), sourceCommit=seed['sourceCommit'],
    scope='Local prerequisite isolation only; no job behavior acceptance'), indent=2))
print(output.read_text())
