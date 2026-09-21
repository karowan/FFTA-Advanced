"""Nearest-neighbor native-cell conversion of palette-guided imagegen trials.

No source drawings are overwritten. Generated grids are sampled uniformly;
opaque RGB is mapped to unchanged native colors and alpha is thresholded.
"""
import argparse,importlib.util,json,shutil
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from native_art import ROOT,sha,pack_tiles

spec=importlib.util.spec_from_file_location('colorstudy',ROOT/'scripts/study-reviewed-native-color.py')
study=importlib.util.module_from_spec(spec);spec.loader.exec_module(study)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--slug',required=True);parser.add_argument('--version',required=True)
    parser.add_argument('--palette',type=int,choices=range(3),default=0);parser.add_argument('--prompt',type=Path,required=True)
    args=parser.parse_args();out=study.OUT/args.slug;out.mkdir(exist_ok=True)
    generated=out/('generated-'+args.version+'.png');shutil.copy2(args.source,generated)
    im=Image.open(generated).convert('RGBA');native=im.resize((32,32),Image.Resampling.NEAREST)
    raw=np.array(native);raw[:,:,3]=np.where(raw[:,:,3]>=128,255,0);native=Image.fromarray(raw)
    colors=json.loads((study.OUT/'manifest.json').read_text())['palettes'][args.palette]
    exact,_=study.convert(native,colors,'neutral');dest=out/('generated-'+args.version+'-native.png');exact.save(dest,bits=4)
    rawcolors=np.array(exact.getpalette()).reshape(-1,3)
    assert set(np.unique(np.array(exact)))-{0}<=set(range(1,16))
    assert np.array_equal(rawcolors[:16],np.array(colors))
    source=Image.open(out/'source.png').convert('RGBA')
    current=1 if args.slug=='human-samurai' else 0
    images=[source,Image.open(out/f'palette-{current}-rgb555.png').convert('RGBA'),Image.open(out/f'palette-{args.palette}-neutral.png').convert('RGBA'),exact.convert('RGBA')]
    labels=['Approved source','Rejected conversion','Perceptual conversion','Palette-guided generation']
    board=Image.new('RGBA',(1024,320),(228,226,220,255));draw=ImageDraw.Draw(board)
    for i,(part,label) in enumerate(zip(images,labels)):
        draw.text((i*256+8,8),label,fill='black');board.alpha_composite(part.resize((224,224),Image.Resampling.NEAREST),(i*256+16,40));board.alpha_composite(part,(i*256+112,276))
    board.save(out/('generated-'+args.version+'-comparison.png'))
    prompt=json.loads(args.prompt.read_text())
    prompt.update(output=str(generated.relative_to(ROOT)),outputSha256=sha(generated.read_bytes()),converted=str(dest.relative_to(ROOT)),
        convertedSha256=sha(dest.read_bytes()),tileSha256=sha(pack_tiles(exact,16)),nativePalette=args.palette,
        nativePaletteWordsUnchanged=True,logicalCanvas=[32,32],conversion='Full-canvas nearest-neighbor sampling; alpha128; perceptual native-index mapping',
        status='review-only-not-approved',limitations='Generation may shift pixels; not a replacement for the accepted animation base yet.')
    (out/('generated-'+args.version+'.json')).write_text(json.dumps(prompt,indent=2)+'\n')
    print(json.dumps(dict(output=str(dest),comparison=str(out/('generated-'+args.version+'-comparison.png')))))


if __name__=='__main__':main()
