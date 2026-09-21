"""Private imagegen Samurai idle import, with existing native palette constraints.

Only land idle descriptors0/1 are changed. This is not full artwork acceptance:
other animations, miniature images and custom palette allocation remain open.
"""
import hashlib,json,struct
from pathlib import Path
from PIL import Image
from native_art import ROOT,TILES,OAM,pack_tiles,palette,sha,layout,compose
from native_actor_import import END

base=json.loads((ROOT/'build/art/actor-import/current.json').read_text())
source=Path(base['path']);original=source.read_bytes()
assert hashlib.sha1(original).hexdigest()==base['romSha1']
assets=ROOT/'build/art/imagegen/samurai/native-v4-coverage'
provenance=json.loads((assets/'manifest.json').read_text())
assert sha(Path(provenance['source']).read_bytes())==provenance['sourceSha256']
rom=bytearray(original);cursor=(base['used'][1]+3)&~3;start=cursor;segments=[]
def add(blob,kind):
    global cursor
    cursor=(cursor+3)&~3;p=cursor;cursor+=len(blob)
    assert cursor<=END and rom[p:cursor]==b'\xff'*len(blob)
    rom[p:cursor]=blob;segments.append(dict(offset=p,bytes=len(blob),kind=kind,sha256=sha(blob)))
    return p

# Technical palette mapping only. Native palette bytes/routing are untouched.
# This proves pixels/OAM transport, not final color design or bank allocation.
# Normal color-mode bank1, authenticated against the actual Samurai OAM bank
# and OBJ palette in deployment/idle captures. 0x41a860 is the dim variant.
palette_offset=0x419d60+32
pal,rgb=palette(original,palette_offset)
work=ROOT/'build/art/generated-actor-poc';work.mkdir(parents=True,exist_ok=True)
frames=[]
for i in (0,4,2,6):
    with Image.open(assets/f'frame-{i:02}.png') as image:
        assert sha(pack_tiles(image,16))==provenance['frames'][i]['tileSha256']
        image=image.convert('RGBA')
        mapped=Image.new('P',(32,32));mapped.putpalette(rgb+[0]*(768-len(rgb)))
        for y in range(32):
            for x in range(32):
                pixel=image.getpixel((x,y))
                if pixel[3]:
                    idx=min(range(1,16),key=lambda c:sum((pixel[k]-rgb[c*3+k])**2 for k in range(3)))
                    mapped.putpixel((x,y),idx)
        mapped.info['transparency']=0;mapped.save(work/f'constrained-frame-{i:02}.png',bits=4)
        raw=pack_tiles(mapped,16);frames.append(dict(sourceFrame=i,tile=add(raw,'generated-tiles'),sha256=sha(raw)))
# Match the original actor's opaque foot baseline relative to its world anchor.
# Native pose previews use anchor(48,64); original Samurai bottom is59, so -5.
# Generated canvases have exclusive foot baseline31, requiring OAM Y=-36.
native_land=next(r for r in base['resources'] if r['id']==256)
native_sequence=struct.unpack_from('<I',original,native_land['descriptors'])[0]-0x08000000
native_t,native_o=struct.unpack_from('<II',original,native_sequence+4)
native_objects,_=layout(original,OAM+native_o)
native_count=max(v['tile']+v['width']*v['height']//64 for v in native_objects)
native_pose=compose(original[TILES+native_t:TILES+native_t+native_count*32],native_objects,rgb)
native_mask=Image.frombytes('L',native_pose.size,native_pose.tobytes())
native_bottom=native_mask.getbbox()[3]-64
generated_bottom=max(v['origin'][1]+v['nativeSize'][1] for v in provenance['frames'])
object_y=native_bottom-generated_bottom
assert (native_bottom,generated_bottom,object_y)==(-5,31,-36)
# One non-affine32x32 4bpp object, matching the existing16-tile allocation.
oam=add(struct.pack('<4H',1,object_y&255,0x8000|((-16)&511),0),'generated-oam')
land=next(r for r in base['resources'] if r['id']==256)
descriptors=bytearray(original[land['descriptors']:land['descriptors']+12*land['slots']]);seqs=[]
for slot,ids in ((0,(0,1,0,1)),(1,(2,3,2,3))):
    offset=struct.unpack_from('<I',descriptors,slot*12)[0]-0x08000000
    count=struct.unpack_from('<I',original,offset)[0];assert count==4
    seq=bytearray(original[offset:offset+4+count*20])
    for f,idx in enumerate(ids):
        assert seq[4+20*f+9]==1,'Idle frame command changed'
        struct.pack_into('<II',seq,4+f*20,frames[idx]['tile']-TILES,oam-OAM)
    target=add(seq,'generated-idle-sequence');struct.pack_into('<I',descriptors,slot*12,0x08000000+target)
    seqs.append(dict(slot=slot,source=offset,target=target,frames=ids))
table=add(descriptors,'generated-land-descriptors')
entry=base['table']+256*4;struct.pack_into('<I',rom,entry,0x08000000+table)
allowed=set(range(start,cursor))|set(range(entry,entry+4))
assert len(rom)==len(original) and all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
digest=hashlib.sha1(rom).hexdigest();out=work/digest;out.mkdir(exist_ok=True)
path=out/'generated-idle.gba';path.write_bytes(rom)
report=dict(path=str(path),romSha1=digest,source=base['source'],baseRomSha1=base['baseRomSha1'],
            relocationSource=str(source),relocationRomSha1=base['romSha1'],used=[base['used'][0],cursor],
            generatedRange=[start,cursor],frames=frames,oam=oam,sequences=seqs,segments=segments,
            sourceManifest=str(assets/'manifest.json'),sourceManifestSha256=sha((assets/'manifest.json').read_bytes()),
            nativePaletteReference=palette_offset,nativePaletteSha256=sha(pal),
            footAlignment=dict(nativeBottom=native_bottom,generatedBottom=generated_bottom,objectY=object_y),
            scope='Imagegen idle pixels and one32x32 native OAM proof only. Native palette-constrained mapping, no custom palette bank. Land idle slots0/1 only; remaining actions/water/menu art are donors, not accepted production art.')
for p in (out/'manifest.json',work/'current.json'):p.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(path=str(path),romSha1=digest,bytes=cursor-start)))
