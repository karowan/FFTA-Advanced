"""Prepare a traceable retry or reviewed rigid registration, never draw art.

The note names observed anatomy/orientation errors. Clearing a worksheet target
changes reference composition only; imagegen still creates every new pixel.
"""
import argparse
import json
from pathlib import Path
from PIL import Image
from new_job_art_helpers import checked,record


def revise(path,revision,note,blank=False,identity=None,registration=None,source=None,motion_anchor=None):
    req=json.loads(path.read_text());target=path.parent/(req['pose']+'-request-'+revision+'.json')
    if target.exists():raise ValueError('Preserve previous requests')
    req['parentRequest']=record(path);req['revisionReason']=note
    if blank:
        sheet=Image.open(checked(req['references'][0])).convert('RGBA')
        w,h=sheet.size;grid=req['logicalGrid'];crop=req['crop']
        rect=tuple(int(v*(w/grid[0] if i%2==0 else h/grid[1])) for i,v in enumerate(crop))
        sheet.paste(sheet.getpixel((0,0)),rect)
        output=path.parent/(req['pose']+'-'+revision+'-worksheet.png');sheet.save(output);req['references'][0]=record(output)
        req['prompt']=req['prompt'].replace('Edit ONLY the BOTTOM RIGHT sprite','Draw ONLY in the empty BOTTOM RIGHT cell').replace('BOTTOM RIGHT currently duplicates it and is your edit target.','BOTTOM RIGHT is empty and is your drawing target.')
    if identity:req['references'][1]=record(identity)
    if motion_anchor:
        anchor=json.loads(motion_anchor.read_text());anchor_req=json.loads(checked(anchor['request']).read_text())
        assert anchor_req['job']==req['job'] and anchor_req['origin']==req['origin']
        assert anchor_req['palette']==req['palette']
        base=Image.open(checked(anchor['native'])).convert('RGBA');assert base.size==(64,64)
        atlas=checked(req['atlas']).parent
        native=Image.open(atlas/anchor_req['nativeAction']['image']).convert('RGBA')
        action=Image.open(atlas/req['nativeAction']['image']).convert('RGBA')
        board=Image.new('RGBA',(128,128),(228,226,220,255))
        for im,xy in [(native,(0,0)),(action,(64,0)),(base,(0,64))]:board.alpha_composite(im,xy)
        worksheet=path.parent/(req['pose']+'-'+revision+'-motion-worksheet.png');board.resize((1024,1024),Image.Resampling.NEAREST).save(worksheet)
        identity=path.parent/(req['pose']+'-'+revision+'-motion-identity.png');base.resize((512,512),Image.Resampling.NEAREST).save(identity)
        req['references'][:2]=[record(worksheet),record(identity)]
        req['motionAnchor']=record(motion_anchor);req['nativeNeutral']=anchor_req['nativeAction']
        bounds=req['nativeAction']['geometry']['bounds'];local=[bounds[0]+32,bounds[1]+56,bounds[2]+32,bounds[3]+56]
        req['prompt']=('Use case: precise-object-edit. Complete ONLY the empty BOTTOM RIGHT quadrant of image 1. Return the whole square worksheet. '
            'TOP LEFT is the original game character in a related pose; TOP RIGHT is the exact required pose. '
            'BOTTOM LEFT is the revised new character in the SAME related pose as top left; it supplies costume and anatomy continuity. '
            'Transfer ONLY the small change between the top pair to the new bottom pair. Do not return to the upright neutral stance. '
            'Image 2 is the new related pose enlarged, image 3 the existing native palette. Keep the new costume/colors; do not copy the original costume. '
            f'The complete worksheet is 128x128 logical pixels, four 64x64 cells. Actor origin in each cell is (32,56). Target local bounds {local}, right/bottom exclusive. '
            'Keep coarse logical pixel clusters and original anatomical scale. No fitting, stretching, extra equipment, labels or new effects. '
            'Keep the other three quadrants unchanged, flat gray background. The target begins at (64,64). All-ages fully clothed fantasy game art. ')
    if registration:
        if source is None:raise ValueError('Registration requires the exact raw source')
        req['registration']=dict(sourceSha256=record(source)['sha256'],translation=registration,reason=note)
    else:req['prompt']+=' FOCUSED REVISION: '+note
    target.write_text(json.dumps(req,indent=2)+'\n');print(target)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--request',type=Path,required=True);p.add_argument('--revision',required=True);p.add_argument('--note',required=True);p.add_argument('--blank-target',action='store_true');p.add_argument('--identity',type=Path);p.add_argument('--translation',type=int,nargs=2);p.add_argument('--source',type=Path);p.add_argument('--motion-anchor',type=Path)
    a=p.parse_args();revise(a.request.resolve(),a.revision,a.note,a.blank_target,a.identity.resolve() if a.identity else None,a.translation,a.source.resolve() if a.source else None,a.motion_anchor.resolve() if a.motion_anchor else None)
