"""Historical correction recipes; v2-v4 misidentified scarf as trousers.

Use the original concept in all future revisions. No art is drawn by code.
"""
import copy
import argparse
import json
import runpy
import shutil
from PIL import Image, ImageDraw

H=runpy.run_path(__file__.replace('prepare-animation-consistency.py','assemble-class-animation.py'))
ROOT,OUT=H['ROOT'],H['OUT']


def main():
    m=H['read']();queue=[]
    for slug,facing,correction in [
        ('human-samurai','front','Match the pants on the RIGHT sprite to the LEFT reference: the same dark teal fabric, the same teal shadows and highlights. Keep red armor panels separate from the pants. Preserve the right walking pose and all other details.'),
        ('nu-mou-chemist','back','Make the entire head and hood of the RIGHT sprite identical in size, silhouette, features and colors to the LEFT reference. Move that unchanged head as a rigid unit if the walking bob requires it. Preserve the right walking legs, apron and satchel.')]:
        u=next(u for u in m['units'] if u['slug']==slug)
        anchor=OUT/slug/(facing+'-neutral.png')
        for pose in u['poses']:
            if pose['id'] not in (facing+'-step-a',facing+'-step-b'):continue
            if pose.get('consistencyRevision'):raise SystemExit('Already prepared; use saved manifest to resume.')
            old=copy.deepcopy(pose)
            snapshot=OUT/slug/(pose['id']+'-before-consistency.png')
            shutil.copy2(ROOT/pose['output'],snapshot);old['output']=str(snapshot.relative_to(ROOT))
            target=Image.open(snapshot).convert('RGBA')
            board=Image.new('RGBA',(96,48),H['BG'])
            board.alpha_composite(Image.open(anchor).convert('RGBA'),(8,8));board.alpha_composite(target,(64,8))
            template=OUT/slug/(pose['id']+'-consistency-v2-template.png')
            board.resize((1536,768),Image.Resampling.NEAREST).save(template)
            pose['previousGeneration']=old
            for key in ['designReference','designReferenceSha256','reusedFrom']:
                pose.pop(key,None)
            pose.update(consistencyRevision=2,status='ready',template=str(template.relative_to(ROOT)),templateSha256=H['sha'](template),
                        anchor=str(anchor.relative_to(ROOT)),anchorSha256=H['sha'](anchor),
                        source=str((OUT/slug/(pose['id']+'-consistency-v2-generated.png')).relative_to(ROOT)),
                        prompt=correction+' Keep the two-sprite layout and pixel grid unchanged. Change only the right sprite.',
                        workbenchSpec=dict(grid=[96,48],crop=[64,8,96,40],strip=[64,0,96,48]),
                        generationInputs='One worksheet: left neutral costume/anatomy reference; right existing pose to edit. Native references retained as provenance only.')
            queue.append(dict(slug=slug,id=pose['id'],template=pose['template'],source=pose['source'],prompt=pose['prompt']))
    H['save'](m);print(json.dumps(queue))


def restore_stride():
    """Use original walking poses as edit targets and a fabric crop as color reference."""
    m=H['read']();u=next(u for u in m['units'] if u['slug']=='human-samurai');folder=OUT/u['slug']
    if any(p.get('consistencyRevision',0)>=3 for p in u['poses']):
        raise SystemExit('Stride revision already prepared; resume from manifest.')
    color=folder/'pants-color-reference-v3.png'
    Image.open(folder/'front-neutral.png').convert('RGBA').crop((15,21,18,26)).resize((384,640),Image.Resampling.NEAREST).save(color)
    prompt='Edit image 1: recolor only the trousers to the dark teal colors sampled in image 2. Keep every shape and pixel position in image 1 unchanged, especially its bent legs, foot placement, arm swing and pants silhouette. This is a color-only edit of the existing walking frame. Preserve the square canvas, pixel grid and background. Return only image 1.'
    for pose in u['poses']:
        if pose['id'] not in ['front-step-a','front-step-b']:continue
        old=copy.deepcopy(pose);snapshot=folder/(pose['id']+'-consistency-v2.png')
        shutil.copy2(ROOT/pose['output'],snapshot);old['output']=str(snapshot.relative_to(ROOT))
        anchor=folder/(pose['id']+'-before-consistency.png')
        board=Image.new('RGBA',(32,32),H['BG']);board.alpha_composite(Image.open(anchor).convert('RGBA'))
        template=folder/(pose['id']+'-color-only-v3-template.png')
        board.resize((1024,1024),Image.Resampling.NEAREST).save(template)
        pose.update(previousGeneration=old,consistencyRevision=3,status='ready',prompt=prompt,
                    anchor=str(anchor.relative_to(ROOT)),anchorSha256=H['sha'](anchor),
                    template=str(template.relative_to(ROOT)),templateSha256=H['sha'](template),
                    designReference=str(color.relative_to(ROOT)),designReferenceSha256=H['sha'](color),
                    source=str((folder/(pose['id']+'-color-only-v3-generated.png')).relative_to(ROOT)),
                    workbenchSpec=dict(grid=[32,32],crop=[0,0,32,32],strip=[0,0,32,32]),
                    generationInputs='Image 1: original walking step edit target. Image 2: neutral-frame fabric crop [15,21,18,26], color only; no neutral-body pose supplied.')
    H['save'](m)


