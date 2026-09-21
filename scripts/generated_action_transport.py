"""Route every owned land/water sequence through temporary generated poses.

This is a transport proof, not finished animation: existing idle poses repeat
through preserved action commands, and water uses cropped upper-body pixels.
No new artwork is drawn. Explicit frame plans override only their declared slots.
"""
import hashlib,json,struct
from pathlib import Path
from PIL import Image
from native_art import ROOT,TILES,OAM,sha,layout,compose,tile_image,pack_tiles
START,END=0x1e80000,0x1f80000

def build(base_manifest=None, *, publish_current=True, animation_plan=None):
    parentpath=Path(base_manifest) if base_manifest else ROOT/'build/art/generated-portraits/current.json';parent=json.loads(parentpath.read_text())
    base=json.loads((Path(parent['source']).parent/'manifest.json').read_text())
    original=Path(parent['path']).read_bytes();assert hashlib.sha1(original).hexdigest()==parent['romSha1']
    plan=None
    if animation_plan:
        from generated_animation_plan import AnimationPlan
        plan=AnimationPlan(animation_plan,original,base['classResources']['resources'],ROOT/'build/art/generated-actions/conversions')
    rom=bytearray(original);assert rom[START:END]==b'\xff'*(END-START),'Action reservation occupied'
    cursor=START;segments=[];changed=set();resources=[];tilecache={};oamcache={}
    def add(raw,kind):
        nonlocal cursor
        cursor=(cursor+3)&~3;p=cursor;cursor+=len(raw);assert cursor<=END
        rom[p:cursor]=raw;segments.append(dict(offset=p,bytes=len(raw),sha256=sha(raw),kind=kind));return p
    rgb=[i*16 for i in range(16) for _ in range(3)]
    for res in base['classResources']['resources']:
        art=next(j for j in base['jobs'] if j['job']==res['job']);water=res['lifetime']=='water'
        entry=base['classResources']['table']+res['id']*4
        source=struct.unpack_from('<I',original,entry)[0]-0x08000000
        desc=bytearray(original[source:source+12*res['slots']]);sequences=[];cache={}
        for slot in range(res['slots']):
            pointer=struct.unpack_from('<I',desc,12*slot)[0]
            assigned=plan.sequence(res['job'],res['lifetime'],slot) if plan else None
            if not pointer or (not water and slot<2 and assigned is None):continue
            q=pointer-0x08000000;key=(q,slot%2,tuple((v['asset'],v['frame']) for v in assigned) if assigned else None)
            if key not in cache:
                count=struct.unpack_from('<I',original,q)[0];seq=bytearray(original[q:q+4+count*20]);frames=[]
                for f in range(count):
                    frame=q+4+20*f;t,o=struct.unpack_from('<II',original,frame);objects,_=layout(original,OAM+o)
                    n=max(v['tile']+v['width']*v['height']//64 for v in objects)
                    native=compose(original[TILES+t:TILES+t+n*32],objects,rgb)
                    mask=Image.frombytes('L',native.size,native.tobytes());bounds=mask.getbbox();assert bounds
                    native_bottom=bounds[3]-64
                    if assigned:
                        image=plan.frame(assigned[f],original,art['nativePaletteReference']);raw=pack_tiles(image,16)
                    else:
                        pose=art['frames'][(2 if slot%2 else 0)+(f%2)]
                        raw=original[pose['tile']:pose['tile']+512];image=tile_image(raw,rgb,32)
                    if water and assigned is None:
                        # Explicit technical crop only: no invented swimming
                        # pose or claim of finished water/action animation.
                        cropped=Image.new('P',(32,32));cropped.putpalette(image.getpalette())
                        cropped.paste(image.crop((0,0,32,20)),(0,0));image=cropped;raw=pack_tiles(image,16)
                    bottom=Image.frombytes('L',image.size,image.tobytes()).getbbox()[3]
                    dy=native_bottom-bottom;assert -128<=dy<128
                    raw_oam=struct.pack('<4H',1,dy&255,0x8000|((-16)&511),0)
                    if raw not in tilecache:tilecache[raw]=add(raw,'explicit-pose' if assigned else 'water-crop' if water else 'action-pose')
                    if raw_oam not in oamcache:oamcache[raw_oam]=add(raw_oam,'aligned-32x32-layout')
                    pt,po=tilecache[raw],oamcache[raw_oam]
                    struct.pack_into('<II',seq,4+20*f,pt-TILES,po-OAM)
                    frames.append(dict(tile=pt,oam=po,sourceFrame=frame,generatedFrame=assigned[f]['frame'] if assigned else (2 if slot%2 else 0)+(f%2),
                        nativeBottom=native_bottom,generatedBottom=bottom,y=dy,sha256=sha(raw),**(dict(explicitFrame=assigned[f]) if assigned else {})))
                p=add(seq,'water-sequence' if water else 'action-sequence');cache[key]=(p,frames)
            p,frames=cache[key];struct.pack_into('<I',desc,12*slot,p+0x08000000)
            sequences.append(dict(slot=slot,source=q,target=p,frames=frames))
        p=add(desc,'owned-descriptors');struct.pack_into('<I',rom,entry,p+0x08000000);changed.update(range(entry,entry+4))
        resources.append(dict(id=res['id'],job=res['job'],lifetime=res['lifetime'],sourceDescriptors=source,descriptors=p,
            slots=res['slots'],size=res['size'],sequences=sequences))
    changed.update(range(START,cursor));assert all(a==b or i in changed for i,(a,b) in enumerate(zip(original,rom)))
    digest=hashlib.sha1(rom).hexdigest();root=ROOT/'build/art/generated-actions';out=root/digest;out.mkdir(parents=True,exist_ok=True)
    path=out/'FFTA_Generated_Actions.gba';path.write_bytes(rom)
    result=dict(path=str(path),romSha1=digest,romSha256=sha(rom),source=parent['path'],baseRomSha1=parent['romSha1'],
        releaseSource=parent['releaseSource'],sourceManifestSha256=sha(parentpath.read_bytes()),reservation=[START,END],used=[START,cursor],
        table=base['classResources']['table'],sizeTable=base['classResources']['sizeTable'],resources=resources,segments=segments,
        scope='All20 owned resource descriptor tables. Temporary repeated imagegen poses for all present non-idle land and water sequences; water upper20-pixel crop. Original command/timing/metadata, null slots and land idle descriptors retained. No finished action/water art or rendered-consumer acceptance; not packaged or installed.')
    if plan:
        result['animationPlan']=plan.report()
        result['scope']='Explicit imagegen sequence/frame assignments recorded in animationPlan. Unmapped slots retain the temporary repeated-pose/cropped-water transport; all native timing/commands/metadata preserved. Coverage does not accept art. Private stage only, not assembled or packaged.'
    for p in ((out/'manifest.json',root/'current.json') if publish_current else (out/'manifest.json',)):p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(romSha1=digest,bytes=cursor-START,resources=len(resources),sequences=sum(len(r['sequences']) for r in resources))));return result

if __name__=='__main__':build()
