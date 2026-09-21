"""Reproduce native reference, conversion and continuity evidence for imagegen.

Read-only with respect to ROMs/catalogs. Original artwork is extracted solely
for style/scale comparison. Generated images provide every new character pixel;
this script only converts them, applies existing palettes and compares frames.
It does not approve art, author pixel patterns or modify a playable candidate.
"""
import importlib.util,json
from pathlib import Path
from PIL import Image
from native_art import ROOT,sha,compose,palette,tile_image
from native_table_literals import authenticate
from generated_class_transport import mapped_frame

def build():
    specpath=ROOT/'src/art/imagegen/samurai-native-study.json';spec=json.loads(specpath.read_text())
    out=ROOT/'build/art/imagegen/samurai/native-scale-study';out.mkdir(parents=True,exist_ok=True)
    clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();authenticate(clean)
    reference=Image.new('RGBA',(128,40));records=[]
    for column,resource in enumerate((0,2,4,6)):
        manifestpath=ROOT/f'build/art/native-reference/actor-{resource:03}/native.json'
        original=json.loads(manifestpath.read_text());pose=original['poses'][original['slots'][0]['frames'][0]['pose']]
        raw=clean[pose['tileOffset']:pose['tileOffset']+pose['tileCount']*32];assert sha(raw)==pose['tileSha256']
        im=compose(raw,pose['objects'],palette(clean,0x419d60)[1]).convert('RGBA')
        bounds=im.getbbox();im=im.crop(bounds);reference.alpha_composite(im,(column*32+(32-im.width)//2,35-im.height))
        records.append(dict(resource=resource,bounds=bounds,size=list(im.size),tileSha256=sha(raw),manifestSha256=sha(manifestpath.read_bytes())))
    reference.resize((1024,320),Image.Resampling.NEAREST).save(out/'original-human-reference.png')
    assert sha((out/'original-human-reference.png').read_bytes())==spec['referenceSha256']
    module_spec=importlib.util.spec_from_file_location('sprite_conversion',ROOT/'scripts/convert-generated-sprites.py')
    module=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(module)
    rgb=palette(clean,0x419d80)[1];results=[];images={}
    for version in spec['versions']:
        source=ROOT/version['source'];assert sha(source.read_bytes())==version['sourceSha256']
        for conversion in version['conversions']:
            folder=out/conversion['name']
            module.convert(source,folder,version['columns'],version['rows'],conversion['height'],resampling=conversion['resampling'])
            meta=json.loads((folder/'manifest.json').read_text());frames=[];native=[]
            for index,frame in enumerate(meta['frames']):
                im=mapped_frame(folder/f'frame-{index:02}.png',frame,rgb)
                im.save(folder/f'native-palette-{index:02}.png',bits=4);native.append(im)
                frames.append(dict(index=index,size=frame['nativeSize'],bounds=im.getbbox(),indexedSha256=sha(im.tobytes())))
            sheet=Image.new('RGBA',(32*version['columns'],32*version['rows']),(63,94,97,255))
            for index,im in enumerate(native):sheet.alpha_composite(im.convert('RGBA'),((index%version['columns'])*32,(index//version['columns'])*32))
            sheet.resize((sheet.width*8,sheet.height*8),Image.Resampling.NEAREST).save(folder/'native-palette-review.png')
            continuity=[]
            if len(native)==4:
                for first,second in ((0,1),(2,3)):
                    a=native[first].tobytes();b=native[second].tobytes();different=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
                    continuity.append(dict(frames=[first,second],changedPixels=len(different),changedFootPixels=sum(i//32>=27 for i in different)))
            results.append(dict(version=version['name'],conversion=conversion,sourceSha256=version['sourceSha256'],frames=frames,continuity=continuity))
            images[conversion['name']]=native
    # Comparison image is a review artifact: original Soldier/Paladin, shipped
    # temporary Samurai, then latest generated front and back in native colors.
    delivery=json.loads((ROOT/'build/art/pipeline/delivery/current.json').read_text())
    assert delivery['rom']['sha1']=='a6d883b5d7657f10c3eb6d9b8407c489d287dbc7'
    candidatepath=ROOT/Path(delivery['rom']['path']).parent/'candidate.json'
    candidate=json.loads(candidatepath.read_text());rom=(ROOT/delivery['rom']['path']).read_bytes()
    import hashlib
    assert hashlib.sha1(rom).hexdigest()==delivery['rom']['sha1']
    job=next(v for v in candidate['components']['classes']['jobs'] if v['job']==116)
    old=tile_image(rom[job['frames'][0]['tile']:job['frames'][0]['tile']+512],rgb,32).convert('RGBA')
    views=[reference.crop((0,0,32,40)),reference.crop((32,0,64,40)),old,
           images['v5-h30'][0].convert('RGBA'),images['v5-h30'][2].convert('RGBA')]
    comparison=Image.new('RGBA',(160,44),(63,94,97,255))
    for column,im in enumerate(views):comparison.alpha_composite(im,(column*32,0 if im.height==40 else 4))
    comparison.resize((1280,352),Image.Resampling.NEAREST).save(out/'review-comparison.png')
    result=dict(status='review evidence; animation consistency rejected',sourcesSha256=sha(specpath.read_bytes()),
        nativeReferences=records,conversions=results,paletteOffset=0x419d80,paletteSha256=sha(clean[0x419d80:0x419da0]),
        comparisonColumns=['Original Soldier','Original Paladin','Packaged temporary Samurai','v5 front','v5 back'],
        limitations=['Generated source does not satisfy exact requested logical grid.','v5 idle phases change costume/foot detail, not only breathing.','Metrics describe differences; no threshold automatically accepts artwork.','No ROM, catalog, launcher, save or runtime-test changes.'])
    (out/'review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(report=str(out/'review.json'),status=result['status'],conversions=len(results))))

if __name__=='__main__':build()
