"""Import imagegen status pixels through the existing dedicated status consumer.

Only the two owned Exposed/Centered glyph payloads change. Native selectors,
timing, layout, palette, other statuses and all gameplay code are preserved.
"""
import ast,hashlib,json
from pathlib import Path
from PIL import Image
from native_art import ROOT,sha,palette,pack_tiles

def build(base_manifest=None, *, publish_current=True):
    parentpath=Path(base_manifest) if base_manifest else ROOT/'build/art/generated-actions/current.json'
    parent=json.loads(parentpath.read_text())
    original=Path(parent['path']).read_bytes();assert hashlib.sha1(original).hexdigest()==parent['romSha1']
    # Authenticate the established source glyph payload without running its
    # historical hand-drawing generator or authoring any new pixels in code.
    tree=ast.parse((ROOT/'scripts/generate-status-glyphs.py').read_text())
    glyphs=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and
                any(isinstance(t,ast.Name) and t.id=='glyphs' for t in n.targets))
    old=bytes(int(row[x],16)|(int(row[x+1],16)<<4) for g in glyphs for row in g for x in range(0,8,2))
    offset=original.find(old);assert offset>=0 and original.find(old,offset+1)<0 and len(old)==128
    root=ROOT/'build/art/generated-status';work=root/'conversion';work.mkdir(parents=True,exist_ok=True)
    specpath=ROOT/'src/art/imagegen/status-transport-prompts.json';spec=json.loads(specpath.read_text());source=ROOT/spec['source']
    assert sha(source.read_bytes())==spec['sourceSha256']
    image=Image.open(source).convert('RGBA');assert image.getchannel('A').getextrema()==(0,255)
    pal,rgb=palette(original,0x419d60);frames=[];pixels=b''
    for i,name in enumerate(('Exposed','Centered')):
        crop=image.crop((image.width*i//2,0,image.width*(i+1)//2,image.height))
        mask=crop.getchannel('A').point(lambda v:255 if v>=128 else 0);bounds=mask.getbbox();assert bounds
        crop=crop.crop(bounds);crop.thumbnail((8,16),Image.Resampling.NEAREST)
        indexed=Image.new('P',(8,16));indexed.putpalette(rgb+[0]*(768-len(rgb)));indexed.info['transparency']=0
        dx=(8-crop.width)//2;dy=(16-crop.height)//2
        for y in range(crop.height):
            for x in range(crop.width):
                r,g,b,a=crop.getpixel((x,y))
                if a>=128:indexed.putpixel((dx+x,dy+y),min(range(1,16),key=lambda c:sum((v-rgb[c*3+k])**2 for k,v in enumerate((r,g,b)))))
        raw=pack_tiles(indexed,2);assert any(raw) and raw!=old[i*64:(i+1)*64]
        indexed.save(work/(name.lower()+'.png'),bits=4);pixels+=raw
        frames.append(dict(status=25+i,name=name,sourceHalf=i,sourceBounds=list(bounds),scaled=list(crop.size),tile=0x1e0+2*i,sha256=sha(raw)))
    rom=original[:offset]+pixels+original[offset+128:]
    assert len(rom)==len(original) and rom[:offset]==original[:offset] and rom[offset+128:]==original[offset+128:]
    digest=hashlib.sha1(rom).hexdigest();out=root/digest;out.mkdir(parents=True,exist_ok=True);path=out/'FFTA_Generated_Status.gba';path.write_bytes(rom)
    result=dict(path=str(path),romSha1=digest,source=parent['path'],baseRomSha1=parent['romSha1'],releaseSource=parent['releaseSource'],
                offset=offset,bytes=128,originalSha256=sha(old),pixelsSha256=sha(pixels),paletteOffset=0x419d60,paletteSha256=sha(pal),
                sourceArt=spec['source'],sourceArtSha256=spec['sourceSha256'],promptSha256=sha(specpath.read_bytes()),frames=frames,
                scope='Two generated status glyph pixel payloads only, using existing native status storage/palette/shape/selector. Temporary conversion; actual consumer acceptance separate. Other custom statuses, equipment, effects and production art remain open.')
    for p in ((out/'manifest.json',root/'current.json') if publish_current else (out/'manifest.json',)):p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(romSha1=digest,offset=offset,bytes=128)));return result

if __name__=='__main__':build()
