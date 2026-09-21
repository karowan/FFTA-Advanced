"""Native Royal Valley event, final battle exits and entry to scene101.

Declared input: one native event26 dispatch from an ordinary disposable save,
with999 current/maximum HP for the24 party slots before deployment.
Enemy HP zero after native deployment is a controlled battle-exit precondition,
not a claim of winning these battles through combat. Original deployment,
victory detection, scene transitions and result dialogs execute unchanged.
Stop at scene101 and reuse the accepted ending suffix. Earlier campaign
eligibility and map placement are outside this test.
"""
import pathlib
SOURCE=pathlib.Path(__file__).resolve();ROOT=SOURCE.parents[1];SCOPE=__doc__
helper=ROOT/'scripts/test-campaign-ending-scenes.py'
import hashlib
helper_bytes=helper.read_bytes()
assert hashlib.sha1(helper_bytes).hexdigest()=='e5cb244449f183ef3feb92c653df421faeea0c6a'
head=helper_bytes.decode().split('try:\n    e=E(TEST_ROM)')[0]
assert head!=helper_bytes.decode()
head=head.replace("'ending-scenes-'","'final-battle-bridge-'")
head=head.replace('(0x9b7024,0x9b83cc)','(0x9b6184,0x9b83cc),(0x9c04,0x9c94),(0x563a70+26*12,0x563a70+27*12)')
head=head.replace('L[0]=0; L[1]++; scene=101;',
    'L[0]=0; L[1]++; ((void (*)(const void *,unsigned))0x08009c19u)((const void *)0x08563ba8u,30); return 0;')
head=head.replace('if(op[1]==14) { L[5]++; L[6]=(unsigned)op; L[7]=(unsigned)context; }',
    'if(op[1]==3) { L[4]++; L[6]=(unsigned)op; L[7]=(unsigned)context; }')
head=head.replace('creditOps=words[4]','battleStarts=words[4]')
exec(compile(head,str(helper),'exec'));__doc__=SCOPE
import ctypes as C
import sys
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
RETURN,STACK=0x08000100,0x03006800
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
menus=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
exits=[];seen=[];last_battle=0;phase_steps=0;retained=None

def prepare_exit(current):
    m=ARM(patched,C.string_at(*e.maps[0x03000000]));m.put(0x02000000,e.memory())
    manager=m.word(0x0200f4b0);count=m.call(0x08099cdc,manager,0x02008000)
    pointers=[m.word(m.word(0x02008000+4*i)) for i in range(count)]
    before=e.memory()
    enemies=[p for p in pointers if 0x02002fc4<=p<0x02003c24 and (p-0x02002fc4)%264==0
             and before[p-0x02000000+0x29]&128]
    check(len(enemies)==(6 if last_battle==1 else 3) and count<=24,
          'Native deployment exposes only hostile combatants:'+str(last_battle))
    row=dict(battle=last_battle,scene=current['currentScene'],count=count,
        enemies=[dict(address=hex(p),hp=int.from_bytes(before[p-0x02000000+0x18:p-0x02000000+0x1a],'little')) for p in enemies])
    for p in enemies:e.set_memory(p-0x02000000+0x18,bytes(2))
    check(e.memory()[0x80:0x1940]==before[0x80:0x1940],'Controlled exit leaves party records unchanged')
    after=e.memory()
    check(all(after[p-0x02000000:p-0x02000000+264]==before[p-0x02000000:p-0x02000000+264]
              for p in pointers if p not in enemies),'Controlled exit preserves judges, guests and story actors')
    capture('exit-input-'+str(len(exits)));exits.append(row)