def restore_equipment():
    """Correct the wide step's missing equipment without changing its stride."""
    m=H['read']();u=next(u for u in m['units'] if u['slug']=='human-samurai');folder=OUT/u['slug']
    pose=next(p for p in u['poses'] if p['id']=='front-step-b')
    if pose.get('consistencyRevision',0)>=4:raise SystemExit('Equipment revision already prepared; resume from manifest.')
    old=copy.deepcopy(pose);anchor=folder/'front-step-b-consistency-v3.png'
    shutil.copy2(ROOT/pose['output'],anchor);old['output']=str(anchor.relative_to(ROOT))
    template=folder/'front-step-b-equipment-v4-template.png';reference=folder/'lower-costume-v4-reference.png'
    for source,target,box in [(anchor,template,(0,0,32,32)),(folder/'front-neutral.png',reference,(8,18,24,31))]:
        im=Image.open(source).convert('RGBA').crop(box);bg=Image.new('RGBA',im.size,H['BG']);bg.alpha_composite(im)
        bg.resize((im.width*32,im.height*32),Image.Resampling.NEAREST).save(target)
    pose.update(previousGeneration=old,consistencyRevision=4,status='ready',
                prompt="Keep the exact wide walking pose of image 1. Restore the red lacquer thigh-armor panels on the outer sides of BOTH teal pant legs, and the gold ankle bands and off-white toe caps shown in image 2. The forward leg must not become entirely blue: its red armor travels with the leg. Image 2 is equipment/color reference only, NOT a pose reference. Keep image 1's foot positions, bent knees, silhouette, upper body and 32-by-32 pixel grid unchanged. Return only image 1 on its same canvas.",
                anchor=str(anchor.relative_to(ROOT)),anchorSha256=H['sha'](anchor),
                template=str(template.relative_to(ROOT)),templateSha256=H['sha'](template),
                designReference=str(reference.relative_to(ROOT)),designReferenceSha256=H['sha'](reference),
                source=str((folder/'front-step-b-equipment-v4-generated.png').relative_to(ROOT)),
                workbenchSpec=dict(grid=[32,32],crop=[0,0,32,32],strip=[0,0,32,32]),
                generationInputs='Image 1: v3 wide walking step edit target. Image 2: neutral lower-costume crop [8,18,24,31], equipment and colors only.')
    H['save'](m)


