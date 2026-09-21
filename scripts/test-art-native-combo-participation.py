"""Fresh generic Dark Knight initiator and Viking participant Combo graphics.

Reuses the exact native-palette ready allocation. Declared legal equipment,
mastery/JP, starting geometry, target HP and native RNG are private inputs.
No job/body identity is rewritten. Control changes only the participant lesson's
global profile to its accepted native donor7; native chain/action code stays.
"""
import ast,ctypes as C,datetime,hashlib,json,runpy,struct
from pathlib import Path
from native_art import ROOT,sha
from native_battle_wrappers import from_emulator,fixed_giza_formation
from actor_render_evidence import actors
from native_body_display import pending_from_anchor,retained,layout_reset_display,completed_pending_facing
from native_oam_evidence import reconstruct
from native_hidden_constructor import observe as hidden_constructor
from mgba_instruction_trace import InstructionTrace

manifest=ROOT/'build/art/connected/a28b624bb13c8f2f2597a4d4bd3999b17c234b99/manifest.json'
meta=json.loads(manifest.read_text());rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
source=ROOT/'build/art/native-palette-entry/20260919T070815.647048Z';prior=json.loads((source/'report.json').read_text())
assert prior['status']=='passed' and prior['romSha1']==meta['romSha1']
seed=source/'candidate-ready.state';seedbytes=seed.read_bytes();ram0=(source/'candidate-ready.ram').read_bytes();iw0=(source/'candidate-ready.iwram').read_bytes()
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
lesson=next(x for x in registry['lessons'] if x['id']=='VIK-C1');owner=next(o for o in lesson['owners'] if o['jobId']==118)
word=lambda b,p:struct.unpack_from('<I',b,p)[0]
half=lambda b,p:struct.unpack_from('<H',b,p)[0]
lessons=word(rom,0xcd538)-0x08000000;race_base=word(rom,lessons+2*4)-0x08000000;record=race_base+8*owner['abilityIndex']
assert rom[record+6]==5 and half(rom,record+4)==lesson['globalAbilityId']
control=bytearray(rom);struct.pack_into('<H',control,record+4,7)
assert control[:record+4]==rom[:record+4] and control[record+6:]==rom[record+6:]
out=ROOT/'build/art/native-combo-participation'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
controlpath=out/'native-donor.gba';controlpath.write_bytes(control)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];menus=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
# Reuse the exact constructor observer independently proven by test-art-facing-reset.
observer_source=(ROOT/'scripts/test-samurai-fight.py').read_text();tree=ast.parse(observer_source)
constructor_code=compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='initial_action_reset'],type_ignores=[]),'<verified native constructor observer>','exec')
scope=dict(word=word,half=half,struct=struct,rom=rom);exec(constructor_code,scope)
INIT,PART,TARGET=0x290,0x398,0x33e4
checks=[];results={};inputs=[];e=None;clock=0;case='setup';trace=None;anchors={};previous={};samples=[];seen=set();membership=[]

def check(ok,label):
    assert ok,case+'/'+label
    checks.append(case+'/'+label)

class ComboTrace(InstructionTrace):
    def _instruction(self,cpu,opcode):
        pc=self.registers[15]-4
        if pc==0x080b32e8:
            try:
                r=self.emulator.memory();ctx=self.registers[7]-0x02000000
                assert 0<=ctx<=len(r)-0x15c4
                count=r[ctx+0x1539];assert count<=12
                def unit(pointer):
                    p=pointer-0x02000000;assert 0<=p<=len(r)-4
                    return word(r,p)
                self.events.append(dict(site='membership',videoFrame=self.frame_counter(self.core),
                    initiator=unit(word(r,ctx+0x141c)),target=unit(word(r,ctx+0x1420)),
                    members=[unit(word(r,ctx+0x1458+4*i)) for i in range(count)]))
            except BaseException as error:self.error=repr(error)
        super()._instruction(cpu,opcode)

def step(n,key=0):
    global clock
    e.run(n,key);clock+=n

def tap(key,wait=180):inputs.append([case,8,key,wait]);step(8,key);step(wait)

def active():
    r=e.memory();return word(r,word(r,0xf438)-0x02000000+24)

def save(label):
    e.save(out/(case+'-'+label+'.state'))
    if e.frame:e.screenshot(out/(case+'-'+label+'.png'))
    for ext,address in [('ram',0x02000000),('iwram',0x03000000),('vram',0x06000000),('palette',0x05000000),('oam',0x07000000)]:
        (out/(case+'-'+label+'.'+ext)).write_bytes(C.string_at(*e.maps[address]))

