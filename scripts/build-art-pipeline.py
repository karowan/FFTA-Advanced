"""Compose verified native transports and temporary generated menu art.

Private technical candidate only: no installed ROM/save or release acceptance
is updated. All component sources/assets are authenticated before composition.
"""
import hashlib,json
from pathlib import Path
from native_art import ROOT,sha
from equipment_preview import apply

def build():
    actor_path=ROOT/'build/art/generated-actor-poc/current.json'
    miniature_path=ROOT/'build/art/generated-miniature-poc/current.json'
    actor=json.loads(actor_path.read_text());mini=json.loads(miniature_path.read_text())
    assert mini['baseRomSha1']==actor['romSha1']
    original=Path(mini['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==mini['romSha1']
    assert sha(actor_path.read_bytes())==mini['sourceManifestSha256']
    root=ROOT/'build/art/pipeline';work=root/'compile';rom=bytearray(original)
    preview=apply(rom,work,generated_portraits=True)
    allowed=set(range(preview['reservation'][0],preview['reservation'][0]+preview['bytes']))
    for change in preview['changes']:allowed.update(range(change['offset'],change['offset']+change['bytes']))
    assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
    digest=hashlib.sha1(rom).hexdigest();out=root/digest;out.mkdir(parents=True,exist_ok=True)
    path=out/'FFTA_Art_Pipeline.gba';path.write_bytes(rom)
    for number in range(116,126):
        (out/f'portrait-{number}.png').write_bytes((work/f'portrait-{number}.png').read_bytes())
    preview.update(source=actor['source'],baseRomSha1=actor['baseRomSha1'],assetDirectory=str(out))
    sources={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [actor_path,miniature_path,ROOT/'src/art/imagegen/catalog.json']}
    report=dict(schema=1,path=str(path),romSha1=digest,romSha256=sha(rom),source=actor['source'],baseRomSha1=actor['baseRomSha1'],
        components=dict(actor=actor,miniature=mini,preview=preview),sources=sources,
        status='technical candidate; temporary artwork; not final release',
        coverage=dict(equipmentPreview='ten generated portrait crops and native labels across party/buy/sell; pending composed acceptance',
            battleActor='Samurai land idle only; original action/water placeholders remain',
            menuFigure='Samurai job-wheel miniature only; other new classes remain donors',
            palettes='existing consumer-specific palettes; custom allocation remains open',
            weaponsEffectsStatus='original presentation placeholders; dedicated imports remain open'))
    for p in (out/'manifest.json',root/'current.json'):p.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(path=str(path),romSha1=digest,status=report['status'])))
    return report

if __name__=='__main__':build()
