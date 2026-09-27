"""Shared path/hash helpers for offline new-job art preparation."""
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def record(path):
    return dict(path=path.resolve().relative_to(ROOT).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def checked(ref):
    path=(ROOT/ref['path']).resolve()
    if not path.is_relative_to(ROOT) or record(path)['sha256']!=ref['sha256']:
        raise ValueError('Reference changed or outside checkout: '+ref['path'])
    return path
