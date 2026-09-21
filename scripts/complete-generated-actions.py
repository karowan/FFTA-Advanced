"""Complete missing Moogle weapon streams using existing generated placeholders.

This explicit final stage preserves the connected parent and all native jobs.
Only missing owned land descriptors are added. Native same-race commands,
durations and events are retained; graphics come from the class's imagegen idle
payload. Water attack selection, other action families and final art remain
separate acceptance. No installed selector or player files are changed.
"""
import argparse, datetime, hashlib, json, struct
from pathlib import Path
from PIL import Image
from native_art import ROOT, TILES, OAM, sha, layout, compose, tile_image

# This is an unused subrange of the existing generated-action reservation.
START, END = 0x1f00000, 0x1f80000
PROFILES = ((122, 42, 39, 7), (122, 60, 42, 12), (123, 42, 39, 7))
word = lambda data, p: struct.unpack_from('<I', data, p)[0]
half = lambda data, p: struct.unpack_from('<H', data, p)[0]

def build(source, *, publish_current=True):
    source = Path(source); source_raw = source.read_bytes(); parent = json.loads(source_raw)
    original = Path(parent['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest() == parent['romSha1']
    assert not parent['components'].get('actionCompletion'), 'Completion already applied'
    actions = parent['components']['actions']
    assert actions['reservation'][0] <= START < END <= actions['reservation'][1]
    assert actions['used'][1] <= START and original[START:END] == b'\xff'*(END-START)
    rom = bytearray(original); cursor = START; segments, entries = [], []
    def add(raw, kind):
        nonlocal cursor
        cursor = (cursor+3)&~3; p = cursor; cursor += len(raw)
        assert cursor <= END, 'Completion reservation exhausted'
        rom[p:cursor] = raw
        segments.append(dict(offset=p,bytes=len(raw),kind=kind,sha256=sha(raw)))
        return p
    table = word(original,0x2102c)-0x08000000
    jobs = word(original,0xc8598)-0x08000000
    permissions = word(original,0xcac40)-0x08000000
    descriptors, patches, layouts = {}, [], {}
    gray = [i*16 for i in range(16) for _ in range(3)]
    for job, first_slot, donor_job, weapon_type in PROFILES:
        record = jobs+job*52; donor_record = jobs+donor_job*52
        resource = half(original,record+7); donor_resource = half(original,donor_record+7)
        assert original[record+4] == original[donor_record+4] == 5
        assert word(original,permissions+original[record+0x2d]*4)&(1<<(weapon_type-1))
        assert resource == 256+(job-116)*2
        source_descriptor = word(original,table+resource*4)-0x08000000
        donor_descriptor = word(original,table+donor_resource*4)-0x08000000
        res = next(v for v in actions['resources'] if v['id']==resource)
        assert res['slots']==84 and res['size']==16
        if resource not in descriptors:
            descriptors[resource] = bytearray(original[source_descriptor:source_descriptor+84*12])
        desc = descriptors[resource]
        for slot in (first_slot, first_slot+1):
            assert desc[slot*12:slot*12+12]==bytes(12), 'Never replace an existing action'
            native_descriptor = original[donor_descriptor+slot*12:donor_descriptor+(slot+1)*12]
            q = word(native_descriptor,0)-0x08000000
            assert 0 <= q < len(original)-4, 'Missing native command template'
            count = word(original,q); assert 0 < count < 100
            sequence = bytearray(original[q:q+4+20*count]); frames = []
            idle = word(original,source_descriptor+(slot%2)*12)-0x08000000
            idle_first = idle+4
            assert original[idle_first+9] == 1
            generated_tiles = TILES+word(original,idle_first)
            raw = original[generated_tiles:generated_tiles+512]
            image = tile_image(raw,gray,32)
            bottom = Image.frombytes('L',image.size,image.tobytes()).getbbox()[3]
            for index in range(count):
                frame = q+4+20*index; tile, oam = struct.unpack_from('<II',original,frame)
                opcode = original[frame+9]
                assert 1 <= opcode <= 8, 'Unknown native frame command'
                if opcode != 1 or (tile,oam)==(0xffff,0xffffffff):
                    frames.append(dict(index=index,command=opcode,unchanged=True)); continue
                objects,_ = layout(original,OAM+oam)
                n = max(v['tile']+v['width']*v['height']//64 for v in objects)
                native = compose(original[TILES+tile:TILES+tile+n*32],objects,gray)
                native_bottom = Image.frombytes('L',native.size,native.tobytes()).getbbox()[3]-64
                dy = native_bottom-bottom; assert -128 <= dy < 128
                raw_oam = struct.pack('<4H',1,dy&255,0x8000|((-16)&511),0)
                if raw_oam not in layouts: layouts[raw_oam] = add(raw_oam,'generated-body-layout')
                target_oam = layouts[raw_oam]
                struct.pack_into('<II',sequence,4+20*index,generated_tiles-TILES,target_oam-OAM)
                frames.append(dict(index=index,command=opcode,tiles=generated_tiles,tileSha256=sha(raw),oam=target_oam,
                    nativeBottom=native_bottom,generatedBottom=bottom,y=dy))
            target = add(sequence,'native-commands-generated-pixels')
            desc[slot*12:(slot+1)*12] = native_descriptor
            struct.pack_into('<I',desc,slot*12,target+0x08000000)
            entries.append(dict(job=job,resource=resource,slot=slot,weaponType=weapon_type,
                donorJob=donor_job,donorResource=donor_resource,sourceSequence=q,sequence=target,
                descriptorSha256=sha(native_descriptor),sourceSequenceSha256=sha(original[q:q+4+20*count]),frames=frames))
    for resource, desc in descriptors.items():
        target = add(desc,'completed-owned-descriptors'); p = table+resource*4
        patches.append(dict(offset=p,before=original[p:p+4].hex(),after=struct.pack('<I',target+0x08000000).hex()))
        struct.pack_into('<I',rom,p,target+0x08000000)
    allowed = set(range(START,cursor))
    for patch in patches: allowed.update(range(patch['offset'],patch['offset']+4))
    assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom))), 'Unexpected change outside owned streams'
    digest = hashlib.sha1(rom).hexdigest(); out = ROOT/'build/art/action-completion'/digest; out.mkdir(parents=True,exist_ok=True)
    path = out/'FFTA_Completed_Actions.gba'; path.write_bytes(rom)
    component = dict(path=str(path),romSha1=digest,source=parent['path'],baseRomSha1=parent['romSha1'],
        sourceManifest=str(source),sourceManifestSha256=sha(source_raw),reservation=[START,END],used=[START,cursor],
        entries=entries,segments=segments,patches=patches,scope=__doc__)
    (out/'manifest.json').write_text(json.dumps(component,indent=2)+'\n',encoding='utf-8')
    connected = dict(parent,path=str(path),romSha1=digest,romSha256=sha(rom),
        components=dict(parent['components'],actionCompletion=component),
        status='Engineering candidate; missing Moogle weapon streams completed; acceptance remains separate')
    folder = ROOT/'build/art/connected'/digest; folder.mkdir(parents=True,exist_ok=True)
    (folder/'manifest.json').write_text(json.dumps(connected,indent=2)+'\n',encoding='utf-8')
    view = json.loads((source.parent/'live-palette-view.json').read_text())
    view.update(path=str(path),romSha1=digest,connectedManifest=str(folder/'manifest.json'),actionCompletion=str(out/'manifest.json'))
    (folder/'live-palette-view.json').write_text(json.dumps(view,indent=2)+'\n',encoding='utf-8')
    report = dict(status='passed',romSha1=digest,sourceManifestSha256=sha(source_raw),
        manifest=str(folder/'manifest.json'),view=str(folder/'live-palette-view.json'),addedSlots=len(entries),bytes=cursor-START,
        scope='Exact scoped construction only; no native runtime acceptance.')
    runs = ROOT/'build/art/action-completion/runs'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'); runs.mkdir(parents=True)
    (runs/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    if publish_current:
        (ROOT/'build/art/action-completion/current.json').write_text(json.dumps(view,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report)); return connected

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    args=parser.parse_args(); build(args.source)
