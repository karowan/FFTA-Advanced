"""Authenticated private repair of the historical integrated data collisions.

This does not install a game. Fresh builds use native_table_literals instead.
The repair is an explicit bridge for retained generated-art evidence/artifacts.
"""
import hashlib,json,struct
from pathlib import Path
from native_art import ROOT,sha
from native_table_literals import authenticate,NATIVE_TABLE_LITERALS

RELEASE='1b070824a8dad4995434eee3ab40fa08187a6120'
PARENT='377330c4c16a1c8d3352bf6ae748f45a4fc90a00'
MANIFEST=ROOT/'build/expansion/probes/integrated-jobs/b26778520203359c3b129bcc025b92dd0e4c01f1'/RELEASE/'manifest.json'

def build():
    clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();authenticate(clean)
    raw=MANIFEST.read_bytes();assert sha(raw)=='5133b37443b6112ffacccf85b5754e14cfda5f13ba0c457ae17c79e80a140e12'
    release=json.loads(raw);assert release['romSha1']==RELEASE
    original=Path(release['path']).read_bytes();assert hashlib.sha1(original).hexdigest()==RELEASE
    parent=json.loads((ROOT/'build/art/generated-equipment'/PARENT/'manifest.json').read_text())
    source=Path(parent['path']).read_bytes();assert hashlib.sha1(source).hexdigest()==PARENT
    rom=bytearray(source);records=[]
    native=[c for c in release['changes'] if c.get('kind')=='table literal relocation' and c['offset']<len(clean)]
    assert len(native)==169 and sum(c['offset'] in NATIVE_TABLE_LITERALS for c in native)==30
    for c in native:
        p=c['offset']
        if p in NATIVE_TABLE_LITERALS:continue
        assert struct.unpack_from('<I',clean,p)[0]==c['old']
        assert struct.unpack_from('<I',original,p)[0]==c['value']
        assert struct.unpack_from('<I',source,p)[0]==c['value'],'Later change needs review'
        struct.pack_into('<I',rom,p,c['old']);records.append(c)
    allowed={i for c in records for i in range(c['offset'],c['offset']+4)}
    changed=[i for i,(a,b) in enumerate(zip(source,rom)) if a!=b]
    assert len(records)==139 and set(changed)<=allowed
    digest=hashlib.sha1(rom).hexdigest();root=ROOT/'build/art/native-data-repair';out=root/digest;out.mkdir(parents=True,exist_ok=True)
    path=out/'FFTA_Native_Data_Repaired.gba';path.write_bytes(rom)
    report=dict(path=str(path),romSha1=digest,source=parent['path'],baseRomSha1=PARENT,releaseSource=release['path'],
        releaseSha1=RELEASE,releaseManifest=str(MANIFEST),releaseManifestSha256=sha(raw),records=records,changedBytes=len(changed),
        scope='Restore139 original data words accidentally relocated by historical integration;30 reviewed native table references and all other bytes unchanged. Private technical candidate, not installed or visually accepted.')
    for p in (out/'manifest.json',root/'current.json'):p.write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    m=build();print(json.dumps(dict(romSha1=m['romSha1'],words=len(m['records']),changedBytes=m['changedBytes'])))
