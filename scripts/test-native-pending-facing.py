"""Captured native Judge queued upload across a facing change, plus rejections."""
import datetime,json,struct
from native_art import ROOT,TILES,OAM,sha
from native_body_display import completed_pending_facing
root=ROOT/'build/art/generated-actions/battle/20260918T124919.470171Z'
raw=(root/'failed.json').read_bytes();assert sha(raw)=='48eb4b5d5a086a247a3e1e8b83f7d822a3c11d779cc65b253ccfdfc1f7288d20'
rom=(root/'generated/natural-water.gba').read_bytes();assert sha(rom)=='4ccf8396b9c643312d10891287bc00b78fc4ea178bbe56264893d0f1392021fd'
vram=(root/'generated-move-56.vram').read_bytes();assert sha(vram)=='5227efb0ecc21de0cc56d13d486e091018c3ce0bca192d82103059df24168727'
obs=json.loads(raw)['observations']['generated']
def actor(label):return next(a for a in obs[label]['actors'] if a['address']==133468)
before=actor('move-48');now=actor('move-56');after=actor('move-64')
source,oam=struct.unpack_from('<II',rom,before['first']-0x08000000+20*(before['index']-1))
start=0x10000+now['tile']*32;block=vram[start:start+now['allocation']*32];size=before['tileCount']*32
assert size==640 and block[:size]==rom[TILES+source:TILES+source+size] and oam+OAM+0x08000000==before['oam']
assert before['displayProof']==after['displayProof']=='current' and now['displayProof']=='unverified'
# Retained evidence proves the exact native640-byte command. Earlier tail/source
# values below are rejection-control inputs; fresh playback captures them live.
old=dict(before,tileOffset=source)
anchor=dict(direct=True,actor=old,block=b'\xa5'*size+block[size:],identity=(old['resource'],old['tile'],old['allocation']))
checks=[]
def check(ok,label):assert ok,label;checks.append(label)
check(completed_pending_facing(rom,now,block,anchor,8) is not None,'Exact captured queued native command at facing change')
for age in (0,9,16):check(completed_pending_facing(rom,now,block,anchor,age) is None,'Reject age '+str(age))
for field,value in (('resource',103),('tile',now['tile']+1),('allocation',now['allocation']+1),('flags',0),('index',2),('current',now['current']+20),('mode',4),('declaredSequence',False)):
 check(completed_pending_facing(rom,dict(now,**{field:value}),block,anchor,8) is None,'Reject changed current '+field)
for field,value in (('tileOffset',source+32),('oam',old['oam']+8),('flags',0),('current',old['current']-20),('index',0),('declaredSequence',False)):
 check(completed_pending_facing(rom,now,block,dict(anchor,actor=dict(old,**{field:value})),8) is None,'Reject changed preceding '+field)
for index in (0,size-1,size,len(block)-1):
 bad=bytearray(block);bad[index]^=1
 check(completed_pending_facing(rom,now,bytes(bad),anchor,8) is None,'Reject changed pixel or allocation tail '+str(index))
check(completed_pending_facing(rom,now,block,dict(anchor,direct=False),8) is None,'Reject inferred anchor')
check(completed_pending_facing(rom,now,block,None,8) is None,'Reject absent anchor')
out=ROOT/'build/art/pending-facing'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
report=dict(status='passed',checks=checks,sourceReportSha256=sha(raw),fixtureRomSha256=sha(rom),scope='Retained original Judge640-byte queued command plus exact metadata/age/pixel/tail rejection controls. Full preceding allocation/source history is verified during fresh live playback; not inferred from missing earlier raw captures.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