def observe(label,wrappers,producer=None):
    r=e.memory();v=C.string_at(*e.maps[0x06000000]);oam=C.string_at(*e.maps[0x07000000]);pal=C.string_at(*e.maps[0x05000000]);rows=[]
    geometry=None
    if producer:
        check(bytes.fromhex(producer['memory']['oam'])==oam,'Actual OAM matches last composition boundary '+label)
        iw=bytearray(0x8000)
        for key,p in [('main',0),('auxiliary',0x2c50),('mode',0x940)]:
            raw=bytes.fromhex(producer['memory'][key]);iw[p:p+len(raw)]=raw
        expected,counts=reconstruct(rom,iw)
        check(expected==oam,'Complete original native OAM including palette banks '+label)
        check(bytes.fromhex(producer['memory']['palette'])==pal,'Displayed palette equals native boundary '+label)
        geometry=dict(nativeShapes=True,counts=counts)
    for unit,job in ((INIT,117),(PART,118)):
        body=word(r,wrappers[unit]+0x44)-0x02000000;anchor=anchors.get(unit)
        found=actors(rom,r,v,{body});a=found[0] if found else None
        if a is None and anchor:a=layout_reset_display(rom,r,v,oam,body,anchor,clock-anchor['frame'])
        if a is None:
            scope.update(anchor=anchor,clock=clock)
            a=scope['initial_action_reset'](r,v,oam,body,geometry)
        if a is None and producer:a=hidden_constructor(rom,r,iw,v,oam,body,anchor,clock,check)
        check(a is not None,label+' Configured or bounded native body '+str(job))
        p=0x10000+a['tile']*32;block=v[p:p+a['allocation']*32]
        direct=bool(a['displayedFrames']) and a['declaredSequence'];hold=None
        if not direct:
            if anchor:hold=pending_from_anchor(a,block,anchor,clock-anchor['frame'])
            if not hold:hold=retained(a,block,previous.get(unit))
            if not hold and anchor:hold=completed_pending_facing(rom,a,block,anchor,clock-anchor['frame'])
            if not hold and a.get('configured') is False:hold=a['displayProof']
        row=dict(direct=direct,identity=(a['resource'],a['tile'],a['allocation']),block=block,first=a['first'],index=a['index'])
        hardware=[struct.unpack_from('<3H',oam,i*8) for i in range(128)]
        copies=[x for x in hardware if x!=(0xa8,0xf8,0) and x[0]&0x300!=0x200 and x[2]&1023==a['tile']]
        if direct:anchors[unit]=dict(row,frame=clock,actor=a,hardware=copies)
        elif not hold:anchors.pop(unit,None)
        previous[unit]=row
        check(a['resource']==256+2*(job-116) and a['declaredSequence'] and bool(direct or hold),label+' Exact current or bounded retained body '+str(job))
        check(a['expectedTiles']==a['tileCount']<=a['allocation'],label+' Bounded native body allocation '+str(job))
        signature=(job,a['mode'],tuple(a['displayedFrames']),bool(copies))
        if a['mode']>=8 and copies and direct and signature not in seen:
            seen.add(signature);e.screenshot(out/(case+'-job'+str(job)+'-mode'+str(a['mode'])+'-'+str(clock)+'.png'))
        rows.append(dict(unit=unit,job=job,actor=a,displayProof='current' if direct else hold,shown=bool(copies),blockSha256=sha(block)))
    samples.append(dict(frame=clock,label=label,rows=rows,paletteSha256=sha(pal),oamSha256=sha(oam)))

