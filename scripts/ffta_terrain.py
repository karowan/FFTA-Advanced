"""Validate reviewed, coordinate-based Geomancer material source."""
import hashlib
from ffta_maps import Maps,COUNT,CLEAN_SHA1

SYMBOLS={'.':0,'R':1,'V':2,'W':4,'H':8,'I':16,'S':18,'G':3,'T':10,'M':6}

def material_table(rom,catalog):
    assert catalog['schema']==2 and catalog['cleanRomSha1']==CLEAN_SHA1
    assert catalog['symbols']==SYMBOLS,'Terrain symbol meanings changed'
    maps=Maps(rom);table=bytearray(163*256);seen=set()
    for entry in catalog['maps']:
        index=entry['map']
        assert type(index) is int and 0<=index<COUNT and index not in seen
        seen.add(index);h=maps.heights(index)
        sources={'heightSha1':h,'arrangementSha1':maps.planar(index),'graphicsSha1':maps.graphics(index).data}
        for field,data in sources.items():
            assert entry[field]==hashlib.sha1(data).hexdigest(),(index,'Stale terrain review',field)
        assert isinstance(entry['review'],str) and entry['review'].strip(),(index,'Missing review rationale')
        rows=entry['rows'];assert len(rows)==16 and all(isinstance(row,str) and len(row)==16 for row in rows)
        for y,row in enumerate(rows):
            for x,symbol in enumerate(row):
                assert symbol in SYMBOLS,(index,x,y,'Unknown material symbol')
                mask=SYMBOLS[symbol]
                assert not mask or h[(y*16+x)*2],(index,x,y,'Material on a void cell')
                table[index*256+y*16+x]=mask
    assert seen==set(range(COUNT)),'Terrain review must cover every native map'
    return table
