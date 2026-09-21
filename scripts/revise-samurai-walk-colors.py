"""Native-palette Samurai movement review; generated step revisions only."""
# Accepted recipe: src/art/native-ui-review/README.md, section 3. The combined
# sheet attempt is retained evidence, not the accepted correction. Use final
# individual-paths.json (including the p005 helmet retry) with ingest-individual.
# prepare is intentionally fresh-only; never overwrite an earlier prompt plan.
import json,sys,shutil,re,struct
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from native_art import ROOT,sha

OUT=ROOT/'build/art/samurai-walk-consistency-2026-09-20'
OLD=ROOT/'build/art/native-human-integration-2026-09-20/human-samurai'
def rec(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p.read_bytes()))
def prepare():
    OUT.mkdir(exist_ok=True);assert not (OUT/'plan.json').exists()
    sheet=Image.new('RGBA',(96,64));records=[]
    for n in range(6):
        p=OLD/f'p{n:03}.png';im=Image.open(p).convert('RGBA');sheet.alpha_composite(im,(n%3*32,n//3*32));records.append(rec(p))
    target=OUT/'movement-edit.png';sheet.resize((1152,768),Image.Resampling.NEAREST).save(target)
    palette=Image.open(OLD/'p001.png').getpalette()[:48]
    swatch=Image.new('RGB',(480,64));draw=ImageDraw.Draw(swatch)
    for i in range(16):draw.rectangle((i*30,0,i*30+29,63),fill=tuple(palette[i*3:i*3+3]))
    swatch.save(OUT/'native-colors.png')
    concept=ROOT/'build/art/approved-class-animation-2026-09-19/human-samurai/original-concept-user-reference.png'
    prompt='Edit this exact SIX-FRAME Samurai movement sheet for COLOR CONSISTENCY. Image 1 is the edit target: three 32x32 front poses on the top row, three 32x32 rear poses on the bottom row. The MIDDLE pose of each row is the accepted neutral color reference and must stay unchanged. Recolor the four OUTER step poses to match those middle frames. Keep every pose, limb placement, facial/eye shape, helmet silhouette, pixel grid, stride, cell spacing and transparency unchanged. Bright red lacquer armor with the same gold trim in all six; charcoal-black cloth sleeves and trousers; same small pale/yellow skin-colored face and exposed hands; the waist scarf stays the same MUTED mauve-gray from the middle frames, not red, white or blue. Do not change large sleeve/arm areas into skin: especially the screen-left arm in BOTTOM-RIGHT must retain the same dark sleeve and red shoulder armor as the bottom-middle, with only the small hand using skin colors. Keep gold shin guards consistent in every step. Lighting, highlights and material color ramps stay fixed across the cycle; no bright white flashes on armor or trousers. Image 2 is original costume/anatomy reference only: it shows charcoal trousers, dark sleeves and separate waist scarf; retain the already accepted muted scarf color of image 1. Image 3 contains the ONLY available native colors. Coarse actual 32x32 pixel-art per frame, no new fine detail. Return exactly the same 3-column 2-row sheet and canvas. Transparent background, no text, no extra frames.'
    (OUT/'plan.json').write_text(json.dumps(dict(prompt=prompt,references=[rec(target),rec(concept),rec(OUT/'native-colors.png')],sources=records,palette=palette,grid=[3,2],cell=[32,32],fixedPoses=['p001','p004'],revisedPoses=['p000','p002','p003','p005']),indent=2)+'\n')
    print(target)

def ingest(individual=False):
    plan=json.loads((OUT/'plan.json').read_text());receipt=json.loads((OUT/'generated-path.json').read_text(encoding='utf-8-sig'))
    raw=OUT/'generated-sheet.png';shutil.copy2(receipt['path'],raw)
    individual_rows=json.loads((OUT/'individual-paths.json').read_text(encoding='utf-8-sig')) if individual else []
    for row in individual_rows:
        for r in row.get('referenceHashes',[]):assert sha((ROOT/r['path']).read_bytes())==r['sha256']
    for r in plan['references']+plan['sources']:assert sha((ROOT/r['path']).read_bytes())==r['sha256']
    sheet=Image.open(raw).convert('RGBA').resize((96,64),Image.Resampling.NEAREST);sheet.save(OUT/'sampled-sheet.png')
    pal=np.array(plan['palette']).reshape(16,3);records=[]
    words=struct.unpack_from('<16H',(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes(),0x419d60+32)
    assert plan['palette']==[((w>>s)&31)*255//31 for w in words for s in (0,5,10)]
    board=Image.new('RGBA',(1152,460),'#e7e5df');draw=ImageDraw.Draw(board)
    for n in range(6):
        pose=f'p{n:03}';old=Image.open(OLD/(pose+'.png'));original=np.array(old)
        cell=sheet.crop((n%3*32,n//3*32,n%3*32+32,n//3*32+32))
        rawrec=None
        if individual and pose not in plan['fixedPoses']:
            r=next(r for r in individual_rows if r['pose']==pose);dest=OUT/(pose+'-generated.png');shutil.copy2(r['path'],dest)
            cell=Image.open(dest).convert('RGBA').resize((32,32),Image.Resampling.NEAREST);rawrec=rec(dest)
            if 'registration' in r:
                # Recorded integer registration corrects a known model offset
                # (p002/p003: one row down). Do not auto-fit the opaque bounds;
                # that would change frame alignment and hide generation drift.
                dx,dy=r['registration']['offset'];cell=cell.transform((32,32),Image.Transform.AFFINE,(1,0,-dx,0,1,-dy),Image.Resampling.NEAREST)
        cell.save(OUT/(pose+'-sampled.png'))
        # p001/p004 are immutable material-color references, not regeneration
        # candidates. A common palette alone cannot keep armor/sleeve/skin
        # assignments consistent; visually inspect every converted step too.
        if pose in plan['fixedPoses']:native=old.copy()
        else:
            rgb=np.array(cell)[:,:,:3].astype(float)
            idx=(((rgb[:,:,None,:]-pal[None,None,1:,:])**2).sum(3).argmin(2)+1).astype('uint8')
            # Color-only import: preserve original opaque footprint/contact shadow.
            # Quantize opaque pixels against indices 1..15 only; restore index
            # zero from the old footprint so a pale model background cannot
            # become new silhouette pixels. Shape edits need a separate review.
            idx[original==0]=0
            native=Image.fromarray(idx);native.putpalette(old.getpalette());native.info['transparency']=0
        dest=OUT/(pose+'-native.png');native.save(dest,bits=4)
        arr=np.array(native);assert np.array_equal(arr==0,original==0)
        assert native.getpalette()[:48]==plan['palette']
        if pose in plan['fixedPoses']:assert np.array_equal(arr,original)
        records.append(dict(pose=pose,source=plan['sources'][n],native=rec(dest),sampled=rec(OUT/(pose+'-sampled.png')),raw=rawrec,registration=r.get('registration') if rawrec else None,changedPixels=int((arr!=original).sum()),originalAlphaPreserved=True))
        draw.text((n*192+5,4),pose,fill='black')
        for row,im in enumerate([old,native]):board.alpha_composite(im.convert('RGBA').resize((192,192),Image.Resampling.NEAREST),(n*192,25+row*215))
    board.save(OUT/'native-comparison.png')
    (OUT/'results.json').write_text(json.dumps(dict(records=records,rejectedSheet=rec(raw) if individual else None,generationReceipts=individual_rows,plan=rec(OUT/'plan.json'),nativePaletteSelector=1,nativePaletteWords=words,method='Generated color reference, fixed grid nearest sampling and recorded integer registration, native palette quantization. Original alpha/contact footprint retained; neutral indices unchanged. Offline proposal only.'),indent=2)+'\n')
    print([(r['pose'],r['changedPixels']) for r in records])

def build():
    base=ROOT/'build/art/job-art-approval-v7-2026-09-20';dest=ROOT/'build/art/job-art-approval-v8-2026-09-20'
    dest.mkdir(exist_ok=True);shutil.copytree(base/'assets',dest/'assets',dirs_exist_ok=True)
    for name in ('export-proof.json','regeneration-proof.json','revision-proof.json','anchor-verification.json','targeted-verification.json'):shutil.copy2(base/name,dest/name)
    data=json.loads((base/'review-data.json').read_text());original=json.loads((base/'review-data.json').read_text());results=json.loads((OUT/'results.json').read_text())
    unit=next(u for u in data['units'] if u['job']==116);prior=next(u for u in original['units'] if u['job']==116)
    references=[]
    for r in results['records']:
        p=next(p for p in unit['poses'] if p['id']==r['pose'])
        new=np.array(Image.open(ROOT/r['native']['path']));old=np.array(Image.open(ROOT/r['source']['path']))
        assert np.array_equal(new==0,old==0)
        if r['pose'] in ('p001','p004'):assert np.array_equal(new,old);continue
        p['previousGameTileSha256']=p['sha256'];p['sha256']=sha(new.tobytes());p['proposal']='Color consistency revision, not yet imported into ROM.'
        for side in ('ally','enemy'):
            oldim=Image.open(base/p['images'][side]);arr=np.array(oldim);assert np.array_equal(arr[12:44,16:48],old)
            arr[12:44,16:48]=new;im=Image.fromarray(arr);im.putpalette(oldim.getpalette());im.info['transparency']=0
            name='assets/human-samurai-'+r['pose']+'-colors-v8-'+side+'.png';im.save(dest/name);p['images'][side]=name
            references.append(dict(path=name,sha256=sha((dest/name).read_bytes())))
    data['latest']=[]
    for start,label in ((0,'Front walk'),(3,'Rear walk')):
        pair={}
        for stage in ('before','after'):
            strip=Image.new('RGBA',(96,32))
            for n in range(3):
                path=OLD/f'p{start+n:03}.png' if stage=='before' else OUT/f'p{start+n:03}-native.png'
                strip.alpha_composite(Image.open(path).convert('RGBA'),(n*32,0))
            name=f'assets/samurai-walk-{start}-{stage}.png';strip.save(dest/name);pair[stage]=name
        data['latest'].append(dict(slug='human-samurai',label=label+' · three keyframes',width=96,height=32,scale=4,**pair))
    data['round']=8;data['status']='Four Samurai movement color proposals; no ROM change.'
    changed=[]
    for u,old in zip(data['units'],original['units']):
        assert u['sequences']==old['sequences'] and u['emptySlots']==old['emptySlots']
        for p,q in zip(u['poses'],old['poses']):
            if p!=q:changed.append((u['job'],p['id']))
        for key in ('newPortrait','newIcon','badges'):assert u[key]==old[key]
    assert set(changed)=={(116,k) for k in ('p000','p002','p003','p005')}
    html=(base/'index.html').read_text(encoding='utf-8');html=re.sub(r'const DATA=.*?;\nconst E=',lambda _: 'const DATA='+json.dumps(data).replace('</','<\\/')+';\nconst E=',html,flags=re.S)
    html=html.replace('Round 07','Round 08').replace('One focused Samurai badge revision: removing the small inward-pointing lower helmet tips while retaining the frontal face.','Samurai movement color review: four stepping poses revised against the accepted front and rear neutral frames. The two neutral frames are unchanged. The shared native palette and all animation timings are retained.')
    html=html.replace('Latest revisions · before and after','Samurai walking colors · before and after')
    html=html.replace('Export checked:','Original-build export, before these movement revisions:')
    html=html.replace('Portraits and icons below are proposals; game screenshots and animations show the previous assembled build.','Portraits and icons remain proposals. Samurai poses p000, p002, p003 and p005 now show color-revision proposals wherever reused; all other animation poses and game screenshots show the previous assembled build.')
    html=html.replace("section.append(E('h3',{},'3 · Animations and keyframes'));","if(u.job===116)section.append(E('p',{class:'notice'},'Walking color proposals: p000, p002, p003 and p005 revised; neutral p001/p004 unchanged. These images are not yet imported into the game. Other Samurai action poses still await visual approval.'));section.append(E('h3',{},'3 · Animations and keyframes'));")
    (dest/'review-data.json').write_text(json.dumps(data,indent=2)+'\n');(dest/'index.html').write_text(html,encoding='utf-8')
    (dest/'page-script.js').write_text(re.search('<script>(.*?)</script>',html,re.S)[1],encoding='utf-8')
    shutil.copy2(OUT/'results.json',dest/'movement-revision.json');shutil.copy2(OUT/'individual-plan.json',dest/'movement-prompts.json')
    html=(dest/'index.html').read_text(encoding='utf-8').replace('<footer>','<footer><a href="movement-revision.json">Movement revision records</a> · <a href="movement-prompts.json">Movement edit prompts</a> · ',1);(dest/'index.html').write_text(html,encoding='utf-8')
    def visit(x):
        if isinstance(x,dict):
            for v in x.values():visit(v)
        elif isinstance(x,list):
            for v in x:visit(v)
        elif isinstance(x,str) and x.startswith('assets/'):assert (dest/x).is_file(),x
    visit(data)
    oldarm=np.array(Image.open(OLD/'p005.png'))[16:22,7:14];newarm=np.array(Image.open(OUT/'p005-native.png'))[16:22,7:14]
    arm=dict(region=[7,16,14,22],paleBefore=int(np.isin(oldarm,[3,10,11]).sum()),paleAfter=int(np.isin(newarm,[3,10,11]).sum()),scope='Diagnostic sleeve/hand region, not a universal material classifier.')
    assert arm['paleAfter']<arm['paleBefore']
    proof=dict(changedPoses=changed,neutralFramesUnchanged=True,originalAlphaPreserved=True,nativePaletteUnchanged=True,sequenceRecordsUnchanged=True,otherArtUnchanged=True,counts=data['counts'],reviewFiles=references,markedArm=arm,runtimeTestRun=False)
    (dest/'movement-verification.json').write_text(json.dumps(proof,indent=2)+'\n');print(dest/'index.html')

if __name__=='__main__':{'prepare':prepare,'ingest':ingest,'ingest-individual':lambda:ingest(True),'build':build}[sys.argv[1]]()
