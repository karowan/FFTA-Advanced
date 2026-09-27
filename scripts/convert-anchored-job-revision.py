"""Convert one imagegen worksheet using its declared fixed native coordinates.

No bbox fitting, silhouette edits, facial patching or newly painted pixels.
The original palette bank is untouched; quantization uses the approved base's
existing indices to prevent new material colors appearing between frames.
"""
import argparse
import json
import runpy
import shutil
import hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from new_job_art_helpers import ROOT, checked, record


def convert(request_path, source, revision):
    req=json.loads(request_path.read_text());folder=request_path.parent
    if not folder.is_relative_to(ROOT/'build/art'):raise ValueError('Use ignored art output')
    if not revision.isalnum():raise ValueError('Alphanumeric revision required')
    for ref in req['references']:checked(ref)
    if req.get('parentRequest'):checked(req['parentRequest'])
    if req.get('poseNotes'):checked(req['poseNotes']['source'])
    if req.get('motionAnchor'):checked(req['motionAnchor'])
    checked(req['atlas']);base=Image.open(checked(req['approvedBase']))
    rom=checked(req['paletteROM']).read_bytes();pal=req['palette']
    words=[int.from_bytes(rom[p:p+2],'little') for p in range(pal['offset'],pal['offset']+32,2)]
    assert words==pal['words']
    allowed=sorted(set(base.tobytes())-{0});assert allowed
    colors=np.array([[((w>>s)&31)*255//31 for s in (0,5,10)] for w in words])
    aid=req['pose']+'-'+revision
    receipt_path=folder/(aid+'-receipt.json')
    if receipt_path.exists():raise ValueError('Preserve previous revisions')
    raw=folder/(aid+'-generated.png');shutil.copy2(source,raw)
    image=Image.open(raw).convert('RGBA')
    assert image.width==image.height,'Wrong sheet aspect; never fit the figure'
    sampled=image.resize(tuple(req['logicalGrid']),Image.Resampling.NEAREST)
    clear=runpy.run_path(str(ROOT/'scripts/assemble-other-race-studies.py'))['clear_background']
    sampled=clear(sampled)
    cell=sampled.crop(tuple(req['crop']));assert cell.size==(64,64)
    registration=req.get('registration')
    if registration:
        # A reviewed rigid translation corrects worksheet placement, never body
        # proportions. It must be tied to this exact preserved raw generation.
        assert registration['sourceSha256']==hashlib.sha256(raw.read_bytes()).hexdigest()
        assert registration['reason'].strip()
        dx,dy=registration['translation']
        assert type(dx) is int and type(dy) is int and max(abs(dx),abs(dy))<=8
        box=cell.getbbox();assert box
        assert 0<=box[0]+dx<box[2]+dx<=64 and 0<=box[1]+dy<box[3]+dy<=64
        shifted=Image.new('RGBA',(64,64));shifted.alpha_composite(cell,(dx,dy));cell=shifted
    rgba=np.array(cell);mask=rgba[:,:,3]>0
    ds=((rgba[:,:,:3].astype(float)[:,:,None,:]-colors[allowed][None,None,:,:])**2).sum(3)
    indices=np.array(allowed,dtype='uint8')[ds.argmin(2)];indices[~mask]=0
    native=Image.fromarray(indices);native.putpalette(colors.flatten().tolist()+[0]*(768-48));native.info['transparency']=0
    box=native.convert('RGBA').getbbox();assert box and box[0]>0 and box[1]>0 and box[2]<64 and box[3]<64,'Clipped target'
    dest=folder/(aid+'-native.png');native.save(dest);cell.save(folder/(aid+'-sampled.png'))
    native.resize((512,512),Image.Resampling.NEAREST).save(folder/(aid+'-8x.png'))
    bounds=[box[0]-32,box[1]-56,box[2]-32,box[3]-56]
    expected=req['nativeAction']['geometry']['bounds']
    receipt=dict(request=record(request_path),source=record(raw),native=record(dest),approvedBase=req['approvedBase'],
        logicalGrid=req['logicalGrid'],crop=req['crop'],origin=req['origin'],registration=registration,palette=pal,allowedIndices=allowed,
        bounds=bounds,nativeReferenceBounds=expected,edgeDifferences=[a-b for a,b in zip(bounds,expected)],
        method='Whole-grid nearest sampling; fixed quadrant extraction; alpha preservation; approved index subset of unchanged native palette',
        status='converted-requires-anatomy-and-motion-review',runtimeImported=False)
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(receipt=record(receipt_path),native=record(dest),bounds=bounds,expected=expected)))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--request',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--revision',required=True)
    a=p.parse_args();convert(a.request.resolve(),a.source.resolve(),a.revision)
