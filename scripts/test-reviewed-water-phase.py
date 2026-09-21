"""Read-only palette phase diagnosis from an exact failed natural-water state."""
import argparse
import ctypes as C
import datetime
import hashlib
import json
import runpy
import struct
from pathlib import Path
from native_art import ROOT,sha
from mgba_instruction_trace import InstructionTrace

parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path,required=True);args=parser.parse_args()
prior=json.loads(args.report.read_text());folder=args.report.parent;path=folder/'natural-water.gba';rom=path.read_bytes()
assert hashlib.sha1(rom).hexdigest()==prior['fixture']['fixtureRomSha1']
meta=json.loads((ROOT/'build/art/reviewed-integration/action-candidate.json').read_text());assert meta['romSha1']==prior['romSha1']
live=meta['components']['livePalette'];base=live['ramReservation'][0];length=live['ramReservation'][1]-base
slots=live['historySlots'];colors=struct.unpack_from('<160H',rom,live['symbols']['ffta_art_custom_colors']-0x08000000)
out=ROOT/'build/art/reviewed-integration/water-phase'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
ranges={'oam':(0x07000000,1024),'palette':(0x05000000,1024)}
for i in range(0,length,4096):ranges['live'+str(i)]=(base+i,min(4096,length-i))
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];e=None;events=[];states=[];frames=[];observations=[]
def inspect(label,raw,pal,oam):
    keys=raw[live['variantOffset']:live['variantOffset']+slots];scales=raw[live['variantOffset']+slots:live['variantOffset']+2*slots]
    tags=raw[live['tagOffset']:live['tagOffset']+128];visible=raw[live['visibleColorsOffset']:live['visibleColorsOffset']+slots*32]
    objects=[]
    for index,slot in enumerate(tags):
        if slot>=slots:continue
        a,b,c=struct.unpack_from('<3H',oam,index*8)
        if a&0x300==0x200:continue
        owner=keys[slot]>>4;scale=scales[slot];bank=c>>12
        assert owner<10
        expected=struct.pack('<16H',*[sum((((v>>s)&31)*scale//32)<<s for s in (0,5,10)) for v in colors[owner*16:owner*16+16]])
        actual=pal[512+bank*32:544+bank*32];shown=visible[slot*32:slot*32+32]
        objects.append(dict(index=index,slot=slot,owner=owner,scale=scale,bank=bank,expected=expected.hex(),visible=shown.hex(),hardware=actual.hex(),
                            visibleExact=shown==expected,hardwareExact=actual==expected))
    return dict(label=label,objects=objects)
try:
    for observed in (False,True):
        e=E(path);e.load(folder/'failed.state')
        if observed:
            observations.append(inspect('failed-sample',e.memory()[base-0x02000000:base-0x02000000+length],C.string_at(*e.maps[0x05000000]),C.string_at(*e.maps[0x07000000])))
            sites={0x080004dc:'compose-return',0x080004fa:'display-return'}
            with InstructionTrace(e,sites,{p:ranges for p in sites}) as trace:e.run(4)
            events=trace.events
            for event in events:
                raw=b''.join(bytes.fromhex(event['memory']['live'+str(i)]) for i in range(0,length,4096))
                observation=inspect(event['site'],raw,bytes.fromhex(event['memory']['palette']),bytes.fromhex(event['memory']['oam']))
                observation.update(frame=event['videoFrame'],scanline=event['scanline']);observations.append(observation)
        else:e.run(4)
        state=out/f'{observed}.state';e.save(state);states.append(sha(state.read_bytes()));frames.append(sha(e.frame[0]));e.close();e=None
    assert len(set(states))==len(set(frames))==1,'Observer changes replay'
    assert len(events)>=6
    report=dict(status='passed',scope=__doc__,sourceReportSha256=sha(args.report.read_bytes()),sourceStateSha256=sha((folder/'failed.state').read_bytes()),
                romSha1=prior['romSha1'],fixtureRomSha1=prior['fixture']['fixtureRomSha1'],observations=observations,states=states,frames=frames,events=events)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(report=str(out/'report.json'),observations=[dict(label=o['label'],scanline=o.get('scanline'),objects=[{k:v for k,v in a.items() if k not in ('expected','visible','hardware')} for a in o['objects']]) for o in observations])))
finally:
    if e:e.close()
