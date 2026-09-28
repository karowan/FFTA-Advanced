"""Replay retained paired decisions to audit frame-sampled native action lists."""
import argparse,json,runpy,struct
from contextlib import ExitStack
from ai_planner_seed import PlannerSeed,BOUNDARY
from pathlib import Path
from chemist_candidate import ROOT
from mgba_instruction_trace import InstructionTrace
base=ROOT/'build/expansion/ai-timing'
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--report',type=Path)
args=parser.parse_args()
path=args.report or Path(json.loads((base/'latest-measurement.json').read_text())['report'])
report=json.loads(path.read_text())
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
results=[]
for row in report['records'][:2]:
    folder=Path(row['folder']);changes=[];last=None
    with E(Path(report['fixtureDirectory'])/row['build']/'frozen.gba') as e:
        e.load(folder/'planning-start.state')
        sites={0x080c1eb4:'constructor',0x080c2174:'raw-actions',0x080c21d4:'inclusion-chance',0x080c21d8:'inclusion-result',0x08002804:'rng'}
        snapshots={pc:{'rng':(0x030034b0,4)} for pc in sites}
        trace=PlannerSeed(e,row['seed'],sites,snapshots) if report.get('seedBoundary')==BOUNDARY else InstructionTrace(e,sites,snapshots)
        with trace as observer:
            e.run(6)
        (folder/'constructor-trace.json').write_text(json.dumps(observer.events,indent=2))
        print(row['build'],[(ev['site'],ev['registers'][0],ev['memory']['rng'],hex(ev['registers'][14])) for ev in observer.events if ev['site']!='rng'],flush=True)
        e.load(folder/'planning-start.state')
        with ExitStack() as controls:
            if report.get('seedBoundary')==BOUNDARY:controls.enter_context(PlannerSeed(e,row['seed']))
            for frame in range(row['decisionFrames']):
                ram=e.memory();phase=struct.unpack_from('<H',ram,0x156ec)[0]
                p=struct.unpack_from('<I',ram,0x101f8)[0]-0x02000000
                if 0<=p<0x3a000:
                    count=struct.unpack_from('<H',ram,p+0x58)[0]
                    if 0<count<=40:
                        actions=struct.unpack_from('<'+'H'*count,ram,p+8)
                        if (phase,actions)!=last:
                            changes.append(dict(frame=frame,phase=phase,actions=actions));last=(phase,actions)
                e.run(1)
        assert e.memory()==(folder/'choice-published.ram').read_bytes()
    result=dict(build=row['build'],romSha1=row['romSha1'],exactReplay=True,changes=changes)
    results.append(result);print(json.dumps(result),flush=True)
(path.parent/'action-list-audit.json').write_text(json.dumps(dict(source=str(path),records=results),indent=2))
