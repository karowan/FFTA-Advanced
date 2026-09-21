"""Reconcile retained campaign acceptance and the affected current lifetimes.

Read-only source, ROM and evidence audit. Historical campaign tests keep their
original identities and declared scenario limits. This does not certify E03
maximum capacity or E05 source rebuild/package. No emulator or player files.
"""
import ast, datetime, hashlib, json, subprocess
from pathlib import Path
from native_art import ROOT, sha

index_path=ROOT/'notes/native-art-campaign-evidence.json';index=json.loads(index_path.read_text())
out=ROOT/'build/art/campaign-compatibility'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];regions=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    for row in index['files']:check(sha((ROOT/row['path']).read_bytes())==row['sha256'],'Retained evidence '+row['path'])
    meta=json.loads((ROOT/'build/art/connected'/index['candidateSha1']/'manifest.json').read_text());rom=Path(meta['path']).read_bytes();old=Path(meta['fixtureSource']).read_bytes()
    check(hashlib.sha1(rom).hexdigest()==index['candidateSha1'] and hashlib.sha1(old).hexdigest()=='1b070824a8dad4995434eee3ab40fa08187a6120','Exact current and historical campaign ROMs')
    release=json.loads((ROOT/'build/release-acceptance.json').read_text());rebuild=json.loads((ROOT/'build/reproducibility/20260917T225624.978478Z/report.json').read_text())
    check(release['passed'] and release['romSha1']==hashlib.sha1(old).hexdigest() and rebuild['passed'],'Accepted original release and corrected source-base rebuild')
    for name,digest in release['frozenReportsAndLogs'].items():check(sha((ROOT/name).read_bytes())==digest,'Original report/log '+name)
    revised_notes=[]
    for name,digest in release['reusedEvidenceNotes'].items():
        raw=(ROOT/name).read_bytes()
        if sha(raw)!=digest:
            revised_notes.append(dict(path=name,currentSha256=sha(raw)))
            raw=subprocess.check_output(['git','show',release['sourceCommit']+':'+name],cwd=ROOT)
        check(sha(raw)==digest,'Exact historical accepted note '+name)
    # The corrected gameplay base retained every original gameplay source.
    # Later source edits are the reviewed owned-menu pointer and status iterator.
    changed=[]
    for name,digest in release['shippingSources'].items():
        if not name.startswith('src/'):continue
        check(rebuild['sources'][name]==digest,'Gameplay source unchanged in corrected base '+name)
        if sha((ROOT/name).read_bytes())!=digest:changed.append(name)
    check(sorted(changed)==['src/engine/chemist-preference.c','src/engine/integrated-jobs.c'],'Only reviewed owned-menu and native status iterator gameplay source changes')
    # Compare whole original mission/scene execution regions, not just a few
    # entrance instructions. The US keyboard size is the only scene-region edit.
    for name,start,end in [('mission and pub/result consumers',0xcfc00,0xd2300),('native formations',0x54cd54,0x55128c),('mission/event tables',0x55ae4c,0x56466c),('scene interpreter and actors',0x120000,0x12d000),('expansion action/application tables',0x11e8000,0x11ee000)]:
        a=bytearray(old[start:end]);b=rom[start:end]
        if name=='scene interpreter and actors':
            check(old[0x12a15e:0x12a162].hex()=='c6200002' and rom[0x12a15e:0x12a162].hex()=='42200002','Only declared US glyph allocation reduction')
            a[0x12a15e-start:0x12a162-start]=b[0x12a15e-start:0x12a162-start]
        check(bytes(a)==b,'Complete preserved '+name);regions.append(dict(name=name,start=start,end=end,sha256=sha(b)))
    tree=ast.parse((ROOT/'scripts/test-campaign-ending-scenes.py').read_text());ending_expression=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='NATIVE_RANGES' for t in n.targets))
    check(all(isinstance(n,(ast.List,ast.Tuple,ast.Constant,ast.BinOp,ast.Add,ast.Mult,ast.Load)) for n in ast.walk(ending_expression)),'Historical ending range expression contains constants only')
    ending_ranges=eval(compile(ast.Expression(ending_expression),'<ending bounds>','eval'),{'__builtins__':{}})
    for start,end in ending_ranges:
        check(rom[start:end]==old[start:end],'Unchanged original ending dependency '+hex(start));regions.append(dict(name='ending dependency',start=start,end=end,sha256=sha(rom[start:end])))
    saves=json.loads((ROOT/'build/art/campaign-saves/20260919T093907.228501Z/report.json').read_text())
    result=json.loads((ROOT/'build/art/battle-exit/20260919T094742.944213Z/report.json').read_text())
    ending=json.loads((ROOT/'build/art/campaign-ending/20260919T095035.310874Z/report.json').read_text())
    check(saves['status']=='passed' and saves['romSha1']==index['candidateSha1'] and len(saves['checks'])==54,'Current ordinary/ending cold loads and actual postgame consumers54')
    check(result['status']=='passed' and result['coldRomSha1']==index['candidateSha1'] and len(result['checks'])==16 and result['retainedResult'],'Retained battle result plus native placement/menu/save/current-cold suffix16')
    check(ending['passed'] and ending['romSha1']==index['candidateSha1'] and ending['assertions']==14,'Current native ending/credits/scene-owned save/reset/Continue/cold14')
    report=dict(status='passed',candidateSha1=index['candidateSha1'],checks=checks,regions=regions,inputIndexSha256=sha(index_path.read_bytes()),scope=__doc__,changedGameplaySources=changed,revisedNotes=revised_notes,
        limitations=['Representative declared campaign milestones, not uninterrupted full-combat replay or every script variation.','Battle fixture changes formation32 and class records; no claim of naturally earning that composition.','No cross-ROM savestate compatibility; flash cold-load is tested.','E03 capacity/root review and E05 clean final build/delivery remain separate.'])
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',checks=checks,regions=regions,error=str(error)),indent=2)+'\n',encoding='utf-8');print('Artifacts: '+str(out));raise
