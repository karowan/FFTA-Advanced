"""Read-only reconciliation of retained capacity selection/action/return evidence.

Verify exact hashes and complete before/after heap block lists. No emulation,
new fixture, build or player files. Earlier failed run identities stay failed.
"""
import ast, datetime, hashlib, json, struct
from pathlib import Path
from native_art import ROOT, sha

index_path=ROOT/'notes/native-art-capacity-followup-evidence.json';index=json.loads(index_path.read_text())
checks=[];out=ROOT/'build/art/capacity-followup-audit'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    for row in index['files']:check(sha((ROOT/row['path']).read_bytes())==row['sha256'],'Exact retained evidence '+row['path'])
    selection=json.loads((ROOT/'build/art/native-event-roots/20260919T091248.211528Z/report.json').read_text())
    check(selection['status']=='passed' and len(selection['checks'])==4273 and len(selection['missions'])==512 and len(selection['scenarios'])==1612,'Complete declared native selection evidence')
    root=ROOT/'build/art/capacity-action/20260919T092806.315981Z';result=json.loads((root/'report.json').read_text())
    check(result['status']=='passed' and len(result['checks'])==195 and result['candidateSha1']==index['candidateSha1'] and result['romSha1']==index['fixtureRomSha1'],'Exact passing return suffix and candidate/fixture identity')
    prior=json.loads((ROOT/'build/art/capacity-action/20260919T092036.958105Z/failed.json').read_text())
    check(prior['status']=='failed' and prior['error']=='execution/Action roots retired' and result['retainedAction']['samples']==prior['samples'],'Retained actual cast samples preserve failed enclosing outcome')
    execution=[s for s in prior['samples'] if s['phase']=='execution']
    frames=[s['frame'] for s in execution]
    check(frames[-1800:]==list(range(frames[-1]-1799,frames[-1]+1)),'Every one of1800 consecutive action frames has a retained heap observation')
    check(result['damage']=={'12228':1,'13020':1},'Two declared adjacent new-class targets received actual nonlethal damage')
    tree=ast.parse((ROOT/'scripts/probe-ap-copy-heap.py').read_text())
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='heap'],type_ignores=[]),'<retained heap walk>','exec'))
    heaps={name:heap((root/(name+'.ram')).read_bytes()) for name in ('next-turn','status-0','returned-0','status-1','returned-1')}
    for name in ('returned-0','returned-1'):check(heaps[name]==heaps['next-turn'],'Every heap block, payload, address and aggregate restored '+name)
    check(heaps['status-0']==heaps['status-1'],'Repeated Status consumes the identical complete allocation structure')
    check(heaps['status-0']['freePayload']==11052 and heaps['status-0']['largestFree']==8776 and heaps['next-turn']['freePayload']==54632,'Actual minimum and returned free capacity')
    report=dict(status='passed',checks=checks,candidateSha1=index['candidateSha1'],fixtureRomSha1=index['fixtureRomSha1'],
        indexSha256=sha(index_path.read_bytes()),heaps=heaps,scope=__doc__,limitations=['Not an exhaustive script-spawn, all-effect, scene-exit, campaign or save proof.','New full-route helper includes these heap equality assertions; existing playback was not repeated for a static assertion addition.'])
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',checks=checks,error=str(error)),indent=2)+'\n',encoding='utf-8');print('Artifacts: '+str(out));raise
