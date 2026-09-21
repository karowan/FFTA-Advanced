"""Keep the complete review; compare sprite-based badge revisions and eye repairs."""
import json,shutil,re
from PIL import Image,ImageDraw
import numpy as np
from native_art import ROOT,sha

BASE=ROOT/'build/art/job-art-approval-v2-2026-09-20'
FIRST=ROOT/'build/art/job-art-approval-2026-09-20'
GEN=ROOT/'build/art/native-ui-revision-v3-2026-09-20'
OUT=ROOT/'build/art/job-art-approval-v3-2026-09-20'
def main():
    OUT.mkdir(exist_ok=True);shutil.copytree(BASE/'assets',OUT/'assets',dirs_exist_ok=True)
    data=json.loads((BASE/'review-data.json').read_text());prior=json.loads((FIRST/'review-data.json').read_text())
    results=json.loads((GEN/'results.json').read_text());assert len(results['assets'])==12
    files=[]
    def copy(r,name):
        p=ROOT/r['path'];assert sha(p.read_bytes())==r['sha256']
        dest=OUT/'assets'/(name+'.png');shutil.copy2(p,dest);path=str(dest.relative_to(OUT)).replace('\\','/')
        files.append(dict(path=path,sha256=sha(dest.read_bytes())));return path
    for u,first in zip(data['units'],prior['units']):
        slug=u['slug'];u['firstBadges']=first['badges'];u['round2Portrait']=u['newPortrait']
        u['regeneration']=[a for a in u['regeneration'] if a['kind']=='portrait' and u['job'] not in (117,125)]
        for a in [x for x in results['assets'] if x['job']==u['job']]:
            kind=a['kind'];prefix=slug+'-round3-'+kind
            native=copy(a['native'],prefix+'-native');sampled=copy(a['sampled'],prefix+'-sampled')
            assert Image.open(OUT/native).size==tuple(a['nativeSize'])
            if kind=='portrait':u.update(newPortrait=native,newPortraitSource=sampled)
            else:
                u.update(newIcon=native,newIconSource=sampled)
                u['cleanRaceIcons']=copy(a['references'][1],slug+'-clean-race-icons')
                head=np.array(Image.open(OUT/native));u['badges']={}
                for state,path in first['badges'].items():
                    im=Image.open(FIRST/path);old=np.array(im);new=old.copy();new[1:15,1:17]=np.where(head==0,3,head)
                    mask=np.ones(old.shape,dtype=bool);mask[1:15,1:17]=False;assert np.array_equal(old[mask],new[mask])
                    out=Image.fromarray(new);out.putpalette(im.getpalette());dest=OUT/'assets'/(prefix+'-'+state+'.png');out.save(dest)
                    u['badges'][state]=str(dest.relative_to(OUT)).replace('\\','/')
            u['regeneration'].append(dict(kind=kind,single=True,prompt=a['prompt'],
                template=copy(a['references'][0],prefix+'-edit-target'),worksheet=copy(a['raw'],prefix+'-raw'),
                references=[copy(r,prefix+'-ref-'+str(n)) for n,r in enumerate(a['references'][1:])]))
        u['eyeRevised']=u['job'] in (117,125)
    data.update(round=3,status='Sprite-based badge revisions and two portrait eye repairs await user review. No ROM changes.')
    (OUT/'review-data.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    for name in ['export-proof.json','regeneration-proof.json']:shutil.copy2(BASE/name,OUT/name)
    (OUT/'revision-proof.json').write_text(json.dumps(dict(assets=results['assets'],reviewFiles=files),indent=2)+'\n')
    template=(ROOT/'scripts/art-approval-round3.html.txt').read_text(encoding='utf-8')
    assert all(s not in template for s in ['localStorage','textarea','function approval'])
    html=template.replace('/*REVIEW_DATA*/',json.dumps(data).replace('</','<\\/'));(OUT/'index.html').write_text(html,encoding='utf-8')
    (OUT/'page-script.js').write_text(re.search('<script>(.*?)</script>',html,re.S)[1],encoding='utf-8')
    def check(x):
        if isinstance(x,dict):
            for v in x.values():check(v)
        elif isinstance(x,list):
            for v in x:check(v)
        elif isinstance(x,str) and x.startswith('assets/'):assert (OUT/x).exists(),x
    check(data)
    for u,old in zip(data['units'],prior['units']):
        assert u['poses']==old['poses'] and u['sequences']==old['sequences'] and u['emptySlots']==old['emptySlots']
    board=Image.new('RGBA',(1000,520),(231,229,223,255));draw=ImageDraw.Draw(board)
    for n,u in enumerate(data['units']):
        x=n%5*200;y=n//5*180;draw.text((x+3,y+3),u['label'],fill='black')
        for key,dy in [('firstBadges',25),('badges',105)]:
            im=Image.open(OUT/u[key]['eligible']).convert('RGBA');board.alpha_composite(im.resize((160,80),Image.Resampling.NEAREST),(x+3,y+dy))
    for n,u in enumerate([u for u in data['units'] if u['eyeRevised']]):
        im=Image.open(OUT/u['newPortrait']).convert('RGBA');board.alpha_composite(im.resize((144,168),Image.Resampling.NEAREST),(n*200+550,352))
    board.save(OUT/'comparison.png');print(json.dumps(dict(page=str(OUT/'index.html'),revised=12,counts=data['counts'])))
if __name__=='__main__':main()
