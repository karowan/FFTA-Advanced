"""Fixed player inputs through Forbidden Dance selection, cast and rendering.

Uses a real Viera sprite/turn and isolated native battle save. Controlled inputs
are job/learning, formation, initial statuses and fixed cast seeds. Status-roll
outcomes and action results always come from the native engine.
"""
import pathlib,sys
from datetime import datetime,timezone
SILENCED_SMOKE='--silenced-smoke' in sys.argv
ROOT=pathlib.Path(__file__).resolve().parents[1]
support=(ROOT/'scripts/test-integrated-reaction-playback.py').read_text().split('for lesson,job,race,weapon,hidden in cases:')[0]
support=support.replace("OUT=LAB/'reaction-playback'","OUT=LAB/'dancer-choice-playback'")
if SILENCED_SMOKE:
    support=support.replace("FIX=LAB/'fixture'","FIX=LAB/'fixture-two-geomancers'")
    name='dancer-silenced-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    support=support.replace("OUT=LAB/'dancer-choice-playback'",'OUT=LAB/'+repr(name))
support=support.replace('log[0]=0x504c4159;', 'log[33]=mode;log[34]=(unsigned)out;log[0]=0x504c4159;')
exec(compile(support,'<shared deterministic playback>','exec'))
ACTOR,TARGET,SECOND=0x5a8,0x33e4,0x2fc4
lesson=next(l for l in registry['lessons'] if l['id']=='DNC-A6')
index=next(o['abilityIndex'] for o in lesson['owners'] if o['race']==4)
def mode(e):
    r=e.memory();return r[word(r,0xf438)-0x02000000+4]
def checkpoint(e,label,folder):
    r=capture(e,label,folder)
    check('native-code-intact',C.string_at(*e.maps[0x03000000])[CODE_FIRST:CODE_LAST]==NATIVE_CODE)
    return r

e=E(TEST_ROM)
try:
    e.load(FIX/'battle-ready.state');e.run(1);menu(e);fixed_giza_formation(image,e)
    check('real-Viera',e.memory()[ACTOR+6]==4)
    for offset in (5,7,0x35):e.set_memory(ACTOR+offset,b'\x7c')
    e.set_memory(ACTOR+8,b'\x00');e.set_memory(ACTOR+0x36,bytes(2))
    e.set_memory(ACTOR+0x40,bytes(0x90));e.set_memory(ACTOR+0x40+index,b'\xff')
    e.set_memory(ACTOR+0x2a,bytes(10));e.set_memory(ACTOR+0x3a,bytes(2))
    for unit in (ACTOR,TARGET,SECOND):
        e.set_memory(unit+0x18,struct.pack('<4H',500,500,99,100));e.set_memory(unit+0xe8,bytes(8))
        e.set_memory(unit+0x20,struct.pack('<4H',70,40,40,40))
    wrappers=from_emulator(image,e)
    # Keep the active Viera at her real turn-start tile. Relocate the two
    # opponents and clear their two destination tiles before native movement.
    for unit,x,y,height in ((ACTOR,0,14,16),(TARGET,1,13,32),(SECOND,1,14,16),(0x290,2,12,32),(0x398,3,12,32)):
        e.set_memory(unit+0xf6,bytes((x,y)));e.set_memory(wrappers[unit]+8,struct.pack('<3H',x*32+16,height,y*32+16))
    for turn in range(12):
        if active(e)==0x02000000+ACTOR:break
        previous=active(e)
        for key in (32,32,256,256):tap(e,key)
        menu(e,previous)
    check('native-Viera-turn',active(e)==0x02000000+ACTOR)
    # Encounter initiative can allow an enemy action before the Viera's turn.
    # Establish the declared scenario at its input boundary, after that setup
    # interval. Subsequent movement, occupancy and combat are native results.
    wrappers=from_emulator(image,e)
    for unit,x,y,height in ((ACTOR,0,14,16),(TARGET,1,13,32),(SECOND,1,14,16),(0x290,2,12,32),(0x398,3,12,32)):
        e.set_memory(unit+0xf6,bytes((x,y)));e.set_memory(wrappers[unit]+8,struct.pack('<3H',x*32+16,height,y*32+16))
    for unit in (ACTOR,TARGET,SECOND):
        e.set_memory(unit+0x18,struct.pack('<4H',500,500,100,100));e.set_memory(unit+0xe8,bytes(8))
    check('declared-target-start',e.memory()[TARGET+0xf6:TARGET+0xf8]==bytes((1,13)))
    check('unoccupied-Move-destination',all(e.memory()[u+0xf6:u+0xf8]!=bytes((0,13)) for u in wrappers))
    e.set_memory(0x3ff44,bytes(8)+b'\xd7'*0xb4);e.set_memory(LOG,bytes(160))
    if SILENCED_SMOKE:e.set_memory(ACTOR+0xeb,b'\x08')
    checkpoint(e,'start',OUT)
finally:e.close()

