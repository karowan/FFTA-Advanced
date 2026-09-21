"""Import explicit reviewed native keyframes without filling missing art.

Default delivery mode requires every drawing to pass the independent artwork
gate. --draft is an isolated progress build: pending poses remain listed and
unchanged, unreviewed generated drawings stay marked provisional, and no game
installation, current shipping index, launcher or save is touched.
"""
import argparse
import copy
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path
from PIL import Image
from native_art import ROOT, TILES, OAM, sha, pack_tiles

START, END = 0x1dd0000, 0x1e80000
CATALOG = ROOT/'src/art/race-study/full-animation-v1.json'
DEFAULT_PARENT = ROOT/'build/art/reviewed-integration/grouped-palette-pilot.json'


def build(parent_path=DEFAULT_PARENT, draft=False, native=False, native_conversion=None, output=None):
    # The independent catalog gate authenticates the original concept inputs,
    # native graph, pose bindings, approved files and exact face reuse.
    subprocess.run([sys.executable,str(ROOT/'scripts/validate-reviewed-actions.py'),
                    *([] if draft else ['--require-complete'])],cwd=ROOT,check=True,capture_output=True)
    catalog=json.loads(CATALOG.read_text());parent=json.loads(Path(parent_path).read_text())
    conversions={};conversion_units={};conversion_raw=b'';selector_changes=[]
    if native_conversion:
        assert native and output, 'Color conversion pilot requires native mode and a separate output manifest'
        conversion_raw=Path(native_conversion).read_bytes();conversion_spec=json.loads(conversion_raw)
        selector_changes=conversion_spec.get('selectorChanges',[])
        for conversion in conversion_spec.get('units',[conversion_spec]):
            unit=next(u for u in catalog['units'] if u['job']==conversion['job'])
            assert unit['job'] not in conversion_units,'Duplicate class conversion'
            conversion_units[unit['job']]=conversion
            assert {p['id'] for p in unit['poses']}=={p['pose'] for p in conversion['records']}
            assert len(unit['poses'])==len(conversion['records'])==conversion['poseCount']
            for row in conversion['records']:conversions[(unit['job'],row['pose'])]=row
    original=Path(parent['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==parent['romSha1']
    assert original[START:END]==b'\xff'*(END-START), 'Explicit action reservation is occupied'
    # Palette ownership and actual ROM colors come from this exact parent,
    # not a regeneratable offline palette preview.
    word=lambda data,p:struct.unpack_from('<I',data,p)[0]
    if native:
        assert 'nativePaletteTransport' in parent['components']
        jobs=word(original,0xc8598)-0x08000000
    else:
        live=parent['components']['livePalette'];group=live['paletteGroups']['ownerMap']
        palette_start=live['symbols']['ffta_art_custom_colors']-0x08000000
    table=word(original,0x2102c)-0x08000000
    rom=bytearray(original);cursor=START;segments=[];assets={};tiles={};oams={};missing=[];provisional=[]
    selector_patches=[]
    for change in selector_changes:
        job=change['job'];assert job in conversion_units and 116<=job<=125
        assert job not in {p['job'] for p in selector_patches},'Duplicate selector change'
        offset=jobs+52*job+11;before=original[offset];after=change['after']
        assert before==change['before'] and before!=after
        assert 0<=after<=255 and after&15 in (0,1,2) and after>>4 in (0,1,2)
        assert after&15==conversion_units[job]['nativePalette']
        # Existing native class/side selection byte only; no palette data/code.
        rom[offset]=after
        selector_patches.append(dict(job=job,offset=offset,before=before,after=after,reason=change['reason']))
    def add(raw,kind):
        nonlocal cursor
        cursor=(cursor+3)&~3;offset=cursor;cursor+=len(raw)
        assert cursor<=END, 'Reviewed action reservation overflow'
        rom[offset:cursor]=raw;segments.append(dict(offset=offset,bytes=len(raw),kind=kind,sha256=sha(raw)))
        return offset
    for unit in catalog['units']:
        if native:
            selectors=rom[jobs+52*unit['job']+11]
            owner=selectors&15;palette_at=0x419d60+owner*32
        else:
            owner=group[unit['job']-116];palette_at=palette_start+owner*32
        colors=struct.unpack_from('<16H',original,palette_at)
        for pose in unit['poses']:
            key=(unit['job'],pose['id']);status=pose['status']
            if status not in ('approved-movement','generated-reviewed','generated-awaiting-review'):
                missing.append(dict(job=key[0],pose=key[1],status=status));continue
            if status=='generated-awaiting-review':
                assert draft, 'Unreviewed drawing cannot enter a final build'
                provisional.append(dict(job=key[0],pose=key[1]))
            path=ROOT/pose['output'];assert sha(path.read_bytes())==pose['outputSha256']
            conversion_record=conversions.get(key)
            if conversion_record:
                conversion=conversion_units[unit['job']]
                assert conversion_record['sourceSha256']==pose['outputSha256']
                assert owner==conversion['nativePalette'] and list(colors)==conversion['nativePaletteWords']
                path=ROOT/conversion_record['selected']['path']
                assert sha(path.read_bytes())==conversion_record['selected']['sha256']
                candidate=Image.open(path)
                assert candidate.mode=='P' and candidate.info.get('transparency')==0
                assert candidate.getpalette()[:48]==[v for w in colors for v in [((w>>s)&31)*255//31 for s in (0,5,10)]]
                original_image=Image.open(ROOT/pose['output']).convert('RGBA')
                if conversion_record['selected']['exactApprovedBase']:
                    assert sha(path.read_bytes())==conversion['approvedNativeBaseSha256']
                else:
                    assert candidate.convert('RGBA').getchannel('A').tobytes()==original_image.getchannel('A').tobytes()
            image=Image.open(path).convert('RGBA');assert image.size==(32,32)
            pixels=[]
            for r,g,b,a in image.get_flattened_data():
                if not a:pixels.append(0);continue
                color=round(r*31/255)|(round(g*31/255)<<5)|(round(b*31/255)<<10)
                pixels.append(min(range(1,16),key=lambda n:sum((((color>>s)&31)-((colors[n]>>s)&31))**2 for s in (0,5,10))))
            indexed=Image.new('P',(32,32));indexed.putdata(pixels);raw=pack_tiles(indexed,16)
            if raw not in tiles:tiles[raw]=add(raw,'generated-drawing')
            bottom=image.getbbox()[3];dy=pose['native']['nativeBottom']-bottom
            assert -128<=dy<128
            # Preserve the engine's native baseline and fixed 16-tile allocation.
            # No artist pixels are cropped, scaled or synthesized here.
            dx=pose.get('registration',{}).get('translationX',0)
            gen=pose.get('generation',{});approval=gen.get('registrationApproval',{})
            extended=(abs(dx)<=8 and approval.get('translationX')==dx and
                      approval.get('sourceSha256')==gen.get('generatedSource',{}).get('sha256') and
                      bool(approval.get('reason')))
            assert abs(dx)<=6 or extended, 'Registration requires exact-source visual approval'
            obj=struct.pack('<4H',1,dy&255,0x8000|((-16+dx)&511),0)
            if obj not in oams:oams[obj]=add(obj,'body-oam')
            assets[key]=dict(job=key[0],pose=key[1],status=status,source=str(path.relative_to(ROOT)),
                            sourceSha256=sha(path.read_bytes()),tile=tiles[raw],oam=oams[obj],
                            tileSha256=sha(raw),paletteOwner=owner,paletteSha256=sha(struct.pack('<16H',*colors)),
                            nativeBottom=pose['native']['nativeBottom'],generatedBottom=bottom,y=dy,x=-16+dx,
                            registration=pose.get('registration'))
            if conversion_record:assets[key]['nativeColorConversion']=dict(source=pose['output'],sourceSha256=pose['outputSha256'],
                approvedBaseSha256=conversion['approvedNativeBaseSha256'],method=conversion['method'],
                neighbors=conversion['selectedNeighbors'],exactApprovedBase=conversion_record['selected']['exactApprovedBase'])
            if native:
                assets[key].update(nativePaletteOffset=palette_at,nativeSelector=owner,opposingSelector=selectors>>4)
    changed_entries=set();resources=[];sequence_cache={};draws=0;imported=0;controls=0
    for resource in catalog['resources']:
        entry=table+resource['resource']*4;desc_source=word(original,entry)-0x08000000
        descriptors=bytearray(original[desc_source:desc_source+84*12]);sequences=[]
        for slot in resource['slots']:
            pointer=word(descriptors,slot['slot']*12)
            if not pointer:
                assert not slot['frames'];continue
            source=pointer-0x08000000;count=word(original,source)
            assert count==len(slot['frames'])
            raw=bytearray(original[source:source+4+20*count]);frames=[];replaced=0
            for i,frame in enumerate(slot['frames']):
                offset=4+20*i;assert raw[offset+8]==frame['duration'] and raw[offset+9]==frame['command']
                if frame['command']!=1:controls+=1;continue
                draws+=1;asset=assets.get((resource['job'],frame['pose']))
                if asset:
                    struct.pack_into('<II',raw,offset,asset['tile']-TILES,asset['oam']-OAM)
                    replaced+=1;imported+=1
                frames.append(dict(index=i,pose=frame['pose'],replaced=bool(asset)))
            target=source
            if replaced:
                packed=bytes(raw)
                if packed not in sequence_cache:sequence_cache[packed]=add(packed,'native-sequence')
                target=sequence_cache[packed]
                struct.pack_into('<I',descriptors,slot['slot']*12,target+0x08000000)
            sequences.append(dict(slot=slot['slot'],source=source,target=target,frames=frames))
        target=add(descriptors,'resource-descriptors');struct.pack_into('<I',rom,entry,target+0x08000000)
        changed_entries.update(range(entry,entry+4))
        resources.append(dict(id=resource['resource'],job=resource['job'],lifetime=resource['lifetime'],
                              sourceDescriptors=desc_source,descriptors=target,sequences=sequences))
    assert draft or (not missing and not provisional and draws==imported)
    allowed=changed_entries|set(range(START,cursor))|{p['offset'] for p in selector_patches}
    assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
    digest=hashlib.sha1(rom).hexdigest();folder=ROOT/'build/art/reviewed-actions'/digest;folder.mkdir(parents=True,exist_ok=True)
    def immutable(path,raw):
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists():assert path.read_bytes()==raw, 'Historical evidence cannot be overwritten: '+str(path)
        else:path.write_bytes(raw)
    path=folder/'FFTA_Reviewed_Actions.gba';immutable(path,bytes(rom))
    catalog_raw=CATALOG.read_bytes();parent_raw=Path(parent_path).read_bytes();importer_raw=Path(__file__).read_bytes()
    provenance=folder/'provenance'/sha(catalog_raw+parent_raw+importer_raw+conversion_raw+bytes([draft]))
    archived_catalog=provenance/'catalog.json';immutable(archived_catalog,catalog_raw)
    archived_parent=provenance/'parent-manifest.json';immutable(archived_parent,parent_raw)
    immutable(provenance/'import-reviewed-actions.py',importer_raw)
    if conversion_raw:immutable(provenance/'native-color-conversion.json',conversion_raw)
    # Review-only metadata can change without changing ROM bytes. Keep each
    # provenance revision and every actually imported 32px source immutable.
    for asset in assets.values():
        source=ROOT/asset['source'];archive=folder/'artwork'/(asset['sourceSha256']+'.png')
        immutable(archive,source.read_bytes());asset['originalSource']=asset['source']
        asset['source']=str(archive.relative_to(ROOT)).replace('\\','/')
    result=copy.deepcopy(parent)
    result.update(path=str(path),romSha1=digest,romSha256=sha(rom),source=parent['path'],baseRomSha1=parent['romSha1'])
    proof=dict(catalog=str(archived_catalog.relative_to(ROOT)),catalogSha256=sha(archived_catalog.read_bytes()),
               sourceManifest=str(archived_parent),sourceManifestSha256=sha(archived_parent.read_bytes()),
               reservation=[START,END],used=[START,cursor],table=table,assets=list(assets.values()),resources=resources,segments=segments,
               draft=draft,paletteMode='native-shared' if native else 'historical-custom',productionAccepted=False,drawRecords=draws,importedDrawRecords=imported,controlRecords=controls,
               missing=missing,provisional=provisional,
               scope='Explicit generated pose bindings with original commands/durations and baseline. No runtime or production acceptance.')
    if conversion_raw:proof['nativeColorConversion']=dict(path=str(provenance/'native-color-conversion.json'),sha256=sha(conversion_raw))
    if selector_patches:proof['nativeSelectorChanges']=selector_patches
    result['components']['reviewedActions']=proof
    result['reviewedArtPilot']=dict(productionAccepted=False,fullAnimationCoverage=not missing and not provisional,
                                  scope='Isolated action artwork integration; final palette/consumer/performance gates remain separate')
    result['archivedManifest']=str(provenance/'manifest.json')
    encoded=(json.dumps(result,indent=2)+'\n').encode('utf-8')
    immutable(provenance/'manifest.json',encoded)
    destination=Path(output) if output else ROOT/'build/art/reviewed-integration'/('native-action-candidate.json' if native else 'action-candidate.json')
    destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(encoded)
    print(json.dumps(dict(romSha1=digest,drawRecords=draws,imported=imported,missing=len(missing),unreviewed=len(provisional),bytes=cursor-START)))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--parent',type=Path,default=DEFAULT_PARENT);parser.add_argument('--draft',action='store_true')
    parser.add_argument('--native',action='store_true')
    parser.add_argument('--native-conversion',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args();build(args.parent,args.draft,args.native,args.native_conversion,args.output)
