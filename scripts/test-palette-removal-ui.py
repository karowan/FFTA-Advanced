"""Real-core checks after retiring the art palette engine.

Disposable Giza battle fixture on the palette-removal candidate (enchant Sniper
profile), fixed inputs only:
- Pre-battle deployment, R on a unit: the native unit Info screen allocates its
  full context and display buffer (the art build could not), renders (at least
  250 distinct 8x8 screen tiles; the broken screen had 103), and keeps the
  native heap valid with room to spare.
- Every clan item set to 99: each Equip Items slot list and each Pick Abilities
  list opens and scrolls; the context's AP/status/job-copy tail
  (+0x5AC0..+0x7280) never changes during item lists (ability lists refresh
  it legitimately) and the display buffer stays within 0x1E00.
- B returns to deployment with the heap exactly as before; Start, Yes and the
  intro begin the battle and reach a native turn menu.
- In battle, Status opens both panels, inspection and help, stays within its
  buffer and heap, and closes with the heap restored.
- The old reservation 0x0203C000..0x0203EFFF lies inside the heap.
"""
import ast, ctypes as C, datetime, hashlib, json, runpy, struct, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from native_battle_wrappers import fixed_giza_formation
tree=ast.parse((ROOT/'scripts/probe-ap-copy-heap.py').read_text())
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='heap'],type_ignores=[]),'<native heap walk>','exec'))
current=ROOT/'build/expansion/palette-removal/current.json'
if '--current' in sys.argv:current=ROOT/sys.argv[sys.argv.index('--current')+1]   # a later stage built on this change
meta=json.loads(Path(json.loads(current.read_text())['manifest']).read_text())
rom_path=Path(meta['path']);rom=rom_path.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
B,SEL,START,DN,RT,A,R=1,4,8,32,128,256,2048
BUFFER,TAIL=0x1e00,(0x5ac0,0x7280)
out=rom_path.parent/('ui-removal-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir()
subprocess.run([sys.executable,str(ROOT/'scripts/create-battle-fixture.py'),'--rom',str(rom_path),'--out',str(out/'fixture'),
    '--party-profile',str(ROOT/'scripts/fixtures/enchant-sniper-profile.json'),'--confirm-pub-exit','--heap-end','0x0203f000'],check=True,capture_output=True)
FIX=out/'fixture';assert (FIX/'frozen.gba').read_bytes()==rom
checks=[];inputs=[];peaks={}
def check(ok,label):
    assert ok,label
    checks.append(label)
e=E(FIX/'frozen.gba')
def walk():
    try:return heap(e.memory())
    except AssertionError:return None
def context():
    iw=C.string_at(*e.maps[0x03000000]);return struct.unpack_from('<I',iw,0x2818)[0]
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
try:
    # Deployment unit Info.
    e.load(FIX/'deployment-4-units.state');e.run(30)
    e.set_memory(0x1941,bytes([99]*460));inputs.append('declared: every item 1..460 owned x99')
    before=walk();check(before and before['end']==0x0203f000,'native heap ends at 0x0203F000 (old reservation is heap)')
    tap(R,300,'info',scope='info')
    h=walk();c=context();r=e.memory()
    b=struct.unpack_from('<I',r,c-0x02000000+0x1c)[0]
    check(h is not None and 0x02000000<b<0x0203f000,'Info context and display buffer allocated in a valid heap')
    check(struct.unpack_from('<I',r,c-0x02000000+0x2d50)[0]==c+0x7280,'Info list uses the full context tail')
    check(h['largestFree']>=512,f"Info leaves heap margin ({h['largestFree']} bytes)")
    check(distinct()>=250,f'Info screen renders ({distinct()} distinct tiles)')
    tail=bytes(r[c-0x02000000+TAIL[0]:c-0x02000000+TAIL[1]])
    def tail_same(label):
        r=e.memory();check(bytes(r[c-0x02000000+TAIL[0]:c-0x02000000+TAIL[1]])==tail and walk() is not None,label)
    tap(A,200,'equip',scope='info')
    for slot in range(5):
        tap(A,200,f'equip-slot{slot}',scope='info')
        for _ in range(40):tap(DN,20,scope='info')
        tail_same(f'Equip slot {slot} list keeps the context tail and heap')
        tap(B,120);tap(DN,60)
    tap(B,150);tap(DN,60);tap(A,250,'abilities',scope='info')
    for kind in range(3):
        tap(A,200,f'abilities-{kind}',scope='info')
        for _ in range(20):tap(DN,20,scope='info')
        # Ability lists legitimately refresh the AP/job-copy tail.
        check(walk() is not None and distinct()>=150,f'Pick Abilities list {kind} renders with a valid heap (lists may be empty)')
        tap(B,120);tap(DN,60)
    tap(B,150);tap(B,300,'deployment-again')
    after=walk()
    check(after and after['freePayload']==before['freePayload'] and after['largestFree']==before['largestFree'],'closing Info restores the heap')
    check(distinct()>=250,'deployment screen renders after Info')
    check(peaks['info']<=BUFFER,f"Info display buffer peak {peaks['info']} within {BUFFER}")
    # Start the battle from deployment.
    tap(START,300,'to-battle');tap(A,600,'battle-intro');tap(A,600)   # Begin battle? Yes; intro
    for _ in range(0,9000,30):
        if observe['menu_visible'](e):break
        e.run(30)
    check(observe['menu_visible'](e),'battle starts and reaches a native turn menu')
    # In-battle Status.
    e.load(FIX/'battle-ready.state');e.run(1);observe['wait_for_menu'](e);fixed_giza_formation(rom,e)
    ready=walk()
    for key in (DN,DN,DN):tap(key,60)
    tap(A,300,'status',scope='status');check(walk() is not None and distinct()>=250,'battle Status renders with a valid heap')
    for i in range(3):tap(RT,120,f'status-panel{i}',scope='status')
    tap(SEL,120,'status-inspect',scope='status')
    for _ in range(6):tap(DN,40,scope='status')
    tap(A,150,'status-help',scope='status');tap(B,90);tap(B,90);tap(B,200,'status-closed')
    closed=walk()
    check(closed and closed['freePayload']==ready['freePayload'],'closing Status restores the heap')
    check(peaks['status']<=BUFFER,f"Status display buffer peak {peaks['status']} within {BUFFER}")
finally:e.close()
report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,bufferPeaks=peaks,inputs=inputs,fixture=str(FIX))
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status='passed',romSha1=meta['romSha1'],checks=len(checks),bufferPeaks=peaks,report=str(out/'report.json'))))
