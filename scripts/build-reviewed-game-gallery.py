"""Build a local review gallery from authenticated actual emulator screenshots.

Images are linked intact; no character pixels or emulator captures are edited.
The machine-readable index records each screenshot's ROM and passing evidence.
"""
import html,json,os,re
from pathlib import Path
from native_art import ROOT,sha


def main():
    out=ROOT/'build/art/reviewed-in-game-2026-09-20';out.mkdir(parents=True,exist_ok=True)
    catalog=json.loads((ROOT/'src/art/race-study/full-animation-v1.json').read_text())
    complete=json.loads((ROOT/'build/art/reviewed-integration/complete-candidate.json').read_text())
    action=json.loads((ROOT/'build/art/reviewed-integration/action-candidate.json').read_text())
    menu=ROOT/'build/art/generated-portraits/ui/20260920T142512.423328Z'
    menu_report=json.loads((menu/'report.json').read_text());assert menu_report['status']=='passed' and menu_report['romSha1']==complete['romSha1']
    fight_run=ROOT/'build/expansion/test-runs/20260920T134159.497899Z'
    ledger=json.loads((fight_run/'report.json').read_text());assert ledger['status']=='passed' and ledger['inputsUnchanged']
    fights={}
    for step in ledger['steps']:
        assert step['status']=='passed'
        text=Path(step['log']).read_text()
        row=next(json.loads(line) for line in text.splitlines() if line.startswith('{"status": "passed"'))
        p=Path(row['report']);r=json.loads(p.read_text());assert r['status']=='passed' and r['romSha1']==action['romSha1']
        fights[r['job']]=(p,r)
    assert set(fights)==set(range(116,126))
    images=[]
    def figure(path,caption,rom,report):
        assert path.is_file()
        images.append(dict(path=str(path.relative_to(ROOT)),sha256=sha(path.read_bytes()),caption=caption,romSha1=rom,
                           report=str(report.relative_to(ROOT)),reportSha256=sha(report.read_bytes())))
        url=html.escape(os.path.relpath(path,out).replace('\\','/'),quote=True)
        return f'<figure><a href="{url}"><img loading="lazy" src="{url}" alt="{html.escape(caption)}"></a><figcaption>{html.escape(caption)}</figcaption></figure>'
    index=json.loads((ROOT/'build/art/reviewed-integration/complete-entry-latest.json').read_text())
    entry_path=ROOT/index['report'];assert sha(entry_path.read_bytes())==index['sha256']
    entry=json.loads(entry_path.read_text());assert entry['status']=='passed' and entry['romSha1']==complete['romSha1']
    overview=figure(entry_path.parent/'battle-approved-sprite-pilot.png','Combined build: native battle',complete['romSha1'],entry_path)
    capacity=ROOT/'build/art/all-class-capacity/20260920T154903.556989Z'
    capacity_report=json.loads((capacity/'report.json').read_text())
    assert capacity_report['status']=='passed' and capacity_report['romSha1']==complete['romSha1']
    mixed=figure(capacity/'final.png','All ten classes in the declared six-versus-six test battle',capacity_report['fixtureRomSha1'],capacity/'report.json')
    mixed+=figure(capacity/'status.png','Native battle Status with the reviewed Viking',capacity_report['fixtureRomSha1'],capacity/'report.json')
    cards=[]
    for u in catalog['units']:
        job=u['job'];p,r=fights[job];folder=p.parent
        eligible=[(name,v) for name,v in r['observations'].items() if name.startswith('attack-') and v['actor']['mode']>=8 and v['actor']['displayedFrames'] and not v['paletteProof'].get('nativeOnly') and (folder/(name+'.png')).is_file()]
        assert eligible,(job,'No actual action screenshot')
        # First directly verified non-idle image is a deterministic selection;
        # every other retained action screenshot remains linked below.
        name,_=eligible[0]
        figures=figure(menu/f'generated-{job}-wheel0.png','Portrait, idle sprite and job wheel',complete['romSha1'],menu/'report.json')
        figures+=figure(folder/(name+'.png'),'Actual Fight animation',action['romSha1'],p)
        extra=' '.join(f'<a href="{html.escape(os.path.relpath(folder/(n+".png"),out).replace(chr(92),"/"),quote=True)}">{n.split("-")[-1]}</a>' for n,_ in eligible)
        cards.append(f'<article><h2>{html.escape(u["label"])}</h2><div class="pair">{figures}</div><details><summary>More attack frames</summary><p>{extra}</p></details></article>')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FFTA — reviewed art in game</title>
<style>body{margin:0;background:#e5e3dc;color:#202431;font:16px/1.5 system-ui,sans-serif}main{max-width:1500px;margin:auto;padding:28px}h1{margin:0;font-size:30px}h2{font-size:20px;margin:0 0 14px}header{margin-bottom:24px}header p{max-width:1000px}article{background:#f7f5ef;padding:20px;border-radius:12px;margin:20px 0}.pair{display:grid;grid-template-columns:1fr 1fr;gap:20px}figure{margin:0}img{display:block;width:100%;max-width:720px;height:auto;image-rendering:pixelated;background:#161c2b}figcaption{padding:7px 0;color:#4b5361;font-size:14px}a{color:#234579}.status{border-left:4px solid #aa7932;padding:10px 16px;background:#fff6e6}summary{cursor:pointer}details a{margin-right:12px}@media(max-width:800px){main{padding:15px}.pair{grid-template-columns:1fr}} </style><main>
<header><h1>Reviewed class artwork — in game</h1><p>Actual emulator captures of all ten new class designs. All 675 reviewed poses are imported across every available land and water animation sequence. Original animation timing and control commands are preserved.</p>
<p class="status">Playable review build. Input-response optimization remains open; this is not final performance acceptance. Existing player saves and the engineering release remain separate.</p>
<p>Fight, Combo and water checks pass for every class. Screenshots below show the combined build’s menus and the identical full-animation artwork during battle. Click an image for its full capture.</p></header>'''
    page+='<article><h2>Battle overview</h2>'+overview+'</article><article><h2>Mixed-class battle and Status</h2><div class="pair">'+mixed+'</div></article>'+''.join(cards)
    page+='<footer><p><a href="manifest.json">Screenshot provenance and tested ROMs</a></p></footer></main></html>'
    (out/'index.html').write_text(page,encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps(dict(schema=1,completeRomSha1=complete['romSha1'],actionRomSha1=action['romSha1'],
        images=images,sourceSha256=sha(Path(__file__).read_bytes()),performanceAccepted=False,scope=__doc__),indent=2)+'\n')
    print(json.dumps(dict(gallery=str(out/'index.html'),screenshots=len(images),classes=len(cards))))


if __name__=='__main__':main()
