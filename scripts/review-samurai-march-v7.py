"""Review authenticated imagegen/native pixels; compositing only, no artwork drawing."""
import json
from PIL import Image
from native_art import ROOT, sha, pack_tiles

folder=ROOT/'build/art/imagegen/samurai/native-scale-study'
reference=folder/'original-human-reference.png'
assert sha(reference.read_bytes())=='2c95aad66a09c1c0e40a885cc4c8bfc7f16b879c40977b4490acab81e2440357'
original=Image.open(reference).convert('RGBA').resize((128,40),Image.Resampling.NEAREST)
panel=Image.new('RGBA',(256,80),(63,94,97,255));versions={};records=[]
for row,version in enumerate((7,8)):
    spec=json.loads((ROOT/f'src/art/imagegen/samurai-march-v{version}.json').read_text(encoding='utf-8'))
    assert sha((ROOT/spec['source']).read_bytes())==spec['sourceSha256']
    directory=folder/f'march-v{version}-own';raw=(directory/'manifest.json').read_bytes();meta=json.loads(raw)
    assert meta['sourceSha256']==spec['sourceSha256']
    assert sha((directory/'palette.bin').read_bytes())==meta['paletteSha256']
    panel.alpha_composite(original.crop((0,0,64,40)),(0,row*40));frames=[];eyes=[]
    for i,record in enumerate(meta['frames']):
        image=Image.open(directory/f'frame-{i:02}.png')
        assert sha(pack_tiles(image,16))==record['tileSha256']
        frame=image.convert('RGBA');frames.append(frame)
        panel.alpha_composite(frame,((i+2)*32,row*40+4))
        if i<3:
            points=[(x,y) for y in range(18) for x in range(32)
                    if min(frame.getpixel((x,y))[:3])>=230 and frame.getpixel((x,y))[3]]
            assert points==[(16,12),(16,13)]
            eyes.append(points)
    versions[version]=frames
    records.append(dict(version=version,sourceSha256=spec['sourceSha256'],conversionSha256=sha(raw),
        sizes=[f['nativeSize'] for f in meta['frames']],whiteFacePixels=eyes,
        upperRegionPairDifferences=[sum(a!=b for a,b in zip(frames[i].crop((0,0,32,18)).get_flattened_data(),frames[i+1].crop((0,0,32,18)).get_flattened_data())) for i in (0,1,3,4)]))
panel.save(folder/'march-v7-v8-comparison-native.png')
panel.resize((1536,480),Image.Resampling.NEAREST).save(folder/'march-v7-v8-comparison.png')
sequence=[]
for index in (0,1,2,1):
    frame=Image.new('RGBA',(64,40),(63,94,97,255))
    for row in range(2):frame.alpha_composite(versions[7][row*3+index],(row*32,4))
    sequence.append(frame.convert('RGB').resize((384,240),Image.Resampling.NEAREST))
sequence[0].save(folder/'march-v7-loop.gif',save_all=True,append_images=sequence[1:],duration=[270,130,270,130],loop=0,disposal=2,optimize=False)
walkpath=ROOT/'build/art/explicit-walk/20260918T215025.008748Z/report.json'
walk=json.loads(walkpath.read_text(encoding='utf-8'))
assert walk['status']=='passed' and walk['romSha1']=='d80e763169223d98284b180a39fa047f650d50e5'
seen={v['blockSha256'] for v in walk['observations']['mapped'].values() if 48<v['position'][0]<144 and v['actor']['displayedFrames']}
converted=json.loads((folder/'march-v7-own/manifest.json').read_text(encoding='utf-8'))
assert len(seen)>=3 and seen<={f['tileSha256'] for f in converted['frames']}
report=dict(status='private artwork review; full production acceptance open',versions=records,
    referenceSha256=sha(reference.read_bytes()),walkReport=str(walkpath),walkReportSha256=sha(walkpath.read_bytes()),
    actualMovingFrameHashes=sorted(seen),frameOrder=[0,1,2,1],nativeTicks=[16,8,16,8],gifMilliseconds=[270,130,270,130],
    limitations=['Comparison and GIF are composites, not emulator video.','GIF timing approximates native60Hz ticks.','Upper-region differences are observations, not automatic acceptance.','Only Samurai idle/march refinement; other actions/water/menu artwork remain unfinished.'])
(folder/'march-v7-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(report=str(folder/'march-v7-review.json'),actualMovingPoses=len(seen))))
