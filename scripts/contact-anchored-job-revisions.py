"""Compose unchanged reference/revision images for visual inspection, not artwork."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw
from new_job_art_helpers import ROOT, checked


def contact(folder, job, start, end, requests=False):
    cells=[]
    choices=json.loads((folder/'choices.json').read_text())
    for n in range(start,end):
        pid=f'p{n:03}'
        reqpath=folder/job/(pid+'-request-initial.json')
        if not reqpath.exists():reqpath=folder/job/(pid+'-request.json')
        if not reqpath.exists():continue
        req=json.loads(reqpath.read_text())
        if requests:
            im=Image.open(checked(req['references'][0])).convert('RGB').resize((384,384),Image.Resampling.NEAREST)
            canvas=Image.new('RGB',(384,410),'#e8e7df');canvas.paste(im,(0,0))
            ImageDraw.Draw(canvas).text((8,387),job+' '+pid,fill='black')
        else:
            rev=choices.get(job,{}).get(pid,'v1')
            path=folder/job/(pid+'-'+rev+'-native.png')
            canvas=Image.new('RGB',(384,222),'#e8e7df')
            original=checked(req['atlas']).parent/req['nativeAction']['image']
            for source,x in [(original,0),(path,192)]:
                if source.exists():
                    im=Image.open(source).convert('RGBA').resize((192,192),Image.Resampling.NEAREST)
                    canvas.paste(im,(x,0),im)
            ImageDraw.Draw(canvas).text((8,195),f'{job} {pid}: original / {rev}',fill='black')
        cells.append(canvas)
    cols=3;rows=(len(cells)+cols-1)//cols
    result=Image.new('RGB',(cols*cells[0].width,rows*cells[0].height),'#e8e7df')
    for i,cell in enumerate(cells):result.paste(cell,((i%cols)*cell.width,(i//cols)*cell.height))
    output=folder/f'{job}-{start}-{end}-{"requests" if requests else "review"}.png'
    result.save(output);print(output)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--job',required=True);p.add_argument('--start',type=int,required=True);p.add_argument('--end',type=int,required=True);p.add_argument('--requests',action='store_true')
    a=p.parse_args();contact(a.out.resolve(),a.job,a.start,a.end,a.requests)
