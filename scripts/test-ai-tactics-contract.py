"""Reject weakened tactical evidence without running or changing the game.

Checks the outcome predicates with counterexamples, then validates a complete
current-ROM report against the committed per-assertion ratchet. Retained timing
reports must also satisfy the faster September 28 reference, independently of
the older release timing gate. --strict fails on remaining tactical desires.
"""
import argparse
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import runpy

from chemist_candidate import candidate
evaluation=runpy.run_path(str(Path(__file__).with_name('evaluate-ai-tactics.py')))
BASE,ROOT,SPEC,LOCK,digest,judge,regressions=(evaluation[name] for name in
    ('BASE','ROOT','SPEC','LOCK','digest','judge','regressions'))


def self_test():
    unit={'position':[2,2],'ally':False,'judge':False,'hp':1}
    units={'1':unit,'2':dict(unit,position=[3,2],ally=True)}
    good=dict(success=1,action=0,target=1,center=[2,2],destination=[0,2],decisionFrames=100)
    checks=0
    for expectation,field,bad in (
        ({'actions':[0]},'action',23),
        ({'excludeActions':[23]},'action',23),
        ({'target':1},'target',2),
        ({'cover':2},'center',[8,8]),
        ({'minimumEnemyDistance':2},'destination',[1,2]),
        ({'avoidElementalArea':2},'action',23),
        ({},'success',0),
    ):
        case={'expect':expectation}
        assert all(judge(case,good,units).values())
        changed=dict(good);changed[field]=bad
        assert not all(judge(case,changed,units).values()), (expectation,field)
        checks+=2
    row=dict(id='control',seed=0,inputSha256='input',checks={'keep':True,'pending':False},
             result=good)
    report=dict(specSha256='spec',harnessSha256='harness',probeSha256='probe',coreSha256='core',
                seedBoundary='boundary',records=[row])
    lock=copy.deepcopy(report);lock['records'][0]['decisionFrames']=100
    assert not regressions(report,lock)
    better=copy.deepcopy(report);better['records'][0]['checks']['pending']=True
    assert not regressions(better,lock);checks+=2
    for fault in ('lost-pass','slower','missing','duplicate','input','coverage','spec','harness','core','seed-boundary'):
        changed=copy.deepcopy(report);r=changed['records'][0]
        if fault=='lost-pass':r['checks']['keep']=False
        elif fault=='slower':r['result']['decisionFrames']=106
        elif fault=='missing':changed['records']=[]
        elif fault=='duplicate':changed['records'].append(copy.deepcopy(r))
        elif fault=='input':r['inputSha256']='other'
        elif fault=='coverage':del r['checks']['pending']
        elif fault=='spec':changed['specSha256']='other'
        elif fault=='harness':changed['harnessSha256']='other'
        elif fault=='core':changed['coreSha256']='other'
        else:changed['seedBoundary']='other'
        try: rejected=bool(regressions(changed,lock))
        except AssertionError:rejected=True
        assert rejected,fault
        checks+=1
    return checks


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strict',action='store_true')
    args=parser.parse_args()
    checks=self_test()
    spec=json.loads(SPEC.read_text());lock=json.loads(LOCK.read_text())
    for p,h in lock['dependencies'].items():
        assert digest(ROOT/p)==h, ('Evaluation dependency changed',p)
    path=BASE/'latest.json';path=ROOT/json.loads(path.read_text())['report']
    report=json.loads(path.read_text())
    assert report['status']=='completed' and report['romSha1']==candidate()['romSha1']
    assert report['specSha256']==digest(SPEC)
    assert report['harnessSha256']==digest(ROOT/'scripts/evaluate-ai-tactics.py')
    assert report['probeSha256']==digest(ROOT/'scripts/native_ai_eval_probe.py')
    assert report['coreSha256']==digest(ROOT/'tools/mgba-test-core/mgba_libretro.dll')
    cases={c['id']:c for c in spec['cases']}
    expected={(c,seed) for c in cases for seed in spec['seeds']}
    assert {(r['id'],r['seed']) for r in report['records']}==expected
    assert len(report['records'])==len(expected)
    for r in report['records']:
        assert len(r['seedPins'])==1 and r['seedPins'][0]['seed']==r['seed']
        assert r['checks']==judge(cases[r['id']],r['result'],r['units'])
        assert r['passed']==all(r['checks'].values())
    assert report['summary']==dict(passed=sum(r['passed'] for r in report['records']),total=len(expected))
    for p,h in report['pins'].items():assert digest(p)==h,('Input changed',p)
    failures=regressions(report,lock)
    timing=[]
    for profile,reference in lock['timing'].items():
        p=ROOT/'build/expansion/ai-timing'/reference['index']
        p=ROOT/json.loads(p.read_text())['report']
        measured=json.loads(p.read_text())
        assert measured['status']=='completed' and measured['skillProfile']==profile
        assert measured['coreSha256']==lock['coreSha256']
        rows={(r['label'],r['seed']):r for r in measured['records'] if r['build']=='mod'}
        assert len(rows)==len(reference['records'])
        for old in reference['records']:
            r=rows[old['label'],old['seed']]
            assert r['romSha1']==report['romSha1']
            assert r['canonicalInputSha256']==old['inputSha256']
            assert len(r['seedPins'])==1 and r['seedPins'][0]['seed']==r['seed']
            limit=(old['frames']*105+99)//100
            if not 0<r['decisionFrames']<=limit:
                failures.append(dict(profile=profile,job=r['label'],seed=r['seed'],check='retained-speed',maximum=limit))
        timing.append(dict(profile=profile,report=str(p),sha256=digest(p)))
    quality=all(r['passed'] for r in report['records'])
    accepted=not failures and (quality or not args.strict)
    result=dict(accepted=accepted,qualityPassed=quality,quality=report['summary'],romSha1=report['romSha1'],
                evaluatorChecks=checks,regressions=failures,report=str(path),reportSha256=digest(path),timing=timing)
    out=BASE/('gate-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir();(out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return 0 if accepted else 1


if __name__=='__main__':raise SystemExit(main())
