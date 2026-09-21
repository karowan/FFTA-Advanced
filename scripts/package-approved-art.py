"""Package authenticated first-pass art and publish current native screenshots.

The prior release stays intact. Reuse its compatible save directory without
reading it into tests, copying it, or modifying any existing save file.
"""
# Source procedure: src/art/native-ui-review/README.md, sections 5-7.
# Packaging authenticates a completed import/test run. It does not grant visual
# approval to newer files or rerun image conversion on the accepted assets.
import argparse, hashlib, html, json, re, shutil
from pathlib import Path
from PIL import Image
from native_art import ROOT, sha

OUT=ROOT/'build/art/approved-first-pass-2026-09-20'
REVIEW=ROOT/'build/art/job-art-approval-v8-2026-09-20'
EXPECTED='f53fedb8421f48fd10faabf60700a5d7ed60ddf8'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',type=Path,required=True)
    args=parser.parse_args();runpath=args.run.resolve();run=json.loads(runpath.read_text())
    meta=json.loads((OUT/'candidate.json').read_text());rom=Path(meta['path']).read_bytes()
    assert hashlib.sha1(rom).hexdigest()==meta['romSha1']==EXPECTED
    # Require the declared affected-consumer set, not merely any passing run.
    # Graphics-only verification does not establish new campaign/save coverage.
    required={s['id'] for s in json.loads((ROOT/'scripts/approved-art-test-plan.json').read_text())['steps']}
    assert run['status']=='passed' and {s['id'] for s in run['steps']}==required
    reports={};records=[]
    def record(path):return dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path.read_bytes()))
    for step in run['steps']:
        assert step['status']=='passed'
        log=Path(step['log']);records.append(record(log));entries=[]
        for line in log.read_text().splitlines():
            try:entries.append(json.loads(line))
            except ValueError:pass
        paths=[Path(e['report']) for e in entries if isinstance(e,dict) and e.get('report')]
        assert len(paths)==1,(step['id'],paths)
        reportpath=paths[0];report=json.loads(reportpath.read_text())
        assert report['status']=='passed' and report['romSha1']==EXPECTED,(step['id'],reportpath)
        reports[step['id']]=reportpath;records.append(dict(test=step['id'],**record(reportpath)))
    # The generic runner also names an unrelated default engine ROM. The
    # component reports above authenticate the actual candidate for every step.
    protected={str(p):sha(p.read_bytes()) for base in (ROOT/'saves',ROOT/'roms/play') if base.exists() for p in base.rglob('*') if p.is_file()}
    release=ROOT/'build/releases/approved-first-pass';release.mkdir(parents=True,exist_ok=True)
    target=release/'FFTA_Reviewed_All_Classes.gba'
    if target.exists():assert target.read_bytes()==rom
    else:target.write_bytes(rom)
    save=ROOT/'saves/native-art-final-2026-09-20/FFTA_Reviewed_All_Classes.sav'
    assert save.exists(),'Retain the existing native-art save; do not silently create or replace it.'
    for path,digest in protected.items():assert sha(Path(path).read_bytes())==digest,path
    package=dict(status='verified approved first-pass artwork',rom=str(target),romSha1=EXPECTED,
                 manifest=str(OUT/'candidate.json'),manifestSha256=sha((OUT/'candidate.json').read_bytes()),
                 run=record(runpath),reports=records,saveDirectory=str(save.parent),
                 preservedSaveSha256=sha(save.read_bytes()),protectedFiles=protected,
                 previousRelease='build/releases/native-art-final/FFTA_Reviewed_All_Classes.gba')
    (release/'current.json').write_text(json.dumps(package,indent=2)+'\n')
    page=OUT/'review';page.mkdir(exist_ok=True)
    # Preserve all provenance, close-up controls, and all ordered keyframes.
    shutil.copytree(REVIEW,page,dirs_exist_ok=True)
    data=json.loads((page/'review-data.json').read_text())
    data.update(romSha1=EXPECTED,status='User-approved first pass, imported and verified in game.')
    fresh=[]
    def capture(path,label):
        dest=page/'assets'/('current-'+path.parent.name+'-'+path.name)
        shutil.copy2(path,dest)
        item=dict(image=dest.relative_to(page).as_posix(),label=label,source=record(path))
        fresh.append(item);return item['image']
    menus=reports['test-approved-menus'].parent
    for u in data['units']:
        u['currentMenu']=capture(menus/f"generated-{u['job']}-wheel0.png",u['label']+' · portrait and job wheel')
        for pose in u['poses']:
            pose.pop('proposal',None)
            asset=next(a for a in meta['components']['reviewedActions']['assets'] if a['job']==u['job'] and a['pose']==pose['id'])
            pose['sha256']=asset['tileSha256']
    for test,name,label in [('test-approved-inventory-ui','party-new-jobs.png','Inventory · all ten badges'),
                            ('test-approved-shop-ui','shop-new-jobs.png','Shop · all ten badges'),
                            ('test-approved-fight-116','moved.png','Samurai · after moving')]:
        capture(reports[test].parent/name,label)
    fight=reports['test-approved-fight-116'].parent
    attacks=sorted(fight.glob('attack-*.png'))
    if attacks:capture(attacks[-1],'Samurai · attack')
    data['currentScreenshots']=fresh
    (page/'review-data.json').write_text(json.dumps(data,indent=2)+'\n')
    text=(page/'index.html').read_text(encoding='utf-8')
    text=re.sub(r'const DATA=.*?;\nconst E=',lambda _: 'const DATA='+json.dumps(data).replace('</','<\\/')+';\nconst E=',text,flags=re.S)
    # Replace only explanatory review status. Historical comparisons remain
    # explicitly labeled previous build; current captures occupy the top.
    start=text.index('<header>');end=text.index('<nav id="jump">',start)
    text=text[:start]+'''<header><div class="eyebrow">FFTA / Approved first pass</div><h1>Approved artwork, now in the game.</h1><p>Current in-game screenshots are shown first. All ten portraits, badges, animations and ordered keyframes remain below, with enlarged frame inspection and Codex browser annotations.</p><div class="notice">Existing native palettes only. The previous release and all existing saves are preserved. Historical before-and-after images remain labeled as comparisons.</div>'''+text[end:]
    cards=''.join('<figure class="figure"><img class="screen" src="'+html.escape(s['image'])+'" alt="'+html.escape(s['label'])+'" width="480" height="320" loading="lazy"><figcaption>'+html.escape(s['label'])+'</figcaption></figure>' for s in fresh)
    text=text.replace('<main>','<main><section class="overview" id="current-game"><h2>Current in-game screenshots</h2><div class="grid">'+cards+'</div></section>',1)
    text=text.replace('New proposal · awaiting review','Approved first pass · imported')
    text=text.replace('These are import previews, not new in-game captures.','These exact approved badge pixels are now imported; current inventory and shop captures appear above.')
    text=text.replace('These images are not yet imported into the game. Other Samurai action poses still await visual approval.','These approved pixels are now imported. All action poses are included in this first pass.')
    text=text.replace('Walking color proposals:','Approved walking colors:')
    text=text.replace("const old=detail('Previous portrait · comparison only');","section.append(figure(u.currentMenu,'Current in-game portrait and job wheel',480,320,'screen'));const old=detail('Previous portrait · comparison only');")
    (page/'index.html').write_text(text,encoding='utf-8')
    (page/'page-script.js').write_text(re.search('<script>(.*?)</script>',text,re.S)[1],encoding='utf-8')
    def links(value):
        if isinstance(value,dict):
            for v in value.values():links(v)
        elif isinstance(value,list):
            for v in value:links(v)
        elif isinstance(value,str) and value.startswith('assets/'):assert (page/value).is_file(),value
    links(data)
    for link in re.findall(r'(?:href|src)="([^"#]+)"',text):
        if ':' not in link:assert (page/link).is_file(),link
    evidence=dict(romSha1=EXPECTED,run=record(runpath),reports=records,screenshots=fresh,
                  nativePaletteOnly=True,existingSavesPreserved=len(protected),review=record(page/'review-data.json'))
    (OUT/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(dict(romSha1=EXPECTED,screenshots=len(fresh),protectedFiles=len(protected),review=str(page/'index.html'))))


if __name__=='__main__':main()
