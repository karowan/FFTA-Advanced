"""Offline regression against preserved real Physician/Sapper generation inputs.

Checks replay and fail-closed provenance/crop/palette guards. No image generation,
gameplay fixtures, ROM modification or runtime tests. Evidence stays in build/art.
"""
import ast
import copy
import json
import runpy
import uuid
from pathlib import Path
from new_job_art_helpers import ROOT, record, checked


def main():
    functions=runpy.run_path(str(ROOT/'scripts/new-job-art.py'))
    source=ROOT/'build/art/chemist-job-art-2026-09-26/base-plan.json'
    original=json.loads(source.read_text())
    out=ROOT/'build/art'/('new-job-art-check-'+uuid.uuid4().hex[:12])
    out.mkdir(parents=True)
    checks=[]
    def attempt(name,edit,expect_error):
        plan=copy.deepcopy(original)
        plan['outputDirectory']=(out/name).relative_to(ROOT).as_posix()
        edit(plan)
        path=out/(name+'.json');path.write_text(json.dumps(plan,indent=2)+'\n')
        try:
            functions['convert'](path)
        except ValueError as error:
            if not expect_error or expect_error not in str(error):raise
            checks.append(dict(name=name,passed=True,rejectedAs=str(error)))
        else:
            if expect_error:raise AssertionError(name+' failed to reject')
            result=json.loads((out/name/'conversion.json').read_text())
            current=json.loads((source.parent/'conversion.json').read_text())
            assert [a['native']['sha256'] for a in result['assets']]==[a['native']['sha256'] for a in current['assets']]
            assert all(a['alphaPreserved'] for a in result['assets'])
            checks.append(dict(name=name,passed=True,identicalNativeAssets=len(result['assets'])))
    attempt('exact-replay',lambda p:None,None)
    attempt('altered-source-hash',lambda p:p['assets'][0]['source'].update(sha256='0'*64),'changed')
    attempt('changed-native-palette',lambda p:p['palette']['words'].__setitem__(1,0),'palette words changed')
    attempt('clipped-body',lambda p:p['assets'][0].update(crop=[128,0,160,32]),'crosses crop')
    attempt('wrong-aspect',lambda p:p['assets'][0].update(logicalGrid=[64,160]),'worksheet aspect')
    ui_functions=runpy.run_path(str(ROOT/'scripts/new-job-ui-art.py'))
    ui_root=source.parent/'ui-v2'
    for slug in ['physician','sapper']:
        for kind,revision in [('portrait','v1'),('icon','v2')]:
            receipt=json.loads((ui_root/slug/f'{kind}-{revision}-receipt.json').read_text())
            request=json.loads(checked(receipt['request']).read_text())
            replay_dir=out/'ui'/slug/kind;replay_dir.mkdir(parents=True)
            replay_request=replay_dir/'request.json';replay_request.write_text(json.dumps(request))
            ui_functions['ingest'](replay_request,checked(receipt['source']),'replay',receipt.get('worksheetBox'),receipt.get('registrationNote'))
            replay=json.loads((replay_dir/f'{kind}-replay-receipt.json').read_text())
            assert replay['native']['sha256']==receipt['native']['sha256']
            assert replay['anchorChanges']==receipt['anchorChanges']
    checks.append(dict(name='four-ui-native-replays-and-anchor-proof',passed=True))
    review_functions=runpy.run_path(str(ROOT/'scripts/review-new-job-actions.py'))
    selections=json.loads((source.parent/'actions/selections.json').read_text())
    selections.setdefault('physician',{})['p999']={}
    bad=out/'unknown-selection.json';bad.write_text(json.dumps(selections))
    try:
        review_functions['build'](source.parent/'actions/actions.json',bad,source.parent/'index.html',source.parent/'bad-review.html')
    except ValueError as error:
        assert 'Unknown selected pose' in str(error)
    else:raise AssertionError('Unknown pose silently accepted')
    checks.append(dict(name='unknown-selection-rejected',passed=True))
    for name in ['new-job-art.py','new_job_art_helpers.py','prepare-new-job-reference.py','prepare-new-job-actions.py','review-new-job-actions.py','new-job-ui-art.py','prepare-new-job-menu.py']:
        ast.parse((ROOT/'scripts'/name).read_text(encoding='utf-8-sig'))
    checks.append(dict(name='python-syntax',passed=True))
    report={'input':record(source),'checks':checks,'runtimeTests':False,'ROMWritten':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'checks':len(checks),'passed':True,'report':str(out/'report.json')}))


if __name__=='__main__':main()
