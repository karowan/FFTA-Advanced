"""Append a generated transport draft to the native menu-figure container.

Keeps the 54 original images and all existing actor mappings intact. Extends
only private Samurai resource256. This is not approved production artwork.
"""
import hashlib,json,struct
from pathlib import Path
from PIL import Image
from native_art import ROOT,sha,palette,tile_image,pack_tiles
from native_miniatures import CONTAINER,LITERALS,decode,encode
from native_actor_import import PARTY_LITERALS,END

def build():
    base=json.loads((ROOT/'build/art/generated-actor-poc/current.json').read_text())
    relocation=json.loads((ROOT/'build/art/actor-import/current.json').read_text())
    original=Path(base['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==base['romSha1']
    assert base['relocationRomSha1']==relocation['romSha1']
    originals=[decode(original,CONTAINER,i) for i in range(54)]
    _,source_rgb=palette(original,base['nativePaletteReference'])
    # Selected Samurai job-wheel bank4, observed in the retained failed
    # hardware capture. This consumer does not use the battle/icon palette.
    menu_palette=0x94ee5c
    _,rgb=palette(original,menu_palette)
    raw=original[base['frames'][0]['tile']:base['frames'][0]['tile']+512]
    assert sha(raw)==base['frames'][0]['sha256']
    source_image=tile_image(raw,source_rgb,32)
    draft=Image.new('P',(32,32));draft.putpalette(rgb+[0]*(768-len(rgb)))
    mapping=[0]+[min(range(1,16),key=lambda c:sum((source_rgb[index*3+k]-rgb[c*3+k])**2 for k in range(3))) for index in range(1,16)]
    draft.putdata([mapping[index] for index in source_image.tobytes()])
    native=tile_image(originals[4],rgb,32)
    baseline=native.getbbox()[3]
    offset=baseline-draft.getbbox()[3]
    assert 0<=offset<=8
    image=Image.new('P',(32,40));image.putpalette(draft.getpalette())
    image.paste(draft,(0,offset));image.info['transparency']=0
    generated=pack_tiles(image,20)
    container=encode(originals+[generated])
    rom=bytearray(original);start=(base['used'][1]+3)&~3;end=start+len(container)
    assert end<=END and rom[start:end]==b'\xff'*len(container)
    rom[start:end]=container
    for literal in LITERALS:
        assert struct.unpack_from('<I',rom,literal)[0]==0x08000000+CONTAINER
        struct.pack_into('<I',rom,literal,0x08000000+start)
    tables=[struct.unpack_from('<I',rom,p)[0]-0x08000000 for p in PARTY_LITERALS]
    assert tables==[relocation['partyTable']]*3
    entry=tables[0]+256*2
    assert rom[entry:entry+2]==original[0x393f0c+4*2:0x393f0c+4*2+2]
    rom[entry]=54
    allowed=set(range(start,end))|{entry}
    for p in LITERALS:allowed.update(range(p,p+4))
    assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
    for i,old in enumerate(originals):assert decode(rom,start,i)==old
    assert decode(rom,start,54)==generated
    digest=hashlib.sha1(rom).hexdigest()
    root=ROOT/'build/art/generated-miniature-poc';out=root/digest;out.mkdir(parents=True,exist_ok=True)
    path=out/'generated-miniature.gba';path.write_bytes(rom)
    image.save(out/'temporary-samurai.png',bits=4)
    report=dict(path=str(path),romSha1=digest,source=str(Path(base['path'])),baseRomSha1=base['romSha1'],
        comparisonSource=relocation['path'],comparisonRomSha1=relocation['romSha1'],
        used=[base['used'][0],end],container=start,containerSha256=sha(container),imageIndex=54,
        imageSha256=sha(generated),imageBytes=generated.hex(),actor=256,job=116,mappingEntry=entry,
        sourceFrameSha256=sha(raw),nativePaletteReference=menu_palette,paletteIndexMapping=mapping,
        baseline=baseline,offsetY=offset,sourceManifestSha256=sha((ROOT/'build/art/generated-actor-poc/current.json').read_bytes()),
        scope='Temporary built-in imagegen Samurai menu figure appended without replacing any original image. Generated land idle retained. No production art, other actions/water/portraits or delivery acceptance.')
    for p in (out/'manifest.json',root/'current.json'):p.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(romSha1=digest,path=str(path),containerBytes=len(container))))
    return report

if __name__=='__main__':build()
