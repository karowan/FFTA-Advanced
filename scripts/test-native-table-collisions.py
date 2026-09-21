"""Exact production relocation-loop replay and repaired native icon consumers."""
import ast,datetime,hashlib,json,runpy,struct,sys
from pathlib import Path
from native_art import ROOT,sha
from native_miniatures import decode
from native_table_literals import authenticate,native_literal_allowed,NATIVE_TABLE_LITERALS

out=ROOT/'build/art/native-data-repair/tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    repair=runpy.run_path(str(ROOT/'scripts/repair-native-table-collisions.py'))
    meta=repair['build']();rom=Path(meta['path']).read_bytes();base=Path(meta['source']).read_bytes()
    release=json.loads(repair['MANIFEST'].read_text());shipping=Path(release['path']).read_bytes()
    clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();authenticate(clean)
    check(hashlib.sha1(rom).hexdigest()==meta['romSha1'],'Authenticated corrected candidate')
    # Reverse the recorded native relocation stage, then replay its ACTUAL AST
    # with the same upstream table extents. This isolates the changed builder
    # policy without overwriting current manifests or rebuilding unrelated jobs.
    rows=[c for c in release['changes'] if c.get('kind')=='table literal relocation' and c['offset']<len(clean)]
    before=bytearray(shipping)
    for c in rows:struct.pack_into('<I',before,c['offset'],c['old'])
    ptr=lambda data,p:struct.unpack_from('<I',data,p)[0]
    maps=[(ptr(before,0xccd84)-0x08000000,432*28,0x11e8000),(0x553e70,209*4,0x11ec000),(0x3a87b0,93*12,0x11ec400),(0x52790c,93*12,0x11ed000)]
    for job,view in release['jobViews'].items():
        image=Path(view['path']).read_bytes();check(hashlib.sha1(image).hexdigest()==view['romSha1'],job+' authenticated source map')
        for native,extent,new in [(0xccd84,438*28,0x11e8000),(0x12f2a0,223*4,0x11ec000),(0x1323b8,102*12,0x11ec400),(0x1339c8,102*12,0x11ed000)]:
            old=ptr(image,native)-0x08000000
            if not any(x[0]==old for x in maps):maps.append((old,extent,new))
    tree=ast.parse((ROOT/'scripts/build-integrated-jobs.py').read_text())
    loops=[n for n in tree.body if isinstance(n,ast.For) and 'preserved native data collision' in ast.unparse(n)]
    assert len(loops)==1
    code=compile(ast.Module(body=loops,type_ignores=[]),'<production relocation loop>','exec')
    env=dict(rom=before,native_clean=clean,table_maps=maps,ptr=ptr,struct=struct,native_literal_allowed=native_literal_allowed,
        classified={},base_regions=[],job_regions={},CODE=0x1000000,GEO_AI=0x1000000,MYK_CODE=0x1000000,RECOVERY_CODE=0x1000000,
        code=b'',geo_code=b'',myk_code=b'',recovery_code=b'',changes=[])
    exec(code,env)
    applied=[c for c in env['changes'] if c['kind']=='table literal relocation']
    preserved=[c for c in env['changes'] if c['kind']=='preserved native data collision']
    check({c['offset'] for c in applied}==set(NATIVE_TABLE_LITERALS),'All30 actual native table references retained')
    check({c['offset'] for c in preserved}=={c['offset'] for c in meta['records']},'All139 data coincidences preserved by production loop')
    expected=bytearray(shipping)
    for c in meta['records']:struct.pack_into('<I',expected,c['offset'],c['old'])
    check(before==expected,'Production loop changes only authenticated139-word repair')
    for p,(load,_) in NATIVE_TABLE_LITERALS.items():
        check(rom[p:p+4]==base[p:p+4] and rom[load:load+2]==clean[load:load+2],f'{p:x} relocated literal and native load preserved')
    changed={i for i,(a,b) in enumerate(zip(base,rom)) if a!=b}
    allowed={i for c in meta['records'] for i in range(c['offset'],c['offset']+4)}
    check(changed<=allowed and len(changed)==meta['changedBytes'],'Whole candidate exact bounded repair')
    check(rom[0x1000000:]==base[0x1000000:],'All appended artwork code palettes metadata byte-exact')
    for c in meta['records']:check(rom[c['offset']:c['offset']+4]==clean[c['offset']:c['offset']+4],f"{c['offset']:x} authenticated clean data restored")
    # Negative controls: neither unreviewed new references nor altered native
    # load instructions can silently pass. Original LDR-looking art tokens at
    #3d255a do NOT grant permission to relocate3d2780.
    for p in (0x3d26dc,0x3d2780):
        check(not native_literal_allowed(clean,clean,p),f'{p:x} graphics tokens rejected as pointers')
        bad=bytearray(before);bad[p]^=1
        try:native_literal_allowed(clean,bad,p)
        except AssertionError:pass
        else:raise AssertionError('Unreviewed changed data accepted')
        check(True,f'{p:x} unknown changed reference fails closed')
    p=next(iter(NATIVE_TABLE_LITERALS));bad=bytearray(before);bad[NATIVE_TABLE_LITERALS[p][0]]^=1
    try:native_literal_allowed(clean,bad,p)
    except AssertionError:pass
    else:raise AssertionError('Changed native load accepted')
    check(True,'Modified native load rejected')
    sys.path.insert(0,str(ROOT/'tools/arm-python'))
    from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
    from unicorn.arm_const import *
    tree=ast.parse((ROOT/'scripts/test-equipment-icons.py').read_text())
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native icon ABI>','exec'))
    a=ARM(rom)
    for ident in range(522):
        pixels=decode(clean,0x3c83fc,ident)
        check(decode(rom,0x3c83fc,ident)==pixels,f'{ident} strict decoder matches clean original')
        check(a.icon(0x080cb980,ident,True)==pixels,f'{ident} actual native generic decoder exact with ABI canaries')
    for ident in (467,469):
        for mode in (5,6):check(a.icon(0x0806796e,ident,True,block=True,mode=mode)==decode(clean,0x3c83fc,ident),f'{ident} shop quest namespace mode{mode}')
        try:decode(base,0x3c83fc,ident)
        except AssertionError:pass
        else:raise AssertionError('Historical corruption control unexpectedly valid')
        check(True,f'{ident} original failed decoder reproduced without executing unsafe native data')
    rebuilt=repair['build']();check(Path(rebuilt['path']).read_bytes()==rom,'Exact repair reproduction')
    report=dict(status='passed',romSha1=meta['romSha1'],baseRomSha1=meta['baseRomSha1'],checks=checks,records=meta['records'],changedBytes=meta['changedBytes'],
        scope='Production-loop replay retains30 native table references, preserves139 original data words, fail-closed controls, whole-ROM bounded repair and exact rebuild. All522 clean/native generic icons plus repaired quest-mode callers. Other139-word consumers require further impact review; old parent gameplay/screens are not automatically child acceptance.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'),romSha1=meta['romSha1'],changedBytes=meta['changedBytes'])))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n');print('Artifacts: '+str(out));raise
