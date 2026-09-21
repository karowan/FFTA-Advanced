"""Actual ten-class large portraits and fixed-character display controls.

Uses an isolated same-race appearance profile in a disposable emulator. Checks
portrait pixel/OAM/palette upload, idle and wheel coexistence and reopen life.
"""
import ctypes as C,datetime,hashlib,json,runpy,struct,sys
from pathlib import Path
from native_art import ROOT,sha
from native_portraits import decode,entry
from native_miniatures import decode as mini_decode
from actor_render_evidence import actors
from art_candidate import candidate
meta=candidate('build/art/generated-portraits/current.json','portraits')
oldmeta=json.loads((Path(meta['source']).parent/'manifest.json').read_text())
reviewed_menu=None
if '--manifest' in sys.argv:
    selected=json.loads((ROOT/sys.argv[sys.argv.index('--manifest')+1]).read_text())
    if 'reviewedNativeMiniatures' in selected.get('components',{}):
        oldmeta=selected['components']['classes'];reviewed_menu=selected['components']['reviewedNativeMiniatures']
    if 'reviewedMenuMiniatures' in selected.get('components',{}):
        oldmeta=selected['components']['classes'];reviewed_menu=selected['components']['reviewedMenuMiniatures']
seedpath=ROOT/'build/showcase/20260917T160011.215713Z/showcase.sav';seed=seedpath.read_bytes()
assert hashlib.sha1(seed).hexdigest()=='7831543efb239ef145764889214f8d83cd56eb14'
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
out=ROOT/'build/art/generated-portraits/ui'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];inputs=[];observations={};e=None
control_proof=None;retained_proof=None
def check(ok,label):
    assert ok,label
    checks.append(label)
def tap(key,wait=120):inputs.append([case,8,key,wait]);e.run(8,key);e.run(wait)
def capture(name,job=None):
    ram=e.memory();vram=C.string_at(*e.maps[0x06000000]);pal=C.string_at(*e.maps[0x05000000]);oam=C.string_at(*e.maps[0x07000000])
    stem=case+'-'+name;e.screenshot(out/(stem+'.png'))
    for suffix,data in [('ram',ram),('vram',vram),('palette',pal),('oam',oam)]: (out/(stem+'.'+suffix)).write_bytes(data)
    obs=dict(frame=sha(e.frame[0]),owned=sha(ram[0x80:0x1e70]),vram=sha(vram),palette=sha(pal),oam=sha(oam));observations[case][name]=obs
    if job:
        raw=decode(rom,entry(rom,meta['pixelArchive'],job['portrait']))[0]
        positions=[p for p in range(0x10000,len(vram)-len(raw)+1,32) if vram[p:p+len(raw)]==raw]
        check(len(positions)==1,stem+' exact independent portrait upload');p=positions[0];obs['portraitVRAM']=p
        tile=(p-0x10000)//32;objects=[struct.unpack_from('<3H',oam,i*8) for i in range(128)]
        owners=[v for v in objects if v[0]&0x300!=0x200 and v[0]&0x2000 and v[2]&1023==tile]
        check(len(owners)==1,stem+' portrait has one native8bpp OAM owner')
        a,b,c=owners[0];check(a>>14==0 and b>>14==3,stem+' native64x64 portrait dimensions')
        if job.get('portraitWindow'):
            from PIL import Image
            box=Image.open(job['nativeImage']).convert('RGBA').getbbox();check(box is not None,stem+' nonempty reviewed portrait')
            left,top,right,bottom=box
            if b&4096:left,right=64-right,64-left
            if b&8192:top,bottom=64-bottom,64-top
            x=b&511;y=a&255;x=x-512 if x>=256 else x;y=y-256 if y>=128 else y
            check(0<=x+left<x+right<=48 and 0<=y+top<y+bottom<=56,stem+' entire reviewed portrait fits visible menu window')
        obs['portraitOAM']=list(owners[0]);check(sha(pal[0x2c0:0x320])==job['paletteSha256'],stem+' exact48-color hardware palette')
        actor=next(j for j in oldmeta['jobs'] if j['job']==job['job']);figures=actors(rom,ram,vram)
        check(len(figures)==1 and figures[0]['resource']==actor['resource'] and figures[0]['declaredSequence'] and bool(figures[0]['displayedFrames']),stem+' unchanged independent idle actor renders')
        mini=mini_decode(rom,oldmeta['container'],actor['miniature']['index'])
        check(any(vram[p:p+640]==mini for p in range(0x10000,len(vram)-639,32)),stem+' independent generated wheel figure still uploaded')
        if reviewed_menu:
            j=next(j for j in reviewed_menu['jobs'] if j['job']==job['job'])
            locations=[p for p in range(0x10000,len(vram)-639,32) if vram[p:p+640]==mini]
            check(len(locations)==1,stem+' reviewed miniature upload unique')
            first=(locations[0]-0x10000)//32
            for tile in (first,first+16):
                parts=[v for v in objects if v[0]&0x300!=0x200 and v[2]&1023==tile]
                check(len(parts)==1,stem+' reviewed miniature native OAM part')
                bank=parts[0][2]>>12
                if 'symbols' in reviewed_menu:
                    check(bank in (j['normalBank'],j['dimBank']),stem+' generated figure has its bright/dim palette')
                    base=reviewed_menu['symbols']['ffta_reviewed_menu_obj']-0x08000000
                    expected=rom[base+bank*32:base+(bank+1)*32]
                else:
                    check(bank in range(6),stem+' original bright/dim palette bank')
                    expected=rom[0x94eddc+bank*32:0x94edfc+bank*32]
                check(pal[0x200+bank*32:0x200+(bank+1)*32]==expected,stem+' exact reviewed figure colors displayed')
    return obs
