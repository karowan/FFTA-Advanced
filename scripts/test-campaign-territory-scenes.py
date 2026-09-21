"""Representative earned mission selection, original result scenes and placement.

Earlier receipts are reused from the authenticated connected progression proof.
Map ownership, placements and story stage are declared milestone inputs. Native services
complete the short remaining prefix and accept the target mission. A one-time
observer records the original world-selected target scene. Ordinary map inputs
travel to the accepted mission; no scene or event entry is substituted. Only hostile HP is zeroed after
deployment. Original results must earn the receipt and next story stage, then
ordinary map inputs must place Quiet Sands; the late result must create
Ambervale at its fixed position. Its real save and departure must enter scene93. No victory, receipt,
scene result or new territory placement is injected.
"""
import pathlib,hashlib
SOURCE=pathlib.Path(__file__).resolve();ROOT=SOURCE.parents[1];SCOPE=__doc__
helper=ROOT/'scripts/test-campaign-ending-scenes.py';helper_bytes=helper.read_bytes()
assert hashlib.sha1(helper_bytes).hexdigest()=='e5cb244449f183ef3feb92c653df421faeea0c6a'
head=helper_bytes.decode().split('try:\n    e=E(TEST_ROM)')[0]
head=head.replace("'ending-scenes-'","'territory-scenes-'")
head=head.replace('L[0]=0; L[1]++; scene=101;',
                  'if(scene==L[40]) { L[0]=0; L[1]++; L[8]=scene; }')
head=head.replace('if(op[1]==14) { L[5]++; L[6]=(unsigned)op; L[7]=(unsigned)context; }',
                  'if(op[1]==3) { L[4]++; L[6]=(unsigned)op; L[7]=(unsigned)context; }')
head=head.replace('creditOps=words[4]','battleStarts=words[4]')
exec(compile(head,str(helper),'exec'));__doc__=SCOPE
import ctypes as C,sys
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
RETURN,STACK=0x08000100,0x03006800
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
menus=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
progress=ROM.parent/'campaign-progression-20260917T083905.312061Z'
raw=(progress/'report.json').read_bytes();assert sha(raw)=='8f5325761e1604d2a0c61af665014570cc9eec1f'
proof=json.loads(raw);assert proof['passed'] and proof['romSha1']==meta['romSha1']
for a,b in ((0x9b1000,0x9b1b20),(0x9b5500,0x9b6190),(0x563a70,0x563bb4),(0x122e50,0x122f24)):
    assert image[a:b]==clean[a:b],('Original campaign range changed',hex(a),hex(b))
cases=[];case=None

def native():
    m=ARM(patched,C.string_at(*e.maps[0x03000000]));m.put(0x02000000,e.memory());return m

def queue(m):
    node=m.word(0x020028c8);result={}
    while node:
        assert 0x020025c8<=node<0x020028c8 and len(result)<64
        ptr=m.word(node);mid=int.from_bytes(m.read(ptr,2),'little')&1023
        assert mid not in result;result[mid]=ptr;node=m.word(node+8)
    return result

