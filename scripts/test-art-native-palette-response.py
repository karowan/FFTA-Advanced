"""Native shared-palette Move/cancel response against original-renderer control.

Each branch restores its own freshly allocated ready state. Offsets0/4 and
128-frame Move/cancel windows are unchanged. Every observed native state and
framebuffer must equal fresh ordinary execution of that same ROM. Raw native
input, foreground, DMA, palette and display timing is retained, never aligned.
"""
import ctypes as C,datetime,hashlib,json,runpy,struct
from pathlib import Path
from native_art import ROOT,sha
from native_battle_wrappers import from_emulator
from mgba_instruction_trace import InstructionTrace,DLL_SHA256

index=json.loads((ROOT/'build/art/native-palette-entry/latest.json').read_text())
entry_path=Path(index['report']);assert sha(entry_path.read_bytes())==index['sha256']
entry=json.loads(entry_path.read_text());assert entry['status']=='passed'
source=entry_path.parent;manifest=Path(entry['manifest']);assert sha(manifest.read_bytes())==entry['manifestSha256']
meta=json.loads(manifest.read_text());assert meta['romSha1']==entry['romSha1']
out=ROOT/'build/art/native-palette-response'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
SITES={0x08000460:'draw',0x080004b0:'vblank',0x0800221c:'input',0x08000498:'input-return',
       0x0800042e:'foreground-return',0x080004c8:'vblank-flag-check',0x080012bc:'compose',
       0x080004dc:'compose-return',0x080004fa:'vblank-display-return'}
SNAPS={p:dict(shadow=(0x03003860,1024),palette=(0x05000000,1024)) for p in (0x080004c8,0x080012bc,0x080004dc)}
NAVIGATION=[[8,key,180] for key in (256,128,128,128)]
ACTIONS=[('move',256,48,144),('cancel',1,144,48)]
checks=[];records=[];failures=[];comparisons=[];e=None;case='setup';trace=None
pins={str(entry_path):sha(entry_path.read_bytes()),str(manifest):sha(manifest.read_bytes())}
for case in ('control','candidate'):
    for suffix in ('state','ram','iwram'):
        p=source/(case+'-ready.'+suffix);pins[str(p)]=sha(p.read_bytes())

def check(ok,label):
    assert ok,case+'/'+label
    checks.append(case+'/'+label)

def frame_hash(frame):
    raw,w,h,pitch,pixel=frame;return sha(struct.pack('<4I',w,h,pitch,pixel)+raw)

def motion(rows,initial,target):
    positions=[r['position'] for r in rows]
    start=next(i for i,p in enumerate(positions) if p[0]!=initial)
    end=next(i for i,p in enumerate(positions) if p[0]==target)
    changes=[i for i in range(1,len(rows)) if positions[i]!=positions[i-1]]
    return dict(start=start,end=end,elapsed=end-start,positions=[positions[i] for i in changes])

def prepare(path,case,delay):
    global e
    e=E(path);e.load(source/(case+'-ready.state'))
    check(e.memory()==(source/(case+'-ready.ram')).read_bytes() and C.string_at(*e.maps[0x03000000])==(source/(case+'-ready.iwram')).read_bytes(),'Exact own-ROM retained ready memory')
    for press,key,wait in NAVIGATION:e.run(press,key);e.run(wait)
    e.run(delay)

