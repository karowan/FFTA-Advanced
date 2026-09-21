"""Connect ten existing imagegen drafts to private idle and miniature consumers.

Technical placeholders only. No artwork is authored here: existing indexed
frames are authenticated, mapped to existing palettes and packed for the ROM.
Other animations and water remain original donors until their separate import.
"""
import hashlib,json,struct
from pathlib import Path
from PIL import Image
from native_art import ROOT,TILES,OAM,sha,palette,pack_tiles,tile_image,layout,compose
from native_actor_import import END,PARTY_LITERALS
from native_miniatures import CONTAINER,LITERALS,decode,encode
from equipment_preview import apply as apply_preview

def mapped_frame(path,proof,rgb):
    with Image.open(path) as source:
        assert source.mode=='P' and source.size==(32,32)
        assert sha(pack_tiles(source,16))==proof['tileSha256']
        source=source.convert('RGBA')
        image=Image.new('P',(32,32));image.putpalette(rgb+[0]*(768-len(rgb)))
        for y in range(32):
            for x in range(32):
                pixel=source.getpixel((x,y))
                if pixel[3]:image.putpixel((x,y),min(range(1,16),key=lambda c:sum((pixel[k]-rgb[c*3+k])**2 for k in range(3))))
    image.info['transparency']=0
    return image

