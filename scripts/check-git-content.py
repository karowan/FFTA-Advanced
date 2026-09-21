"""Fail closed if Git's index contains a game image, dump or local asset.

Checks staged bytes, not merely working files. Run before each commit.
"""
import pathlib
import subprocess
from source_hygiene import PRIVATE_NAMES, secret_findings

ROOT = pathlib.Path(__file__).resolve().parents[1]
BLOCKED_DIRS = {'roms', 'saves', 'build', 'downloads', 'tools', 'patches',
                '.worktrees', '.local', '__pycache__'}
ALLOWED = {'.md', '.txt', '.json', '.mjs', '.js', '.py', '.ps1', '.cmd',
           '.c', '.h', '.s', '.ld', '.inc'}
SPECIAL = {'.gitignore', '.gitattributes', '.githooks/pre-commit'}


def check_index(root=ROOT):
    names = list(filter(None, subprocess.check_output(
        ['git', 'ls-files', '--cached', '-z'], cwd=root).decode().split('\0')))
    if any('\n' in name or '\r' in name for name in names):
        raise SystemExit('Unexpected newline in tracked path')
    batch = subprocess.check_output(['git', 'cat-file', '--batch'], cwd=root,
        input=''.join(':' + name + '\n' for name in names).encode())
    cursor = 0
    errors = []
    count = 0
    for name in names:
        end = batch.index(b'\n', cursor)
        header = batch[cursor:end].split()
        assert len(header) == 3 and header[1] == b'blob', (name, header)
        size = int(header[2])
        data = batch[end + 1:end + 1 + size]
        cursor = end + 2 + size
        path = pathlib.PurePosixPath(name)
        if set(path.parts) & BLOCKED_DIRS or path.name in PRIVATE_NAMES or (
                path.suffix.lower() not in ALLOWED and name not in SPECIAL):
            errors.append(f'Unapproved staged file type/path: {name}')
            continue
        # Every tracked artifact is source or documentation. This also rejects
        # renamed ROM images and binary payloads regardless of extension.
        try:
            data.decode('utf-8-sig')
        except UnicodeDecodeError:
            errors.append(f'Non-text staged content: {name}')
        if b'\0' in data or len(data) > 4 * 1024 * 1024:
            errors.append(f'Binary/oversize staged content: {name}')
        if len(data) > 0xbd and data[0xac:0xb0] == b'AFXE':
            errors.append(f'FFTA game header: {name}')
        for finding in secret_findings(data):
            errors.append(f'Possible credential ({finding["rule"]}): {name}:{finding["line"]}')
        count += 1
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'PASS: {count} staged source/document files; no ROMs or private assets.')


if __name__ == '__main__':
    check_index()
