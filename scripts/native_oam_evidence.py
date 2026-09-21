"""Exact native-only OAM evidence for a hidden generated body.

Stale custom tags do not describe current hardware when composition returns
before ownership scanning. Require the complete native producer output and
prove no hardware object references the retained body's tile allocation.
"""
import struct
from native_art import sha


def snapshot_ranges(meta):
    base=meta['ramReservation'][0]
    return dict(main=(0x03000000,0x830),auxiliary=(0x03002c50,0x860),mode=(0x03000940,2),
        counters=(base+2572,16),emitted=(base+meta['emittedOffset'],8),
        phase=(base+meta['composePhaseOffset'],4),refusals=(base+meta['refusalOffset'],16),
        unsupported=(base+meta['bindingOffset']+meta['bindingCounterOffset']+8,4),oam=(0x07000000,1024))


def boundary_inputs(meta,event,oam,check):
    check(event['site']=='native-composed' and bytes.fromhex(event['memory']['oam'])==oam,
          'Displayed OAM equals the last actual composition boundary')
    # Only the bounded ranges read by hidden_body/reconstruct are populated.
    # Current foreground buffers may already contain the next frame's geometry.
    ram=bytearray(0x40000);iw=bytearray(0x8000)
    for name,(address,size) in snapshot_ranges(meta).items():
        value=bytes.fromhex(event['memory'][name]);check(len(value)==size,'Complete native boundary '+name)
        if 0x02000000<=address<0x02040000:ram[address-0x02000000:address-0x02000000+size]=value
        elif 0x03000000<=address<0x03008000:iw[address-0x03000000:address-0x03000000+size]=value
    return ram,iw


def shapes_at_composition(meta,rom,event,oam,check):
    _,iw=boundary_inputs(meta,event,oam,check)
    expected,counts=reconstruct(rom,iw)
    # Class composition may replace attr2's palette bank only. This comparison
    # proves original geometry, tile/priority and affine fields, not colors.
    def without_banks(raw):
        raw=bytearray(raw)
        for i in range(128):raw[i*8+5]&=15
        return raw
    check(without_banks(oam)==without_banks(expected),'Complete displayed OAM shapes equal original native producer')
    return dict(nativeShapes=True,counts=counts,videoFrame=event['videoFrame'],cycle=event['cycle'])


def hidden_at_composition(meta,rom,event,oam,tile,allocation,check,*,native=False):
    ram,iw=boundary_inputs(meta,event,oam,check)
    proof=native_tiles_hidden(rom,iw,oam,tile,allocation,check) if native else hidden_body(meta,rom,ram,iw,oam,tile,allocation,check)
    proof.update(videoFrame=event['videoFrame'],cycle=event['cycle'],source='actual native composition boundary')
    return proof


def reconstruct(rom, iw):
    assert len(iw)==0x8000
    assert sha(bytes.fromhex('f0b557464e464546')+rom[0x12c4:0x14c8])=='9b66e36f26b094d61539c4790834bd83d102e90433cf5b7e443c268cabbf8c64'
    assert iw[0x28] in (0,1) and iw[0x2f58] in (0,1)
    bank=iw[0x28]^1;other=iw[0x2f58]^1
    word=lambda p:struct.unpack_from('<I',iw,p)[0]
    front=word(0x2c50+4*bank);ui=word(0x2f60+4*other)
    main=word(0x20+4*bank);tail=word(0x3168+4*other)
    assert front<=48 and ui<=32 and main<=128 and tail<=16
    spans=((0x2c58+384*bank,front),
           (0x2f68+256*other,max(0,min(ui,128-main-front))),
           (0x30+1024*bank,main),(0x3170+128*other,tail))
    expected=bytearray(bytes.fromhex('a800f80000000000')*128);cursor=0
    for source,count in spans:
        count=min(count,128-cursor)
        expected[cursor*8:(cursor+count)*8]=iw[source:source+count*8]
        cursor+=count
    for matrix in range(32):
        if iw[0x3270+32*bank+matrix]:
            for component in range(4):
                p=0x32b0+256*bank+8*matrix+2*component
                expected[matrix*32+component*8+6:matrix*32+component*8+8]=iw[p:p+2]
    return bytes(expected),dict(bank=bank,front=front,ui=ui,main=main,tail=tail,extent=cursor)


def hidden_body(meta,rom,ram,iw,oam,tile,allocation,check):
    base=meta['ramReservation'][0]-0x02000000
    proof=native_tiles_hidden(rom,iw,oam,tile,allocation,check)
    counts=proof['counts']
    active,applied,restored,failed=struct.unpack_from('<4I',ram,base+2572)
    unsupported=struct.unpack_from('<I',ram,base+meta['bindingOffset']+meta['bindingCounterOffset']+8)[0]
    refused=struct.unpack_from('<4I',ram,base+meta['refusalOffset'])
    check(not active and not failed and not unsupported and not any(refused),'Native-only frame has no active custom overlay or refusal')
    check(struct.unpack_from('<I',ram,base+meta['composePhaseOffset'])[0]==1 and
          struct.unpack_from('<I',ram,base+meta['emittedOffset']+4*counts['bank'])[0]==0,
          'Native-only frame returns before ownership scan with no custom emission')
    return dict(proof,active=active,applied=applied,restored=restored)


def native_tiles_hidden(rom,iw,oam,tile,allocation,check):
    """Prove native hardware references none of a retained body's tile range.

    This has no custom-overlay assumptions. The original producer, current
    mapping and every native object span remain required, including8bpp spans.
    """
    expected,counts=reconstruct(rom,iw)
    check(oam==expected,'Complete hidden-body hardware OAM equals original native producer')
    check(bool(struct.unpack_from('<H',iw,0x940)[0]&64),'Native-only tile ranges use current one-dimensional mapping')
    check(0<=tile<1024 and 0<allocation<=1024-tile,'Retained hidden body tile bounds')
    widths=(8,16,32,64,16,32,32,64,8,8,16,32)
    heights=(8,16,32,64,8,8,16,32,16,32,32,64)
    for index in range(128):
        a,b,c=struct.unpack_from('<3H',oam,index*8)
        if a&0x300==0x200 or oam[index*8:index*8+6]==bytes.fromhex('a800f8000000'):continue
        shape=a>>14;size=b>>14
        check(shape<3,'Native-only hardware shape is bounded')
        first=c&(1022 if a&0x2000 else 1023)
        length=widths[shape*4+size]*heights[shape*4+size]//(32 if a&0x2000 else 64)
        check(first+length<=1024 and (first+length<=tile or first>=tile+allocation),
              'Native-only hardware does not reference retained class-body tiles')
    return dict(nativeOnly=True,counts=counts,bodyTiles=[tile,tile+allocation])
