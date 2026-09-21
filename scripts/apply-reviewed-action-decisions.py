"""Apply explicit primary visual-review decisions after image inspection.

This is a batch front end, not an automatic artwork judge. The decision file
must enumerate every pose and explain each review or revision.
"""
import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from native_art import ROOT

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('decisions')
args=parser.parse_args()
decisions=json.loads(Path(args.decisions).read_text())
spec=importlib.util.spec_from_file_location('prepare',ROOT/'scripts/prepare-reviewed-actions.py')
prepare=importlib.util.module_from_spec(spec);spec.loader.exec_module(prepare)
for entry in decisions:
    slug=entry['slug']
    assert len({p for group in entry.get('reviews',[]) for p in group['poses']})==sum(len(g['poses']) for g in entry.get('reviews',[]))
    for group in entry.get('reviews',[]):
        command=[sys.executable,str(ROOT/'scripts/record-reviewed-action.py'),'--slug',slug,'--note',group['note']]
        for pose in group['poses']:command+=['--pose',pose]
        subprocess.run(command,check=True,cwd=ROOT)
    for change in entry.get('revisions',[]):
        prepare.revise(slug,change['pose'],change['reason'],change['instruction'])
