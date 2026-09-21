"""Reproduce the private native pose reference and aligned support-art review.

Composites authenticated images only; never draws replacement character art.
This is a comparison contact sheet, not an emulator screenshot or animation.
"""
import hashlib,importlib.util,json
from pathlib import Path
from PIL import Image,ImageDraw
from native_art import ROOT,TILES,OAM,sha,palette,layout,compose,tile_image

work=ROOT/'build/art/imagegen/samurai/action-study';work.mkdir(parents=True,exist_ok=True)
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
assert hashlib.sha1(clean).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
native=json.loads((ROOT/'build/art/native-reference/actor-004/native.json').read_text(encoding='utf-8'))
_,rgb=palette(clean,0x419d80)
keys=['0132c0-000000','014040-000000','013a40-000026','013c40-000026','013e40-000026',
      '013680-000000','014180-000000','013b40-000026','013d40-000026','013f40-000026']

def reference(key):
    p=native['poses'][key];objects,_=layout(clean,p['oamOffset'])
    raw=clean[p['tileOffset']:p['tileOffset']+p['tileCount']*32]
    assert sha(raw)==p['tileSha256']
    indexed=compose(raw,objects,rgb);im=indexed.convert('RGBA')
    im.putalpha(Image.frombytes('L',indexed.size,indexed.tobytes()).point(lambda x:255 if x else 0))
    return im

# Reproduce exactly the native pose-only image used as generation input.
source_reference=Image.new('RGB',(400,200),(61,85,89));draw=ImageDraw.Draw(source_reference)
for i,key in enumerate(keys):
    im=reference(key);x=i%5*80;y=i//5*100
    source_reference.paste(im,(x-8,y),im);draw.text((x+2,y+84),key[:6],fill='white')
source_reference.resize((1200,600),Image.Resampling.NEAREST).save(work/'native-support-poses.png')
record=json.loads((ROOT/'src/art/imagegen/samurai-support-v1.json').read_text(encoding='utf-8'))
assert sha((ROOT/record['source']).read_bytes())==record['sourceSha256']
for r in record['references']:assert sha((ROOT/r['path']).read_bytes())==r['sha256']

plan=json.loads((ROOT/'src/art/imagegen/samurai-support-v1-plan.json').read_text(encoding='utf-8'))
by_key={p['nativePose']:p for p in plan['resources'][0]['poses']}
manifests={k:json.loads((ROOT/v['conversionManifest']).read_text(encoding='utf-8')) for k,v in plan['assets'].items()}
for name,asset in plan['assets'].items():
    assert sha((ROOT/asset['conversionManifest']).read_bytes())==asset['conversionManifestSha256']
    assert sha((ROOT/asset['source']).read_bytes())==asset['sourceSha256']

# Re-run only the deterministic image conversion into a separate review path.
spec=importlib.util.spec_from_file_location('support_conversion',ROOT/'scripts/convert-generated-sprites.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
colors=(ROOT/plan['assets']['march']['conversionManifest']).parent/'palette.bin'
reproduced=work/'support-v1-reproduced'
module.convert(ROOT/record['source'],reproduced,columns=5,rows=2,height=27,target_palette=colors.read_bytes())
support=(ROOT/plan['assets']['support']['conversionManifest']).parent
for path in [Path('palette.bin'),*[Path(f'frame-{i:02}.4bpp') for i in range(10)]]:
    assert (reproduced/path).read_bytes()==(support/path).read_bytes(),'Conversion not byte-reproducible'

sheet=Image.new('RGB',(240,232),(61,85,89));draw=ImageDraw.Draw(sheet)
labels=['NEUTRAL','RAISED','RECOIL','KNEEL','FALLEN'];review=[]
for i,key in enumerate(keys):
    direction=i//5;column=i%5;x=column*48;y=direction*116
    im=reference(key);draw.text((x+1,y),labels[column],fill='white')
    crop=im.crop((24,24,72,72));sheet.paste(crop,(x,y+10),crop)
    ref=by_key[key];asset=plan['assets'][ref['asset']];directory=(ROOT/asset['conversionManifest']).parent
    pose=Image.open(directory/f'frame-{ref["frame"]:02}.png').convert('RGBA')
    # Compare native opaque baselines. No original pixels enter generated art.
    bottom=im.getbbox()[3]-24;newbottom=pose.getbbox()[3]
    sheet.paste(pose,(x+8,y+68+bottom-newbottom),pose)
    white=[(u,v) for v in range(32) for u in range(32) if pose.getpixel((u,v))[3] and min(pose.getpixel((u,v))[:3])>=220]
    review.append(dict(nativePose=key,asset=ref['asset'],frame=ref['frame'],role=ref['role'],whitePixels=white,nativeSize=manifests[ref['asset']]['frames'][ref['frame']]['nativeSize']))
sheet.save(work/'support-v1-comparison-native.png')
sheet.resize((960,928),Image.Resampling.NEAREST).save(work/'support-v1-comparison.png')
report=dict(sourceSha256=record['sourceSha256'],paletteSha256=sha(colors.read_bytes()),frames=review,
    conversionReproduced=True,scope='Original native resource4 front row, generated front row, original back row, generated back row. Labels are review annotations, not game typography. Native baseline alignment; no emulator display or final-art acceptance.',
    limitations=['Body-only partial action sheet; no held-weapon coordination or full battle playback.',
                 'Back-facing support poses expose more side face than v7 march; costume/head-angle continuity remains a visual review item.',
                 'Unmapped attack poses still repeat temporary march frames; water still cropped.'])
candidate=json.loads((ROOT/'build/art/refinement/samurai-support-v1/current.json').read_text(encoding='utf-8'))
rom=Path(candidate['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==candidate['romSha1']
aligned=0
for row in candidate['assignments']:
    for frame in row['frames']:
        if 'explicitAction' not in frame:continue
        ref=frame['explicitAction'];objects,_=layout(rom,frame['oam'])
        im=tile_image(rom[frame['tile']:frame['tile']+512],rgb,32)
        bottom=Image.frombytes('L',im.size,im.tobytes()).getbbox()[3]+objects[0]['y']
        assert bottom==reference(ref['nativePose']).getbbox()[3]-64,'Imported native opaque baseline mismatch'
        aligned+=1
assert aligned==104
report.update(candidateRomSha1=candidate['romSha1'],nativeAlignedFrames=aligned)
(work/'support-v1-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status='review-ready',comparison=str(work/'support-v1-comparison.png'),report=str(work/'support-v1-review.json'))))
