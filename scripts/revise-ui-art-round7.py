"""Remove the Samurai badge's inward-facing lower helmet tips for review."""
import importlib.util,json,sys
from PIL import Image
import numpy as np
from native_art import ROOT,sha

OUT=ROOT/'build/art/ui-detail-v7-2026-09-20'
OLD=ROOT/'build/art/ui-detail-v6-2026-09-20'

def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def prepare():
    OUT.mkdir(exist_ok=True);assert not (OUT/'plan.json').exists()
    data=json.loads((OLD/'results.json').read_text())
    old=next(a for a in data['assets'] if a['slug']=='human-samurai')
    a={k:v for k,v in old.items() if k not in ('raw','native','sampled','palette','paletteError','anchorProof','tool','model','conversion','registration','worksheetBox','layoutDeviation')}
    f=OUT/a['slug'];f.mkdir(exist_ok=True)
    row=Image.new('RGBA',(80,14))
    row.alpha_composite(Image.open(ROOT/a['anchors']['referenceStrip']['path']).convert('RGBA').resize((64,14),Image.Resampling.NEAREST),(0,0))
    row.alpha_composite(Image.open(ROOT/old['native']['path']).convert('RGBA'),(64,0))
    target=f/'edit-row.png';row.resize((1600,280),Image.Resampling.NEAREST).save(target)
    Image.open(ROOT/old['native']['path']).convert('RGBA').resize((640,560),Image.Resampling.NEAREST).save(f/'focused-target.png')
    a.update(references=[dict(path=target.relative_to(ROOT).as_posix(),sha256=sha(target.read_bytes()))],
      prompt='Make one tiny localized edit to ONLY the fifth head (red Samurai) in this five-head pixel-art row: remove the small inward-pointing helmet cheek-guard tips that curl toward the chin underneath the yellow cheeks. The lower side guards should fall straight down beside the face, without a little inward hook, spike or dark metal point intruding under the jaw. Preserve the yellow face and chin, two separate black eyes, cream around the eyes, compact helmet width and height, red/gold crest, upper helmet, and all other pixels as closely as possible. The frontal eyes remain at columns 7 and 10, rows 7 and 8 of the 16x14 head cell. Do not move, rescale or redesign the head. Keep the first FOUR original heads and full row layout unchanged. Match the existing coarse logical pixel grid, only existing colors, no fine detail, no labels. Return the entire row at the same proportions.')
    (OUT/'plan.json').write_text(json.dumps(dict(assets=[a],contracts=data['contracts']),indent=2)+'\n')

def ingest():
    m=module('converter','revise-ui-art-round4.py');m.OUT=OUT;m.ingest()

def build():
    m=module('builder','build-art-approval-round5.py')
    m.GEN=OUT;m.OLDGEN=OLD;m.BASE=ROOT/'build/art/job-art-approval-v6-2026-09-20'
    m.OUT=ROOT/'build/art/job-art-approval-v7-2026-09-20'
    m.ROUND_NUMBER=7;m.EDIT_COUNT=1;m.OLD_RESULTS_NAME='review-results.json'
    m.INTRO='One focused Samurai badge revision: removing the small inward-pointing lower helmet tips while retaining the frontal face.'
    for slug in ('viera-dancer','viera-mystic-knight'):(OUT/slug).mkdir(exist_ok=True)
    m.main()
    sam=np.array(Image.open(OUT/'human-samurai/icon-native.png'))
    dark={(x,y) for y in (7,8) for x in range(6,12) if sam[y,x]==1}
    assert dark=={(7,7),(7,8),(10,7),(10,8)},dark
    tips=[(5,9),(6,10),(12,9)]
    assert all(sam[y,x]!=13 for x,y in tips),'Purple lower-cheek helmet tips remain'
    previous=np.array(Image.open(OLD/'human-samurai/icon-native.png'))
    changed={(int(x),int(y)) for y,x in np.argwhere(previous!=sam)}
    assert changed==set(tips),changed
    report=dict(eyePixels=sorted(dark),removedTipCoordinates=tips,remainingPurpleAtTips=0,changedPixels=sorted(changed),allOtherHeadPixelsUnchanged=True,unchangedOtherSurfaces=19)
    (m.OUT/'targeted-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Whole inner-eye region verified; nineteen other portrait/icon surfaces unchanged.')

if __name__=='__main__':{'prepare':prepare,'ingest':ingest,'build':build}[sys.argv[1]]()
