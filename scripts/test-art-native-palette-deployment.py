"""Exact608-frame paired deployment cadence on freshly allocated native palettes.

Replays the same entry-6 checkpoint and eight-frame confirmation input as the
retained deployment diagnosis. Whole observed state/frame must match ordinary
execution. Raw original rotation, foreground and input cadence is not shifted.
"""
import ctypes as C,datetime,hashlib,json,runpy,struct
from pathlib import Path
from native_art import ROOT,sha
from mgba_instruction_trace import InstructionTrace,DLL_SHA256

idx=json.loads((ROOT/'build/art/native-palette-entry/latest.json').read_text());entry_path=Path(idx['report'])
assert sha(entry_path.read_bytes())==idx['sha256'];entry=json.loads(entry_path.read_text());assert entry['status']=='passed'
source=entry_path.parent;out=ROOT/'build/art/native-palette-deployment'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
SITES={0x080ba66c:'deployment-cycle-start',0x080ba69a:'deployment-cycle-end',
       0x08000460:'draw',0x0800221c:'input',0x0800042e:'foreground-return',
       0x080004c8:'vblank-flag-check',0x080012bc:'compose',0x080004dc:'compose-return',0x080004fa:'vblank-display-return'}
SNAPS={p:dict(shadow=(0x03003860,1024),palette=(0x05000000,1024)) for p in SITES if p in (0x080004c8,0x080012bc,0x080004dc,0x080ba66c,0x080ba69a)}
pins={str(entry_path):sha(entry_path.read_bytes())};records={};checks=[];e=None;case='setup'
for case in ('control','candidate'):
    for suffix in ('state','ram','iwram'):
        p=source/(case+'-entry-6.'+suffix);pins[str(p)]=sha(p.read_bytes())

def check(ok,label):
    assert ok,case+'/'+label
    checks.append(case+'/'+label)

def frame_hash(frame):
    raw,w,h,pitch,pixel=frame;return sha(struct.pack('<4I',w,h,pitch,pixel)+raw)

def prepare(path,case):
    global e
    e=E(path);e.load(source/(case+'-entry-6.state'))
    check(e.memory()==(source/(case+'-entry-6.ram')).read_bytes() and C.string_at(*e.maps[0x03000000])==(source/(case+'-entry-6.iwram')).read_bytes(),'Exact own-ROM deployment state')

try:
    original=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    for case in ('control','candidate'):
        branch=entry['records'][case];path=Path(branch['path']);rom=path.read_bytes()
        check(hashlib.sha1(rom).hexdigest()==branch['romSha1'],'Authenticated branch ROM')
        check(rom[0xba66c:0xba69a]==original[0xba66c:0xba69a],'Exact native deployment cycle instructions')
        prepare(path,case);trace=InstructionTrace(e,SITES,SNAPS);initial=trace.state();baseline=[]
        for tick in range(608):
            e.run(1,256 if tick<8 else 0);baseline.append((sha(trace.state()),frame_hash(e.frame)))
        e.close();e=None;prepare(path,case);trace=InstructionTrace(e,SITES,SNAPS)
        check(trace.state()==initial,'Fresh observed and ordinary initial state identical')
        frames=[];first_frame=trace.frame_counter(trace.core)
        with trace:
            for tick in range(608):
                e.run(1,256 if tick<8 else 0)
                check((sha(trace.state()),frame_hash(e.frame))==baseline[tick],'Whole observed state/frame equals ordinary execution '+str(tick))
                iw=C.string_at(*e.maps[0x03000000])
                frames.append(dict(tick=tick,shadow=iw[0x3860:0x3c60].hex(),palette=C.string_at(*e.maps[0x05000000]).hex(),units=sha(e.memory()[0x80:0x1e70])))
        check(trace.slot.value==trace.original,'Original host dispatch restored')
        before=[x for x in trace.events if x['site']=='compose'];after=[x for x in trace.events if x['site']=='compose-return']
        decision=[x for x in trace.events if x['site']=='vblank-flag-check'];display=[x for x in trace.events if x['site']=='vblank-display-return']
        starts=[x for x in trace.events if x['site']=='deployment-cycle-start'];ends=[x for x in trace.events if x['site']=='deployment-cycle-end']
        check(len(before)==len(after)==len(decision)==len(display)==608,'Every deployment frame includes original DMA/composition/display')
        check(len(starts)==len(ends)>0,'Actual deployment cycle callback exercised')
        for tick,(b,a,d,v) in enumerate(zip(before,after,decision,display)):
            check(b['videoFrame']==a['videoFrame']==d['videoFrame']==v['videoFrame'],'Same deployment frame boundaries '+str(tick))
            check(b['memory']==a['memory'],'Native composition preserves all hardware/shadow colors '+str(tick))
            expected=d['memory']['palette'] if d['frameFlag'] else b['memory']['shadow']
            check(b['memory']['palette']==expected,'Actual original complete BG/OBJ DMA decision '+str(tick))
            check(160<=b['scanline']<=a['scanline']<=v['scanline']<228,'Deployment composition/display inside VBlank '+str(tick))
        cycle=[]
        for b,a in zip(starts,ends):
            check(b['videoFrame']==a['videoFrame'] and b['cycle']<a['cycle'],'Paired native rotation callback')
            cycle.append(dict(frame=b['videoFrame']-first_frame,changed=b['memory']['shadow']!=a['memory']['shadow']))
        e.screenshot(out/(case+'-final.png'));e.close();e=None
        records[case]=dict(romSha1=branch['romSha1'],firstVideoFrame=first_frame,frames=frames,events=trace.events,cycle=cycle,
            compositionCycles=[(a['cycle']-b['cycle'])&0xffffffff for b,a in zip(before,after)])
        print(json.dumps(dict(case=case,callbacks=len(cycle),shifts=sum(v['changed'] for v in cycle))),flush=True)
    for tick,(a,b) in enumerate(zip(records['candidate']['frames'],records['control']['frames'])):
        check(a==b,'Paired full raw shadow/hardware/unit state identical '+str(tick))
    check(records['candidate']['cycle']==records['control']['cycle'],'Exact callback and color-shift frame cadence')
    for site in ('draw','input','foreground-return'):
        timeline=[]
        for case in ('candidate','control'):
            r=records[case];timeline.append([(x['videoFrame']-r['firstVideoFrame'],x['nativeFrame'],x['inputs']) for x in r['events'] if x['site']==site])
        check(timeline[0]==timeline[1],'Exact raw '+site+' cadence without phase alignment')
    check(all(sha(Path(p).read_bytes())==s for p,s in pins.items()),'Retained input files unchanged')
    report=dict(status='passed',romSha1=entry['romSha1'],checks=checks,pins=pins,entryReport=str(entry_path),records=records,coreSha256=DLL_SHA256,inputs=[8,256,600],scope=__doc__)
    dest=out/'report.json';dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),report=str(dest))))
except Exception as error:
    if e:
        e.save(out/'failed.state')
        if e.frame:e.screenshot(out/'failed.png')
        for ext,address in [('ram',0x02000000),('iwram',0x03000000),('palette',0x05000000),('oam',0x07000000)]:
            (out/('failed.'+ext)).write_bytes(C.string_at(*e.maps[address]))
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=entry['romSha1'],error=str(error),checks=checks,pins=pins,records=records),indent=2)+'\n',encoding='utf-8')
    print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
