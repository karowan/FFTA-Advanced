"""Prepare individual poses from an authenticated native animation inventory.

This is offline artwork preparation, not job/runtime implementation. It carries
all native sequence uses and commands forward, but never assigns new ROM IDs.
Each generated drawing must still be inspected and approved before import.
Historical only: the 2026-09-27 geometry review rejected this worksheet method.
See audit-new-job-animation-anchors.py before preparing further artwork.
"""
import argparse
import copy
import json
import runpy
import struct
from pathlib import Path
from PIL import Image
from new_job_art_helpers import ROOT, record, checked
from native_art import ANIM, palette

BG = (228,226,220,255)


def prepare(plan_path, approval_path, out):
    plan = json.loads(plan_path.read_text())
    approval = json.loads(approval_path.read_text())
    out = out.resolve()
    if not out.is_relative_to(ROOT/'build/art') or (out/'actions.json').exists():
        raise ValueError('Use a fresh build/art output; resume existing action receipts')
    if approval['scope'] != 'native-front-rear-designs-and-colors' or not approval['approved']:
        raise ValueError('Explicit native-base approval is required')
    approved = {r['path']:r['sha256'] for r in approval['images']}
    catalog_path = ROOT/'src/art/race-study/full-animation-v1.json'
    catalog = json.loads(catalog_path.read_text())
    rom = checked(plan['paletteROM']).read_bytes()
    helpers = runpy.run_path(str(ROOT/'scripts/prepare-reviewed-actions.py'))
    native_pose = helpers['native_pose']
    rgb = palette(rom,0x41a860)[1]
    word = lambda p: struct.unpack_from('<I',rom,p)[0]
    units=[]
    for spec in plan['jobs']:
        slug=spec['slug']; folder=out/slug; folder.mkdir(parents=True,exist_ok=True)
        source_slug={'physician':'nu-mou-chemist','sapper':'moogle-chemist'}[slug]
        source=next(u for u in catalog['units'] if u['slug']==source_slug)
        front=ROOT/plan['outputDirectory']/(spec['front']+'-native.png')
        back=ROOT/plan['outputDirectory']/(spec['rear']+'-native.png')
        for image in [front,back]:
            ref=record(image)
            if approved.get(ref['path'])!=ref['sha256']:
                raise ValueError('Base image differs from explicit approval')
        bases={'front':record(front),'back':record(back)}
        ids={'nu-mou':[18,20,21,25],'moogle':[35,34,37,39]}[source['race']]
        poses=[]
        for old in source['poses']:
            pose={k:copy.deepcopy(old[k]) for k in ['id','sourceActor','visualReferenceActor','visualReferenceFrame','reference','native','uses']}
            checked(pose['reference'])
            use=pose['uses'][0]; slot=use['slot']; phase=use['frame']
            facing='back' if slot%2 else 'front'
            if slot in (22,23) and phase in (1,3):
                facing='back' if (slot==22 and phase==3) or (slot==23 and phase==1) else 'front'
            if use['lifetime']=='land' and slot in (0,1) and phase==1:
                pose.update(status='user-approved-base',output=bases[facing])
                poses.append(pose);continue
            board=Image.new('RGBA',(160,96),BG); refs=[]
            for col,actor in enumerate(ids):
                actor+=188 if use['lifetime']=='water' else 0
                table=word(ANIM+actor*4)-0x08000000
                for y,s,f in [(16,slot%2,1),(56,slot,phase)]:
                    q=word(table+s*12)-0x08000000
                    fallback=q<0 or f>=word(q) or rom[q+4+f*20+9]!=1
                    frame=pose['visualReferenceFrame'] if fallback else q+4+f*20
                    im,geometry=native_pose(rom,frame,rgb)
                    board.alpha_composite(im,(32*col,y))
                    refs.append(dict(actor=actor,frame=frame,fallbackToActualPose=fallback,geometry=geometry))
            anchor=checked(bases[facing]); im=Image.open(anchor).convert('RGBA')
            board.alpha_composite(im,(128,16))
            template=folder/(pose['id']+'-worksheet.png')
            board.resize((1280,768),Image.Resampling.NEAREST).save(template)
            design=folder/(pose['id']+'-design.png')
            im.resize((512,512),Image.Resampling.NEAREST).save(design)
            meaning=old.get('generation',{}).get('poseMeaning',{}).get('label',f'{use["lifetime"]} slot {slot}, frame {phase}')
            material=('ivory cap and coat, dark teal cap band and shoulder yoke, ochre cuffs, brown medicine case, pale teal Nu Mou face and exposed drooping ears' if slug=='physician' else 'ochre cap, dark goggles ABOVE the eyes, cream ears and face, orange-gold pom-pom, dark teal utility vest, orange gloves, small brown charges and satchel')
            prompt=(f'Fill ONLY the empty bottom-right cell of image 1 with the approved {spec["label"]} from image 2, performing exactly the pose of the four bottom-row native references. '
                f'Pose: {meaning}. Image 1 fixes the 160x96 logical grid, scale, anatomy and pose; top-right is the approved neutral. Image 2 is the exact approved native design and COLORS. Image 3 supplies the ONLY allowed native palette colors. Image 4 is the original costume concept, costume information only; never use its skin colors or fine illustration detail. '
                f'Keep {material} consistent across the new pose. Preserve the same coarse logical pixel clusters, facial landmarks and compact silhouette. '
                'Only change limb positions and head/body orientation to match this specific native pose. No new costume, equipment, weapons, spell effects or fine illustration detail. '
                'Target cell x128..159,y56..87. Return the ENTIRE unchanged 5-column 2-row worksheet on its flat gray background, no labels. Do not move or resize the other cells. ')
            if use['lifetime']=='water':
                prompt+='Match the native waterline and small ripples: submerged lower body invisible. '
            if facing=='back':
                prompt+='This is a REAR view: no face or front goggle lenses on the back; keep equipment on the same anatomical side. '
                if slug=='physician':
                    prompt+='For this normal rear orientation, the medicine case stays on screen LEFT exactly as in image 2; never swap it to screen right. '
            if slot in (0,1,2,3):
                prompt+='Keep the approved head and costume material colors fixed while reproducing this exact stride, arm swing and foot position. '
            if slot in (2,3):
                prompt+='This running frame is in the air: no black ground oval. Follow native foot positions exactly. '
            if slug=='sapper' and slot in (42,43,60,61):
                prompt=prompt.replace('This is a REAR view: no face or front goggle lenses on the back; keep equipment on the same anatomical side. ','')
                prompt+='This sequence turns the body: match the lower native reference pose\'s exact facing at this instant, even when it differs from the neutral above. Never put eyes on the rear of the head; when the head turns toward camera the face may become visible. '
            if slot in (70,71):
                prompt+='Preserve the small native status sparkles visible above the reference head in this specific frame, at the same positions; these existing actor details are required, not a new spell effect. '
            if slot in (20,21,22,23,24,25,42,43,60,61):
                for sentence in ['This is a REAR view: no face or front goggle lenses on the back; keep equipment on the same anatomical side. ','For this normal rear orientation, the medicine case stays on screen LEFT exactly as in image 2; never swap it to screen right. ']:
                    prompt=prompt.replace(sentence,'')
                prompt+='POSE FACING TAKES PRIORITY: copy the exact head and body orientation of the BOTTOM native row. The top neutral is identity only and can face differently. This is a turning action; preserve anatomical equipment sides through the turn, not fixed screen sides. '
            request=dict(schema=1,tool='image_gen.imagegen',model='Tool managed; version not exposed',prompt=prompt,
                references=[record(template),record(design),record(ROOT/plan['outputDirectory']/'palette-0.png'),spec['concept']],nativeReferences=refs,
                logicalGrid=[160,96],crop=[128,56,160,88],strip=[128,48,160,96],
                paletteROM=plan['paletteROM'],palette=plan['palette'],meaning=meaning,status='prepared-not-generated')
            request_path=folder/(pose['id']+'-request.json');request_path.write_text(json.dumps(request,indent=2)+'\n')
            pose.update(status='pending-generation',request=record(request_path),facing=facing)
            poses.append(pose)
        # These are inherited authoring requirements, NOT allocated resources for
        # a new game job. Runtime must independently reconcile its actual table.
        resources=[copy.deepcopy(r) for r in catalog['resources'] if r['job']==source['job']]
        units.append(dict(slug=slug,label=spec['label'],sourceClass=source_slug,bases=bases,poses=poses,
            authoringReferenceResources=resources,runtimeResourcesAllocated=False))
    manifest=dict(schema=1,sourceCatalog=record(catalog_path),approval=record(approval_path),paletteROM=plan['paletteROM'],
        status='authoring-in-progress-not-runtime-art',units=units)
    (out/'actions.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps([dict(slug=u['slug'],poses=len(u['poses']),pending=sum(p['status']=='pending-generation' for p in u['poses'])) for u in units]))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--approval',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--historical-replay',action='store_true',
                        help='Reproduce the superseded 2026-09-26 worksheet process; not for new generation')
    args=parser.parse_args()
    if not args.historical_replay:
        parser.error('This worksheet process was superseded after animation distortion. '
                     'Run audit-new-job-animation-anchors.py and follow Gate 4 of '
                     'NEW-JOB-ART-RUNBOOK.md. --historical-replay is only for provenance reproduction.')
    prepare(args.plan.resolve(),args.approval.resolve(),args.out)
