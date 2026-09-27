"""Append the two approved menu portraits and wheel figures, without repainting.

This is a transport stage, not gameplay acceptance. It preserves every older
portrait, OAM record, miniature and native palette. The generated header is an
input to the separately compiled 12-job equipment panel, not an installed hook.
"""
import hashlib, json, struct
from pathlib import Path
from PIL import Image
from new_job_art_helpers import ROOT, checked, record
from native_art import pack_tiles, sha
import native_portraits as portraits
import native_miniatures as miniatures

START, END = 0x1aa0000, 0x1b80000

def build():
    approval=json.loads((ROOT/'src/art/new-job-review/chemist-integration-approval-2026-09-27.json').read_text())
    menu=json.loads(checked(approval['menu']).read_text())
    parent=Path(json.loads((ROOT/'build/expansion/chemist-progressions/art/current.json').read_text())['manifest'])
    meta=json.loads(parent.read_text());original=Path(meta['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==meta['romSha1']
    assert original[START:END]==b'\xff'*(END-START)
    word=lambda p:struct.unpack_from('<I',original,p)[0]-0x08000000
    pt,ot,mt,mp=word(0xcb828),word(0xcb948),word(0x87bd8),word(0x87bd4)
    assert struct.unpack_from('<H',original,pt+2)[0]==struct.unpack_from('<H',original,ot+2)[0]==113
    pixels=[];layouts=[];previous=[]
    for i in range(113):
        p=portraits.entry(original,pt,i);raw,end=portraits.decode(original,p)
        pixels.append(original[p:end]);_,oam=portraits.layout(original,portraits.entry(original,ot,i))
        layouts.append(oam);previous.append((raw,oam))
    figures=[miniatures.decode(original,mt,i) for i in range(64)]
    mapping=bytearray(original[mp:mp+276*2])+bytearray(8)
    rom=bytearray(original);cursor=START;segments=[];patches=[];jobs=[];badges=[]
    def add(raw,label):
        nonlocal cursor
        p=(cursor+3)&~3;cursor=p+len(raw);assert cursor<=END
        rom[p:cursor]=raw;segments.append(dict(offset=p,bytes=len(raw),sha256=sha(raw),label=label));return p
    def patch(at,raw,label):
        before=bytes(rom[at:at+len(raw)]);rom[at:at+len(raw)]=raw
        patches.append(dict(offset=at,before=before.hex(),after=raw.hex(),label=label))
    jt=word(0xc8598)
    for n,u in enumerate(menu['units']):
        job=126+n;source=checked(u['portrait']);receipt=json.loads(checked(u['portraitReceipt']).read_text())
        im=Image.open(source);assert im.mode=='P' and im.size==(48,56) and max(im.tobytes())<48
        assert receipt['native']==u['portrait']
        pal=receipt['palette'];index=pal['index'];assert index<165
        palette=miniatures.decode(original,portraits.PALETTES[0],index)
        assert list(struct.unpack('<48H',palette))==pal['words']
        rgb=[((w>>s)&31)*255//31 for w in pal['words'] for s in (0,5,10)]
        assert im.getpalette()[:144]==rgb and im.info.get('transparency')==0
        # Exact indices and orientation from the accepted 48x56 window. The
        # native portrait consumer flips the transport object horizontally.
        flipped=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        transported=Image.new('P',(64,64))
        transported.paste(flipped.point(lambda x:x+96 if x else 0),(8,8))
        raw=portraits.pack(transported);pixels.append(portraits.encode(raw))
        oam=struct.pack('<4H',1,0x20c0,0xc1c8,0);layouts.append(oam)
        restored=transported.crop((8,8,56,64)).point(lambda x:x-96 if x else 0).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        assert restored.tobytes()==im.tobytes()
        patch(jt+job*52+13,bytes((113+n,index,index)),u['slug']+' portrait/palette selectors')
        wheel=Image.open(checked(u['wheel']['native']));assert wheel.mode=='P' and wheel.size==(32,40)
        figure=pack_tiles(wheel,20);assert sha(figure)==u['wheel']['tileSha256'];figures.append(figure)
        for resource in (276+n*2,277+n*2):struct.pack_into('<H',mapping,resource*2,64+n)
        badge=Image.open(checked(u['badges']['eligible']));assert badge.mode=='P' and badge.size==(32,16)
        badges.append(pack_tiles(badge,8))
        jobs.append(dict(job=job,slug=u['slug'],portrait=113+n,palette=index,miniature=64+n,
            portraitSource=u['portrait'],portraitTilesSha256=sha(raw),wheelSource=u['wheel']['native'],badgeSource=u['badges']['eligible']))
    newpt=add(portraits.archive(pixels,4),'115 portrait entries')
    newot=add(portraits.archive(layouts,2),'115 portrait layouts')
    newmt=add(miniatures.encode(figures),'66 wheel figures')
    newmp=add(mapping,'280 resource-to-wheel selectors')
    for refs,old,new in ((portraits.PIXEL_LITERALS,pt,newpt),(portraits.LAYOUT_LITERALS,ot,newot),
                         (miniatures.LITERALS,mt,newmt),((0x87bd4,0x87c54,0x87d8c),mp,newmp)):
        for p in refs:
            assert word(p)==old;patch(p,struct.pack('<I',0x08000000+new),'archive pointer')
    # Verify all original records after native-format decoding, not just the
    # two new images. No palette archive or pointer changes are authorized.
    for i,(raw,oam) in enumerate(previous):
        assert portraits.decode(rom,portraits.entry(rom,newpt,i))[0]==raw
        assert portraits.layout(rom,portraits.entry(rom,newot,i))[1]==oam
    for i,raw in enumerate(figures):assert miniatures.decode(rom,newmt,i)==raw
    for p in portraits.PALETTE_LITERALS:assert rom[p:p+4]==original[p:p+4]
    allowed=set(range(START,cursor))|{i for p in patches for i in range(p['offset'],p['offset']+len(bytes.fromhex(p['after'])))}
    assert len(rom)==len(original) and all(a==b or i in allowed for i,(a,b) in enumerate(zip(rom,original)))
    digest=hashlib.sha1(rom).hexdigest();out=ROOT/'build/expansion/chemist-progressions/menu'/digest;out.mkdir(parents=True,exist_ok=True)
    target=out/'candidate.gba';target.write_bytes(rom)
    # Preserve the first ten accepted badges from their installed consumer.
    memory=Path(json.loads((ROOT/'build/expansion/memory-fixes/current.json').read_text())['manifest'])
    old=json.loads(memory.read_text())['components']['preview'];at=old['symbols']['original_job_icons']-0x08000000
    oldbadges=original[at:at+2560];assert len(oldbadges)==2560
    allbadges=[oldbadges[i*256:(i+1)*256] for i in range(10)]+badges
    original_icon=0x08000000+0xcb9e0
    # The original-icon fallback is resolved by the code builder. A direct
    # CB9E0 fallback would recurse into the replacement native entry.
    header=out/'job-icons.h';header.write_text('#include <stdint.h>\nextern unsigned ffta_cp_original_icon(void *,unsigned);\n#define FFTA_ORIGINAL_ICON ffta_cp_original_icon\nstatic const uint8_t original_job_icons[12][256]={\n'+',\n'.join('{'+','.join(map(str,b))+'}' for b in allbadges)+'\n};\n')
    result=dict(status='Menu transport verified; equipment header awaits code installation and rendered acceptance',
        path=str(target),romSha1=digest,parent=record(parent),reservation=[START,END],used=[START,cursor],
        segments=segments,patches=patches,jobs=jobs,pixelArchive=newpt,oamArchive=newot,
        miniatureArchive=newmt,miniatureMapping=newmp,header=record(header),source=record(Path(__file__)))
    manifest=out/'manifest.json';manifest.write_text(json.dumps(result,indent=2)+'\n')
    (out.parent/'current.json').write_text(json.dumps(dict(manifest=str(manifest)))+'\n')
    print(json.dumps(dict(status='passed',portraits=115,figures=66,romSha1=digest,manifest=str(manifest))))
    return result

if __name__=='__main__':build()
