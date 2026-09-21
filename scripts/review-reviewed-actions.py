"""Build source/target inspection sheets and native-timing action previews.

This only lays out existing pixels. It does not author or repair artwork.
Missing drawings remain blank and prevent animation-preview creation.
"""
import argparse
import html
import json
from PIL import Image, ImageDraw
from native_art import ROOT


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--slug',required=True)
    parser.add_argument('--templates',action='store_true');parser.add_argument('--start',type=int,default=0);parser.add_argument('--end',type=int,default=999)
    parser.add_argument('--awaiting-only',action='store_true')
    args=parser.parse_args()
    catalog=json.loads((ROOT/'src/art/race-study/full-animation-v1.json').read_text())
    unit=next(u for u in catalog['units'] if u['slug']==args.slug)
    folder=ROOT/'build/art/reviewed-integration'/args.slug
    available={p['id']:p for p in unit['poses'] if p['status']!='pending'}
    bg=(228,226,220,255);cards=[]
    if args.templates:
        prepared=[p for p in unit['poses'] if 'generation' in p and args.start<=int(p['id'][1:])<=args.end]
        files=[]
        for start in range(0,len(prepared),6):
            group=prepared[start:start+6];sheet=Image.new('RGBA',(1280,((len(group)+1)//2)*404),bg);draw=ImageDraw.Draw(sheet)
            for n,p in enumerate(group):
                x=(n%2)*640;y=(n//2)*404;draw.text((x+5,y+2),p['id'],fill='black')
                im=Image.open(ROOT/p['generation']['template']['path']).convert('RGBA').resize((640,384),Image.Resampling.NEAREST)
                sheet.alpha_composite(im,(x,y+20))
            target=folder/f"templates-{group[0]['id']}-{group[-1]['id']}.png";sheet.save(target);files.append(str(target))
        print(json.dumps(files));return
    # Small groups keep native pixels legible when opened in the tool.
    generated=[p for p in unit['poses'] if p['status'].startswith('generated-')
               and args.start<=int(p['id'][1:])<=args.end
               and (not args.awaiting_only or p['status']=='generated-awaiting-review')]
    for start in range(0,len(generated),12):
        group=generated[start:start+12]
        sheet=Image.new('RGBA',(768,((len(group)+3)//4)*156),bg);draw=ImageDraw.Draw(sheet)
        for n,p in enumerate(group):
            x=(n%4)*192;y=(n//4)*156
            draw.text((x+4,y+2),p['id']+'  native / new',fill='black')
            for col,path in enumerate([p['reference']['path'],p['output']]):
                im=Image.open(ROOT/path).convert('RGBA').resize((96,96),Image.Resampling.NEAREST)
                sheet.alpha_composite(im,(x+col*96,y+22))
            draw.text((x+4,y+122),'X '+str(p.get('registration',{}).get('translationX',0)),fill='black')
        name=f'actions-review-{start//12+1:02d}.png';sheet.save(folder/name)
        cards.append(f'<a href="{name}"><img class="sheet" src="{name}"></a>')
    cycles=[]
    for resource in catalog['resources']:
        if resource['job']!=unit['job']:continue
        for slot in resource['slots']:
            draws=[f for f in slot['frames'] if f['command']==1]
            if not draws or any(f['pose'] not in available for f in draws):continue
            frames=[];durations=[]
            for frame in draws:
                p=available[frame['pose']];im=Image.open(ROOT/p['output']).convert('RGBA')
                canvas=Image.new('RGBA',(64,64),bg)
                # Native OAM origin and baseline, as used by the importer.
                dx=p.get('registration',{}).get('translationX',0)
                y=48+p['native']['nativeBottom']-im.getbbox()[3]
                canvas.alpha_composite(im,(16+dx,y))
                frames.append(canvas.convert('RGB').resize((256,256),Image.Resampling.NEAREST))
                durations.append(max(10,round(frame['duration']*1000/60)))
            name=f"action-{resource['resource']}-{slot['slot']:02d}.gif"
            frames[0].save(folder/name,save_all=True,append_images=frames[1:],duration=durations,loop=0,disposal=2)
            cycles.append(f'<figure><img src="{name}"><figcaption>{resource["lifetime"]} slot {slot["slot"]}: '+
                          html.escape(', '.join(f['pose'] for f in draws))+'</figcaption></figure>')
    page='''<!doctype html><meta charset="utf-8"><title>Action drawing review</title>
<style>body{font:16px system-ui;background:#e4e2dc;margin:24px;color:#20232a}section{display:flex;flex-wrap:wrap;gap:16px}figure{margin:0;background:#f6f4ee;padding:12px;max-width:300px}img{image-rendering:pixelated}.sheet{width:768px;max-width:100%}p{max-width:1000px}</style>'''
    page+=f'<h1>{html.escape(unit["label"])} action drafts</h1><p>Native reference on the left, new drawing on the right. These are unaccepted drafts. Loops below replay available drawing records at native durations; they do not simulate control commands, effects, or battle attachment behavior.</p>'
    page+='<section>'+''.join(cards)+'</section><h2>Available drawing sequences</h2><section>'+''.join(cycles)+'</section>'
    (folder/'actions-review.html').write_text(page,encoding='utf-8')
    print(json.dumps(dict(sheets=len(cards),sequences=len(cycles),generated=len(generated),page=str(folder/'actions-review.html'))))


if __name__=='__main__':main()
