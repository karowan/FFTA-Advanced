"""Inventory every displayed native keyframe before authoring reviewed actions.

Reference extraction and worksheet layout only; imagegen authors new artwork.
Native command-only records do not introduce a new drawing. Each drawing keeps
all of its actual sequence uses, so coverage cannot be fabricated by slot count.
"""
import argparse
import hashlib
import json
import struct
import runpy
import shutil
from pathlib import Path

from PIL import Image, ImageDraw
from native_art import ROOT, TILES, OAM, ANIM, compose, layout, palette, sha

OUT = ROOT / 'build/art/reviewed-integration'
CATALOG = ROOT / 'src/art/race-study/full-animation-v1.json'
PARENT = ROOT / 'build/art/connected/a28b624bb13c8f2f2597a4d4bd3999b17c234b99/manifest.json'
BG = (228, 226, 220, 255)
word = lambda b, p: struct.unpack_from('<I', b, p)[0]


def relative(p):
    return str(p.relative_to(ROOT)).replace('\\', '/')


def record(p):
    return dict(path=relative(p), sha256=sha(p.read_bytes()))


def native_pose(rom, frame, rgb):
    t, o = struct.unpack_from('<II', rom, frame)
    objects, _ = layout(rom, OAM + o)
    count = max(a['tile'] + a['width'] * a['height'] // 64 for a in objects)
    result = compose(rom[TILES + t:TILES + t + count * 32], objects, rgb).convert('RGBA')
    box = result.getbbox()
    assert box and box[2] - box[0] <= 48 and box[3] - box[1] <= 48, box
    if box[2] - box[0] > 32 or box[3] - box[1] > 32:
        part = result.crop(box); part.thumbnail((32,32), Image.Resampling.NEAREST)
        fitted = Image.new('RGBA', (32,32)); fitted.alpha_composite(part, ((32-part.width)//2,32-part.height))
        return fitted, dict(tileOffset=TILES+t, oamOffset=OAM+o, crop=list(box),
                            referenceFit=list(part.size), nativeBounds=list(box), nativeBottom=box[3]-64)
    # Keep native horizontal registration where possible and native baseline.
    x = min(max(32, box[2] - 32), box[0])
    y = min(max(28, box[3] - 32), box[1])
    return result.crop((x, y, x + 32, y + 32)), dict(
        tileOffset=TILES + t, oamOffset=OAM + o, crop=[x, y, x + 32, y + 32],
        nativeBounds=list(box), nativeBottom=box[3] - 64)


def prepare():
    assert not CATALOG.exists(), 'Existing provenance must be resumed, not replaced'
    parent = json.loads(PARENT.read_text())
    final = Path(parent['path']).read_bytes()
    clean = (ROOT / 'roms/clean/FFTA_US_clean.gba').read_bytes()
    assert hashlib.sha1(final).hexdigest() == parent['romSha1']
    assert hashlib.sha1(clean).hexdigest() == '4ac05441f4de70a4ec3dd932116346c61b8783d9'
    movement = json.loads((ROOT / 'src/art/race-study/animation-generation-v1.json').read_text())
    concepts = json.loads((ROOT / 'src/art/race-study/illustrated-class-concepts-v2.json').read_text())
    components = parent['components']
    additions = {(e['resource'], e['slot']): e for e in components['actionCompletion']['entries']}
    final_table = word(final, 0x2102c) - 0x08000000
    inventory, units = [], []
    for unit in movement['units']:
        folder = OUT / unit['slug']; folder.mkdir(parents=True, exist_ok=True)
        concept = next(c for c in concepts['concepts'] if c['job'] == unit['job'])
        # The selected concept is resolved explicitly; never substitute a sprite.
        concept_path = ROOT / concept['output']['path']
        assert sha(concept_path.read_bytes()) == concept['output']['sha256']
        if unit['job'] == 116:
            concept_path = ROOT / 'build/art/approved-class-animation-2026-09-19/human-samurai/original-concept-user-reference.png'
        poses, native_cache = [], {}
        approved = ROOT / 'build/art/approved-class-animation-2026-09-19' / unit['slug']
        for resource in [r for r in components['classResources']['resources'] if r['job'] == unit['job']]:
            final_desc = word(final, final_table + resource['id'] * 4) - 0x08000000
            native_desc = word(clean, ANIM + resource['originalID'] * 4) - 0x08000000
            slots = []
            for slot in range(resource['slots']):
                final_pointer = word(final, final_desc + slot * 12)
                native_pointer = word(clean, native_desc + slot * 12)
                if not final_pointer:
                    assert not native_pointer
                    slots.append(dict(slot=slot, frames=[], status='native-null'))
                    continue
                source_actor = resource['originalID']
                if not native_pointer:
                    addition = additions[(resource['id'], slot)]
                    native_pointer = addition['sourceSequence'] + 0x08000000
                    source_actor = addition['donorResource']
                q, nq = final_pointer - 0x08000000, native_pointer - 0x08000000
                count = word(final, q); assert count == word(clean, nq)
                frames = []
                for i in range(count):
                    f, nf = q + 4 + i * 20, nq + 4 + i * 20
                    assert final[f + 8:f + 20] == clean[nf + 8:nf + 20], (unit['job'], slot, i)
                    command = final[f + 9]
                    entry = dict(index=i, duration=final[f + 8], command=command,
                                 params=list(struct.unpack_from('<5H', final, f + 10)))
                    if command == 1:
                        t, o = struct.unpack_from('<II', clean, nf)
                        key = (t, o)
                        if key not in native_cache:
                            pid = f'p{len(poses):03}'
                            image, info = native_pose(clean, nf, palette(clean, 0x41a860)[1])
                            visual_actor, visual_frame = source_actor, nf
                            if unit['job'] == 116 and resource['lifetime'] == 'land':
                                # Samurai's engineering donor is not its style base.
                                # Use the user's established Soldier pose reference.
                                visual_actor = 0
                                dq = word(clean, ANIM) - 0x08000000
                                sq = word(clean, dq + slot * 12) - 0x08000000
                                assert 0 <= i < word(clean, sq)
                                visual_frame = sq + 4 + i * 20
                                assert clean[visual_frame + 9] == 1
                                image, _ = native_pose(clean, visual_frame, palette(clean, 0x41a860)[1])
                            path = folder / (pid + '-native.png'); image.save(path)
                            pose = dict(id=pid, sourceActor=source_actor, visualReferenceActor=visual_actor,
                                        visualReferenceFrame=visual_frame, reference=record(path),
                                        native=info, uses=[], status='pending',
                                        output=relative(folder / (pid + '.png')))
                            native_cache[key] = pose; poses.append(pose)
                            if resource['lifetime'] == 'land' and slot in (0, 1):
                                name = ('front' if slot == 0 else 'back') + '-' + ['step-a', 'neutral', 'step-b', 'neutral'][i]
                                path = approved / (name + '.png')
                                pose.update(status='approved-movement', output=relative(path), outputSha256=sha(path.read_bytes()))
                        pose = native_cache[key]
                        pose['uses'].append(dict(resource=resource['id'], lifetime=resource['lifetime'], slot=slot, frame=i))
                        entry['pose'] = pose['id']
                    else:
                        entry['status'] = 'native-control-preserved'
                    frames.append(entry)
                slots.append(dict(slot=slot, sourceActor=source_actor, sourceSequence=nq, finalSequence=q, frames=frames))
            inventory.append(dict(job=unit['job'], resource=resource['id'], lifetime=resource['lifetime'],
                                  originalID=resource['originalID'], descriptors=final_desc, slots=slots))
        units.append(dict(job=unit['job'], slug=unit['slug'], race=unit['race'], label=unit['label'],
                          originalConcept=record(concept_path), front=record(approved / 'front-neutral.png'),
                          back=record(approved / 'back-neutral.png'), poses=poses))
    spec = dict(schema=1, tool='built-in image_gen', model='Tool default; version not exposed',
                sourceManifest=record(PARENT), sourceRomSha1=parent['romSha1'],
                cleanRomSha1=hashlib.sha1(clean).hexdigest(), units=units, resources=inventory,
                status='Incomplete: every pending distinct native drawing requires authored artwork',
                acceptance='No idle substitution, copied donor costume, or water crop counts as authored coverage')
    CATALOG.write_text(json.dumps(spec, indent=2) + '\n')
    print(json.dumps([dict(job=u['job'], poses=len(u['poses']), pending=sum(p['status']=='pending' for p in u['poses'])) for u in units]))


def sheets(slug):
    spec = json.loads(CATALOG.read_text()); unit = next(u for u in spec['units'] if u['slug']==slug)
    folder = OUT / slug
    board = Image.new('RGBA', (64, 32), BG)
    for i, name in enumerate(('front', 'back')):
        board.alpha_composite(Image.open(ROOT / unit[name]['path']).convert('RGBA'), (32*i, 0))
    board.resize((1024, 512), Image.Resampling.NEAREST).save(folder / 'approved-design.png')
    # Eight native/target pairs per worksheet. Coordinates are immutable and
    # stored for technical extraction. Placeholder targets are native references,
    # never accepted as generated outputs.
    pending = [p for p in unit['poses'] if p['status']=='pending']
    groups = []
    for start in range(0, len(pending), 8):
        group = pending[start:start+8]; board = Image.new('RGBA', (128, 160), BG)
        for n, pose in enumerate(group):
            x, y = (n % 2)*64, (n // 2)*40
            im = Image.open(ROOT / pose['reference']['path']).convert('RGBA')
            board.alpha_composite(im, (x, y)); board.alpha_composite(im, (x+32, y))
        path = folder / f'actions-{start//8:02}-template.png'
        board.resize((1024, 1280), Image.Resampling.NEAREST).save(path)
        groups.append(dict(id=f'actions-{start//8:02}', template=record(path),
                           poses=[p['id'] for p in group], logicalSize=[128,160],
                           crops=[[n%2*64+32,n//2*40,n%2*64+64,n//2*40+32] for n in range(len(group))],
                           status='pending',
                           prompt='Replace the RIGHT sprite of each pair in image 1 with the approved character from image 2, doing exactly the pose of its LEFT neighbor. Image 3 is the original costume concept. Keep all eight pairs and their positions. Same tiny pixel style, camera, proportions and face; keep costume colors consistent. Do not add weapons or effects.'))
    unit['batches'] = groups
    CATALOG.write_text(json.dumps(spec, indent=2)+'\n')
    print(json.dumps([dict(id=b['id'],poses=b['poses']) for b in groups]))


def single(slug, pose_id):
    spec = json.loads(CATALOG.read_text()); unit = next(u for u in spec['units'] if u['slug']==slug)
    pose = next(p for p in unit['poses'] if p['id']==pose_id)
    assert pose['status'] == 'pending'
    use = pose['uses'][0]; slot, phase = use['slot'], use['frame']
    ids = {'human':[0,2,5,7], 'bangaa':[11,13,14,16], 'nu-mou':[18,20,21,25],
           'moogle':[35,34,37,39], 'viera':[26,27,29,31]}[unit['race']]
    if use['lifetime']=='water': ids = [i+188 for i in ids]
    rom = (ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes(); rgb=palette(rom,0x41a860)[1]
    board = Image.new('RGBA',(160,96),BG); refs=[]
    facing = 'back' if slot%2 else 'front'
    # The turn sequences alternate front/rear drawings within one slot.
    # Their slot parity alone cannot select the approved facing anchor.
    if slot in (22,23) and phase in (1,3):
        facing = 'back' if (slot==22 and phase==3) or (slot==23 and phase==1) else 'front'
    anchor=unit[facing]
    for n, actor in enumerate(ids):
        table = word(rom, ANIM+actor*4)-0x08000000
        for row,s,f in [(16,slot%2,1),(56,slot,phase)]:
            q=word(rom,table+s*12)-0x08000000
            if q<0 or f>=word(rom,q) or rom[q+4+f*20+9]!=1:
                # Slot-specific attack variants need their actual same-race
                # donor, not a guessed frame from an incompatible sequence.
                q=pose['visualReferenceFrame']-4; f=0
            frame=q+4+f*20; im,_=native_pose(rom,frame,rgb)
            board.alpha_composite(im,(32*n,row));refs.append(dict(actor=actor,frame=frame))
    im=Image.open(ROOT/anchor['path']).convert('RGBA')
    for y in (16,56):board.alpha_composite(im,(128,y))
    path=OUT/slug/(pose_id+'-template.png');board.resize((1280,768),Image.Resampling.NEAREST).save(path)
    design=OUT/slug/(pose_id+'-design.png');im.resize((512,512),Image.Resampling.NEAREST).save(design)
    pose['generation']=dict(tool='built-in image_gen',model='Tool default; version not exposed',
        template=record(path),design=record(design),concept=unit['originalConcept'],nativeReferences=refs,
        logicalSize=[160,96],crop=[128,56,160,88],strip=[128,48,160,96],
        prompt='Put the Samurai from image 2 into the bottom-right cell of image 1, doing the same pose as the four bottom-row references. Keep its costume and colors from the original concept in image 3. Keep the full worksheet layout.' if slug=='human-samurai' else
               f'Put the {unit["label"]} from image 2 into the bottom-right cell of image 1, doing the same pose as the four bottom-row references. Keep its costume and colors from the original concept in image 3. Keep the full worksheet layout.')
    if use['lifetime']=='water':
        pose['generation']['prompt']+=' Match the references\' waterline and small ripples; the submerged lower body is not visible.'
    hints={
        2:('running front','This is a running step, matching the bottom-row leg and arm positions.'),
        3:('running rear','This is a running step seen from behind, matching the bottom-row leg and arm positions.'),
        4:('front flinch','Bow the head in a flinch, matching the bottom-row references.'),
        5:('rear flinch','Match the bottom-row rear flinch, including the head tilt.'),
        6:('front lowered stance','Lower the body and bow the head, matching the bottom-row references.'),
        7:('rear lowered stance','Lower the body and bow the head seen from behind, matching the bottom-row references.'),
        10:('front collapsed','Show the character collapsed low on the ground, matching the bottom-row references.'),
        11:('rear collapsed','Show the character collapsed low on the ground seen from behind, matching the bottom-row references.'),
        64:('front crouch','Crouch with knees bent, matching the bottom-row references.'),
        65:('rear crouch','Crouch with knees bent seen from behind, matching the bottom-row references.'),
        78:('front prayer','Bring both hands together in front of the chest, matching the bottom-row references.'),
        79:('rear prayer','Bring both hands together in front of the chest, seen from behind, matching the bottom-row references.')}
    if slot==66 and unit['job']!=117:
        hints[slot]=('closed eyes','Close the eyes completely if they are visible, matching the bottom-row references.')
    if slot==68 and phase in (0,2):
        hints[slot]=('front head turn','Turn the head '+('left' if phase==0 else 'toward the viewer')+', matching the bottom-row references.')
    if slot==69 and phase in (0,2):
        hints[slot]=('rear head turn','Keep the body facing away and turn the head '+('left' if phase==0 else 'away from the viewer')+', matching the bottom-row references.')
    if slot in hints:
        label,hint=hints[slot]
        pose['generation']['poseMeaning']=dict(label=label,basis='Visual reading of the attached native keyframe; not a new runtime command')
        pose['generation']['prompt']+=' '+hint
    if unit['job']==117:pose['generation']['prompt']+=' Keep his helmet on.'
    CATALOG.write_text(json.dumps(spec,indent=2)+'\n'); print(json.dumps(pose['generation']))


def ingest(slug, pose_id, source):
    spec=json.loads(CATALOG.read_text()); unit=next(u for u in spec['units'] if u['slug']==slug)
    pose=next(p for p in unit['poses'] if p['id']==pose_id); gen=pose['generation']
    assert pose['status']=='pending'
    for key in ('template','design','concept'):
        assert sha((ROOT/gen[key]['path']).read_bytes())==gen[key]['sha256']
    target=OUT/slug/(pose_id+'-generated-v'+str(gen.get('version',1))+'.png')
    if target.exists():assert sha(target.read_bytes())==sha(Path(source).read_bytes()), 'Do not overwrite a prior attempt'
    else:shutil.copy2(source,target)
    if gen.get('registrationApproval'):
        assert gen['registrationApproval']['sourceSha256']==sha(target.read_bytes())
    clear=runpy.run_path(str(ROOT/'scripts/assemble-other-race-studies.py'))['clear_background']
    full=clear(Image.open(target).convert('RGBA').resize(tuple(gen['logicalSize']),Image.Resampling.NEAREST))
    register_anchor(pose,full)
    strip=gen['strip'];crop=list(gen['crop']); bounds=full.crop(tuple(strip)).getbbox()
    assert bounds and bounds[3]-bounds[1]<=32, ('Generated art exceeds 32px body height',bounds)
    if bounds[1]<crop[1]-strip[1] or bounds[3]>crop[3]-strip[1]:
        # Translation only. Raised limbs may shift the entire drawing within
        # the worksheet's tall strip; never clip them to the neutral crop.
        y=min(max(crop[1],strip[1]+bounds[3]-32),strip[1]+bounds[1])
        crop[1],crop[3]=y,y+32
    gen['extractionCrop']=crop
    im=full.crop(tuple(crop))
    if pose.get('mechanicalCorrection'):
        correction=pose['mechanicalCorrection'];ref=ROOT/correction['source']
        assert sha(ref.read_bytes())==correction['sourceSha256']
        im.paste(Image.open(ref).convert('RGBA').crop(tuple(correction['sourceBox'])),tuple(correction['position']))
    path=ROOT/pose['output'];im.save(path)
    pose.update(status='generated-awaiting-review',outputSha256=sha(path.read_bytes()),bounds=list(im.getbbox()))
    gen['generatedSource']=record(target)
    gen['conversion']='Nearest-neighbor worksheet reduction, connected flat backdrop removal, exact target crop; no rescaling within cell'
    preview=Image.new('RGBA',(64,32),BG)
    preview.alpha_composite(Image.open(ROOT/pose['reference']['path']).convert('RGBA'),(0,0));preview.alpha_composite(im,(32,0))
    preview.resize((512,256),Image.Resampling.NEAREST).save(OUT/slug/(pose_id+'-review.png'))
    CATALOG.write_text(json.dumps(spec,indent=2)+'\n');print(json.dumps(dict(id=pose_id,bounds=pose['bounds'],path=pose['output'])))


def register_anchor(pose, worksheet):
    """Recover worksheet translation using its unchanged top-right neutral.

    This never edits pixels. The native importer applies an integer OAM X
    offset, so global worksheet drift cannot turn into character movement.
    Native bottom registration already handles the vertical position.
    """
    gen=pose['generation']
    expected=Image.open(ROOT/gen['design']['path']).convert('RGBA').getbbox()
    design_size=Image.open(ROOT/gen['design']['path']).size
    assert design_size==(512,512)
    expected=[int(v/16) for v in expected]
    observed=worksheet.crop((128,16,160,48)).getbbox();assert observed
    dx=(expected[0]+expected[2]-observed[0]-observed[2]+1)//2
    approval=gen.get('registrationApproval',{})
    assert abs(dx)<=6 or (abs(dx)<=8 and approval.get('translationX')==dx and approval.get('reason')), ('Worksheet translation needs visual reinspection',dx)
    pose['registration']=dict(method='neutral-anchor-horizontal-translation',
        expectedBounds=expected,observedBounds=list(observed),translationX=dx,
        scope='Integer OAM offset only; generated artwork pixels are unchanged')


def revise(slug, pose_id, reason, instruction):
    """Preserve a rejected attempt and queue an explicit imagegen revision."""
    spec=json.loads(CATALOG.read_text());unit=next(u for u in spec['units'] if u['slug']==slug)
    pose=next(p for p in unit['poses'] if p['id']==pose_id)
    assert pose['status'] in ('generated-awaiting-review','generated-reviewed','pending') and reason and instruction
    version=pose['generation'].get('version',1)
    history={k:v for k,v in pose.items() if k not in ('attempts','uses','native','reference')}
    history.update(reason=reason)
    if pose['status'] in ('generated-awaiting-review','generated-reviewed'):
        path=ROOT/pose['output'];archive=path.with_name(pose_id+f'-rejected-v{version}.png')
        assert not archive.exists(), 'Keep prior rejected sources immutable'
        shutil.copy2(path,archive)
        history['archivedOutput']=record(archive)
    else:
        # A failed technical extraction still has an immutable model output.
        # Preserve it without pretending a valid32px drawing was produced.
        source=OUT/slug/(pose_id+f'-generated-v{version}.png')
        assert source.is_file(), 'Cannot revise a still-running generation'
        history['conversionRejectedSource']=record(source)
    pose.setdefault('attempts',[]).append(history)
    gen=pose['generation'].copy()
    for key in ('generatedSource','conversion','extractionCrop','registrationApproval'):gen.pop(key,None)
    gen.update(version=version+1,prompt=gen['prompt']+' '+instruction)
    pose['generation']=gen;pose['status']='pending'
    for key in ('outputSha256','bounds','registration','mechanicalCorrection','review'):pose.pop(key,None)
    CATALOG.write_text(json.dumps(spec,indent=2)+'\n')
    print(json.dumps(gen))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('command', choices=['prepare','sheets','single','ingest','revise']); parser.add_argument('--slug'); parser.add_argument('--pose'); parser.add_argument('--source'); parser.add_argument('--reason'); parser.add_argument('--instruction')
    args = parser.parse_args()
    if args.command=='prepare':prepare()
    elif args.command=='sheets':sheets(args.slug)
    elif args.command=='single':single(args.slug,args.pose)
    elif args.command=='revise':revise(args.slug,args.pose,args.reason,args.instruction)
    else:ingest(args.slug,args.pose,args.source)
