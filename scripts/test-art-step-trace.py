"""Prove host instruction observation matches normal frames before using its trace."""
import ctypes as C
import datetime,hashlib,json,runpy,struct
from pathlib import Path
from native_art import ROOT,sha
from mgba_instruction_trace import InstructionTrace,DLL_SHA256

META=ROOT/'build/art/connected/4a7d55ce09cd4a40965a0bb97de2701d276789c5/manifest.json'
SOURCE=ROOT/'build/art/live-palette/battle/20260918T183919.610099Z'
out=ROOT/'build/art/instruction-trace'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];e=None;trace=None
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    meta=json.loads(META.read_text(encoding='utf-8'));rom=Path(meta['path']).read_bytes()
    check(hashlib.sha1(rom).hexdigest()==meta['romSha1']=='4a7d55ce09cd4a40965a0bb97de2701d276789c5','Exact current ready-state ROM')
    seed=(SOURCE/'candidate-ready.state').read_bytes()
    check(sha((SOURCE/'candidate-ready.ram').read_bytes())=='0a0de57cd3ee8b617475b572b856b2181628eed8ed0e120af93451394f642018','Pinned ready RAM')
    check(sha((SOURCE/'candidate-ready.iwram').read_bytes())=='6ab0ad9dd121fc844eb9aaa15f184ee83ba4f1ebdb8cd9b5109ad433f686ada4','Pinned ready IWRAM')
    E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
    e=E(Path(meta['path']));e.load(SOURCE/'candidate-ready.state')
    check(e.memory()==(SOURCE/'candidate-ready.ram').read_bytes() and C.string_at(*e.maps[0x03000000])==(SOURCE/'candidate-ready.iwram').read_bytes(),'Loaded state matches authenticated raw memory')
    sites={0x08000460:'draw',0x080004b0:'vblank',0x0800221c:'input',0x08000498:'input-return',
           0x080069f4:'dispatch',0x080012bc:'compose',0x080004dc:'compose-return',0x08000788:'display-end'}
    trace=InstructionTrace(e,sites)
    cpu=C.create_string_buffer(e.core.retro_serialize_size());assert e.core.retro_serialize(cpu,len(cpu))
    check(list(trace.registers[:17])==list(struct.unpack_from('<17I',cpu,0x20)),'Native ARM register ABI matches existing serializer')
    keys=[0]*4+[256]*8+[0]*4
    baseline=[]
    for key in keys:
        e.run(1,key);baseline.append((trace.state(),e.frame))
    e.load(SOURCE/'candidate-ready.state')
    with trace:
        for index,key in enumerate(keys):
            before=trace.cycles();counter=trace.frame_counter(trace.core)
            e.run(1,key)
            trace.frames.append(dict(frame=counter,startCycle=before,endCycle=trace.cycles()))
            actual=trace.state();expected=baseline[index][0]
            if actual!=expected:
                (out/'normal.state').write_bytes(expected);(out/'stepped.state').write_bytes(actual)
            check(actual==expected,'Entire native serialized state identical after frame '+str(index))
            check(e.frame==baseline[index][1],'Complete rendered framebuffer identical after frame '+str(index))
    check(trace.slot.value==trace.original,'Host instruction-table reference restored')
    check({x['site'] for x in trace.events}==set(sites.values()),'All declared native event sites observed')
    check((SOURCE/'candidate-ready.state').read_bytes()==seed,'Source state unchanged')
    report=dict(status='passed',checks=checks,romSha1=meta['romSha1'],coreSha256=DLL_SHA256,source=str(SOURCE),stateSha256=sha(seed),inputs=keys,
                hostRvas=trace.host_rvas,events=trace.events,frames=trace.frames,
                scope='Host-only Thumb instruction-dispatch observation of sixteen exact-ROM frames with a fixed A press; every entire native serialized state and framebuffer matches ordinary retro_run. Native event/run loop unchanged. No emulated instruction/memory patches. Establishes observation method for this scene, not input-latency acceptance, all scenes or final art.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),events=len(trace.events),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,events=trace.events if trace else [],frames=trace.frames if trace else []),indent=2)+'\n',encoding='utf-8')
    print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
