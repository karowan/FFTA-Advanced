"""Build a complete, honest animation review from explicit revision choices.

v1 is the declared default attempt, never a newest-file heuristic. Optional
choices.json maps job/pose to a different revision ID. Missing outputs remain
pending. Original timings and every repeated drawing/control record are kept.
"""
import argparse
import html
import json
import os
from pathlib import Path
from PIL import Image
from new_job_art_helpers import ROOT, checked, record


def build(out):
    requests=json.loads((out/'requests.json').read_text());atlas_path=checked(requests['atlas'])
    atlas=json.loads(atlas_path.read_text());old=json.loads(checked(atlas['manifest']).read_text())
    assert [u['slug'] for u in atlas['units']]==[u['slug'] for u in old['units']],'Unit order/identity mismatch'
    choices=json.loads((out/'choices.json').read_text()) if (out/'choices.json').exists() else {}
    esc=html.escape
    def rel(path):return Path(os.path.relpath(path,out)).as_posix()
    widths={}
    def pic(path,caption):
        if path not in widths:widths[path]=Image.open(path).width
        width=widths[path]
        return f'<figure><img class="sprite" loading="lazy" data-native-width="{width}" style="width:{width*4}px" src="{esc(rel(path))}" alt="{esc(caption)}"><figcaption>{esc(caption)}</figcaption></figure>'
    sections=[];counts={};selected={};records=0;players=0
    overview='<section><h2>Approved designs and native bases</h2><p>These four bases retain their approved pixels. Motion drawings below are new proposals.</p><div class="grid">'
    for u,ou in zip(atlas['units'],old['units']):
        slug=u['slug'];chosen={};receipts={};originalposes={p['id']:p for p in ou['poses']}
        for pid in u['poseUses']:
            p=originalposes[pid]
            if p['status']=='user-approved-base':
                base=Image.open(checked(p['output']));canvas=Image.new('P',(64,64));canvas.putpalette(base.getpalette());canvas.paste(base,(16,20));canvas.info['transparency']=0
                path=out/slug/(pid+'-approved-base.png');canvas.save(path);chosen[pid]=path
                assert canvas.crop((16,20,48,52)).tobytes()==base.tobytes()
                receipts[pid]=dict(approvedSource=p['output'],preview=record(path))
                overview+=pic(checked(p['output']),u['label']+(' · front' if pid=='p001' else ' · rear'))
            else:
                revision=choices.get(slug,{}).get(pid,'v1')
                rp=out/slug/(pid+'-'+revision+'-receipt.json')
                if not rp.exists():continue
                r=json.loads(rp.read_text());req=json.loads(checked(r['request']).read_text());checked(r['source']);checked(req['atlas'])
                if req['job']!=slug or req['pose']!=pid:raise ValueError('Wrong revision identity')
                im=Image.open(checked(r['native']));assert im.size==(64,64) and im.mode=='P' and im.info.get('transparency')==0
                base=Image.open(checked(r['approvedBase']));assert im.getpalette()[:48]==base.getpalette()[:48]
                assert set(im.tobytes())<=set(r['allowedIndices'])|{0}
                chosen[pid]=checked(r['native']);receipts[pid]=record(rp)
        selected[slug]=receipts;counts[slug]=dict(ready=len(chosen),required=len(u['poseUses']),approvedBases=2)
        body=f'<section id="{slug}"><h2>{esc(u["label"])}</h2><p>{len(chosen)}/{len(u["poseUses"])} drawings available. Two bases are approved; new motion drawings are proposals.</p>'
        for life in ['land','water']:
            seqs=[s for s in u['sequences'] if s['lifetime']==life and s['records']]
            body+=f'<details open><summary>{life.title()} · {len(seqs)} animations</summary>'
            for s in seqs:
                frames=[];figures=[];records+=len(s['records'])
                for r in s['records']:
                    pid=r['pose'];label=f'Record {r["index"]+1} · {pid} · {r["duration"]} ticks'
                    if pid in chosen:
                        frames.append(dict(src=rel(chosen[pid]),caption=label,ticks=r['duration']))
                        figures.append(f'<div id="{s["id"]}-record-{r["index"]}">'+pic(chosen[pid],label)+'</div>')
                    elif pid:figures.append(f'<figure id="{s["id"]}-record-{r["index"]}" class="pending">{esc(label)}<p>Revision pending</p></figure>')
                    else:figures.append(f'<figure id="{s["id"]}-record-{r["index"]}">Control record {r["index"]+1}<p>Command {r["command"]}</p></figure>')
                complete=all(r['pose'] in chosen for r in s['records'] if r['pose'])
                preview=''
                if complete and frames:
                    players+=1;data=esc(json.dumps(frames),quote=True)
                    preview=f'<div class="player" data-frames="{data}"><img class="sprite" data-native-width="64" src="{frames[0]["src"]}" alt="{esc(u["label"])} animation {s["slot"]}"><p class="now">{esc(frames[0]["caption"])}</p><button data-step="-1">Previous</button> <button data-step="1">Next</button> <button class="toggle">Play / stop</button></div>'
                meaning=['Walk front','Walk rear','Run front','Run rear'][s['slot']] if s['slot']<4 else 'Native action'
                body+=f'<article id="{s["id"]}"><h3>{life.title()} · {s["slot"]:02} · {meaning}</h3><div class="grid">{preview}{"".join(figures)}</div><details><summary>Original record timing and commands</summary><pre>{esc(json.dumps(s["schedule"],indent=2))}</pre></details></article>'
            body+='</details>'
        body+='<details><summary>Every distinct pose · revised / original / previous proposal</summary>'
        for pid,uses in u['poseUses'].items():
            ref=atlas['nativeDrawings'][uses[0]['canonical']]
            figures=pic(chosen[pid],'Revised '+pid) if pid in chosen else '<figure class="pending">Revision pending</figure>'
            figures+=pic(atlas_path.parent/ref['image'],'Original positional reference '+pid)
            figures+=pic(atlas_path.parent/u['drafts'][pid]['image'],'Previous proposal '+pid)
            body+=f'<article id="{slug}-{pid}"><h3>{pid}</h3><div class="grid">{figures}</div></article>'
        body+='</details></section>';sections.append(body)
    ui=json.loads((ROOT/'build/art/chemist-job-art-2026-09-26/menu/menu.json').read_text())
    menu='<section><h2>Existing portrait and equipment proposals</h2><p>Retained for the complete review; this revision changes body animations.</p><div class="grid">'
    for u in ui['units']:
        for key in ['portrait','head']:menu+=pic(checked(u[key]),u['label']+' '+key)
        for key,ref in u['badges'].items():menu+=pic(checked(ref),u['label']+' '+key+' badge')
    menu+='</div></section>'
    overview+='</div></section>'
    ready=sum(v['ready'] for v in counts.values());required=sum(v['required'] for v in counts.values())
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Physician and Sapper · anchored animation revision</title><style>
body{font:16px/1.5 system-ui;background:#e8e7df;color:#223740;margin:0}header,main{max-width:1450px;margin:auto;padding:24px}nav{position:sticky;top:0;z-index:2;background:#faf9f3;border-bottom:1px solid #bbb;padding:12px;display:flex;gap:12px;flex-wrap:wrap}a{color:#17677b}section,article{padding:18px;background:#faf9f3;border:1px solid #ccc;border-radius:8px;margin:20px 0}summary{font-weight:650;padding:12px;cursor:pointer}.grid{display:flex;gap:12px;flex-wrap:wrap;align-items:start}figure{margin:0;padding:8px;background:#e3e4de;max-width:100%}.sprite{width:256px;height:auto;image-rendering:pixelated;cursor:zoom-in;max-width:100%;background:repeating-conic-gradient(#dddeda 0% 25%,#eaebe6 0% 50%) 0/16px 16px}figcaption{font-size:13px;max-width:256px}.player{max-width:100%}.pending{color:#813b28;padding:24px}button,select{font:inherit;padding:6px}pre{max-height:260px;overflow:auto;font-size:12px}dialog{max-width:95vw}dialog img{width:min(768px,85vw);image-rendering:pixelated}p{max-width:1050px}</style>
<header><h1>Physician and Sapper · motion revision</h1><p>New motion drawings based on fixed original animation references and the approved designs. Compare facing, head shape, arms, feet and clothing through each sequence. Click any image to enlarge it.</p>'''+f'<p><strong>{ready}/{required} drawings available · {players}/150 complete animation previews.</strong> New drawings await visual review. Nothing has been imported into the game.</p>'+'''<details><summary>Reference and conversion details</summary><p>No pose was stretched or fitted to its silhouette. New drawings use the approved character's existing native palette indices. Inspected whole-drawing placement corrections are recorded in the individual receipts. The 64×64 review window retains a common original origin; it is not a runtime graphics allocation. Native control records are listed but not simulated by these previews.</p><p><a href="../chemist-animation-anchors-2026-09-27/index.html">Original anchor atlas</a> · <a href="../chemist-job-art-2026-09-26/review.html">Previous complete review</a> · <a href="review-receipt.json">Exact selections and coverage</a></p></details></header>
<nav><a href="#physician">Physician</a><a href="#sapper">Sapper</a><button id="pause">Pause all</button><label>Size <select id="size"><option value="1">Native size</option><option value="4" selected>4×</option><option value="6">6×</option><option value="8">8×</option></select></label><label><input type="checkbox" id="mirror"> Mirror</label><span>Annotate using Codex browser comments</span></nav><main>'''+overview+''.join(sections)+menu+'''</main><dialog id="zoom"><button id="close">Close</button><div><img id="large" alt="Enlarged sprite"></div></dialog><script>
const $=s=>document.querySelector(s);const players=[...document.querySelectorAll('.player')].map(el=>({el,frames:JSON.parse(el.dataset.frames),i:0,time:0,playing:true}));
function draw(p){const f=p.frames[p.i];p.el.querySelector('img').src=f.src;p.el.querySelector('.now').textContent=f.caption}
players.forEach(p=>{p.el.querySelectorAll('[data-step]').forEach(b=>b.onclick=()=>{p.playing=false;p.i=(p.i+Number(b.dataset.step)+p.frames.length)%p.frames.length;draw(p)});p.el.querySelector('.toggle').onclick=()=>{p.playing=!p.playing;p.time=performance.now()}});
setInterval(()=>{const now=performance.now();players.forEach(p=>{if(!p.playing||!p.el.closest('section>details').open)return;const rect=p.el.getBoundingClientRect();if(rect.bottom<0||rect.top>innerHeight)return;if(now-p.time>=Math.max(1,p.frames[p.i].ticks)*1000/60){p.i=(p.i+1)%p.frames.length;p.time=now;draw(p)}})},16);
$('#pause').onclick=()=>players.forEach(p=>p.playing=false);$('#size').onchange=e=>document.querySelectorAll('.sprite').forEach(im=>im.style.width=(Number(e.target.value)*Number(im.dataset.nativeWidth))+'px');$('#mirror').onchange=e=>document.querySelectorAll('.sprite').forEach(im=>im.style.transform=e.target.checked?'scaleX(-1)':'');document.querySelectorAll('.sprite').forEach(im=>im.onclick=()=>{$('#large').src=im.src;$('#large').alt=im.alt;$('#large').style.width=(12*Number(im.dataset.nativeWidth))+'px';$('#large').style.maxWidth='85vw';$('#large').style.transform=im.style.transform;$('#zoom').showModal()});$('#close').onclick=()=>$('#zoom').close();
</script></html>'''
    (out/'index.html').write_text(page,encoding='utf-8')
    result=dict(status='proposals-not-runtime-approval',atlas=requests['atlas'],coverage=counts,completePlayers=players,orderedRecords=records,selections=selected,page=record(out/'index.html'))
    (out/'review-receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(coverage=counts,players=players,records=records)))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args();build(a.out.resolve())
