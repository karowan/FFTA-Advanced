"""Build a public release ZIP from an accepted, checksum-pinned BPS input.

No ROM, emulator, private fixture, network access or game compilation. The
release input's acceptance record describes local testing, not a CI replay.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import struct
import zlib

from mod_release import ROOT, archive_bytes, json_bytes, read_archive, sha


def require(condition, message):
    if not condition:
        raise ValueError(message)


def number(raw, cursor):
    value, shift = 0, 1
    for _ in range(10):
        require(cursor < len(raw) - 12, 'Truncated BPS header')
        byte = raw[cursor]; cursor += 1
        value += (byte & 127) * shift
        if byte & 128:
            return value, cursor
        shift <<= 7; value += shift
    raise ValueError('Oversize BPS header integer')


def verify_patch(raw, config):
    require(len(raw) == config['patch']['bytes'] and sha(raw) == config['patch']['sha256'], 'Patch differs from accepted input')
    require(len(raw) >= 19 and raw[:4] == b'BPS1', 'Invalid BPS header')
    source_size, cursor = number(raw, 4)
    target_size, cursor = number(raw, cursor)
    metadata_size, cursor = number(raw, cursor)
    require(source_size == config['source']['bytes'] and target_size == config['target']['bytes'], 'BPS source/target size mismatch')
    require(cursor + metadata_size < len(raw) - 12, 'Invalid BPS metadata length')
    source_crc, target_crc, patch_crc = struct.unpack('<III', raw[-12:])
    require(f'{source_crc:08x}' == config['source']['crc32'], 'BPS source CRC mismatch')
    require(f'{target_crc:08x}' == config['target']['crc32'], 'BPS target CRC mismatch')
    require(zlib.crc32(raw[:-4]) == patch_crc, 'BPS patch CRC mismatch')


def build(config, patch, template, notes, tag):
    require(config['schema'] == 1, 'Unsupported release input schema')
    require(re.fullmatch(r'v[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?', tag), 'Invalid version tag')
    require(tag == config['tag'] and tag == 'v' + config['version'], 'Tag does not match release input')
    require(config['patch']['file'] == 'FFTA_Expansion.bps' and config['patch']['format'] == 'BPS', 'Unexpected patch name/format')
    verify_patch(patch, config)
    text = template.replace('\r\n', '\n')
    values = dict(MOD_NAME=config['name'], VERSION=config['version'], SOURCE_BYTES=str(config['source']['bytes']),
                  SOURCE_SHA1=config['source']['sha1'], TARGET_SHA1=config['target']['sha1'])
    for key, value in values.items():
        token = '{{' + key + '}}'
        require(token in text, 'Missing README field: ' + key)
        text = text.replace(token, value)
    require('{{' not in text and '}}' not in text, 'Unresolved README field')
    readme = text.encode('utf-8'); changes = notes.replace('\r\n', '\n').encode('utf-8')
    manifest = {key: copy.deepcopy(config[key]) for key in ('schema', 'name', 'version', 'source', 'target', 'patch')}
    manifest['license'] = {'spdx': 'MIT', 'text': (ROOT / 'LICENSE').read_text(encoding='utf-8'), 'scope': 'Original project contributions only; original game assets and third-party rights are excluded.'}
    manifest['documents'] = {'README.md': sha(readme), 'CHANGELOG.md': sha(changes)}
    manifest['validation'] = {
        'localAcceptance': copy.deepcopy(config['localAcceptance']),
        'ci': {'scope': 'Release packaging from accepted BPS; no game compilation or ROM execution.',
               'acceptedPatchSha256Verified': True, 'bpsHeaderAndChecksumsVerified': True}}
    files = {'FFTA_Expansion.bps': patch, 'README.md': readme, 'CHANGELOG.md': changes, 'manifest.json': json_bytes(manifest)}
    archive = archive_bytes(files)
    require(archive_bytes(files) == archive, 'Nondeterministic ZIP')
    read_archive(archive)
    return archive, files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--patch', type=Path, required=True)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--output', type=Path, default=ROOT / 'build/ci-release')
    args = parser.parse_args()
    config = json.loads((ROOT / 'release/input.json').read_bytes())
    archive, _ = build(config, args.patch.read_bytes(), (ROOT / 'MOD-README.md').read_text(encoding='utf-8'),
                       (ROOT / 'release/NOTES.md').read_text(encoding='utf-8'), args.tag)
    output = args.output.resolve()
    require(output.is_relative_to(ROOT / 'build'), 'Release output must stay under ignored build/')
    output.mkdir(parents=True, exist_ok=True)
    filename = 'FFTA-Advanced-' + args.tag + '.zip'
    destination = output / filename
    if destination.exists():
        require(destination.read_bytes() == archive, 'Refuse to replace a different release ZIP')
    else:
        destination.write_bytes(archive)
    sums = f'{sha(archive)}  {filename}\n{config["patch"]["sha256"]}  FFTA_Expansion.bps\n'
    (output / 'SHA256SUMS.txt').write_text(sums, encoding='utf-8', newline='\n')
    print(json.dumps(dict(status='passed', file=destination.name, bytes=len(archive), sha256=sha(archive),
                         targetSha1=config['target']['sha1'])))


if __name__ == '__main__':
    main()
