"""Bounded native Throw-impact reference format, distinct from actor resources.

Only the authenticated primary24x24 effect is characterized here. Exporting it
does not authorize changes to original Throw or prove a new action dispatcher.
"""
import struct
from native_art import ROOT,sha,layout,compose
from ffta_maps import lz77

SOURCE,LAYOUT,PALETTE=0x912e78,0x4fe8b0,0x8ea7f0
def expand2(raw):
    return bytes(v for b in raw for v in ((b&3)|((b>>2&3)<<4),(b>>4&3)|((b>>6&3)<<4)))

def literal_lz(raw):
    return struct.pack('<I',len(raw)<<8|0x10)+b''.join(b'\0'+raw[p:p+8] for p in range(0,len(raw),8))

def reference(rom):
    assert rom[SOURCE:SOURCE+4]==bytes.fromhex('0202fd7f')
    packed=lz77(rom,SOURCE+4);pixels=expand2(packed.data)
    assert len(pixels)==0x360
    flags,end=struct.unpack_from('<HH',rom,LAYOUT);assert (flags,end)==(12,92)
    offsets=struct.unpack_from('<4H',rom,LAYOUT+4);assert offsets==(8,34,60,86)
    frames=[]
    for index,offset in enumerate(offsets):
        p=LAYOUT+4+offset
        if index==3:
            assert p==LAYOUT+end-2 and rom[p:p+2]==bytes(2);continue
        objects,data=layout(rom,p)
        assert len(objects)==4 and sum(o['width']*o['height']//64 for o in objects)==9
        assert min(o['tile'] for o in objects)==9*index
        assert max(o['tile']+o['width']*o['height']//64 for o in objects)==9*(index+1)
        frames.append(dict(offset=p,objects=objects,sha256=sha(data)))
    assert rom[PALETTE:PALETTE+2]==bytes((7,3))
    palettes=[]
    for phase in range(7):
        colors=bytes(2)+rom[PALETTE+2+phase*6:PALETTE+8+phase*6]+bytes(24)
        rgb=[((v>>s)&31)*255//31 for v in struct.unpack('<16H',colors) for s in (0,5,10)]
        palettes.append(dict(raw=colors.hex(),rgb=rgb))
    return dict(packed=packed,pixels=pixels,frames=frames,palettes=palettes,flags=flags)

def export(rom,out):
    r=reference(rom);out.mkdir(parents=True,exist_ok=True)
    for phase,pal in enumerate(r['palettes']):
        for index,frame in enumerate(r['frames']):
            # Original OAM uses a24x24 arrangement split16x16,8x16,16x8,8x8.
            compose(r['pixels'],frame['objects'],pal['rgb']).save(out/f'phase-{phase}-frame-{index}.png',bits=4)
    (out/'primary.4bpp').write_bytes(r['pixels'])
    return r
