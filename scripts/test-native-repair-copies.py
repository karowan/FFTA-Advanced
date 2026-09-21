"""Audit copied art provenance and test the repaired native palette consumer."""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
import native_portraits as portrait
from native_miniatures import decode
from native_repair_copies import build

checks=[];out=ROOT/'build/art/native-repair-complete/tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    meta=build();rom=Path(meta['path']).read_bytes();base=Path(meta['source']).read_bytes()
    clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();p=meta['portraitManifest']
    classmeta=json.loads((ROOT/'build/art/class-resources/5d8fcf3a36d128c646c2628c41b4bcfe83924e42/manifest.json').read_text())
    repair=json.loads((Path(meta['source']).parent/'manifest.json').read_text())
    check(hashlib.sha1(rom).hexdigest()==meta['romSha1'],'Authenticated final repair child')
    check(rom[:0x1000000]==base[:0x1000000],'All139 corrected original words remain identical')
    overlaps=[]
    for s in classmeta['segments']:
        start=s.get('sourceOffset')
        if start is not None:
            overlaps.extend((s,c) for c in repair['records'] if start<c['offset']+4 and c['offset']<start+s['bytes'])
    check(not overlaps,'No collisions copied into20 cloned actor resources')
    for i in range(103):
        check(portrait.decode(rom,portrait.entry(rom,p['pixelArchive'],i))[0]==portrait.decode(clean,portrait.entry(clean,portrait.PIXELS,i))[0],f'{i} copied portrait pixels match clean original')
        check(portrait.layout(rom,portrait.entry(rom,p['oamArchive'],i))[1]==portrait.layout(clean,portrait.entry(clean,portrait.LAYOUTS,i))[1],f'{i} copied portrait OAM matches clean original')
    classes=json.loads((ROOT/'build/art/generated-classes/595782ba32f4a20ff2053218f8722ab5e491112d/manifest.json').read_text())
    for i in range(54):check(decode(rom,classes['container'],i)==decode(clean,0x3b5a5c,i),f'{i} copied miniature matches clean original')
    sys.path.insert(0,str(ROOT/'tools/arm-python'))
    from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
    from unicorn.arm_const import *
    UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
    tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=1000000'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native palette ARM>','exec'))
    iw=(Path(meta['releaseSource']).parent/'fixture/battle-ready.iwram').read_bytes();a=ARM(rom,iw)
    for mode,archive in enumerate(p['paletteArchives']):
        for i in range(185):
            actual=decode(rom,archive,i)
            expected=decode(clean,portrait.PALETTES[mode],i) if i<165 else decode(base,archive,i)
            check(actual==expected,f'{mode}/{i} clean original or preserved generated palette')
        # Only the changed record and its adjacent records need runtime replay;
        # other routing and native decoder evidence remains applicable.
        a.put(0x02002fc2,bytes([mode]))
        for i in (148,149,150):
            raw=decode(clean,portrait.PALETTES[mode],i)
            for stack in (STACK,STACK-4):
                dest=0x02022020;a.put(dest-32,b'\xa5'*160);a.call(0x080cb8d4,dest,i,stack=stack)
                check(a.read(dest,96)==raw and a.read(dest-32,32)==a.read(dest+96,32)==b'\xa5'*32,f'{mode}/{i}/{stack:x} actual native palette output and bounds')
    check(decode(base,p['paletteArchives'][1],149)!=decode(clean,portrait.PALETTES[1],149),'Inherited wrong palette reproduced as negative control')
    changed={i for i,(x,y) in enumerate(zip(base,rom)) if x!=y}
    check(changed=={c['offset'] for c in meta['changes']},'Whole child difference matches explicit palette bytes only')
    check(Path(build()['path']).read_bytes()==rom,'Exact copied-palette repair reproduction')
    report=dict(status='passed',romSha1=meta['romSha1'],baseRomSha1=meta['baseRomSha1'],checks=checks,changes=meta['changes'],
        scope='No139-word collision intersects cloned actor inputs;103 copied portrait pixels/OAM,54 copied miniatures and495 original palettes match clean ROM.60 new palette records unchanged. Native repaired palette149 and neighbors in3 modes/2 stack residues. No blanket gameplay/scene acceptance of original-data restoration.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),romSha1=meta['romSha1'],changedBytes=len(meta['changes']),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n');print('Artifacts: '+str(out));raise
