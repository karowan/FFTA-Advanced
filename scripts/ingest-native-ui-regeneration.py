"""Sample prescribed generation cells once; no bounding-box fit or art repairs."""
# See src/art/native-ui-review/README.md, section 4. Generate for the target
# portrait/head layout first. Fitting a large concept crop after generation
# lost native facial definition and was superseded by these fixed worksheets.
import json,shutil,runpy
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from native_art import ROOT,sha

OUT=ROOT/'build/art/native-ui-regeneration-v2-2026-09-20'
def main():
    plan=json.loads((OUT/'plan.json').read_text());paths=json.loads((OUT/'generated-paths.json').read_text())
    clear=runpy.run_path(str(ROOT/'scripts/assemble-other-race-studies.py'))['clear_background']
    results=[];cells=[]
    for row in paths:
        job=next(j for j in plan['jobs'] if j['slug']==row['slug']);asset=next(a for a in job['assets'] if a['kind']==row['kind'])
        folder=OUT/job['slug'];original=Path(row['path']);raw=folder/('generated-'+row['kind']+'.png')
        if raw.exists():assert raw.read_bytes()==original.read_bytes()
        else:shutil.copy2(original,raw)
        for ref in [asset['template'],job['concept']]+([job['iconPalette']] if row['kind']=='icon' else []):assert sha((ROOT/ref['path']).read_bytes())==ref['sha256']
        sheet=Image.open(raw).convert('RGBA')
        crop=row.get('crop',asset['crop'])
        # One declared grid sample, then exact cell extraction. A model layout
        # deviation must be recorded in the receipt, not guessed from getbbox.
        im=sheet.resize(tuple(asset['logicalSize']),Image.Resampling.NEAREST).crop(tuple(crop))
        im=clear(im);assert im.size==tuple(asset['nativeSize']) and im.getbbox(),(row['slug'],row['kind'],'Empty or incorrect generation cell')
        sampled=folder/(row['kind']+'-sampled.png');im.save(sampled)
        pixels=np.asarray(im);rgb=pixels[:,:,:3].astype(float);alpha=pixels[:,:,3]>0
        choices=[dict(index='badge',words=job['iconPaletteWords'])] if row['kind']=='icon' else job['portraitPalettes']
        options=[]
        for candidate in choices:
            colors=np.array([[((w>>s)&31)*255//31 for s in (0,5,10)] for w in candidate['words']])
            distances=((rgb[:,:,None,:]-colors[None,None,1:,:])**2).sum(axis=3)
            indices=distances.argmin(axis=2)+1;score=float(distances.min(axis=2)[alpha].mean())
            options.append((score,indices,colors,candidate))
        # Lowest color error is a proposal, not visual acceptance: skin, eyes
        # and cloth may merge despite a good score. The approval page compares
        # sampled and native versions; only its approved hashes may be imported.
        score,indices,colors,candidate=min(options,key=lambda x:x[0]);indices[~alpha]=0
        indexed=Image.fromarray(indices.astype('uint8'),'P');indexed.putpalette(colors.astype('uint8').ravel().tolist()+[0]*(768-colors.size));indexed.info['transparency']=0
        native=folder/(row['kind']+'-native.png');indexed.save(native)
        record=dict(job=job['job'],slug=job['slug'],kind=row['kind'],prompt=row.get('prompt',asset['prompt']),tool='image_gen.imagegen',model='Built-in, tool managed',
            references=[asset['template'],job['concept']]+([job['iconPalette']] if row['kind']=='icon' else []),
            generatedSource=dict(path=str(raw.relative_to(ROOT)),sha256=sha(raw.read_bytes()),size=list(sheet.size)),
            logicalSize=asset['logicalSize'],crop=crop,layoutNote=row.get('layoutNote','Requested bottom-right cell'),sampled=dict(path=str(sampled.relative_to(ROOT)),sha256=sha(sampled.read_bytes())),
            native=dict(path=str(native.relative_to(ROOT)),sha256=sha(native.read_bytes())),nativeSize=list(im.size),
            conversion='One nearest-neighbor sampling of fixed worksheet grid, fixed cell extraction, transparency threshold/connected flat background removal, existing native palette mapping. No bounding-box resizing, repositioning or painted repairs.',
            palette=candidate,paletteMatchError=score,status='new generation awaiting user visual review')
        results.append(record);cells.append((job['label']+' '+row['kind'],im,indexed.convert('RGBA')))
    (OUT/'results.json').write_text(json.dumps(dict(schema=1,assets=results),indent=2)+'\n')
    board=Image.new('RGBA',(800,((len(cells)+3)//4)*230),(228,226,220,255));draw=ImageDraw.Draw(board)
    for n,(label,im,native) in enumerate(cells):
        x=n%4*200;y=n//4*230;draw.text((x+4,y+4),label,fill='black')
        factor=3 if im.width==48 else 8
        board.alpha_composite(im.resize((im.width*factor,im.height*factor),Image.Resampling.NEAREST),(x+4,y+24))
        # Native-size palette-constrained result beside source magnification.
        board.alpha_composite(native,(x+150,y+150))
    board.save(OUT/'review-contact.png');print(json.dumps(dict(assets=len(results),review=str(OUT/'review-contact.png'))))
if __name__=='__main__':main()
