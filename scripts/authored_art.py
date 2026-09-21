"""Record manually drawn indexed PNGs as reproducible text; never invent pixels.

PNG/editor files remain private. A source record contains only authored pixels,
palette and provenance; rendering reverses the index remap exactly. This is not
a native-animation importer or artistic acceptance check.
"""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image

def sha(data):return hashlib.sha256(data).hexdigest()
def record(source,destination,description):
    with Image.open(source) as png:
        assert png.mode=='P','Use an indexed canvas in the editor'
        assert png.info.get('transparency')==0,'Transparent background must use index zero'
        used=[0]+sorted(set(png.tobytes())-{0})
        assert len(used)<=16,'At most fifteen visible colors plus transparency'
        remap={old:new for new,old in enumerate(used)}
        pixels=bytes(remap[v] for v in png.tobytes())
        palette=png.getpalette()
        colors=[palette[i*3:i*3+3] for i in used]
        result=dict(schema=1,kind='authored-pixel-draft',status='Construction draft; not accepted for production',
                    authorship=description,width=png.width,height=png.height,paletteRgb=colors,
                    transparentIndex=0,rows=[pixels[y*png.width:(y+1)*png.width].hex() for y in range(png.height)],
                    pixelEncoding='two hex digits per palette index',pixelSha256=sha(pixels),
                    rgbaSha256=sha(png.convert('RGBA').tobytes()))
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(result,indent=2)+'\n')
    # Reconstruct in memory, preserving every visible color and transparent RGB.
    assert sha(render(result).convert('RGBA').tobytes())==result['rgbaSha256']
    return dict(path=str(destination),colors=len(used),pixelSha256=result['pixelSha256'])

def render(spec):
    assert spec['schema']==1 and spec['kind']=='authored-pixel-draft'
    pixels=b''.join(bytes.fromhex(row) for row in spec['rows'])
    assert len(spec['rows'])==spec['height']
    assert all(len(row)==spec['width']*2 for row in spec['rows'])
    assert sha(pixels)==spec['pixelSha256'] and max(pixels)<len(spec['paletteRgb'])<=16
    image=Image.frombytes('P',(spec['width'],spec['height']),pixels)
    colors=[v for color in spec['paletteRgb'] for v in color]
    image.putpalette(colors+[0]*(768-len(colors)));image.info['transparency']=0
    return image

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('record','render'))
    parser.add_argument('source',type=Path);parser.add_argument('destination',type=Path)
    parser.add_argument('--authorship',default='')
    args=parser.parse_args()
    if args.mode=='record':
        assert args.authorship,'Record actual drawing provenance explicitly'
        print(json.dumps(record(args.source,args.destination,args.authorship)))
    else:
        image=render(json.loads(args.source.read_text()))
        args.destination.parent.mkdir(parents=True,exist_ok=True)
        image.save(args.destination,bits=4)
