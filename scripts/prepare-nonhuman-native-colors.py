"""Review native color calibration without changing approved sprite geometry.

Imagegen supplies color references. This converter transfers colors only; it
does not draw, composite body parts, change alpha or invent palette entries.
"""
import argparse,html,importlib.util,json
import numpy as np
from PIL import Image
from native_art import ROOT,sha

spec=importlib.util.spec_from_file_location('transfer',ROOT/'scripts/study-approved-native-transfer.py')
transfer=importlib.util.module_from_spec(spec);spec.loader.exec_module(transfer)


def calibrated(frame,training,labels,colors,base_colors,extras):
    native,metrics=transfer.convert(frame,training,labels,colors,5)
    if extras:
        extra_training=np.concatenate([training]+[e[0] for e in extras])
        extra_labels=np.concatenate([labels]+[e[1] for e in extras])
        supplemental,_=transfer.convert(frame,extra_training,extra_labels,colors,5)
        rgba=np.asarray(frame.convert('RGBA'));indices=np.array(native)
        unseen=np.array([tuple(p[:3]) not in base_colors and p[3]>0 for p in rgba.reshape(-1,4)]).reshape(32,32)
        indices[unseen]=np.asarray(supplemental)[unseen]
        native.putdata(indices.ravel())
    return native,metrics


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--all-poses',action='store_true')
    args=parser.parse_args()
    study=ROOT/'build/art/native-color-study-2026-09-20'
    approvals=json.loads((ROOT/'src/art/race-study/nonhuman-native-color-v1.json').read_text())
    plans=approvals['bases']
    catalog=json.loads((ROOT/'src/art/race-study/full-animation-v1.json').read_text())
    out=ROOT/'build/art/native-nonhuman-integration-2026-09-20';out.mkdir(exist_ok=True)
    rows=[];images=[];conversions=[]
    for plan in plans:
        slug=plan['slug'];unit=next(u for u in catalog['units'] if u['slug']==slug)
        receipt=plan['generatedReference']
        sourcepath=ROOT/unit['front']['path'];targetpath=ROOT/receipt['converted']
        assert sha(sourcepath.read_bytes())==unit['front']['sha256']
        assert sha(targetpath.read_bytes())==receipt['convertedSha256']
        source=Image.open(sourcepath).convert('RGBA');target=Image.open(targetpath)
        colors=np.array(target.getpalette()[:48]).reshape(16,3).tolist()
        training,labels=transfer.fit(source,target)
        base_colors={tuple(p[:3]) for p in np.asarray(source).reshape(-1,4) if p[3]}
        extras=[]
        for ref in plan.get('supplementalReferences',[]):
            src=ROOT/ref['source']['path'];dst=ROOT/ref['converted']
            assert sha(src.read_bytes())==ref['source']['sha256'] and sha(dst.read_bytes())==ref['convertedSha256']
            extra=Image.open(dst);assert extra.getpalette()[:48]==target.getpalette()[:48]
            extras.append(transfer.fit(Image.open(src),extra))
        folder=out/slug;folder.mkdir(exist_ok=True)
        converted,metrics=calibrated(source,training,labels,colors,base_colors,extras)
        path=folder/'calibrated-base.png';converted.save(path,bits=4)
        row=dict(job=unit['job'],slug=slug,nativePalette=plan['nativePalette'],sourceBase=unit['front'],
                 generatedReference=receipt,converted=str(path.relative_to(ROOT)),convertedSha256=sha(path.read_bytes()),
                 alphaGridAgreement=float(np.mean((np.array(source)[:,:,3]>0)==(np.array(target)>0))),
                 method='Inverse-distance nearest reference-color voting in Oklab; five neighbors; original alpha; base RGB mappings frozen, supplementary references for previously unseen RGB',
                 status='native-base-awaiting-primary-review',**metrics)
        rows.append(row)
        images.extend([(slug+' source',source),('Generated reference',target),('Calibrated native',converted)])
        if args.all_poses:
            assert plan['status']=='native-base-primary-reviewed-for-integration'
            assert sha(path.read_bytes())==plan['convertedSha256'],'Reviewed base must reproduce exactly'
            records=[];poses=[]
            for pose in unit['poses']:
                sourcefile=ROOT/pose['output'];assert sha(sourcefile.read_bytes())==pose['outputSha256']
                frame=Image.open(sourcefile).convert('RGBA')
                native,_=calibrated(frame,training,labels,colors,base_colors,extras)
                dest=folder/(pose['id']+'.png');native.save(dest,bits=4)
                exact=pose['outputSha256']==unit['front']['sha256']
                if exact:assert dest.read_bytes()==path.read_bytes()
                records.append(dict(pose=pose['id'],source=pose['output'],sourceSha256=pose['outputSha256'],
                    selected=dict(path=str(dest.relative_to(ROOT)),sha256=sha(dest.read_bytes()),exactApprovedBase=exact)))
                poses.append((pose['id'],native))
            transfer.board(poses,folder/'native-poses.png')
            words=json.loads((ROOT/'src/art/race-study/native-color-study-v1.json').read_text())['nativePalettes'][plan['nativePalette']]['words']
            conversions.append(dict(job=unit['job'],poseCount=len(records),sourceBase=unit['front'],
                approvedNativeBase=plan['converted'],approvedNativeBaseSha256=plan['convertedSha256'],
                reviewAuthority='primary agent; not user approval',nativePalette=plan['nativePalette'],
                nativePaletteWords=words,method=row['method'],selectedNeighbors=5,records=records))
    # Generic comparison sheet uses conversion output; no pixels are authored.
    from PIL import ImageDraw
    canvas=Image.new('RGBA',(600,len(rows)*240),'#e4e2dc');draw=ImageDraw.Draw(canvas)
    for n,(label,im) in enumerate(images):
        x,y=n%3*200,n//3*240
        draw.text((x+8,y+4),label,fill='black')
        canvas.alpha_composite(im.convert('RGBA').resize((192,192),Image.Resampling.NEAREST),(x+4,y+20))
        canvas.alpha_composite(im.convert('RGBA'),(x+84,y+208))
    canvas.save(out/'base-comparison.png')
    (out/'bases.json').write_text(json.dumps(rows,indent=2)+'\n')
    cards=[]
    for row in rows:
        slug=row['slug'];label=html.escape(slug.replace('-',' ').title())
        cards.append(f'<article><h2>{label}</h2><img class="base" src="{slug}/calibrated-base.png">'
                     f'<p>Native palette {row["nativePalette"]}. Original sprite shape retained.</p>'
                     f'<details><summary>All converted poses (draft)</summary><img class="sheet" src="{slug}/native-poses.png"></details></article>')
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
        '<title>Other races: native color drafts</title><style>body{font:16px system-ui;background:#e4e2dc;color:#202431;margin:24px}'
        'main{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}article{padding:16px;background:#f5f3ed;border-radius:10px}'
        'img{image-rendering:pixelated}.base{width:128px;height:128px}.sheet{max-width:100%}</style>'
        '<h1>Other races: native color drafts</h1><p>Brighter native colors, with the approved pixel shapes preserved. These are not yet in-game acceptance.</p>'
        '<p>Water colors use a separate generated color reference while retaining the original pose shapes. Bard, Dancer and Mystic Knight use different existing native palette choices.</p>'
        '<main>'+''.join(cards)+'</main><p><a href="base-comparison.png">Source and color comparison</a> · '
        '<a href="../../../src/art/race-study/nonhuman-native-color-v1.json">Built-in imagegen prompts and references</a> · '
        '<a href="../native-human-integration-2026-09-20/index.html">Verified Samurai screenshots</a></p>',encoding='utf-8')
    if args.all_poses:
        humans=json.loads((ROOT/'build/art/native-human-integration-2026-09-20/conversions.json').read_text())
        humans['units'].extend(conversions)
        humans['status']='Human bases user-approved; nonhuman bases primary-reviewed; combined runtime acceptance pending'
        humans['selectorChanges']=[dict(job=job,before=before,after=after,reason=reason) for job,before,after,reason in (
            (123,0x10,0x01,'Existing palette 1 preserves the Bard red scarf'),
            (124,0x10,0x01,'Existing palette 1 preserves the Dancer red costume'),
            (125,0x01,0x10,'Existing palette 0 preserves Mystic Knight blue hair and clothing'))]
        (out/'conversions.json').write_text(json.dumps(humans,indent=2)+'\n')
    print(json.dumps(dict(out=str(out),bases=len(rows))))


if __name__=='__main__':main()
