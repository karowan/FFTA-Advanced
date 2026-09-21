"""Native Samurai Move/cancel with explicitly assigned generated walking frames."""
import argparse,ctypes as C,datetime,hashlib,json,runpy,struct
from pathlib import Path
from native_art import ROOT,sha
from native_battle_wrappers import fixed_giza_formation,from_emulator
from actor_render_evidence import actors
from native_body_display import pending_from_anchor,retained,layout_reset_display

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--current',type=Path,default=ROOT/'build/art/generated-actions/mapped-walk-current.json')
parser.add_argument('--live-refinement',action='store_true')
parser.add_argument('--comparison-manifest',type=Path)
args=parser.parse_args()
meta=json.loads(args.current.read_text(encoding='utf-8'))
if args.live_refinement:
    assert args.comparison_manifest
    comparison=json.loads(args.comparison_manifest.read_text(encoding='utf-8'))
    meta=dict(meta,comparisonSource=comparison['path'],comparisonRomSha1=comparison['romSha1'],releaseSource=meta['fixtureSource'])
    from live_palette_evidence import observe as palette_observe
fixture=Path(meta['releaseSource']).parent/'fixture';seed=fixture/'accepted-world.state';seedbytes=seed.read_bytes()
routepath=fixture/'route.json';route=json.loads(routepath.read_text());proof=json.loads((fixture/'report.json').read_text())
assert proof['passed'] and proof['romSha1']==route['romSha1']==hashlib.sha1(Path(meta['releaseSource']).read_bytes()).hexdigest()
assert (fixture/'frozen.gba').read_bytes()==Path(meta['releaseSource']).read_bytes()
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];menu=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
out=ROOT/'build/art/explicit-walk'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];inputs=[];observations={};outcomes={};e=None;case='setup';clock=0;anchors={};previous={};wrappers={}
def check(ok,label):
    assert ok,case+'/'+label
    checks.append(case+'/'+label)
def active():
    r=e.memory();return struct.unpack_from('<I',r,struct.unpack_from('<I',r,0xf438)[0]-0x02000000+24)[0]
def step(frames,key=0):
    global clock
    e.run(frames,key);clock+=frames
def tap(key,wait=180):
    inputs.append([case,8,key,wait]);step(8,key);step(wait)
def capture(name):
    ram=e.memory();vram=C.string_at(*e.maps[0x06000000]);allactors=actors(rom,ram,vram)
    body=struct.unpack_from('<I',ram,wrappers[0x290]+0x44)[0]-0x02000000
    anchor=anchors.get(body);hardware=C.string_at(*e.maps[0x07000000])
    a=next((a for a in allactors if a['address']==body),None)
    if a is None:
        a=layout_reset_display(rom,ram,vram,hardware,body,anchor,clock-anchor['frame']) if anchor else None
    check(a is not None,name+' configured or strictly bounded native layout reset')
    p=0x10000+a['tile']*32;block=vram[p:p+a['allocation']*32]
    direct=bool(a['displayedFrames']) and a['declaredSequence']
    hold=pending_from_anchor(a,block,anchor,clock-anchor['frame']) if anchor else None
    if not hold:hold=retained(a,block,previous.get(body))
    if not hold and a.get('configured') is False:hold=a['displayProof']
    row=dict(direct=direct,identity=(a['resource'],a['tile'],a['allocation']),block=block,first=a['first'],index=a['index'])
    if direct:
        objects=[struct.unpack_from('<3H',hardware,i*8) for i in range(128)]
        anchors[body]=dict(row,frame=clock,actor=a,hardware=[v for v in objects if v[0]&0x300!=0x200 and v[2]&1023==a['tile']])
    elif not hold:anchors.pop(body,None)
    previous[body]=row
    position=list(struct.unpack_from('<3H',ram,wrappers[0x290]+8))
    observations[case][name]=dict(actor=a,position=position,displayProof='current' if direct else hold,frame=clock,blockSha256=sha(block),owned=sha(ram[0x80:0x1e70]))
    check(a['resource']==256 and a['declaredSequence'] and bool(direct or hold),name+' exact owned native body upload')
    check(a['expectedTiles']==a['tileCount']<=a['allocation'],name+' bounded native OAM')
    if args.live_refinement and case=='mapped':
        palette_observe(meta,rom,ram,C.string_at(*e.maps[0x05000000]),hardware,check,{0})
    if name in ('ready','moved','returned') or 48<position[0]<144:
        if name in ('ready','moved','returned') or not any(v['actor']['mode']==a['mode'] and v['actor']['displayedFrames']==a['displayedFrames'] for k,v in observations[case].items() if k!=name):
            e.screenshot(out/(case+'-'+name+'.png'))
            for ext,data in (('ram',ram),('vram',vram),('palette',C.string_at(*e.maps[0x05000000])),('oam',C.string_at(*e.maps[0x07000000]))):(out/(case+'-'+name+'.'+ext)).write_bytes(data)
    return ram
