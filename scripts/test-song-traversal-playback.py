"""Bard command controls and Updraft persistence through actual player inputs.

One prepared turn per race. All commands are selected in the native menu,
previewed/cancelled, committed, rendered, and followed by native Wait. Buff
cases cold boot the original candidate, then expire through actual turns.
"""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
support=(ROOT/'scripts/test-remaining-reaction-playback.py').read_text().split('\nconfigs=[')[0]
support=support.replace("'remaining-reactions-'+stamp", "'song-traversal-'+stamp")
support=support.replace('remaining-reactions-latest.json','song-traversal-latest.json')
exec(compile(support,'<authenticated playback support>','exec'))
TARGET=0x80
costs={393:8,394:12,395:12,396:8,397:12,398:0,399:0,400:24,377:8}
cases=[(a,False) for a in range(393,401)]+[(398,True),(377,False)]
if '--updraft-only' in sys.argv:cases=[(377,False)]
if '--bard-only' in sys.argv:cases=[c for c in cases if c[0]!=377]
if '--action' in sys.argv:cases=[c for c in cases if c[0]==int(sys.argv[sys.argv.index('--action')+1])]
assert cases
reused=None
if '--resume-latest' in sys.argv:
    previous_path=pathlib.Path(json.loads((LAB/'song-traversal-latest.json').read_text())['path'])
    previous=json.loads(previous_path.read_text())
    assert previous['romSha1']==meta['romSha1'] and previous['instrumentedSha1']==hashlib.sha1(instrumented).hexdigest()
    outcomes=previous['outcomes'];cold=previous['cold']
    for row in outcomes:
        for name in ('prior','after'):row[name]={int(k):v for k,v in row[name].items()}
        recorded=(pathlib.Path(row['sample'])/'native-result.ram').read_bytes()
        assert word(recorded,LOG)==0x504c4159 and word(recorded,LOG+8)==row['action']
    cases=[c for c in cases if not any(o['action']==c[0] and o['silenced']==c[1] for o in outcomes)]
    reused=dict(path=str(previous_path),sha1=hashlib.sha1(previous_path.read_bytes()).hexdigest())

def observe_owned(e,units):
    m=ARM(image,C.string_at(*e.maps[0x03000000]));m.put(0x02000000,e.memory())
    result={}
    for u in units:
        ptr=m.call(meta['symbols']['ffta_job_state'],0x02000000+u)
        result[u]=dict(state=m.read(ptr,22).hex(),move=m.call(0x080ca394,0x02000000+u),jump=e.memory()[u+0xfe],
                       updraft=[m.call(meta['symbols']['ffta_geo_updraft'],0x02000000+u,k) for k in (0,1)])
    return result

def save_report(passed=False):
    data=dict(passed=passed,romSha1=meta['romSha1'],instrumentedSha1=hashlib.sha1(instrumented).hexdigest(),
              fixture=proof,total=sum(checks.values()),checks=dict(checks),outcomes=outcomes,cold=cold,reused=reused,
              limits=['Declared mastery, resources, formation and undead condition before inputs.',
                      'Frame progression is not a pixel-perfect artwork or banner-text certification.',
                      'Only selected cold cases have native timer expiry; acquisition/campaign remain separate.'])
    (OUT/'report.json').write_text(json.dumps(data,indent=2))
    (LAB/'song-traversal-latest.json').write_text(json.dumps(dict(path=str(OUT/'report.json'),passed=passed)))
    return data

