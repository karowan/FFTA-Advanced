"""Record a primary-agent visual review tied to exact current artwork bytes.

Call only after inspecting the source/target sheets. This is not an automatic
quality check or user approval, and it does not establish runtime acceptance.
"""
import argparse
import datetime
import json
from native_art import ROOT,sha

parser=argparse.ArgumentParser()
parser.add_argument('--slug',required=True)
parser.add_argument('--pose',action='append',required=True)
parser.add_argument('--note',required=True)
args=parser.parse_args()
path=ROOT/'src/art/race-study/full-animation-v1.json';catalog=json.loads(path.read_text())
unit=next(u for u in catalog['units'] if u['slug']==args.slug)
assert len(set(args.pose))==len(args.pose)
for pid in args.pose:
    pose=next(p for p in unit['poses'] if p['id']==pid)
    assert pose['status']=='generated-awaiting-review'
    assert sha((ROOT/pose['output']).read_bytes())==pose['outputSha256']
    pose['review']=dict(reviewer='primary agent',date=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        outputSha256=pose['outputSha256'],nativeReferenceSha256=pose['reference']['sha256'],
        originalConceptSha256=unit['originalConcept']['sha256'],note=args.note,
        scope='Source drawing visual review only; not user approval, palette conversion, live playback, or final production acceptance')
    pose['status']='generated-reviewed'
path.write_text(json.dumps(catalog,indent=2)+'\n')
print(f'Recorded exact-source visual review for {len(args.pose)} drawings.')
