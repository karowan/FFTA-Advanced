"""Summarize retained instruction events; never execute a ROM or normalize phases."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('report', type=Path)
args = parser.parse_args()
report = json.loads(args.report.read_text(encoding='utf-8'))
assert report['status'] == 'passed'
rows = []
for record in report['records']:
    for action, data in record['actions'].items():
        events = data['events']
        start = data['frames'][0]['startCycle']
        by_site = {site: [e for e in events if e['site'] == site] for site in
                   ('input', 'compose', 'compose-return', 'vblank-flag-check')}
        polls = by_site['input']
        pairs = list(zip(by_site['compose'], by_site['compose-return']))
        assert len(by_site['compose']) == len(by_site['compose-return']) == 128
        assert all(a['videoFrame'] == b['videoFrame'] for a, b in pairs)
        costs = [((b['cycle']-a['cycle']) & 0xffffffff)/1232 for a, b in pairs]
        key = 1 if action == 'move' else 2  # Native GBA button bits.
        pressed = next(e for e in polls if e['registers'][1] & key)
        gaps = [((b['cycle']-a['cycle']) & 0xffffffff)/280896 for a, b in zip(polls, polls[1:])]
        rows.append(dict(case=record['case'], idle=record['idleFramesBeforeMove'], action=action,
            firstPressedPollFrames=round(((pressed['cycle']-start) & 0xffffffff)/280896, 6),
            moveStart=data['motion']['start'], moveEnd=data['motion']['end'],
            moveDuration=data['motion']['elapsed'], polls=len(polls),
            skippedPaletteDMA=sum(bool(e['frameFlag']) for e in by_site['vblank-flag-check']),
            longestPollGapFrames=round(max(gaps), 6),
            meanComposeScanlines=round(sum(costs)/len(costs), 6),
            maxComposeScanlines=round(max(costs), 6)))
        if 'reuseCounters' in data['frames'][0]:
            frames = data['frames']
            first, last = frames[0]['reuseCounters'], frames[-1]['reuseCounters']
            by_frame = {a['videoFrame']: cost for (a, _), cost in zip(pairs, costs)}
            hit_costs, miss_costs = [], []
            for before, after in zip(frames, frames[1:]):
                delta = after['reuseCounters'][0]-before['reuseCounters'][0]
                (hit_costs if delta else miss_costs).append(by_frame[after['videoFrame']])
            rows[-1]['reuseCountersDeltaAfterFirstFrame'] = [b-a for a,b in zip(first,last)]
            rows[-1]['meanHitScanlines'] = round(sum(hit_costs)/len(hit_costs),6) if hit_costs else None
            rows[-1]['meanNonHitScanlines'] = round(sum(miss_costs)/len(miss_costs),6) if miss_costs else None
        if 'repeatCounters' in data['frames'][0]:
            hits={e['videoFrame'] for e in events if e['site']=='repeat-key-proof'}
            hit_costs=[cost for (a,_),cost in zip(pairs,costs) if a['videoFrame'] in hits]
            nonhit_costs=[cost for (a,_),cost in zip(pairs,costs) if a['videoFrame'] not in hits]
            rows[-1]['auditedRepeatFrames']=len(hits)
            rows[-1]['meanRepeatScanlines']=round(sum(hit_costs)/len(hit_costs),6) if hit_costs else None
            rows[-1]['meanNonRepeatScanlines']=round(sum(nonhit_costs)/len(nonhit_costs),6) if nonhit_costs else None
print(json.dumps(dict(source=str(args.report), romSha1=report['romSha1'],
    frameOrigin='Zero-based video frame containing the first held input; includes eight press frames.',
    rows=rows), indent=2))