starts={}
for actor in sorted({0x290 if action==377 else 0x188 for action,_ in cases}):
    case=('prepare',actor);e=E(TEST_ROM)
    try:
        e.load(FIX/'battle-ready.state');e.run(1);menu(e);fixed_giza_formation(image,e)
        wrappers=from_emulator(image,e);r=e.memory()
        grid=word(r,0x7f14)-0x02000000;width=r[0x7f18]
        height=lambda x,y:r[grid+2*(width*y+x)]
        if actor==0x290:
            # The first natural vertical pair exactly two height apart supplies the
            # real conditional Jump case. No map height is modified.
            pairs=[(x,y) for y in range(1,14) for x in range(1,15) if height(x,y) and height(x,y+1) and height(x,y)-height(x,y+1)==2]
            check('natural-Updraft-height-pair',bool(pairs));x,y=pairs[0]
            tx,ty=x,y+1;direction=32
        else:x,y=0,14;tx,ty=1,14;direction=128
        positions={actor:(x,y),TARGET:(tx,ty)}
        # Keep other actors away from the controlled cross. Valid native Giza
        # tiles and their exact decoded elevations preserve actual sprites.
        reserve=[(2,12),(3,12),(3,13),(3,14),(4,14),(5,14),(8,11),(7,11),(5,8),(10,5),(8,2)]
        taken=set(positions.values())
        for u in wrappers:
            if u in positions:continue
            xy=next(p for p in reserve if p not in taken and abs(p[0]-tx)+abs(p[1]-ty)>1)
            positions[u]=xy;taken.add(xy)
        for u,(ux,uy) in positions.items():
            check('valid-declared-tile',bool(height(ux,uy)))
            e.set_memory(u+0xf6,bytes((ux,uy)))
            e.set_memory(wrappers[u]+8,struct.pack('<3H',ux*32+16,height(ux,uy)*16,uy*32+16))
            e.set_memory(u+0x18,struct.pack('<4H',500,500,99,99))
            e.set_memory(u+0xe8,bytes(8));e.set_memory(u+0x3a,bytes(2))
        for turn in range(16):
            if active(e)==0x02000000+actor:break
            previous=active(e)
            for key in (32,32,256,256):tap(e,key)
            menu(e,previous)
        check('native-selected-racial-turn',active(e)==0x02000000+actor)
        e.set_memory(0x3ff44,bytes(8)+b'\xd7'*0xb4);e.set_memory(LOG,bytes(160))
        checkpoint(e,'start-'+str(actor),OUT);starts[actor]=dict(x=x,y=y,target=[tx,ty],direction=direction,heights=[height(x,y),height(tx,ty)])
    finally:e.close()

