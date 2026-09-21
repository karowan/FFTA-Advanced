"""Create an isolated Git worktree and copy ignored local prerequisites.

Run from the primary checkout. All destinations stay under .worktrees. No
symlinks/hardlinks, downloads, commits, ROM publication or player-save access.
"""
import argparse
import hashlib
import json
import pathlib
import re
import shutil
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def seed_files():
    files = {ROOT / 'roms/clean/FFTA_US_clean.gba',
             ROOT / 'build/test-lab/early-town.sav'}
    expansion = ROOT / 'build/expansion'
    files.update(p for p in expansion.iterdir() if p.is_file() and
                 (p.suffix in {'.h', '.inc'} or p.name in
                  {'engine.bin', 'engine.symbols', 'registry.json'}))
    # Older harnesses import these generated foundation stages. Copy the
    # immediate files only, not years of recursive experiment captures.
    probes = expansion / 'probes'
    files.update(p for p in probes.iterdir() if p.is_file() and
                 p.suffix in {'.gba', '.json', '.ram', '.iwram', '.state'})
    for kind in ('fell-private',):
        current = probes / kind / 'current.json'
        meta = json.loads(current.read_text())
        files.add(current)
        private = pathlib.Path(meta['path'])
        assert private.resolve().is_relative_to(ROOT)
        files.update([private, private.with_name('base.gba'),
                      expansion / 'accepted' / meta['baseSha1'] / 'combat.gba'])
    base = json.loads((probes / 'combat.json').read_text())['romSha1']
    capture = probes / 'fell-main' / base
    files.update(capture / name for name in
                 ('fell.gba', 'executor-report.json', 'executor-capture.state',
                  'executor-capture.ram', 'executor-capture.iwram',
                  'fixture/frozen.gba', 'fixture/battle-ready.state'))
    for name in ('arm-gnu', 'arm-python', 'mgba-test-core',
                 'ffta-engine-hacks', 'ffta-randomizer-source', 'ffta-agent-source'):
        files.update(p for p in (ROOT / 'tools' / name).rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts and '.git' not in p.parts)
    return sorted(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job', choices=['dark-knight', 'viking', 'chemist'])
    parser.add_argument('--ref', default='HEAD')
    args = parser.parse_args()
    destination = (ROOT / '.worktrees' / args.job).resolve()
    assert destination.is_relative_to(ROOT / '.worktrees') and not destination.exists()
    files = seed_files()
    for source in files:
        assert source.is_file() and not source.is_symlink(), source
        assert source.resolve().is_relative_to(ROOT), source
    subprocess.run(['git', 'worktree', 'add', '-b', 'jobs/' + args.job,
                    str(destination), args.ref], cwd=ROOT, check=True)
    entries = []
    for source in files:
        relative = source.relative_to(ROOT)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        # Local pointers must point at this checkout, never at mutable parent
        # outputs. Preserve original and relocated digests in the seed ledger.
        if target.suffix == '.json':
            def relocate(value):
                if isinstance(value, dict):
                    return {k: relocate(v) for k, v in value.items()}
                if isinstance(value, list):
                    return [relocate(v) for v in value]
                if isinstance(value, str):
                    for prefix in (str(ROOT), ROOT.as_posix()):
                        if value.startswith(prefix + '\\') or value.startswith(prefix + '/'):
                            return str(destination) + value[len(prefix):]
                return value
            data = json.loads(target.read_text(encoding='utf-8-sig'))
            relocated = relocate(data)
            if data != relocated:
                target.write_text(json.dumps(relocated, indent=2) + '\n', encoding='utf-8')
        entries.append(dict(path=relative.as_posix(), sourceSha256=digest(source),
                            localSha256=digest(target), bytes=target.stat().st_size))
    output = destination / '.local/worktree-seed.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(dict(schema=1, job=args.job,
        sourceCommit=subprocess.check_output(['git', 'rev-parse', args.ref], cwd=ROOT, text=True).strip(),
        sourceRoot=str(ROOT), worktree=str(destination), files=entries), indent=2) + '\n')
    print(json.dumps(dict(worktree=str(destination), files=len(entries),
                         bytes=sum(x['bytes'] for x in entries), manifest=str(output))))


if __name__ == '__main__':
    main()
