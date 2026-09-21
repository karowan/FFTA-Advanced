"""Give all ten expansion classes independent complete land/water resources.

An unchanged resource transport stage, not production artwork. Original jobs
and all their native graphics remain intact. Menu mappings are extended too.
"""
import hashlib,json,struct
from pathlib import Path
from native_art import ROOT,ANIM,SIZES,sha
from native_actor_import import Arena,clone_resource,START,END,PARTY,PARTY_LITERALS

def build(base_manifest=None, *, publish_current=True):
    parentpath=Path(base_manifest) if base_manifest else ROOT/'build/expansion/probes/integrated-jobs/current.json'
    parent=json.loads(parentpath.read_text())
    original=Path(parent['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==parent['romSha1']
    assert struct.unpack_from('<I',original,0x2102c)[0]==0x08000000+ANIM
    assert struct.unpack_from('<I',original,0x21060)[0]==0x08000000+SIZES
    rom=bytearray(original);arena=Arena(rom);resources=[];jobs=[]
    job_table=struct.unpack_from('<I',original,0xc8598)[0]-0x08000000
    for job in range(116,126):
        record=job_table+job*52
        land,water=struct.unpack_from('<HH',original,record+7)
        first=256+(job-116)*2
        job_resources=[]
        for donor,private,lifetime in [(land,first,'land'),(water,first+1,'water')]:
            resource=clone_resource(original,arena,donor,private)
            resource.update(job=job,lifetime=lifetime)
            resources.append(resource);job_resources.append(private)
        struct.pack_into('<HH',rom,record+7,*job_resources)
        jobs.append(dict(job=job,record=record,race=original[record+4],original=[land,water],resources=job_resources,
                         status='independent unchanged native resources; temporary donors'))
    pointers=list(struct.unpack_from('<248I',original,ANIM))
    sizes=list(struct.unpack_from('<248H',original,SIZES))
    pointers.extend([pointers[0]]*(276-len(pointers)));sizes.extend([sizes[0]]*(276-len(sizes)))
    for r in resources:pointers[r['id']]=0x08000000+r['descriptors'];sizes[r['id']]=r['size']
    table=arena.add(struct.pack('<276I',*pointers),'animation-table')
    size_table=arena.add(struct.pack('<276H',*sizes),'size-table')
    party=bytearray(original[PARTY:PARTY+512])+bytearray(40)
    for r in resources:party[r['id']*2:r['id']*2+2]=original[PARTY+r['originalID']*2:PARTY+r['originalID']*2+2]
    party_table=arena.add(party,'party-image-mapping')
    for literal in PARTY_LITERALS:
        assert struct.unpack_from('<I',original,literal)[0]==0x08000000+PARTY
        struct.pack_into('<I',rom,literal,0x08000000+party_table)
    struct.pack_into('<I',rom,0x2102c,0x08000000+table)
    struct.pack_into('<I',rom,0x21060,0x08000000+size_table)
    from native_menu_actor_width import apply
    menu_width=apply(rom,arena,ROOT/'build/art/class-resources/compile')
    allowed=set(range(START,arena.cursor))|set(range(0x2102c,0x21030))|set(range(0x21060,0x21064))
    for j in jobs:allowed.update(range(j['record']+7,j['record']+11))
    for literal in PARTY_LITERALS:allowed.update(range(literal,literal+4))
    for change in menu_width['changes']:allowed.update(range(change['offset'],change['offset']+change['bytes']))
    assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
    digest=hashlib.sha1(rom).hexdigest();root=ROOT/'build/art/class-resources';out=root/digest;out.mkdir(parents=True,exist_ok=True)
    path=out/'class-resources.gba';path.write_bytes(rom)
    result=dict(path=str(path),romSha1=digest,source=parent['path'],baseRomSha1=parent['romSha1'],
        reservation=[START,END],used=[START,arena.cursor],table=table,sizeTable=size_table,partyTable=party_table,tableCount=276,
        jobs=jobs,resources=resources,segments=arena.segments,menuWidth=menu_width,
        scope='Ten independent complete land/water resources plus matching menu mappings. Original pixels and metadata retained; no new art or custom palette acceptance.')
    previews=[c for c in parent.get('changes',[]) if c['kind']=='Paged native equipment preview']
    assert len(previews)<=1
    if previews:
        preview=dict(previews[0]);s,e=preview['reservation']
        preview['binarySha256']=sha(original[s:s+preview['bytes']])
        result['installedPreview']=preview
    for p in ((out/'manifest.json',root/'current.json') if publish_current else (out/'manifest.json',)):p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(path=str(path),romSha1=digest,bytes=arena.cursor-START,jobs=jobs)))
    return result

if __name__=='__main__':build()
