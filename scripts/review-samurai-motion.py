"""Native-scale motion comparison from authenticated pixels, without drawing art."""
import json
from PIL import Image
from native_art import ROOT,sha,pack_tiles

folder=ROOT/'build/art/imagegen/samurai/native-scale-study'
specpath=ROOT/'src/art/imagegen/samurai-march-v6.json'
spec=json.loads(specpath.read_text())
assert sha((ROOT/spec['source']).read_bytes())==spec['sourceSha256']
reference=folder/'original-idle-motion.png'
assert sha(reference.read_bytes())=='0b1f4c4b5a34cc9dc7f13cd3ed567b1068c8980e2db02daaa6d882302de977d9'
original=Image.open(reference).convert('RGBA').resize((128,80),Image.Resampling.NEAREST)
converted=folder/'march-v6-native';meta=json.loads((converted/'manifest.json').read_text())
assert meta['sourceSha256']==spec['sourceSha256']
images=[];boots=[]
for i,frame in enumerate(meta['frames']):
    with Image.open(converted/f'frame-{i:02}.png') as im:
        assert sha(pack_tiles(im,16))==frame['tileSha256']
        images.append(im.convert('RGBA'))
        # Descriptive samples only: native brown index5 in the bottom8 rows.
        # Sheath pixels can also be brown; this is not automatic gait acceptance.
        boots.append(dict(frame=i,brownPixels=[(x,y) for y in range(24,32) for x in range(32) if im.getpixel((x,y))==5]))
sequence=[]
for phase,index in enumerate((0,1,2,1)):
    panel=Image.new('RGBA',(64,80),(63,94,97,255))
    for row in range(2):
        panel.alpha_composite(original.crop((phase*32,row*40,phase*32+32,row*40+40)),(0,row*40))
        panel.alpha_composite(images[row*3+index],(32,row*40+4))
    sequence.append(panel.convert('RGB').resize((384,480),Image.Resampling.NEAREST))
sequence[0].save(folder/'march-v6-motion.gif',save_all=True,append_images=sequence[1:],duration=[270,130,270,130],loop=0,disposal=2,optimize=False)
sheet=Image.new('RGB',(384*4,480),(63,94,97))
for phase,im in enumerate(sequence):sheet.paste(im,(phase*384,0))
sheet.save(folder/'march-v6-motion-phases.png')
result=dict(status='review evidence; unaccepted production art',sourceSha256=spec['sourceSha256'],referenceSha256=sha(reference.read_bytes()),
    frameOrder=[0,1,2,1],durationsMs=[270,130,270,130],nativeTicks=[16,8,16,8],
    convertedSizes=[f['nativeSize'] for f in meta['frames']],brownFootSamples=boots,
    layout='Each phase: original native motion reference left, newly generated Samurai right; front above and back below.',
    limitations=['GIF delays approximate60Hz ticks to GIF10ms precision.','Comparison composites are not emulator capture.','Boot color samples are descriptive and include possible sheath pixels.','Face/helmet drift and final costume fidelity remain visually unaccepted.'])
(folder/'march-v6-motion-review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(report=str(folder/'march-v6-motion-review.json'),sizes=result['convertedSizes'])))
