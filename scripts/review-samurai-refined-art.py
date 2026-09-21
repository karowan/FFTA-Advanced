"""Compare pinned imagegen conversions at one native scale; no drawn artwork."""
import hashlib,json
from pathlib import Path
from PIL import Image
from native_art import ROOT,sha,pack_tiles

folder=ROOT/'build/art/imagegen/samurai/native-scale-study'
reference=folder/'original-human-reference.png'
assert sha(reference.read_bytes())=='2c95aad66a09c1c0e40a885cc4c8bfc7f16b879c40977b4490acab81e2440357'
original=Image.open(reference).convert('RGBA').resize((128,40),Image.Resampling.NEAREST)
frames={};records=[]
for version in (3,4):
    specpath=ROOT/f'src/art/imagegen/samurai-march-v{version}.json'
    spec=json.loads(specpath.read_text());assert sha((ROOT/spec['source']).read_bytes())==spec['sourceSha256']
    converted=folder/f'march-v{version}-native';manifest=json.loads((converted/'manifest.json').read_text())
    assert manifest['sourceSha256']==spec['sourceSha256']
    images=[]
    for i,row in enumerate(manifest['frames']):
        im=Image.open(converted/f'frame-{i:02}.png');assert sha(pack_tiles(im,16))==row['tileSha256']
        images.append(im.convert('RGBA'))
    frames[version]=images
    changes=[]
    for first,second in ((0,1),(1,2),(3,4),(4,5)):
        a=images[first];b=images[second]
        changes.append(dict(frames=[first,second],changedPixels=sum(x!=y for x,y in zip(a.getdata(),b.getdata()))))
    records.append(dict(version=version,sourceSha256=spec['sourceSha256'],sizes=[f['nativeSize'] for f in manifest['frames']],phaseDifferences=changes))

# Compositing and nearest-neighbor display only: the source sprites are intact.
panel=Image.new('RGBA',(192,40),(63,94,97,255))
views=[original.crop((0,0,32,40)),original.crop((32,0,64,40)),frames[3][0],frames[4][0],frames[4][1],frames[4][3]]
for col,im in enumerate(views):panel.alpha_composite(im,(col*32,0 if im.height==40 else 4))
panel.save(folder/'march-v4-comparison-native.png')
panel.resize((1152,240),Image.Resampling.NEAREST).save(folder/'march-v4-comparison.png')
meta=json.loads((ROOT/'build/art/generated-actions/refined-samurai-current.json').read_text())
assert hashlib.sha1(Path(meta['path']).read_bytes()).hexdigest()==meta['romSha1']
result=dict(status='Visual review evidence; production artwork unaccepted',romSha1=meta['romSha1'],versions=records,
    columns=['Original Soldier','Original Paladin','Generated v3 front','Generated v4 front A','Generated v4 front B','Generated v4 back A'],
    review=['v4 has consistent16x27 bounds in all six cells.','Front eye and crescent more consistent than v3 after conversion.','Stepping amplitude and costume/back detail continuity still need imagegen revision.','Exact native runtime proof does not grant visual acceptance.'])
(folder/'march-v4-review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
