"""Relocate authenticated actor resources into isolated private ownership.

This unchanged-donor proof is not new artwork. Never patch installed ROMs.
"""
import hashlib,json,struct
from pathlib import Path
from native_art import ROOT,ANIM,SIZES,TILES,OAM,layout,sha

START,END=0x1d10000,0x1d80000
NEW_LAND,NEW_WATER=256,257
PARTY=0x393f0c
PARTY_LITERALS=(0x87bd4,0x87c54,0x87d8c)

class Arena:
    def __init__(self,rom):
        assert rom[START:END]==b'\xff'*(END-START),'Actor import reservation occupied'
        self.rom,self.cursor,self.segments=rom,START,[]
    def add(self,data,kind,original=None):
        self.cursor=(self.cursor+3)&~3
        offset=self.cursor;self.cursor+=len(data)
        assert self.cursor<=END,'Actor import reservation overflow'
        self.rom[offset:self.cursor]=data
        self.segments.append(dict(offset=offset,bytes=len(data),kind=kind,sourceOffset=original,sha256=sha(data)))
        return offset

def clone_resource(rom,arena,idx,new_idx):
    path=ROOT/f'build/art/native-reference/actor-{idx:03}/native.json'
    manifest=json.loads(path.read_text())
    for offset,segment in manifest['segments'].items():
        actual=rom[int(offset):int(offset)+segment['bytes']]
        assert sha(actual)==segment['sha256'],('Native reference drift',idx,offset)
    poses={};tiles={};oams={}
    for key,p in manifest['poses'].items():
        tile_key=(p['tileOffset'],p['tileCount']*32)
        if tile_key not in tiles:
            off,size=tile_key;tiles[tile_key]=arena.add(rom[off:off+size],'tiles',off)
        off=p['oamOffset']
        if off not in oams:
            objects,raw=layout(rom,off);assert objects==p['objects']
            oams[off]=arena.add(raw,'oam',off)
        poses[key]=dict(tile=tiles[tile_key],oam=oams[off],tileCount=p['tileCount'])
    descriptors=bytearray(rom[manifest['tableOffset']:manifest['tableOffset']+12*len(manifest['slots'])])
    sequences={};relocations=[]
    for slot in manifest['slots']:
        i=slot['slot'];old_pointer=struct.unpack_from('<I',descriptors,i*12)[0]
        if not old_pointer:continue
        off=old_pointer-0x08000000
        if off not in sequences:
            count=struct.unpack_from('<I',rom,off)[0]
            assert count==len(slot['frames'])
            seq=bytearray(rom[off:off+4+count*20])
            for f,frame in enumerate(slot['frames']):
                p=poses[frame['pose']];struct.pack_into('<II',seq,4+f*20,p['tile']-TILES,p['oam']-OAM)
            sequences[off]=arena.add(seq,'sequence',off)
        target=sequences[off]
        struct.pack_into('<I',descriptors,i*12,0x08000000+target)
        relocations.append(dict(slot=i,sourceSequence=off,sequence=target))
    table=arena.add(descriptors,'descriptors',manifest['tableOffset'])
    return dict(originalID=idx,id=new_idx,descriptors=table,slots=len(manifest['slots']),size=manifest['size'],poses=poses,sequences=relocations,
                referenceSha256=sha(path.read_bytes()))

def build():
    parent=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
    original=Path(parent['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==parent['romSha1']
    assert struct.unpack_from('<I',original,0x2102c)[0]==0x08000000+ANIM
    assert struct.unpack_from('<I',original,0x21060)[0]==0x08000000+SIZES
    rom=bytearray(original);arena=Arena(rom)
    resources=[clone_resource(original,arena,4,NEW_LAND),clone_resource(original,arena,192,NEW_WATER)]
    pointers=list(struct.unpack_from('<248I',original,ANIM))
    sizes=list(struct.unpack_from('<248H',original,SIZES))
    pointers.extend([pointers[0]]*(NEW_WATER+1-len(pointers)))
    sizes.extend([sizes[0]]*(NEW_WATER+1-len(sizes)))
    for r in resources:pointers[r['id']]=0x08000000+r['descriptors'];sizes[r['id']]=r['size']
    table=arena.add(struct.pack('<'+str(len(pointers))+'I',*pointers),'animation-table')
    size_table=arena.add(struct.pack('<'+str(len(sizes))+'H',*sizes),'size-table')
    # Party/wheel figures are a separate compressed-image consumer indexed by
    # the land resource ID, not by the animation descriptor table.
    party=bytearray(original[PARTY:PARTY+256*2])+bytearray(4)
    for r in resources:
        party[r['id']*2:r['id']*2+2]=original[PARTY+r['originalID']*2:PARTY+r['originalID']*2+2]
    party_table=arena.add(party,'party-image-mapping')
    for literal in PARTY_LITERALS:
        assert struct.unpack_from('<I',original,literal)[0]==0x08000000+PARTY
        struct.pack_into('<I',rom,literal,0x08000000+party_table)
    struct.pack_into('<I',rom,0x2102c,0x08000000+table)
    struct.pack_into('<I',rom,0x21060,0x08000000+size_table)
    jobs=struct.unpack_from('<I',rom,0xc8598)[0]-0x08000000
    record=jobs+116*52
    assert struct.unpack_from('<HH',rom,record+7)==(4,192)
    struct.pack_into('<HH',rom,record+7,NEW_LAND,NEW_WATER)
    allowed=set(range(START,arena.cursor))|set(range(0x2102c,0x21030))|set(range(0x21060,0x21064))|set(range(record+7,record+11))
    for literal in PARTY_LITERALS:allowed.update(range(literal,literal+4))
    assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
    digest=hashlib.sha1(rom).hexdigest();root=ROOT/'build/art/actor-import';out=root/digest;out.mkdir(parents=True,exist_ok=True)
    path=out/'actor-import.gba';path.write_bytes(rom)
    report=dict(path=str(path),romSha1=digest,source=parent['path'],baseRomSha1=parent['romSha1'],
                reservation=[START,END],used=[START,arena.cursor],table=table,sizeTable=size_table,partyTable=party_table,tableCount=len(pointers),jobRecord=record,
                resources=resources,segments=arena.segments,scope='Private unchanged Samurai land/water relocation with wide resource IDs. No new artwork, palette modification, installed build or save changes.')
    for dest in (out/'manifest.json',root/'current.json'):dest.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(path=str(path),romSha1=digest,bytes=arena.cursor-START,resources=[(r['originalID'],r['id']) for r in resources])))
    return report

if __name__=='__main__':build()
