"""Prepare sprite-derived head edits and targeted portrait eye repairs."""
import json,shutil,sys
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
from native_art import ROOT,sha

OUT=ROOT/'build/art/native-ui-revision-v3-2026-09-20'
OLD=ROOT/'build/art/native-ui-regeneration-v2-2026-09-20'
BASE=ROOT/'build/art/job-art-approval-2026-09-20'

def rec(p):return dict(path=str(p.relative_to(ROOT)),sha256=sha(p.read_bytes()))
def prepare():
    OUT.mkdir(exist_ok=True);plan=json.loads((OLD/'plan.json').read_text());rows=[]
    for j in plan['jobs']:
        slug=j['slug'];folder=OUT/slug;folder.mkdir(exist_ok=True)
        # First reviewed badge, which was extracted from the approved actor.
        head=Image.open(BASE/'assets'/(slug+'-badge-eligible.png')).convert('RGBA').crop((1,1,17,15))
        target=folder/'icon-edit-target.png';head.resize((768,672),Image.Resampling.NEAREST).save(target)
        refs=Image.new('RGBA',(64,14),(255,255,238,255))
        for n,r in enumerate(j['assets'][1]['refs']):
            native_job=int(Path(r['path']).name.split('-')[1])
            clean=Image.open(ROOT/f'build/art/native-reference/ui/job-{native_job:03}.png').convert('RGBA').crop((1,1,17,15))
            refs.paste(clean,(n*16,0))
        refpath=folder/'clean-race-icons.png';refs.resize((1536,336),Image.Resampling.NEAREST).save(refpath)
        prompt=(f'Edit image 1, the sprite-based {j["label"]} equipment head icon. Preserve its recognizable costume and distinct silhouette. '
                'Match the clean original same-race job icons in image 2: head proportions, face direction, eye shape, clear solid pixel clusters. '
                'Keep the original sprite detail; do not turn it into a big generic cartoon face. The output is just ONE head on the same 16 by 14 logical pixel grid as image 1, enlarged with hard square pixels. '
                'Use only the native colors in image 3. Keep the silhouette completely inside the canvas. Transparent background, no checkerboard, letters or border.')
        if j['job'] in (117,119):prompt+=' Closed helmet; read as helmet, not multiple eyes. Blue cloth trails behind the helmet.'
        rows.append(dict(job=j['job'],slug=slug,kind='icon',nativeSize=[16,14],prompt=prompt,references=[rec(target),rec(refpath),j['iconPalette']],paletteWords=j['iconPaletteWords']))
        if j['job'] in (117,125):
            target=folder/'portrait-edit-target.png';Image.open(OLD/slug/'portrait-sampled.png').resize((768,896),Image.Resampling.NEAREST).save(target)
            if j['job']==117:
                prompt='Edit only the eye opening in this Human Dark Knight pixel portrait. The three pale vertical marks look like three eyes. Replace them with an anatomically correct pair of small eyes in a dark, narrow visor opening, separated by the nose bridge; the farther eye is narrower. No other eye-like bars or highlights. Keep the closed helmet, gold trim, blue cloth behind it, pose, silhouette and everything else unchanged. Preserve the 48 by 56 logical pixel grid, hard square pixels and transparent background. Return only the same single portrait.'
            else:
                prompt='Correct the eyes in this Viera Mystic Knight pixel portrait. Make a natural coherent pair of eyes looking in the same direction: one clear near eye and a smaller far eye with proper perspective. Remove the stray dark eye-shaped mark near the nose/hair on the left side of the face. Keep the face identity, ears, hair, costume, pose and all other details unchanged. Preserve the 48 by 56 logical pixel grid, hard square pixels and transparent background. Return only the same single portrait.'
            rows.append(dict(job=j['job'],slug=slug,kind='portrait',nativeSize=[48,56],prompt=prompt,references=[rec(target)],paletteChoices=j['portraitPalettes']))
    path=OUT/'plan.json';assert not path.exists(),'Preserve prior generation inputs'
    path.write_text(json.dumps(dict(assets=rows),indent=2)+'\n');print(path)

def ingest():
    plan=json.loads((OUT/'plan.json').read_text());paths=json.loads((OUT/'generated-paths.json').read_text(encoding='utf-8-sig'));results=[]
    for a in plan['assets']:
        r=next(x for x in paths if (x['slug'],x['kind'])==(a['slug'],a['kind']))
        a={**a,**r.get('revision',{})}
        folder=OUT/a['slug'];raw=folder/r.get('rawName','generated-'+a['kind']+'.png')
        if raw.exists():assert raw.read_bytes()==Path(r['path']).read_bytes()
        else:shutil.copy2(r['path'],raw)
        for ref in a['references']:assert sha((ROOT/ref['path']).read_bytes())==ref['sha256']
        im=Image.open(raw).convert('RGBA').resize(tuple(a['nativeSize']),Image.Resampling.NEAREST)
        im.putalpha(im.getchannel('A').point(lambda p:255 if p>=128 else 0))
        sampled=folder/(a['kind']+'-sampled.png');im.save(sampled)
        pix=np.array(im);alpha=pix[:,:,3]>0;choices=a.get('paletteChoices',[dict(words=a.get('paletteWords'))]);options=[]
        for c in choices:
            pal=np.array([[((w>>s)&31)*255//31 for s in (0,5,10)] for w in c['words']])
            dist=((pix[:,:,:3].astype(float)[:,:,None,:]-pal[None,None,1:,:])**2).sum(3)
            idx=dist.argmin(2)+1;options.append((float(dist.min(2)[alpha].mean()),idx,pal,c))
        score,idx,pal,c=min(options,key=lambda x:x[0]);idx[~alpha]=0
        native=Image.fromarray(idx.astype('uint8'));native.putpalette(pal.flatten().tolist()+[0]*(768-pal.size));native.info['transparency']=0
        path=folder/(a['kind']+'-native.png');native.save(path)
        results.append(dict(**a,raw=rec(raw),sampled=rec(sampled),native=rec(path),palette=c,paletteError=score,tool='image_gen.imagegen',model='Tool managed',conversion='Single fixed-grid nearest sampling, alpha threshold, existing native palette only; no bbox fitting or painted repairs.'))
    (OUT/'results.json').write_text(json.dumps(dict(assets=results),indent=2)+'\n');print('Converted',len(results),'assets')

if __name__=='__main__':prepare() if sys.argv[1]=='prepare' else ingest()
