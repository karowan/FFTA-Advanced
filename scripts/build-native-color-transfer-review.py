"""Build an evidence-linked gallery from a completed declared native-color run."""
import argparse, html, json, re, shutil
from pathlib import Path
from PIL import Image, ImageDraw
from native_art import ROOT, sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--human',action='store_true',help='Render the combined human candidate with changed-Samurai playback')
    args=parser.parse_args()
    run=json.loads(args.run.read_text());assert run['status']=='passed' and run['inputsUnchanged']
    reports={}
    for step in run['steps']:
        assert step['status']=='passed'
        for line in Path(step['log']).read_text().splitlines():
            if line.startswith('{') and line.rstrip().endswith('}'):
                record=json.loads(line)
                if 'report' in record:
                    path=Path(record['report']);report=json.loads(path.read_text());assert report['status']=='passed'
                    reports[step['id']]=(path,report)
    expected={'test-native-color-contract','test-native-color-import','test-native-color-entry',
              'test-native-color-fight-117','test-native-color-combo-117','test-native-color-water-117'}
    if args.human:expected={s.replace('test-native-color','test-human-native').replace('-117','-116') for s in expected}
    assert set(reports)==expected
    hashes={r['romSha1'] for p,r in reports.values()};assert len(hashes)==1
    out=ROOT/('build/art/native-human-integration-2026-09-20' if args.human else 'build/art/native-color-transfer-2026-09-20');cards=[];images=[]
    choices=[('Fight turn','test-native-color-fight-117','ready.png'),
             ('After Move','test-native-color-fight-117','moved.png'),
             ('Sword attack','test-native-color-fight-117','attack-55.png'),
             ('Combo jump','test-native-color-combo-117','attack-193.png'),
             ('Combo afterimages','test-native-color-combo-117','attack-266.png'),
             ('In water','test-native-color-water-117','water-0.png')]
    if args.human:
        choices=[(label,test.replace('test-native-color','test-human-native').replace('-117','-116'),name) for label,test,name in choices]
        choices[3]=('Combo strike','test-human-native-combo-116','attack-188.png')
        choices[4]=('Combo follow-through','test-human-native-combo-116','attack-381.png')
    for label,test,name in choices:
        original=reports[test][0].parent/name;dest=out/(test+'-'+name)
        shutil.copy2(original,dest);assert dest.read_bytes()==original.read_bytes()
        cards.append(f'<figure><img src="{dest.name}" alt="{html.escape(label)}"><figcaption>{html.escape(label)}</figcaption></figure>')
        images.append(dict(label=label,path=str(dest.relative_to(ROOT)),sha256=sha(dest.read_bytes()),
                           original=str(original.relative_to(ROOT)),report=str(reports[test][0].relative_to(ROOT))))
    evidence=[dict(test=k,path=str(p.relative_to(ROOT)),sha256=sha(p.read_bytes()),checks=len(r['checks'])) for k,(p,r) in reports.items()]
    report=dict(status='review-only',romSha1=next(iter(hashes)),runner=str(args.run),runnerSha256=sha(args.run.read_bytes()),
                screenshots=images,evidence=evidence,
                scope='Dark Knight battle colors across66 poses. Other classes, menus, portraits and full-game delivery remain unfinished.')
    if args.human:report['scope']='Both approved human native bases imported across132 poses; actual Samurai playback and unchanged tested Dark Knight bytes. Remaining races and final combined delivery unfinished.'
    (out/'review.json').write_text(json.dumps(report,indent=2)+'\n')
    candidate=json.loads((out/('candidate.json' if args.human else 'dark-knight-candidate.json')).read_text());assert candidate['romSha1']==report['romSha1']
    assets=[a for a in candidate['components']['reviewedActions']['assets'] if a['job']==(116 if args.human else 117)]
    sheet=Image.new('RGBA',(1408,912),'#e4e2dc');draw=ImageDraw.Draw(sheet)
    assert len(assets)==66
    for i,a in enumerate(assets):
        path=ROOT/a['source'];assert sha(path.read_bytes())==a['sourceSha256']
        im=Image.open(path).convert('RGBA');x,y=i%11*128,i//11*152
        draw.text((x+4,y+2),a['pose'],fill='black')
        sheet.alpha_composite(im.resize((128,128),Image.Resampling.NEAREST),(x,y+20))
    sheetname='imported-samurai-poses.png' if args.human else 'imported-dark-knight-poses.png'
    sheet.save(out/sheetname)
    links=''.join(f'<li>{html.escape(x["test"])}: {x["checks"]} checks</li>' for x in evidence)
    page='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Dark Knight native animation review</title>
<style>body{font:16px/1.5 system-ui;background:#e4e2dc;color:#202431;margin:24px}main{max-width:1500px;margin:auto}.screens{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:20px}figure{margin:0;background:#f5f3ed;padding:12px;border-radius:10px}img{width:100%;image-rendering:pixelated}a{color:#234579}p{max-width:950px}</style>
<main><h1>Dark Knight — native animation review</h1><p>The approved native base is now used in the animation set. All66 poses use colors from the unchanged game palette, with the existing movement and action timing.</p>
<p>These are intact in-game captures from the same tested ROM. This is the Dark Knight battle-art checkpoint; the other classes and final combined release are still in progress.</p><div class="screens">'''+''.join(cards)+'''</div>
<h2>Every Dark Knight pose</h2><p>The exact66 imported drawings, including the approved native standing base.</p><img src="imported-dark-knight-poses.png">
<p><a href="human-dark-knight/index.html">Original, rejected conversion and new conversion comparisons</a> · <a href="../native-color-study-2026-09-20/base-review.html">Samurai skin revision</a></p>
<details><summary>Verification and saved evidence</summary><ul>'''+links+'</ul><p><a href="review.json">Screenshot hashes and test reports</a></p></details></main>'
    if args.human:
        page=page.replace('Dark Knight','Samurai').replace('human-dark-knight/index.html','../native-color-transfer-2026-09-20/index.html')
        page=page.replace('Original, rejected conversion and new conversion comparisons','Previously tested Dark Knight screenshots')
        page=page.replace('Samurai skin revision','Approved human bases')
        page=page.replace('imported-dark-knight-poses.png',sheetname)
    page=page.replace('All66','All 66').replace('exact66','exact 66')
    (out/'index.html').write_text(page,encoding='utf-8')
    for link in re.findall(r'(?:href|src)="([^"]+)"',page):assert (out/link).is_file(),link
    print(json.dumps(dict(gallery=str(out/'index.html'),romSha1=report['romSha1'],screenshots=len(images))))


if __name__=='__main__':main()
