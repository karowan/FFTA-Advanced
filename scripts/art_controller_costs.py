"""Read-only direct-call costs inside the native battle controller.

Authenticate actual ARMv4T BL encodings. Candidate sites in literal pools never
count unless executed. Local branches to the controller's common epilogue are
excluded. Calls are measured inclusively, including interrupts and descendants;
do not add nested costs together or call these exclusive CPU measurements.
"""
import hashlib,json,struct
from pathlib import Path
from native_art import ROOT
from native_art import sha

START,END=0x08092784,0x08096b28

def boundaries(rom,movement=False):
    sites,rows={},[]
    assert rom[START-0x08000000:START-0x08000000+12].hex()=='f0b557464e464546e0b4a4b0'
    assert rom[0x96b14:0x96b26].hex()=='012024b038bc9846a146aa46f0bc02bc0847'
    regions=[('native-controller',START,END)]
    upstream_proof=None
    if movement:
        upstream_path=ROOT/'build/expansion/probes/integrated-jobs/current.json'
        upstream_raw=upstream_path.read_bytes();upstream=json.loads(upstream_raw)
        original=Path(upstream['path']).read_bytes()
        assert hashlib.sha1(original).hexdigest()==upstream['romSha1']=='1b070824a8dad4995434eee3ab40fa08187a6120'
        # Bounds are actual adjacent compiled functions in this pinned image.
        for name,start,end in [('ffta_geo_tile',0x091e481e,0x091e489c),
                               ('ffta_geo_tile_entry',0x091e48b8,0x091e48d4),
                               ('ffta_geo_updraft',0x091e4998,0x091e49d6),
                               ('ffta_geo_grounded',0x091e4a1a,0x091e4a4a),
                               ('ffta_geo_field_at',0x091e4a4a,0x091e4b70)]:
            assert upstream['symbols'][name]==start
            assert rom[start-0x08000000:end-0x08000000]==original[start-0x08000000:end-0x08000000]
            regions.append((name,start,end))
        assert rom[0x97814:0x97820]==original[0x97814:0x97820]
        assert struct.unpack_from('<I',rom,0x9781c)[0]==0x091e48b9
        upstream_proof=dict(manifest=str(upstream_path),manifestSha256=sha(upstream_raw),
                            romSha1=upstream['romSha1'],hookBytes=rom[0x97814:0x97820].hex())
    for caller,start,end in regions:
      for pc in range(start,end-3,2):
        a,b=struct.unpack_from('<HH',rom,pc-0x08000000)
        if a&0xf800!=0xf000 or b&0xf800!=0xf800:continue
        displacement=((a&2047)<<12)|((b&2047)<<1)
        if displacement&(1<<22):displacement-=1<<23
        target=pc+4+displacement
        if start<=target<end:continue
        assert 0x08000000<=target<0x0a000000
        rows.append(dict(call=pc,returnPC=pc+4,target=target,caller=caller,instructions=rom[pc-0x08000000:pc-0x08000000+4].hex()))
        # Consecutive BLs share a previous-return/next-call address.
        sites[pc]='controller-cost:'+hex(pc)
        sites[pc+4]='controller-cost:'+hex(pc+4)
    assert rows
    proof=dict(start=START,end=END,codeSha256=sha(rom[START-0x08000000:END-0x08000000]),calls=rows)
    if movement:proof.update(upstream=upstream_proof,regions=[dict(name=n,start=s,end=e,sha256=sha(rom[s-0x08000000:e-0x08000000])) for n,s,e in regions])
    return sites,proof

def summarize(events,proof):
    entries={r['call']:r for r in proof['calls']};exits={r['returnPC']:r for r in proof['calls']}
    active={};results={};shared={}
    for event in events:
        if not event['site'].startswith('controller-cost:'):continue
        pc=int(event['site'].split(':')[1],16)
        if pc in exits:
            row=exits[pc];key=row['call'];stack=active.get(key,[])
            if not stack:
                shared[hex(pc)]=shared.get(hex(pc),0)+1
            else:
                before=stack.pop();cycles=(event['cycle']-before['cycle'])&0xffffffff
                assert 0<cycles<280896*32,'Controller child exceeds bounded observation'
                assert event['registers'][13]==before['registers'][13],'Native call stack imbalance'
                results.setdefault(hex(key),[]).append(dict(target=row['target'],cycles=cycles,
                    videoFrame=before['videoFrame'],stack=before['registers'][13],arguments=before['registers'][:4],returnValue=event['registers'][0]))
        if pc in entries:active.setdefault(pc,[]).append(event)
    pending={hex(k):len(v) for k,v in active.items() if v}
    assert not pending,('Incomplete controller calls',pending)
    assert results,'No actual controller calls observed'
    return dict(calls=results,sharedReturnArrivalsExcluded=shared,
        scope='Complete observed external direct BL invocations from the authenticated regions; inclusive GBA cycles. Indirect calls and descendants outside the declared regions are not separately profiled.')