def build(base_manifest=None, *, publish_current=True):
    basepath=Path(base_manifest) if base_manifest else ROOT/'build/art/class-resources/current.json';base=json.loads(basepath.read_text())
    original=Path(base['path']).read_bytes();assert hashlib.sha1(original).hexdigest()==base['romSha1']
    catalogpath=ROOT/'src/art/imagegen/catalog.json';catalog=json.loads(catalogpath.read_text())
    rom=bytearray(original);start=cursor=(base['used'][1]+3)&~3;segments=[];jobs=[];entries=[]
    miniatures=[decode(original,CONTAINER,i) for i in range(54)]
    root=ROOT/'build/art/generated-classes';work=root/'compile';work.mkdir(parents=True,exist_ok=True)
    def add(raw,kind):
        nonlocal cursor
        cursor=(cursor+3)&~3;p=cursor;cursor+=len(raw)
        assert cursor<=END and rom[p:cursor]==b'\xff'*len(raw),'Unowned or overflowing class-art reservation'
        rom[p:cursor]=raw;segments.append(dict(offset=p,bytes=len(raw),kind=kind,sha256=sha(raw)))
        return p
    for art in catalog['jobs']:
        job=next(j for j in base['jobs'] if j['job']==art['job']);number=job['job'];land=job['resources'][0]
        resource=next(r for r in base['resources'] if r['id']==land)
        proofpath=ROOT/art['technicalConversion'];proof=json.loads(proofpath.read_text())
        assert sha((ROOT/art['privateSource']).read_bytes())==proof['sourceSha256']==art['sourceSha256']
        # Native job selector6 uses the low nibble of byte11. Palette routing
        # stays unchanged; custom palette allocation is a separate open gate.
        bank=original[job['record']+11]&15;palref=0x419d60+32*bank
        pal,rgb=palette(original,palref)
        # Eight-cell drafts contain two idle phases per facing. Four-cell
        # drafts contain one phase per facing: duplicate, do not invent motion.
        ids=(0,4,2,6) if len(proof['frames'])==8 else (0,0,2,2)
        assert len(proof['frames']) in (4,8)
        images=[mapped_frame(proofpath.parent/f'frame-{i:02}.png',proof['frames'][i],rgb) for i in ids]
        frames=[]
        for index,(source,image) in enumerate(zip(ids,images)):
            raw=pack_tiles(image,16);p=add(raw,f'{number}/idle-tiles')
            frames.append(dict(sourceFrame=source,tile=p,sha256=sha(raw)))
            image.save(work/f'{number}-idle-{index}.png',bits=4)
        # Align each class against its own original opaque foot baseline.
        q=struct.unpack_from('<I',original,resource['descriptors'])[0]-0x08000000
        t,o=struct.unpack_from('<II',original,q+4);objects,_=layout(original,OAM+o)
        count=max(v['tile']+v['width']*v['height']//64 for v in objects)
        native=compose(original[TILES+t:TILES+t+count*32],objects,rgb)
        native_bottom=Image.frombytes('L',native.size,native.tobytes()).getbbox()[3]-64
        generated_bottom=max(image.getbbox()[3] for image in images);dy=native_bottom-generated_bottom
        oam=add(struct.pack('<4H',1,dy&255,0x8000|((-16)&511),0),f'{number}/idle-oam')
        desc=bytearray(original[resource['descriptors']:resource['descriptors']+12*resource['slots']]);seqs=[]
        for slot,indexes in ((0,(0,1,0,1)),(1,(2,3,2,3))):
            q=struct.unpack_from('<I',desc,12*slot)[0]-0x08000000
            count=struct.unpack_from('<I',original,q)[0];assert count==4
            seq=bytearray(original[q:q+4+count*20])
            for f,index in enumerate(indexes):
                assert seq[13+20*f]==1,'Only native draw commands are replaced'
                struct.pack_into('<II',seq,4+20*f,frames[index]['tile']-TILES,oam-OAM)
            target=add(seq,f'{number}/idle-sequence');struct.pack_into('<I',desc,12*slot,target+0x08000000)
            seqs.append(dict(slot=slot,source=q,target=target,frames=list(indexes)))
        table=add(desc,f'{number}/land-descriptors');entry=base['table']+land*4
        struct.pack_into('<I',rom,entry,table+0x08000000);entries.extend(range(entry,entry+4))
        # The wheel uses a separate palette and640-byte compressed image.
        mini_palette=0x94ee3c+bank*32;_,mrgb=palette(original,mini_palette)
        draft=mapped_frame(proofpath.parent/'frame-00.png',proof['frames'][0],mrgb)
        donor=original[base['partyTable']+land*2]
        native_mini=tile_image(miniatures[donor],mrgb,32)
        offset=native_mini.getbbox()[3]-draft.getbbox()[3]
        assert 0<=offset<=8,(number,offset)
        mini=Image.new('P',(32,40));mini.putpalette(draft.getpalette());mini.paste(draft,(0,offset));mini.info['transparency']=0
        mini_raw=pack_tiles(mini,20);mini_id=len(miniatures);miniatures.append(mini_raw)
        entry=base['partyTable']+land*2;rom[entry]=mini_id;entries.append(entry)
        mini.save(work/f'{number}-miniature.png',bits=4)
        jobs.append(dict(job=number,name=art['name'],resource=land,originalResource=resource['originalID'],frames=frames,oam=oam,
            descriptors=table,sourceDescriptors=resource['descriptors'],slots=resource['slots'],sequences=seqs,
            nativePaletteReference=palref,nativePaletteSha256=sha(pal),footAlignment=dict(nativeBottom=native_bottom,generatedBottom=generated_bottom,objectY=dy),
            miniature=dict(index=mini_id,donor=donor,mappingEntry=entry,paletteReference=mini_palette,offsetY=offset,sha256=sha(mini_raw)),
            source=art['privateSource'],sourceSha256=art['sourceSha256'],conversionManifest=art['technicalConversion'],conversionManifestSha256=sha(proofpath.read_bytes())))
    container_blob=encode(miniatures);container=add(container_blob,'64-entry-miniature-container')
    for literal in LITERALS:
        assert struct.unpack_from('<I',rom,literal)[0]==CONTAINER+0x08000000
        struct.pack_into('<I',rom,literal,container+0x08000000);entries.extend(range(literal,literal+4))
    for literal in PARTY_LITERALS:assert struct.unpack_from('<I',rom,literal)[0]==base['partyTable']+0x08000000
    prior=base.get('installedPreview')
    preview=apply_preview(rom,work,generated_portraits=True,previous=prior)
    owned_size=max(preview['bytes'],prior['bytes'] if prior else 0)
    allowed=set(range(start,cursor))|set(entries)|set(range(preview['reservation'][0],preview['reservation'][0]+owned_size))
    for change in preview['changes']:allowed.update(range(change['offset'],change['offset']+change['bytes']))
    assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
    for i,raw in enumerate(miniatures):assert decode(rom,container,i)==raw
    digest=hashlib.sha1(rom).hexdigest();out=root/digest;out.mkdir(parents=True,exist_ok=True)
    path=out/'FFTA_Generated_Classes.gba';path.write_bytes(rom)
    for p in work.glob('*.png'):(out/p.name).write_bytes(p.read_bytes())
    preview.update(source=base['source'],baseRomSha1=base['baseRomSha1'],assetDirectory=str(out))
    result=dict(path=str(path),romSha1=digest,romSha256=sha(rom),source=base['path'],baseRomSha1=base['romSha1'],
        releaseSource=base['source'],releaseRomSha1=base['baseRomSha1'],used=[base['used'][0],cursor],generatedRange=[start,cursor],
        classResources=base,jobs=jobs,segments=segments,container=container,containerSha256=sha(container_blob),miniatureCount=len(miniatures),preview=preview,
        sourceManifestSha256=sha(basepath.read_bytes()),catalogSha256=sha(catalogpath.read_bytes()),
        scope='Ten imagegen-derived land idle transports, ten separate menu miniatures and ten equipment portraits. Existing palettes; remaining actions/water/large portraits/weapon/effect/status and production-art acceptance are open. Not packaged or installed.')
    for p in ((out/'manifest.json',root/'current.json') if publish_current else (out/'manifest.json',)):p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(romSha1=digest,path=str(path),generatedBytes=cursor-start,jobs=len(jobs))))
    return result

if __name__=='__main__':build()
