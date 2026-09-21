"""Import the exact approved round8 pixels without generating or repainting art.

Portraits select original native palette IDs, including native color modes.
Their 48x56 pixels receive only a fixed 64x64 transport placement and the
inverse of the native menu horizontal flip. Badges retain original lettering.
"""
# Workflow and failure lessons: src/art/native-ui-review/README.md, section 6.
# This is a receipt-specific import, not a latest-file selector. The module
# docstring is serialized into immutable evidence below; explanatory changes
# belong in ordinary comments so documentation does not change that metadata.
import copy, hashlib, json, struct
from pathlib import Path
from PIL import Image
from native_art import ROOT, sha, pack_tiles
from native_portraits import entry, decode, encode, pack, PALETTES
from native_miniatures import decode as palette_decode

OUT = ROOT/'build/art/approved-first-pass-2026-09-20'
PLAN = ROOT/'src/art/native-ui-review/approved-round8.json'


def build():
    # Approval binds exact native PNGs and the parent manifest/ROM. Never choose
    # a newer generation opportunistically: it may be a rejected experiment.
    plan = json.loads(PLAN.read_text())
    def source(ref):
        p = ROOT/ref['path']
        assert sha(p.read_bytes()) == ref['sha256'], p
        return p
    parent_path = source(plan['parent'])
    source(plan['review'])
    parent = json.loads(parent_path.read_text())
    original = Path(parent['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest() == plan['parentRomSha1'] == parent['romSha1']
    meta = copy.deepcopy(parent)
    rom = bytearray(original)
    patches = []
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'native').mkdir(exist_ok=True)
    def patch(at, raw, kind):
        assert 0 <= at < at+len(raw) <= len(rom)
        patches.append(dict(offset=at, bytes=len(raw), beforeSha256=sha(original[at:at+len(raw)]), sha256=sha(raw), kind=kind))
        rom[at:at+len(raw)] = raw
    portraits = meta['components']['portraits']
    badges = meta['components']['reviewedMenuBadges']
    for row in plan['jobs']:
        im = Image.open(source(row['portrait']))
        assert im.mode == 'P' and im.size == (48, 56) and max(im.get_flattened_data()) < 48
        pid = row['portraitPalette']
        pal = palette_decode(original, PALETTES[0], pid)
        assert im.getpalette()[:144] == [((w >> s)&31)*255//31 for w in struct.unpack('<48H', pal) for s in (0,5,10)]
        # Transport only: do not resize the reviewed 48x56 image. Native menu
        # OAM flips this object horizontally, so invert that flip in storage.
        # Palette window is OBJ96..143; index zero stays transparent and opaque
        # source indices 1..47 become OBJ97..143 (not arbitrary new colors).
        transport = Image.new('P', (64,64))
        palette = [0]*768
        palette[288:432] = im.getpalette()[:144]
        transport.putpalette(palette)
        shifted = im.transpose(Image.Transpose.FLIP_LEFT_RIGHT).point(lambda v: v+96 if v else 0)
        transport.paste(shifted, (8,8))
        transport.info['transparency'] = 0
        raw = pack(transport)
        dest = next(j for j in portraits['jobs'] if j['job'] == row['job'])
        at = entry(original, portraits['pixelArchive'], dest['portrait'])
        _, end = decode(original, at)
        # The authenticated parent already owns this slot. Equal encoded length
        # prevents overwriting the next archive entry or silently relocating it.
        assert end-at == len(encode(raw))
        patch(at, encode(raw), 'portrait-'+row['slug'])
        # Reuse original palette records, not newly authored palette payloads.
        patch(dest['record']+14, bytes([pid,pid]), 'native-portrait-selector-'+row['slug'])
        target = OUT/'native'/(row['slug']+'-portrait-transport.png')
        transport.save(target)
        dest.update(paletteIDs=[pid,pid], pixelsSha256=sha(raw), paletteSha256=sha(pal),
                    paletteModeSha256=[sha(palette_decode(original, archive, pid)) for archive in PALETTES],
                    nativeImage=str(target), portraitWindow=[48,56], source=row['portrait']['path'],
                    sourceSha256=row['portrait']['sha256'], reviewedPortraitPlan=str(PLAN))
        for ref in ('icon', 'ineligibleBadge'): source(row[ref])
        image = Image.open(source(row['badge']))
        assert image.mode == 'P' and image.size == (32,16)
        raw = pack_tiles(image, 8)
        at = badges['offset']+(row['job']-116)*256
        # The approval page uses live game lettering. Preserve all pixels
        # outside the head, verifying against that authenticated review.
        patch(at, raw, 'badge-'+row['slug'])
        dest = next(j for j in badges['jobs'] if j['job'] == row['job'])
        bank = row['badgeBank']; offset = 0x419d60+(bank-13)*32
        assert image.getpalette()[:48] == [((w>>s)&31)*255//31 for w in struct.unpack_from('<16H', original, offset) for s in (0,5,10)]
        dest['badge'].update(**row['badge'], paletteBank=bank, paletteOffset=offset,
                             paletteSha256=sha(original[offset:offset+32]), tileSha256=sha(raw))
        dest['status'] = 'user-approved-first-pass'
    # Existing native job icon donor property: Dancer now uses the same native
    # plum icon colors as Mystic Knight. No code, palette, or bank is added.
    donors = bytes([6,3,13,15,25,27,41,36,29,30])
    assert original.count(donors) == 1 and original.find(donors) == 0x11064b0
    patch(0x11064b8, bytes([30]), 'dancer-native-icon-donor')
    for row in plan['walk']:
        # Only four approved color revisions; neutral p001/p004 and all native
        # sequence timings/control records are inherited unchanged. These are
        # 32x32 body PNGs, not the 64x64 canvases used by the review page.
        path = source(row['image']); im = Image.open(path)
        assert im.mode == 'P' and im.size == (32,32)
        asset = next(a for a in meta['components']['reviewedActions']['assets'] if a['job']==116 and a['pose']==row['pose'])
        assert im.getpalette()[:48] == [((w>>s)&31)*255//31 for w in struct.unpack_from('<16H',original,asset['nativePaletteOffset']) for s in (0,5,10)]
        # tileSha256 authenticates packed 4bpp bytes, not im.tobytes() indices.
        raw = pack_tiles(im,16)
        assert sha(original[asset['tile']:asset['tile']+512]) == asset['tileSha256']
        patch(asset['tile'],raw,'samurai-walk-'+row['pose'])
        asset.update(source=row['image']['path'],sourceSha256=row['image']['sha256'],tileSha256=sha(raw),status='user-approved-first-pass',nativeColorConversion=dict(method='Exact approved round8 native indices',approvalPlan=str(PLAN)))
    # The allowlist is the import boundary: 35 data patches in this receipt.
    # Prove palette payloads, executable code and animation records stayed
    # unchanged instead of inferring that from a successful PNG round trip.
    allowed = {i for p in patches for i in range(p['offset'],p['offset']+p['bytes'])}
    assert len(rom)==len(original) and all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
    digest = hashlib.sha1(rom).hexdigest()
    target = OUT/digest/'FFTA_Approved_First_Pass.gba'
    target.parent.mkdir(exist_ok=True)
    if target.exists(): assert target.read_bytes()==rom
    else: target.write_bytes(rom)
    meta.update(path=str(target),romSha1=digest,romSha256=sha(rom),source=parent['path'],baseRomSha1=parent['romSha1'])
    badges.update(sha256=sha(rom[badges['offset']:badges['offset']+badges['bytes']]),productionAccepted=True)
    preview=meta['components']['preview'];start=preview['reservation'][0]
    preview['binarySha256']=sha(rom[start:start+preview['bytes']]);preview['portraits']=copy.deepcopy(badges['jobs'])
    portraits['scope']='Approved exact48x56 art; original native palette IDs and color modes, fixed transport placement. No palette payload changes.'
    meta['components']['approvedRound8']=dict(plan=str(PLAN),planSha256=sha(PLAN.read_bytes()),parentManifest=str(parent_path),parentManifestSha256=sha(parent_path.read_bytes()),patches=patches,productionAccepted=True,scope=__doc__)
    meta['archivedManifest']=str(target.parent/'manifest.json')
    content=(json.dumps(meta,indent=2)+'\n').encode()
    archive=Path(meta['archivedManifest'])
    if archive.exists(): assert archive.read_bytes()==content
    else: archive.write_bytes(content)
    (OUT/'candidate.json').write_bytes(content)
    print(json.dumps(dict(romSha1=digest,patches=len(patches),manifest=str(OUT/'candidate.json'))))
    return meta


if __name__ == '__main__': build()
