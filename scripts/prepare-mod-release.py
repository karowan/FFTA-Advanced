"""Resolve the current sharing artifact into an authenticated local play ROM."""
import argparse,json
from pathlib import Path
from mod_release import ROOT,prepare,local
p=argparse.ArgumentParser();p.add_argument('--channel',default='build/releases/current.json');a=p.parse_args()
print(json.dumps(prepare(local(ROOT,a.channel))))
