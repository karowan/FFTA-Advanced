"""Copy accepted standalone custom sprites, never native references or screenshots.

Uses authenticated local catalogs and the approved-art candidate. No drawing,
resampling, generation, ROM extraction or game execution.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from public_art import ROLES, png_size

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-root', type=Path, required=True)
    args = parser.parse_args(); source = args.private_root.resolve()
    destination = ROOT / 'artwork'
    candidate_path = source / 'build/art/approved-first-pass-2026-09-20/candidate.json'
    candidate = json.loads(candidate_path.read_bytes())
    if candidate['romSha1'] != 'f53fedb8421f48fd10faabf60700a5d7ed60ddf8': raise ValueError('Wrong art parent')
    approval_path = source / 'src/art/native-ui-review/approved-round8.json'
    approval = json.loads(approval_path.read_bytes())
    if hashlib.sha256(approval_path.read_bytes()).hexdigest() != candidate['components']['approvedRound8']['planSha256']:
        raise ValueError('Approval receipt changed')
    units = [json.loads(p.read_bytes()) for p in sorted((source / 'src/art/race-study/full-animation-v1').glob('*.json'))]
    if [u['job'] for u in units] != list(range(116,126)): raise ValueError('Incomplete class catalog')
    by_job = {u['job']:u for u in units}; pending = {}; rows = []
    def add(path, digest, job, role, identifier):
        original = (source / path).resolve()
        if not original.is_relative_to(source / 'build/art'): raise ValueError('Unexpected artwork source')
        raw = original.read_bytes()
        if hashlib.sha256(raw).hexdigest() != digest: raise ValueError('Changed artwork source: ' + original.name)
        size = png_size(raw)
        if size != ROLES[role]: raise ValueError(f'Wrong standalone dimensions: {original.name} {size}')
        slug = by_job[job]['slug']; name = f'artwork/characters/{slug}/{role}/{identifier}.png'
        if name in pending: raise ValueError('Duplicate artwork')
        pending[name] = raw
        rows.append(dict(path=name, sha256=digest, bytes=len(raw), size=list(size), job=job,
                         role=role, id=identifier, originalSource=original.relative_to(source).as_posix()))
    assets = candidate['components']['reviewedActions']['assets']
    if len(assets) != 675: raise ValueError('Incomplete accepted animation set')
    for row in assets: add(row['source'], row['sourceSha256'], row['job'], 'native-pose', row['pose'])
    for unit in units:
        for pose in unit['poses']: add(pose['output'], pose['outputSha256'], unit['job'], 'source-pose', pose['id'])
    for row in approval['jobs']:
        for key, role in [('portrait','portrait'),('icon','head-icon')]:
            add(row[key]['path'], row[key]['sha256'], row['job'], role, 'approved')
    for row in candidate['components']['reviewedNativeMiniatures']['jobs']:
        add(row['source'], row['sourceSha256'], row['job'], 'miniature-source', 'neutral')
    for key, role in [('equipment','generated-axe'), ('effect','generated-impact'), ('status','generated-status')]:
        row = candidate['components'][key]; original = source / row['sourceArt']; raw = original.read_bytes()
        if hashlib.sha256(raw).hexdigest() != row['sourceArtSha256']: raise ValueError('Changed effect/equipment artwork')
        # Remove ancillary Content Credentials metadata from the public copy;
        # compressed pixel data and its PNG checksums are copied verbatim.
        chunks = []; removed = []; cursor = 8
        while cursor < len(raw):
            length = struct.unpack('>I', raw[cursor:cursor+4])[0]; end = cursor + 12 + length
            if end > len(raw): raise ValueError('Truncated original PNG')
            kind = raw[cursor+4:cursor+8]
            if kind == b'caBX': removed.append('caBX')
            else: chunks.append(raw[cursor:end])
            cursor = end
        cleaned = raw[:8] + b''.join(chunks); size = png_size(cleaned)
        if size != ROLES[role]: raise ValueError('Wrong extra-artwork dimensions')
        name = 'artwork/extras/' + role + '.png'; pending[name] = cleaned
        rows.append(dict(path=name, sha256=hashlib.sha256(cleaned).hexdigest(), bytes=len(cleaned), size=list(size),
                         role=role, originalSource=row['sourceArt'], originalSourceSha256=row['sourceArtSha256'],
                         removedMetadataChunks=removed, conversion='PNG chunk copy; all image data bytes unchanged'))
    for name, raw in pending.items():
        path = ROOT / name; path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            if path.read_bytes() != raw: raise ValueError('Refuse to overwrite changed artwork: ' + name)
        else: path.write_bytes(raw)
    inventory = dict(schema=1, license='MIT', scope='Standalone project-generated class artwork only. No original game reference sprites, worksheets containing game references, UI frames, lettering, screenshots, ROMs or third-party concept images.',
                     approvedArtParentSha1=candidate['romSha1'], approvalReceiptSha256=candidate['components']['approvedRound8']['planSha256'],
                     files=rows)
    (destination / 'manifest.json').write_text(json.dumps(inventory, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(files=len(rows), bytes=sum(len(raw) for raw in pending.values()), classes=len(units))))


if __name__ == '__main__': main()
