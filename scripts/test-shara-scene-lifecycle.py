"""Native postgame town arrival, Shara scene, full clan and vacancy acceptance.

Input is an authenticated actual clear save. Original late-story stage31 and
completed dispatch381 are declared eligibility inputs. Native town selection
must queue scene129; no scene result, candidate or acceptance flag is injected.
A declared empty slot23 is compared with the same full24-slot clan. Fixed
buttons drive scene/offer/cancel/accept/save; unmodified cold loading verifies
persistence. This does not claim campaign acquisition of the input conditions.
"""
import pathlib,hashlib
SOURCE=pathlib.Path(__file__).resolve();ROOT=SOURCE.parents[1];SCOPE=__doc__
helper=ROOT/'scripts/test-campaign-ending-scenes.py';helper_bytes=helper.read_bytes()
assert hashlib.sha1(helper_bytes).hexdigest()=='e5cb244449f183ef3feb92c653df421faeea0c6a'
head=helper_bytes.decode().split('try:\n    e=E(TEST_ROM)')[0]
head=head.replace("'ending-scenes-'","'shara-scene-'")
head=head.replace('(0x9b7024,0x9b83cc)','(0x9ba680,0x9babfb),(0x1222c8,0x12237c),(0x123294,0x1232a4)')
head=head.replace('L[0]=0; L[1]++; scene=101;','if(scene==129) { L[0]=0; L[1]++; }')
head=head.replace('L[4]++;\n    return ((unsigned (*)(void *,const unsigned char *))0x08123a61u)(context,op);',
    'L[4]++; L[6]=(unsigned)op;\n    return ((unsigned (*)(void *,const unsigned char *))0x08123295u)(context,op);')
head=head.replace('(0x3a7ee4+0x62*6+2,0x08123a61,','(0x3a7ee4+0x36*6+2,0x08123295,')
head=head.replace('creditOps=words[4]','recruitOps=words[4]')
exec(compile(head,str(helper),'exec'));__doc__=SCOPE
clear_source=ROM.parent/'ending-scenes-20260917T110459.056443Z'
clear_report=(clear_source/'report.json').read_bytes();assert sha(clear_report)=='13e138e2c9fc9ab977c4087afb71e293959bbd09'
cleared=(clear_source/'cleared.sav').read_bytes();assert sha(cleared)=='f2afe32c0c9d1edd94f362a9aad547b70f173594'
import sys
cases=[];case=None;retained=None;prepared_folder=OUT
from PIL import Image
world_path=clear_source/'uninstrumented-cold.png'
world_capture=next(c for c in json.loads(clear_report)['captures'] if c['label']=='uninstrumented-cold')
assert sha(world_path.read_bytes())==world_capture['files'][world_path.name]
world_image=Image.open(world_path).resize((240,160),Image.Resampling.NEAREST).convert('RGB')
# Original Law-tab glyph and outline; exclude the changing map background.
world_points=[(x,y,world_image.getpixel((x,y))) for y in range(11,19) for x in range(8,24)
              if world_image.getpixel((x,y)) in ((8,8,0),(246,242,230))]
assert len(world_points)>40

