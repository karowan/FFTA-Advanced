"""Read-only frame-boundary PC sampling of retained AI timing cases.

This uses the authenticated core ABI to READ CPU registers, with a one-time declared RNG input controller at candidate construction.
The PC sampler itself never changes game state. Samples locate
likely hot paths, not exact inclusive/exclusive function costs. Each replay
must reproduce the complete retained decision-boundary RAM byte for byte.
"""
from contextlib import ExitStack
import collections, hashlib, json, runpy
from pathlib import Path
from datetime import datetime, timezone
from chemist_candidate import ROOT, candidate
from mgba_instruction_trace import InstructionTrace
from ai_planner_seed import PlannerSeed, BOUNDARY

BASE = ROOT / 'build/expansion/ai-timing'
source = Path(json.loads((BASE/'latest-measurement.json').read_text())['report'])
report = json.loads(source.read_text())
assert report['status']=='completed'
assert any(r['romSha1']==candidate()['romSha1'] for r in report['records'])
codepath=ROOT/'build/expansion/chemist-progressions/code/manifest.json'
code=json.loads(codepath.read_text())
binary=Path(code['binary']).read_bytes()
assert hashlib.sha256(binary).hexdigest()==code['binarySha256']
functions=[(s['address']&~1,(s['address']&~1)+s['bytes'],n) for n,s in code['symbols'].items()]
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
out=BASE/('profile-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
out.mkdir()
records=[]
for row in report['records']:
    if row['seed']!=5 or row['actor'] not in ('0x188','0x5a8'):continue
    folder=Path(row['folder'])
    rom=Path(report['fixtureDirectory'])/row['build']/'frozen.gba'
    image=rom.read_bytes()
    assert hashlib.sha1(image).hexdigest()==row['romSha1']
    if row['build']=='mod':assert image[0x1a50000:0x1a50000+len(binary)]==binary
    def symbol(pc):
        if row['build']=='mod':
            names=[n for start,end,n in functions if start<=pc<end]
            if len(names)==1:return names[0]
        return f'native/unresolved {pc&~0xfff:08x}'
    with E(rom) as e, ExitStack() as seed_scope:
        e.load(folder/'planning-start.state')
        pin = PlannerSeed(e,row['seed']) if report.get('seedBoundary')==BOUNDARY else None
        reader=InstructionTrace(e,{})  # No context entry: no host hooks installed.
        original=reader.slot.value
        if pin: seed_scope.enter_context(pin)
        samples=[]
        for frame in range(row['decisionFrames']):
            r=e.memory()
            phase=int.from_bytes(r[0x156ec:0x156ee],'little')
            if phase==1: seed_scope.close()
            pc,lr,cpsr=reader.registers[15],reader.registers[14],reader.registers[16]
            samples.append(dict(frame=frame,phase=phase,pc=hex(pc),lr=hex(lr),mode=cpsr&31,
                                symbol=symbol(pc),caller=symbol(lr&~1)))
            e.run(1)
        assert e.memory()==(folder/'choice-published.ram').read_bytes(), 'Observed replay differs from ordinary execution'
        if pin:
            seed_scope.close()
            assert len(pin.pins)==1
        assert reader.slot.value==original, 'Host dispatch restored'
        hot=collections.Counter(s['symbol'] for s in samples if s['phase']==1)
        callers=collections.Counter(s['caller'] for s in samples if s['phase']==1)
        rec=dict(build=row['build'],job=row['label'],seed=5,romSha1=row['romSha1'],
                 sourceStateSha256=hashlib.sha256((folder/'planning-start.state').read_bytes()).hexdigest(),
                 exactReplay=True,phase1Samples=sum(hot.values()),hot=hot.most_common(20),callers=callers.most_common(20),samples=samples)
        records.append(rec)
        print(json.dumps({k:v for k,v in rec.items() if k!='samples'}),flush=True)
value=dict(status='completed',source=str(source),sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),
           codeManifestSha256=hashlib.sha256(codepath.read_bytes()).hexdigest(),scope=__doc__,records=records)
(out/'report.json').write_text(json.dumps(value,indent=2))
(BASE/'latest-profile.json').write_text(json.dumps(dict(report=str(out/'report.json'))))
