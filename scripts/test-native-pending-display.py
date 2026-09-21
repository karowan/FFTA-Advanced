"""Independent retained native pixels and bounded pending-upload rejection tests."""
import datetime,json,struct
from native_art import ROOT,TILES,OAM,sha,layout
from native_body_display import pending_from_anchor

root=ROOT/'build/art/generated-actions/battle/20260918T004832.698616Z'
payload=(root/'failed.json').read_bytes()
assert sha(payload)=='c2c346249a0787db0aa549e0373759b0572a0ffefded435a1e22892990e28591'
prior=json.loads(payload);obs=prior['observations']['generated'];address=133468
rom=(root/'generated/natural-water.gba').read_bytes();proof=json.loads((root/'generated/fixture.json').read_text())
import hashlib
assert hashlib.sha1(rom).hexdigest()==proof['fixtureRomSha1']
def actor(name):return next(a for a in obs[name]['actors'] if a['address']==address)
before=actor('cancel-move-64');now=actor('cancel-move-80');after=actor('cancel-move-88')
t,o=struct.unpack_from('<II',rom,before['first']-0x08000000+20*before['displayedFrames'][0])
size=sum(v['width']*v['height']//64 for v in layout(rom,OAM+o)[0])*32
vram=(root/'generated-cancel-move-80.vram').read_bytes();p=0x10000+now['tile']*32
assert sha(vram)==obs['cancel-move-80']['vram'] and vram[p:p+size]==rom[TILES+t:TILES+t+size]
assert before['displayProof']=='current' and after['displayProof']=='current' and size==640
# The retained capture independently proves visible pixels only. Full-allocation
# identity below is a rejection-control input; the fresh runtime records it live.
block=vram[p:p+now['allocation']*32]
anchor=dict(direct=True,block=block,identity=(before['resource'],before['tile'],before['allocation']),first=before['first'],index=before['index'])
checks=['Authenticated failed report and fixture','Exact640-byte original Judge frame retained during pending facing','Directly verified frame before and after bounded hold']
def check(ok,label):
    assert ok,label
    checks.append(label)
for age in (8,16):check(pending_from_anchor(now,block,anchor,age) is not None,'Accept verified anchor within '+str(age)+' frames')
for age in (-1,0,17,24):check(pending_from_anchor(now,block,anchor,age) is None,'Reject age '+str(age))
for field,value in (('resource',103),('tile',now['tile']+1),('allocation',now['allocation']+1),('flags',0)):
    check(pending_from_anchor(dict(now,**{field:value}),block,anchor,16) is None,'Reject altered '+field)
bad=bytes([block[0]^1])+block[1:]
check(pending_from_anchor(now,bad,anchor,16) is None,'Reject changed uploaded pixels')
check(pending_from_anchor(now,block,dict(anchor,direct=False),16) is None,'Reject inferred anchor')
check(pending_from_anchor(now,block,None,16) is None,'Reject absent anchor')
out=ROOT/'build/art/pending-display'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
report=dict(status='passed',checks=checks,sourceReportSha256=sha(payload),romSha1=prior['romSha1'],scope='Retained visible640-byte native Judge facing hold, plus strict16-frame/identity/bytes/pending/direct-anchor controls. Full allocation history is tested by live natural-water playback, not inferred from missing earlier raw capture.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
