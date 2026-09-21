"""Reproduce selected pixel conversions and the four connected art stages.

Uses the previously verified v0.7 base, original pinned generated PNGs and
source. This does not rerun the unchanged eight-stage gameplay rebuild.
"""
import datetime,hashlib,json,runpy,subprocess,sys
from pathlib import Path
from native_art import ROOT,sha
before=json.loads((ROOT/'build/art/pipeline/current.json').read_text())
out=ROOT/'build/art/pipeline/rebuild'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True,exist_ok=False)
checks=[]
try:
    convert=runpy.run_path(str(ROOT/'scripts/convert-generated-sprites.py'))['convert']
    for job in json.loads((ROOT/'src/art/imagegen/catalog.json').read_text())['jobs']:
        old=json.loads((ROOT/job['technicalConversion']).read_text())
        source=ROOT/job['privateSource'];assert sha(source.read_bytes())==job['sourceSha256']
        columns=max(f['cell'][0] for f in old['frames'])+1
        rows=max(f['cell'][1] for f in old['frames'])+1
        cuts=[old['frames'][row*columns]['box'][1] for row in range(1,rows)]
        height=round(old['scale']*max(f['bounds'][3]-f['bounds'][1] for f in old['frames']))
        directory=out/str(job['job'])
        convert(source,directory,columns,rows,height,row_cuts=cuts,
                quantizer=old.get('quantizer','coverage'),resampling=old.get('resampling','nearest'))
        new=json.loads((directory/'manifest.json').read_text())
        assert new['paletteSha256']==old['paletteSha256'],job['name']+' palette drift'
        assert [f['tileSha256'] for f in new['frames']]==[f['tileSha256'] for f in old['frames']],job['name']+' frame drift'
        checks.append(job['name']+' original PNG reproduces every indexed frame and palette')
    for name in ['native_actor_import.py','build-generated-actor-poc.py','build-generated-miniature-poc.py','build-art-pipeline.py']:
        result=subprocess.run([sys.executable,str(ROOT/'scripts'/name)],cwd=ROOT,capture_output=True,text=True)
        (out/(name+'.log')).write_text(result.stdout+'\n'+result.stderr)
        assert result.returncode==0,name+' failed: '+result.stderr
        checks.append(name+' source stage completed')
    after=json.loads((ROOT/'build/art/pipeline/current.json').read_text())
    assert before['romSha1']==after['romSha1'] and before['romSha256']==sha(Path(after['path']).read_bytes())
    checks.append('complete composed ROM byte equality to runtime-tested candidate')
    report=dict(status='passed',romSha1=after['romSha1'],checks=checks,
        scope='Ten original generated PNG conversions and four art source stages. Authenticated existing v0.7 base; unchanged gameplay clean-build evidence reused. Not deterministic regeneration of artwork or full expansion acceptance.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=before['romSha1'],checks=checks,error=str(error)),indent=2)+'\n')
    print('Artifacts: '+str(out));raise
