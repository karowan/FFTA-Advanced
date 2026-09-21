"""Fail engineering acceptance on measured extra Move/cancel response frames.

Read authenticated complete native-event evidence; never run a new game,
realign observations, average away a failing input offset, or waive latency.
Passing this bounded gate would not establish every encounter's performance.
"""
import argparse,datetime,hashlib,json
from pathlib import Path
from native_art import ROOT,sha

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--trace',type=Path,required=True)
parser.add_argument('--trace-sha256',required=True)
parser.add_argument('--manifest',type=Path,required=True)
args=parser.parse_args()
out=ROOT/'build/art/response-budget'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];rows=[];failures=[]

def check(ok,label):
    assert ok,label
    checks.append(label)

try:
    raw=args.trace.read_bytes();check(sha(raw)==args.trace_sha256,'Exact complete native-event report authenticated')
    trace=json.loads(raw);meta=json.loads(args.manifest.read_text(encoding='utf-8'))
    check(trace['status']=='passed' and trace['controlKind']=='bypass','Complete observer proof with exact same-ROM compositor-bypass control')
    check(sha(args.manifest.read_bytes())==trace['manifestSha256'],'Exact traced candidate manifest')
    check(hashlib.sha1(Path(meta['path']).read_bytes()).hexdigest()==meta['romSha1']==trace['romSha1'],'Actual candidate ROM bytes authenticated')
    records={(r['case'],r['idleFramesBeforeMove']):r for r in trace['records']}
    check(len(records)==len(trace['records'])==4 and set(records)=={(c,d) for c in ('active','bypass') for d in (0,4)},'Both declared input offsets and both branches present exactly once')
    for delay in (0,4):
        for action in ('move','cancel'):
            active=records['active',delay]['actions'][action]
            control=records['bypass',delay]['actions'][action]
            check(len(active['frames'])==len(control['frames'])==128,'Complete action windows '+str((delay,action)))
            check(active['motion']['positions']==control['motion']['positions'],'Same ordered native motion '+str((delay,action)))
            row=dict(idle=delay,action=action,active={k:active['motion'][k] for k in ('start','end','elapsed')},
                     control={k:control['motion'][k] for k in ('start','end','elapsed')})
            row['extraFrames']={k:row['active'][k]-row['control'][k] for k in ('start','end','elapsed')}
            rows.append(row)
            for metric,delta in row['extraFrames'].items():
                if delta>0:failures.append(f'{action} idle{delay} {metric}: +{delta} frames')
    report=dict(status='failed' if failures else 'passed',romSha1=meta['romSha1'],checks=checks,failures=failures,rows=rows,
                trace=str(args.trace),traceSha256=args.trace_sha256,manifest=str(args.manifest),scope=__doc__)
    destination=out/('failed.json' if failures else 'report.json')
    destination.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=report['status'],checks=len(checks),failures=failures,report=str(destination))))
    if failures:raise SystemExit(1)
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,rows=rows),indent=2)+'\n',encoding='utf-8',newline='\n')
    raise
