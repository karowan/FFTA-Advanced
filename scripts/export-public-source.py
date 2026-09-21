"""Prepare a separate, redacted source tree. Never initialize/push Git or delete.

Copies tracked and nonignored new source, not tools/assets/private build data.
The original repository, source receipts and Git history stay untouched.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

from historical_sources import source_file, source_tree
from source_hygiene import personal_path_lines, secret_findings

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('public_audit', ROOT / 'scripts/audit-public-source.py')
audit = importlib.util.module_from_spec(spec); spec.loader.exec_module(audit)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def redact(raw):
    text = raw.decode('utf-8-sig')
    # Preserve prompts, content hashes and filenames. Only local workstation
    # prefixes change; public provenance is explicitly not an original receipt.
    pattern = r'[A-Za-z]:[/\\]+Users[/\\]+[^/\\\s\"\'<>]+'
    text = re.sub(pattern, '<LOCAL_USER>', text)
    text = re.sub(r'/(?:Users|home)/[^/\s\"\'<>]+', '<LOCAL_USER>', text)
    return text.encode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, help='New directory inside ignored .local/')
    args = parser.parse_args()
    destination = (ROOT / args.output).resolve()
    if not destination.is_relative_to((ROOT / '.local').resolve()) or destination == (ROOT / '.local').resolve():
        parser.error('Choose a new directory strictly inside .local/')
    if destination.exists():
        parser.error('Destination exists; never overwrite an earlier export')
    names = set(filter(None, subprocess.check_output(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0')))
    files, redactions, formatting = {}, [], []
    for name in sorted(names):
        path = ROOT / name
        if not path.is_file():
            continue
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            raise ValueError('Refusing source symlink: ' + name)
        raw = path.read_bytes()
        issues = audit.scan_blob(name, raw)
        if issues:
            raise ValueError('Source failed publication audit: ' + name)
        if personal_path_lines(raw):
            changed = redact(raw)
            if personal_path_lines(changed):
                raise ValueError('Unredacted personal path: ' + name)
            if path.suffix == '.json':
                json.loads(changed)
            redactions.append(dict(path=name, originalSha256=sha(raw), publicSha256=sha(changed)))
            raw = changed
        # Remove surplus empty lines at EOF from ordinary source/documents only.
        # Art metadata and historical bootstrap inputs retain exact byte layout.
        if not name.startswith(('src/art/', 'bootstrap/')) and path.suffix in {'.py', '.mjs', '.js', '.ps1', '.c', '.h', '.s', '.md', '.txt'}:
            newline = b'\r\n' if raw.endswith(b'\r\n') else b'\n'
            cleaned = raw.rstrip(b'\r\n') + newline if raw else raw
            if name == 'scripts/test-axe-visuals.py':
                cleaned = re.sub(rb'(?m)^[ \t]+(?=\r?$)', b'', cleaned)
            if cleaned != raw:
                formatting.append(dict(path=name, originalSha256=sha(raw), publicSha256=sha(cleaned)))
                raw = cleaned
        files[name] = raw
    bootstrap = json.loads((ROOT / 'notes/engine-bootstrap.json').read_bytes())['sourceCommit']
    original, _ = source_tree(bootstrap)
    commits = {bootstrap: original}
    profile = json.loads((ROOT / 'notes/native-art-gameplay-base.json').read_bytes())
    for row in profile['overrides']:
        raw = source_file(row['commit'], row['path'])
        if sha(raw) != row['sha256']:
            raise ValueError('Pinned source mismatch: ' + row['path'])
        commits.setdefault(row['commit'], {})[row['path']] = raw
    index = {'schema': 1, 'commits': {}}
    for commit, entries in commits.items():
        index['commits'][commit] = {}
        for name, raw in entries.items():
            target = 'bootstrap/' + commit + '/' + name
            if audit.scan_blob(target, raw) or personal_path_lines(raw):
                raise ValueError('Historical build input cannot be published unchanged: ' + name)
            index['commits'][commit][name] = sha(raw)
            files[target] = raw
    files['bootstrap/index.json'] = (json.dumps(index, indent=2) + '\n').encode()
    provenance = dict(schema=1, scope='Public redacted provenance. Original receipt bytes and old private test evidence stay in the development repository. Do not use a redacted JSON file as proof of its original receipt checksum.', files=redactions, formattingOnly=formatting)
    files['notes/public-provenance.json'] = (json.dumps(provenance, indent=2) + '\n').encode()
    files['bootstrap/README.md'] = b'''# Historical build inputs

These are authenticated source files needed by the gameplay rebuild. They are
data for the build driver, not a second editable engine tree. The index records
their original revisions and SHA-256 values. No old Git history, game images,
tools or generated code payloads are included. The source loader fails on changed
bytes. Update normal source under src/ and scripts/, not these snapshots.

Only gameplay bootstrap and its three source overrides are bundled. Older
campaign/evidence audits and historical diagnostic scripts still require the
private development history and reports; they are not fresh-checkout acceptance.
'''
    destination.mkdir(parents=True)
    for name, raw in files.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
    # Export inventory stays outside the export, so it can cover all source bytes.
    report = destination.with_name(destination.name + '-export.json')
    report.write_text(json.dumps(dict(schema=1, files={n: sha(b) for n,b in sorted(files.items())},
        redactedFiles=len(redactions), bootstrapFiles=sum(map(len,commits.values())),
        sourceHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        includesWorkingChanges=True), indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(directory=str(destination), sourceFiles=len(files), redactedFiles=len(redactions),
                         bootstrapFiles=sum(map(len,commits.values())), report=str(report)), indent=2))


if __name__ == '__main__':
    main()
