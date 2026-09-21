"""Publish fixed-grid portrait/icon proposals with the complete existing art review.

Review only: no ROM, palette bank or player-save writes.
"""
import json, shutil, re
from pathlib import Path
from PIL import Image
import numpy as np
from native_art import ROOT, sha

BASE=ROOT/'build/art/job-art-approval-2026-09-20'
GEN=ROOT/'build/art/native-ui-regeneration-v2-2026-09-20'
OUT=ROOT/'build/art/job-art-approval-v2-2026-09-20'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    shutil.copytree(BASE/'assets',OUT/'assets',dirs_exist_ok=True)
    data=json.loads((BASE/'review-data.json').read_text())
    plan=json.loads((GEN/'plan.json').read_text())
    results=json.loads((GEN/'results.json').read_text())
    assert len(results['assets'])==20
    records=[]
    def copy(path,name,expected=None):
        source=Path(path);source=source if source.is_absolute() else ROOT/source
        digest=sha(source.read_bytes())
        if expected:assert digest==expected
        dest=OUT/'assets'/(name+source.suffix)
        shutil.copy2(source,dest)
        records.append(dict(path=str(dest.relative_to(OUT)).replace('\\','/'),sha256=digest,source=str(source.relative_to(ROOT))))
        return records[-1]['path']
    for u in data['units']:
        job=next(j for j in plan['jobs'] if j['job']==u['job']);slug=u['slug']
        u['issue']='Blue cloth must emerge behind the helmet, never across its front.' if u['job']==119 else ''
        u['regeneration']=[]
        for a in job['assets']:
            r=next(x for x in results['assets'] if x['job']==u['job'] and x['kind']==a['kind'])
            kind=a['kind'];prefix=slug+'-new-'+kind
            for field in ['native','sampled']:
                im=Image.open(ROOT/r[field]['path'])
                assert im.size==tuple(a['nativeSize'])
                if field=='native':
                    assert im.mode=='P'
                    assert max(im.get_flattened_data())<len(r['palette']['words'])
            native=copy(r['native']['path'],prefix+'-native',r['native']['sha256'])
            sampled=copy(r['sampled']['path'],prefix+'-sampled',r['sampled']['sha256'])
            if kind=='portrait':u.update(newPortrait=native,newPortraitSource=sampled)
            else:u.update(newIcon=native,newIconSource=sampled)
            u['regeneration'].append(dict(kind=kind,prompt=r['prompt'],crop=r['crop'],layoutNote=r['layoutNote'],
                template=copy(a['template']['path'],prefix+'-template',a['template']['sha256']),
                worksheet=copy(r['generatedSource']['path'],prefix+'-worksheet',r['generatedSource']['sha256']),
                references=[copy(x['path'],prefix+'-reference-'+str(n),x['sha256']) for n,x in enumerate(a['refs'])]))
        # Fixed placement only: keep the game's label/frame pixels outside the
        # head's 16x14 window byte-for-byte. Native index zero becomes UI bg 3.
        head=np.array(Image.open(OUT/u['newIcon']))
        for state,old in list(u['badges'].items()):
            base=Image.open(BASE/old);before=np.array(base);after=before.copy()
            assert base.mode=='P' and base.size==(32,16)
            after[1:15,1:17]=np.where(head==0,3,head)
            mask=np.ones(before.shape,dtype=bool);mask[1:15,1:17]=False
            assert np.array_equal(before[mask],after[mask])
            badge=Image.fromarray(after);badge.putpalette(base.getpalette())
            dest=OUT/'assets'/(slug+'-proposed-badge-'+state+'.png');badge.save(dest)
            u['badges'][state]=str(dest.relative_to(OUT)).replace('\\','/')
            records.append(dict(path=u['badges'][state],sha256=sha(dest.read_bytes()),source='Fixed head insertion into '+old))
    evidence=json.loads((ROOT/'build/art/native-final-integration-2026-09-20/evidence.json').read_text())
    data['checks']=[]
    labels={'test-final-native-capacity-final.png':'Mixed-class battle after Status',
            'test-final-native-save-cold-continue.png':'Cold Continue after saving',
            'test-final-native-inventory-ui-party-new-jobs.png':'Previous equipment eligibility screen'}
    for r in evidence['screenshots']:
        name=Path(r['path']).name
        if '-attack-' in name:
            job=int(name.split('-')[4]);u=next(u for u in data['units'] if u['job']==job)
            u['attack']=copy(r['path'],Path(name).stem,r['sha256'])
        elif name in labels:data['checks'].append(dict(label=labels[name],image=copy(r['path'],Path(name).stem,r['sha256'])))
    data.update(round=2,status='New native-palette portraits and icons await user approval. Animations and screenshots are the unchanged prior build.')
    (OUT/'review-data.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    shutil.copy2(BASE/'export-proof.json',OUT/'export-proof.json')
    receipt=dict(schema=1,assets=results['assets'],reviewFiles=records,animationBuildSha1=data['romSha1'],counts=data['counts'])
    (OUT/'regeneration-proof.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    template=(ROOT/'scripts/art-approval-round2.html.txt').read_text(encoding='utf-8')
    assert all(x not in template for x in ['localStorage','textarea','saveNotes','function approval','Export review notes'])
    html=template.replace('/*REVIEW_DATA*/',json.dumps(data).replace('</','<\\/'))
    (OUT/'index.html').write_text(html,encoding='utf-8')
    # Every embedded path resolves, including lazy animation/keyframe assets.
    def walk(x):
        if isinstance(x,dict):
            for v in x.values():walk(v)
        elif isinstance(x,list):
            for v in x:walk(v)
        elif isinstance(x,str) and x.startswith('assets/'):assert (OUT/x).is_file(),x
    walk(data)
    for u,old in zip(data['units'],json.loads((BASE/'review-data.json').read_text())['units']):
        assert u['poses']==old['poses'] and u['sequences']==old['sequences'] and u['emptySlots']==old['emptySlots']
    (OUT/'page-script.js').write_text(re.search(r'<script>(.*?)</script>',html,re.S)[1],encoding='utf-8')
    # Keep the user's currently-open round-one URL usable, with native browser
    # annotations only. It remains the prior build, not the new proposals.
    base_template=(ROOT/'scripts/art-approval-page.html.txt').read_text(encoding='utf-8')
    olddata=json.loads((BASE/'review-data.json').read_text())
    (BASE/'index.html').write_text(base_template.replace('/*REVIEW_DATA*/',json.dumps(olddata).replace('</','<\\/')),encoding='utf-8')
    print(json.dumps(dict(page=str(OUT/'index.html'),newArt=20,counts=data['counts'],nativePaletteOnly=True,romChanged=False)))

if __name__=='__main__':main()
