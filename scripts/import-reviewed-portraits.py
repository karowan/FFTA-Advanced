"""Replace only ten owned portrait payloads in an authenticated art candidate.

No actor, miniature, original portrait, pointer or save changes. Existing
fixed-length codecs permit exact in-place replacement without new ROM space.
"""
import argparse,copy,hashlib,json,struct
from pathlib import Path
from PIL import Image,ImageDraw
from native_art import ROOT,sha
from native_portraits import entry,decode,encode,pack
from native_miniatures import decode as palette_decode

def quantize(source):
    im=Image.open(source).convert('RGBA');assert im.size==(64,64)
    # The actual menu portrait window is48px wide and56px tall. Its native
    # anchor flips the portrait; fit its entire silhouette rather than letting
    # the old generic64px OAM offset cut off half of the new face.
    part=im.crop(im.getbbox());part.thumbnail((44,54),Image.Resampling.NEAREST)
    im=Image.new('RGBA',(64,64));im.alpha_composite(part,((64-part.width)//2,64-part.height))
    opaque=[p[:3] for p in im.get_flattened_data() if p[3]>=128];assert opaque
    strip=Image.new('RGB',(len(opaque),1));strip.putdata(opaque)
    q=strip.quantize(colors=47,method=Image.Quantize.MAXCOVERAGE,dither=Image.Dither.NONE)
    rgb=q.getpalette()[:141]
    words=[0]+[sum(round(rgb[i*3+k]*31/255)<<(5*k) for k in range(3)) for i in range(47)]
    colors=[0]*768;colors[288:432]=[((w>>s)&31)*255//31 for w in words for s in (0,5,10)]
    result=Image.new('P',(64,64));result.putpalette(colors)
    for y in range(64):
        for x in range(64):
            p=im.getpixel((x,y))
            if p[3]>=128:
                index=min(range(47),key=lambda i:sum((p[k]-colors[(97+i)*3+k])**2 for k in range(3)))
                result.putpixel((x,y),97+index)
    result.info['transparency']=0
    return result,struct.pack('<48H',*words)

def build(parent_path, output=None):
    parent=json.loads(parent_path.read_text());original=Path(parent['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==parent['romSha1']
    planpath=ROOT/'build/art/reviewed-integration/portraits/generation-plan.json'
    plan=json.loads(planpath.read_text());assert [j['job'] for j in plan['jobs']]==list(range(116,126))
    rom=bytearray(original);component=parent['components']['portraits'];patches=[];converted=[]
    def patch(offset,data,kind):
        before=original[offset:offset+len(data)];rom[offset:offset+len(data)]=data
        patches.append(dict(offset=offset,bytes=len(data),beforeSha256=sha(before),sha256=sha(data),kind=kind))
    for j in plan['jobs']:
        assert j['status']=='generated-reviewed' and j['review']['outputSha256']==j['output']['sha256']
        for key in ('output','generatedSource','template','concept'):
            ref=j[key];assert sha((ROOT/ref['path']).read_bytes())==ref['sha256']
        prior=next(p for p in component['jobs'] if p['job']==j['job'])
        im,pal=quantize(ROOT/j['output']['path']);raw=pack(im)
        address=entry(original,component['pixelArchive'],prior['portrait']);old,end=decode(original,address)
        assert sha(old)==prior['pixelsSha256'] and end-address==len(encode(raw))
        patch(address,encode(raw),'portrait-'+j['slug'])
        oam_address=entry(original,component['oamArchive'],prior['portrait'])
        old_oam=original[oam_address:oam_address+8]
        assert sha(old_oam)==prior['oamSha256'] and old_oam==struct.pack('<4H',1,0x20c0,0xc1e0,0)
        # Native menu flips the object and its origin: authoredX=-56 becomes
        # displayedX=-8 for a64px object. Preserve that native transform.
        new_oam=struct.pack('<4H',1,0x20c0,0xc1c8,0)
        patch(oam_address,new_oam,'portrait-placement-'+j['slug'])
        for mode,archive in enumerate(component['paletteArchives']):
            for index in prior['paletteIDs']:
                assert palette_decode(original,archive,index)==palette_decode(original,archive,prior['paletteIDs'][0])
                assert sha(palette_decode(original,archive,index))==prior['paletteSha256']
                p=archive+int.from_bytes(original[archive+8+index*4:archive+12+index*4],'big')
                assert original[p]==0xdf and original[p+1:p+97]==palette_decode(original,archive,index)
                patch(p+1,pal,f'palette-{mode}-{index}')
        converted.append((j,im,raw,pal))
    allowed={i for p in patches for i in range(p['offset'],p['offset']+p['bytes'])}
    assert len(rom)==len(original) and all(a==b or i in allowed for i,(a,b) in enumerate(zip(rom,original)))
    digest=hashlib.sha1(rom).hexdigest();folder=ROOT/'build/art/reviewed-portraits'/digest
    def immutable(path,data):
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists():assert path.read_bytes()==data,'Immutable output differs: '+str(path)
        else:path.write_bytes(data)
    path=folder/'FFTA_Reviewed_Portraits.gba';immutable(path,bytes(rom))
    provenance=folder/'provenance'/sha(planpath.read_bytes()+parent_path.read_bytes()+Path(__file__).read_bytes())
    immutable(provenance/'plan.json',planpath.read_bytes());immutable(provenance/'parent.json',parent_path.read_bytes())
    immutable(provenance/'import-reviewed-portraits.py',Path(__file__).read_bytes())
    result=copy.deepcopy(parent);result.update(path=str(path),romSha1=digest,romSha256=sha(rom),source=parent['path'],baseRomSha1=parent['romSha1'])
    board=Image.new('RGBA',(960,560),(228,226,220,255));draw=ImageDraw.Draw(board)
    for n,(j,im,raw,pal) in enumerate(converted):
        ref=j['output'];archive=folder/'artwork'/(ref['sha256']+'.png');immutable(archive,(ROOT/ref['path']).read_bytes())
        imagepath=folder/(j['slug']+'-native.png');im.save(imagepath)
        dest=next(p for p in result['components']['portraits']['jobs'] if p['job']==j['job'])
        for key in ('crop','size','conversionManifest','conversionManifestSha256'):dest.pop(key,None)
        dest.update(source=str(archive.relative_to(ROOT)),sourceSha256=ref['sha256'],pixelsSha256=sha(raw),paletteSha256=sha(pal),
                    oamSha256=sha(struct.pack('<4H',1,0x20c0,0xc1c8,0)),portraitWindow=[44,54],
                    reviewedPortraitPlan=str(provenance/'plan.json'),nativeImage=str(imagepath))
        x=n%5*192;y=n//5*280;draw.text((x+4,y+4),j['label'],fill='black')
        rgba=im.convert('RGBA');board.alpha_composite(rgba.resize((192,192),Image.Resampling.NEAREST),(x,y+24));board.alpha_composite(rgba,(x+64,y+216))
    board.save(folder/'native-review.png')
    result['components']['portraits']['scope']='Ten reviewed generated64px portraits,47 opaque RGB555 colors plus transparency. Original portrait/OAM records and495 original palettes unchanged. Custom alternatives retain identical colors as the prior transport; runtime approval remains separate.'
    result['components']['reviewedPortraits']=dict(plan=str(provenance/'plan.json'),planSha256=sha(planpath.read_bytes()),
        parentManifest=str(provenance/'parent.json'),parentManifestSha256=sha(parent_path.read_bytes()),patches=patches,productionAccepted=False)
    result['archivedManifest']=str(provenance/'manifest.json');encoded=(json.dumps(result,indent=2)+'\n').encode()
    immutable(provenance/'manifest.json',encoded)
    destination=output or ROOT/'build/art/reviewed-integration/portrait-candidate.json'
    destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(encoded)
    print(json.dumps(dict(romSha1=digest,portraits=10,patches=len(patches),review=str(folder/'native-review.png'))))
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--parent',type=Path,default=ROOT/'build/art/reviewed-integration/action-candidate.json')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args();build(args.parent,args.output)
