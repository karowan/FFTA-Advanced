"""Native-derived face anchors, generation receipts, and palette-only review conversion."""
# Shared-anchor procedure and accepted later refinements are documented in
# src/art/native-ui-review/README.md, section 4. This file retains the original
# single-head trial as well as the row workflow; the final approval receipt,
# not this script's round number, determines which generated assets are used.
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image
from native_art import ROOT, sha

OUT=ROOT/'build/art/anchor-ui-v4-2026-09-20'
OLD=ROOT/'build/art/native-ui-regeneration-v2-2026-09-20'
R3=ROOT/'build/art/native-ui-revision-v3-2026-09-20'
FIRST=ROOT/'build/art/job-art-approval-2026-09-20'
RACES={'human':([2,4,7,9],[6,7,12,11]),'bangaa':([13,15,16,18],[6,7,12,14]),
       'nu-mou':([20,22,23,27],[4,7,13,14]),'moogle':([37,36,39,41],[5,8,13,13]),
       'viera':([28,29,31,33],[7,6,11,10])}

def rec(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p.read_bytes()))
def enlarge(im,p,scale=48):im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST).save(p);return rec(p)

def prepare():
    assert not (OUT/'plan.json').exists(), 'Preserve existing prompts, references and generation receipts'
    OUT.mkdir(exist_ok=True);plan=json.loads((OLD/'plan.json').read_text());rows=[];contracts={}
    for race,(ids,box) in RACES.items():
        src=[ROOT/f'build/art/native-reference/ui/job-{j:03}.png' for j in ids]
        heads=[Image.open(p).crop((1,1,17,15)) for p in src]
        a=np.array([np.array(im) for im in heads]);mask=(a==a[0]).all(0)
        roi=np.zeros((14,16),bool);x1,y1,x2,y2=box;roi[y1:y2,x1:x2]=True;mask &= roi
        # Only unchanged pixels agreed by all original jobs; no invented face art.
        coords=[[int(x),int(y),int(a[0,y,x])] for y,x in zip(*np.where(mask))]
        layer=Image.new('RGBA',(16,14))
        for x,y,_ in coords:layer.putpixel((x,y),heads[0].convert('RGBA').getpixel((x,y)))
        layer.save(OUT/(race+'-shared-pixels.png'))
        refs=Image.new('RGBA',(64,14))
        for n,im in enumerate(heads):refs.paste(im.convert('RGBA'),(n*16,0))
        contracts[race]=dict(references=[rec(p) for p in src],crop=[1,1,17,15],faceRegion=box,
            coordinates=coords,referenceStrip=enlarge(refs,OUT/(race+'-references.png'),20),
            layer=enlarge(layer,OUT/(race+'-anchor-layer.png')),frontalTemplate=enlarge(heads[0].convert('RGBA'),OUT/(race+'-frontal-template.png')),
            scope='Exact indexed-pixel agreement within the stated facial region of these four jobs only; not a universal race mask.')
    for j in plan['jobs']:
        slug=j['slug'];race=next(r for r in RACES if slug.startswith(r+'-'));c=contracts[race]
        f=OUT/slug;f.mkdir(exist_ok=True)
        first=Image.open(FIRST/'assets'/(slug+'-badge-eligible.png')).convert('RGBA').crop((1,1,17,15))
        identity=enlarge(first,f/'first-sprite-head.png')
        helmet=j['job'] in (117,119)
        prompt=(f'Create the {j["label"]} equipment HEAD icon, facing DIRECTLY toward the camera, symmetrically frontal like image 1. '
            'Use the exact 16 by 14 pixel layout of image 1, especially its eye row, eye spacing, head center and chin baseline. '
            'Image 2 is the character identity from its approved sprite; image 3 shows four original same-race icons; image 4 is its costume concept. '
            'Use the native colors of image 2. Image 5 shows the shared face pixels that stay fixed. '
            'Make the distinctive headgear recognizable around the common facial layout. Simple bold pixel clusters, no fine detail. '
            'Return ONE 16 by 14 logical-pixel head enlarged with hard square pixels, filling the SAME canvas as image 1. No body, lettering or border. Pale cream background. ')
        if helmet:
            prompt+='Closed helmet variant: use the same eye positions and frontal head center but hide all skin and nose. Two simple golden round eyes in black helmet darkness. Blue cloth emerges behind the helmet. Do not copy the exposed face pixels from image 5.'
        rows.append(dict(job=j['job'],slug=slug,race=race,kind='icon',nativeSize=[16,14],prompt=prompt,
            references=[c['frontalTemplate'],identity,c['referenceStrip'],j['concept'],c['layer']],
            paletteWords=j['iconPaletteWords'],anchorMode='helmet-landmarks-only' if helmet else 'exact-shared-native-pixels',anchors=c))
        if j['job'] in (117,125):
            target=enlarge(Image.open(R3/slug/'portrait-sampled.png').convert('RGBA'),f/'portrait-edit-target.png',16)
            if j['job']==117:
                fft=OUT/'fft-dark-knight-user-reference.png'
                if not fft.is_file():
                    raise FileNotFoundError(f'Supply the original user reference at {fft}; it is a private input, not a machine clipboard path.')
                prompt='Edit image 1. Inside the helmet use exactly TWO simple solid golden circular eyes in a completely black void, like the FFT Dark Knight in image 2. No human face, nose, eyelids, eyebrows, pupils, whites or realistic eyes. Keep the helmet, gold trim, blue cloth behind it and framing unchanged. Coarse 48 by 56 pixel portrait, with eyes that remain clear at that resolution. Return only the same single pixel portrait with transparent background.'
                refs=[target,rec(fft)]
            else:
                refs=[target]+j['assets'][0]['refs'][:3]+[j['concept']]
                prompt='Repair the face in image 1, the Viera Mystic Knight portrait. Use the original Viera portraits in images 2 through 4 as the facial anatomy and pixel-cluster reference. Image 5 is the character concept. A clean coherent face with two readable eyes, a small nose and a CLEAR small dark mouth separated from the chin. Keep the long ears, white hair, armor, blue cloth, identity and framing unchanged. Design directly at 48 by 56 pixels so the mouth and eyes survive at native size. No tiny subpixel details. Return only the single portrait with transparent background.'
            rows.append(dict(job=j['job'],slug=slug,kind='portrait',nativeSize=[48,56],prompt=prompt,references=refs,paletteChoices=j['portraitPalettes']))
    (OUT/'plan.json').write_text(json.dumps(dict(assets=rows,contracts=contracts),indent=2)+'\n')
    print('Prepared',len(rows),'assets; shared facial pixels:',{k:len(v['coordinates']) for k,v in contracts.items()})

