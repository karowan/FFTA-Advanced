"""Replay the fixed Counter Rhythm blocker and record native code integrity."""
import pathlib,json,struct,ctypes as C
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-reaction-playback.py';ns={'__file__':str(source),'__name__':'dancer_diagnostic'}
exec(compile(source.read_text().split('for lesson,job,race,weapon,hidden in ')[0],str(source),'exec'),ns)
e=ns['E'](ns['TEST_ROM']);out=ns['OUT']/'dancer-diagnostic';out.mkdir(exist_ok=True);events=[]
try:
 e.load(ns['OUT']/'DNC-R2-on/confirmation.state');e.set_memory(ns['LOG']+148,struct.pack('<II',1,0))
 initial=C.string_at(*e.maps[0x03000000]);e.run(8,256)
 for frames in range(0,1801,12):
  iw=C.string_at(*e.maps[0x03000000]);r=e.memory()
  changes=[i for i in range(ns['CODE_FIRST'],ns['CODE_LAST']) if iw[i]!=initial[i]]
  completed=ns['word'](r,ns['LOG'])==0x504c4159
  if changes or completed or frames==1800:
   stem=out/str(frames);e.save(stem.with_suffix('.state'));stem.with_suffix('.ram').write_bytes(r);stem.with_suffix('.iwram').write_bytes(iw)
   events.append(dict(frames=frames,completed=completed,changedCode=[hex(i) for i in changes]))
   break
  e.run(12)
finally:e.close()
(out/'report.json').write_text(json.dumps(events,indent=2));print(json.dumps(dict(path=str(out),events=events),indent=2))
