"""Read-only baseline-color evidence for live, untransformed class bodies.

Call only in declared movement/idle scenarios after opening fades finish.
Does not normalize native palette phases or accept arbitrary transformed colors.
"""
import struct

def observe(meta,rom,ram,palette,oam,check,allowed):
    base=meta['ramReservation'][0]-0x02000000
    slots=meta['historySlots'];binding=base+meta['bindingOffset']
    keys=ram[base+meta['variantOffset']:base+meta['variantOffset']+slots]
    scales=ram[base+meta['variantOffset']+slots:base+meta['variantOffset']+2*slots]
    tags=ram[base+meta['tagOffset']:base+meta['tagOffset']+128]
    visible=ram[base+meta['visibleColorsOffset']:base+meta['visibleColorsOffset']+slots*32]
    p=meta['symbols']['ffta_art_custom_colors']-0x08000000
    colors=struct.unpack_from('<160H',rom,p)
    active,applied,restored,failed=struct.unpack_from('<4I',ram,base+2572)
    refused=struct.unpack_from('<4I',ram,base+meta['refusalOffset'])
    unsupported=struct.unpack_from('<I',ram,binding+meta['bindingCounterOffset']+8)[0]
    check(not failed and not unsupported and not any(refused),'no custom palette allocation or unsupported effect failure')
    seen=set();banks=set();objects=[]
    for index,slot in enumerate(tags):
        if slot>=slots:continue
        a,b,c=struct.unpack_from('<3H',oam,index*8)
        if a&0x300==0x200:continue
        owner=keys[slot]>>4;scale=scales[slot];bank=c>>12
        check(owner in allowed and scale in (19,32),'owner and brightness match declared racial class')
        expected=struct.pack('<16H',*[sum((((color>>shift)&31)*scale//32)<<shift for shift in (0,5,10)) for color in colors[owner*16:owner*16+16]])
        check(visible[slot*32:slot*32+32]==expected==palette[512+bank*32:544+bank*32],
            'exact generated baseline reaches owned hardware bank')
        seen.add(owner);banks.add(bank);objects.append(dict(index=index,slot=slot,owner=owner,bank=bank,scale=scale))
    check(active==sum(1<<bank for bank in banks),'active mask equals actual tagged hardware banks')
    check(bool(seen),'at least one generated body actually displayed')
    return dict(active=active,applied=applied,restored=restored,failed=failed,unsupported=unsupported,
        refusals=list(refused),owners=sorted(seen),objects=objects)
