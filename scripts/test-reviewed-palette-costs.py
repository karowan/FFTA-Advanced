"""Attribute the remaining response cost on the exact failed candidate.

Read-only instruction observation of a fixed native Move. Compare complete
emulator state to the same unobserved replay, retaining all raw event cycles.
"""
import argparse
import datetime
import hashlib
import json
import runpy
from pathlib import Path
from native_art import ROOT,sha
from art_composition_costs import cost_sites,summarize_costs
from mgba_instruction_trace import InstructionTrace


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--response',type=Path,required=True);args=parser.parse_args()
    prior=json.loads(args.response.read_text());meta=json.loads((ROOT/'build/art/reviewed-integration/grouped-palette-pilot.json').read_text())
    rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']==prior['romSha1']
    live=meta['components']['livePalette'];sites,boundaries=cost_sites(live,rom)
    source=args.response.parent/'focus-ready.state';assert source.is_file()
    out=ROOT/'build/art/reviewed-integration/costs'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];e=None;events=[];failure=None;states=[];frames=[]
    try:
        for observed in (False,True):
            e=E(meta['path']);e.load(source);e.run(6)
            for key in (256,128,128,128):e.run(8,key);e.run(180)
            if observed:
                with InstructionTrace(e,sites,{}) as trace:e.run(8,256);e.run(120)
                events=trace.events
            else:e.run(8,256);e.run(120)
            path=out/('observed.state' if observed else 'plain.state');e.save(path);states.append(sha(path.read_bytes()))
            frames.append(sha(e.frame[0]));e.close();e=None
        assert states[0]==states[1], 'Complete observed emulator state differs'
        assert frames[0]==frames[1], 'Observed final image differs'
        summary=summarize_costs(events)
        stats={key:dict(count=len(values),meanLines=sum(v['cycles'] for v in values)/len(values)/1232,
                        maxLines=max(v['cycles'] for v in values)/1232)
               for key,values in summary['calls'].items()}
        (out/'events.json').write_text(json.dumps(events)+'\n')
        report=dict(status='passed',romSha1=meta['romSha1'],responseSha256=sha(args.response.read_bytes()),
                    sourceStateSha256=sha(source.read_bytes()),states=states,frames=frames,boundaries=boundaries,
                    costs=stats,raw=summary,scope=__doc__)
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(dict(report=str(out/'report.json'),costs=stats)))
    finally:
        if e:e.close()


if __name__=='__main__':main()
