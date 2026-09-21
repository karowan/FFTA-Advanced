"""All ten existing placeholder body inputs through the common override path.

Compile/compose only; exact equality reuses installed gameplay evidence.
Restore historical manifest bytes and every existing delivery/current index.
"""
import datetime,hashlib,importlib.util,json
from pathlib import Path
from native_art import ROOT,sha

def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value

delivery=json.loads((ROOT/'build/art/pipeline/delivery/current.json').read_text(encoding='utf-8'))
package=(ROOT/delivery['rom']['path']).parent
candidate=json.loads((package/'candidate.json').read_text(encoding='utf-8'))
expected=(ROOT/delivery['rom']['path']).read_bytes();assert sha(expected)==delivery['rom']['sha256']
out=ROOT/'build/art/placeholder-workbench'/candidate['romSha1']/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
paths={ROOT/'build/art/pipeline/delivery/current.json',ROOT/'build/art/connected/current.json',ROOT/'build/art/live-palette/status-current.json',
       ROOT/'build/art/connected'/candidate['romSha1']/'manifest.json',ROOT/'build/art/connected'/candidate['romSha1']/'live-palette-view.json'}
for part in candidate['components'].values():
    if 'path' in part:
        p=Path(part['path']).parent/'manifest.json'
        if p.exists():paths.add(p)
before={p:p.read_bytes() for p in paths};checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    overrides=out.parent/'battle-overrides.json';spec=json.loads(overrides.read_text(encoding='utf-8'))
    check([r['job'] for r in spec['jobs']]==list(range(116,126)),'All ten jobs, including117, use common override interface')
    builder=module('placeholder_palette','build-live-art-palette.py');live=candidate['components']['livePalette'];builder.PARENT=Path(live['source']).parent/'manifest.json'
    built=builder.build(history_slots=20,all_classes=True,workspace_low_address=True,provisional_history=True,fast_rotation=True,
        owned_menu_buffer=True,shared_battle_menu_heap=True,compact_us_keyboard=True,compact_battle_status=True,
        art_overrides=overrides,publish_current=False)
    check(built['romSha1']==live['romSha1'],'All-ten override palette build exact installed bytes')
    for old,new in zip(live['artInputs'],built['artInputs']):
        check(old['job']==new['job'] and old['sourceSha256']==new['sourceSha256'] and old['paletteSha256']==new['paletteSha256'],'Exact selected class input '+str(new['job']))
    connected=module('placeholder_connected','build-connected-art.py').build(Path(built['path']).parent/'manifest.json',publish_current=False,fixture_source=candidate['fixtureSource'])
    check(connected['romSha1']==candidate['romSha1'] and Path(connected['path']).read_bytes()==expected,'Complete private override composition byte-exact to packaged ROM')
    # Preserve source provenance inside the immutable handed-off bundle.
    (out/'override-build.json').write_text(json.dumps(connected,indent=2)+'\n',encoding='utf-8',newline='\n')
finally:
    for p,raw in before.items():p.write_bytes(raw)
check(all(p.read_bytes()==raw for p,raw in before.items()),'All existing source manifests and installed indexes restored exactly')
report=dict(status='passed',romSha1=candidate['romSha1'],checks=checks,overrideManifest=str(overrides),overrideSha256=sha(overrides.read_bytes()),scope=__doc__)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
