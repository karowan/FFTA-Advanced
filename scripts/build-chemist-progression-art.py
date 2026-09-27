"""Import approved Physician/Sapper bodies without moving an opaque pixel.

This stage owns four new native resources (276..279). It preserves all existing
resource entries and every animation command/parameter. It does not enable the
jobs or claim that gameplay/menu consumers have been integrated.
"""
import hashlib
import json
import struct
from pathlib import Path
from PIL import Image
from new_job_art_helpers import ROOT, checked, record
from native_art import TILES, OAM, ANIM, pack_tiles, layout, compose

START, END = 0x1a10000, 0x1a50000
APPROVAL = ROOT/'src/art/new-job-review/chemist-integration-approval-2026-09-27.json'


def build():
    approval=json.loads(APPROVAL.read_text())
    review=json.loads(checked(approval['review']).read_text());checked(approval['page'])
    atlas=json.loads(checked(review['atlas']).read_text())
    parent=ROOT/'build/expansion/chemist-progressions/data-only/manifest.json'
    meta=json.loads(parent.read_text());original=Path(meta['target']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==meta['targetSha1']
    assert original[START:END]==b'\xff'*(END-START)
    clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    assert hashlib.sha1(clean).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
    rom=bytearray(original);cursor=START;segments=[];patches=[];assets=[];resources=[]
    def add(data,kind):
        nonlocal cursor
        at=(cursor+3)&~3;cursor=at+len(data);assert cursor<=END
        rom[at:cursor]=data
        segments.append(dict(offset=at,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),kind=kind))
        return at
    def patch(at,data,label):
        old=bytes(rom[at:at+len(data)]);rom[at:at+len(data)]=data
        patches.append(dict(offset=at,before=old.hex(),after=data.hex(),label=label))
    word=lambda at:struct.unpack_from('<I',original,at)[0]
    table=word(0x2102c)-0x08000000;sizes=word(0x21060)-0x08000000
    pointers=list(struct.unpack_from('<276I',original,table))+[0]*4
    widths=list(struct.unpack_from('<276H',original,sizes))+[20]*4
    jobs=word(0xc8598)-0x08000000
    rgb=[((v>>s)&31)*255//31 for v in struct.unpack_from('<16H',original,0x419d60) for s in (0,5,10)]
    for ordinal,unit in enumerate(atlas['units']):
        slug=unit['slug'];job=approval['jobs'][slug];poses={}
        for pid,ref in approval['selections'][slug].items():
            if 'approvedSource' in ref:source=ref['preview'];checked(ref['approvedSource'])
            else:source=json.loads(checked(ref).read_text())['native']
            im=Image.open(checked(source));assert im.mode=='P' and im.size==(64,64)
            assert im.getpalette()[:48]==rgb and im.info.get('transparency')==0
            box=im.convert('RGBA').getbbox();assert box
            # Transparent transport padding is removed only. Coordinates are
            # restored in OAM relative to the reviewed origin (32,56). A 32x40
            # container preserves the Physician's two 33-pixel-tall poses.
            x,y=box[:2];assert box[2]-x<=32 and box[3]-y<=40
            cell=im.crop((x,y,x+32,y+40));raw=pack_tiles(cell,20)
            tile=add(raw,'body-'+slug+'-'+pid)
            ox,oy=x-32,y-56
            oam=struct.pack('<7H',2,oy&255,0x8000|(ox&511),0,
                            0x4000|((oy+32)&255),0x4000|(ox&511),16)
            obj=add(oam,'oam-'+slug+'-'+pid)
            objects,_=layout(rom,obj)
            rendered=compose(raw,objects,rgb).crop((16,8,80,72))
            assert rendered.tobytes()==im.tobytes(),(slug,pid,'pixel/position roundtrip')
            poses[pid]=(tile,obj)
            assets.append(dict(job=job,slug=slug,pose=pid,source=source,tile=tile,oam=obj,
                               origin=[32,56],transport=[x,y,32,40],tiles=20))
        for life,resource in [('land',276+ordinal*2),('water',277+ordinal*2)]:
            seqs=[s for s in unit['sequences'] if s['lifetime']==life]
            assert len(seqs)==84
            descriptors=bytearray(84*12);records=0
            for seq in seqs:
                if 'descriptorHex' in seq:desc=bytes.fromhex(seq['descriptorHex'])
                else:
                    actor=next(s['canonicalActor'] for s in seqs if 'canonicalActor' in s)
                    source=struct.unpack_from('<I',clean,ANIM+actor*4)[0]-0x08000000+seq['slot']*12
                    desc=clean[source:source+12];assert desc[:4]==bytes(4)
                assert len(desc)==12
                pointer=struct.unpack_from('<I',desc)[0]
                if not pointer:
                    assert not seq['records'];descriptors[seq['slot']*12:(seq['slot']+1)*12]=desc;continue
                at=pointer-0x08000000
                count=struct.unpack_from('<I',clean,at)[0];assert count==len(seq['records'])
                data=bytearray(clean[at:at+4+20*count])
                for rec in seq['records']:
                    i=4+20*rec['index'];assert data[i:i+20].hex()==rec['raw']
                    if rec['pose']:
                        tile,obj=poses[rec['pose']];struct.pack_into('<II',data,i,tile-TILES,obj-OAM)
                    assert data[i+8:i+20]==bytes.fromhex(rec['raw'])[8:]
                dest=add(data,'sequence-'+seq['id']);records+=count
                descriptors[seq['slot']*12:(seq['slot']+1)*12]=struct.pack('<I',dest+0x08000000)+desc[4:]
            dest=add(descriptors,'descriptors-'+slug+'-'+life)
            pointers[resource]=dest+0x08000000
            resources.append(dict(job=job,id=resource,lifetime=life,descriptors=dest,slots=84,records=records,tiles=20))
        patch(jobs+job*52+7,struct.pack('<HH',276+ordinal*2,277+ordinal*2),'new class resources')
        patch(jobs+job*52+11,b'\x10','existing native ally0/enemy1 selector')
    dest=add(struct.pack('<280I',*pointers),'animation table');patch(0x2102c,struct.pack('<I',dest+0x08000000),'animation pointer')
    dest=add(struct.pack('<280H',*widths),'allocation sizes');patch(0x21060,struct.pack('<I',dest+0x08000000),'size pointer')
    allowed=set(range(START,cursor))|{p['offset']+i for p in patches for i in range(len(bytes.fromhex(p['after'])))}
    assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
    digest=hashlib.sha1(rom).hexdigest();out=ROOT/'build/expansion/chemist-progressions/art'/digest;out.mkdir(parents=True,exist_ok=True)
    target=out/'candidate.gba';target.write_bytes(rom)
    result=dict(status='Approved body import; gameplay and menus still require integration',path=str(target),romSha1=digest,
                parent=record(parent),approval=record(APPROVAL),reservation=[START,END],used=[START,cursor],
                assets=assets,resources=resources,segments=segments,patches=patches,tableCount=280)
    (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    (out.parent/'current.json').write_text(json.dumps(dict(manifest=str(out/'manifest.json')))+'\n')
    print(json.dumps(dict(romSha1=digest,drawings=len(assets),records=sum(r['records'] for r in resources),bytes=cursor-START)))


if __name__=='__main__':build()
