"""Prepare imagegen edits with lossless original neutral/action registration.

Reference composition only. No new artwork is drawn by this script. The target
starts as the approved new-job base; imagegen performs all visual alterations.
64x64 reference/preview cells preserve actor origin (32,56), including effects
outside the old 32px crop. This does not allocate a larger runtime resource.
"""
import argparse
import json
from pathlib import Path
from PIL import Image
from new_job_art_helpers import ROOT, checked, record


def prepare(atlas_path, out, notes_path=None):
    a=json.loads(atlas_path.read_text());old=json.loads(checked(a['manifest']).read_text())
    assert [u['slug'] for u in a['units']]==[u['slug'] for u in old['units']],'Unit order/identity mismatch'
    base_plan=json.loads((ROOT/'build/art/chemist-job-art-2026-09-26/base-plan.json').read_text())
    if not out.is_relative_to(ROOT/'build/art'):raise ValueError('Use ignored art output')
    if out.exists() and any(out.iterdir()):raise ValueError('Use a new output folder; preserve previous generation inputs')
    out.mkdir(parents=True,exist_ok=True)
    requests=[]
    notes=json.loads(notes_path.read_text()) if notes_path else {}
    for u,original in zip(a['units'],old['units']):
        slug=u['slug'];folder=out/slug;folder.mkdir(exist_ok=True)
        poses={p['id']:p for p in original['poses']}
        for pid,uses in u['poseUses'].items():
            if poses[pid]['status']=='user-approved-base':continue
            use=uses[0];seq=next(s for s in u['sequences'] if s['id']==use['sequence'])
            rec=seq['records'][use['record']]; rear=seq['slot']%2==1
            pose_note=notes.get(slug,{}).get(pid,{})
            base=original['bases']['back' if rear else 'front']
            # Neutral anatomy comes from the SAME original actor as the action.
            # Its matching original walk record is found in the atlas, not fitted.
            neutral_seq=next(s for s in u['sequences'] if s['lifetime']=='land' and s['slot']==int(rear))
            neutral_rec=neutral_seq['records'][1]
            actor=seq['canonicalActor']-(188 if seq['lifetime']=='water' else 0)
            ref=next(r for r in neutral_rec['references'] if r['actor']==actor)
            native_neutral=a['nativeDrawings'][ref['drawing']]
            native_action=a['nativeDrawings'][rec['canonical']]
            approved=Image.open(checked(base)).convert('RGBA')
            cell=Image.new('RGBA',(64,64));cell.alpha_composite(approved,(16,20))
            board=Image.new('RGBA',(128,128),(228,226,220,255))
            for im,xy in [(Image.open(atlas_path.parent/native_neutral['image']).convert('RGBA'),(0,0)),
                          (Image.open(atlas_path.parent/native_action['image']).convert('RGBA'),(64,0)),
                          (cell,(0,64)),(cell,(64,64))]:board.alpha_composite(im,xy)
            if pose_note.get('blankTarget'):board.paste((228,226,220,255),(64,64,128,128))
            worksheet=folder/(pid+'-worksheet.png');board.resize((1024,1024),Image.Resampling.NEAREST).save(worksheet)
            design=folder/('rear-approved.png' if rear else 'front-approved.png')
            if not design.exists():approved.resize((384,384),Image.Resampling.NEAREST).save(design)
            if 'identity' in pose_note:
                if pose_note['identity'] not in ('front','back'):raise ValueError('Unknown identity view')
                alternate=Image.open(checked(original['bases'][pose_note['identity']])).convert('RGBA')
                design=folder/(pose_note['identity']+'-identity-approved.png')
                alternate.resize((384,384),Image.Resampling.NEAREST).save(design)
            bounds=native_action['geometry']['bounds']
            relative=[bounds[0]+32,bounds[1]+56,bounds[2]+32,bounds[3]+56]
            material=('ivory close cap, teal cap band, ivory medical coat, teal yoke, ochre cuffs, pale teal Nu Mou muzzle and long drooping ears, brown medical case' if slug=='physician' else 'ochre close cap, goggles parked ABOVE the eyes, cream Moogle face and ears, orange pompom, dark teal short vest, orange gloves, small brown pouches')
            prompt=(f'Use case: precise-object-edit. Edit ONLY the BOTTOM RIGHT sprite of image 1. Return the complete same square worksheet. '
                f'This is one original {original["label"]} animation drawing {pid}: {seq["lifetime"]} sequence {seq["slot"]}, record {rec["index"]+1}. '
                'TOP LEFT is the original game job in neutral; TOP RIGHT is that same original job in the REQUIRED action pose. '
                'BOTTOM LEFT is the approved NEW character neutral. BOTTOM RIGHT currently duplicates it and is your edit target. '
                'Transfer only the pose change from the top pair to the bottom pair. Keep the new character identity, facial anatomy, head size and clothing from bottom left. '
                'Do not copy the original job costume. Image 2 is the exact approved new character; image 3 contains the existing native colors. '
                f'Keep {material}. All pixels are coarse logical pixels, not detailed art. '
                'GEOMETRY IS MANDATORY: the worksheet is 128x128 logical pixels, four 64x64 quadrants; every quadrant shares the actor origin (32,56). '
                f'The original action occupies local pixel bounds {relative} (right/bottom exclusive). '
                'Match its anatomical scale and the positions of its face, head/body connection, hands and feet. '
                'Keep costume-specific outline differences small and preserve the approved head proportions. Never squash or stretch the torso or float the body above its native feet. '
                'Preserve the approved facial pixel clusters unless this pose genuinely turns the head. Keep both long ears attached in the same places. '
                'Match the actual top-right orientation even if it turns away from the neutral. Copy the direction and anatomical side of the action, not the costume. '
                'Use only the exact colors of the approved sprite and native palette. Preserve all other three quadrants and the flat neutral gray background EXACTLY. '
                'No labels, grids, extra figures, new weapons, extra costume details, new shadows or outline boxes. '
                'Target quadrant is x64..127,y64..127; no per-figure resizing or repositioning of the worksheet.')
            prompt+=' Do not rearrange the sheet into front/rear studies. The bottom-right action must keep the top-right action registration plus exactly 64 logical pixels vertically; do not shift the bottom row upward.'
            if seq['slot'] in (0,1):prompt+=' This is a subtle WALK step: head bobs by about one native pixel; preserve the neutral head shape and body length, move the arms and feet only as the top pair demonstrates.'
            if seq['slot'] in (2,3):prompt+=' RUN pose: preserve the native airborne feet and absence of a ground oval.'
            if seq['lifetime']=='water':prompt+=' WATER: match the original waterline and submerged lower body; no full feet below the water.'
            if pose_note.get('blankTarget'):
                prompt=prompt.replace('Edit ONLY the BOTTOM RIGHT sprite','Draw ONLY in the empty BOTTOM RIGHT cell').replace('BOTTOM RIGHT currently duplicates it and is your edit target.','BOTTOM RIGHT is empty and is your drawing target.')
            if pose_note.get('note'):prompt+=' POSE LANDMARK REVIEW: '+pose_note['note']
            req=dict(schema=2,tool='image_gen.imagegen',model='Tool managed; version not exposed',prompt=prompt,
                references=[record(worksheet),record(design),record(ROOT/'build/art/chemist-job-art-2026-09-26/palette-0.png')],
                atlas=record(atlas_path),pose=pid,job=slug,sourceSequence=use['sequence'],sourceRecord=use['record'],
                nativeNeutral=native_neutral,nativeAction=native_action,sharedPatches=rec['sharedPatches'],approvedBase=base,
                logicalGrid=[128,128],crop=[64,64,128,128],origin=[32,56],paletteROM=base_plan['paletteROM'],palette=base_plan['palette'],
                status='prepared-not-generated')
            if notes_path:req['poseNotes']=dict(source=record(notes_path),entry=pose_note)
            path=folder/(pid+'-request.json')
            if path.exists():raise ValueError('Preserve previous revision requests')
            path.write_text(json.dumps(req,indent=2)+'\n');requests.append(record(path))
    (out/'requests.json').write_text(json.dumps(dict(atlas=record(atlas_path),requests=requests),indent=2)+'\n')
    print(f'{len(requests)} fixed-origin requests prepared')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--atlas',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--pose-notes',type=Path)
    a=p.parse_args();prepare(a.atlas.resolve(),a.out.resolve(),a.pose_notes.resolve() if a.pose_notes else None)
