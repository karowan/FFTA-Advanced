"""Map generated actor pixels to FFTA's native shared palettes at build time.

New artwork, native action graphs and all twenty land/water resources remain.
The conversion preserves transparency and uses only indices1..15 for opaque
pixels. Native party/opposing palette selectors, fades and hardware composition
then run unchanged. Final artwork must be reviewed in this native palette.
This is technical conversion of existing imagegen assets, not authored artwork.
"""
import datetime,hashlib,json,struct
from pathlib import Path
from native_art import ROOT,TILES,OAM,sha,layout

# Unused tail inside the existing generated-action reservation, after the
# separately verified Moogle action-completion payload. Original streams stay.
START,END=0x1f10000,0x1f80000
word=lambda b,p:struct.unpack_from('<I',b,p)[0]

def build(source,*,publish_current=False):
    source=Path(source);source_raw=source.read_bytes();parent=json.loads(source_raw)
    original=Path(parent['path']).read_bytes();assert hashlib.sha1(original).hexdigest()==parent['romSha1']
    assert 'actionCompletion' in parent['components'] and 'nativePaletteTransport' not in parent['components']
    actions=parent['components']['actions'];live=parent['components']['livePalette']
    assert actions['reservation'][0]<=START<END<=actions['reservation'][1]
    assert parent['components']['actionCompletion']['used'][1]<=START
    assert original[START:END]==b'\xff'*(END-START)
    rom=bytearray(original);cursor=START;segments=[];patches=[];resources=[];palettes=[]
    tile_cache={};sequence_cache={};table=word(original,0x2102c)-0x08000000
    jobs=word(original,0xc8598)-0x08000000
    def add(raw,kind):
        nonlocal cursor
        cursor=(cursor+3)&~3;p=cursor;cursor+=len(raw);assert cursor<=END,'Native palette transport reservation exhausted'
        rom[p:cursor]=raw;segments.append(dict(offset=p,bytes=len(raw),kind=kind,sha256=sha(raw)));return p
    def patch(p,old,new,purpose):
        assert len(old)==len(new) and rom[p:p+len(old)]==old,(purpose,hex(p))
        rom[p:p+len(old)]=new;patches.append(dict(offset=p,bytes=len(old),before=old.hex(),after=new.hex(),purpose=purpose))
    colors=live['symbols']['ffta_art_custom_colors']-0x08000000
    for owner in range(10):
        job=116+owner;selector=original[jobs+52*job+11]&15;opposing=original[jobs+52*job+11]>>4
        native=struct.unpack_from('<16H',original,0x419d60+32*selector)
        custom=struct.unpack_from('<16H',original,colors+32*owner)
        def distance(a,b):return sum((((a>>s)&31)-((b>>s)&31))**2 for s in (0,5,10))
        mapping=[0]+[min(range(1,16),key=lambda j:distance(v,native[j])) for v in custom[1:]]
        lookup=bytes(mapping[i&15]|(mapping[i>>4]<<4) for i in range(256))
        palettes.append(dict(job=job,selector=selector,opposingSelector=opposing,
                             sourceColors=list(custom),nativeColors=list(native),indexMap=mapping,
                             nativePaletteOffset=0x419d60+32*selector,
                             nativePaletteSha256=sha(original[0x419d60+32*selector:0x419d80+32*selector])))
        for resource in (256+owner*2,257+owner*2):
            info=next(r for r in actions['resources'] if r['id']==resource)
            descriptor=word(original,table+resource*4)-0x08000000
            desc=bytearray(original[descriptor:descriptor+12*info['slots']]);streams=[]
            for slot in range(info['slots']):
                pointer=word(desc,slot*12)
                if not pointer:continue
                q=pointer-0x08000000;count=word(original,q)
                assert 0<count<100 and 0<=q<=len(original)-4-count*20
                sequence=bytearray(original[q:q+4+count*20]);frames=[]
                for frame in range(count):
                    p=4+frame*20
                    if sequence[p+9]!=1:continue
                    t,o=struct.unpack_from('<II',sequence,p)
                    assert t!=0xffff and o!=0xffffffff,'Unrecognized body draw marker'
                    objects,_=layout(original,OAM+o)
                    assert len(objects)==1 and objects[0]['width']==objects[0]['height']==32 and objects[0]['tile']==0
                    raw=original[TILES+t:TILES+t+512];assert len(raw)==512
                    converted=raw.translate(lookup)
                    assert all((a&15==0)==(b&15==0) and (a>>4==0)==(b>>4==0) for a,b in zip(raw,converted))
                    if converted not in tile_cache:tile_cache[converted]=add(converted,'native-palette-imagegen-body')
                    new=tile_cache[converted];struct.pack_into('<I',sequence,p,new-TILES)
                    frames.append(dict(frame=frame,sourceTile=TILES+t,tile=new,sourceSha256=sha(raw),sha256=sha(converted)))
                raw_sequence=bytes(sequence)
                if raw_sequence not in sequence_cache:sequence_cache[raw_sequence]=add(raw_sequence,'preserved-native-action-commands')
                new=sequence_cache[raw_sequence];struct.pack_into('<I',desc,slot*12,new+0x08000000)
                streams.append(dict(slot=slot,sourceSequence=q,sequence=new,count=count,frames=frames))
            new=add(desc,'native-palette-descriptors')
            patch(table+resource*4,original[table+resource*4:table+(resource+1)*4],struct.pack('<I',new+0x08000000),'Native palette class resource '+str(resource))
            resources.append(dict(job=job,resource=resource,slots=info['slots'],sourceDescriptors=descriptor,descriptors=new,streams=streams))
    # Retain independent heap/menu fixes. Remove precisely the palette/OAM
    # interception layer: no ownership scans, bank remapping, fade translation
    # or palette-copy observation runs for these native-indexed assets.
    restored=[]
    for change in live['changes']:
        purpose=change['purpose']
        if not (purpose.startswith('native palette ') or purpose.startswith('native fade ') or
                purpose=='native OBJ palette reload notification preserving existing copy handler'):continue
        patch(change['offset'],bytes.fromhex(change['after']),bytes.fromhex(change['before']),'Restore '+purpose)
        restored.append(change['offset'])
    assert len(restored)==29 and {0x6d0,0x788,0x1194,0x12bc,0x216f8,0x8f1f4,0x36d4bc}<=set(restored)
    mask=live['symbols']['ffta_art_custom_mask']-0x08000000
    patch(mask,struct.pack('<I',1023),bytes(4),'Native-indexed artwork requires no custom palette ownership')
    allowed=set(range(START,cursor))
    for item in patches:allowed.update(range(item['offset'],item['offset']+item['bytes']))
    assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
    digest=hashlib.sha1(rom).hexdigest();out=ROOT/'build/art/native-palettes'/digest;out.mkdir(parents=True,exist_ok=True)
    path=out/'FFTA_Native_Palette_Expansion.gba';path.write_bytes(rom)
    component=dict(path=str(path),romSha1=digest,source=parent['path'],baseRomSha1=parent['romSha1'],
        sourceManifest=str(source),sourceManifestSha256=sha(source_raw),sourceSha256=sha(Path(__file__).read_bytes()),
        reservation=[START,END],used=[START,cursor],segments=segments,patches=patches,resources=resources,palettes=palettes,
        scope=__doc__,restoredNativeHooks=restored)
    (out/'manifest.json').write_text(json.dumps(component,indent=2)+'\n',encoding='utf-8')
    connected=dict(parent,path=str(path),romSha1=digest,romSha256=sha(rom),
        components=dict(parent['components'],nativePaletteTransport=component),
        status='Native shared-palette engineering candidate; acceptance pending')
    folder=ROOT/'build/art/connected'/digest;folder.mkdir(parents=True,exist_ok=True)
    (folder/'manifest.json').write_text(json.dumps(connected,indent=2)+'\n',encoding='utf-8')
    view=json.loads((source.parent/'live-palette-view.json').read_text())
    view.update(path=str(path),romSha1=digest,connectedManifest=str(folder/'manifest.json'),nativePaletteTransport=str(out/'manifest.json'))
    (folder/'live-palette-view.json').write_text(json.dumps(view,indent=2)+'\n',encoding='utf-8')
    if publish_current:(ROOT/'build/art/native-palettes/current.json').write_bytes((folder/'manifest.json').read_bytes())
    return connected
