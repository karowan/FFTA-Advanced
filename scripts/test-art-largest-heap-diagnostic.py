"""Replay the retained fourteen-actor confirmation and locate invalid heap samples.

Read-only sampling of heap walks and native CPU position. No ROM or emulated
state changes and no interactive inputs. Reproducing a transient or persistent
invalid walk does not accept encounter capacity or excuse memory corruption.
"""
import ast,ctypes as C,datetime,hashlib,json,runpy,struct
from pathlib import Path
from native_art import ROOT,sha
from mgba_instruction_trace import InstructionTrace
source=ROOT/'build/art/connected/larger-encounter/20260919T081942.583224Z'
rom_path=source/'native-formation23.gba';rom=rom_path.read_bytes()
meta=json.loads((ROOT/'build/art/connected/a28b624bb13c8f2f2597a4d4bd3999b17c234b99/manifest.json').read_text());candidate=Path(meta['path']).read_bytes()
assert hashlib.sha1(candidate).hexdigest()==meta['romSha1']=='a28b624bb13c8f2f2597a4d4bd3999b17c234b99'
p=0x54cd54+32*40;q=0x54cd54+23*40
assert rom[:p]==candidate[:p] and rom[p:p+40]==candidate[q:q+40] and rom[p+40:]==candidate[p+40:]
seed=source/'to-battle-start.state';seedbytes=seed.read_bytes()
ram0=(source/'to-battle-start.ram').read_bytes();iw0=(source/'to-battle-start.iwram').read_bytes()
out=ROOT/'build/art/largest-heap-diagnostic'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
tree=ast.parse((ROOT/'scripts/probe-ap-copy-heap.py').read_text())
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='heap'],type_ignores=[]),'<native heap walk>','exec'))
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];menus=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
checks=[];samples=[];e=None;first_bad=None;recoveries=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
def capture(label):
    e.save(out/(label+'.state'));e.screenshot(out/(label+'.png'))
    for ext,address in [('ram',0x02000000),('iwram',0x03000000),('vram',0x06000000),('palette',0x05000000),('oam',0x07000000)]:
        (out/(label+'.'+ext)).write_bytes(C.string_at(*e.maps[address]))
try:
    e=E(rom_path);e.load(seed)
    check(e.memory()==ram0 and C.string_at(*e.maps[0x03000000])==iw0,'Exact retained confirmation state')
    # The pinned core adapter exposes registers read-only; its hook table is
    # never installed in this diagnostic. Ordinary emulation runs unchanged.
    cpu=InstructionTrace(e,{0x08007138:'allocate'})
    for frame in range(608):
        e.run(1,256 if frame<8 else 0);r=e.memory();error=None
        try:h=heap(r);h={k:v for k,v in h.items() if k!='allocationBlocks'}
        except AssertionError as failure:h=None;error=str(failure)
        row=dict(frame=frame+1,heap=h,error=error,pc=int(cpu.registers[15]),lr=int(cpu.registers[14]),sp=int(cpu.registers[13]),cpsr=int(cpu.registers[16]))
        samples.append(row)
        if error and first_bad is None:first_bad=frame+1;capture('first-invalid')
        if not error and len(samples)>1 and samples[-2]['error']:
            recoveries.append(frame+1);capture('recovered-'+str(frame+1))
    capture('final')
    check(first_bad is not None,'Original invalid heap walk reproduced without emulator hooks or state edits')
    check(any('0x161d8' in (s['error'] or '') for s in samples),'Retained failing header reached')
    check(seed.read_bytes()==seedbytes,'Source state preserved')
    report=dict(status='passed',romSha1=hashlib.sha1(rom).hexdigest(),candidateSha1=meta['romSha1'],checks=checks,samples=samples,
        firstInvalidFrame=first_bad,recoveryFrames=recoveries,invalidFrames=sum(bool(s['error']) for s in samples),
        finalMenuVisible=menus['menu_visible'](e),finalHeap=samples[-1]['heap'],
        source=dict(directory=str(source),stateSha256=sha(seedbytes),ramSha256=sha(ram0),iwramSha256=sha(iw0)),scope=__doc__)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),firstInvalidFrame=first_bad,recoveryFrames=recoveries,invalidFrames=report['invalidFrames'],finalMenuVisible=report['finalMenuVisible'],report=str(out/'report.json'))))
except Exception as error:
    if e and e.frame:capture('failed')
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,samples=samples),indent=2)+'\n',encoding='utf-8');print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