try:
    for case in ('control','candidate'):
        row=entry['records'][case];path=Path(row['path']);rom=path.read_bytes()
        check(hashlib.sha1(rom).hexdigest()==row['romSha1'],'Authenticated exact branch ROM')
        for delay in (0,4):
            label='idle'+str(delay);prepare(path,case,delay)
            wrapper=from_emulator(rom,e)[0x290];canonical=e.memory()[0x80:0x1e70]
            trace=InstructionTrace(e,SITES,SNAPS);initial=trace.state();baseline=[]
            for _,key,_,_ in ACTIONS:
                for tick in range(128):
                    e.run(1,key if tick<8 else 0);baseline.append((sha(trace.state()),frame_hash(e.frame)))
            e.close();e=None;prepare(path,case,delay);trace=InstructionTrace(e,SITES,SNAPS)
            check(trace.state()==initial,label+' Fresh ordinary and observed branches start byte-identically')
            actions={}
            with trace:
                for action_index,(action,key,initial_x,target_x) in enumerate(ACTIONS):
                    rows=[];event_start=len(trace.events)
                    for tick in range(128):
                        start_cycles=trace.cycles();video_frame=trace.frame_counter(trace.core)
                        pressed=key if tick<8 else 0;e.run(1,pressed)
                        actual=(sha(trace.state()),frame_hash(e.frame));expected=baseline[action_index*128+tick]
                        if actual!=expected:
                            (out/'observed-mismatch.state').write_bytes(trace.state())
                            (out/'observed-mismatch.json').write_text(json.dumps(dict(case=case,delay=delay,action=action,tick=tick,actual=actual,expected=expected),indent=2)+'\n',encoding='utf-8')
                        check(actual==expected,label+'/'+action+'/'+str(tick)+' Entire observed state and frame equal ordinary execution')
                        ram=e.memory()
                        rows.append(dict(tick=tick,input=pressed,videoFrame=video_frame,startCycle=start_cycles,endCycle=trace.cycles(),
                            position=list(struct.unpack_from('<3H',ram,wrapper+8))))
                    check(rows[-1]['position']==[target_x,32,432],label+'/'+action+' Native target reached')
                    check(ram[0x80:0x1e70]==canonical,label+'/'+action+' Canonical party unchanged')
                    events=trace.events[event_start:]
                    decision=[x for x in events if x['site']=='vblank-flag-check']
                    before=[x for x in events if x['site']=='compose'];after=[x for x in events if x['site']=='compose-return']
                    display=[x for x in events if x['site']=='vblank-display-return']
                    check(len(decision)==len(before)==len(after)==len(display)==128,label+'/'+action+' Every native DMA/render/display boundary captured')
                    for tick,(d,b,a,v) in enumerate(zip(decision,before,after,display)):
                        prefix=label+'/'+action+'/'+str(tick)
                        check(d['videoFrame']==b['videoFrame']==a['videoFrame']==v['videoFrame'],prefix+' Boundaries belong to one frame')
                        check(b['memory']['shadow']==a['memory']['shadow'],prefix+' Entire native shadow retained')
                        check(b['memory']['palette']==a['memory']['palette'],prefix+' Native OAM composition does not rewrite hardware colors')
                        expected=d['memory']['palette'] if d['frameFlag'] else b['memory']['shadow']
                        check(b['memory']['palette']==expected,prefix+' Complete BG/OBJ hardware follows actual original DMA decision')
                        check(160<=b['scanline']<=a['scanline']<=v['scanline']<228,prefix+' Composition and display fit VBlank')
                    actions[action]=dict(motion=motion(rows,initial_x,target_x),frames=rows,events=events,
                        composeCycles=[(a['cycle']-b['cycle'])&0xffffffff for b,a in zip(before,after)])
            check(trace.slot.value==trace.original,label+' Host instruction dispatch restored')
            records.append(dict(case=case,idleFramesBeforeMove=delay,romSha1=row['romSha1'],actions=actions))
            print(json.dumps(dict(case=case,idle=delay,motion={k:{f:v['motion'][f] for f in ('start','end','elapsed')} for k,v in actions.items()})),flush=True)
            e.close();e=None
    for delay in (0,4):
        actual=next(r for r in records if r['case']=='candidate' and r['idleFramesBeforeMove']==delay)
        control=next(r for r in records if r['case']=='control' and r['idleFramesBeforeMove']==delay)
        for action,_,_,_ in ACTIONS:
            a,b=actual['actions'][action],control['actions'][action]
            check(a['motion']['positions']==b['motion']['positions'],'Identical complete ordered movement '+str((delay,action)))
            delta={k:a['motion'][k]-b['motion'][k] for k in ('start','end','elapsed')}
            for metric,value in delta.items():
                if value>0:failures.append(dict(delay=delay,action=action,metric=metric,extraFrames=value))
            mismatch=[]
            for site in ('input','draw','compose'):
                left=[e for e in a['events'] if e['site']==site];right=[e for e in b['events'] if e['site']==site]
                def times(events):
                    first=a['frames'][0]['videoFrame'] if events is left else b['frames'][0]['videoFrame']
                    return [(e['videoFrame']-first,e['nativeFrame'],e['inputs']) for e in events]
                if times(left)!=times(right):mismatch.append(site)
            for site in ('compose','compose-return'):
                left=[e['memory'] for e in a['events'] if e['site']==site];right=[e['memory'] for e in b['events'] if e['site']==site]
                if left!=right:failures.append(dict(delay=delay,action=action,nativeColorMismatch=site))
            comparisons.append(dict(delay=delay,action=action,candidate=a['motion'],control=b['motion'],extraFrames=delta,rawCadenceDifferences=mismatch))
    check(all(sha(Path(p).read_bytes())==s for p,s in pins.items()),'Every input evidence file remains unchanged')
    result=dict(status='failed' if failures else 'passed',romSha1=meta['romSha1'],checks=checks,failures=failures,comparisons=comparisons,
        entryReport=str(entry_path),pins=pins,records=records,navigation=NAVIGATION,actions=ACTIONS,coreSha256=DLL_SHA256,scope=__doc__)
    dest=out/('failed.json' if failures else 'report.json');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],checks=len(checks),failures=failures,report=str(dest))))
    if failures:raise SystemExit(1)
except Exception as error:
    if e:
        e.save(out/'failed.state')
        if e.frame:e.screenshot(out/'failed.png')
        for ext,address in [('ram',0x02000000),('iwram',0x03000000),('vram',0x06000000),('palette',0x05000000),('oam',0x07000000)]:
            (out/('failed.'+ext)).write_bytes(C.string_at(*e.maps[address]))
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),checks=checks,pins=pins,records=records),indent=2)+'\n',encoding='utf-8')
    print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
