"""Attempt native Shara invitation with all24 slots occupied, then cancel.

Reuse the authenticated original scene129 offer. No roster, flag, candidate
or slot input is changed. This tests the capacity branch after Yes, not merely
declining the offer. Fixed controls leave the original roster intact.
"""
import pathlib,hashlib
CAP_SCOPE=__doc__;CAP_SOURCE=pathlib.Path(__file__).resolve()
support=CAP_SOURCE.parent/'test-shara-scene-lifecycle.py';support_bytes=support.read_bytes()
assert hashlib.sha1(support_bytes).hexdigest()=='bd52b4d359defe6d8f6ebd6c4cb835bd0638076c'
prefix=support_bytes.decode().split('\ntry:\n')[0]
assert prefix!=support_bytes.decode()
exec(compile(prefix,str(support),'exec'));__doc__=CAP_SCOPE
try:
    folder=ROM.parent/'shara-scene-20260917T112601.593293Z'
    raw=(folder/'report.json').read_bytes();assert sha(raw)=='c3f62ac5cf55a7dc127bbad0cc9eb845093bb31f'
    old=json.loads(raw);assert old['romSha1']==meta['romSha1'] and old['instrumentedSha1']==sha(patched)
    cap=next(c for c in old['captures'] if c['label']=='full-offer')
    for name,digest in cap['files'].items():assert sha((folder/name).read_bytes())==digest
    e=E(TEST_ROM);e.load(folder/'full-offer.state');e.set_memory(0,cleared,0)
    before=owned(e.memory())
    check(sum(bool(e.memory()[0x84+i*264]) for i in range(24))==24,'All24 native slots occupied')
    check(e.memory()[0x2c78:0x2c7c]==bytes(4),'Native candidate bridge found no vacancy')
    tap(256,180);capture('invitation-question')
    tap(256,180);inputs.append([600,0,0]);e.run(600);capture('capacity-prompt')
    check(not flag(603) and not members(),'Yes with a full clan does not accept or overwrite a member')
    check(owned(e.memory())==before,'Capacity branch preserves the full offered profile')
    for step in range(30):
        tap(1 if step<3 else 256,180)
        if flag(621):break
    capture('capacity-cancelled')
    check(flag(621) and not flag(603) and not members(),'Cancelling full-capacity invitation retains original retry')
    check(owned(e.memory())==before,'Cancelled capacity branch preserves every member and expansion record')
    check(e.memory(0)==cleared,'Capacity attempt does not alter saved flash')
except BaseException as error:
    import traceback
    traceback.print_exc();failure=repr(error)
    if e is not None:capture('failure')
finally:
    if e is not None:e.close()
result=dict(passed=failure is None,scope=CAP_SCOPE,romSha1=meta['romSha1'],instrumentedSha1=sha(patched),
    sourceSha1=sha(CAP_SOURCE.read_bytes()),supportSha1=sha(support_bytes),assertions=len(checks),checks=checks,
    inputs=inputs,captures=captures,failure=failure,retained=dict(report=str(folder/'report.json'),sha1=sha(raw)))
(OUT/'script.py').write_bytes(CAP_SOURCE.read_bytes());(OUT/'report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(passed=result['passed'],checks=len(checks),failure=failure,report=str(OUT/'report.json'))))
assert failure is None,failure
