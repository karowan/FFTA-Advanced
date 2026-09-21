"""Diagnose the retained one-frame response difference at display completion.

Replays the exact failed Move/cancel inputs and compares visible body OAM plus
world position at the native display-return boundary. No gate is relaxed.
"""
import argparse
import hashlib
import json
import datetime
import runpy
import struct
from pathlib import Path
from native_art import ROOT,sha
from native_battle_wrappers import from_emulator
from mgba_instruction_trace import InstructionTrace


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--response',type=Path,required=True)
    parser.add_argument('--scheduler',action='store_true',help='Also observe native input poll, scene update and VBlank scheduling without patching emulated state')
    args=parser.parse_args()
    prior=json.loads(args.response.read_text());meta=json.loads((ROOT/'build/art/reviewed-integration/grouped-palette-pilot.json').read_text())
    rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']==prior['romSha1']
    source=args.response.parent/'focus-ready.state';source_hash=sha(source.read_bytes())
    control=args.response.parent/'mask-bypass.gba';bypass=control.read_bytes()
    offset=meta['components']['livePalette']['symbols']['ffta_art_custom_mask']-0x08000000
    assert rom[:offset]==bypass[:offset] and rom[offset+4:]==bypass[offset+4:] and bypass[offset:offset+4]==bytes(4)
    out=ROOT/'build/art/reviewed-integration/display-response'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];records=[];e=None
    try:
        for case,path in [('candidate',Path(meta['path'])),('mask-bypass',control)]:
            for delay in (0,4):
                states=[];frame_hashes=[];actions={}
                for observed in (False,True):
                    e=E(path);e.load(source);e.run(6)
                    wrapper=from_emulator(rom,e)[0x290]
                    body=struct.unpack_from('<I',e.memory(),wrapper+0x44)[0]-0x02000000
                    tile=struct.unpack_from('<H',e.memory(),body+0x12)[0]
                    for key in (256,128,128,128):e.run(8,key);e.run(180)
                    e.run(delay)
                    sites={0x080004fa:'display-return'}
                    if args.scheduler:sites.update({0x080003fc:'scene-update',0x08000460:'input-poll',0x080004b0:'vblank-start',0x0800042e:'main-loop-return'})
                    snapshots={pc:{'position':(0x02000000+wrapper+8,6)} for pc in sites}
                    snapshots[0x080004fa]['oam']=(0x07000000,1024)
                    trace=InstructionTrace(e,sites,snapshots) if observed else None
                    for name,key in [('move',256),('cancel',1)]:
                        if trace:
                            before=len(trace.events)
                            with trace:e.run(8,key);e.run(120)
                            all_events=trace.events[before:]
                            events=[v for v in all_events if v['site']=='display-return'];assert len(events)>=100
                            if args.scheduler:
                                actions[name+'Scheduler']=[dict(site=v['site'],cycle=v['cycle'],frame=v['videoFrame'],scanline=v['scanline'],frameFlag=v['frameFlag'],nativeFrame=v['nativeFrame'],inputs=v['inputs'],position=list(struct.unpack('<3H',bytes.fromhex(v['memory']['position'])))) for v in all_events]
                            first=events[0]['videoFrame'];rows=[]
                            for event in events:
                                raw=bytes.fromhex(event['memory']['oam']);objects=[]
                                for n in range(128):
                                    a,b,c=struct.unpack_from('<3H',raw,n*8)
                                    if a&0x300==0x200 or c&1023!=tile:continue
                                    if (a,b,c)==(0xa8,0xf8,0):continue
                                    x=b&511;y=a&255
                                    if x>=256:x-=512
                                    if y>=160:y-=256
                                    if x<240 and x+32>0 and y<160 and y+32>0:objects.append([a,b,c&4095])
                                rows.append(dict(frame=event['videoFrame']-first,scanline=event['scanline'],
                                    position=list(struct.unpack('<3H',bytes.fromhex(event['memory']['position']))),objects=objects))
                            assert all(row['objects'] for row in rows),'Focus body missing from hardware display'
                            actions[name]=rows
                        else:e.run(8,key);e.run(120)
                    state=out/f'{case}-{delay}-{observed}.state';e.save(state);states.append(sha(state.read_bytes()));frame_hashes.append(sha(e.frame[0]))
                    e.close();e=None
                assert len(set(states))==len(set(frame_hashes))==1,'Observation changes native replay'
                records.append(dict(case=case,delay=delay,states=states,frameHashes=frame_hashes,actions=actions))
        deltas=[]
        for delay in (0,4):
            a=next(r for r in records if r['case']=='candidate' and r['delay']==delay)
            b=next(r for r in records if r['case']=='mask-bypass' and r['delay']==delay)
            for action,start,target in [('move',48,144),('cancel',144,48)]:
                metrics=[]
                for r in (a,b):
                    rows=r['actions'][action]
                    first=next(row['frame'] for row in rows if row['position'][0]!=start)
                    last=next(row['frame'] for row in rows if row['position'][0]==target)
                    metrics.append(dict(start=first,end=last,duration=last-first))
                deltas.append(dict(delay=delay,action=action,candidate=metrics[0],bypass=metrics[1],
                    extraFrames={k:metrics[0][k]-metrics[1][k] for k in metrics[0]}))
        report=dict(status='passed',scope=__doc__,romSha1=meta['romSha1'],sourceStateSha256=source_hash,
            responseSha256=sha(args.response.read_bytes()),records=records,deltas=deltas,
            interpretation='Diagnostic completed; any positive displayed-response delta remains a timing failure.')
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(dict(report=str(out/'report.json'),deltas=deltas)))
    except BaseException as error:
        (out/'failed.json').write_text(json.dumps(dict(status='failed',error=repr(error),records=records),indent=2)+'\n')
        print('Artifacts: '+str(out));raise
    finally:
        if e:e.close()


if __name__=='__main__':main()
