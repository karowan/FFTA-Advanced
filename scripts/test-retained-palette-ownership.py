"""Authenticate retained menu OAM/pixels and inventory actual palette consumers."""
import datetime,hashlib,json,struct
from pathlib import Path
from native_art import ROOT,sha
from native_portraits import decode,entry
root=ROOT/'build/art/generated-portraits/ui/20260917T213052.159909Z'
payload=(root/'report.json').read_bytes();assert sha(payload)=='c834ca3974fd70a783de40e4d0798cbedaea25a3f666f72b8d472e7a74723a0c'
proof=json.loads(payload);assert proof['status']=='passed'
meta=json.loads((ROOT/f'build/art/generated-portraits/{proof["romSha1"]}/manifest.json').read_text())
rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==proof['romSha1']
classes=json.loads((Path(meta['source']).parent/'manifest.json').read_text())
out=ROOT/'build/art/palette-ownership'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];records=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    for job in meta['jobs']:
        name='generated-'+str(job['job']);art=next(v for v in classes['jobs'] if v['job']==job['job'])
        poses=[rom[f['tile']:f['tile']+512] for f in art['frames']]
        portrait=decode(rom,entry(rom,meta['pixelArchive'],job['portrait']))[0]
        for phase in ('wheel0','wheel1','wheel2','wheel3','reopened'):
            obs=proof['observations'][name][phase];stem=root/(name+'-'+phase)
            data={field:stem.with_suffix('.'+field).read_bytes() for field in ('vram','palette','oam')}
            for field,b in data.items():check(sha(b)==obs[field],name+'/'+phase+' authenticated '+field)
            bank_owners={};custom=[];eight=[]
            for index in range(128):
                a,b,c=struct.unpack_from('<3H',data['oam'],8*index)
                if a&0x300==0x200:continue
                tile=c&1023;p=0x10000+tile*32
                if a&0x2000:
                    check([a,b,c]==obs['portraitOAM'] and p==obs['portraitVRAM'],name+'/'+phase+' only authenticated8bpp portrait')
                    check(data['vram'][p:p+len(portrait)]==portrait,name+'/'+phase+' exact8bpp index stream')
                    used=sorted({v//16 for v in portrait if v});eight.append(dict(index=index,banks=used))
                    for bank in used:bank_owners.setdefault(bank,[]).append(dict(index=index,kind='portrait8bpp'))
                else:
                    owned=(a>>14==0 and b>>14==2 and data['vram'][p:p+512] in poses)
                    if owned:custom.append(dict(index=index,tile=tile,bank=c>>12))
                    bank_owners.setdefault(c>>12,[]).append(dict(index=index,kind='customActor' if owned else 'other4bpp'))
            check(len(custom)==1,name+'/'+phase+' exactly one pixel-authenticated custom actor')
            check(len(eight)==1 and eight[0]['banks']==[6,7,8],name+'/'+phase+' portrait reserves exactly banks6/7/8')
            own=custom[0];others=[o for o in bank_owners[own['bank']] if o['kind']!='customActor']
            records.append(dict(job=job['job'],phase=phase,actor=own,actorBankShared=bool(others),bankOwners=bank_owners,
                unusedInCapture=[i for i in range(16) if i not in bank_owners],
                paletteSha256=sha(data['palette'])))
    check(any(r['job']==117 and r['actorBankShared'] for r in records),'Dark Knight original bank is shared with other displayed4bpp graphics')
    result=dict(status='passed',romSha1=proof['romSha1'],checks=checks,captures=records,
        sourceReport=str(root/'report.json'),sourceReportSha256=sha(payload),
        scope='50 authenticated historical menu captures for10 generated classes. Exact actor pixels/OAM and portrait8bpp color-bank demand; conservative4bpp usage includes offscreen enabled objects. Unused in one capture is not a safe global reservation, battle allocation or future-lifetime guarantee.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as e:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(e),checks=checks,captures=records),indent=2)+'\n');print(str(out));raise
