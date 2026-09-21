"""Lossless native actor-resource extraction; private references, not new artwork.

The preview is assembled from native OAM. Edit tile atlases, not flattened
previews: overlapping/hidden object pixels remain in the tile atlas. Unknown
frame/sequence metadata is preserved verbatim and separately inventoried.
"""
import hashlib
import json
import struct
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SHAPES = (((8,8),(16,16),(32,32),(64,64)),
          ((16,8),(32,8),(32,16),(64,32)),
          ((8,16),(8,32),(16,32),(32,64)))
TILES, OAM, ANIM, SIZES = 0x69b89c, 0x852e7c, 0x390e44, 0x391224
def sha(data): return hashlib.sha256(data).hexdigest()
def u16(data, p): return struct.unpack_from('<H', data, p)[0]
def u32(data, p): return struct.unpack_from('<I', data, p)[0]
def romoff(pointer, rom):
    assert 0x08000000 <= pointer < 0x08000000+len(rom), hex(pointer)
    return pointer-0x08000000
def palette(rom, offset):
    raw=rom[offset:offset+32]; assert len(raw)==32
    rgb=[((v>>shift)&31)*255//31 for v in struct.unpack('<16H',raw) for shift in (0,5,10)]
    return raw,rgb
def tile_image(raw, rgb, width=128):
    assert len(raw)%32==0 and width%8==0
    n=len(raw)//32; height=max(8,((n+width//8-1)//(width//8))*8)
    image=Image.new('P',(width,height)); image.putpalette(rgb+[0]*(768-len(rgb)))
    pixels=image.load()
    for tile in range(n):
        for y in range(8):
            for x in range(8):
                byte=raw[tile*32+y*4+x//2]
                pixels[(tile%(width//8))*8+x,(tile//(width//8))*8+y]=(byte>>(4*(x%2)))&15
    image.info['transparency']=0
    return image
def pack_tiles(image, count):
    assert image.mode=='P' and image.width%8==0
    assert count*64<=image.width*image.height
    p=image.load();out=bytearray()
    for t in range(count):
        tx=t%(image.width//8)*8;ty=t//(image.width//8)*8
        for y in range(8):
            for x in range(0,8,2):
                a,b=p[tx+x,ty+y],p[tx+x+1,ty+y]
                assert 0<=a<16 and 0<=b<16,'Requires indexed 4bpp pixels'
                out.append(a|b<<4)
    return bytes(out)
def layout(rom, offset):
    n=u16(rom,offset); assert 0<n<=128
    objects=[]
    for k in range(n):
        a,b,c=struct.unpack_from('<3H',rom,offset+2+k*6)
        assert a>>14<3 and not a&0x2000,'Unsupported affine/8bpp layout'
        assert not a&0x100,'Affine OAM requires a separate renderer'
        w,h=SHAPES[a>>14][b>>14]
        x=b&511;y=a&255
        objects.append(dict(attributes=[a,b,c],x=x-512 if x>=256 else x,
                            y=y-256 if y>=128 else y,width=w,height=h,
                            tile=c&1023,flipH=bool(b&4096),flipV=bool(b&8192)))
    raw=struct.pack('<H',n)+b''.join(struct.pack('<3H',*o['attributes']) for o in objects)
    assert raw==rom[offset:offset+len(raw)]
    return objects,raw
def compose(raw, objects, rgb):
    atlas=tile_image(raw,rgb,128);result=Image.new('P',(96,96));result.putpalette(atlas.getpalette())
    # Lowest OAM index wins where objects overlap. Transparent index zero skips.
    for obj in reversed(objects):
        w,h=obj['width'],obj['height'];part=Image.new('P',(w,h));part.putpalette(atlas.getpalette())
        for y in range(h//8):
            for x in range(w//8):
                t=obj['tile']+y*(w//8)+x
                part.paste(atlas.crop(((t%16)*8,(t//16)*8,(t%16)*8+8,(t//16)*8+8)),(x*8,y*8))
        if obj['flipH']:part=part.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if obj['flipV']:part=part.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        # Test the palette INDEX, not its RGB luminance. Converting a P-mode
        # 0/255 lookup result to L applies the palette and can erase every pixel.
        mask=Image.frombytes('L',part.size,part.tobytes()).point(lambda v:255 if v else 0)
        result.paste(part,(48+obj['x'],64+obj['y']),mask)
    result.info['transparency']=0
    return result

def extract_actor(rom, idx, out, rgb):
    pointers=[romoff(u32(rom,ANIM+i*4),rom) for i in range((SIZES-ANIM)//4)]
    p=pointers[idx];end=next((v for v in sorted(set(pointers)) if v>p),None)
    assert end and (end-p)%12==0 and 1<=(end-p)//12<=256,('extent',idx)
    out.mkdir(parents=True,exist_ok=True)
    slots=[];poses={};segments={}
    def remember(off,data):
        assert data==rom[off:off+len(data)]
        segments[str(off)]=dict(bytes=len(data),sha256=sha(data),hex=data.hex())
    for slot in range((end-p)//12):
        descriptor=rom[p+slot*12:p+(slot+1)*12]
        pointer=u32(descriptor,0)
        entry=dict(slot=slot,descriptorOffset=p+slot*12,descriptor=descriptor.hex(),frames=[])
        remember(p+slot*12,struct.pack('<3I',*struct.unpack('<3I',descriptor)))
        if pointer:
            q=romoff(pointer,rom);count=u32(rom,q);assert 0<count<=256,(idx,slot,count)
            remember(q,struct.pack('<I',count))
            for frame in range(count):
                f=q+4+20*frame;values=struct.unpack_from('<IIBB5H',rom,f)
                t,o=values[:2];objects,oam=layout(rom,OAM+o)
                count_tiles=max(x['tile']+x['width']*x['height']//64 for x in objects)
                raw=rom[TILES+t:TILES+t+count_tiles*32];assert len(raw)==count_tiles*32
                key=f'{t:06x}-{o:06x}'
                if key not in poses:
                    img=tile_image(raw,rgb);img.save(out/f'{key}-tiles.png',bits=4)
                    with Image.open(out/f'{key}-tiles.png') as saved:
                        rebuilt=pack_tiles(saved,count_tiles)
                    remember(TILES+t,rebuilt);remember(OAM+o,oam)
                    compose(raw,objects,rgb).save(out/f'{key}-pose.png',bits=4)
                    poses[key]=dict(tileOffset=TILES+t,oamOffset=OAM+o,tileCount=count_tiles,
                                    tileSha256=sha(raw),objects=objects)
                remember(f,struct.pack('<IIBB5H',*values))
                entry['frames'].append(dict(offset=f,pose=key,duration=values[2],command=values[3],params=values[4:]))
        slots.append(entry)
    remember(SIZES+idx*2,struct.pack('<H',u16(rom,SIZES+idx*2)))
    manifest=dict(id=idx,tableOffset=p,size=u16(rom,SIZES+idx*2),slots=slots,poses=poses,segments=segments)
    (out/'native.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest

def main():
    rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    assert hashlib.sha1(rom).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
    out=ROOT/'build/art/native-reference';out.mkdir(parents=True,exist_ok=True)
    # Native color-mode banks selected by CBA3C; preserve raw palette words.
    banks={str(mode):[dict(offset=base+i*32,raw=palette(rom,base+i*32)[0].hex()) for i in range(87)]
           for mode,base in enumerate((0x419d60,0x41b340,0x41a860))}
    jobs=[];resources={};errors=[];rebuilt=bytearray(rom)
    for j in range(2,116):
        rec=0x521a14+j*52
        jobs.append(dict(id=j,race=rom[rec+4],land=u16(rom,rec+7),water=u16(rom,rec+9),
                         paletteLow=rom[rec+11]&15,paletteHigh=rom[rec+11]>>4,
                         portrait=list(rom[rec+13:rec+16])))
        for idx in (u16(rom,rec+7),u16(rom,rec+9)):
            if idx in resources or any(e['id']==idx for e in errors):continue
            try:
                # Reference color bank zero for all resources; per-job selectors
                # are retained, and actual job palette routing is a runtime gate.
                m=extract_actor(rom,idx,out/f'actor-{idx:03}',palette(rom,0x41a860)[1]);resources[idx]=m
                for off,segment in m['segments'].items():
                    raw=bytes.fromhex(segment['hex']);assert sha(raw)==segment['sha256']
                    rebuilt[int(off):int(off)+len(raw)]=raw
            except (AssertionError,IndexError,struct.error) as error:
                errors.append(dict(id=idx,error=str(error)))
    assert rebuilt==rom,'Unchanged native resource import differs'
    report=dict(sourceSha1=hashlib.sha1(rom).hexdigest(),romRoundtripSha256=sha(rebuilt),jobs=jobs,
                palettes=banks,resourceCount=len(resources),poseCount=sum(len(m['poses']) for m in resources.values()),
                frameRecords=sum(len(s['frames']) for m in resources.values() for s in m['slots']),
                errors=errors,limitations=['Reference previews currently use one authenticated native palette bank; per-job routing requires native proof.',
                                         'No custom artwork or live animation import acceptance. Unsupported resources are explicitly listed.'])
    (out/'library.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('jobs','palettes')},indent=2))
def rebuild_previews():
    """Refresh composed views from authenticated exports without re-extraction."""
    rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    assert hashlib.sha1(rom).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
    rgb=palette(rom,0x41a860)[1];count=nonempty=0
    for path in sorted((ROOT/'build/art/native-reference').glob('actor-*/native.json')):
        manifest=json.loads(path.read_text())
        for key,pose in manifest['poses'].items():
            raw=rom[pose['tileOffset']:pose['tileOffset']+32*pose['tileCount']]
            assert sha(raw)==pose['tileSha256']
            objects,_=layout(rom,pose['oamOffset'])
            assert objects==pose['objects']
            image=compose(raw,objects,rgb)
            image.save(path.parent/f'{key}-pose.png',bits=4)
            count+=1;nonempty+=bool(image.getbbox())
    result=dict(poses=count,nonempty=nonempty,scope='Reference previews only; single palette routing remains incomplete')
    (ROOT/'build/art/native-reference/preview-report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rebuild-previews',action='store_true')
    args=parser.parse_args()
    if args.rebuild_previews:rebuild_previews()
    else:main()
