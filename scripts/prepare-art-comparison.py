"""Prepare equal-brief API requests without decrypting keys or making requests."""
# Experimental screening only; see src/art/provider-comparison/README.md.
import hashlib, json
from pathlib import Path
from native_art import ROOT

def digest(data): return hashlib.sha256(data).hexdigest()

def prepare():
    source=ROOT/'src/art/provider-comparison/brief.txt'
    prompt=source.read_text(encoding='utf-8').strip()
    assert len(prompt)<=5000, 'Qwen prompt size limit'
    size={'width':1536,'height':1024}
    entries=[]
    for model,extra in [
        ('fal-ai/flux-2-pro',{'seed':17092026}),
        ('ideogram/v4',{'seed':17092026,'expansion_model':'None','rendering_speed':'QUALITY','acceleration':'none','num_images':1}),
        ('bytedance/seedream/v5/pro/text-to-image',{'num_images':1}),
        ('alibaba/qwen-image-3/text-to-image',{'seed':17092026,'enable_prompt_expansion':False,'num_images':1})]:
        entries.append({'provider':'fal','model':model,'endpoint':'https://queue.fal.run/'+model,
                        'request':{'prompt':prompt,'image_size':size,'output_format':'png','enable_safety_checker':True,**extra},
                        'limitations':['Identical numeric seeds across model families are not equivalent latent inputs.','No reference-conditioned or repeat-generation consistency acceptance in this initial text-only round.'],
                        'documentation':'https://fal.ai/models/'+model+'/api'})
    out=ROOT/'build/art/provider-comparison/prepared';out.mkdir(parents=True,exist_ok=True)
    for number,item in enumerate(entries,1):
        raw=json.dumps(item['request'],ensure_ascii=False,sort_keys=True,indent=2).encode()
        name=f'request-{number:02}.json';(out/name).write_bytes(raw)
        item.update(requestFile=name,requestSha256=digest(raw),promptSha256=digest(prompt.encode()))
        del item['request']
    manifest={'status':'prepared-not-submitted','scope':'Four model configurations across four developer families; first-round screening only.',
              'promptFile':str(source.relative_to(ROOT)),'promptSha256':digest(prompt.encode()),'characters':[116,121,122],
              'layout':{'columns':3,'rows':2,'cellLogicalPixels':[32,32],'targetSize':[1536,1024]},
              'authorization':{'spendingCap':None,'paidInferenceAllowed':False},'requests':entries,
              'evaluation':{'sourceAndNativeViewsRequired':True,'blindedReviewerIDsRequired':True,
                            'criteria':['FFTA fidelity and race anatomy','game-size face and silhouette readability','class identity','front/back equipment continuity','consistent proportions and palette'],
                            'acceptance':'Ranking is comparative, not production acceptance. All five races, ten classes and full actions/consumers remain required.'}}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'status':manifest['status'],'models':len(entries),'families':4,'sharedPromptSha256':manifest['promptSha256'],'out':str(out),'networkRequests':0}))
    return manifest

if __name__=='__main__':prepare()
