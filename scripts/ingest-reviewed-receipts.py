"""Resume completed imagegen conversions from exact saved tool receipts.

Receipts record actual tool-returned paths, prompts and referenced inputs.
This only performs the existing technical extraction; it never reviews artwork.
"""
import argparse
import importlib.util
import json
import datetime
from pathlib import Path
from native_art import ROOT,sha


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--slug',required=True)
    args=parser.parse_args()
    spec=importlib.util.spec_from_file_location('reviewed_prepare',ROOT/'scripts/prepare-reviewed-actions.py')
    prepare=importlib.util.module_from_spec(spec);spec.loader.exec_module(prepare)
    folder=ROOT/'build/art/reviewed-integration'/args.slug/'generation-receipts'
    failures=[]
    for path in sorted(folder.glob('*-v*.json')):
        receipt=json.loads(path.read_text())
        catalog=json.loads(prepare.CATALOG.read_text())
        unit=next(u for u in catalog['units'] if u['slug']==args.slug)
        pose=next(p for p in unit['poses'] if p['id']==receipt['pose'])
        gen=pose['generation']
        assert receipt['slug']==args.slug and receipt['tool']=='built-in image_gen'
        if receipt['version']<gen.get('version',1):
            print(json.dumps(dict(pose=pose['id'],status='older-attempt-retained')));continue
        assert receipt['version']==gen.get('version',1)
        assert receipt['prompt']==gen['prompt']
        assert receipt['inputs']==[gen[key] for key in ('template','design','concept')]
        source=Path(receipt['outputPath']);assert source.is_file()
        if pose['status']!='pending':
            assert sha(source.read_bytes())==gen['generatedSource']['sha256']
            print(json.dumps(dict(pose=pose['id'],status='already-ingested')));continue
        try:
            prepare.ingest(args.slug,pose['id'],source)
        except (AssertionError,ValueError) as error:
            failure=dict(pose=pose['id'],receipt=str(path),error=repr(error))
            failures.append(failure);print(json.dumps(failure))
    if failures:
        stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
        (folder/('conversion-failures-'+stamp+'.json')).write_text(json.dumps(failures,indent=2)+'\n')
    if failures:raise SystemExit(1)


if __name__=='__main__':main()