for action,silenced in cases:
    case=(action,silenced);actor=0x290 if action==377 else 0x188;race=3 if action==377 else 5;job=121 if action==377 else 123
    folder=OUT/(str(action)+('-silenced' if silenced else ''));folder.mkdir();e=E(TEST_ROM)
    try:
        e.load(OUT/('start-'+str(actor)+'.state'));e.run(1)
        check('native-race-retained',e.memory()[actor+6]==race)
        for u in (actor,TARGET):
            e.set_memory(u+0x18,struct.pack('<4H',200,500,20,100));e.set_memory(u+0xe8,bytes(8));e.set_memory(u+0x3a,bytes(2))
            e.set_memory(u+0x20,struct.pack('<4H',70,40,70,40))
            e.set_memory(u+0x2a,bytes(10));e.set_memory(u+0x29,b'\0')
        e.set_memory(actor+0x1c,struct.pack('<H',100))
        e.set_memory(actor+5,bytes((job,race,job)));e.set_memory(actor+0x35,bytes((job,)))
        e.set_memory(actor+8,b'\0');e.set_memory(actor+0x36,bytes(2));e.set_memory(actor+0x40,bytes(144))
        lesson=next(l for l in registry['lessons'] if l['globalAbilityId']==action and l['type'][0]=='A')
        index=next(o['abilityIndex'] for o in lesson['owners'] if o['race']==race)
        e.set_memory(actor+0x40+index,b'\xff')
        if silenced:e.set_memory(actor+0xeb,b'\x08')
        if action==393:
            e.set_memory(TARGET+0xe9,b'\x06');e.set_memory(TARGET+0xeb,b'\x18')
        if action==396:
            e.set_memory(TARGET+0xe9,b'\x08');e.set_memory(TARGET+0x29,b'\x80');e.set_memory(TARGET+0x13,b'\x01')
        before=checkpoint(e,'declared-input',folder);prior=observe_owned(e,(actor,TARGET))
        # Act before Move, primary command set, its single mastered lesson.
        for key in (32,256,32,256,256):tap(e,key)
        selected=checkpoint(e,'targeting',folder)
        check('selected-native-command',word(selected,word(selected,0xf438)-0x02000000+20)==action)
        if action!=398:tap(e,starts[actor]['direction'])
        tap(e,256);preview=checkpoint(e,'preview',folder)
        check('actual-preview-action',half(preview,0xf3fc)==action)
        check('preview-does-not-pay',half(preview,actor+0x1c)==100)
        check('preview-does-not-apply-owned-effects',observe_owned(e,(actor,TARGET))==prior)
        tap(e,1);cancel=checkpoint(e,'cancelled',folder)
        check('cancel-keeps-resources',cancel[actor+0x18:actor+0x20]==before[actor+0x18:actor+0x20] and cancel[0x1940:0x1e70]==before[0x1940:0x1e70])
        check('cancel-keeps-owned-state',observe_owned(e,(actor,TARGET))==prior)
        # Restore the actual pre-cancel cursor; no final result is supplied.
        e.load(folder/'preview.state')
        if mode(preview)!=11:tap(e,256)
        confirmed=checkpoint(e,'confirmation',folder)
        check('native-final-confirmation',mode(confirmed)==11)
        e.set_memory(LOG+148,struct.pack('<II',1,3));tap(e,256,1)
        executed=None;rendered=set()
        for frames in range(3001):
            r=e.memory();rendered.add(hashlib.sha1(e.frame[0]).hexdigest())
            if word(r,LOG)==0x504c4159 and executed is None:executed=checkpoint(e,'native-result',folder)
            if frames%480==0:e.screenshot(folder/f'frame-{frames:04}.png')
            if executed is not None and frames>300 and observe['menu_visible'](e):break
            if frames<3000:e.run(1)
        check('native-result-and-menu-return',executed is not None and observe['menu_visible'](e))
        after=checkpoint(e,'after-playback',folder);actual_owned=observe_owned(e,(actor,TARGET))
        check('one-selected-native-execution',word(after,LOG+4)==1 and word(after,LOG+8)==action and word(after,LOG+24)==0x02000000+actor)
        check('once-MP-cost',half(after,actor+0x1c)==100-costs[action])
        check('no-payment-or-learning-side-effects',after[0x1940:0x1e70]==before[0x1940:0x1e70] and after[actor+0x40:actor+0xd0]==before[actor+0x40:actor+0xd0])
        check('no-rendering-reapplication',all(after[u+0x18:u+0x20]==executed[u+0x18:u+0x20] for u in (actor,TARGET)))
        check('native-rendering-progress',len(rendered)>3)
        if action==393:
            check('Soul-Etude-heal-and-four-cures',half(after,TARGET+0x18)==360 and not after[TARGET+0xe9]&6 and not after[TARGET+0xeb]&24)
        if action in (394,400):check('Protect-granted',bool(after[TARGET+0xeb]&2))
        if action in (395,400):check('Shell-granted',bool(after[TARGET+0xeb]&1))
        if action in (397,400):check('Regen-granted',bool(after[TARGET+0xe8]&8))
        if action in (394,395):check('owned-song-T2',((bytes.fromhex(actual_owned[TARGET]['state'])[10]>>(3 if action==395 else 0))&7)==2)
        if action==396:check('actual-Requiem-injury',0<half(after,TARGET+0x18)<200)
        if action==397:check('Angelsong-immediate-healing',half(after,TARGET+0x18)==280)
        if action==398:check('Hide-Invisible-and-Silence-retained',bool(after[actor+0xe9]&16) and bool(after[actor+0xeb]&8)==silenced)
        if action==399:check('Ballad-only-other-ally-MP',half(after,TARGET+0x1c)==40)
        if action==377:
            check('Updraft-real-height-difference',starts[actor]['heights'][0]-starts[actor]['heights'][1]>=2)
            check('Updraft-Move-and-conditional-Jump',actual_owned[TARGET]['updraft']==[1,1] and actual_owned[actor]['updraft']==[1,0])
            check('Updraft-native-mobility-updated',actual_owned[TARGET]['move']==prior[TARGET]['move']+1 and actual_owned[TARGET]['jump']==prior[TARGET]['jump']+1)
            check('Updraft-no-immediate-movement',all(after[u+0xf6:u+0xf8]==before[u+0xf6:u+0xf8] for u in (actor,TARGET)))
        previous=active(e)
        for key in (32,32,256,256):tap(e,key)
        menu(e,previous);checkpoint(e,'next-turn',folder)
        outcomes.append(dict(action=action,silenced=silenced,actor=actor,sample=str(folder),frames=frames,prior=prior,after=actual_owned,formation=starts[actor]));save_report()
    except BaseException:
        e.save(folder/'failure.state');e.screenshot(folder/'failure.png');(folder/'failure.ram').write_bytes(e.memory());save_report();raise
    finally:e.close()

