"""All ten classes allocated together through native six-versus-six entry.

Disposable Giza event shell uses the complete original formation324 map record.
Its six generic enemies retain race, level, positions and side; only job,
secondary skillset and legal weapon loadout are declared presentation inputs.
Four already-recruited same-race party members supply the complementary jobs.
This is demanding graphics/heap/Status coverage, not mission eligibility or a
claim that a formation-table count establishes the maximum reachable battle.
"""
import argparse, ast, ctypes as C, datetime, hashlib, json, runpy, struct
from pathlib import Path
from native_art import ROOT, sha
from native_battle_wrappers import from_emulator
from actor_render_evidence import actors
from live_palette_evidence import observe as palette_observe

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--current',type=Path,required=True)
parser.add_argument('--reviewed-entry',action='store_true',help='Reuse authenticated combined-ROM cold world state for the existing formation324 scenario')
parser.add_argument('--entry-index',type=Path,default=ROOT/'build/art/reviewed-integration/complete-entry-latest.json')
args=parser.parse_args()
meta=json.loads(args.current.read_text(encoding='utf-8'));live=meta['components']['livePalette']
native_palette=meta['components'].get('nativePaletteTransport')
rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
assert hashlib.sha1(clean).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
out=ROOT/'build/art/all-class-capacity'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True)
word=lambda b,p:struct.unpack_from('<I',b,p)[0]
half=lambda b,p:struct.unpack_from('<H',b,p)[0]
table=0x54cd54;source=table+324*40;target=table+32*40
templates=word(rom,source+4)-0x08000000
assert rom[source:source+40]==clean[source:source+40] and rom[source]==6
assert rom[templates:templates+288]==clean[templates:templates+288]
assert all(half(rom,templates+48*i+42)&0x8000 for i in range(6))
jobs=word(rom,0xc8598)-0x08000000;items=word(rom,0x79aec)-0x08000000
permissions=word(rom,0xcac40)-0x08000000
def weapon(job):
    mask=word(rom,permissions+rom[jobs+52*job+0x2d]*4)
    return next(i for i in range(1,461) if rom[items+32*i+8] in (*range(1,20),31)
                and mask&(1<<(rom[items+32*i+8]-1)))
party={2:116,3:118,4:120,5:124};enemy=[117,119,121,125,122,123]
fixture=bytearray(rom);fixture[target:target+40]=rom[source:source+40];changes=[]
for index,job in enumerate(enemy):
    p=templates+48*index;prior=rom[p:p+48];race=rom[jobs+52*job+4]
    assert prior[0]==1 and rom[jobs+52*prior[1]+4]==race
    fixture[p+1:p+3]=bytes((job,0))
    fixture[p+8:p+18]=struct.pack('<5H',weapon(job),0,0,0,0)
    changes.append(dict(index=index,job=job,race=race,weapon=weapon(job),before=prior.hex(),after=fixture[p:p+48].hex()))
allowed=set(range(target,target+40))|set(range(templates,templates+288))
assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(rom,fixture)))
fixture=bytes(fixture);path=out/'fixture.gba';path.write_bytes(fixture)
if args.reviewed_entry:
    index=json.loads(args.entry_index.read_text())
    entry_path=ROOT/index['report'];entry=json.loads(entry_path.read_text())
    assert sha(entry_path.read_bytes())==index['sha256'] and entry['status']=='passed'
    assert entry['romSha1']==meta['romSha1'] and entry['manifestSha256']==sha(args.current.read_bytes())
    world=entry_path.parent/'cold-entry'
