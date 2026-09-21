"""Deterministic technical conversion/comparison only; imagegen authors the art."""
import argparse
import importlib.util
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / 'build/art/race-study-2026-09-19'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--height',type=int,default=27)
    parser.add_argument('--context-grid',action='store_true',help='Preserve fifth workbench cell grid:32x64 logical pixels, crop rows16..47')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('conversion', ROOT / 'scripts/convert-generated-sprites.py')
    converter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(converter)
    assert 1 <= args.height <= 31
    source_for_conversion = args.source
    if args.context_grid:
        args.output.mkdir(parents=True,exist_ok=True)
        full = Image.open(args.source).convert('RGBA').resize((32,64),Image.Resampling.NEAREST)
        full.putalpha(full.getchannel('A').point(lambda a:255 if a>=128 else 0))
        bounds = full.getbbox()
        assert bounds and bounds[1]>=16 and bounds[3]<=48, ('Context crop would clip art',bounds)
        grid = full.crop((0,16,32,48))
        source_for_conversion = args.output/'input-grid.png'
        grid.save(source_for_conversion)
        bounds = grid.getbbox()
        args.height = bounds[3]-bounds[1]
    converter.convert(source_for_conversion, args.output, columns=1, rows=1, height=args.height)
    # This is a visual draft palette, not a native shared-palette acceptance.
    frame = Image.open(args.output / 'frame-00.png').convert('RGBA')
    reference = Image.open(STUDY / 'user-face-reference.png').convert('RGBA')
    assert reference.size == (1024,320)
    reference = reference.resize((128,40), Image.Resampling.NEAREST)
    board = Image.new('RGBA',(160,40),'#e4e2dc')
    board.alpha_composite(reference)
    board.alpha_composite(frame,(128,4))
    board.save(args.output / 'comparison-1x.png')
    board.resize((1280,320),Image.Resampling.NEAREST).save(args.output / 'comparison-8x.png')
    source = Image.open(args.source).convert('RGBA')
    mask = source.getchannel('A').point(lambda a:255 if a>=128 else 0)
    bounds = mask.getbbox()
    report = json.loads((args.output/'manifest.json').read_text())
    report['scope'] = 'Single base visual review only. Generated 15-color draft, no ROM/runtime or shared-palette acceptance.'
    report['sourceAlphaExtrema'] = source.getchannel('A').getextrema()
    report['sourceOpaqueBounds'] = bounds
    report['originalSource'] = str(args.source)
    report['originalSourceSha256'] = converter.sha(args.source.read_bytes())
    report['contextGrid'] = args.context_grid
    if args.context_grid:
        assert report['scale']==1, 'Do not rescale the recovered source grid'
        report['gridExtraction'] = {'resizedCell':[32,64],'crop':[0,16,32,48],'resampling':'nearest','paintedPixels':0}
    report['comparisonColumns'] = ['native reference 1','native reference 2','native reference 3','native reference 4','generated candidate']
    report['conversionVerified'] = frame.size == (32,32) and len(set(Image.open(args.output/'frame-00.png').tobytes())) <= 16
    assert report['conversionVerified']
    (args.output/'review-metadata.json').write_text(json.dumps(report,indent=2)+'\n')
    print(args.output/'comparison-8x.png')

if __name__ == '__main__':
    main()
