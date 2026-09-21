"""Import reviewed wheel figures into the existing native miniature palettes.

Only ten archive images and three archive pointers change. No code, palette
words, RAM, palette selection rules or original miniature pixels change.
"""
import argparse,copy,hashlib,json,struct
from pathlib import Path
from PIL import Image
from native_art import ROOT,sha,pack_tiles,tile_image
from native_miniatures import decode,encode,LITERALS


def build(parent_path,output,native_conversion=None):
    parent=json.loads(parent_path.read_text());original=Path(parent['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==parent['romSha1']
    actions=parent['components']['reviewedActions'];assert actions['paletteMode']=='native-shared'
    classes=copy.deepcopy(parent['components']['classes']);old=classes['container']
    images=[decode(original,old,i) for i in range(64)]
    catalog=json.loads((ROOT/'src/art/race-study/full-animation-v1.json').read_text())
    conversions={}
    if native_conversion:
        recipe=json.loads(native_conversion.read_text())
        conversions={u['job']:u for u in recipe['units']}
        assert set(conversions)==set(range(116,126))
    job_table=struct.unpack_from('<I',original,0xc8598)[0]-0x08000000
    jobs=[]
    for n,unit in enumerate(catalog['units']):
        prior=next(j for j in classes['jobs'] if j['job']==unit['job']);mini=prior['miniature']
        assert mini['index']==54+n
        conversion=conversions.get(unit['job'])
        if conversion:
            source=ROOT/conversion['approvedNativeBase'];assert sha(source.read_bytes())==conversion['approvedNativeBaseSha256']
            native=Image.open(source)
            selector=original[job_table+52*unit['job']+11]&15
            assert selector==conversion['nativePalette'] and native.mode=='P' and native.info.get('transparency')==0
            # Bright menu and battle palettes use the same original index roles.
            # Quantizing bright artwork against the dim bank destroys contrast.
            palref=0x94eddc+selector*32
            assert original[palref+2:palref+32]==original[0x419d60+selector*32+2:0x419d60+selector*32+32]
            assert native.getpalette()[:48]==[v for w in conversion['nativePaletteWords'] for v in [((w>>s)&31)*255//31 for s in (0,5,10)]]
            mini['paletteReference']=palref
        else:
            source=ROOT/'build/art/approved-class-animation-2026-09-19'/unit['slug']/'front-neutral.png'
            pose=next(p for p in unit['poses'] if p['outputSha256']==sha(source.read_bytes()))
            assert pose['status'] in ('approved-movement','generated-reviewed')
            palref=mini['paletteReference']
        im=Image.open(source).convert('RGBA');assert im.size==(32,32)
        assert 0x94eddc<=palref<0x94eddc+256*2
        colors=struct.unpack_from('<16H',original,palref)
        donor=tile_image(images[mini['donor']],[0]*48,32)
        offset=donor.getbbox()[3]-im.getbbox()[3];assert 0<=offset<=8
        indexed=Image.new('P',(32,40))
        if conversion:indexed.paste(native,(0,offset))
        else:
            for y in range(32):
                for x in range(32):
                    p=im.getpixel((x,y))
                    if p[3]<128:continue
                    w=sum(round(p[k]*31/255)<<(5*k) for k in range(3))
                    index=min(range(1,16),key=lambda c:sum((((w>>s)&31)-((colors[c]>>s)&31))**2 for s in (0,5,10)))
                    indexed.putpixel((x,y+offset),index)
        raw=pack_tiles(indexed,20);images[54+n]=raw
        mini.update(offsetY=offset,sha256=sha(raw))
        jobs.append(dict(job=unit['job'],slug=unit['slug'],index=54+n,offsetY=offset,
            source=str(source),sourceSha256=sha(source.read_bytes()),tileSha256=sha(raw),
            paletteReference=palref,paletteSha256=sha(original[palref:palref+32]),
            conversion='Exact native base indices; original menu bright/dim routing' if conversion else 'Historical RGB conversion'))
    start=(actions['used'][1]+255)&~255;blob=encode(images);end=start+len(blob)
    assert end<=actions['reservation'][1] and original[start:end]==b'\xff'*len(blob)
    rom=bytearray(original);rom[start:end]=blob
    for literal in LITERALS:
        assert struct.unpack_from('<I',original,literal)[0]==old+0x08000000
        struct.pack_into('<I',rom,literal,start+0x08000000)
    allowed=set(range(start,end))|{i for p in LITERALS for i in range(p,p+4)}
    assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
    for i,raw in enumerate(images):assert decode(rom,start,i)==raw
    digest=hashlib.sha1(rom).hexdigest();folder=ROOT/'build/art/reviewed-native-miniatures'/digest
    folder.mkdir(parents=True,exist_ok=True)
    def immutable(path,data):
        if path.exists():assert path.read_bytes()==data
        else:path.write_bytes(data)
    path=folder/'FFTA_Reviewed_Native_Miniatures.gba';immutable(path,rom)
    classes.update(container=start,containerSha256=sha(blob))
    result=copy.deepcopy(parent)
    result.update(path=str(path),romSha1=digest,romSha256=sha(rom),source=parent['path'],baseRomSha1=parent['romSha1'])
    result['components']['classes']=classes
    result['components']['reviewedNativeMiniatures']=dict(jobs=jobs,container=start,priorContainer=old,
        used=[start,end],pointers=list(LITERALS),parentManifest=str(folder/'parent-manifest.json'),
        parentManifestSha256=sha(parent_path.read_bytes()),sourceSha256=sha(Path(__file__).read_bytes()),scope=__doc__)
    archive=folder/'manifest.json';result['archivedManifest']=str(archive)
    data=(json.dumps(result,indent=2)+'\n').encode();immutable(archive,data)
    immutable(folder/'parent-manifest.json',parent_path.read_bytes())
    output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(data)
    print(json.dumps(dict(romSha1=digest,used=[start,end],jobs=len(jobs))))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--parent',type=Path,default=ROOT/'build/art/reviewed-integration/native-portrait-candidate.json')
    parser.add_argument('--output',type=Path,default=ROOT/'build/art/reviewed-integration/native-menu-candidate.json')
    parser.add_argument('--native-conversion',type=Path)
    args=parser.parse_args();build(args.parent,args.output,args.native_conversion)