else:world=Path(meta['fixtureSource']).parent/'fixture'
seed=world/'accepted-world.state';seedbytes=seed.read_bytes()
route=json.loads((world/'route.json').read_text());proof=json.loads((world/'report.json').read_text())
assert proof['passed'] and proof['romSha1']==route['romSha1']==hashlib.sha1((world/'frozen.gba').read_bytes() if args.reviewed_entry else Path(meta['fixtureSource']).read_bytes()).hexdigest()
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
menus=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
tree=ast.parse((ROOT/'scripts/probe-ap-copy-heap.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='heap'],type_ignores=[]),'<heap walk>','exec'))
BASE=live['ramReservation'][0]-0x02000000
checks=[];inputs=[];samples=[];captures={};frames=[];seen=set();e=None;phase='setup';wrappers={};profiles={};clock=0
def check(ok,label):
    assert ok,phase+'/'+label
    checks.append(phase+'/'+label)
def mem(address):return C.string_at(*e.maps[address])
def capture(label):
    r=e.memory();e.save(out/(label+'.state'));e.screenshot(out/(label+'.png'))
    for ext,addr in [('ram',0x02000000),('iwram',0x03000000),('vram',0x06000000),('palette',0x05000000),('oam',0x07000000)]:
        (out/(label+'.'+ext)).write_bytes(mem(addr))
    captures[label]=dict(frame=clock,ramSha256=sha(r),heap=heap(r));return r
def observe():
    r=e.memory();s=heap(r)
    if 'freePayload' in s:
        check(s['end']==0x0203c000,'Heap respects art reservation')
        check(r[0x80:0x84]!=bytes(4),'Canonical party header intact')
        samples.append({k:v for k,v in s.items() if k!='allocationBlocks'})
    if word(r,BASE)==0x50414c31:
        check(word(r,BASE+2584)==0,'No palette ownership/allocation failure')
        check(not any(struct.unpack_from('<4I',r,BASE+live['refusalOffset'])) and
              word(r,BASE+live['bindingOffset']+live['bindingCounterOffset']+8)==0,'No palette/effect refusal')
def run(n,key=0):
    global clock
    for start in range(0,n,12):
        amount=min(12,n-start);e.run(amount,key);clock+=amount;observe()
def tap(key,wait=180):inputs.append([8,key,wait]);run(8,key);run(wait)
def display(label,n):
    for tick in range(n):
        run(1);r=e.memory();v=mem(0x06000000);pal=mem(0x05000000);oam=mem(0x07000000)
        bodies={unit:word(r,wrappers[unit]+0x44)-0x02000000 for unit in profiles}
        rows={a['address']:a for a in actors(fixture,r,v,set(bodies.values()))}
        check(len(rows)==10,label+' all ten bodies remain configured')
        for unit,body in bodies.items():
            a=rows[body];job=profiles[unit]
            check(a['resource'] in (256+2*(job-116),257+2*(job-116)) and a['declaredSequence'],label+' exact class resource '+str(job))
            check(a['expectedTiles']==a['tileCount']<=a['allocation'],label+' bounded native tiles '+str(job))
            check(bool(a['displayedFrames']),label+' exact native idle upload '+str(job))
        if native_palette:
            owners=set()
            for unit,body in bodies.items():
                a=rows[body];job=profiles[unit];side=bool(half(r,unit+0x28)&0x8000)
                selector=rom[jobs+52*job+11]>>(4 if side else 0)&15
                reference=struct.unpack_from('<16H',rom,0x419d60+selector*32)
                for i in range(128):
                    attr,x,tile=struct.unpack_from('<3H',oam,i*8)
                    # Native12BC fills its unused tail with this offscreen
                    # sentinel. Its tile0 also equals the first real body.
                    if (attr,x,tile)==(0x00a8,0x00f8,0):continue
                    if attr&0x300==0x200 or tile&1023!=a['tile']:continue
                    check(not attr&0x2100 and attr>>14==0 and x>>14==2,'Native custom body uses original4bpp OAM format')
                    actual=pal[512+(tile>>12)*32:544+(tile>>12)*32]
                    matches=[]
                    for scale in (32,19):
                        expected=struct.pack('<16H',*[sum((((c>>s)&31)*scale//32)<<s for s in (0,5,10)) for c in reference])
                        if actual==expected:matches.append(scale)
                    check(bool(matches),'Exact native side/brightness palette for class '+str(job))
                    left=x&511;top=attr&255
                    if left>=256:left-=512
                    if top>=160:top-=256
                    if left<240 and left+32>0 and top<160 and top+32>0:owners.add(job-116)
            check(bool(owners),'Generated native-palette bodies actually displayed')
            p=dict(owners=sorted(owners),active=0)
        else:p=palette_observe(live,fixture,r,pal,oam,check,set(range(3 if args.reviewed_entry else 10)))
        seen.update(p['owners'])
        frames.append(dict(label=label,tick=tick,frame=clock,owners=p['owners'],active=p['active'],
                           bodies={str(profiles[u]):dict(address=b,resource=rows[b]['resource'],tile=rows[b]['tile'],
                                  allocation=rows[b]['allocation'],displayed=rows[b]['displayedFrames']) for u,b in bodies.items()}))
def report(status,error=None):
    return dict(status=status,error=error,phase=phase,romSha1=meta['romSha1'],fixtureRomSha1=hashlib.sha1(fixture).hexdigest(),
                manifest=str(args.current),manifestSha256=sha(args.current.read_bytes()),scope=__doc__,
                checks=checks,inputs=inputs,samples=samples,captures=captures,frames=frames,seenOwners=sorted(seen),
                fixture=dict(sourceFormation=324,targetShell=32,templates=changes,partyProfiles=party,
                             world=str(seed),worldSha256=sha(seedbytes)),actors=len(wrappers),profiles=profiles,
                minFreeBytes=min((s['freePayload'] for s in samples),default=None),
                minLargestBlock=min((s['largestFree'] for s in samples),default=None))
try:
    e=E(path);e.load(seed);story=e.memory()[0x80:0x290]
    if args.reviewed_entry:
        check(e.memory()==(world/'accepted-world.ram').read_bytes(),'Exact own-ROM world checkpoint before declared formation inputs')
        check(e.memory()[0x3ff44:0x3ff4c]==b'\xd7'*8,'Cold-entry allocation canaries before action setup')
        e.set_memory(0x3ff44,bytes(8))
        inputs.append(['replace cold-entry canaries with empty action/execution roots',0x0203ff44,8])
    for slot,job in party.items():
        unit=0x80+264*slot;race=rom[jobs+52*job+4]
        check(e.memory()[unit+4]==1 and e.memory()[unit+6]==race,'Existing same-race generic party input '+str(slot))
        e.set_memory(unit+4,bytes((1,job,race,job)));e.set_memory(unit+0x35,bytes((job,)))
        e.set_memory(unit+0x2a,struct.pack('<5H',weapon(job),0,0,0,0))
    check(e.memory()[0x80:0x290]==story,'Both fixed story records preserved before entry')
    inputs.append(['preallocation four party/six enemy class profiles; legal loadouts',party,changes])
    phase='entry'
    for x,y,key in route['path']:run(1,key)
    run(30);tap(256,1200)
    for i in range(7):tap(256,600);capture('entry-'+str(i))
    for _ in range(3):tap(256)
    for _ in range(3):
        for key in (128,256,256,256):tap(key)
    tap(8,600);tap(256,600);tap(256,600)
    # Formation324 begins with an enemy turn. Retained timeout replay
    # 20260919T065732.199504Z reaches the actual party menu within600 more
    # no-input frames; the old1800-frame Giza budget was insufficient.
    waited=0
    # Reviewed full-action replay154819 reaches the menu240 frames after the
    # retained2400-frame timeout, identically with no input or one confirmation.
    # Preserve the older candidate budget and bound this reviewed case at3000.
    entry_budget=3000 if args.reviewed_entry else 2400
    while not menus['menu_visible'](e):
        check(waited<entry_budget,'Native party menu within declared'+str(entry_budget)+'-frame entry budget')
        run(10);waited+=10
    inputs.append(['bounded native battle-menu observation',waited,entry_budget])
    observe();r=capture('ready');phase='capacity'
    wrappers=from_emulator(fixture,e)
    check(len(wrappers)==13,'Native six party plus six enemies plus judge allocated')
    check({u for u in wrappers if 0x80<=u<0x80+24*264}=={0x80+264*i for i in range(6)},'All six original party slots deployed')
    profiles={0x80+264*slot:job for slot,job in party.items()}
    profiles.update({0x2fc4+264*i:job for i,job in enumerate(enemy)})
    check(set(profiles)<=set(wrappers) and set(profiles.values())==set(range(116,126)),'All ten different classes allocated together')
    for unit,job in profiles.items():
        check(r[unit+4]==1 and r[unit+7]==job and r[unit+6]==rom[jobs+52*job+4],'Native constructor retained racial class '+str(job))
    display('idle',120);capture('idle')
    phase='status'
    for key in (32,32,32,256):tap(key)
    r=capture('status');ctx=word(mem(0x03000000),0x2818)
    check(0x02000000<=ctx<ctx+0x7280<=0x0203c000,'Compact Status fits demanding live heap')
    check(word(r,ctx-0x02000000+0x2d50)==ctx+0x4340,'Status list owned by allocated context')
    check(struct.unpack_from('<4I',r,live['partyHeapRoot']-0x02000000)==(0x50485232,word(r,0xf434),1,0),'Native Status lifetime active')
    tap(1);run(180)
    for key in (16,16,16):tap(key)
    check(menus['menu_visible'](e),'Returned to native battle command menu')
    r=capture('returned');check(from_emulator(fixture,e)==wrappers,'All13 actors survive Status return')
    check(struct.unpack_from('<4I',r,live['partyHeapRoot']-0x02000000)==(0,word(r,0xf434),1,1),'Status ownership balanced after native destructor')
    check(word(r,0x3ff40)==0,'Status copy owner retired')
    phase='returned';display('returned',120);capture('final')
    check(seed.read_bytes()==seedbytes,'Source world checkpoint preserved')
    (out/'report.json').write_text(json.dumps(report('passed'),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),actors=len(wrappers),seenOwners=sorted(seen),report=str(out/'report.json'))))
except Exception as error:
    if e and e.frame:capture('failed')
    (out/'failed.json').write_text(json.dumps(report('failed',str(error)),indent=2)+'\n',encoding='utf-8')
    print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
