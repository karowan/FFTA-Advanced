"""Run the accepted native ending route on the current engineering candidate.

The changed heap/menu layout makes actual ending actors and scene-owned saving
relevant again. Reuse the original exact deterministic test, ordinary flash and
assertions. Only candidate/output/producer selection changes. Initial scene101
is still a declared one-time input; earned final-battle entry is separate retained
evidence. No old savestate crosses ROMs, and no player save is read or written.
"""
import hashlib
from native_art import ROOT

helper=ROOT/'scripts/test-campaign-ending-scenes.py';raw=helper.read_bytes()
assert hashlib.sha1(raw).hexdigest()=='e5cb244449f183ef3feb92c653df421faeea0c6a'
source=raw.decode()
replacements={
 "meta = json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())":
 "meta = json.loads((ROOT/'build/art/connected/a28b624bb13c8f2f2597a4d4bd3999b17c234b99/manifest.json').read_text())",
 "producer = ROM.parent/'clear-save-20260917T091908.745148Z'":
 "producer = pathlib.Path(meta['fixtureSource']).parent/'clear-save-20260917T091908.745148Z'",
 "prior['romSha1'] == meta['romSha1']":
 "prior['romSha1'] == '1b070824a8dad4995434eee3ab40fa08187a6120'",
 "OUT = ROM.parent/('ending-scenes-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))":
 "OUT = ROOT/'build/art/campaign-ending'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')",
 "OUT.mkdir()":"OUT.mkdir(parents=True)",
 "sourceSha1=sha(pathlib.Path(__file__).read_bytes())":
 "sourceSha1=sha(EFFECTIVE_SOURCE.encode()),historicalHelperSha1='e5cb244449f183ef3feb92c653df421faeea0c6a'",
 "(OUT/'script.py').write_bytes(pathlib.Path(__file__).read_bytes())":
 "(OUT/'script.py').write_bytes(EFFECTIVE_SOURCE.encode())",
}
for before,after in replacements.items():
    assert source.count(before)==1,('Unexpected historical test shape',before)
    source=source.replace(before,after)
exec(compile(source,str(helper),'exec'),dict(__file__=str(helper),__name__='__main__',EFFECTIVE_SOURCE=source))