def animated_tap(key,label):
    inputs.append([case,'sampled input',key,8,600,2]);step(8,key);capture(label+'-press')
    for tick in range(0,600,2):step(2);capture(label+'-'+str(tick))
try:
    for case,path,digest in (('parent',meta['comparisonSource'],meta['comparisonRomSha1']),('mapped',meta['path'],meta['romSha1'])):
        rom=Path(path).read_bytes();check(hashlib.sha1(rom).hexdigest()==digest,'Authenticated ROM')
        e=E(Path(path));e.load(seed);e.set_memory(0x3ff44,bytes(8));clock=0;anchors.clear();previous.clear();observations[case]={}
        check(e.memory()[0x296]==1,'Existing recruited human slot2')
        e.set_memory(0x294,bytes([1,116,1,116]));e.set_memory(0x2c5,bytes([116]));inputs.append([case,'preallocation Human Samurai profile',2,[1,116,1,116]])
        items=struct.unpack_from('<I',rom,0x79aec)[0]-0x08000000
        katana=next(i for i in range(1,461) if rom[items+32*i+8]==9)
        e.set_memory(0x2ba,struct.pack('<5H',katana,0,0,0,0));inputs.append([case,'preallocation ordinary katana-only loadout',katana])
        for x,y,key in route['path']:step(1,key)
        step(30);tap(256,1200)
        for _ in range(7):tap(256,600)
        for _ in range(3):tap(256)
        for _ in range(3):
            for key in (128,256,256,256):tap(key)
        tap(8,600);tap(256,600);tap(256,600);menu['wait_for_menu'](e)
        for turn in range(12):
            if active()==0x02000290:break
            old=active();inputs.append([case,'Wait preceding actor',old])
            for key in (32,32,256,256):tap(key)
            for waited in range(0,6300,30):
                if active()!=old and menu['menu_visible'](e):break
                step(30)
            else:raise AssertionError('Native turn did not advance')
        check(active()==0x02000290,'Actual recruited Samurai turn')
        fixed_giza_formation(rom,e);step(30);wrappers=from_emulator(rom,e);inputs.append([case,'canonical Giza start'])
        initial=capture('ready');w=wrappers[0x290]
        check(struct.unpack_from('<3H',initial,w+8)==(48,32,432),'Declared start1,13')
        for key in (256,128,128,128):tap(key)
        animated_tap(256,'move');moved=capture('moved')
        check(struct.unpack_from('<3H',moved,w+8)==(144,32,432),'Native three-cell Move to4,13')
        animated_tap(1,'cancel');final=capture('returned')
        check(struct.unpack_from('<3H',final,w+8)==(48,32,432),'Native cancel restores position')
        check(final[0x1940:0x1ebc]==initial[0x1940:0x1ebc] and final[0x3ff44:0x3ff4c]==bytes(8),'No inventory/status mutation or retained action root')
        walking=[v for v in observations[case].values() if 48<v['position'][0]<144 and v['actor']['displayedFrames']]
        check(bool(walking),'Actual interpolated walking positions with verified frames observed')
        if case=='mapped':
            if args.live_refinement:
                expected={f['tileSha256'] for s in meta['assignments'] if s['resource']==256 and s['slot']<4 for f in s['frames']}
            else:
                resource=next(r for r in meta['resources'] if r['id']==256)
                expected={f['sha256'] for s in resource['sequences'] if s['slot'] in (0,1,2,3) for f in s['frames']}
            seen={v['blockSha256'] for v in walking}
            check(seen<=expected and len(seen)>=3,'At least three distinct explicitly mapped walk poses uploaded')
        outcomes[case]=dict(position=list(struct.unpack_from('<3H',final,w+8)),owned=sha(final[0x80:0x1e70]),active=active())
        e.close();e=None
    check(outcomes['parent']==outcomes['mapped'],'Paired Move/cancel gameplay outcome exact')
    check(seed.read_bytes()==seedbytes,'World fixture unchanged')
    report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,inputs=inputs,outcomes=outcomes,observations=observations,fixtureSha256=sha(seedbytes),routeSha256=sha(routepath.read_bytes()),scope='Native recruited Human Samurai turn, actual three-cell Move and cancel; explicit mapped walking frames in native VRAM, allocation and paired outcomes. Draft art, not completed walk aesthetics, all directions/actions or packaged delivery.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    if e:
        e.save(out/(case+'-failed.state'));e.screenshot(out/(case+'-failed.png'))
        for ext,addr in (('ram',0x02000000),('iwram',0x03000000),('vram',0x06000000)):(out/(case+'-failed.'+ext)).write_bytes(C.string_at(*e.maps[addr]))
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),checks=checks,inputs=inputs,observations=observations),indent=2)+'\n');print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