def flag(data,index):return bool(data[0x1f70+index//8]&(1<<(index&7)))

def route_to(tile):
    m=native();x=m.call(0x08035a20,tile-1)+6;y=m.call(0x08035a44,tile-1)+4
    route=[]
    for _ in range(600):
        cx,cy=struct.unpack_from('<HH',e.memory(),0x2c16)
        if abs(cx-x)<=2 and abs(cy-y)<=2:break
        key=(128 if cx<x else 64) if abs(cx-x)>2 else (32 if cy<y else 16)
        route.append([cx,cy,key]);e.run(1,key)
    else:raise AssertionError('Native map cursor route exceeded bound')
    inputs.append(dict(case=case['mission'],tile=tile,route=route));e.run(30)

def exit_input():
    m=native();count=m.call(0x08099cdc,m.word(0x0200f4b0),0x02008000)
    actors=[m.word(m.word(0x02008000+4*i)) for i in range(count)];before=e.memory()
    enemies=[p for p in actors if 0x02002fc4<=p<0x02003c24 and (p-0x02002fc4)%264==0 and before[p-0x02000000+0x29]&128]
    check(0<len(enemies)<=12 and count<=24,'Native hostile deployment:'+str(case['mission']))
    for p in enemies:e.set_memory(p-0x02000000+0x18,bytes(2))
    after=e.memory()
    check(after[0x80:0x1940]==before[0x80:0x1940] and all(after[p-0x02000000:p-0x02000000+264]==before[p-0x02000000:p-0x02000000+264] for p in actors if p not in enemies),'Controlled defeat preserves nonhostiles')
    case['hostiles']=[hex(p) for p in enemies];capture(str(case['mission'])+'-exit-input')

def finish_final_entry():
    before=e.memory(0);capture('final-save-offer')
    tap(256,180);tap(256,180);capture('final-save-overwrite-question')
    tap(64,60);tap(256,300);capture('final-save-written')
    check(e.memory(0)!=before and flag(e.memory(),75),'Original pre-final save writes flash and sets arrival gate75')
    tap(1,180);capture('final-save-closed')
    check(native().call(0x08036350,e.memory()[0x1f69])==30,'Current region is newly created Ambervale')
    # Selecting a different destination invokes native D1A18 before travel.
    # Selecting Ambervale again only opens its save question again.
    route_to(3);tap(256,1200);capture('native-departure-event')
    for step in range(150):
        obs=observe()
        if 93 in obs['scenes'] and obs['battleStarts']==2:break
        tap(256,180)
    else:raise AssertionError('Earned Royal Valley departure did not reach deployment')
    check(flag(e.memory(),572) and not flag(e.memory(),793) and not flag(e.memory(),54),
          'Original final scene entered without premature final completion or clear flag')
    check(obs['fired']==1,'Only original Over The Hill observer marker fired; no scene or event substituted')
    capture('earned-final-deployment');case['finalEntry']=obs

try:
    for target,stage,story,prefix,loc,award,expected in [
        (19,2,21,[319,14,27,15,16,320,17,321,18],21,20,[63,64]),
        (25,3,29,[20,322,21,22,323,23,325,24],24,30,[89,92])]:
        case=dict(mission=target,stageInput=story,earlierReceiptsStage=stage,prefix=prefix,location=loc,award=award);cases.append(case)
        e=E(TEST_ROM);e.set_memory(0,seed,0);e.run(3600)
        for key,wait in ((8,180),(256,60),(256,60),(256,180)):tap(key,wait)
        entry=next(row for row in proof['milestones'] if row['stage']==stage)
        stored=(progress/entry['ram']).read_bytes();assert sha(stored)==entry['ramSha1']
        # Reuse only authenticated receipt flags. Earlier placements/stage are
        # explicit boundary inputs, leaving the next award unplaced.
        e.set_memory(0x1f70,stored[0x1f70:0x2030]);e.set_memory(0x2190,bytes((story,story)))
        for location in range(1,31):
            at=0x2cc0+12*(location-1)
            e.set_memory(at+1,bytes((0 if location==award else 1,)))
            e.set_memory(at+3,bytes((0 if location==award else 30 if award==30 and location==9 else location,)))
        e.set_memory(0x2e58,b'\x02' if award==30 else b'\x03');e.set_memory(0x2fba,b'\x01')
        for slot in range(24):e.set_memory(0x80+264*slot+0x18,struct.pack('<HH',999,999))
        m=native()
        for mid in prefix+[target]:
            m.call(0x080cfcd0,0);entries=queue(m)
            check(mid in entries,'Native mission eligible:'+str(mid));ptr=entries[mid]
            m.call(0x080d0b48,ptr,0,0,0)
            if mid!=target:m.call(0x080d1e70,ptr,1)
        after_services=m.read(0x02000000,0x40000)
        before_services=e.memory()
        case.setdefault('nativeServiceChanges',[]).append([hex(i) for i in range(0x40000) if before_services[i]!=after_services[i]])
        e.set_memory(0,after_services)
        check(not flag(e.memory(),target+767),'Target not already complete')
        check(native().call(0x08036330,award)==0,'Award territory initially unplaced')
        e.set_memory(LOG,bytes(168));e.set_memory(LOG,struct.pack('<I',0x53434e45))
        e.set_memory(LOG+160,struct.pack('<II',expected[0],loc));capture(str(target)+'-prepared')
        route_to(loc);tap(256,1200);capture(str(target)+'-destination')
        seen=[];phase=0;exited=False
        for step in range(450):
            obs=observe()
            if obs['scenes']!=seen:
                seen=obs['scenes'];capture(str(target)+'-scene-'+str(obs['currentScene']));print(json.dumps(dict(mission=target,step=step,observation=obs)),flush=True)
            if e.memory()[0x2190]==story+1 and flag(e.memory(),target+767):
                e.run(600);capture(str(target)+'-result-world');break
            if step==60:check(expected[0] in seen,'Native earned world event enters original scene')
            if obs['battleStarts']:
                phase+=1
                if not exited and (phase==8 or menus['menu_visible'](e)):
                    exit_input();exited=True
                if menus['menu_visible'](e):
                    for key in (32,32,256,256):tap(key,120)
                    e.run(1800);continue
                if phase in (8,16,24,32):tap(8,180)
            tap(256,180)
        else:raise AssertionError('Result scene/receipt not reached within bound')
        check(exited and all(s in seen for s in expected),'Representative original battle/result scene chain')
        check(obs['fired']==1 and obs['saveState']==expected[0],'Native world selector chose accepted target event')
        check(e.memory()[0x2190]==story+1 and flag(e.memory(),target+767),'Original results earn story stage and receipt')
        if target==19:
            for _ in range(4):tap(1,120)
            m=native();tiles=[t for t in range(1,31) if not m.call(0x08036350,t)]
            check(len(tiles)==1,'Declared preceding placements leave one native tile')
            route_to(tiles[0]);tap(256,300);capture(str(target)+'-placement-selected');tap(256,600)
            check(native().call(0x08036330,award)==tiles[0],'Original result awards and inputs place next territory')
        else:
            tiles=[native().call(0x08036330,30)]
            check(tiles==[9],'Original Over The Hill result creates Royal Valley at fixed tile9')
            check(native().call(0x08036350,9)==30,'Native map resolves new Royal Valley territory')
            m=native();placed=[m.call(0x08036330,i) for i in range(1,31)]
            check(len(set(placed))==30 and sorted(placed)==list(range(1,31)),'Native final territory has a unique map position')
        capture(str(target)+'-placed');case['observation']=observe();case['placedTile']=tiles[0]
        if target==25:
            m=native();m.call(0x080cfcd0,0);entries=queue(m)
            check(26 in entries and not flag(e.memory(),793),'Real Over The Hill result makes Royal Valley eligible')
            m.call(0x080d0b48,entries[26],0,0,0)
            e.set_memory(0,m.read(0x02000000,0x40000))
            for _ in range(4):tap(1,120)
            route_to(tiles[0]);tap(256,1200)
            finish_final_entry()
        e.close();e=None
except BaseException as error:
    import traceback;traceback.print_exc();failure=repr(error)
    if e is not None:capture('failure')
finally:
    if e is not None:e.close()
report=dict(passed=failure is None,scope=SCOPE,romSha1=meta['romSha1'],instrumentedSha1=sha(patched),sourceSha1=sha(SOURCE.read_bytes()),
    helperSha1=sha(helper_bytes),progressionProofSha1=sha(raw),checks=checks,cases=cases,inputs=inputs,captures=captures,failure=failure)
(OUT/'script.py').write_bytes(SOURCE.read_bytes());(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(passed=report['passed'],checks=len(checks),failure=failure,report=str(OUT/'report.json'))))
assert failure is None,failure
