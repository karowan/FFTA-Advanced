"""Repair the one decoded portrait palette copied before native-data repair."""
import hashlib,json,struct
from pathlib import Path
from native_art import ROOT,sha
from native_table_literals import authenticate
from native_portraits import PALETTES
from native_miniatures import decode,encode

def build():
    parent=json.loads((ROOT/'build/art/native-data-repair/current.json').read_text())
    source=Path(parent['path']).read_bytes();assert hashlib.sha1(source).hexdigest()==parent['romSha1']=='0c7d5fe7c79565727d2c2da63c21f303c9c25661'
    clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();authenticate(clean)
    portrait=json.loads((ROOT/'build/art/generated-portraits/75029dea8310b93cd5e462ee7517248c9452fa0a/manifest.json').read_text())
    rom=bytearray(source);corrections=[]
    for mode,archive in enumerate(portrait['paletteArchives']):
        records=[decode(source,archive,i) for i in range(185)]
        old=encode(records,96);assert source[archive:archive+len(old)]==old
        for i in range(165):
            native=decode(clean,PALETTES[mode],i)
            if records[i]!=native:
                corrections.append(dict(mode=mode,index=i,oldSha256=sha(records[i]),newSha256=sha(native)))
                records[i]=native
        new=encode(records,96);assert len(new)==len(old);rom[archive:archive+len(new)]=new
    assert [(c['mode'],c['index']) for c in corrections]==[(1,149)]
    changes=[dict(offset=i,old=a,value=b) for i,(a,b) in enumerate(zip(source,rom)) if a!=b]
    digest=hashlib.sha1(rom).hexdigest();root=ROOT/'build/art/native-repair-complete';out=root/digest;out.mkdir(parents=True,exist_ok=True)
    path=out/'FFTA_Native_Repair_Complete.gba';path.write_bytes(rom)
    report=dict(path=str(path),romSha1=digest,source=parent['path'],baseRomSha1=parent['romSha1'],releaseSource=parent['releaseSource'],
        corrections=corrections,changes=changes,portraitManifest=portrait,
        scope='Authenticated139-word original-data repair plus its one inherited decoded portrait-palette copy. Temporary art and outstanding consumer/assembled delivery gates remain.')
    for p in (out/'manifest.json',root/'current.json'):p.write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':
    m=build();print(json.dumps(dict(romSha1=m['romSha1'],changedBytes=len(m['changes']))))
