"""Audit tracked working sources and optionally all reachable Git history.

Reports paths, lines and object IDs, never matched secret values. No network,
history rewriting, ROM building, deletion or publication. Reports are private.
"""
import argparse
import ast
import collections
import importlib.util
import json
import pathlib
import re
import subprocess
from urllib.parse import unquote, urlsplit

from source_hygiene import PRIVATE_NAMES, personal_path_lines, secret_findings

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('git_content', ROOT / 'scripts/check-git-content.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)
LINK = re.compile(r'!?\[[^\]\n]*\]\(([^)\n]+)\)')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def allowed(name):
    path = pathlib.PurePosixPath(name)
    return (not (set(path.parts) & guard.BLOCKED_DIRS)
            and path.name not in PRIVATE_NAMES
            and (path.suffix.lower() in guard.ALLOWED or name in guard.SPECIAL))


def scan_blob(name, raw):
    errors = []
    if not allowed(name):
        errors.append({'file': name, 'rule': 'private-or-unapproved-path'})
    if b'\0' in raw or len(raw) > 4 * 1024 * 1024:
        errors.append({'file': name, 'rule': 'binary-or-oversize'})
    try:
        raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        errors.append({'file': name, 'rule': 'non-text'})
    errors.extend(dict(file=name, **entry) for entry in secret_findings(raw))
    return errors


def check_links(name, text, names):
    errors, private = [], []
    for match in LINK.finditer(text):
        target = match.group(1).strip()
        if target.startswith('<'):
            target = target[1:target.index('>')] if '>' in target else target
        else:
            target = re.split(r'\s+[\"\']', target, maxsplit=1)[0]
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        # This template is rendered inside the release ZIP, which supplies these
        # two files. The packaging test authenticates both archive entries.
        if name == 'MOD-README.md' and target in {'manifest.json', 'CHANGELOG.md'}:
            continue
        decoded = unquote(parsed.path).replace('\\', '/')
        # Historical notes sometimes use a root-relative path from notes/.
        resolved = (ROOT / pathlib.PurePosixPath(name).parent / decoded).resolve()
        if not resolved.is_relative_to(ROOT):
            errors.append({'file': name, 'rule': 'link-outside-repository', 'target': target})
            continue
        relative = resolved.relative_to(ROOT).as_posix()
        if relative.split('/')[0] in guard.BLOCKED_DIRS:
            private.append({'file': name, 'target': relative})
        elif relative not in names and not any(n.startswith(relative.rstrip('/') + '/') for n in names):
            errors.append({'file': name, 'rule': 'missing-source-link', 'target': target})
    return errors, private


def audit_history():
    rows = git('rev-list', '--objects', '--all').decode().splitlines()
    objects = {row.split(' ', 1)[0]: row.partition(' ')[2] for row in rows}
    info = git('cat-file', '--batch-all-objects', '--batch-check=%(objectname) %(objecttype) %(objectsize)').decode().splitlines()
    blobs = [(oid, objects[oid], int(size)) for oid, kind, size in (line.split() for line in info)
             if kind == 'blob' and oid in objects]
    findings, personal = [], []
    # Read one object at a time; do not materialize the entire repository history.
    with subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT,
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE) as proc:
        for oid, name, size in blobs:
            proc.stdin.write((oid + '\n').encode()); proc.stdin.flush()
            header = proc.stdout.readline().split()
            if len(header) != 3 or header[1] != b'blob' or int(header[2]) != size:
                raise RuntimeError('Unexpected Git object response')
            raw = proc.stdout.read(size)
            if proc.stdout.read(1) != b'\n':
                raise RuntimeError('Truncated Git object response')
            findings.extend(dict(object=oid, **entry) for entry in scan_blob(name, raw))
            lines = personal_path_lines(raw)
            if lines:
                personal.append({'object': oid, 'file': name, 'lines': lines})
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError('Git history scan failed')
    return {'reachableBlobs': len(blobs), 'findings': findings, 'personalPaths': personal,
            'scope': 'All blobs reachable from local refs; not reflogs, unreachable objects, remote refs not fetched, or a comprehensive secret detector.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--history', action='store_true')
    parser.add_argument('--report', default='build/public-source-audit.json')
    parser.add_argument('--require-private-paths-clean', action='store_true')
    args = parser.parse_args()
    names = set(filter(None, git('ls-files', '--cached', '--others', '--exclude-standard', '-z').decode().split('\0')))
    errors, personal, links, private = [], [], [], []
    counts = collections.Counter()
    for name in sorted(names):
        path = ROOT / name
        if not path.is_file():
            # A tracked deletion is valid in the working tree audit.
            continue
        raw = path.read_bytes()
        errors.extend(scan_blob(name, raw))
        lines = personal_path_lines(raw)
        if lines:
            personal.append({'file': name, 'lines': lines})
        counts[path.suffix or '(none)'] += 1
        try:
            if path.suffix == '.json':
                json.loads(raw.decode('utf-8-sig'))
            elif path.suffix == '.py':
                ast.parse(raw.decode('utf-8-sig'), filename=name)
            elif path.suffix == '.md':
                missing, local = check_links(name, raw.decode('utf-8-sig'), names)
                links.extend(missing); private.extend(local)
        except (ValueError, SyntaxError) as exc:
            errors.append({'file': name, 'rule': 'parse-error', 'detail': type(exc).__name__})
    result = {'sourceFiles': sum(counts.values()), 'extensions': dict(counts), 'findings': errors,
              'personalPaths': personal, 'brokenLinks': links, 'privateEvidenceLinks': private}
    if args.history:
        result['history'] = audit_history()
    result['passed'] = not (errors or links or result.get('history', {}).get('findings'))
    if args.require_private_paths_clean and (personal or result.get('history', {}).get('personalPaths')):
        result['passed'] = False
    report = (ROOT / args.report).resolve()
    if not report.is_relative_to(ROOT / 'build'):
        parser.error('Reports must stay under ignored build/')
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': result['passed'], 'files': result['sourceFiles'],
                      'findings': len(errors), 'brokenLinks': len(links),
                      'personalPathFiles': len(personal),
                      'historyBlobs': result.get('history', {}).get('reachableBlobs'),
                      'historyFindings': len(result.get('history', {}).get('findings', [])),
                      'report': report.relative_to(ROOT).as_posix()}, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
