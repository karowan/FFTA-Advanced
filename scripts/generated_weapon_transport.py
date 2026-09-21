"""Independent held-axe resource; temporary generated pixels, native motion.

Both descriptor sequence pointers matter for held weapons. Sentinel command
frames are not tile records. Preserve OAM, timing and attachment parameters.
"""
import hashlib,json,struct
from pathlib import Path
from native_art import ROOT,TILES,OAM,ANIM,SIZES,sha,layout,palette,tile_image
from native_miniatures import decode
START,END=0x1f84000,0x1f88000
RESOURCE,DONOR=276,128
AXES=(*range(392,400),448,*range(453,461))

def build(base_manifest=None, *, equipment_manifest=None, publish_current=True):
    chain=json.loads((Path(base_manifest) if base_manifest else ROOT/'build/art/clean-chain/current.json').read_text());original=Path(chain['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==chain['romSha1']
    clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();assert hashlib.sha1(clean).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
    rom=bytearray(original);assert rom[START:END]==b'\xff'*(END-START)
    equipment=json.loads(Path(equipment_manifest).read_text()) if equipment_manifest else chain['components']['equipment']
    if equipment_manifest:
        assert equipment['romSha1']==chain['romSha1'] and Path(equipment['path']).read_bytes()==original
    raw=decode(original,equipment['symbols']['ffta_art_axe_container']-0x08000000,0)
    assert len(raw)==128 and sha(raw)==equipment['pixelsSha256']
    pointers=struct.unpack_from('<276I',rom,struct.unpack_from('<I',rom,0x2102c)[0]-0x08000000)
    old_sizes=struct.unpack_from('<I',rom,0x21060)[0]-0x08000000
    source=pointers[DONOR]-0x08000000
    next_source=min(p-0x08000000 for p in pointers if p>pointers[DONOR]);assert next_source-source==120
    desc=bytearray(original[source:next_source]);assert desc==clean[source:next_source]
    root=ROOT/'build/art/generated-weapon';reference=root/'original-reference';reference.mkdir(parents=True,exist_ok=True)
    cursor=START;segments=[];sequences={};payloads={};original_poses={}
    def add(data,kind):
        nonlocal cursor
        cursor=(cursor+3)&~3;p=cursor;cursor+=len(data);assert cursor<=END
        rom[p:cursor]=data;segments.append(dict(offset=p,bytes=len(data),kind=kind,sha256=sha(data)));return p
    for slot in range(10):
        for channel in range(3):
            entry=slot*12+channel*4;pointer=struct.unpack_from('<I',desc,entry)[0]
            if not pointer:continue
            q=pointer-0x08000000
            if q not in sequences:
                count=struct.unpack_from('<I',original,q)[0];assert 0<count<128
                seq=bytearray(original[q:q+4+20*count]);assert seq==clean[q:q+len(seq)]
                frames=[]
                for i in range(count):
                    p=4+20*i;t,o=struct.unpack_from('<II',seq,p)
                    if o==0xffffffff:
                        assert t==65535;frames.append(dict(index=i,commandOnly=True));continue
                    objects,oam=layout(original,OAM+o)
                    n=max(v['tile']+v['width']*v['height']//64 for v in objects)
                    assert 4<=n<=8 and objects[0]['width']==objects[0]['height']==16 and objects[0]['tile']==0
                    assert original[OAM+o:OAM+o+len(oam)]==clean[OAM+o:OAM+o+len(oam)]
                    pixels=original[TILES+t:TILES+t+32*n];assert pixels==clean[TILES+t:TILES+t+32*n]
                    key=(t,n)
                    if key not in original_poses:
                        _,rgb=palette(clean,0x419d60);image=tile_image(pixels,rgb,16)
                        path=reference/f'{t:06x}-{n}.png';image.save(path,bits=4)
                        original_poses[key]=dict(tileOffset=TILES+t,tiles=n,sha256=sha(pixels),pngSha256=sha(path.read_bytes()))
                    if n not in payloads:payloads[n]=add(raw+bytes((n-4)*32),'temporary axe plus transparent native auxiliary tiles')
                    struct.pack_into('<I',seq,p,payloads[n]-TILES)
                    frames.append(dict(index=i,commandOnly=False,tile=payloads[n],tiles=n,oam=OAM+o,sourceTile=TILES+t))
                target=add(seq,'native held weapon sequence');sequences[q]=dict(source=q,target=target,count=count,frames=frames)
            struct.pack_into('<I',desc,entry,sequences[q]['target']+0x08000000)
    descriptor=add(desc,'held axe descriptors')
    table=add(struct.pack('<277I',*pointers,descriptor+0x08000000),'277-entry animation table')
    sizes=add(original[old_sizes:old_sizes+276*2]+original[old_sizes+DONOR*2:old_sizes+DONOR*2+2],'277-entry allocation sizes')
    struct.pack_into('<I',rom,0x2102c,table+0x08000000);struct.pack_into('<I',rom,0x21060,sizes+0x08000000)
    itemtable=struct.unpack_from('<I',rom,0x79aec)[0]-0x08000000
    changed=set(range(START,cursor))|set(range(0x2102c,0x21030))|set(range(0x21060,0x21064))
    assert tuple(i for i in range(461) if rom[itemtable+32*i+8]==31)==AXES,'Axe inventory changed'
    for i in AXES:
        p=itemtable+32*i;assert rom[p+8]==31 and rom[p+13]==0 and struct.unpack_from('<H',rom,p+14)[0]==DONOR
        struct.pack_into('<H',rom,p+14,RESOURCE);changed.update((p+14,p+15))
    assert all(a==b or i in changed for i,(a,b) in enumerate(zip(original,rom)))
    digest=hashlib.sha1(rom).hexdigest();out=root/digest;out.mkdir(parents=True,exist_ok=True);path=out/'FFTA_Generated_Held_Axe.gba';path.write_bytes(rom)
    meta=dict(path=str(path),romSha1=digest,source=chain['path'],baseRomSha1=chain['romSha1'],releaseSource=chain.get('fixtureSource',chain.get('releaseSource')),
        reservation=[START,END],used=[START,cursor],resource=RESOURCE,donor=DONOR,sourceDescriptors=source,descriptors=descriptor,table=table,sizeTable=sizes,
        itemTable=itemtable,items=list(AXES),payloads={str(k):v for k,v in payloads.items()},pixelsSha256=sha(raw),sourceArt=equipment['sourceArt'],
        sourceArtSha256=equipment['sourceArtSha256'],paletteOffset=0x419d60,originalPoses=list(original_poses.values()),sequences=list(sequences.values()),segments=segments,
        scope='Temporary imagegen axe through independent held weapon resource276, both primary/secondary descriptor sequences, original attachment/OAM/timing/command frames. Other auxiliary tiles transparently padded. Existing item category/stats/palette and donor128 preserved. Native/actual acceptance and finished weapon animation separate.')
    for p in ((out/'manifest.json',root/'current.json') if publish_current else (out/'manifest.json',)):p.write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps(dict(romSha1=digest,bytes=cursor-START,sequences=len(sequences),references=len(original_poses))));return meta

if __name__=='__main__':build()
