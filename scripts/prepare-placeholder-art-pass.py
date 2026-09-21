"""Audit the installed placeholder bundle and prepare a private art-swap desk.

Reads the immutable packaged candidate, not whichever experiment is current.
No generation, ROM mutation, launch, save creation or evidence substitution.
"""
import datetime,hashlib,html,json,os
from pathlib import Path
from native_art import ROOT,sha

def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def rel(path):return Path(path).resolve().relative_to(ROOT).as_posix()
def checked(path,digest):
    path=ROOT/path;assert sha(path.read_bytes())==digest,'Changed private asset: '+str(path)
    return path

delivery=read(ROOT/'build/art/pipeline/delivery/current.json');rompath=ROOT/delivery['rom']['path'];folder=rompath.parent
out=ROOT/'build/art/placeholder-workbench'/delivery['rom']['sha1'];out.mkdir(parents=True,exist_ok=True)
run=out/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');run.mkdir()
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    raw=rompath.read_bytes();check(hashlib.sha1(raw).hexdigest()==delivery['rom']['sha1'] and sha(raw)==delivery['rom']['sha256'],'Packaged ROM exact')
    check(sha((folder/delivery['patch']['file']).read_bytes())==delivery['patch']['sha256'],'Packaged BPS exact')
    check(sha((folder/'ART-PIPELINE.md').read_bytes())==delivery['guideSha256'],'Packaged player guide exact')
    check(sha((folder/'candidate.json').read_bytes())==delivery['candidateManifestSha256'],'Immutable candidate manifest exact')
    check(read(folder/'manifest.json')==delivery,'Current launcher resolves exact immutable bundle')
    check(delivery['patch']['roundtrip'] and delivery['patch']['deterministic'] and delivery['patch']['wrongSourceRejected'],'Recorded exact patch roundtrip and wrong-source rejection')
    check(delivery['saves']==dict(directory='saves/art-pipeline/'+delivery['rom']['sha1'],importsPlayerSave=False),'Independent save path; no player import')
    candidate=read(folder/'candidate.json');parts=candidate['components']
    check(candidate['romSha1']==delivery['rom']['sha1'],'Packaged candidate identity')
    check(len(delivery['evidence'])==19,'Nineteen retained acceptance reports')
    for name,proof in delivery['evidence'].items():
        report=read(checked(proof['report'],proof['reportSha256']))
        runner=read(checked(proof['runner'],proof['runnerSha256']));checked(proof['log'],proof['logSha256'])
        check(report['status']=='passed' and report['romSha1']==candidate['romSha1'],'Exact-candidate accepted report '+name)
        check(runner['status'] in ('passed','failed') and runner['inputsUnchanged'],'Terminal retained runner '+name)
    jobs=[];body={x['job']:x for x in parts['livePalette']['artInputs']};portraits={x['job']:x for x in parts['portraits']['jobs']}
    for row in parts['classes']['jobs']:
        job=row['job'];actor=body[job];portrait=portraits[job]
        checked(actor['source'],actor['sourceSha256']);conversion=checked(actor['conversionManifest'],actor['conversionManifestSha256'])
        converted=read(conversion);checked(conversion.parent/'palette.bin',actor['paletteSha256'])
        checked(row['source'],row['sourceSha256']);checked(row['conversionManifest'],row['conversionManifestSha256'])
        checked(portrait['source'],portrait['sourceSha256'])
        from PIL import Image
        from native_art import pack_tiles
        for index,frame in enumerate(converted['frames']):
            tile=checked(conversion.parent/f'frame-{index:02}.4bpp',frame['tileSha256'])
            with Image.open(conversion.parent/f'frame-{index:02}.png') as image:check(pack_tiles(image,16)==tile.read_bytes(),'Indexed body pixels '+str((job,index)))
        with Image.open(conversion.parent/'native-sheet.png') as sheet:
            columns,rows=sheet.width//32,sheet.height//32
            check(sheet.width%32==sheet.height%32==0 and rows*columns==len(converted['frames']),'Native sheet grid '+str(job))
        resources=[r for r in parts['actions']['resources'] if r['job']==job]
        check({r['lifetime'] for r in resources}=={'land','water'},str(job)+' owns land and water resources')
        check(all(any(a['resource']==r['id'] for a in parts['livePalette']['assignments']) for r in resources),str(job)+' both resources populated')
        jobs.append(dict(job=job,name=row['name'],productionAccepted=False,
            body=dict(source=rel(actor['source']),sourceSha256=actor['sourceSha256'],conversionManifest=rel(conversion),conversionManifestSha256=actor['conversionManifestSha256'],palette=rel(conversion.parent/'palette.bin'),nativeSheet=rel(conversion.parent/'native-sheet.png'),rows=rows,columns=columns),
            menu=dict(source=row['source'],sourceSha256=row['sourceSha256'],conversionManifest=row['conversionManifest'],consumers=['equipment eligibility icon','job-wheel miniature','large portrait']),
            resourceIDs={r['lifetime']:r['id'] for r in resources},replacementCatalog='src/art/imagegen/catalog.json'))
    check([j['job'] for j in jobs]==list(range(116,126)),'All ten racial class placeholders present')
    extra=[]
    for name in ('status','equipment','weapon','effect'):
        part=parts[name];checked(part['sourceArt'],part['sourceArtSha256'])
        extra.append(dict(consumer=name,source=part['sourceArt'],sourceSha256=part['sourceArtSha256'],importer='scripts/generated_'+name+'_transport.py',scope=part.get('scope','Axe held-weapon placeholder, separate from body artwork')))
    inventory=dict(schema=1,status='Working placeholders; final artwork deferred by user',romSha1=candidate['romSha1'],bundle=rel(folder),launcher='Play Art Pipeline Preview.cmd',jobs=jobs,additionalAssets=extra,
        laterDrafts=['src/art/imagegen/samurai-v7-preview.json','src/art/imagegen/samurai-support-v1-preview.json'],
        caveats=['Repeated action poses and cropped water are intentional placeholders.',
                 'The installed Samurai is the packaged draft, not the later unshipped march/support experiments.',
                 'Human Dark Knight battle source differs from its menu source; inspect both.',
                 'Full replacement build must refresh pinned parents; historical byte-rebuild command intentionally refuses changed artwork.',
                 'Final sprite aesthetics and bespoke animation are deferred, not accepted.'])
    (out/'art-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n',encoding='utf-8',newline='\n')
    overrides=dict(schema=1,status='All ten installed body inputs; private replacement starting point',jobs=[
        dict(job=j['job'],source=j['body']['source'],sourceSha256=j['body']['sourceSha256'],conversionManifest=j['body']['conversionManifest'],conversionManifestSha256=j['body']['conversionManifestSha256']) for j in jobs])
    (out/'battle-overrides.json').write_text(json.dumps(overrides,indent=2)+'\n',encoding='utf-8',newline='\n')
    # Explicit source slots are a handoff template, never an automatic publisher.
    template=dict(schema=1,baseRomSha1=candidate['romSha1'],publishCurrent=False,productionAccepted=False,
        jobs=[dict(job=j['job'],name=j['name'],replacementSource=None,conversionManifest=None,replaceConsumers=['battle body','water body','equipment icon','miniature','portrait'],current=j) for j in jobs])
    (out/'replacement-template.json').write_text(json.dumps(template,indent=2)+'\n',encoding='utf-8',newline='\n')
    def link(path):return html.escape(os.path.relpath(ROOT/path,out).replace('\\','/'),quote=True)
    cards=[]
    for j in jobs:
        cards.append('<article><h2>'+html.escape(j['name'])+'</h2><p>Job '+str(j['job'])+' · placeholder</p><div class="native"><img src="'+link(j['body']['nativeSheet'])+'" alt="Converted battle frames"></div><p><a href="'+link(j['body']['source'])+'">Battle source</a> · <a href="'+link(j['menu']['source'])+'">Menu source</a> · <a href="'+link(j['body']['conversionManifest'])+'">Conversion record</a></p></article>')
    extras=''.join('<li>'+html.escape(a['consumer'])+': <a href="'+link(a['source'])+'">source image</a></li>' for a in extra)
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>FFTA placeholder art desk</title><style>body{font:16px system-ui;margin:32px;background:#18232b;color:#e9f2f4}a{color:#8fdaed}h1{font-size:30px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}article{background:#2f414c;padding:20px;border-radius:12px}h2{font-size:20px}.native{background:#536b72;padding:12px;min-height:190px}.native img{image-rendering:pixelated;width:100%;max-width:384px}p{line-height:1.6}.intro{max-width:900px}</style><h1>FFTA placeholder art desk</h1><div class="intro"><p>These are the sources in the separately playable placeholder package. Final sprite art and bespoke animations are deferred. Later Samurai experiments are separate.</p><p><a href="art-inventory.json">Complete inventory</a> · <a href="replacement-template.json">Replacement handoff template</a> · <a href="'+link('ART-PLACEHOLDERS.md')+'">Replacement guide</a></p><p>Play: <strong>Play Art Pipeline Preview.cmd</strong>. ROM '+candidate['romSha1']+'. Existing saves remain separate.</p></div><main>'+''.join(cards)+'</main><h2>Other connected assets</h2><ul>'+extras+'</ul></html>'
    (out/'index.html').write_text(page,encoding='utf-8',newline='\n')
    # Every local gallery image/link must resolve before handing it off.
    import re,urllib.parse
    for href in re.findall(r'(?:href|src)="([^"]+)"',page):check((out/urllib.parse.unquote(html.unescape(href))).resolve().is_file(),'Gallery link resolves '+href)
    report=dict(status='passed',romSha1=candidate['romSha1'],checks=checks,inventory=rel(out/'art-inventory.json'),gallery=rel(out/'index.html'),scope='Read-only immutable bundle/source/evidence audit and ten-job replacement inventory. Reuses completed runtime and BPS acceptance; no new gameplay, launch, publication or art acceptance.')
    (run/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(status='passed',checks=len(checks),report=str(run/'report.json'),gallery=str(out/'index.html'))))
except Exception as error:
    (run/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n',encoding='utf-8');raise
