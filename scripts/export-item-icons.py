"""Publish the approved 16x16 equipment icons for the 85 expansion weapons.

Each selected native-palette preview is authenticated against the committed
draft record (src/art/imagegen/new-item-icon-drafts.json: native pixel hash,
donor icon and palette bank) and copied byte-for-byte to artwork/items. The
approval receipt (src/art/imagegen/new-item-icons-approved.json) pins every
published file; artwork/manifest.json gains matching item-icon rows. No drawing,
resampling or generation happens here.
"""
import hashlib
import json
from pathlib import Path

from PIL import Image
from native_art import pack_tiles
from public_art import png_size

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / 'src/art/imagegen/new-item-icon-drafts.json'
RECEIPT = ROOT / 'src/art/imagegen/new-item-icons-approved.json'
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def slug(name):
    return ''.join(c if c.isalnum() else '-' for c in name.lower()).strip('-').replace('--', '-')


def main():
    drafts = json.loads(DRAFTS.read_text(encoding='utf-8'))
    items = drafts['items']
    if [row['id'] for row in items] != list(range(376, 461)):
        raise ValueError('Draft record must list items 376..460 in order')
    selection = json.loads((ROOT / 'build/art/item-drafts/selection.json').read_text(encoding='utf-8'))
    rows, receipt = [], []
    for row in items:
        folder = ROOT / 'build/art/item-drafts' / selection[str(row['id'])]
        preview = folder / 'native-preview.png'
        raw = preview.read_bytes()
        image = Image.open(preview)
        if image.mode != 'P' or image.size != (16, 16) or image.info.get('transparency') != 0:
            raise ValueError(f"{row['id']}: not an indexed 16x16 preview")
        pixels = pack_tiles(image, 4)
        if sha(pixels) != row['nativePixelsSha256'] or sha(raw) != row['indexedPreviewSha256']:
            raise ValueError(f"{row['id']}: preview differs from the committed draft record")
        if png_size(raw) != (16, 16):
            raise ValueError(f"{row['id']}: unexpected PNG")
        name = f"artwork/items/{row['id']}-{slug(row['name'])}.png"
        path = ROOT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_bytes() != raw:
            raise ValueError('Refuse to overwrite changed artwork: ' + name)
        path.write_bytes(raw)
        rows.append(dict(path=name, sha256=sha(raw), bytes=len(raw), size=[16, 16], role='item-icon', item=row['id'],
                         originalSource=preview.relative_to(ROOT).as_posix(), nativePixelsSha256=row['nativePixelsSha256'],
                         donorIcon=row['donorOriginalIconId'], paletteBank=row['donorPaletteBank']))
        receipt.append(dict(id=row['id'], name=row['name'], path=name, sha256=sha(raw),
                            nativePixelsSha256=row['nativePixelsSha256'], donorIcon=row['donorOriginalIconId'],
                            paletteBank=row['donorPaletteBank']))
    RECEIPT.write_text(json.dumps(dict(
        schema=1, status='approved-for-release',
        approval='Player instruction, September 26, 2026: include the 85 native-palette equipment icon drafts in the release.',
        draftRecordSha256=sha(DRAFTS.read_bytes()), items=receipt), indent=2) + '\n', encoding='utf-8')
    manifest_path = ROOT / 'artwork/manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['files'] = [row for row in manifest['files'] if row['role'] != 'item-icon'] + rows
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(status='passed', icons=len(rows), receipt=str(RECEIPT))))


if __name__ == '__main__':
    main()
