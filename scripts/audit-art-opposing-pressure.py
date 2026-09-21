"""Pinned all-class deployment shortage in the exclusive-bank planner.

Reads retained failure only. Counts current unowned4bpp banks and the nonzero
indices of potentially visible whole8bpp source tiles, preserving the planner's
affine/mosaic conservatism. This is not a hardware impossibility proof: changing
palette/tile representation or exact color sharing may avoid exclusive banks.
"""
import datetime,hashlib,json,struct
from pathlib import Path
from native_art import ROOT,sha
index_path=ROOT/'notes/native-art-opposing-pressure-evidence.json'
index=json.loads(index_path.read_text());data={}
for name,entry in index['files'].items():
    raw=(ROOT/entry['path']).read_bytes();assert sha(raw)==entry['sha256'],name
    data[name]=raw
failure=json.loads(data['failed.json']);assert failure['status']=='failed'
assert failure['romSha1']==index['romSha1'] and failure['fixtureRomSha1']==index['fixtureRomSha1']
manifest=ROOT/'build/art/connected'/index['romSha1']/'manifest.json';meta=json.loads(manifest.read_text())
assert hashlib.sha1(Path(meta['path']).read_bytes()).hexdigest()==index['romSha1']
live=meta['components']['livePalette'];base=live['ramReservation'][0]-0x02000000
ram=data['failed.ram'];oam=data['failed.oam'];obj=data['failed.vram'][0x10000:]
tags=ram[base+live['tagOffset']:base+live['tagOffset']+128]
widths=[8,16,32,64,16,32,32,64,8,8,16,32];heights=[8,16,32,64,8,8,16,32,16,32,32,64]
used=set();wanted=set();eight=[];ordinary=[]
for i in range(128):
    a,b,c=struct.unpack_from('<3H',oam,i*8)
    if a&0x300==0x200:continue
    shape=a>>14;size=b>>14;assert shape<3
    if tags[i]!=255:
        assert tags[i]<live['historySlots'] and not a&0x2100 and shape==0 and size==2
        wanted.add(tags[i]);continue
    if not a&0x2000:
        used.add(c>>12);ordinary.append(dict(object=i,bank=c>>12));continue
    width=widths[shape*4+size];height=heights[shape*4+size];start=(c&1022)*32
    assert start+width*height<=32768
    x=b&511;y=a&255
    if x>=256:x-=512
    if y>=160:y-=256
    banks=set();colors=set();tiles=0
    for row in range(0,height,8):
        for col in range(0,width,8):
            px=x+(width-8-col if b&0x1000 else col);py=y+(height-8-row if b&0x2000 else row)
            if not a&0x1100 and (px>=240 or px+8<=0 or py>=160 or py+8<=0):continue
            pixels=obj[start+row*width+col*8:start+row*width+col*8+64];assert len(pixels)==64
            colors.update(p for p in pixels if p);tiles+=1
    banks={p>>4 for p in colors};used.update(banks)
    eight.append(dict(object=i,attributes=[a,b,c],width=width,height=height,x=x,y=y,
                      wholeVisibleTiles=tiles,nonzeroIndices=sorted(colors),banks=sorted(banks)))
assert len(wanted)==9 and used=={0,1,6,7,8,10,11,12}
assert struct.unpack_from('<I',ram,base+2584)[0]==3
assert struct.unpack_from('<4I',ram,base+live['refusalOffset'])==(0,0,0,0)
assert len(wanted)>16-len(used)
out=ROOT/'build/art/opposing-pressure'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
report=dict(status='passed',scope=__doc__,sourceIndex=str(index_path),sourceIndexSha256=sha(index_path.read_bytes()),
            romSha1=index['romSha1'],frame=failure['captures']['failed']['frame'],
            requestedHistories=sorted(wanted),occupiedNativeBanks=sorted(used),availableBanks=16-len(used),
            exclusiveBankShortfall=len(wanted)-(16-len(used)),eightBitObjects=eight,ordinaryObjects=ordinary,
            liveFailure='Three allocator refusals, zero variant/effect refusals; full capacity test remains failed.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status='passed',requested=len(wanted),available=16-len(used),report=str(out/'report.json'))))
