"""Disposable ordinary-UI route from the early-town seed to the first mission."""
import hashlib,importlib.util,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('h',ROOT/'scripts/emulator-test.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
out=ROOT/'build/expansion/probes/battle-entry';out.mkdir(exist_ok=True)
resume='--resume' in sys.argv
frozen=out/'frozen.gba'
if not resume:frozen.write_bytes((ROOT/'build/expansion/probes/ability-core.gba').read_bytes())
e=h.Emulator(frozen)
def tap(k,w=80):e.run(8,k);e.run(w)
try:
    if resume:e.load(out/'current.state')
    else:
        e.set_memory(0,(ROOT/'build/test-lab/early-town.sav').read_bytes(),0);e.run(3600)
        tap(8,180);tap(256,60);tap(256,60);tap(256,180)
        tap(256,240);tap(256,180);tap(256,180)
    for key in sys.argv[1:]:
        if key!='--resume':tap(int(key,0),180)
    e.screenshot(out/'current.png');e.save(out/'current.state')
    (out/'current.ram').write_bytes(e.memory())
    (out/'rom-sha1.txt').write_text(hashlib.sha1(frozen.read_bytes()).hexdigest())
finally:e.close()
