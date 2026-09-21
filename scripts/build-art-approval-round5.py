"""Assemble five targeted revisions while retaining the complete review inventory."""
import importlib.util,json,re,shutil
from native_art import ROOT,sha
from art_review_zoom import add_zoom

GEN=ROOT/'build/art/ui-detail-v5-2026-09-20'
OLDGEN=ROOT/'build/art/anchor-ui-v4-2026-09-20'
BASE=ROOT/'build/art/job-art-approval-v4-2026-09-20'
OUT=ROOT/'build/art/job-art-approval-v5-2026-09-20'
ROUND_NUMBER=5
EDIT_COUNT=5
OLD_RESULTS_NAME='results.json'
INTRO='Five focused revisions: matching golden Dark Knight portrait eyes, a more centered frontal helmet badge, a smaller Samurai helmet, and distinct gold jewelry for each Viera job.'

def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    edits=json.loads((GEN/'results.json').read_text())
    old=json.loads((OLDGEN/OLD_RESULTS_NAME).read_text())
    replacements={(a['slug'],a['kind']):a for a in edits['assets']}
    assert len(replacements)==EDIT_COUNT
    merged={**old,'assets':[replacements.get((a['slug'],a['kind']),a) for a in old['assets']]}
    (GEN/'review-results.json').write_text(json.dumps(merged,indent=2)+'\n')
    for slug in ('viera-dancer','viera-mystic-knight'):
        shutil.copy2(OLDGEN/slug/'final-anchor-layer.png',GEN/slug/'final-anchor-layer.png')
    template=(ROOT/'scripts/art-approval-round4.html.txt').read_text(encoding='utf-8')
    template=template.replace('Round 04',f'Round {ROUND_NUMBER:02}')
    start=template.index('<p>All ten badge heads')
    end=template.index('</p>',start)+4
    template=template[:start]+'<p>'+INTRO+' Compare the previous round with the new native-palette proposals below. All other portraits, badges, animations and keyframes remain available on this page. Use Codex’s integrated browser annotations.</p>'+template[end:]
    template=template.replace('<main>','<main><section class="overview" id="latest"><h2>Latest revisions · before and after</h2><div id="latest-grid" class="grid"></div></section>',1)
    marker='for(const u of DATA.units){const slug=u.slug;'
    comparison="""for(const r of DATA.latest){const card=E('article',{class:'portrait-card','data-job':r.slug});card.append(E('h3',{},r.label));const row=E('div',{class:'grid'});for(const [src,label] of [[r.before,'Previous round'],[r.after,'Revised']])row.append(figure(src,label,r.width*r.scale,r.height*r.scale));card.append(row);document.querySelector('#latest-grid').append(card);}
"""
    template=template.replace(marker,comparison+marker)
    template=template.replace('No second fit-to-box reduction.','The Dark Knight eye revision uses area sampling to preserve the rounded shapes.')
    template=template.replace('Any letterboxing or changed output cell is recorded in the revision proof.','Letterboxing, sampling and fixed anchor registration are recorded in the revision proof.')
    template=add_zoom(template)
    path=GEN/'review-template.html';path.write_text(template,encoding='utf-8')
    builder=module('builder4','build-art-approval-round4.py')
    builder.BASE=BASE;builder.GEN=GEN;builder.OUT=OUT;builder.ROUND_NUMBER=ROUND_NUMBER
    builder.RESULTS_NAME='review-results.json';builder.TEMPLATE=path;builder.main()
    data=json.loads((OUT/'review-data.json').read_text());previous=json.loads((BASE/'review-data.json').read_text())
    data['latest']=[]
    for u,p in zip(data['units'],previous['units']):
        u['regeneration']=[a for i,a in enumerate(u['regeneration']) if not any(b['kind']==a['kind'] for b in u['regeneration'][i+1:])]
        for kind in ('icon','portrait'):
            key=(u['slug'],kind)
            if key not in replacements:continue
            before=p['badges']['eligible'] if kind=='icon' else p['newPortrait']
            after=u['badges']['eligible'] if kind=='icon' else u['newPortrait']
            data['latest'].append(dict(slug=u['slug'],label=u['label']+' '+('badge' if kind=='icon' else 'portrait'),before=before,after=after,width=32 if kind=='icon' else 48,height=16 if kind=='icon' else 56,scale=4 if kind=='icon' else 3))
        assert u['poses']==p['poses'] and u['sequences']==p['sequences'] and u['emptySlots']==p['emptySlots']
        for kind,field in [('portrait','newPortrait'),('icon','newIcon')]:
            if (u['slug'],kind) not in replacements:
                assert sha((OUT/u[field]).read_bytes())==sha((BASE/p[field]).read_bytes())
    (OUT/'review-data.json').write_text(json.dumps(data,indent=2)+'\n')
    html=template.replace('/*REVIEW_DATA*/',json.dumps(data).replace('</','<\\/'))
    (OUT/'index.html').write_text(html,encoding='utf-8')
    (OUT/'page-script.js').write_text(re.search('<script>(.*?)</script>',html,re.S)[1],encoding='utf-8')
    checker=module('check4','verify-ui-anchor-review.py')
    checker.GEN=GEN;checker.OUT=OUT;checker.RESULTS_NAME='review-results.json';checker.main()
    print(f'{EDIT_COUNT} revised surfaces; {20-EDIT_COUNT} unchanged portrait/icon surfaces verified byte-for-byte against previous round.')

if __name__=='__main__':main()
