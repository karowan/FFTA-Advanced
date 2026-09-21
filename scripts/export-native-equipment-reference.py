"""Private original16x16 equipment/quest references with native mode0 palettes."""
import hashlib,json
from native_art import ROOT,sha,palette,tile_image,pack_tiles
from native_miniatures import decode
rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
assert hashlib.sha1(rom).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
container=0x3c83fc;count=int.from_bytes(rom[container+2:container+4],'big');assert count==522
out=ROOT/'build/art/native-reference/equipment-original';out.mkdir(parents=True,exist_ok=True)
records=[];unsupported=[]
for i in range(count):
    try:raw=decode(rom,container,i)
    except (AssertionError,IndexError) as error:
        unsupported.append(dict(index=i,error=repr(error)));continue
    assert len(raw)==128
    # Native CB99C selects this nibble; CBA3C maps mode0 to419D60.
    bank=rom[0x3c7fe4+4+i*2]>>4;pal,rgb=palette(rom,0x419d60+bank*32)
    image=tile_image(raw,rgb,16);assert pack_tiles(image,4)==raw
    path=out/f'icon-{i:03}.png';image.save(path,bits=4)
    records.append(dict(index=i,pixelsSha256=sha(raw),paletteBank=bank,paletteSha256=sha(pal),pngSha256=sha(path.read_bytes())))
assert not unsupported and len(records)==522,unsupported
report=dict(status='passed',sourceSha1=hashlib.sha1(rom).hexdigest(),records=records,unsupported=unsupported,
            scope='522 authenticated clean-ROM indexed16x16 equipment/quest images, native CB99C mode0 palette selectors, exact4bpp pixel roundtrips. Shipping expansion corruption at467/469 is separate; no custom art or blanket consumer acceptance.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status='passed',images=len(records),unsupported=unsupported,report=str(out/'report.json'))))
