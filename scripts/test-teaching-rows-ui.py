"""Real-core equipment help checks: shop R Info, Item List and Equip Items.

Fixed inputs from build/test-lab/early-town.sav view Gloom Sword, Sanguine
Edge, Storm Axe and Raider Axe. Checks row counts, per-row AP, the type icon,
merged-row badge cycling and the panel bottom after a two-lesson weapon.
--parent runs the same inputs on the parent release and records failures.
"""
import datetime, hashlib, json, runpy, struct, sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
# --current selects a later bounded stage that retains the teaching-row patch.
CURRENT=sys.argv[sys.argv.index('--current')+1] if '--current' in sys.argv else 'build/expansion/teaching-rows/current.json'
PARENT='--parent' in sys.argv
meta=json.loads(Path(json.loads((ROOT/CURRENT).read_text())['manifest']).read_text())
rom=Path(meta['path']);digest=hashlib.sha1(rom.read_bytes()).hexdigest();assert digest==meta['romSha1']
if PARENT:
    rom=Path(json.loads(Path(meta['teachingRows']['parent']).read_text())['path'])
    assert hashlib.sha1(rom.read_bytes()).hexdigest()==meta['teachingRows']['baseSha1']
seed=(ROOT/'build/test-lab/early-town.sav').read_bytes()
assert hashlib.sha1(seed).hexdigest()=='b0199e7490f7c22f84512825a4a1bde08d3b3eec'
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
out=Path(meta['path']).parent/(('parent-' if PARENT else '')+'ui-rows-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
out.mkdir(parents=True)
START,A,B,DOWN,UP,RIGHT,R=8,256,1,32,16,128,2048
ITEMS=(384,385,392,393)
# Gloom Sword, Sanguine Edge, Storm Axe, Raider Axe: AP per row.
EXPECTED={384:[100],385:[150,300],392:[100],393:[100,150]}
inputs=[];checks=[];failures=[];shots={}

def check(ok,label):
    (checks if ok else failures).append(label)
    if not ok and not PARENT:raise AssertionError(label)

def session(screen):
    e=E(rom);e.set_memory(0,seed,0);e.run(3600)
    def tap(key,wait=60,name=None):
        e.run(8,key);e.run(wait);inputs.append([screen,key,wait,name])
        if name:
            path=out/f'{screen}-{name}.png';e.screenshot(path)
            shots[f'{screen}-{name}']=Image.open(path).resize((240,160),Image.NEAREST).convert('RGB')
    for key,wait in ((START,180),(A,60),(A,60),(A,180)):tap(key,wait)
    return e,tap

def ap_rows(im):
    """Rows of the yellow AP icon inside the right-hand help panel."""
    ys=[y for y in range(160) if sum(1 for x in range(165,194) if (lambda p:p[0]>200 and p[1]>150 and p[2]<80)(im.getpixel((x,y))))>=5]
    rows=[]
    for y in ys:
        if not rows or y>rows[-1][-1]+1:rows.append([y])
        else:rows[-1].append(y)
    found=[]
    for group in rows:
        top=group[0]-3
        xs=[x for x in range(165,194) if any((lambda p:p[0]>200 and p[1]>150 and p[2]<80)(im.getpixel((x,y))) for y in group)]
        found.append((top,min(xs),max(xs)))
    return found
def crop(im,box):return im.crop(box).tobytes()

def item_views(screen,names):
    views={}
    for item,name in zip(ITEMS,names):
        im=shots[f'{screen}-{name}'];rows=ap_rows(im)
        check(len(rows)==len(EXPECTED[item]),f'{screen} item {item} shows {len(EXPECTED[item])} lesson rows')
        views[item]=dict(image=im,rows=rows,ap=[crop(im,(right+1,top,right+27,top+10)) for top,_,right in rows])
    apv={}
    for item,view in views.items():
        for value,sig in zip(EXPECTED[item],view['ap']):apv.setdefault(value,set()).add(sig)
    check(all(len(s)==1 for s in apv.values()),f'{screen} equal AP values render identically')
    check(len({next(iter(s)) for s in apv.values()})==len(apv),f'{screen} distinct AP values render distinctly')
    icons={crop(v["image"],(194,31,224,47)) for v in views.values()}
    check(len(icons)==1,f'{screen} two-lesson weapons keep the first lesson Action icon')
    bottom=lambda item:crop(views[item]["image"],(136,144,224,152))
    check(bottom(392)==bottom(384) and bottom(393)==bottom(384),f'{screen} panel bottom clean after a two-lesson weapon')
    return views

def cycling(screen,prefix,frames,rows):
    top,left,_=rows[0]
    return len({crop(shots[f'{screen}-{prefix}{i}'],(left-34,top-2,left-2,top+12)) for i in range(frames)})

report={}
# Shop: the Sprohm opening stock lists all four weapons consecutively.
e,tap=session('shop')
try:
    tap(A,240);tap(DOWN);tap(A,180);tap(A,120);tap(RIGHT,100);tap(RIGHT,100)
    ram=e.memory();ctx=struct.unpack_from('<I',ram,0xf428)[0]-0x02000000
    count=struct.unpack_from('<H',ram,ctx+0xa338)[0]
    ids=[struct.unpack_from('<H',ram,ctx+0x9c08+i*4)[0] for i in range(count)]
    start=ids.index(384);check(ids[start:start+4]==list(ITEMS),'shop lists the four weapons in order')
    for _ in range(start):tap(DOWN,20)
    tap(R,120,'gloom')
    for i in range(6):tap(0,30,f'gloom-frame{i}')
    tap(DOWN,90,'sanguine');tap(DOWN,90,'storm');tap(DOWN,90,'raider')
finally:e.close()
views=item_views('shop',['gloom','sanguine','storm','raider'])
check(cycling('shop','gloom-frame',6,views[384]['rows'])>=2,'shop merged Dark Knight row cycles Human and Bangaa badges')
# Item List and Equip Items: add the weapons to the bag; they follow the five
# starting weapons in item order.
for screen in ('itemlist','equip'):
    e,tap=session(screen)
    try:
        for item in ITEMS:e.set_memory(0x1940+item,b'\x01')
        if screen=='itemlist':
            tap(START,120);tap(A,120);tap(START,180);tap(RIGHT,90)
        else:
            e.set_memory(0x80+0x2e,b'\x00\x00')
            tap(START,120)
            for _ in range(4):tap(A,120)
            tap(RIGHT,120)
        tap(R,120)
        for _ in range(5):tap(DOWN,60)
        tap(0,60,'gloom')
        for i in range(6):tap(0,30,f'gloom-frame{i}')
        tap(DOWN,90,'sanguine');tap(DOWN,90,'storm');tap(DOWN,90,'raider')
    finally:e.close()
    views=item_views(screen,['gloom','sanguine','storm','raider'])
    check(cycling(screen,'gloom-frame',6,views[384]['rows'])>=2,f'{screen} merged Dark Knight row cycles Human and Bangaa badges')
status='passed' if not failures else 'failed'
result=dict(status=status,romSha1=hashlib.sha1(rom.read_bytes()).hexdigest(),candidateSha1=digest,parentControl=PARENT,
    save='build/test-lab/early-town.sav',saveSha1='b0199e7490f7c22f84512825a4a1bde08d3b3eec',inputs=inputs,
    checks=checks,failures=failures,screenshots=sorted(str(p.name) for p in out.glob('*.png')))
(out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(status=status,romSha1=result['romSha1'],checks=len(checks),failures=failures,report=str(out/'report.json'))))
if failures and not PARENT:sys.exit(1)
