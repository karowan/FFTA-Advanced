"""Real-core check that the approved weapon icons reach the screen.

Disposable Sprohm fixture on the item-icons candidate with every item 1..460
owned once (declared). Fixed inputs scroll every Sell tab of the Sprohm shop
and the party Item List to their ends. After each step VRAM is searched for
each approved icon's exact 4bpp pixels; all 85 weapons must appear on screen
in both lists. Rows showing new weapons are screenshotted for visual review.
The game_pass monitor checks resident code, stack, heap and rendering.
"""
import ctypes as C, datetime, hashlib, json, runpy, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from PIL import Image
from native_art import pack_tiles
from game_pass import Pass
meta=json.loads(Path(json.loads((ROOT/'build/expansion/item-icons/current.json').read_text())['manifest']).read_text())
rom_path=Path(meta['path']);assert hashlib.sha1(rom_path.read_bytes()).hexdigest()==meta['romSha1']
receipt=json.loads((ROOT/'src/art/imagegen/new-item-icons-approved.json').read_text(encoding='utf-8'))
icons={row['id']:pack_tiles(Image.open(ROOT/row['path']),4) for row in receipt['items']}
out=rom_path.parent/('ui-item-icons-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir()
fixture=out/'fixture'
if '--fixture' in sys.argv:fixture=Path(sys.argv[sys.argv.index('--fixture')+1])
else:subprocess.run([sys.executable,str(ROOT/'scripts/create-battle-fixture.py'),'--rom',str(rom_path),'--out',str(fixture),
    '--confirm-pub-exit','--heap-end','0x0203f000'],check=True,capture_output=True)
assert (fixture/'frozen.gba').read_bytes()==rom_path.read_bytes()
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
D,R,A,B,ST=32,128,256,1,8
seen={};shots=[];problems=[]
def scan(e,where):
    vram=C.string_at(*e.maps[0x06000000]);found=[i for i,raw in icons.items() if raw in vram]
    new=[i for i in found if i not in seen.get(where,set())]
    seen.setdefault(where,set()).update(found)
    if new and len(shots)<40:
        name=f'{where}-{min(new)}';e.screenshot(out/(name+'.png'));shots.append(name)
def walk(where,route):
    e=E(fixture/'frozen.gba')
    try:
        e.load(fixture/'accepted-world.state');e.run(30);e.set_memory(0x1941,bytes([1]*460))   # declared: every item owned once
        p=Pass(e,out,where+'-');p.arm()
        for key,wait,scroll in route:
            e.run(8,key);e.run(wait)
            if scroll:
                for _ in range(scroll):e.run(8,D);e.run(16);scan(e,where)
        p.check('end',min_tiles=1);problems.extend(p.problems)
    finally:e.close()
# Sprohm shop > Sell: eight tabs, each scrolled to its end (d-pad Right changes tab).
walk('sell',[(A,240,0),(D,120,0),(A,300,0),(D,120,0),(A,300,0)]+[(R if t else 0,150,360) for t in range(8)])
# World menu > Party > Start: the Item List, all tabs.
walk('item-list',[(ST,150,0),(A,300,0),(ST,300,0)]+[(R if t else 0,150,360) for t in range(8)])
missing={where:sorted(set(icons)-ids) for where,ids in seen.items()}
for where,ids in missing.items():
    if ids:problems.append((where,f'weapon icons never on screen: {ids}'))
report=dict(status='passed' if not problems else 'failed',romSha1=meta['romSha1'],seen={k:len(v) for k,v in seen.items()},
            missing=missing,problems=problems,screenshots=shots,fixture=str(fixture))
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status=report['status'],romSha1=meta['romSha1'],seen=report['seen'],problems=problems[:10],report=str(out/'report.json'))))
sys.exit(0 if not problems else 1)
