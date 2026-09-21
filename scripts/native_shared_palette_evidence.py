"""Native party/opposing baseline colors for declared new-class body owners.

Use only after entry fades, in baseline/dim scenarios. Association comes from
actual native wrappers and body allocations, never inactive custom tags. This
does not claim transformed-effect colors or independently prove body pixels.
"""
import struct
from native_art import sha


def observe(rom,ram,palette,oam,wrappers,check,allowed,*,require_visible=True):
    word=lambda p:struct.unpack_from('<I',ram,p)[0]
    half=lambda p:struct.unpack_from('<H',ram,p)[0]
    jobs=struct.unpack_from('<I',rom,0xc8598)[0]-0x08000000
    objects=[];owners=set();allocated=set()
    for unit,wrapper in wrappers.items():
        job=ram[unit+7]
        # Named story characters keep their native appearance even when their
        # fallback gameplay job is new. Only generic presentation1 is mapped.
        if ram[unit+4]!=1 or not 116<=job<=125:continue
        owner=job-116
        check(owner in allowed,'Native allocated owner is declared')
        body=word(wrapper+0x44)-0x02000000
        check(0<=body<=len(ram)-72,'Native body allocation pointer bounded')
        resource=half(body+6);tile=half(body+0x12);allocation=half(body+0x16)
        check(resource in (256+2*owner,257+2*owner),'Native allocated class resource')
        check(0<allocation and tile+allocation<=1024,'Native allocated body tile span')
        side=bool(half(unit+0x28)&0x8000)
        selector=(rom[jobs+52*job+11]>>(4 if side else 0))&15
        colors=struct.unpack_from('<16H',rom,0x419d60+selector*32)
        ramps={scale:struct.pack('<16H',*[sum((((c>>s)&31)*scale//32)<<s for s in (0,5,10)) for c in colors]) for scale in (32,19)}
        allocated.add(owner)
        for index in range(128):
            a,b,c=struct.unpack_from('<3H',oam,index*8)
            if (a,b,c)==(0xa8,0xf8,0) or a&0x300==0x200 or c&1023!=tile:continue
            check(not a&0x2100 and a>>14==0 and b>>14==2,'Native body OAM is32x32 4bpp')
            bank=c>>12;raw=palette[512+32*bank:544+32*bank]
            scales=[s for s,r in ramps.items() if r==raw]
            check(bool(scales),'Exact native side and baseline/dim hardware palette')
            x=b&511;y=a&255
            if x>=256:x-=512
            if y>=160:y-=256
            displayed=x<240 and x+32>0 and y<160 and y+32>0
            if displayed:owners.add(owner)
            objects.append(dict(index=index,owner=owner,bank=bank,scales=scales,displayed=displayed,
                                unit=unit,body=body,resource=resource,paletteSha256=sha(raw)))
    if require_visible:check(bool(owners),'At least one native-palette new class actually displayed')
    else:check(bool(objects),'Native palette checked on emitted objects, which may be clipped offscreen')
    return dict(backend='native',owners=sorted(owners),allocatedOwners=sorted(allocated),objects=objects)
