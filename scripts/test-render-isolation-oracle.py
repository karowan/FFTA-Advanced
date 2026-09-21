"""Retained-capture rendering proof plus corrupt-data rejection controls."""
import datetime,hashlib,json,struct
from pathlib import Path
from native_art import ROOT,sha
from actor_render_evidence import compare

meta=json.loads((ROOT/'build/art/generated-actor-poc/a914169fe4d715192028ebebcfbfc6437b8b458b/manifest.json').read_text())
original=Path(meta['source']).read_bytes();changed=Path(meta['path']).read_bytes()
assert hashlib.sha1(original).hexdigest()==meta['baseRomSha1']
assert hashlib.sha1(changed).hexdigest()==meta['romSha1']
# This retained failed run remains a failure under its original fixed-block
# assertion. Analyze it independently, never overwrite/relabel that report.
new=ROOT/'build/art/generated-actor-poc/battle/20260917T182600.672585Z'
old=ROOT/'build/art/actor-import/battle/20260917T181957.011026Z'
prior=json.loads((old/'report.json').read_text());failed=json.loads((new/'failed.json').read_text())
assert prior['status']=='passed' and failed['status']=='failed'
assert prior['baseRomSha1']==meta['baseRomSha1'] and failed['romSha1']==meta['romSha1']
out=ROOT/'build/art/generated-actor-poc/oracle'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True,exist_ok=False);checks=[];reports={};controls=[];bg={}
try:
    for name,entry in prior['observations']['baseline'].items():
        v=(old/f'baseline-{name}.vram').read_bytes();assert sha(v)==entry['vram']
        bg[name]=v[:0x10000]
    for name,entry in failed['observations']['relocated'].items():
        a=(old/f'baseline-{name}.vram').read_bytes();b=(new/f'relocated-{name}.vram').read_bytes()
        assert sha(b)==entry['vram']
        ra=(old/f'baseline-{name}.ram').read_bytes();rb=(new/f'relocated-{name}.ram').read_bytes()
        phases={'deployed':bg['deployed']} if name=='deployed' else {k:v for k,v in bg.items() if k!='deployed'}
        report=compare(original,changed,ra,rb,a,b,phases);reports[name]=report
        checks.extend(name+'/'+v for v in report['checks'])
        if name=='battle-ready':
            selected=report['actors'][0]['generated']
            for label,where in [('neighbor tiles',0x10000+selected['tile']*32+32),('background',0x200),('unowned OBJ tiles',0x17fe0)]:
                damaged=bytearray(b);damaged[where]^=0x37
                try:compare(original,changed,ra,rb,a,damaged,phases)
                except AssertionError as error:controls.append(dict(mutation=label,rejectedBy=str(error)))
                else:raise AssertionError('Oracle accepted corruption: '+label)
            damaged=bytearray(rb);struct.pack_into('<H',damaged,selected['address']+0x16,1)
            try:compare(original,changed,ra,damaged,a,b,phases)
            except AssertionError as error:controls.append(dict(mutation='actor allocation',rejectedBy=str(error)))
            else:raise AssertionError('Oracle accepted corrupted allocation')
    assert len(controls)==4
    report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,controls=controls,captures=reports,
                scope='Independent retained-capture analysis and four corruption controls. Original failed runtime report preserved; no emulator or player state touched.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status='passed',checks=len(checks),controls=len(controls),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,controls=controls),indent=2)+'\n');raise