def restore_concept():
    """Correct scarf/trouser interpretation with the original concept in every call."""
    m=H['read']();u=next(u for u in m['units'] if u['slug']=='human-samurai');folder=OUT/u['slug']
    if any(p.get('consistencyRevision',0)>=5 for p in u['poses']):raise SystemExit('Concept correction already prepared; resume from manifest.')
    concept=folder/'original-concept-user-reference.png'
    assert concept.exists(),'Copy the user-provided original concept into this path first.'
    prompts={'front-step-a':"In image 1, make the pants charcoal, not blue. The teal is a loose waist scarf (see the original design in image 2). Keep image 1's running step with one foot tucked behind the other, and everything else unchanged. Edit image 1 only.",'front-step-b':"In image 1, make the pants charcoal, not blue. The teal is a loose waist scarf (see the original design in image 2). Keep image 1's wide walking step with its feet apart, and everything else unchanged. Edit image 1 only."}
    for pose in u['poses']:
        if pose['id'] not in prompts:continue
        old=copy.deepcopy(pose);anchor=folder/(pose['id']+'-before-concept-v5.png')
        shutil.copy2(ROOT/pose['output'],anchor);old['output']=str(anchor.relative_to(ROOT))
        template=folder/(pose['id']+'-concept-v5-template.png')
        bg=Image.new('RGBA',(32,32),H['BG']);bg.alpha_composite(Image.open(anchor).convert('RGBA'))
        bg.resize((1024,1024),Image.Resampling.NEAREST).save(template)
        stem=pose['id']+'-concept-v5'+('-attempt3' if pose['id']=='front-step-a' else '')+'-generated.png'
        pose.update(previousGeneration=old,consistencyRevision=5,status='ready',prompt=prompts[pose['id']],
                    anchor=str(anchor.relative_to(ROOT)),anchorSha256=H['sha'](anchor),
                    template=str(template.relative_to(ROOT)),templateSha256=H['sha'](template),
                    designReference=str(concept.relative_to(ROOT)),designReferenceSha256=H['sha'](concept),
                    source=str((folder/stem).relative_to(ROOT)),
                    workbenchSpec=dict(grid=[32,32],crop=[0,0,32,32],strip=[0,0,32,32]),
                    generationInputs='Image 1: existing walking sprite. Image 2: complete original user-provided concept art; authoritative garment identity and colors.',
                    garmentInterpretation='Dark charcoal trousers. Teal waist scarf and hanging tails are separate fabric, not trouser legs. Red armor, gold shin guards, cream sandal straps.')
        if pose['id']=='front-step-a':
            rejected=[]
            for filename,prompt,reason in [
                ('front-step-a-concept-v5-generated.png',"Correct the costume of the walking sprite in image 1 using the ORIGINAL concept art in image 2. The trousers are dark charcoal, NEVER blue. Teal is ONLY the waist scarf and its separate hanging tails. Retain red skirt armor, gold shin guards and cream sandal straps from the concept. Keep image 1's exact walking pose, foot positions, arm swing, head, proportions and 32-by-32 pixel grid. Change the clothing interpretation, not the animation. Return only image 1 on the same square canvas.",'Changed pose, scale and detail too much.'),
                ('front-step-a-concept-v5-attempt2-generated.png',"Image 1 is a finished animation frame. Change ONLY the blue trouser-leg pixels to dark charcoal, as shown by the original concept in image 2. Keep the teal waist scarf and its narrow hanging tail separate from the charcoal legs. Preserve every other pixel, the exact pose, feet, equipment, outline, low resolution and canvas. Do not redraw or add concept details. Return only the edited image 1.",'Changed the tucked-foot step into a separated-foot stance.')]:
                source=folder/filename
                rejected.append(dict(source=str(source.relative_to(ROOT)),sourceSha256=H['sha'](source),prompt=prompt,
                                     template=pose['template'],templateSha256=pose['templateSha256'],
                                     designReference=pose['designReference'],designReferenceSha256=pose['designReferenceSha256'],reason=reason))
            pose['rejectedConceptAttempts']=rejected
    u['costumeAuthority']=dict(path=str(concept.relative_to(ROOT)),sha256=H['sha'](concept),source='User attachment: codex-clipboard-7ba3e801-9f87-4a9e-9890-be9711dd95cd.png')
    H['save'](m)


