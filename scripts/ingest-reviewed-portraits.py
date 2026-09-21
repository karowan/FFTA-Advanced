"""Extract imagegen menu portraits without drawing or repairing their pixels.

Preserves worksheet, exact prompt and input hashes. Alternate worksheet cells
must be explicitly recorded after visual inspection; outputs await review.
"""
import argparse,json,shutil,runpy
from pathlib import Path
from PIL import Image,ImageDraw
from native_art import ROOT,sha

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--slug');args=parser.parse_args()
    folder=ROOT/'build/art/reviewed-integration/portraits'
    planpath=folder/'generation-plan.json';plan=json.loads(planpath.read_text())
    clear=runpy.run_path(str(ROOT/'scripts/assemble-other-race-studies.py'))['clear_background']
    def record(path):return dict(path=str(path.relative_to(ROOT)).replace('\\','/'),sha256=sha(path.read_bytes()))
    for job in plan['jobs']:
        if args.slug and args.slug!=job['slug']:continue
        version=job.get('version',1)
        receipt=json.loads((folder/'receipts'/f"{job['slug']}-v{version}.json").read_text())
        assert receipt['prompt']==job['prompt'] and receipt['inputs']==[job['template'],job['concept']]
        for ref in receipt['inputs']:assert sha((ROOT/ref['path']).read_bytes())==ref['sha256']
        source=Path(receipt['outputPath']);target=folder/f"{job['slug']}-generated-v{version}.png"
        if target.exists():assert sha(target.read_bytes())==sha(source.read_bytes())
        else:shutil.copy2(source,target)
        crop=job.get('extractionCrop',job['crop'])
        if crop!=job['crop']:
            approval=job['extractionAdjustment']
            assert approval['sourceSha256']==sha(source.read_bytes()) and approval['reason']
        full=clear(Image.open(target).convert('RGBA').resize(tuple(job['logicalSize']),Image.Resampling.NEAREST))
        # The empty gap above the target protects tall ears/crests that cross
        # the nominal row boundary. Preserve the entire generated silhouette.
        strip=[crop[0],48,crop[2],128]
        part=full.crop(tuple(strip));box=part.getbbox();assert box
        part=part.crop(box);original_size=list(part.size)
        part.thumbnail((64,64),Image.Resampling.NEAREST)
        im=Image.new('RGBA',(64,64));im.alpha_composite(part,((64-part.width)//2,64-part.height))
        output=folder/f"{job['slug']}-portrait-v{version}-fit2.png"
        if output.exists():
            assert Image.open(output).convert('RGBA').tobytes()==im.tobytes()
        else:im.save(output)
        job.update(generatedSource=record(target),output=record(output),bounds=list(im.getbbox()),
                   status='generated-awaiting-review',extractionStrip=strip,extractionBounds=list(box),sourceSize=original_size,
                   conversion='Nearest worksheet reduction, connected flat background removal, whole target silhouette fitted to 64x64 and bottom centered; no art pixels drawn')
        print(json.dumps(dict(slug=job['slug'],bounds=job['bounds'])))
    planpath.write_text(json.dumps(plan,indent=2)+'\n')
    ready=[j for j in plan['jobs'] if 'output' in j]
    board=Image.new('RGBA',(960,((len(ready)+4)//5)*280),(228,226,220,255));draw=ImageDraw.Draw(board)
    for n,j in enumerate(ready):
        x=n%5*192;y=n//5*280;draw.text((x+4,y+4),j['label'],fill='black')
        im=Image.open(ROOT/j['output']['path']).convert('RGBA')
        board.alpha_composite(im.resize((192,192),Image.Resampling.NEAREST),(x,y+24))
        board.alpha_composite(im,(x+64,y+216))
    board.save(folder/'source-review.png')

if __name__=='__main__':main()
