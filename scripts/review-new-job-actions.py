"""Build one local review page from explicit native-pose selections.

Pending drawings stay visibly pending. Native record order is preserved; the
browser previews drawing durations only, not the engine's control commands.
No annotation storage, ROM writes, automatic approval or newest-file selection.
"""
import argparse
import html
import json
import os
from pathlib import Path
from PIL import Image
from new_job_art_helpers import ROOT, checked, record


def build(manifest_path, selection_path, base_page, output, menu_path=None):
    if not output.resolve().is_relative_to(ROOT/'build/art'):
        raise ValueError('Review output must stay in build/art')
    if output.parent.resolve()!=base_page.parent.resolve():
        raise ValueError('Keep review beside base page so its relative references remain valid')
    manifest=json.loads(manifest_path.read_text()); selections=json.loads(selection_path.read_text())
    approval=json.loads(checked(manifest['approval']).read_text())
    if not approval.get('approved') or approval.get('scope')!='native-front-rear-designs-and-colors':
        raise ValueError('Exact native bases must be approved before action review')
    checked(manifest['sourceCatalog']);checked(manifest['paletteROM'])
    esc=html.escape
    def url(ref):
        return Path(os.path.relpath(checked(ref),output.parent)).as_posix()
    def picture(ref,label,width=192):
        return f'<img class="pixel" loading="lazy" src="{esc(url(ref),quote=True)}" width="{width}" alt="{esc(label,quote=True)}">'
    sections=[]; counts={}
    if menu_path:
        menu=json.loads(menu_path.read_text())
        checked(menu['baseApproval']);checked(menu['paletteROM']);checked(menu['font'])
        ui=[]
        for unit in menu['units']:
            figures=[]
            for key,label,size in [('portrait','Portrait',(48,56)),('head','Front-facing equipment head',(16,14))]:
                ref=unit[key];receipt=json.loads(checked(unit[key+'Receipt']).read_text())
                if receipt['native']!=ref:raise ValueError('UI receipt does not match selected image')
                with Image.open(checked(ref)) as im:
                    if im.size!=size:raise ValueError('Wrong UI dimensions: '+key)
                figures.append(f'<figure>{picture(ref,label,size[0]*4)}{picture(ref,label+" · actual size",size[0])}<figcaption>{label} · {size[0]}×{size[1]}</figcaption></figure>')
            for side,ref in unit['badges'].items():
                figures.append(f'<figure>{picture(ref,side+" badge",160)}{picture(ref,side+" badge · actual size",32)}<figcaption>{side.title()} badge</figcaption></figure>')
            figures.append(f'<figure>{picture(unit["wheel"]["native"],"Job-wheel figure",160)}<figcaption>Job-wheel figure · exact approved body</figcaption></figure>')
            ui.append(f'<article id="{unit["slug"]}-ui"><h3>{esc(unit["label"])}</h3><div class="grid">{"".join(figures)}</div></article>')
        sections.append('<section id="ui-proposals"><h2>Portraits and equipment badges</h2><p>New proposals awaiting visual approval. These are native-size import previews, not in-game captures. The dim badge uses the preserved native UI capture colors; new-job eligibility still needs runtime verification.</p>'+''.join(ui)+'</section>')
    for unit in manifest['units']:
        slug=unit['slug']; poses={p['id']:p for p in unit['poses']}; selected={}
        for ref in unit['bases'].values():
            if ref not in approval['images']:raise ValueError('Base not in user approval receipt')
            checked(ref)
        with Image.open(checked(unit['bases']['front'])) as base:
            palette=base.getpalette()[:48]
        if set(selections.get(slug,{}))-set(poses):raise ValueError('Unknown selected pose')
        for pose in unit['poses']:
            pid=pose['id']
            if pose['status']=='user-approved-base':
                if pose['output'] not in approval['images']:raise ValueError('Unapproved neutral drawing')
                selected[pid]=pose['output']
            elif pid in selections.get(slug,{}):
                choice=selections[slug][pid]
                conversion=json.loads(checked(choice['conversion']).read_text())
                checked(conversion['plan'])
                matches=[a for a in conversion['assets'] if a['id']==choice['attempt']]
                if len(matches)!=1 or matches[0]['native']!=choice['native']:
                    raise ValueError('Selected drawing does not match conversion receipt')
                checked(matches[0]['source'])
                ref=choice['native'];checked(ref);selected[pid]=ref
        for ref in selected.values():
            with Image.open(checked(ref)) as im:
                if im.size!=(32,32) or im.mode!='P' or max(im.tobytes())>15 or im.getpalette()[:48]!=palette or im.info.get('transparency')!=0:
                    raise ValueError('Actor selection must be native 32×32 indexed 4bpp')
        counts[slug]=dict(selected=len(selected),required=len(poses))
        cards=[]
        for resource in unit['authoringReferenceResources']:
            lifetime=resource['lifetime']; sequences=[]
            for slot in resource['slots']:
                if not slot['frames']:continue
                draws=[f for f in slot['frames'] if 'pose' in f]
                ready=bool(draws) and all(f['pose'] in selected for f in draws)
                sid=f'{slug}-{lifetime}-{slot["slot"]:02}'
                label=f'{lifetime.title()} · sequence {slot["slot"]:02}'
                if slot['slot']<4:label+=' · '+['Walk front','Walk rear','Run front','Run rear'][slot['slot']]
                frames=[]; figures=[]
                for frame in slot['frames']:
                    pid=frame.get('pose'); fid=f'{sid}-record-{frame["index"]}'
                    caption=f'Record {frame["index"]+1} · {pid} · {frame["duration"]} ticks' if pid else f'Control record {frame["index"]+1} · command {frame["command"]}'
                    if pid in selected:
                        figures.append(f'<figure id="{fid}">{picture(selected[pid],slug+" · "+caption)}<figcaption>{esc(caption)}</figcaption></figure>')
                        frames.append(dict(src=url(selected[pid]),ticks=frame['duration'],caption=caption))
                    else:
                        figures.append(f'<figure id="{fid}"><p>{"Drawing pending" if pid else "Native control record"}</p><figcaption>{esc(caption)}</figcaption></figure>')
                preview=''
                if ready:
                    data=esc(json.dumps(frames),quote=True)
                    preview=f'<div class="player" data-frames="{data}"><img class="pixel" width="192" src="{esc(frames[0]["src"],quote=True)}" alt="{esc(slug+" "+label,quote=True)}"><p class="now">{esc(frames[0]["caption"])}</p><button data-step="-1">Previous</button> <button data-step="1">Next</button> <button class="toggle">Play / stop</button></div>'
                raw=esc(json.dumps(slot['frames'],indent=2))
                sequences.append(f'<article id="{sid}"><h4>{esc(label)}</h4><div class="grid">{preview}{"".join(figures)}</div><details><summary>Native records</summary><pre>{raw}</pre></details></article>')
            cards.append(f'<details><summary>{lifetime.title()} · {len(sequences)} populated sequences</summary>{"".join(sequences)}</details>')
        index=''.join(f'<figure id="{slug}-{pid}">{picture(ref,slug+" · "+pid,128)}<figcaption>{pid}</figcaption></figure>' for pid,ref in selected.items())
        sections.append(f'<section id="{slug}-animations"><h2>{esc(unit["label"])} animations</h2><p>{len(selected)} of {len(poses)} distinct drawings currently available for review. Neutral bases are approved; other images remain proposals. Missing drawings are shown explicitly.</p>{"".join(cards)}<details><summary>All distinct drawings</summary><div class="grid">{index}</div></details></section>')
    page=base_page.read_text(encoding='utf-8')
    page=page.replace('native base review','complete art review')
    page=page.replace('</header>','<nav><a href="#ui-proposals">Portraits and badges</a> · <a href="#physician-animations">Physician animations</a> · <a href="#sapper-animations">Sapper animations</a></nav></header>')
    page=page.replace('big.src=im.src;big.alt=im.alt;', 'big.src=im.src;big.alt=im.alt;big.style.transform=im.style.transform;')
    extra='''<section><h2>Animation and UI proposals</h2><p>Native drawing order and tick durations are preserved. Control records are listed but not simulated. These are inherited authoring references; the new jobs have no allocated runtime graphics resources yet. Click any keyframe to enlarge; use Codex browser comments.</p><button id="pause-all">Pause all previews</button> <label><input id="mirror" type="checkbox"> Mirror action poses</label> <label>Sprite size <select id="sprite-size"><option value="128">Small</option><option value="192" selected>Medium</option><option value="256">Large</option></select></label></section>'''+''.join(sections)
    page=page.replace('</main>',extra+'</main>')
    page=page.replace('</style>','article{border:1px solid #c9c9be;padding:16px;margin:18px 0}pre{overflow:auto;max-height:250px;font-size:12px}summary{font-weight:600}.player{min-width:210px}</style>')
    page=page.replace('</body>','') # Base page deliberately uses optional HTML body tags.
    script='''<script>
const players=[...document.querySelectorAll('.player')].map(el=>({el,frames:JSON.parse(el.dataset.frames),i:0,time:0,playing:true}));
document.querySelector('#mirror').onchange=e=>document.querySelectorAll('[id$="-animations"] img').forEach(im=>im.style.transform=e.target.checked?'scaleX(-1)':'');
document.querySelector('#sprite-size').onchange=e=>document.querySelectorAll('[id$="-animations"] img').forEach(im=>im.width=Number(e.target.value));
function draw(p){const f=p.frames[p.i];p.el.querySelector('img').src=f.src;p.el.querySelector('.now').textContent=f.caption;}
players.forEach(p=>{p.el.querySelectorAll('[data-step]').forEach(b=>b.onclick=()=>{p.playing=false;p.i=(p.i+Number(b.dataset.step)+p.frames.length)%p.frames.length;draw(p)});p.el.querySelector('.toggle').onclick=()=>{p.playing=!p.playing;p.time=performance.now()}});
document.querySelector('#pause-all').onclick=()=>players.forEach(p=>p.playing=false);
setInterval(()=>{const now=performance.now();players.forEach(p=>{const group=p.el.closest('section > details');if(!p.playing||!group?.open)return;if(now-p.time>=Math.max(1,p.frames[p.i].ticks)*1000/60){p.i=(p.i+1)%p.frames.length;p.time=now;draw(p)}})},16);
</script>'''
    page=page.replace('</html>',script+'</html>')
    output.write_text(page,encoding='utf-8')
    complete=all(c['selected']==c['required'] for c in counts.values())
    receipt=dict(manifest=record(manifest_path),selections=record(selection_path),basePage=record(base_page),page=record(output),coverage=counts,status=('complete-art-proposals' if complete else 'partial-art-review')+'-not-runtime-acceptance')
    if menu_path:receipt['menu']=record(menu_path)
    output.with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(output)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['manifest','selections','base-page','output']:parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--menu',type=Path)
    args=parser.parse_args()
    build(args.manifest.resolve(),args.selections.resolve(),args.base_page.resolve(),args.output.resolve(),args.menu.resolve() if args.menu else None)
