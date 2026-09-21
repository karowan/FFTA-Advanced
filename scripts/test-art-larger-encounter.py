"""Original mixed formation through a disposable existing encounter shell.

Only the complete native formation32 record is replaced with original record1
or23. Map, roster, spawn and deployment data remain that record's original data.
The Giza scene is retained: this is not original event eligibility/lifecycle.
The formation23 route intentionally retains the failed fourteen-actor case;
native draw-sort overflow does not establish that this combination is reachable.
"""
import argparse,ast,ctypes as C,datetime,hashlib,json,runpy,struct
from pathlib import Path
from native_art import ROOT,sha
from native_battle_wrappers import from_emulator
from actor_render_evidence import actors

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--manifest',type=Path,default=ROOT/'build/art/connected/current.json')
parser.add_argument('--formation',type=int,choices=(1,23),default=1)
args=parser.parse_args()
meta=json.loads(args.manifest.read_text());live=meta['components']['livePalette']
native_palette='nativePaletteTransport' in meta['components']
rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
table=0x54cd54;source_record=table+args.formation*40;target_record=table+32*40
assert rom[source_record:source_record+40]==clean[source_record:source_record+40]
assert rom[target_record:target_record+40]==clean[target_record:target_record+40]
template_count=8 if args.formation==1 else 10
allied_count=4 if args.formation==1 else 5
expected_party=8-allied_count;expected_actors=template_count+expected_party+1
party_slots=(0,1,2,3) if args.formation==1 else (1,2,3)
custom_slots=tuple(slot for slot in party_slots if slot>=2)
assert len(party_slots)==expected_party
assert rom[source_record]==template_count and rom[target_record]==5
templates=struct.unpack_from('<I',rom,source_record+4)[0]-0x08000000
assert rom[templates:templates+48*template_count]==clean[templates:templates+48*template_count]
flags=[struct.unpack_from('<H',rom,templates+48*i+42)[0] for i in range(template_count)]
assert sum(bool(x&0x8000) for x in flags)==template_count-allied_count and flags.count(0)==allied_count
assert rom[source_record+32]==8  # native deployment counter ceiling
assert rom[source_record+33]==1
if args.formation==23:
    event=0x563a70+203*12
    assert rom[event:event+12]==clean[event:event+12]==bytes.fromhex('00a817000000000100000000')
