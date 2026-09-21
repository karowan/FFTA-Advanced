"""Store the large reviewed catalog as per-class source JSON; restore losslessly.

The aggregate is a generated local file. Splitting along class boundaries keeps
each source document below the repository's four-MiB text limit, without dropping
prompts, source references, decisions or failed attempt history.
"""
import argparse,json
from pathlib import Path
from native_art import ROOT,sha


def encoded(value):return (json.dumps(value,indent=2)+'\n').encode('utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('export','restore','verify'));args=parser.parse_args()
    root=ROOT/'src/art/race-study';aggregate=root/'full-animation-v1.json';index=root/'full-animation-v1.index.json'
    if args.mode=='export':
        raw=aggregate.read_bytes();document=json.loads(raw)
        newline='CRLF' if b'\r\n' in raw else 'LF'
        rendered=encoded(document).replace(b'\n',b'\r\n') if newline=='CRLF' else encoded(document)
        assert rendered==raw,'Aggregate serialization must round-trip exactly'
        units=document['units'];document['units']=[];parts=[];folder=root/'full-animation-v1';folder.mkdir(exist_ok=True)
        for unit in units:
            data=encoded(unit);assert len(data)<4*1024*1024
            path=folder/(str(unit['job'])+'-'+unit['slug']+'.json');path.write_bytes(data)
            parts.append(dict(path=str(path.relative_to(root)).replace('\\','/'),sha256=sha(data),bytes=len(data),job=unit['job']))
        index.write_bytes(encoded(dict(schema=1,aggregate=aggregate.name,aggregateSha256=sha(raw),aggregateBytes=len(raw),aggregateNewline=newline,template=document,units=parts)))
    source=json.loads(index.read_bytes());document=source['template'];units=[]
    for part in source['units']:
        path=root/part['path'];assert path.resolve().is_relative_to(root.resolve())
        raw=path.read_bytes();assert sha(raw)==part['sha256'] and len(raw)==part['bytes']<4*1024*1024
        unit=json.loads(raw);assert unit['job']==part['job'];units.append(unit)
    document['units']=units;raw=encoded(document)
    if source['aggregateNewline']=='CRLF':raw=raw.replace(b'\n',b'\r\n')
    assert sha(raw)==source['aggregateSha256'] and len(raw)==source['aggregateBytes']
    if args.mode=='restore':
        if aggregate.exists():assert aggregate.read_bytes()==raw,'Refuse to replace changed local catalog; export its changes first'
        else:aggregate.write_bytes(raw)
    else:assert aggregate.read_bytes()==raw
    print(json.dumps(dict(status='passed',classes=len(units),aggregateSha256=sha(raw),bytes=len(raw),mode=args.mode)))


if __name__=='__main__':main()
