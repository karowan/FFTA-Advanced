"""Read authenticated historical source from Git or the public bootstrap bundle.

The public tree has fresh history. Its explicit text bundle replaces old commit
lookups for the gameplay rebuild, without changing any pinned executable bytes.
"""
import hashlib
import io
import json
import re
from pathlib import Path, PurePosixPath
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
SUFFIXES = {'.py', '.mjs', '.js', '.json', '.c', '.h', '.s', '.ld', '.txt', '.inc'}


def validate_name(name):
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name:
        raise ValueError('Unsafe historical source path')
    return path


def bundled_files(root, commit):
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('Invalid historical source revision')
    index = json.loads((root / 'bootstrap/index.json').read_bytes())
    if index['schema'] != 1 or commit not in index['commits']:
        raise ValueError('Historical source revision is not bundled')
    files = {}
    for name, expected in index['commits'][commit].items():
        validate_name(name)
        path = (root / 'bootstrap' / commit / name).resolve()
        if not path.is_relative_to((root / 'bootstrap' / commit).resolve()):
            raise ValueError('Historical source escaped its bundle')
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('Historical source checksum mismatch: ' + name)
        files[name] = raw
    return files


def source_file(commit, name, root=ROOT):
    validate_name(name)
    if (root / 'bootstrap/index.json').is_file():
        return bundled_files(root, commit)[name]
    return subprocess.check_output(['git', 'show', commit + ':' + name], cwd=root)


def source_tree(commit, root=ROOT):
    if (root / 'bootstrap/index.json').is_file():
        files = bundled_files(root, commit)
        return files, {'bundleIndexSha256': hashlib.sha256((root / 'bootstrap/index.json').read_bytes()).hexdigest()}
    archive = subprocess.check_output(['git', 'archive', '--format=tar', commit], cwd=root)
    files = {}
    with tarfile.open(fileobj=io.BytesIO(archive)) as tree:
        for member in tree.getmembers():
            path = validate_name(member.name)
            if member.isfile() and path.parts[0] in {'src', 'scripts', 'notes'} and path.suffix.lower() in SUFFIXES:
                files[path.as_posix()] = tree.extractfile(member).read()
    return files, {'archiveSha256': hashlib.sha256(archive).hexdigest()}
