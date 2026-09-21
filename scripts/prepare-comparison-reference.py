"""Compose authenticated native poses into a private style reference, unchanged."""
import json
from PIL import Image
from native_art import ROOT,sha

out=ROOT/'build/art/provider-comparison/reference';out.mkdir(parents=True,exist_ok=True)
board=Image.new('RGBA',(96,64),(255,0,255,255));records=[]
for col,actor in enumerate([4,23,39]):
    directory=ROOT/f'build/art/native-reference/actor-{actor:03}'
    native=json.loads((directory/'native.json').read_text())
    for row,slot in enumerate([0,1]):
        pose=native['slots'][slot]['frames'][0]['pose']
        path=directory/(pose+'-pose.png')
        # Original OAM is composed on96x96 with world anchor48,64. This is
        # coordinate extraction, not repainting or retouching any source pixel.
        image=Image.open(path).convert('RGBA')
        crop=image.crop((32,32,64,64))
        board.alpha_composite(crop,(col*32,row*32))
        records.append(dict(actor=actor,slot=slot,path=str(path),sha256=sha(path.read_bytes()),crop=[32,32,64,64]))
board.save(out/'native-reference.png')
board.resize((1536,1024),Image.Resampling.NEAREST).save(out/'native-reference-16x.png')
(out/'manifest.json').write_text(json.dumps(dict(scope='Original native pose style/anatomy reference only; unchanged source pixels, fixed crop and nearest enlargement. Preview palettes are not accepted per-job palette routing.',records=records),indent=2)+'\n')
print(str(out/'native-reference-16x.png'))
