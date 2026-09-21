"""Grouped-palette Move/cancel timing against an exact-layout mask bypass.

The control changes only the four-byte custom-mask constant; every code byte,
pointer, graphic, actor resource and saved address is identical. It is a timing
control with intentionally wrong colors, never a playable/visual candidate.
"""
import ctypes as C
import argparse
import datetime
import hashlib
import json
import runpy
import struct
from pathlib import Path
from native_art import ROOT, sha
from native_battle_wrappers import from_emulator, fixed_giza_formation
from live_palette_evidence import observe
from mgba_instruction_trace import InstructionTrace


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--complete',action='store_true');args=parser.parse_args()
    index=json.loads((ROOT/'build/art/reviewed-integration'/('complete-entry-latest.json' if args.complete else 'entry-latest.json')).read_text());entry_path=ROOT/index['report']
    assert sha(entry_path.read_bytes())==index['sha256'];entry=json.loads(entry_path.read_text());assert entry['status']=='passed'
    meta=json.loads((ROOT/'build/art/reviewed-integration'/('complete-candidate.json' if args.complete else 'grouped-palette-pilot.json')).read_text());live=meta['components']['livePalette']
    rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==entry['romSha1']==meta['romSha1']
    source=entry_path.parent;out=ROOT/'build/art/reviewed-integration/response'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];menus=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
    checks=[];inputs=[];records=[];e=None;failure=None;deltas=[]
    def check(ok,label):
        assert ok,label
        checks.append(label)
    def tap(key,wait=180):
        inputs.append([8,key,wait]);e.run(8,key);e.run(wait)
    def active():
        r=e.memory();p=struct.unpack_from('<I',r,0xf438)[0]-0x02000000
        return struct.unpack_from('<I',r,p+24)[0]
    def motion(rows,start,target):
        first=next(i for i,p in enumerate(rows) if p[0]!=start)
        last=next(i for i,p in enumerate(rows) if p[0]==target)
        changes=[rows[i] for i in range(1,len(rows)) if rows[i]!=rows[i-1]]
        return dict(start=first,end=last,elapsed=last-first,positions=changes)
    try:
        e=E(meta['path']);e.load(source/'ready.state')
        for turn in range(12):
            if active()==0x02000290:break
            previous=active()
            for key in (32,32,256,256):tap(key)
            for waited in range(0,6300,30):
                if active()!=previous and menus['menu_visible'](e):break
                e.run(30)
            else:raise AssertionError('Native Wait did not reach another turn')
        check(active()==0x02000290,'Native Samurai turn reached')
        fixed_giza_formation(rom,e);e.run(30);e.save(out/'focus-ready.state');e.screenshot(out/'focus-ready.png');e.close();e=None
        offset=live['symbols']['ffta_art_custom_mask']-0x08000000
        check(struct.unpack_from('<I',rom,offset)[0]==7,'Exact three-group mask')
        control=bytearray(rom);control[offset:offset+4]=bytes(4)
        check(control[:offset]==rom[:offset] and control[offset+4:]==rom[offset+4:],'Every code/data/pointer byte identical outside the mask')
        control_path=out/'mask-bypass.gba';control_path.write_bytes(control)
        for case,path in [('candidate',Path(meta['path'])),('mask-bypass',control_path)]:
            for delay in (0,4):
                e=E(path);e.load(out/'focus-ready.state');e.run(6)
                check(active()==0x02000290,'Identical actor addresses after constant-only control selection')
                wrapper=from_emulator(rom,e)[0x290]
                for key in (256,128,128,128):tap(key)
                e.run(delay);canonical=e.memory()[0x80:0x1e70];actions={}
                trace=InstructionTrace(e,{0x080004dc:'compose-return',0x080004fa:'display-return'}, {})
                with trace:
                    for name,key,start,target in [('move',256,48,144),('cancel',1,144,48)]:
                        positions=[];event_start=len(trace.events)
                        for tick in range(128):
                            e.run(1,key if tick<8 else 0);r=e.memory()
                            positions.append(list(struct.unpack_from('<3H',r,wrapper+8)))
                        check(positions[-1]==[target,32,432],case+'/'+name+' exact destination')
                        check(e.memory()[0x80:0x1e70]==canonical,case+'/'+name+' canonical party unchanged')
                        events=trace.events[event_start:]
                        actions[name]=dict(motion=motion(positions,start,target),positions=positions,events=events)
                        if case=='candidate':
                            observe(live,rom,e.memory(),C.string_at(*e.maps[0x05000000]),C.string_at(*e.maps[0x07000000]),check,{0,1,2})
                            e.screenshot(out/f'{case}-{delay}-{name}.png')
                records.append(dict(case=case,delay=delay,actions=actions));e.close();e=None
        for delay in (0,4):
            candidate=next(r for r in records if r['case']=='candidate' and r['delay']==delay)
            bypass=next(r for r in records if r['case']=='mask-bypass' and r['delay']==delay)
            for name in ('move','cancel'):
                a=candidate['actions'][name];b=bypass['actions'][name]
                delta={k:a['motion'][k]-b['motion'][k] for k in ('start','end','elapsed')}
                deltas.append(dict(delay=delay,action=name,extraFrames=delta))
                check(a['motion']['positions']==b['motion']['positions'],'Identical ordered native motion '+str((delay,name)))
                check(all(160<=event['scanline']<228 for event in a['events']),'Palette composition and display stay in VBlank')
        check(all(v<=0 for row in deltas for v in row['extraFrames'].values()),'No extra input/movement frames '+str(deltas))
    except BaseException as error:
        failure=repr(error)
        if e:
            e.save(out/'failed.state')
            if e.frame:e.screenshot(out/'failed.png')
    finally:
        if e:e.close()
        report=dict(status='failed' if failure else 'passed',romSha1=meta['romSha1'],entryReport=str(entry_path),entrySha256=sha(entry_path.read_bytes()),
                    checks=checks,inputs=inputs,records=records,deltas=deltas,failure=failure,scope=__doc__)
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(dict(status=report['status'],checks=len(checks),deltas=deltas,failure=failure,report=str(out/'report.json'))))
    assert failure is None,failure


if __name__=='__main__':main()