def review():
    """Lay out unchanged source crops and create before/after preview loops."""
    cards=[]
    for version in ['before','after']:
        board=Image.new('RGB',(960,640),H['BG'][:3]);draw=ImageDraw.Draw(board)
        for row,(slug,facing) in enumerate([('human-samurai','front'),('nu-mou-chemist','back')]):
            draw.text((10,row*320+5),slug,fill='black');frames=[]
            for col,phase in enumerate(['step-a','neutral','step-b']):
                stem=f'{facing}-{phase}'
                suffix='-before-consistency' if version=='before' and phase!='neutral' else ''
                im=Image.open(OUT/slug/(stem+suffix+'.png')).convert('RGBA')
                enlarged=im.resize((256,256),Image.Resampling.NEAREST)
                board.paste(enlarged,(col*320+32,row*320+40),enlarged)
                draw.text((col*320+32,row*320+25),phase,fill='black')
                bg=Image.new('RGBA',(192,192),H['BG'])
                bg.alpha_composite(im.resize((192,192),Image.Resampling.NEAREST));frames.append(bg.convert('RGB'))
            sequence=[frames[i] for i in [0,1,2,1]]
            unit=next(u for u in H['read']()['units'] if u['slug']==slug)
            exact_colors=H['protected_preview_colors'](unit,facing) if version=='after' else []
            H['save_loop'](sequence,OUT/slug/(facing+'-consistency-'+version+'.gif'),exact_colors)
        board.save(OUT/('consistency-'+version+'.png'))
    for slug,facing,label in [('human-samurai','front','Samurai pants'),('nu-mou-chemist','back','Chemist head')]:
        previous='';latest=f'{facing}-consistency-after.gif'
        if slug=='human-samurai' and (OUT/slug/'front-walk-consistency-v3.gif').exists():
            previous=f'<figure><figcaption>Previous revision</figcaption><img src="{slug}/front-walk-consistency-v2.gif"></figure>'
            latest='front-walk-consistency-v3.gif'
        if slug=='human-samurai' and (OUT/slug/'front-walk-consistency-v4.gif').exists():
            previous=f'<figure><figcaption>Previous revision</figcaption><img src="{slug}/front-walk-consistency-v3.gif"></figure>'
            latest='front-walk-consistency-v4.gif'
        if slug=='human-samurai' and (OUT/slug/'front-walk-consistency-v5.gif').exists():
            previous=f'<figure><figcaption>Previous revision</figcaption><img src="{slug}/front-walk-consistency-v4.gif"></figure>'
            latest='front-walk-consistency-v5.gif'
            label='Samurai: charcoal trousers, teal scarf'
            previous=f'<figure><figcaption>Original concept</figcaption><img style="height:300px;width:auto;image-rendering:auto" src="{slug}/original-concept-user-reference.png"></figure>'+previous
        if slug=='human-samurai' and (OUT/slug/'front-walk-consistency-v6.gif').exists():
            previous=f'<figure><figcaption>Original concept</figcaption><img style="height:300px;width:auto;image-rendering:auto" src="{slug}/original-concept-user-reference.png"></figure><figure><figcaption>Previous revision</figcaption><img src="{slug}/front-walk-consistency-v5.gif"></figure>'
            latest='front-walk-consistency-v6.gif'
            label='Samurai: identical approved face pixels'
        cards.append(f'<article><h2>{label}</h2><div><figure><figcaption>Original movement</figcaption><img src="{slug}/{facing}-consistency-before.gif"></figure>{previous}<figure><figcaption>Revised</figcaption><img src="{slug}/{latest}"></figure></div></article>')
    (OUT/'consistency-review.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Movement consistency revisions</title><style>body{background:#e4e2dc;color:#252630;font:18px system-ui;margin:30px}main,article div{display:flex;gap:24px;flex-wrap:wrap}article{background:#f3f1eb;padding:20px;border-radius:12px}figure{margin:0}img{image-rendering:pixelated}figcaption{margin-bottom:12px}</style><h1>Movement consistency revisions</h1><p>Same neutral frames, revised individual steps. Compare color and head silhouette through each loop. These remain animation drafts.</p><main>'+''.join(cards)+'</main><p><a href="index.html">All units</a> · <a href="consistency-after.png">Revised frames</a></p></html>',encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--review',action='store_true');parser.add_argument('--restore-stride',action='store_true');parser.add_argument('--restore-equipment',action='store_true');parser.add_argument('--restore-concept',action='store_true');args=parser.parse_args()
    if args.review:review()
    elif args.restore_stride:restore_stride()
    elif args.restore_equipment:restore_equipment()
    elif args.restore_concept:restore_concept()
    else:main()
