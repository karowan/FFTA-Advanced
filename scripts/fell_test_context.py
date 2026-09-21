"""Resolve immutable Fell test inputs for a private or assembled ROM."""
import hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
P=ROOT/'build/expansion/probes'
def load_context(current=False):
    private=json.loads((P/'fell-private/current.json').read_text())
    if not current:return private
    main=json.loads((P/'combat.json').read_text());rom=(P/'combat.gba').read_bytes()
    assert hashlib.sha1(rom).hexdigest()==main['romSha1']
    lab=P/'fell-main'/main['romSha1'];lab.mkdir(parents=True,exist_ok=True)
    base=ROOT/'build/expansion/accepted'/private['baseSha1']/'combat.gba'
    base_bytes=base.read_bytes();assert hashlib.sha1(base_bytes).hexdigest()==private['baseSha1']
    for name,data in [('fell.gba',rom),('base.gba',base_bytes)]:
        path=lab/name
        if path.exists():assert path.read_bytes()==data,('Immutable snapshot changed',str(path))
        else:path.write_bytes(data)
    symbols={p[2]:int(p[0],16) for line in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=line.split())==3}
    result=dict(baseSha1=private['baseSha1'],romSha1=main['romSha1'],path=str(lab/'fell.gba'),symbols=symbols,assembled=True)
    (lab/'manifest.json').write_text(json.dumps(result,indent=2))
    return result
