"""Real-core checks for the memory-fixes candidate.

Disposable Giza battle fixture (Viera Mystic Knight profile: the widest job
name, 11 tiles), fixed inputs only:
- Deployment Info on each of the six units renders, keeps the display buffer
  within 0x1E00 and restores the heap on close; the Mystic Knight's buffer use
  equals the ten-tile names' (the native glyph writer does not clip).
- Equip Items: equipping from a list runs the old-layout rebuild entry 7A094
  (traced), which now yields only valid, unique item IDs; heap stays valid.
- Suspend: Save Now writes JST1 into the flash image; a cold resume restores
  the job-state bank and leaves no JST1 marker in live RAM.
"""
import ast, ctypes as C, datetime, hashlib, json, runpy, struct, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from mgba_instruction_trace import InstructionTrace
tree=ast.parse((ROOT/'scripts/probe-ap-copy-heap.py').read_text())
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='heap'],type_ignores=[]),'<native heap walk>','exec'))
current=ROOT/'build/expansion/memory-fixes/current.json'
if '--current' in sys.argv:current=ROOT/sys.argv[sys.argv.index('--current')+1]   # a later stage built on this change
meta=json.loads(Path(json.loads(current.read_text())['manifest']).read_text())
rom_path=Path(meta['path']);rom=rom_path.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
B,START,UP,DN,LT,RT,A,R=1,8,16,32,64,128,256,2048
BUFFER,BANK=0x1e00,0x3f400
out=rom_path.parent/('ui-memory-fixes-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir()
subprocess.run([sys.executable,str(ROOT/'scripts/create-battle-fixture.py'),'--rom',str(rom_path),'--out',str(out/'fixture'),
    '--party-profile',str(ROOT/'scripts/fixtures/mystic-knight-profile.json'),'--confirm-pub-exit','--heap-end','0x0203f000'],check=True,capture_output=True)
FIX=out/'fixture';assert (FIX/'frozen.gba').read_bytes()==rom
checks=[];inputs=[];peaks={}
def check(ok,label):
    assert ok,label
    checks.append(label)
e=None
def walk():
    try:return heap(e.memory())
    except AssertionError:return None
def context():
    return struct.unpack_from('<I',C.string_at(*e.maps[0x03000000]),0x2818)[0]
def buffer_used():
    r=e.memory();c=context()
    if not 0x02000000<=c<0x02040000:return 0
    b=struct.unpack_from('<I',r,c-0x02000000+0x1c)[0]
    if not 0x02000000<=b<0x02040000:return 0
    d=r[b-0x02000000:b-0x02000000+BUFFER];nz=[i for i in range(0,BUFFER,32) if any(d[i:i+32])]
    return nz[-1]+32 if nz else 0
def distinct():
    raw,w,h,pitch,px=e.frame;bpp=4 if px==1 else 2
    return len({b''.join(bytes(raw[(y+j)*pitch+x*bpp:(y+j)*pitch+(x+8)*bpp]) for j in range(8)) for y in range(0,h,8) for x in range(0,w,8)})
def tap(key,wait=60,name=None,scope=None):
    e.run(8,key)
    for _ in range(max(1,wait//10)):
        e.run(10)
        if scope:peaks[scope]=max(peaks.get(scope,0),buffer_used())
    inputs.append([key,wait,name])
    if name:e.screenshot(out/(name+'.png'))
def job_name(unit):return e.memory()[0x80+264*unit+5]

# 1. Deployment Info on every unit, then equip from a list.
e=E(FIX/'frozen.gba')
try:
    e.load(FIX/'deployment-4-units.state');e.run(30)
    before=walk();check(before and before['end']==0x0203f000,'native heap ends at 0x0203F000')
    units={}
    for u in range(6):
        tap(RT,120);tap(R,300,f'info-{u}',scope=f'info-{u}')
        c=context();r=e.memory();unit=struct.unpack_from('<I',r,c-0x02000000+0x1d0c)[0]
        units[u]=unit;check(distinct()>=250 and walk() is not None,f'Info {u} renders with a valid heap')
        tap(B,300)
        after=walk();check(after and after['freePayload']==before['freePayload'],f'closing Info {u} restores the heap')
    myk=[u for u,unit in units.items() if 0x02000080<=unit<0x02001940 and e.memory()[unit-0x02000000+5]==125]
    check(len(myk)==1,'the Mystic Knight Info was opened')
    others=[peaks[f'info-{u}'] for u in units if u not in myk]
    check(peaks[f'info-{myk[0]}']<=max(others) and max(peaks.values())<=BUFFER,f"Mystic Knight name within the display buffer ({peaks})")
    # Equip: Info -> Equip Items -> first slot -> equip the first listed item.
    e.set_memory(0x1941,bytes([99]*460));inputs.append('declared: every item 1..460 owned x99')
    # Cycle to the Human Soldier (third unit after the loop), who can wear the listed helms.
    for _ in range(3):tap(RT,120)
    tap(R,300,'equip-info');tap(A,200,'equip-menu');tap(A,200,'equip-list')
    trace=InstructionTrace(e,{0x0807a094:'7A094',0x0808d0c4:'8D0C4'})
    with trace:tap(A,300,'equipped')
    rebuilt=[x for x in trace.events if x['site']=='7A094']
    check(rebuilt,f'equipping runs the old-layout rebuild entry 7A094 ({len(rebuilt)} calls)')
    r=e.memory();ids=[]
    for event in rebuilt[-1:]:
        destination=event['registers'][1]-0x02000000;n=0
        while n<460 and (i:=struct.unpack_from('<I',r,destination+0x230+20*n+4)[0]):ids.append(i);n+=1
    check(ids and all(1<=i<=460 for i in ids) and len(set(ids))==len(ids),f'rebuilt list: {len(ids)} valid, unique item IDs')
    check(walk() is not None and distinct()>=150,'equip screen renders with a valid heap')
    tap(B,200);tap(B,200);tap(B,300,'deployment-after-equip')
    final=walk();check(final and final['freePayload']==before['freePayload'],'leaving Info after equipping restores the heap')
finally:e.close()

# 2. Suspend save and cold resume.
e=E(FIX/'frozen.gba')
try:
    e.load(FIX/'battle-ready.state');e.run(1)
    live=e.memory();check(live[0x1f04:0x1f08]!=b'JST1','battle state carries no JST1 marker')
    records=bytes(live[BANK:BANK+808]);old=e.memory(0)
    for key in (B,START,UP,A,A):tap(key,180)
    tap(A,300,'saved');saved=e.memory(0)
    check(saved!=old and b'JST1' in saved,'Save Now wrote the suspend image with its JST1 marker')
    check(e.memory()[0x1f04:0x1f08]==live[0x1f04:0x1f08],'saving restored the live marker bytes')
finally:e.close()
e=E(FIX/'frozen.gba')
try:
    e.set_memory(0,saved,0);e.run(3600)
    for key,wait in ((START,600),(A,600),(A,600),(A,600),(A,600),(LT,60),(A,1800)):tap(key,wait)
    observe['wait_for_menu'](e,limit=9000);e.screenshot(out/'resumed.png');resumed=e.memory()
    check(resumed[BANK:BANK+808]==records,'cold resume restored the job-state bank')
    check(resumed[0x1f04:0x1f08]==bytes(4),'cold resume leaves no JST1 marker in live RAM')
finally:e.close()
report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,bufferPeaks=peaks,inputs=inputs,fixture=str(FIX))
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status='passed',romSha1=meta['romSha1'],checks=len(checks),bufferPeaks=peaks,report=str(out/'report.json'))))