def world_visible():
    if e.frame is None:return False
    raw,w,h,pitch,pixel=e.frame
    if (w,h)!=(240,160):return False
    for x,y,expected in world_points:
        if pixel==1:
            pos=y*pitch+x*4;actual=tuple(raw[pos:pos+3][::-1])
        else:
            pos=y*pitch+x*2;v=int.from_bytes(raw[pos:pos+2],'little')
            if pixel==2:actual=((v>>11&31)*255//31,(v>>5&63)*255//63,(v&31)*255//31)
            else:actual=((v>>10&31)*255//31,(v>>5&31)*255//31,(v&31)*255//31)
        if actual!=expected:return False
    return True

def flag(index):return bool(e.memory()[0x1f70+index//8]&(1<<(index&7)))

def members():return [slot for slot in range(24) if e.memory()[0x84+slot*264]==12]

def verify_offer(obs):
    check(obs['scenes']==[129] and obs['recruitOps']==1,'Original town selection enters Shara scene:'+case)
    check(obs['saveOpcode']=='0x89ba91d','Original scene129 recruit instruction:'+case)
    check(e.memory()[0x3b20]==12 and not flag(603) and not members(),'Actual Shara candidate before acceptance:'+case)

def reach_offer():
    for step in range(150):
        tap(256,180)
        obs=observe()
        if obs['recruitOps']:
            e.run(360);capture(case+'-offer')
            verify_offer(obs)
            return
        if step in (10,40):capture(case+'-scene-'+str(step))
    raise AssertionError('Native Shara offer did not appear within28800frames:'+case)

try:
    if '--resume-accepted' in sys.argv:
        folder=ROM.parent/'shara-scene-20260917T112850.429399Z'
        raw=(folder/'report.json').read_bytes();assert sha(raw)=='74de8db0fdcc773bbd96b21329e6e4f4f7c17e1f'
        old=json.loads(raw);assert old['romSha1']==meta['romSha1'] and old['instrumentedSha1']==sha(patched)
        cap=next(c for c in old['captures'] if c['label']=='accepted')
        for name,digest in cap['files'].items():assert sha((folder/name).read_bytes())==digest
        checks.extend(old['checks']);cases.extend(old['cases'])
        retained=dict(report=str(folder/'report.json'),sha1=sha(raw),completedChecks=len(checks))
        case='vacancy';e=E(TEST_ROM);e.load(folder/'accepted.state');e.set_memory(0,cleared,0)
        check(flag(603) and members()==[23],'Authenticated accepted scene endpoint restored')
        capture('retained-accepted')
    else:
        e=E(TEST_ROM);e.set_memory(0,cleared,0);e.run(3600)
        for key,wait in ((8,180),(256,60),(256,60),(256,180)):tap(key,wait)
        check(flag(54) and not flag(603),'Actual clear save loaded without prior Shara acceptance')
        check(owned(e.memory())==prior['profiles']['0'],'Authenticated full expansion profile loaded')
        # Eligibility input only; do not set the queued scene or a recruit result.
        p=0x1f70+1148//8;e.set_memory(p,bytes((e.memory()[p]|(1<<(1148&7)),)))
        e.set_memory(0x2190,bytes((31,31)))
        e.set_memory(LOG,bytes(168));e.set_memory(LOG,struct.pack('<I',0x53434e45))
        capture('prepared-world');before=owned(e.memory())
        case='full'
        if '--resume-offer' in sys.argv:
            prepared_folder=ROM.parent/'shara-scene-20260917T112601.593293Z'
            raw=(prepared_folder/'report.json').read_bytes();assert sha(raw)=='c3f62ac5cf55a7dc127bbad0cc9eb845093bb31f';old=json.loads(raw)
            assert old['romSha1']==meta['romSha1'] and old['instrumentedSha1']==sha(patched)
            for label in ('prepared-world','full-offer'):
                cap=next(c for c in old['captures'] if c['label']==label)
                for name,digest in cap['files'].items():assert sha((prepared_folder/name).read_bytes())==digest
            before=owned((prepared_folder/'prepared-world.ram').read_bytes())
            e.load(prepared_folder/'full-offer.state');e.set_memory(0,cleared,0)
            retained=dict(report=str(prepared_folder/'report.json'),sha1=sha(raw))
            verify_offer(observe());capture('retained-full-offer')
        else:reach_offer()
        offer_before=owned(e.memory())
        cases.append(dict(case='full-offer-generation',changedFields=[k for k in before if before[k]!=offer_before[k]],
            before=before,after=offer_before))
        # Refuse the full-clan offer; no existing member may be displaced.
        for step in range(30):
            tap(1 if step<3 else 256,180)
            if flag(621):break
        capture('full-return')
        check(not flag(603) and not members(),'Full clan does not accept Shara')
        check(owned(e.memory())==offer_before,'Full-clan cancellation preserves the entire offered profile')
        check(flag(621),'Native unaccepted scene sets its retry gate')
        cases.append(dict(case=case,observation=observe(),retry=True))
        case='vacancy';e.load(prepared_folder/'prepared-world.state');e.set_memory(0,cleared,0)
        e.set_memory(0x80+23*264,bytes(264));e.set_memory(0x1b40+23*34,bytes(34));e.set_memory(0x1e80+23,bytes(1))
        capture('vacancy-input');reach_offer();before=owned(e.memory())
        for step in range(30):
            tap(256,180)
            if flag(603):break
        capture('accepted')
        check(flag(603) and members()==[23],'Original acceptance assigns Shara to slot23 and records ownership')
        after=owned(e.memory())
        check(after['roster'][:23*264*2]==before['roster'][:23*264*2],'All23 existing native records retained')
        check(after['extendedAP']==before['extendedAP'] and after['preferences']==before['preferences'],
              'New recruit initializes only its vacant expansion record')
    for step in range(120):
        if world_visible():break
        tap(256,180)
    else:raise AssertionError('Recruit scene did not return to the world map within23040frames')
    xy=e.memory()[0x2c16:0x2c1a];e.run(4,128);e.run(20)
    check(e.memory()[0x2c16:0x2c1a]!=xy,'Original world cursor responds after recruitment')
    capture('accepted-world');saved_profile=owned(e.memory())
    for key,wait in ((8,180),(16,180),(256,180),(256,180),(256,180),(64,60),(256,300)):tap(key,wait)
    accepted=e.memory(0);capture('saved')
    check(accepted!=cleared,'Native save writes accepted Shara')
    e.close();e=E(ROM);e.set_memory(0,accepted,0);e.run(3600)
    for key,wait in ((8,180),(256,60),(256,60),(256,180)):tap(key,wait)
    capture('uninstrumented-cold')
    check(flag(603) and members()==[23],'Unmodified cold Continue preserves accepted Shara and receipt')
    check(owned(e.memory())==saved_profile,'Cold load preserves all24 native/expansion records')
    check((clear_source/'cleared.sav').read_bytes()==cleared,'Reusable clear save unchanged')
    cases.append(dict(case=case,savedSha1=sha(accepted),slot=23))
except BaseException as error:
    import traceback
    traceback.print_exc();failure=repr(error)
    if e is not None:capture('failure')
finally:
    if e is not None:e.close()
report=dict(passed=failure is None,scope=SCOPE,romSha1=meta['romSha1'],instrumentedSha1=sha(patched),
    sourceSha1=sha(SOURCE.read_bytes()),helperSha1=sha(helper_bytes),assertions=len(checks),checks=checks,
    cases=cases,inputs=inputs,captures=captures,failure=failure,clearSaveSha1=sha(cleared),retained=retained)
(OUT/'script.py').write_bytes(SOURCE.read_bytes());(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(passed=report['passed'],checks=len(checks),failure=failure,report=str(OUT/'report.json'))))
assert failure is None,failure
