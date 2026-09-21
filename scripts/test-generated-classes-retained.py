"""Recheck a complete retained all-class capture; never replay the emulator."""
import copy,datetime,hashlib,json
from pathlib import Path
from native_art import ROOT,sha
from generated_class_ui_evidence import verify
meta=json.loads((ROOT/'build/art/generated-classes/595782ba32f4a20ff2053218f8722ab5e491112d/manifest.json').read_text())
assert hashlib.sha1(Path(meta['path']).read_bytes()).hexdigest()==meta['romSha1']
folder=ROOT/'build/art/generated-classes/ui/20260917T210702.246719Z'
source=folder/'failed.json';prior=json.loads(source.read_text())
assert prior['romSha1']==meta['romSha1']
out=ROOT/'build/art/generated-classes/retained-tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    verify(meta,folder,prior['observations'],check)
    # Corruption control updates the supplied hash too, so acceptance must
    # fail on ownership rather than merely detecting a stale checksum.
    damaged=folder/'generated-116-wheel0.vram';raw=bytearray(damaged.read_bytes());raw[0]^=1
    corrupted=copy.deepcopy(prior['observations']);corrupted['generated']['116']['wheel0']['vram']=sha(raw)
    def reject(ok,label):
        assert ok,label
    try:verify(meta,folder,corrupted,reject,read=lambda p:bytes(raw) if p==damaged else p.read_bytes())
    except AssertionError as error:check('exact VRAM outside' in str(error),'corruption control rejects BG write outside sprite allocations')
    else:raise AssertionError('Ownership oracle accepted unowned corruption')
    seed=ROOT/'build/showcase/20260917T160011.215713Z/showcase.sav'
    check(hashlib.sha1(seed.read_bytes()).hexdigest()=='7831543efb239ef145764889214f8d83cd56eb14','original shared seed remains unchanged')
    report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,retainedSource=str(source),retainedSourceSha256=sha(source.read_bytes()),
        runtimeChecksRetained=prior['checks'],inputs=prior['inputs'],observations=prior['observations'],
        scope='Read-only corrected ownership comparison for the complete ten-class runtime capture. Native header remains alive after cancellation; no broad tolerances. Original failed runtime report retained. No new runtime, battle action/water, final art or release acceptance.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),checks=checks),indent=2)+'\n');print('Artifacts: '+str(out));raise
