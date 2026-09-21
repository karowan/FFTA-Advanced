"""Bounded six-pose imagegen idle replacement on the assembled technical build.

Preserves the native four-entry A/B/C/B cadence and all other consumers.
This is a technical draft, not production artwork acceptance.
"""
import hashlib, importlib.util, json, struct
from pathlib import Path
from PIL import Image
from native_art import ROOT, TILES, OAM, sha, pack_tiles, palette
from native_table_literals import authenticate

START, END = 0x1f8c000, 0x1f90000

def build(publish_current=True):
    base = json.loads((ROOT/'build/art/assembled/current.json').read_text())
    original = Path(base['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest() == base['romSha1']
    clean = (ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes(); authenticate(clean)
    spec = json.loads((ROOT/'src/art/imagegen/samurai-march-study.json').read_text())['revision']
    source = ROOT/spec['source']
    assert sha(source.read_bytes()) == spec['sourceSha256']
    assets = ROOT/spec['conversion']
    pal, rgb = palette(original, 0x419d80)
    settings = spec['conversionSettings']
    assert settings == dict(columns=3,rows=2,height=30,resampling='nearest',nativePaletteOffset='0x419d80')
    # Reproduce directly from the generated PNG, not cached converted tiles.
    module_spec=importlib.util.spec_from_file_location('sprite_conversion',ROOT/'scripts/convert-generated-sprites.py')
    converter=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(converter)
    converter.convert(source,assets,columns=3,rows=2,height=30,resampling='nearest',target_palette=pal)
    proof = json.loads((assets/'manifest.json').read_text())
    assert proof['sourceSha256'] == spec['sourceSha256'] and len(proof['frames']) == 6
    assert (assets/'palette.bin').read_bytes() == pal == clean[0x419d80:0x419da0]
    assert original[START:END] == b'\xff'*(END-START), 'Reservation occupied'
    rom = bytearray(original); cursor = START; segments = []
    def add(raw, kind):
        nonlocal cursor
        cursor = (cursor+3)&~3; p = cursor; cursor += len(raw)
        assert cursor <= END
        rom[p:cursor] = raw
        segments.append(dict(offset=p, bytes=len(raw), kind=kind, sha256=sha(raw)))
        return p
    frames = []
    for i, f in enumerate(proof['frames']):
        with Image.open(assets/f'frame-{i:02}.png') as image:
            assert image.mode == 'P' and image.size == (32,32)
            raw = pack_tiles(image,16)
            assert sha(raw) == f['tileSha256']
            assert image.getpalette()[3:48] == rgb[3:48]
            assert max(image.getdata()) <= 15 and image.info.get('transparency') == 0
            bottom = image.getbbox()[3]
        tiles = add(raw, 'idle-tiles')
        # Original human foot baseline is -5 relative to native actor origin.
        dy = -5-bottom
        oam = add(struct.pack('<4H',1,dy&255,0x8000|((-16)&511),0), 'idle-oam')
        frames.append(dict(sourceFrame=i, tile=tiles, oam=oam, sha256=sha(raw), objectY=dy))
    table = struct.unpack_from('<I',original,0x2102c)[0]-0x08000000
    entry = table+256*4; olddesc = struct.unpack_from('<I',original,entry)[0]-0x08000000
    resource = next(r for r in base['components']['classResources']['resources'] if r['id']==256)
    desc = bytearray(original[olddesc:olddesc+12*resource['slots']]); sequences = []
    for slot, order in enumerate(((0,1,2,1),(3,4,5,4))):
        old = struct.unpack_from('<I',desc,slot*12)[0]-0x08000000
        assert struct.unpack_from('<I',original,old)[0] == 4
        seq = bytearray(original[old:old+84])
        assert [seq[12+20*f] for f in range(4)] == [16,8,16,8]
        for f, i in enumerate(order):
            assert seq[13+20*f] == 1
            struct.pack_into('<II',seq,4+20*f,frames[i]['tile']-TILES,frames[i]['oam']-OAM)
        target = add(seq,'idle-sequence'); struct.pack_into('<I',desc,slot*12,target+0x08000000)
        sequences.append(dict(slot=slot,source=old,target=target,frames=list(order)))
    newdesc = add(desc,'land-descriptors'); struct.pack_into('<I',rom,entry,newdesc+0x08000000)
    assert rom[:entry] == original[:entry] and rom[entry+4:START] == original[entry+4:START]
    assert rom[cursor:] == original[cursor:] and len(rom) == len(original)
    digest = hashlib.sha1(rom).hexdigest(); root = ROOT/'build/art/samurai-idle'; out = root/digest; out.mkdir(parents=True,exist_ok=True)
    path = out/'FFTA_Samurai_Idle_Draft.gba'; path.write_bytes(rom)
    result = dict(path=str(path),romSha1=digest,source=base['path'],baseRomSha1=base['romSha1'],
        fixtureSource=base['source'],sourceSha256=spec['sourceSha256'],conversionManifest=str(assets/'manifest.json'),
        conversionManifestSha256=sha((assets/'manifest.json').read_bytes()),resource=256,job=116,table=table,entry=entry,
        sourceDescriptors=olddesc,descriptors=newdesc,slots=resource['slots'],frames=frames,sequences=sequences,
        reservation=[START,END],used=[START,cursor],segments=segments,paletteSha256=sha(pal),productionAccepted=False,
        scope='Six generated poses, native A/B/C/B idle cadence, unchanged native actor palette. Only Samurai land idle slots0/1 replaced; all other ROM bytes preserved. Unaccepted art draft; menu miniature/portrait/action/water visuals remain packaged versions.')
    for p in ((out/'manifest.json',root/'current.json') if publish_current else (out/'manifest.json',)):
        p.write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__ == '__main__':
    meta=build(); print(json.dumps(dict(path=meta['path'],romSha1=meta['romSha1'])))
