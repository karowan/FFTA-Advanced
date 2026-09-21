"""Direct native-palette mapping, legacy preservation and source-pixel oracle.

Static asset conversion only: no emulation, ROM mutation or authored art.
"""
import datetime,importlib.util,json,struct
from pathlib import Path
from PIL import Image
from native_art import ROOT,sha,pack_tiles,tile_image,palette
from native_table_literals import authenticate
from generated_class_transport import mapped_frame

out=ROOT/'build/art/direct-native-conversion'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];observations=[]

def check(ok,label):
    assert ok,label
    checks.append(label)

try:
    spec=importlib.util.spec_from_file_location('conversion',ROOT/'scripts/convert-generated-sprites.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();authenticate(clean);raw,rgb=palette(clean,0x419d80)
    sources=[('v5','samurai-idle-v5.png','835862b1994f2be07bda0137070178b539614f043b264e4d9c7438e1ea3d80fd',2,2,'v5-h30'),
             ('march','samurai-march-v1.png',None,3,2,'march-v1-native')]
    prompt=json.loads((ROOT/'src/art/imagegen/samurai-march-study.json').read_text());sources[1]=(sources[1][0],sources[1][1],prompt['sourceSha256'],*sources[1][3:])
    root=ROOT/'build/art/imagegen/samurai/native-scale-study'
    for name,filename,digest,columns,rows,prior in sources:
        source=root/filename;check(sha(source.read_bytes())==digest,name+' exact generated input')
        reference=json.loads((root/prior/'manifest.json').read_text())
        legacy=out/(name+'-legacy');module.convert(source,legacy,columns,rows,30)
        rebuilt=json.loads((legacy/'manifest.json').read_text())
        check(rebuilt['paletteSha256']==reference['paletteSha256'] and [v['tileSha256'] for v in rebuilt['frames']]==[v['tileSha256'] for v in reference['frames']],name+' existing default conversion byte-exact')
        dest=out/name;module.convert(source,dest,columns,rows,30,target_palette=raw)
        meta=json.loads((dest/'manifest.json').read_text());check((dest/'palette.bin').read_bytes()==raw and meta['paletteSha256']==sha(raw),name+' exact consumer palette preserved')
        image=Image.open(source).convert('RGBA');palette_points=[tuple(rgb[i*3:i*3+3]) for i in range(16)]
        frames=[];preview=Image.new('RGBA',(columns*32,rows*32),(63,94,97,255))
        for index,f in enumerate(meta['frames']):
            converted=Image.open(dest/f'frame-{index:02}.png');crop=image.crop(f['box']).crop(f['bounds']).resize(f['nativeSize'],Image.Resampling.NEAREST)
            old=mapped_frame(legacy/f'frame-{index:02}.png',rebuilt['frames'][index],rgb);opaque=changed=error=new_error=0
            occupied=set()
            for y in range(crop.height):
                for x in range(crop.width):
                    color=crop.getpixel((x,y));position=(x+f['origin'][0],y+f['origin'][1]);value=converted.getpixel(position)
                    if color[3]<128:
                        assert value==0;continue
                    distances=[sum((color[k]-v[k])**2 for k in range(3)) for v in palette_points]
                    assert 1<=value<=15 and distances[value]==min(distances[1:])
                    prior_value=old.getpixel(position);assert prior_value!=0
                    assert distances[value]<=distances[prior_value]
                    opaque+=1;changed+=value!=prior_value;error+=distances[prior_value];new_error+=distances[value];occupied.add(position)
            check(all(converted.getpixel((x,y))==0 for y in range(32) for x in range(32) if (x,y) not in occupied),f'{name}/{index} exact source alpha and canvas padding')
            check(opaque>0 and new_error<=error,f'{name}/{index} every source pixel has minimal native-palette error')
            pixels=pack_tiles(converted,16);check(pixels==(dest/f'frame-{index:02}.4bpp').read_bytes() and tile_image(pixels,rgb,32).tobytes()==converted.tobytes(),f'{name}/{index} lossless4bpp roundtrip')
            check(mapped_frame(dest/f'frame-{index:02}.png',f,rgb).tobytes()==converted.tobytes(),f'{name}/{index} existing importer leaves direct native pixels exact')
            preview.alpha_composite(converted.convert('RGBA'),((index%columns)*32,(index//columns)*32))
            frames.append(dict(frame=index,opaquePixels=opaque,changedPixels=changed,twoStageSquaredError=error,directSquaredError=new_error))
        check(sum(v['directSquaredError'] for v in frames)<sum(v['twoStageSquaredError'] for v in frames),name+' strictly reduces measured source color error')
        preview.resize((preview.width*8,preview.height*8),Image.Resampling.NEAREST).save(dest/'native-review.png')
        observations.append(dict(name=name,sourceSha256=digest,frames=frames,manifest=str(dest/'manifest.json')))
    for bad in (b'',bytes(31),bytes(33)):
        try:module.convert(source,out/'invalid',columns,rows,30,target_palette=bad)
        except AssertionError:pass
        else:raise AssertionError('Accepted invalid palette length')
        check(True,'Invalid target palette size rejected: '+str(len(bad)))
    report=dict(status='passed',checks=checks,observations=observations,paletteOffset=0x419d80,paletteSha256=sha(raw),scope='Static conversion only. Default byte preservation, source-alpha/padding, per-pixel nearest native color and nonincreasing error, exact4bpp roundtrip, existing importer identity. Better color fidelity is not production art or animation acceptance.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,observations=observations),indent=2)+'\n');print('Artifacts: '+str(out));raise
