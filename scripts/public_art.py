"""Validate explicitly inventoried, project-authored PNGs without image libraries."""
import hashlib
import json
from pathlib import PurePosixPath
import struct
import zlib

ROLES = {'native-pose': (32, 32), 'source-pose': (32, 32),
         'portrait': (48, 56), 'head-icon': (16, 14), 'miniature-source': (32, 32),
         'generated-axe': (1312, 1199), 'generated-impact': (2172, 724), 'generated-status': (1254, 1254)}


def manifest_entries(raw):
    document = json.loads(raw)
    if document['schema'] != 1:
        raise ValueError('Unknown artwork inventory schema')
    entries = {}
    for row in document['files']:
        path = PurePosixPath(row['path'])
        if (path.parts[:2] not in {('artwork', 'characters'), ('artwork', 'extras')} or '..' in path.parts
                or path.suffix != '.png' or row['path'] in entries or row['role'] not in ROLES):
            raise ValueError('Invalid or duplicate public artwork entry')
        entries[row['path']] = row
    return entries


def png_size(raw):
    if len(raw) > 4 * 1024 * 1024 or not raw.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('Invalid or oversize PNG')
    cursor, size, image_data = 8, None, False
    while cursor < len(raw):
        if cursor + 12 > len(raw): raise ValueError('Truncated PNG chunk')
        length = struct.unpack('>I', raw[cursor:cursor+4])[0]
        kind = raw[cursor+4:cursor+8]; end = cursor + 12 + length
        if end > len(raw): raise ValueError('Truncated PNG data')
        payload = raw[cursor+8:end-4]
        if zlib.crc32(kind+payload) != struct.unpack('>I', raw[end-4:end])[0]:
            raise ValueError('PNG chunk checksum mismatch')
        if kind == b'IHDR':
            if size is not None or cursor != 8 or length != 13: raise ValueError('Invalid PNG header')
            size = struct.unpack('>II', payload[:8])
        elif kind == b'IDAT': image_data = True
        elif kind == b'IEND':
            if length or end != len(raw) or not size or not image_data: raise ValueError('Invalid PNG end')
            return size
        elif kind not in {b'PLTE', b'tRNS', b'gAMA', b'cHRM', b'sRGB', b'pHYs', b'sBIT', b'bKGD'}:
            raise ValueError('PNG metadata or unsupported chunk must be reviewed: ' + kind.decode('ascii', errors='replace'))
        cursor = end
    raise ValueError('PNG has no end chunk')


def artwork_errors(name, raw, entries):
    row = entries.get(name)
    if row is None:
        return ['PNG is not in the approved artwork inventory']
    if hashlib.sha256(raw).hexdigest() != row['sha256'] or len(raw) != row['bytes']:
        return ['Artwork differs from its inventory']
    try:
        size = png_size(raw)
        if size != ROLES[row['role']] or size != tuple(row['size']):
            return ['Unexpected artwork dimensions']
    except ValueError as error:
        return [str(error)]
    return []
