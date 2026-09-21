"""Retain the exact native menu path for a failed mid-turn suspend fixture."""
import argparse,json,pathlib,runpy
ROOT=pathlib.Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--candidate',required=True,type=pathlib.Path);args=parser.parse_args()
rom=args.candidate;folder=rom.parent/'reaction-playback'
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
out=folder/'suspend-diagnostic';out.mkdir(exist_ok=True)
e=E(folder/'playback.gba')
try:
 e.load(folder/'BRD-R1-on/0/suspend-ready.state');old=e.memory(0)
 for n,key in enumerate((1,8,16,256,256,256)):
  e.run(8,key);e.run(300);e.screenshot(out/f'{n}-{key}.png')
  (out/f'{n}-{key}.ram').write_bytes(e.memory())
 report=dict(candidate=str(rom),saveChanged=e.memory(0)!=old,keys=[1,8,16,256,256,256])
 (out/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
finally:e.close()
