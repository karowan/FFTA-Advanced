"""Convert existing imagegen drafts into temporary native menu portraits.

No character pixels are drawn. The fixed head-region extraction is recorded
and deliberately provisional, pending dedicated generated portrait artwork.
"""
import json
from PIL import Image
from native_art import ROOT,sha,palette,pack_tiles

def compile_portraits(out):
    catalog=json.loads((ROOT/'src/art/imagegen/catalog.json').read_text())
    old=json.loads((ROOT/'src/art/job-portraits.json').read_text())
    banks={p['job']:p['paletteBank'] for p in old['portraits']}
    rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    records=[];blobs=[]
    for job in catalog['jobs']:
        number=job['job'];manifest=ROOT/job['technicalConversion']
        provenance=json.loads(manifest.read_text())
        assert sha((ROOT/job['privateSource']).read_bytes())==job['sourceSha256']
        assert provenance['sourceSha256']==job['sourceSha256']
        frame=manifest.parent/'frame-00.png'
        with Image.open(frame) as source:
            assert sha(pack_tiles(source,16))==provenance['frames'][0]['tileSha256']
            source=source.convert('RGBA')
            bounds=source.getbbox();assert bounds
            left,top,right,bottom=bounds
            # Extraction only. Retain the upper half of the existing figure;
            # final portrait source/crop can replace this explicit contract.
            crop=(left,top,right,top+(bottom-top+1)//2)
            part=source.crop(crop)
            factor=min(16/part.width,14/part.height)
            size=(max(1,round(part.width*factor)),max(1,round(part.height*factor)))
            part=part.resize(size,Image.Resampling.NEAREST)
        _,rgb=palette(rom,0x419d60+32*(banks[number]-13))
        image=Image.new('P',(32,16),12);image.putpalette(rgb+[0]*(768-len(rgb)))
        # Existing UI's neutral panel/frame, not character construction.
        for y in range(16):
            for x in range(32):
                if x in (0,31) or y in (0,15):image.putpixel((x,y),1)
                elif x<18:image.putpixel((x,y),3)
        x0=1+(16-size[0])//2;y0=1+(14-size[1])//2
        for y in range(size[1]):
            for x in range(size[0]):
                pixel=part.getpixel((x,y))
                if pixel[3]:
                    color=min(range(1,16),key=lambda c:sum((pixel[k]-rgb[c*3+k])**2 for k in range(3)))
                    image.putpixel((x0+x,y0+y),color)
        raw=pack_tiles(image,8);image.save(out/f'portrait-{number}.png',bits=4)
        blobs.append(raw)
        records.append(dict(job=number,tileSha256=sha(raw),source=job['privateSource'],
            sourceSha256=job['sourceSha256'],conversionManifest=str(manifest.relative_to(ROOT)),
            conversionManifestSha256=sha(manifest.read_bytes()),frameSha256=sha(frame.read_bytes()),
            crop=list(crop),size=list(size),paletteBank=banks[number],
            status='temporary technical extraction; dedicated portrait art and visual acceptance deferred'))
    assert [r['job'] for r in records]==list(range(116,126))
    header='/* Temporary imagegen-derived head crops; not production artwork. */\n'
    header+='static const unsigned char original_job_icons[10][256]={\n'
    header+=',\n'.join('{'+','.join(str(b) for b in raw)+'}' for raw in blobs)+'\n};\n'
    (out/'job-icons.h').write_text(header)
    (out/'portrait-records.json').write_text(json.dumps(records,indent=2)+'\n')
    return records
