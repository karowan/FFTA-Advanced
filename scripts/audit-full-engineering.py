"""Final assembled engineering review: authenticate E01-E04 and clean rebuild.

This read-only acceptance gate reuses reviewed runtime evidence on the identical
candidate. Packaging/launcher verification remains a subsequent gate. It never
turns failed or historical runs into newly executed current passes.
"""
import datetime, hashlib, json, subprocess
from pathlib import Path
from native_art import ROOT, sha

INDEXES=('native-art-native-performance-evidence.json','native-art-engineering-consumer-evidence.json',
    'native-art-shared-palette-evidence.json','native-art-capacity-followup-evidence.json',
    'native-art-campaign-review-evidence.json','native-art-engineering-rebuild-evidence.json')
CHECKPOINT='a28b624bb13c8f2f2597a4d4bd3999b17c234b99'
out=ROOT/'build/art/final-acceptance'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];files={};seen=set();historical_sources=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
def pin(path,expected=None):
    p=Path(path);p=p if p.is_absolute() else ROOT/p
    name=p.relative_to(ROOT).as_posix();digest=sha(p.read_bytes())
    if expected:check(digest==expected,'Exact reviewed evidence '+name)
    files[name]=digest
    if name.startswith('notes/') and p.suffix=='.json' and name not in seen:
        seen.add(name);visit(json.loads(p.read_text()))
    return p
def visit(value):
    if isinstance(value,dict):
        if isinstance(value.get('path'),str) and isinstance(value.get('sha256'),str):
            if isinstance(value.get('commit'),str):
                commit=value['commit'];check(len(commit)==40 and all(c in '0123456789abcdef' for c in commit),'Explicit historical source commit')
                raw=subprocess.check_output(['git','show',commit+':'+value['path']],cwd=ROOT)
                check(sha(raw)==value['sha256'],'Exact historical source stage '+value['path'])
                historical_sources.append(dict(path=value['path'],commit=commit,sha256=value['sha256']))
            else:pin(value['path'],value['sha256'])
        for item in value.values():visit(item)
    elif isinstance(value,list):
        for item in value:visit(item)
try:
    for name in INDEXES:pin('notes/'+name)
    meta_path=ROOT/'build/art/native-palettes/current.json';meta=json.loads(meta_path.read_text());rom=Path(meta['path']).read_bytes();old=Path(meta['fixtureSource']).read_bytes()
    check(hashlib.sha1(rom).hexdigest()==meta['romSha1']==CHECKPOINT,'Exact reviewed engineering ROM')
    check(hashlib.sha1(old).hexdigest()=='1b070824a8dad4995434eee3ab40fa08187a6120','Exact previously accepted gameplay release')
    check(rom[0x90000:0x9cc00]==old[0x90000:0x9cc00],'Complete native battle actor construction/list/sort region preserved')
    native=meta['components']['nativePaletteTransport'];live=meta['components']['livePalette']
    check(len(native['resources'])==20 and len(native['restoredNativeHooks'])==29,'Twenty class resources and restored native renderer')
    check(rom[live['symbols']['ffta_art_custom_mask']-0x08000000:live['symbols']['ffta_art_custom_mask']-0x08000000+4]==bytes(4),'No runtime custom palette ownership demand')
    build_path=ROOT/'build/art/engineering-rebuild/20260919T101346.342232Z/report.json';build=json.loads(build_path.read_text())
    check(build['status']=='passed' and build['byteIdentical'] and build['romSha1']==CHECKPOINT and Path(build['path']).read_bytes()==rom,'Entire source-reconstructed ROM byte-identical')
    base_path=Path(build['gameplayBase']['report']);check(sha(base_path.read_bytes())==build['gameplayBase']['sha256'],'Authenticated fresh gameplay source prefix')
    base=json.loads(base_path.read_text());check(base['passed'] and len(base['steps'])==8 and all(s['exitCode']==0 for s in base['steps']),'All eight source gameplay stages completed')
    art_path=build_path.parent/'art-report.json';art=json.loads(art_path.read_text());check(sha(art_path.read_bytes())==build['artReportSha256'] and art['status']=='passed' and art['romSha1']==CHECKPOINT,'All art stages and source PNG reconversions completed')
    source_pins={name:digest for name,digest in build['artSources'].items() if name.startswith('src/') or (name.startswith('scripts/') and Path(name).suffix in ('.py','.mjs','.js','.ps1') and not Path(name).name.startswith(('test-','audit-','probe-','diagnose-')))}
    for name,digest in source_pins.items():check(sha((ROOT/name).read_bytes())==digest,'Current rebuilt production source '+name)
    for name in ('notes/native-art-final-engineering-review.md','notes/native-art-campaign-compatibility.md','notes/native-art-gameplay-base.json','notes/native-art-build-inputs.json'):pin(name)
    checklist=(ROOT/'IMPLEMENTATION-CHECKLIST.md').read_text(encoding='utf-8')
    check(all('- [x] **'+gate in checklist for gate in ('E01','E02','E03','E04')),'Root accepted all four engineering behavior gates')
    source_pins['scripts/audit-full-engineering.py']=sha(Path(__file__).read_bytes())
    report=dict(passed=True,status='passed',romSha1=CHECKPOINT,romSha256=sha(rom),candidateManifest=str(meta_path),candidateManifestSha256=sha(meta_path.read_bytes()),
        checks=checks,shippingSources=source_pins,evidence=files,historicalSources=historical_sources,rebuildReport=str(build_path),rebuildReportSha256=sha(build_path.read_bytes()),
        approvedForPackaging=True,scope='Complete original USA game plus approved v0.7 gameplay and native graphics engineering; only final artwork/authored poses deferred. Reviewed targeted and retained evidence, not one uninterrupted campaign or arbitrary over-capacity mods. Package and launcher verification remains separate.')
    raw=json.dumps(report,indent=2)+'\n';(out/'report.json').write_text(raw,encoding='utf-8');(ROOT/'build/engineering-acceptance.json').write_text(raw,encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),evidenceFiles=len(files),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,evidence=files),indent=2)+'\n',encoding='utf-8');print('Artifacts: '+str(out));raise
