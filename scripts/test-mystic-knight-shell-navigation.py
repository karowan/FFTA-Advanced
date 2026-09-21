"""Replay the retained Shell fixture's eight navigation keys with observations."""
import pathlib,datetime,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
prior=max(p for p in pathlib.Path(meta['path']).parent.glob('shell-playback-*') if (p/'start.state').exists())
source=ROOT/'scripts/test-mystic-knight-shell-playback.py'
exec(compile(source.read_text(encoding='utf-8').split('e=E(TEST_ROM)\ntry:')[0],str(source),'exec'))
check('matching-instrumentation',TEST_ROM.read_bytes()==(prior/'playback.gba').read_bytes())
e=E(TEST_ROM);steps=[]
try:
 e.load(prior/'start.state')
 for index,key in enumerate((256,16,256,256,32,256,32,256)):
  tap(e,key);r=checkpoint(e,'navigation-'+str(index),OUT)
  steps.append(dict(index=index,key=key,active=hex(active(e)),mode=mode(e),phase=half(r,0xf4e8+0xdc),
   command=half(r,0xf4e8+0xa6),selection=r[0xf4e8+0xae],position=list(r[ACTOR+0xf6:ACTOR+0xf8])))
finally:e.close()
print(json.dumps(dict(passed=True,source=str(prior),output=str(OUT),steps=steps),indent=2))
