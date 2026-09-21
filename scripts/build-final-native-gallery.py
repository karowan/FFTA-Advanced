"""Copy intact final-ROM screenshots into a review with authenticated evidence."""
import argparse,html,json,re,shutil
from pathlib import Path
from native_art import ROOT,sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',type=Path,action='append',required=True)
    args=parser.parse_args();out=ROOT/'build/art/native-final-integration-2026-09-20'
    meta=json.loads((out/'candidate.json').read_text());reports={};runs=[]
    for path in args.run:
        run=json.loads(path.read_text());assert run['status']=='passed' and run['inputsUnchanged']
        runs.append(dict(path=str(path),sha256=sha(path.read_bytes())))
        for step in run['steps']:
            assert step['status']=='passed'
            for line in Path(step['log']).read_text().splitlines():
                if line.startswith('{') and line.endswith('}'):
                    record=json.loads(line)
                    if 'report' in record:
                        p=Path(record['report']);report=json.loads(p.read_text())
                        assert report.get('status')=='passed'
                        if report.get('romSha1')==meta['romSha1']:reports[step['id']]=(p,report)
    screenshots=[]
    def copy(test,name,label):
        p,report=reports[test];source=p.parent/name;dest=out/(test+'-'+name)
        shutil.copy2(source,dest);assert source.read_bytes()==dest.read_bytes()
        screenshots.append(dict(label=label,path=str(dest.relative_to(ROOT)),sha256=sha(dest.read_bytes()),
            source=str(source),report=str(p),reportSha256=sha(p.read_bytes())))
        return f'<figure><img src="{dest.name}" alt="{html.escape(label)}"><figcaption>{html.escape(label)}</figcaption></figure>'
    catalog=json.loads((ROOT/'src/art/race-study/full-animation-v1.json').read_text());cards=[]
    for unit in catalog['units']:
        job=unit['job'];label=html.escape(unit['label'])
        card=copy(f'test-final-native-fight-{job}','moved.png','After moving')
        attacks=list(reports[f'test-final-native-fight-{job}'][0].parent.glob('attack-*.png'))
        attack=min(attacks,key=lambda p:(abs(int(p.stem.split('-')[1])-55),p.name))
        card+=copy(f'test-final-native-fight-{job}',attack.name,'Attack')
        card+=copy('test-final-native-menus',f'generated-{job}-wheel0.png','Portrait and job wheel')
        cards.append(f'<article><h2>{label}</h2><div class="screens">{card}</div></article>')
    extras=copy('test-final-native-capacity','final.png','Mixed-class battle after Status')
    extras+=copy('test-final-native-save','cold-continue.png','Cold Continue after saving')
    extras+=copy('test-final-native-inventory-ui','party-new-jobs.png','Equipment eligibility badges')
    page='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>New sprites in FFTA</title>
<style>body{font:16px/1.5 system-ui;background:#e4e2dc;color:#202431;margin:24px}main{max-width:1550px;margin:auto}article{background:#f6f4ee;padding:18px;margin:20px 0;border-radius:12px}.screens{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}figure{margin:0}img{width:100%;image-rendering:pixelated}figcaption{margin-top:6px}a{color:#234579}</style>
<main><h1>New sprites in FFTA</h1><p>All ten classes, using the game's native colors. The Samurai keeps the approved muted scarf. These are intact in-game captures from the assembled build.</p>
<p>Every animation drawing has been replaced, including movement, attacks, casting, reactions, defeat and water poses. Portraits, menu figures and equipment badges are included.</p>'''+''.join(cards)+'<article><h2>Battle and save checks</h2><div class="screens">'+extras+'</div></article><p><a href="evidence.json">Saved verification and screenshot records</a></p></main>'
    (out/'index.html').write_text(page,encoding='utf-8')
    evidence=dict(status='final review; packaging and visible launch separate',romSha1=meta['romSha1'],
        manifest=str(out/'candidate.json'),manifestSha256=sha((out/'candidate.json').read_bytes()),runs=runs,
        reports=[dict(test=k,path=str(p),sha256=sha(p.read_bytes()),checks=len(r['checks'])) for k,(p,r) in reports.items()],screenshots=screenshots)
    (out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    for link in re.findall(r'(?:src|href)="([^"]+)"',page):assert (out/link).is_file(),link
    print(json.dumps(dict(gallery=str(out/'index.html'),romSha1=meta['romSha1'],screenshots=len(screenshots))))


if __name__=='__main__':main()
