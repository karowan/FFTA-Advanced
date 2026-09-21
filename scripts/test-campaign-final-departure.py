"""Native post-save departure event selects the earned Royal Valley battle.

Reuse the actual Over The Hill result, Ambervale creation and normal save.
Moving the cursor to another territory and pressing A invokes original D1A18
before departure. No scene, event, flag, mission, placement or outcome is
injected. Stop at native deployment and reuse the accepted final battle suffix.
"""
import pathlib,hashlib
ENTRY_SOURCE=pathlib.Path(__file__).resolve();ROOT=ENTRY_SOURCE.parents[1];ENTRY_SCOPE=__doc__
support=ROOT/'scripts/test-campaign-territory-scenes.py';support_bytes=support.read_bytes()
assert hashlib.sha1(support_bytes).hexdigest()=='d514a34cd354ccf69a0b9826494eb77785eb7d1c'
parts=support_bytes.decode().replace('\r\n','\n').split('\ntry:\n',1);assert len(parts)==2
head=parts[0].replace("'territory-scenes-'","'final-departure-'")
exec(compile(head,str(support),'exec'));__doc__=ENTRY_SCOPE
source_folder=ROM.parent/'territory-scenes-20260917T121346.541215Z'
source_raw=(source_folder/'report.json').read_bytes();assert sha(source_raw)=='c444a0e888346c056fd473bdcc9cc4f22fa3b242'
source_proof=json.loads(source_raw);assert source_proof['romSha1']==meta['romSha1'] and source_proof['instrumentedSha1']==sha(patched)
entry=next(c for c in source_proof['captures'] if c['label']=='after-native-save-close')
for file,digest in entry['files'].items():assert sha((source_folder/file).read_bytes())==digest
saved=(source_folder/'after-native-save-close.sav').read_bytes();case=dict(mission=26)
try:
    e=E(TEST_ROM);e.load(source_folder/'after-native-save-close.state');e.set_memory(0,saved,0);e.run(1)
    check(flag(e.memory(),75) and not flag(e.memory(),54) and not flag(e.memory(),572),'Actual saved-arrival gates before final scene')
    check(native().call(0x08036350,e.memory()[0x1f69])==30,'Actual current region is new Ambervale')
    before=observe();capture('saved-world-input')
    route_to(3);tap(256,1200);capture('departure-input')
    seen=[]
    for step in range(150):
        obs=observe()
        if obs['scenes']!=seen:
            seen=obs['scenes'];capture('scene-'+str(obs['currentScene']));print(json.dumps(obs),flush=True)
        if 93 in seen and obs['battleStarts']==2:break
        tap(256,180)
    else:raise AssertionError('Saved-arrival departure did not reach native final deployment')
    check(obs['fired']==before['fired'],'Observer did not substitute a final event or scene')
    check(flag(e.memory(),572) and not flag(e.memory(),54) and not flag(e.memory(),793),'Native final-entry marker without clear or final receipt')
    check(e.memory(0)==saved,'Final scene entry leaves saved flash unchanged')
    capture('native-final-deployment')
except BaseException as error:
    import traceback;traceback.print_exc();failure=repr(error)
    if e is not None:capture('failure')
finally:
    if e is not None:e.close()
report=dict(passed=failure is None,scope=ENTRY_SCOPE,romSha1=meta['romSha1'],instrumentedSha1=sha(patched),
    sourceSha1=sha(ENTRY_SOURCE.read_bytes()),supportSha1=sha(support_bytes),producer=dict(report=str(source_folder/'report.json'),sha1=sha(source_raw),checkpoint=entry),
    checks=checks,inputs=inputs,captures=captures,failure=failure)
(OUT/'script.py').write_bytes(ENTRY_SOURCE.read_bytes());(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(passed=report['passed'],checks=len(checks),failure=failure,report=str(OUT/'report.json'))))
assert failure is None,failure
