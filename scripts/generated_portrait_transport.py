"""Append independent large portraits from existing imagegen sources.

Temporary upper-body crops, not new artwork or accepted portrait designs.
All original pixel/OAM records and palette variants remain byte-preserved.
"""
import hashlib,json,struct
from pathlib import Path
from PIL import Image
from native_art import ROOT,sha
from native_portraits import *
from native_miniatures import decode as palette_decode,encode as palette_encode
START,END=0x1d80000,0x1e80000

def convert(art):
    proofpath=ROOT/art['technicalConversion'];proof=json.loads(proofpath.read_text())
    source=ROOT/art['privateSource'];assert sha(source.read_bytes())==proof['sourceSha256']==art['sourceSha256']
    f=proof['frames'][0];left,top,right,bottom=f['bounds'];bx,by,_,_=f['box']
    crop=(bx+left,by+top,bx+right,by+top+(bottom-top+1)//2)
    with Image.open(source) as im:
        part=im.convert('RGBA').crop(crop)
        scale=min(60/part.width,60/part.height);size=(max(1,round(part.width*scale)),max(1,round(part.height*scale)))
        part=part.resize(size,Image.Resampling.NEAREST)
    # Quantize only existing opaque pixels; index0 stays transparent and the
    # native portrait palette owns OBJ colors96..143 (96 is unused here).
    opaque=[p[:3] for p in part.get_flattened_data() if p[3]>=128];assert opaque
    strip=Image.new('RGB',(len(opaque),1));strip.putdata(opaque)
    quant=strip.quantize(colors=47,method=Image.Quantize.MAXCOVERAGE,dither=Image.Dither.NONE)
    rgb=quant.getpalette()[:141];words=[0]+[sum(round(rgb[i*3+k]*31/255)<<(5*k) for k in range(3)) for i in range(47)]
    pal=struct.pack('<48H',*words);full=[0]*768
    full[96*3:144*3]=[((w>>s)&31)*255//31 for w in words for s in (0,5,10)]
    image=Image.new('P',(64,64));image.putpalette(full);x0=(64-size[0])//2;y0=64-size[1]
    for y in range(size[1]):
        for x in range(size[0]):
            p=part.getpixel((x,y))
            if p[3]>=128:
                c=min(range(47),key=lambda c:sum((p[k]-rgb[c*3+k])**2 for k in range(3)))
                image.putpixel((x0+x,y0+y),97+c)
    image.info['transparency']=0
    return image,pal,dict(crop=list(crop),size=list(size),source=art['privateSource'],sourceSha256=art['sourceSha256'],
        conversionManifest=art['technicalConversion'],conversionManifestSha256=sha(proofpath.read_bytes()))

def build(base_manifest=None, *, publish_current=True):
    basepath=Path(base_manifest) if base_manifest else ROOT/'build/art/generated-classes/current.json';base=json.loads(basepath.read_text())
    original=Path(base['path']).read_bytes();assert hashlib.sha1(original).hexdigest()==base['romSha1']
    rom=bytearray(original);assert rom[START:END]==b'\xff'*(END-START),'Portrait reservation occupied'
    catalogpath=ROOT/'src/art/imagegen/catalog.json';catalog=json.loads(catalogpath.read_text())
    pixels=[];layouts=[];palettes=[[palette_decode(original,b,i) for i in range(165)] for b in PALETTES]
    for i in range(103):
        p=entry(original,PIXELS,i);raw,end=decode(original,p);pixels.append(original[p:end])
        objects,record=layout(original,entry(original,LAYOUTS,i));layouts.append(record)
    jobs=[];images=[];changed=set();cursor=START;segments=[]
    def add(raw,name):
        nonlocal cursor
        cursor=(cursor+3)&~3;p=cursor;cursor+=len(raw);assert cursor<=END
        rom[p:cursor]=raw;segments.append(dict(offset=p,bytes=len(raw),sha256=sha(raw),kind=name));return p
    def redirect(literals,old,new):
        for p in literals:
            assert struct.unpack_from('<I',rom,p)[0]==0x08000000+old
            struct.pack_into('<I',rom,p,0x08000000+new);changed.update(range(p,p+4))
    for art in catalog['jobs']:
        record=next(j['record'] for j in base['classResources']['jobs'] if j['job']==art['job'])
        image,pal,provenance=convert(art);raw=pack(image);pid=len(pixels);palid=len(palettes[0])
        pixels.append(encode(raw));oam=struct.pack('<4H',1,0x20c0,0xc1e0,0);layouts.append(oam)
        for records in palettes:records.extend((pal,pal))
        old=list(rom[record+13:record+16]);rom[record+13:record+16]=bytes((pid,palid,palid+1));changed.update(range(record+13,record+16))
        jobs.append(dict(job=art['job'],name=art['name'],record=record,portrait=pid,paletteIDs=[palid,palid+1],donor=old,
            pixelsSha256=sha(raw),oamSha256=sha(oam),paletteSha256=sha(pal),**provenance));images.append(image)
    pt=add(archive(pixels,4),'113-entry-8bpp-pixels');ot=add(archive(layouts,2),'113-entry-OAM')
    pts=[add(palette_encode(records,96),f'185-entry-palette-mode{mode}') for mode,records in enumerate(palettes)]
    redirect(PIXEL_LITERALS,PIXELS,pt);redirect(LAYOUT_LITERALS,LAYOUTS,ot)
    for literal,old,new in zip(PALETTE_LITERALS,PALETTES,pts):redirect((literal,),old,new)
    changed.update(range(START,cursor));assert all(a==b or i in changed for i,(a,b) in enumerate(zip(original,rom)))
    digest=hashlib.sha1(rom).hexdigest();root=ROOT/'build/art/generated-portraits';out=root/digest;out.mkdir(parents=True,exist_ok=True)
    path=out/'FFTA_Generated_Portraits.gba';path.write_bytes(rom)
    for job,image in zip(jobs,images):image.save(out/f'portrait-{job["job"]}.png')
    meta=dict(path=str(path),romSha1=digest,romSha256=sha(rom),source=base['path'],baseRomSha1=base['romSha1'],
        releaseSource=base['releaseSource'],sourceManifestSha256=sha(basepath.read_bytes()),catalogSha256=sha(catalogpath.read_bytes()),
        reservation=[START,END],used=[START,cursor],pixelArchive=pt,oamArchive=ot,paletteArchives=pts,jobs=jobs,segments=segments,
        scope='Ten independent8bpp large portrait entries and20 palettes in each color mode, from temporary existing-imagegen upper-body crops. Original103 pixel/OAM records and495 palettes preserved. Custom palette alternatives intentionally identical pending art/color-mode tuning. No production-art or rendered-consumer acceptance; not packaged or installed.')
    for p in ((out/'manifest.json',root/'current.json') if publish_current else (out/'manifest.json',)):p.write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps(dict(romSha1=digest,bytes=cursor-START,jobs=len(jobs),path=str(path))));return meta

if __name__=='__main__':build()
