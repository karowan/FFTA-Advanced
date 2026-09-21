"""Tempest Combo native initiation, participation, donor match and cold resume."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
source=(ROOT/'scripts/test-combos-in-game.py').read_text()
start=source.index("ROOT=pathlib.Path(__file__)")
end=source.index("ROWS=",start)
source=source[:start]+"""ROOT=pathlib.Path(__file__).resolve().parents[3];meta=_load_job_candidate(ROOT/'build/expansion/probes/viking/current.json');path=pathlib.Path(meta['path']);rom=path.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
FIX=path.parent/'fixture';assert (FIX/'frozen.gba').read_bytes()==rom
OUT=path.parent/'combo-in-game';OUT.mkdir(exist_ok=True);ROM=OUT/'frozen.gba';ROM.write_bytes(rom);START=FIX/'battle-ready.state';registry=json.loads((ROOT/'build/expansion/registry.json').read_text());Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
"""+source[end:]
source=source.replace("'VIK-C1':453","'VIK-C1':394")
sys.argv=[__file__,'--lesson','VIK-C1']
exec(compile(source,__file__,'exec'))
