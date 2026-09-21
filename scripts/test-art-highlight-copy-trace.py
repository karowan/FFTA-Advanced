"""Observe palette-copy callers in the retained failing Thundaga preview.

No gameplay patches or new fixture. Every observed frame must exactly match
ordinary emulation in a fresh core before using the caller evidence.
"""
import ctypes as C, datetime, hashlib, json, runpy
from pathlib import Path
from native_art import ROOT, sha
from mgba_instruction_trace import InstructionTrace

meta=json.loads((ROOT/'build/art/connected/4a7d55ce09cd4a40965a0bb97de2701d276789c5/manifest.json').read_text())
rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']=='4a7d55ce09cd4a40965a0bb97de2701d276789c5'
source=ROOT/'build/art/connected/casting/20260918T203709.455123Z'
prior=json.loads((source/'failed.json').read_text())
assert prior['romSha1']==meta['romSha1'] and prior['error']=='371-active/No palette allocation/effect refusal 0'
seed=source/'371-active-ready.state'
inputs=[(8,key,180) for key in (256,128,128,128,256,256,32,256,256,128,256,256)]
schedule=[button for press,key,wait in inputs for button in [key]*press+[0]*wait]+[0]*96
sites={meta['components']['livePalette']['symbols']['ffta_art_live_palette_copy']&~1:'palette-copy',
       0x08148104:'native-scale',0x081477dc:'native-gray',0x08148384:'native-exposure',
       0x08147830:'native-blend'}
snapshots={pc:{'shadow':(0x03003860,1024)} for pc in sites}
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
out=ROOT/'build/art/connected/highlight-trace'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];baseline=[];e=None;trace=None
try:
    e=E(Path(meta['path']));e.load(seed);trace=InstructionTrace(e,sites,snapshots)
    initial=trace.state()
    for key in schedule:
        e.run(1,key);baseline.append((sha(trace.state()),sha(e.frame[0])))
    e.close();e=None
    e=E(Path(meta['path']));e.load(seed);trace=InstructionTrace(e,sites,snapshots)
    assert trace.state()==initial;checks.append('Fresh-core initial native state exact')
    with trace:
        for frame,key in enumerate(schedule):
            e.run(1,key)
            assert (sha(trace.state()),sha(e.frame[0]))==baseline[frame],frame
            checks.append('Entire native state and framebuffer exact '+str(frame))
    assert trace.events;checks.append('Native palette call evidence present')
    assert trace.slot.value==trace.original;checks.append('Original host instruction table restored')
    result=dict(status='passed',romSha1=meta['romSha1'],checks=checks,events=trace.events,inputs=inputs,
        source=dict(path=str(seed),sha256=sha(seed.read_bytes()),failedReportSha256=sha((source/'failed.json').read_bytes())),
        scope='Read-only host observation of fixed native Move/Thundaga selection/targeting from the retained exact-ROM ready point, byte-exact ordinary execution equivalence. Caller/argument evidence only, not a graphics fix or acceptance.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),events=len(trace.events),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,events=trace.events if trace else []),indent=2)+'\n',encoding='utf-8');print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
