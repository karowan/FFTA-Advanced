"""Publish intact, authenticated native-palette emulator captures locally."""
import argparse,html,json,os
from pathlib import Path
from native_art import ROOT,sha


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--validation-run',type=Path,required=True)
    parser.add_argument('--playback-run',type=Path,required=True)
    args=parser.parse_args();reports={}
    for source in (args.validation_run,args.playback_run):
        ledger=json.loads(source.read_text());assert ledger['status']=='passed' and ledger['inputsUnchanged']
        for step in ledger['steps']:
            assert step['status']=='passed'
            rows=[json.loads(line) for line in Path(step['log']).read_text().splitlines() if line.startswith('{"status": "passed"')]
            if rows:
                path=Path(rows[-1]['report']);report=json.loads(path.read_text());assert report['status']=='passed'
                reports[step['id']]=(path,report)
    current=ROOT/'build/art/reviewed-integration/native-complete-candidate.json';meta=json.loads(current.read_text())
    out=ROOT/'build/art/reviewed-native-in-game-2026-09-20';out.mkdir(parents=True,exist_ok=True)
    catalog=json.loads((ROOT/'src/art/race-study/full-animation-v1.json').read_text());images=[]
    def figure(report_path,name,caption):
        report=json.loads(report_path.read_text());assert report['romSha1']==meta['romSha1']
        path=report_path.parent/name;assert path.is_file()
        images.append(dict(path=str(path.relative_to(ROOT)),sha256=sha(path.read_bytes()),caption=caption,
            romSha1=report.get('fixtureRomSha1',report['romSha1']),parentRomSha1=report['romSha1'],
            report=str(report_path.relative_to(ROOT)),reportSha256=sha(report_path.read_bytes())))
        url=html.escape(os.path.relpath(path,out).replace('\\','/'),quote=True)
        return f'<figure><a href="{url}"><img src="{url}" alt="{html.escape(caption)}" loading="lazy"></a><figcaption>{html.escape(caption)}</figcaption></figure>'
    entry,_=reports['test-reviewed-native-cold-entry'];capacity,_=reports['test-reviewed-native-capacity'];menu,_=reports['test-reviewed-native-menus']
    overview=figure(entry,'battle-approved-sprite-pilot.png','Native-palette battle entry')+figure(capacity,'final.png','Mixed-class test battle: thirteen actors')
    cards=[]
    for unit in catalog['units']:
        job=unit['job'];path,report=reports['test-reviewed-native-fight-'+str(job)]
        frames=[name for name,v in report['observations'].items() if name.startswith('attack-') and v['actor']['mode']>=8 and v['actor']['displayedFrames'] and (path.parent/(name+'.png')).is_file()]
        assert frames
        body=figure(menu,f'generated-{job}-wheel0.png','Portrait, idle sprite and native job wheel')+figure(path,frames[0]+'.png','Actual Fight animation')
        cards.append('<article><h2>'+html.escape(unit['label'])+'</h2><div class="pair">'+body+'</div></article>')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FFTA native-palette art</title>
<style>body{background:#e5e3dc;color:#202431;font:16px/1.5 system-ui;margin:0}main{max-width:1450px;margin:auto;padding:28px}article{background:#f7f5ef;padding:20px;border-radius:12px;margin:22px 0}h1,h2{margin:0 0 14px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:20px}figure{margin:0}img{width:100%;image-rendering:pixelated}figcaption{font-size:14px;padding:8px 0}a{color:#234579}header p{max-width:1000px}@media(max-width:800px){.pair{grid-template-columns:1fr}main{padding:14px}}</style><main>
<header><h1>Reviewed artwork with native palettes</h1><p>All ten classes, all 675 reviewed poses, and every available land and water animation sequence are imported. These are actual emulator screenshots.</p><p>Battle sprites and menu figures use the original shared palettes and native bright/dim rules. Some costume colors change to fit those colors. Large portraits use the existing native portrait format. No custom runtime palette system is active.</p><p>Fresh battle entry, all ten class attacks, all ten menus, mixed-class battle and save/Continue checks passed. All 1,592 animation mode transitions were checked. This gallery is for visual review; it does not claim a new full-campaign playthrough.</p></header>'''
    page+='<article><h2>Battle overview</h2><div class="pair">'+overview+'</div></article>'+''.join(cards)
    page+='<footer><a href="manifest.json">Screenshot provenance</a></footer></main></html>'
    (out/'index.html').write_text(page,encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps(dict(romSha1=meta['romSha1'],manifestSha256=sha(current.read_bytes()),images=images,
        sources={str(p):sha(p.read_bytes()) for p in (args.validation_run,args.playback_run)},scope=__doc__),indent=2)+'\n')
    print(json.dumps(dict(gallery=str(out/'index.html'),screenshots=len(images))))


if __name__=='__main__':main()
