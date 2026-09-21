"""Prepare and assemble two separately generated native-keyframe pose studies."""
import argparse
import json
import runpy
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/art/approved-class-sprites-2026-09-19'
H=runpy.run_path(str(ROOT/'scripts/assemble-other-race-studies.py'))
MANIFEST=ROOT/'src/art/race-study/samurai-pose-pilot.json'
IDS=[0,2,5,7]

def prepare():
    neutral,_=H['references'](IDS)
    base=Image.open(OUT/'human-samurai-grid.png').convert('RGBA')
    records=[]
    for phase in [0,2]:
        cells=[]
        evidence=[]
        for actor in IDS:
            folder=ROOT/f'build/art/native-reference/actor-{actor:03}'
            native=json.loads((folder/'native.json').read_text())
            frame=native['slots'][0]['frames'][phase]
            path=folder/(frame['pose']+'-pose.png')
            cells.append(Image.open(path).convert('RGBA').crop((32,28,64,60)))
            evidence.append(dict(actor=actor,slot=0,frame=phase,record=frame,path=str(path.relative_to(ROOT)),sha256=H['sha'](path)))
        board=Image.new('RGBA',(160,96),H['BG'])
        for row,images in [(16,neutral+[base]),(56,cells+[base])]:
            for i,im in enumerate(images):
                board.alpha_composite(im,(i*32,row))
        name=f'human-samurai-step-{phase}'
        template=OUT/f'{name}-template.png'
        board.resize((1280,768),Image.Resampling.NEAREST).save(template)
        prompt=("Change only the bottom-right Samurai sprite to the exact stepping pose shown by the four sprites to its left. "
                "The top row shows their neutral poses; preserve the top-right Samurai's crescent helmet, red armor and teal sash. "
                "Match the bottom row's feet, hands, body height and native pixel scale. Keep the complete two-row layout unchanged.")
        records.append(dict(slug=name,slot=0,frame=phase,meaning=f'Opposing walk-cycle step, native slot 0 frame {phase}; visual reference supplies exact limb placement.',
            prompt=prompt,template=str(template.relative_to(ROOT)),templateSha256=H['sha'](template),references=evidence))
    MANIFEST.write_text(json.dumps(dict(tool='built-in image_gen',model='Tool default; version not exposed',settings='One template input per generated pose; other settings tool-managed.',
        base='build/art/approved-class-sprites-2026-09-19/human-samurai-grid.png',baseSha256=H['sha'](OUT/'human-samurai-grid.png'),
        scope='Two separately authored walking poses; offline preview only, no native command or ROM replacement.',poses=records),indent=2)+'\n')

def assemble():
    m=json.loads(MANIFEST.read_text())
    for r in m['poses']:
        assert H['sha'](ROOT/r['template'])==r['templateSha256']
        source=OUT/(r['slug']+'-generated.png')
        full=H['clear_background'](Image.open(source).convert('RGBA').resize((160,96),Image.Resampling.NEAREST))
        im=full.crop((128,56,160,88))
        assert im.getbbox()
        im.save(OUT/(r['slug']+'-grid.png'))
        r['output']=dict(source=str(source.relative_to(ROOT)),sha256=H['sha'](source),crop=[128,56,160,88],logicalGrid=[160,96])
    order=['human-samurai-step-0-grid','human-samurai-grid','human-samurai-step-2-grid','human-samurai-grid']
    board=Image.new('RGBA',(1024,320),H['BG'])
    draw=ImageDraw.Draw(board)
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
    animation=[]
    for i,name in enumerate(order):
        im=Image.open(OUT/(name+'.png')).convert('RGBA').resize((256,256),Image.Resampling.NEAREST)
        board.alpha_composite(im,(i*256,0))
        draw.text((128+i*256,290),['Step A','Neutral','Step B','Neutral'][i],anchor='mm',font=font,fill='#252630')
        frame=Image.new('RGBA',(256,256),H['BG'])
        frame.alpha_composite(im)
        animation.append(frame.convert('RGB'))
    board.save(OUT/'samurai-walk-pilot.png')
    animation[0].save(OUT/'samurai-walk-pilot.gif',save_all=True,append_images=animation[1:],duration=[267,133,267,133],loop=0,disposal=2)
    m['preview']=dict(order=order,durationMilliseconds=[267,133,267,133],note='Offline preview assumes 60 ticks/second for native durations 16,8,16,8; not runtime verification.')
    MANIFEST.write_text(json.dumps(m,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','assemble']);a=p.parse_args()
    prepare() if a.action=='prepare' else assemble()
