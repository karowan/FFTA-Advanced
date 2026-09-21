"""Rebuild the private field-query stage exactly, preserving existing indexes."""
import datetime,hashlib,importlib.util,json
from pathlib import Path
from native_art import ROOT,sha
out=ROOT/'build/art/field-query-rebuild'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
current=ROOT/'build/art/performance/field-query/current.json';view=json.loads(current.read_bytes())
component=json.loads(Path(view['fieldQueryFast']).read_bytes())
source=Path(component['sourceManifest']).parent/'live-palette-view.json'
paths=[current,Path(view['connectedManifest']),Path(view['connectedManifest']).parent/'live-palette-view.json',
       ROOT/'build/art/action-completion/current.json',ROOT/'build/art/pipeline/delivery/current.json']
before={p:p.read_bytes() for p in paths};expected=Path(view['path']).read_bytes()
try:
    spec=importlib.util.spec_from_file_location('field_rebuild',ROOT/'scripts/build-fast-field-query.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    rebuilt=builder.build(source,publish_current=False);actual=Path(rebuilt['path']).read_bytes()
    assert actual==expected and hashlib.sha1(actual).hexdigest()==view['romSha1']==rebuilt['romSha1']
    report=dict(status='passed',romSha1=view['romSha1'],romSha256=sha(actual),bytes=len(actual),scope=__doc__)
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error)),indent=2)+'\n');raise
finally:
    for p,data in before.items():p.write_bytes(data)
assert all(p.read_bytes()==data for p,data in before.items())
report['indexesRestoredExactly']=True
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',report=str(out/'report.json'))))