try:
    item_table=word(rom,0x79aec)-0x08000000
    axe=next(i for i in range(1,461) if rom[item_table+32*i+8]==31)
    for case,path in [('expanded',Path(meta['path'])),('native-donor',controlpath)]:
        e=E(path);e.load(seed);clock=0;anchors={};previous={};samples=[];seen=set()
        check(e.memory()==ram0 and C.string_at(*e.maps[0x03000000])==iw0,'Own-ROM ready state with existing allocated bodies')
        check(active()==0x02000000+INIT,'Actual Dark Knight turn')
        before_identity={u:e.memory()[u:u+8] for u in (INIT,PART)}
        check(before_identity[INIT][4:8]==bytes((1,117,1,117)) and before_identity[PART][4:8]==bytes((1,118,2,118)),'Both generic new class bodies already allocated')
        wrappers=from_emulator(rom,e);fixed_giza_formation(rom,e)
        for unit,x,y,height in ((INIT,1,14,16),(PART,5,13,32)):
            e.set_memory(unit+0xf6,bytes((x,y)));e.set_memory(wrappers[unit]+8,struct.pack('<3H',x*32+16,height,y*32+16))
        for unit in (0x80,0x188,0x290,0x398,0x4a0,0x5a8):
            e.set_memory(unit+0xd6,struct.pack('<H',3 if unit in (INIT,PART) else 0));e.set_memory(unit+0x3c,bytes((11 if unit==INIT else owner['abilityIndex'] if unit==PART else 0,)))
        e.set_memory(INIT+0x40+11,b'\x8a');e.set_memory(PART+0x40+owner['abilityIndex'],b'\x8a')
        e.set_memory(INIT+0x2a,struct.pack('<5H',1,0,0,0,0));e.set_memory(PART+0x2a,struct.pack('<5H',axe,0,0,0,0));e.set_memory(TARGET+0x18,struct.pack('<2H',500,500))
        inputs.append([case,'native allocated profiles unchanged; declared geometry/JP/mastery/loadouts/targetHP',INIT,PART,TARGET,axe,owner['abilityIndex']])
        step(30);observe('ready',wrappers);save('ready')
        for key in (256,128,128,128,256):tap(key)
        menus['wait_for_menu'](e);check(half(e.memory(),wrappers[INIT]+8)==144,'Native Move reaches4,14')
        for key in (256,16,256,128,256,256):tap(key)
        r=e.memory();manager=word(r,0xf438)-0x02000000
        check(r[manager+4]==11,'Actual Combo target confirmation')
        check(half(r,INIT+0xd6)==half(r,PART+0xd6)==3,'No premature JP debit');save('confirmation');observe('confirmation',wrappers)
        C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',0),4);inputs.append([case,'native RNG',0])
        trace=ComboTrace(e,{0x080b32e8:'chain-published',0x080004dc:'native-composed'},
            {0x080004dc:dict(main=(0x03000000,0x830),auxiliary=(0x03002c50,0x860),mode=(0x03000940,2),oam=(0x07000000,1024),palette=(0x05000000,1024))})
        with trace:
            for tick in range(1208):
                step(1,256 if tick<8 else 0)
                producer=next(x for x in reversed(trace.events) if x['site']=='native-composed')
                observe('action-'+str(tick),wrappers,producer)
        membership=[x for x in trace.events if x['site']=='membership']
        check(len(membership)==1 and membership[0]['initiator']==0x02000000+INIT and membership[0]['target']==0x02000000+TARGET and membership[0]['members']==[0x02000000+PART],'Actual native chain contains the new Viking participant')
        step(600);after=e.memory();save('executed')
        check(half(after,INIT+0xd6)==0,'Initiator spends JP once')
        check(0<500-half(after,TARGET+0x18)<500,'Native chain causes bounded nonlethal damage')
        check(all(after[u:u+8]==s for u,s in before_identity.items()),'Class identities unchanged throughout action')
        check(after[0x3ff44:0x3ff4c]==bytes(8),'Native action roots retired')
        for unit,job in ((INIT,117),(PART,118)):
            check(any(x['job']==job and x['shown'] and x['actor']['mode']>=8 and x['displayProof']=='current' for s in samples for x in s['rows']),'Actual non-idle generated body displayed '+str(job))
        old=active();tap(256,900);menus['wait_for_menu'](e,limit=6300);check(active()!=old,'Next native turn returned')
        results[case]=dict(damage=500-half(after,TARGET+0x18),jp=[half(after,u+0xd6) for u in (INIT,PART)],membership=membership,samples=samples,
            equipped=[after[u+0x2a:u+0x34].hex() for u in (INIT,PART)],mastery=[after[u+0x40:u+0xd0].hex() for u in (INIT,PART)],compositionEvents=trace.events)
        e.close();e=None
    for field in ('damage','jp','equipped','mastery'):
        check(results['expanded'][field]==results['native-donor'][field],'Exact native-donor outcome '+field)
    check(seed.read_bytes()==seedbytes,'Source ready checkpoint unchanged')
    report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,results=results,inputs=inputs,scope=__doc__,
        source=dict(path=str(seed),sha256=sha(seedbytes),reportSha256=sha((source/'report.json').read_bytes())),constructorObserverSha256=sha(observer_source.encode()),
        controlPatch=dict(offset=record+4,before=rom[record+4:record+6].hex(),after=control[record+4:record+6].hex()))
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),damage=results['expanded']['damage'],report=str(out/'report.json'))))
except Exception as error:
    if e:save('failed')
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),checks=checks,inputs=inputs,results=results,samples=samples,events=trace.events if trace else []),indent=2)+'\n',encoding='utf-8')
    print('Artifacts: '+str(out));raise
finally:
    if e:e.close()