out=ROOT/'build/art/connected/larger-encounter'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
fixture=bytearray(rom);fixture[target_record:target_record+40]=rom[source_record:source_record+40]
assert fixture[:target_record]==rom[:target_record] and fixture[target_record+40:]==rom[target_record+40:]
path=out/('native-formation'+str(args.formation)+'.gba');path.write_bytes(fixture);fixture=bytes(fixture)
world=Path(meta['fixtureSource']).parent/'fixture';seed=world/'accepted-world.state';seedbytes=seed.read_bytes()
route=json.loads((world/'route.json').read_text());proof=json.loads((world/'report.json').read_text())
assert proof['passed'] and proof['romSha1']==route['romSha1']==hashlib.sha1(Path(meta['fixtureSource']).read_bytes()).hexdigest()
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];menus=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
tree=ast.parse((ROOT/'scripts/probe-ap-copy-heap.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='heap'],type_ignores=[]),'<heap walk>','exec'))
BASE=live['ramReservation'][0]-0x02000000;checks=[];inputs=[];samples=[];captures={};e=None;phase='setup'
w=lambda b,p:struct.unpack_from('<I',b,p)[0]
h=lambda b,p:struct.unpack_from('<H',b,p)[0]
profiles={2:(117,1),3:(118,2),4:(120,3),5:(124,4)}
def check(ok,label):
    assert ok,phase+'/'+label
    checks.append(phase+'/'+label)
def capture(label):
    r=e.memory();e.save(out/(label+'.state'));e.screenshot(out/(label+'.png'))
    for ext,addr in [('ram',0x02000000),('iwram',0x03000000),('vram',0x06000000),('palette',0x05000000),('oam',0x07000000)]:
        (out/(label+'.'+ext)).write_bytes(C.string_at(*e.maps[addr]))
    # Always retain a failing heap snapshot; a diagnostic walk must not mask
    # the original exception or prevent the failure report from being written.
    try:heap_snapshot=heap(r)
    except AssertionError as error:heap_snapshot=dict(error=str(error))
    captures[label]=dict(heap=heap_snapshot,ramSha256=sha(r));return r
def observe():
    r=e.memory();s=heap(r)
    if 'freePayload' in s:
        check(s['end']==0x0203c000,'Actual heap respects art reservation')
        check(r[0x80:0x84]!=bytes(4),'Canonical party identity remains intact')
        samples.append({k:v for k,v in s.items() if k!='allocationBlocks'})
    if not native_palette and w(r,BASE)==0x50414c31:
        check(w(r,BASE+2584)==0,'No class ownership or bank allocation failure')
        check(not any(struct.unpack_from('<4I',r,BASE+live['refusalOffset'])) and w(r,BASE+live['bindingOffset']+live['bindingCounterOffset']+8)==0,'No class palette/effect refusals')
def run(frames,key=0):
    for start in range(0,frames,12):e.run(min(12,frames-start),key);observe()
def tap(key,wait=180):inputs.append([8,key,wait]);run(8,key);run(wait)
try:
    e=E(path);e.load(seed)
    original=e.memory()[0x80:0x290]
    for slot,(job,race) in profiles.items():
        unit=0x80+slot*264;check(e.memory()[unit+6]==race,'Same-race generic profile '+str(slot))
        e.set_memory(unit+4,bytes((1,job,race,job)));e.set_memory(unit+0x35,bytes([job]))
    check(e.memory()[0x80:0x290]==original,'Fixed story records preserved')
    # Give the focus Dark Knight an ordinary legal sword before allocation.
    items=w(rom,0x79aec)-0x08000000;katana=next(i for i in range(1,461) if rom[items+32*i+8]==2)
    e.set_memory(0x2ba,struct.pack('<5H',katana,0,0,0,0))
    inputs.append(['preallocation same-race class profiles',profiles,'focus sword',katana])
    phase='world'
    for x,y,key in route['path']:e.run(1,key)
    e.run(30);tap(256,1200)
    phase='native-entry'
    for i in range(7):tap(256,600);capture('entry-'+str(i))
    # Preserve the native eight-allied-unit ceiling: fixed template allies
    # and two story members leave one or two selectable generic party slots.
    if args.formation==23:
        # This formation supplies Marche as a nonparty template; Montblanc
        # is already placed from the clan. Skip those roster entries to the
        # generic Dark Knight, then select Viking for the final allied slot.
        tap(128)
        for member in range(2):
            for i,key in enumerate((128,256,256,256)):
                tap(key);capture('deploy-member-'+str(member)+'-'+str(i))
    else:
        for i in range(3):tap(256);capture('deploy-first-'+str(i))
        for i,key in enumerate((128,256,256,256)):
            tap(key);capture('deploy-second-'+str(i))
    tap(8,600);capture('to-battle-start');tap(256,600);capture('to-battle-confirm')
    if args.formation==1:tap(256,600)
    waited=0
    while not menus['menu_visible'](e):
        check(waited<6300,'First native party menu within declared6300-frame turn budget')
        run(10);waited+=10
    inputs.append(['first native party menu wait',waited,6300]);observe();r=capture('ready');phase='larger-battle'
    wrappers=from_emulator(fixture,e);party={0x80+264*i for i in party_slots}
    captures['ready']['actualWrappers']=wrappers
    check({u for u in wrappers if 0x80<=u<0x80+24*264}==party,'Exact canonical party count under native eight-allied-unit ceiling')
    check(len(wrappers)>12,'Actually more actors than the prior Giza fixture')
    check(len(wrappers)==expected_actors,'Exact original roster plus allowed party and judge: '+str(expected_actors))
    check(len([u for u in wrappers if 0x2fc4<=u<0x3c24])==template_count+1,'All original nonparty templates plus one judge allocated')
    for index in range(template_count):
        unit=0x2fc4+264*index;template=templates+48*index
        check(unit in wrappers and r[unit+4]==rom[template] and r[unit+7]==rom[template+1],
              'Original native template identity '+str(index))
        check(bool(h(r,unit+40)&0x8000)==bool(flags[index]&0x8000),'Original native template side '+str(index))
    if args.formation==23:
        check(0x80 not in wrappers and 0x30cc in wrappers and r[0x30d0]==2,
              'Native formation Marche is used instead of a duplicate canonical party actor')
    for slot in custom_slots:
        job,race=profiles[slot]
        unit=0x80+slot*264;body=w(r,wrappers[unit]+0x44)-0x02000000
        figure=actors(fixture,r,C.string_at(*e.maps[0x06000000]),{body})
        check(len(figure)==1 and figure[0]['resource']==256+2*(job-116) and figure[0]['declaredSequence'],'Native allocated generated class body '+str(job))
    inputs.append(['actual native actor roster',sorted(wrappers)])
    if native_palette:
        from native_shared_palette_evidence import observe as native_colors
        captures['ready']['nativePalette']=native_colors(fixture,r,C.string_at(*e.maps[0x05000000]),C.string_at(*e.maps[0x07000000]),wrappers,check,set(range(10)))
    run(120);capture('idle')
    phase='larger-status'
    for key in (32,32,32,256):tap(key)
    r=capture('status');iw=C.string_at(*e.maps[0x03000000]);ctx=w(iw,0x2818)
    check(0x02000000<=ctx<ctx+0x7280<=0x0203c000,'Compact Status fits real larger-encounter heap')
    check(w(r,ctx-0x02000000+0x2d50)==ctx+0x4340,'Status list belongs to its allocated context')
    check(struct.unpack_from('<4I',r,live['partyHeapRoot']-0x02000000)==(0x50485232,w(r,0xf434),1,0),'Native Status shared-heap lifetime active')
    tap(1);run(180)
    for key in (16,16,16):tap(key)
    check(menus['menu_visible'](e),'Returned to native battle command menu')
    r=capture('returned')
    check(from_emulator(fixture,e)==wrappers,'Complete larger actor roster survives Status return')
    check(struct.unpack_from('<4I',r,live['partyHeapRoot']-0x02000000)==(0,w(r,0xf434),1,1),'Native destructor releases ownership and retains balanced lifetime counters')
    check(w(r,0x3ff40)==0,'Status copy owner retired')
    if native_palette:
        captures['returned']['nativePalette']=native_colors(fixture,r,C.string_at(*e.maps[0x05000000]),C.string_at(*e.maps[0x07000000]),wrappers,check,set(range(10)))
    check(seed.read_bytes()==seedbytes,'Reusable world source unchanged')
    report=dict(status='passed',romSha1=meta['romSha1'],fixtureRomSha1=hashlib.sha1(fixture).hexdigest(),checks=checks,inputs=inputs,samples=samples,captures=captures,
        actors=len(wrappers),profiles=profiles,deployedPartySlots=list(party_slots),deployedCustomSlots=list(custom_slots),nativeTemplateFlags=flags,minFreeBytes=min(s['freePayload'] for s in samples),minLargestBlock=min(s['largestFree'] for s in samples),
        source=dict(state=str(seed),sha256=sha(seedbytes)),fixture=dict(sourceFormation=args.formation,targetShell=32,offset=target_record,bytes=40,recordSha256=sha(rom[source_record:source_record+40]),templatesSha256=sha(rom[templates:templates+48*template_count]),originalEvent=203 if args.formation==23 else None),
        scope='Complete original mixed map/formation record through disposable Giza encounter shell, original template identities/levels/equipment/positions/side and native eight-allied ceiling. Actual roster count, sampled heap bounds, Status allocation/destruction and return. Native-palette mode checks actual allocated generic body and side/baseline colors at ready/return. Not original mission eligibility or complete scene lifecycle, all-ten simultaneous classes, unsampled allocation peaks, every encounter/effect or final art.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(status='passed',actors=len(wrappers),checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    if e and e.frame:capture('failed')
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],fixtureRomSha1=hashlib.sha1(fixture).hexdigest(),phase=phase,error=str(error),checks=checks,inputs=inputs,samples=samples,captures=captures),indent=2)+'\n',encoding='utf-8');print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