try:
    cases=[('generated-'+str(j['job']),meta['path'],meta['romSha1'],j) for j in meta['jobs']]
    fixed_path,fixed_sha=meta['source'],meta['baseRomSha1']
    if '--manifest' in sys.argv:
        assembled=json.loads((ROOT/sys.argv[sys.argv.index('--manifest')+1]).read_text())
        if assembled['schema']==3:
            from native_portraits import PIXEL_LITERALS,LAYOUT_LITERALS,PALETTE_LITERALS,PIXELS,LAYOUTS,PALETTES
            target=Path(meta['path']).read_bytes();control=bytearray(target);patches=[]
            redirects=[(p,meta['pixelArchive'],PIXELS) for p in PIXEL_LITERALS]
            redirects += [(p,meta['oamArchive'],LAYOUTS) for p in LAYOUT_LITERALS]
            redirects += list(zip(PALETTE_LITERALS,meta['paletteArchives'],PALETTES))
            for offset,new,old in redirects:
                check(struct.unpack_from('<I',control,offset)[0]==0x08000000+new,'Exact connected portrait literal '+hex(offset))
                struct.pack_into('<I',control,offset,0x08000000+old)
                patches.append(dict(offset=offset,before=target[offset:offset+4].hex(),after=control[offset:offset+4].hex()))
            allowed={i for p,_,_ in redirects for i in range(p,p+4)}
            check(all(a==b or i in allowed for i,(a,b) in enumerate(zip(target,control))),'Control changes only portrait archive literals')
            fixed_path=out/'fixed-original-portraits.gba';fixed_path.write_bytes(control)
            fixed_sha=hashlib.sha1(control).hexdigest();control_proof=dict(path=str(fixed_path),sha1=fixed_sha,patches=patches)
    if '--retained-generics' in sys.argv:
        priorpath=ROOT/sys.argv[sys.argv.index('--retained-generics')+1]
        expected=sys.argv[sys.argv.index('--retained-sha256')+1]
        check(sha(priorpath.read_bytes())==expected,'Retained report authenticated')
        prior=json.loads(priorpath.read_text())
        check(prior['romSha1']==meta['romSha1'] and prior['status']=='failed' and
              prior['error']=='Fixed-character wheel0 unchanged frame','Retained failure is only the later fixed-character comparison')
        artifacts={}
        for job in meta['jobs']:
            case='generated-'+str(job['job'])
            for name in ('wheel0','wheel1','wheel2','wheel3','cancelled','reopened'):
                stem=case+'-'+name;obs=prior['observations'][case][name]
                for ext in ('vram','palette','oam','ram','png'):
                    path=priorpath.parent/(stem+'.'+ext);raw=path.read_bytes();artifacts[str(path)]=sha(raw)
                    if ext in ('vram','palette','oam'):check(sha(raw)==obs[ext],stem+' retained '+ext+' exact')
                    if ext=='ram':check(sha(raw[0x80:0x1e70])==obs['owned'],stem+' retained owned data exact')
                if name!='cancelled':
                    for suffix in (' exact independent portrait upload',' portrait has one native8bpp OAM owner',
                        ' native64x64 portrait dimensions',' exact48-color hardware palette',
                        ' unchanged independent idle actor renders',' independent generated wheel figure still uploaded'):
                        check(stem+suffix in prior['checks'],stem+' completed retained check '+suffix)
            observations[case]=prior['observations'][case]
        retained_proof=dict(report=str(priorpath),sha256=expected,artifacts=artifacts,
                            scope='Completed ten-class checks before the retained fixed-character failure; no reuse of failed fixed-character comparison.')
        cases=[]
    cases += [('fixed-baseline',fixed_path,fixed_sha,None),('fixed-candidate',meta['path'],meta['romSha1'],None)]
    for case,path,digest,job in cases:
        rom=Path(path).read_bytes();check(hashlib.sha1(rom).hexdigest()==digest,case+' authenticated ROM');observations[case]={}
        if job:
            record=next(j for j in oldmeta['classResources']['jobs'] if j['job']==job['job']);race=record['race'];slot={1:2,2:3,3:4,5:1,4:5}[race]
        else:slot=1
        e=E(Path(path));e.set_memory(0,seed,0);e.run(3600)
        for key in (8,256,256,256):tap(key,300)
        if job:
            check(e.memory()[0x80+slot*264+6]==race,case+' existing same-race member')
            profile=bytes([1,job['job'],race,job['job']]);e.set_memory(0x80+slot*264+4,profile);inputs.append([case,'appearance profile',slot,list(profile)])
        else:check(e.memory()[0x80+slot*264+4]!=1,case+' authentic fixed-character control')
        for key in (8,256):tap(key)
        if slot>=4:tap(32)
        for _ in range(slot%4):tap(128)
        tap(256);tap(32);tap(32);tap(256,600)
        if '--trace-miniature' in sys.argv and case=='generated-116':
            from mgba_instruction_trace import InstructionTrace
            state=out/'miniature-observer-start.state';e.save(state);e.close()
            e=E(Path(path));e.load(state)
            e.run(2);plain=out/'miniature-observer-plain.state';e.save(plain)
            plain_frame=sha(e.frame[0]);e.close();e=E(Path(path));e.load(state)
            sites={0x08001cf0:'front-layout',0x08001e18:'ui-layout',0x08001f34:'main-layout'}
            ranges={pc:{'stack':(0x03007000,4096)} for pc in sites}
            trace=InstructionTrace(e,sites,ranges)
            with trace:e.run(2)
            seen=out/'miniature-observer-traced.state';e.save(seen)
            (out/'miniature-producer-trace.json').write_text(json.dumps(dict(
                romSha1=meta['romSha1'],events=trace.events,stackBase=0x03007000),indent=2)+'\n')
            check(plain.read_bytes()==seen.read_bytes() and sha(e.frame[0])==plain_frame,
                  'Miniature producer observation preserves exact native state and display')
        capture('wheel0',job)
        for i in range(1,4):e.run(16);capture('wheel'+str(i),job)
        tap(1,180);capture('cancelled')
        tap(256,600);capture('reopened',job)
        e.close();e=None
    for name in observations['fixed-baseline']:
        old=observations['fixed-baseline'][name];new=observations['fixed-candidate'][name]
        for field in ('frame','owned','vram','palette','oam'):check(old[field]==new[field],'Fixed-character '+name+' unchanged '+field)
    check(seedpath.read_bytes()==seed,'Source save unchanged')
    report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,inputs=inputs,observations=observations,
        fixedControl=control_proof,retainedGenerics=retained_proof,
        scope='Ten generic large8bpp portrait uploads, native OAM and48-color palettes, coexistence with idle actors/wheel miniatures, idle advances and cancel/reopen. Actual named-character frame/VRAM/OAM/palette/owned-data differential control. Isolated presentation profile; no battle/water/action/production-art acceptance.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),checks=checks,inputs=inputs,observations=observations),indent=2)+'\n');print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
