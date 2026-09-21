"""Independently audit final native graph coverage and imagegen provenance.

The inventory check may pass while production coverage remains incomplete.
--require-complete is the separate hard gate for the final importer.
"""
import argparse
import datetime
import hashlib
import json
import runpy
import struct
from pathlib import Path
from PIL import Image
from native_art import ROOT, ANIM, sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--require-complete',action='store_true');args=parser.parse_args()
    path=ROOT/'src/art/race-study/full-animation-v1.json';spec=json.loads(path.read_text())
    checks=0
    clear_background=runpy.run_path(str(ROOT/'scripts/assemble-other-race-studies.py'))['clear_background']
    def check(ok,label):
        nonlocal checks
        assert ok,label
        checks+=1
    def authenticate(ref):
        p=ROOT/ref['path'];check(p.is_file() and sha(p.read_bytes())==ref['sha256'],'Source hash '+str(p))
    authenticate(spec['sourceManifest'])
    parent=json.loads((ROOT/spec['sourceManifest']['path']).read_text());rom=Path(parent['path']).read_bytes()
    clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
    check(hashlib.sha1(rom).hexdigest()==spec['sourceRomSha1'],'Final engineering ROM identity')
    check(hashlib.sha1(clean).hexdigest()==spec['cleanRomSha1'],'Clean native command reference identity')
    word=lambda b,p:struct.unpack_from('<I',b,p)[0]
    table=word(rom,0x2102c)-0x08000000
    check([u['job'] for u in spec['units']]==list(range(116,126)),'Exactly ten owned jobs')
    check([r['resource'] for r in spec['resources']]==list(range(256,276)),'Exactly twenty land/water resources')
    uses={};poses={};pose_count=ready=draws=controls=slots=0;pending=[]
    for unit in spec['units']:
        authenticate(unit['originalConcept']);authenticate(unit['front']);authenticate(unit['back'])
        for pose in unit['poses']:
            key=(unit['job'],pose['id']);check(key not in uses,'Unique pose identity')
            uses[key]=set();poses[key]=pose;pose_count+=1;authenticate(pose['reference'])
            im=Image.open(ROOT/pose['reference']['path']);check(im.size==(32,32),'Bounded native worksheet reference')
            if pose['status'] in ('approved-movement','generated-reviewed','generated-awaiting-review'):
                p=ROOT/pose['output'];check(p.is_file() and sha(p.read_bytes())==pose['outputSha256'],'Current artwork hash')
                image=Image.open(p).convert('RGBA');check(image.size==(32,32) and bool(image.getbbox()),'Nonempty 32px artwork')
                check(set(image.getchannel('A').get_flattened_data())<={0,255},'Binary transparency')
                if pose['status']!='approved-movement':
                    gen=pose['generation']
                    for name in ('template','design','concept','generatedSource'):authenticate(gen[name])
                    check(gen['concept']==unit['originalConcept'],'Original concept included in generation')
                    check(bool(gen['prompt']) and gen['tool']=='built-in image_gen','Preserved model and exact prompt')
                    # Reconstruct the registration proof from immutable sources,
                    # not from the importer or its saved translation value.
                    anchor=pose['registration']
                    design=Image.open(ROOT/gen['design']['path']).convert('RGBA')
                    check(design.size==(512,512),'Approved registration reference dimensions')
                    expected=[v//16 for v in design.getbbox()]
                    source=Image.open(ROOT/gen['generatedSource']['path']).convert('RGBA')
                    worksheet=clear_background(source.resize((160,96),Image.Resampling.NEAREST))
                    observed=worksheet.crop((128,16,160,48)).getbbox()
                    check(observed is not None,'Generated neutral registration anchor exists')
                    translation=(expected[0]+expected[2]-observed[0]-observed[2]+1)//2
                    approval=gen.get('registrationApproval',{})
                    extended=(abs(translation)<=8 and approval.get('translationX')==translation and
                              approval.get('sourceSha256')==gen['generatedSource']['sha256'] and bool(approval.get('reason')))
                    check(anchor['method']=='neutral-anchor-horizontal-translation' and
                          anchor['expectedBounds']==expected and anchor['observedBounds']==list(observed) and
                          anchor['translationX']==translation and (abs(translation)<=6 or extended),
                          'Native X registration is derived from the actual worksheet neutral')
                    if pose['status']=='generated-reviewed':
                        review=pose['review']
                        check(review['reviewer']=='primary agent' and bool(review['note']) and
                              review['outputSha256']==pose['outputSha256'] and
                              review['nativeReferenceSha256']==pose['reference']['sha256'] and
                              review['originalConceptSha256']==unit['originalConcept']['sha256'],
                              'Visual review belongs to these exact current source pixels')
                if pose.get('mechanicalCorrection'):
                    fix=pose['mechanicalCorrection'];p0=ROOT/fix['source'];before=ROOT/fix['before']
                    check(sha(p0.read_bytes())==fix['sourceSha256'] and sha(before.read_bytes())==fix['beforeSha256'],'Identity reuse source hashes')
                    reference=Image.open(p0).convert('RGBA').crop(tuple(fix['sourceBox']));x,y=fix['position']
                    check(image.crop((x,y,x+reference.width,y+reference.height)).tobytes()==reference.tobytes(),'Exact approved face pixels')
                    old=Image.open(before).convert('RGBA')
                    check(all(image.getpixel((a,b))==old.getpixel((a,b)) for b in range(32) for a in range(32)
                              if not(x<=a<x+reference.width and y<=b<y+reference.height)),'No changes outside approved face reuse')
            if pose['status'] in ('approved-movement','generated-reviewed'):ready+=1
            else:pending.append(dict(job=unit['job'],pose=pose['id'],status=pose['status']))
    for resource in spec['resources']:
        desc=word(rom,table+resource['resource']*4)-0x08000000
        check(len(resource['slots'])==84,'Complete descriptor inventory')
        for slot in resource['slots']:
            pointer=word(rom,desc+slot['slot']*12)
            if not pointer:
                check(not slot['frames'] and slot['status']=='native-null','Native null preserved');continue
            slots+=1;q=pointer-0x08000000
            check(len(slot['frames'])==word(rom,q),'Exact final frame count')
            nq=slot['sourceSequence'];check(word(clean,nq)==word(rom,q),'Original/native extension frame count')
            for i,frame in enumerate(slot['frames']):
                p=q+4+i*20;np=nq+4+i*20
                check(rom[p+8:p+20]==clean[np+8:np+20],'Native duration/control/parameters preserved')
                check(frame['command']==rom[p+9] and frame['duration']==rom[p+8],'Catalog command and duration')
                if frame['command']==1:
                    key=(resource['job'],frame['pose']);check(key in uses,'Every displayed frame has a declared drawing')
                    tile,oam=struct.unpack_from('<II',clean,np)
                    check(poses[key]['native']['tileOffset']==tile+0x69b89c and
                          poses[key]['native']['oamOffset']==oam+0x852e7c,'Drawing is bound to its actual original native keyframe')
                    uses[key].add((resource['resource'],resource['lifetime'],slot['slot'],i));draws+=1
                else:
                    check('pose' not in frame and frame['status']=='native-control-preserved','Control command not mislabeled as new art');controls+=1
    for unit in spec['units']:
        for pose in unit['poses']:
            expected={(u['resource'],u['lifetime'],u['slot'],u['frame']) for u in pose['uses']}
            check(expected==uses[(unit['job'],pose['id'])] and bool(expected),'Exact bidirectional pose reuse bindings')
    out=ROOT/'build/art/reviewed-integration/validation'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    report=dict(status='passed' if not args.require_complete or not pending else 'failed',checks=checks,
                sourceRomSha1=spec['sourceRomSha1'],catalogSha256=sha(path.read_bytes()),
                presentSlots=slots,drawRecords=draws,controlRecords=controls,distinctPoses=pose_count,
                reviewedPoses=ready,remaining=len(pending),pending=pending,
                scope='Static source inventory and provenance only; no native integration, runtime, color or final art acceptance')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='pending'}))
    if args.require_complete:check(not pending,'Every animation needs reviewed new-design artwork before final import')


if __name__=='__main__':main()
