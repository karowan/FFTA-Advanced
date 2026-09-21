"""Summarize retained exact graphics snapshots; no emulation or acceptance waiver."""
import collections,hashlib,json,sys
from pathlib import Path
path=Path(sys.argv[1]);raw=path.read_bytes();report=json.loads(raw)
assert report['status']=='passed'
rows=[]
for record in report['records']:
    for action,data in record['actions'].items():
        frames=[e for e in data['events'] if e['site']=='graphics-inputs']
        assert len(frames)==128
        uncovered=[];sites=collections.Counter();audited=0;validated=0
        for e in frames:
            spans=[]
            for write in e['writesSincePrevious']:
                sites[(write['kind'],hex(write['pc']))]+=1
                if write['kind']=='thumb-obj-dma':
                    if write['timing']==0:spans.append((write['low'],write['high']))
                else:spans.append((write['address'],write['address']+write['bytes']))
            for tile in e['changedObjTiles']:
                lo=0x06010000+64*tile
                if not any(a<lo+64 and b>lo for a,b in spans):uncovered.append([e['videoFrame'],tile])
            if 'dirtyCache' in e:audited+=1;validated+=e['dirtyCache']['validatedTiles']
        rows.append(dict(case=record['case'],idle=record['idleFramesBeforeMove'],action=action,
            frames=len(frames),exactObjUnchanged=sum(e['objUnchanged'] for e in frames),
            exactOamUnchanged=sum(e['oamUnchanged'] for e in frames),
            visible8bppUnchanged=sum(e['visible8bppUnchanged'] for e in frames),
            changedTilesWithoutObservedWriteOverlap=uncovered,
            writeSites=[dict(kind=k[0],pc=k[1],count=v) for k,v in sites.items()],
            cacheAuditedFrames=audited,cacheTileMaskValidations=validated))
print(json.dumps(dict(trace=str(path),traceSha256=hashlib.sha256(raw).hexdigest(),romSha1=report['romSha1'],rows=rows,
    scope='Exact snapshot equality and observed Thumb write overlap only. A write overlapping a changed64-byte tile does not prove every changed byte had that producer. ARM, BIOS, other store forms and other scenes remain outside coverage. Cache mask audit counts exist only when the observer explicitly enabled that check.'),indent=2))