# Actual selected player casts; every seed is retained, including misses.
selected=[(c,b,s) for c,b in enumerate((10,27,9,28),1) for s in (0,3,18) if not SILENCED_SMOKE or c==1]
for choice,bit,seed in selected:
    case=('Forbidden-player',choice,seed);folder=OUT/str(choice)/str(seed);folder.mkdir(parents=True,exist_ok=True);e=E(TEST_ROM)
    try:
        e.load(OUT/'start.state');e.run(1)
        # Native movement refreshes targeting after the declared fixture
        # formation. Then Act is the turn menu's selected remaining command.
        for key in (256,16,256):tap(e,key)
        menu(e)
        moved=checkpoint(e,'native-movement',folder)
        # Native movement updates the wrapper first; A433C later synchronizes
        # unit F6/F7. Observe the live position, not those deferred unit bytes.
        w=wrappers[ACTOR]
        check('native-movement-to-declared-tile',(half(moved,w+8)//32,half(moved,w+12)//32)==(0,13))
        for key in (256,32,256):tap(e,key)
        checkpoint(e,'choices',folder)
        check('native-command-mode',mode(e) in (6,7,8))
        for _ in range(choice-1):tap(e,32)
        tap(e,256);checkpoint(e,'targeting',folder)
        r=e.memory();manager=word(r,0xf438)-0x02000000
        check('player-selected-choice',half(r,manager+16)==choice)
        # Right selects the center at1,13. Confirm its cross preview, then
        # confirm the recipients to reach the native final cast prompt.
        for key in (128,256):tap(e,key)
        preview=checkpoint(e,'recipient-preview',folder)
        check('preview-selected-action',half(preview,0xf3fc)==406)
        check('preview-selected-status',half(preview,0xf3fe)==choice)
        tap(e,256)
        before=checkpoint(e,'confirmation',folder)
        check('native-final-confirmation',mode(e)==11)
        if SILENCED_SMOKE:check('player-caster-still-Silenced',bool(before[ACTOR+0xeb]&8))
        check('no-premature-execution',word(before,LOG+4)==0)
        e.set_memory(LOG+148,struct.pack('<II',1,seed));tap(e,256,1)
        rendered=set();executed=None
        for frames in range(0,1801,12):
            r=e.memory();rendered.add(hashlib.sha1(e.frame[0]).hexdigest())
            if word(r,LOG)==0x504c4159 and executed is None:executed=checkpoint(e,'native-result',folder)
            if frames%120==0:e.screenshot(folder/f'frame-{frames:04}.png')
            if frames<1800:e.run(12)
        check('native-cast-completed',executed is not None)
        check('one-Forbidden-cast',word(executed,LOG+4)==1 and word(executed,LOG+8)==406)
        check('native-caster-identity',word(executed,LOG+24)==0x02000000+ACTOR)
        check('native-choice-reached-executor',word(executed,LOG+132)==choice)
        out=word(executed,LOG+136)-0x02000000
        check('native-result-storage',0<=out<0x40000-0x2c4)
        check('native-selected-center',executed[out+10:out+12]==bytes((1,13)))
        recipients=set()
        for i in range(executed[out+0x2c0]):
            # Native recipient rows are0x2C bytes (see execution-scope and
            # reaction-queue consumers), independent of the0x2C4 object size.
            wrapper=word(executed,out+0x20+0x2c*i)-0x02000000
            check('native-recipient-wrapper',0<=wrapper<0x40000-4)
            recipients.add(word(executed,wrapper)-0x02000000)
        check('native-cross-two-recipients',recipients=={TARGET,SECOND})
        check('once-only-MP-cost',half(before,ACTOR+0x1c)-half(executed,ACTOR+0x1c)==14)
        after=checkpoint(e,'after-playback',folder)
        check('real-rendering',len(rendered)>3)
        for unit in (TARGET,SECOND):
            check('no-wrong-status',all(not(after[unit+0xe8+b//8]&(1<<(b%8))) for b in (10,27,9,28) if b!=bit))
            check('no-target-HP-damage',half(after,unit+0x18)==half(before,unit+0x18))
        check('inventory-AP-unchanged',after[0x1940:0x1e70]==before[0x1940:0x1e70])
        check('caster-learning-unchanged',after[ACTOR+0x40:ACTOR+0xd0]==before[ACTOR+0x40:ACTOR+0xd0])
        check('no-self-ailment',after[ACTOR+0xe8:ACTOR+0xf0]==before[ACTOR+0xe8:ACTOR+0xf0])
        check('rendering-no-extra-MP',half(after,ACTOR+0x1c)==half(executed,ACTOR+0x1c))
        outcomes.append(dict(choice=choice,seed=seed,bit=bit,applied=[bool(after[u+0xe8+bit//8]&(1<<(bit%8))) for u in (TARGET,SECOND)],frames=len(rendered)))
        previous=active(e);tap(e,256,900);menu(e,previous);checkpoint(e,'next-turn',folder)
    finally:e.close()
for choice in sorted({c for c,b,s in selected}):
    for target in range(2):check('nonvacuous-chosen-ailment-'+str((choice,target)),any(o['choice']==choice and o['applied'][target] for o in outcomes))
report=dict(passed=True,romSha1=meta['romSha1'],instrumentedSha1=hashlib.sha1(instrumented).hexdigest(),checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,
            limits=['Does not prove AI choice search or all law/immunity combinations.'])
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