try:
    e=E(TEST_ROM)
    check(image[0x563ba8:0x563bb4]==bytes.fromhex('1e5d3a000000000104000000'),'Original event26 maps Royal Valley to scene93 and formation58')
    if '--resume-battle-entry' in sys.argv:
        folder=ROM.parent/'final-battle-bridge-20260917T111323.526039Z'
        raw=(folder/'report.json').read_bytes();assert sha(raw)=='474e54fd9b39a8ef293b7835da5bdc25e2a8503a';old=json.loads(raw)
        assert old['romSha1']==meta['romSha1'] and old['instrumentedSha1']==sha(patched)
        checkpoint=next(c for c in old['captures'] if c['label']=='battle-start-1')
        for name,digest in checkpoint['files'].items():assert sha((folder/name).read_bytes())==digest
        e.load(folder/'battle-start-1.state');e.set_memory(0,seed,0)
        retained=dict(report=str(folder/'report.json'),sha1=sha(raw),checkpoint=checkpoint)
        check(observe()['scenes']==[93] and observe()['battleStarts']==1,'Retained native Royal Valley deployment entry')
    else:
        e.set_memory(0,seed,0);e.run(3600)
        for key,wait in ((8,180),(256,60),(256,60),(256,180)):tap(key,wait)
        check(owned(e.memory())==prior['profiles']['0'],'Authenticated saved profile loaded')
        capture('ordinary-input');e.set_memory(LOG,bytes(168));e.set_memory(LOG,struct.pack('<I',0x53434e45))
    # Declared late-battle HP input. The level1 source clan otherwise loses
    # Marche before receiving a turn against the original final formation.
    for slot in range(24):e.set_memory(0x80+264*slot+0x18,struct.pack('<HH',999,999))
    capture('durable-party-input')
    for step in range(1100):
        current=observe()
        if current['scenes']!=seen:
            seen=current['scenes'];capture('scene-'+str(current['currentScene']))
            print(json.dumps(dict(step=step,observation=current)),flush=True)
        if 101 in seen:break
        if step==60:check(93 in seen,'Native event26 enters original scene93')
        if current['battleStarts']!=last_battle:
            last_battle=current['battleStarts'];phase_steps=0;capture('battle-start-'+str(last_battle))
        if last_battle and menus['menu_visible'](e):
            if not any(r['battle']==last_battle for r in exits):prepare_exit(current)
            for key in (32,32,256,256):tap(key,120)
            e.run(1800)
        else:
            tap(256,180);phase_steps+=1
            if last_battle and phase_steps in (8,16,24,32):
                capture('deployment-'+str(last_battle)+'-'+str(phase_steps))
                if phase_steps==8:prepare_exit(current)
                tap(8,180);tap(256,180)
            if last_battle and phase_steps==60:
                check(any(r['battle']==last_battle for r in exits),'Battle reaches native deployment within bounded input:'+str(last_battle))
    else:raise AssertionError('Final battle chain did not reach scene101 within bounded inputs')
    check(current['fired']==1,'Exactly one declared event entry')
    check(all(s in seen for s in (93,95,96,97,98,100,101)),'Native final battle and result scenes connect to accepted ending')
    check(current['battleStarts']==3,'Three original final battle-start instructions execute')
    check({r['battle'] for r in exits}=={1,2,3},'Each battle constructs native actors before controlled defeat setup')
    check(e.memory(0)==seed,'Bridge does not rewrite source flash')
    check((producer/'before-clear.sav').read_bytes()==seed,'Reusable source save unchanged')
except BaseException as error:
    import traceback
    traceback.print_exc();failure=repr(error)
    if e is not None:capture('failure')
finally:
    if e is not None:e.close()
report=dict(passed=failure is None,scope=SCOPE,romSha1=meta['romSha1'],instrumentedSha1=sha(patched),
    sourceSha1=sha(SOURCE.read_bytes()),helperSha1=sha(helper_bytes),assertions=len(checks),checks=checks,
    battleExits=exits,inputs=inputs,captures=captures,failure=failure,retained=retained,
    partyInput={'hp':999,'maxHp':999,'slots':24})
(OUT/'script.py').write_bytes(SOURCE.read_bytes());(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(passed=report['passed'],checks=len(checks),failure=failure,report=str(OUT/'report.json'))))
assert failure is None,failure