def ingest():
    plan=json.loads((OUT/'plan.json').read_text());paths=json.loads((OUT/'generated-paths.json').read_text(encoding='utf-8-sig'));results=[]
    for original in plan['assets']:
        matches=[r for r in paths if (r['slug'],r['kind'])==(original['slug'],original['kind'])]
        if not matches:continue
        r=matches[-1];a={**original,**r.get('revision',{})};f=OUT/a['slug'];raw=f/r.get('rawName','generated-'+a['kind']+'.png')
        if raw.exists():assert raw.read_bytes()==Path(r['path']).read_bytes()
        else:shutil.copy2(r['path'],raw)
        for ref in a['references']:assert sha((ROOT/ref['path']).read_bytes())==ref['sha256']
        im=Image.open(raw).convert('RGBA')
        if 'worksheetBox' in a:im=im.crop(tuple(a['worksheetBox']))
        method=Image.Resampling.BOX if a.get('sampling')=='area' else Image.Resampling.NEAREST
        im=im.resize(tuple(a.get('logicalSize',a['nativeSize'])),method)
        if 'crop' in a:im=im.crop(tuple(a['crop']))
        if 'registration' in a:
            # A declared transform aligns known landmarks. Preserve the raw
            # image and transform in evidence; do not silently fit a head to
            # detected bounds, or each job will acquire a different face scale.
            reg=a['registration']
            if 'affine' in reg:im=im.transform(tuple(a['nativeSize']),Image.Transform.AFFINE,tuple(reg['affine']),resample=Image.Resampling.NEAREST)
            else:
                part=im.resize(tuple(reg['size']),Image.Resampling.NEAREST)
                im=Image.new('RGBA',tuple(a['nativeSize']));im.alpha_composite(part,tuple(reg['offset']))
        im.putalpha(im.getchannel('A').point(lambda p:255 if p>=128 else 0));sampled=f/(a['kind']+'-sampled.png');im.save(sampled)
        pix=np.array(im);alpha=pix[:,:,3]>0;options=[]
        for c in a.get('paletteChoices',[dict(words=a.get('paletteWords'))]):
            pal=np.array([[((w>>s)&31)*255//31 for s in (0,5,10)] for w in c['words']])
            dist=((pix[:,:,:3].astype(float)[:,:,None,:]-pal[None,None,1:,:])**2).sum(3)
            options.append((float(dist.min(2)[alpha].mean()),dist.argmin(2)+1,pal,c))
        score,idx,pal,c=min(options,key=lambda x:x[0]);idx[~alpha]=0
        proof={}
        if a.get('anchorMode')=='exact-shared-native-pixels':
            # These are authenticated common pixels from original race icons,
            # not hand-authored facial repairs. A sparse mask cannot detect
            # extra eyes beside its coordinates: inspect the entire inner face
            # and use the later verification checks before accepting the result.
            coords=a.get('conversionAnchors',a['anchors'])['coordinates'];before=sum(int(idx[y,x])==v for x,y,v in coords)
            for x,y,v in coords:idx[y,x]=v
            assert all(int(idx[y,x])==v for x,y,v in coords)
            proof=dict(count=len(coords),matchingBefore=before,matchingAfter=len(coords))
        if a.get('anchorMode')=='helmet-landmarks-only':
            # Closed helmets must NOT inherit an exposed-skin face mask. Check
            # generated gold eye positions without painting substitute eyes.
            expected={(7,7),(10,7)}
            if a['slug']=='human-dark-knight':expected|={(7,8),(10,8)}
            actual={(x,y) for y in (7,8) for x in range(5,12) if idx[y,x]==7}
            assert actual==expected,(a['slug'],'Helmet eye-anchor mismatch',actual,expected)
            proof=dict(count=len(expected),matchingAfter=len(expected),goldEyeCoordinates=sorted(expected),
                       method='Generated eye pixels validated at native eye columns 7 and 10; no face pixels composited into helmets.')
        native=Image.fromarray(idx.astype('uint8'));native.putpalette(pal.flatten().tolist()+[0]*(768-pal.size));native.info['transparency']=0
        path=f/(a['kind']+'-native.png');native.save(path)
        results.append(dict(**a,raw=rec(raw),sampled=rec(sampled),native=rec(path),palette=c,paletteError=score,anchorProof=proof,
            tool='image_gen.imagegen',model='Tool managed',conversion='Declared grid sampling and optional recorded registration, then native palette conversion. Exposed faces restore only exact indexed pixels shared by the recorded native references. Helmet landmarks require visual review.'))
    (OUT/'results.json').write_text(json.dumps(dict(assets=results,contracts=plan['contracts']),indent=2)+'\n');print('Converted',len(results),'assets')

def prepare_rows():
    """Recreate the final geometry worksheet without overwriting a generation plan."""
    trial=json.loads((ROOT/'src/art/native-ui-review/round4/single-head-plan-rejected.json').read_text())
    for a in trial['assets']:
        if a['kind']!='icon':continue
        refs=a['references'];strip=Image.open(ROOT/refs[2]['path']).convert('RGBA').resize((64,14),Image.Resampling.NEAREST)
        head=Image.open(ROOT/refs[0]['path']).convert('RGBA').resize((16,14),Image.Resampling.NEAREST)
        sheet=Image.new('RGBA',(80,14));sheet.paste(strip,(0,0));sheet.paste(head,(64,0))
        path=OUT/a['slug']/'anchor-worksheet.png';enlarged=sheet.resize((1600,280),Image.Resampling.NEAREST)
        if path.exists():assert np.array_equal(np.array(Image.open(path)),np.array(enlarged))
        else:enlarged.save(path)
    print('Ten original-reference worksheets verified/prepared; generation plans preserved.')

if __name__=='__main__':
    if sys.argv[1]=='prepare-single-head-trial':prepare()
    elif sys.argv[1]=='prepare-rows':prepare_rows()
    elif sys.argv[1]=='ingest':ingest()
    else:raise SystemExit('Use ingest with the preserved round4 plan and generation receipts. prepare-single-head-trial reproduces the rejected initial experiment only.')