for selected in [o for o in outcomes if o['action'] in (394,395,400,377) and not any(c['action']==o['action'] for c in cold)]:
    action=selected['action'];actor=selected['actor'];case=('cold',action);source=pathlib.Path(selected['sample']);folder=OUT/(str(action)+'-cold');folder.mkdir()
    e=E(TEST_ROM)
    try:
        e.load(source/'next-turn.state');expected=e.memory();expected_owned=observe_owned(e,(actor,TARGET));expected_actor=active(e)
        for key in (1,8,16,256,256):tap(e,key)
        old=e.memory(0);tap(e,256,300);saved=e.memory(0)
        check('native-suspend-save',saved!=old);(folder/'suspended.sav').write_bytes(saved)
    finally:e.close()
    e=E(ROM)
    try:
        e.set_memory(0,saved,0);e.run(3600)
        for key,wait in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):tap(e,key,wait)
        menu(e);actual=e.memory();restored=observe_owned(e,(actor,TARGET))
        check('cold-owned-records-and-native-mobility',restored==expected_owned)
        check('cold-HP-MP-statuses',all(actual[u+0x18:u+0x20]==expected[u+0x18:u+0x20] and actual[u+0xe8:u+0xf0]==expected[u+0xe8:u+0xf0] for u in (actor,TARGET)))
        check('cold-AP-inventory',actual[0x1940:0x1e70]==expected[0x1940:0x1e70])
        check('cold-turn-preserved',active(e)==expected_actor)
        check('cold-roots-clear',actual[0x3ff44:0x3ff4c]==bytes(8))
        e.save(folder/'cold-resumed.state');e.screenshot(folder/'cold-resumed.png');(folder/'cold-resumed.ram').write_bytes(actual)
        # Check target-owned T2 through exactly two actual subsequent turns.
        turns=[];target_ends=0
        if action in (394,395,377):
            for n in range(36):
                previous=active(e)
                for key in (32,32,256,256):tap(e,key)
                menu(e,previous)
                if previous==0x02000000+TARGET:target_ends+=1
                current=observe_owned(e,(TARGET,))[TARGET];state=bytes.fromhex(current['state'])
                timer=(state[18]>>1)&3 if action==377 else (state[10]>>(3 if action==395 else 0))&3
                check('target-turn-only-T2-expiry',timer==2-target_ends)
                if action==377:
                    check('Jump-timer-expires-with-Move',((state[18]>>4)&3)==2-target_ends)
                    check('native-mobility-tracks-expiry',current['move']==selected['prior'][TARGET]['move']+int(target_ends<2) and current['jump']==selected['prior'][TARGET]['jump']+int(target_ends<2))
                turns.append(dict(actor=previous,targetEnds=target_ends,state=current))
                if target_ends==2:break
            check('reached-second-target-turn',target_ends==2)
            e.save(folder/'expired.state');e.screenshot(folder/'expired.png')
        cold.append(dict(action=action,saveSha1=hashlib.sha1(saved).hexdigest(),before=expected_owned,restored=restored,turns=turns));save_report()
    except BaseException:
        e.save(folder/'failure.state');e.screenshot(folder/'failure.png');(folder/'failure.ram').write_bytes(e.memory());save_report();raise
    finally:e.close()
print(json.dumps(save_report(True),indent=2))
