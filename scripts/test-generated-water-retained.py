"""Accept completed paired water capture with a bounded native-transfer oracle.

Reuses both actual movements and every recorded successful assertion. The
original failed report remains immutable. No emulator or player save is used.
"""
import copy,datetime,hashlib,json,struct
from pathlib import Path
from native_art import ROOT,TILES,OAM,sha,layout
from actor_render_evidence import actors
from native_body_display import retained

capture=ROOT/'build/art/generated-actions/battle/20260917T221612.382005Z'
source=capture/'failed.json';payload=source.read_bytes()
assert sha(payload)=='f69bdfe1cdb19c6465dba4037ed3c1e197aa5793edeede9245babc09f5c104b3'
prior=json.loads(payload);meta=json.loads((ROOT/'build/art/generated-actions/current.json').read_text())
assert prior['romSha1']==meta['romSha1']=='714f45eb9997ad39d11b13f92c35d5b0de1a0e7f'
rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
baseline=Path(meta['source']).read_bytes();assert hashlib.sha1(baseline).hexdigest()==meta['baseRomSha1']
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)

check(prior['error']=='All sampled unit-body graphics verified; auxiliary effects remain separate','Only graphics oracle failed after both complete scenarios')
check(prior['outcomes']['baseline']==prior['outcomes']['generated'],'Exact final gameplay outcomes match')
check(prior['outcomes']['generated']['position']==[48,16,464] and prior['outcomes']['generated']['resource']==260,'Native land return completed')
check(len(prior['renderFailures'])==1,'Exactly one retained mismatch')
failure=prior['renderFailures'][0]
check(failure==dict(case='generated',snapshot='cancel-move-40',address=134016,label='exact current or bounded retained display'),'Exact known mismatch identity')
for case in ('baseline','generated'):
    for name in ('water','land-return'):
        obs=prior['observations'][case][name]
        for ext,key in (('vram','vram'),):
            check(sha((capture/f'{case}-{name}.{ext}').read_bytes())==obs[key],case+'/'+name+' retained capture hash')
        check(any(a['resource']==(261 if name=='water' else 260) and a['displayedFrames'] for a in obs['actors']),case+'/'+name+' directly verified native body')
    for label in ('native submerged destination height','native wrapper selects water resource261','water body actually uploaded',
                  'native cancel returns original land position','native wrapper restores land resource260',
                  'water preserves inventory AP preferences status','water leaves transient roots retired'):
        check(case+' '+label in prior['checks'],case+' reused '+label)

observations=prior['observations']['generated'];keys=list(observations);name=failure['snapshot'];previous=keys[keys.index(name)-1]
now=observations[name];before=observations[previous]
ram=(capture/f'generated-{name}.ram').read_bytes();vram=(capture/f'generated-{name}.vram').read_bytes()
check(sha(vram)==now['vram'],'Mismatch capture VRAM authenticated')
a=next(a for a in actors(rom,ram,vram) if a['address']==failure['address'])
record=next(a for a in now['actors'] if a['address']==failure['address'])
check(all(record[k]==v for k,v in a.items()),'Independent parser reproduces failed body record')
b=next(x for x in before['actors'] if x['address']==failure['address'])
check(b['displayProof']=='current' and b['declaredSequence'] and len(b['displayedFrames'])==1,'Preceding sample is a directly proved frame')
t,o=struct.unpack_from('<II',rom,b['first']-0x08000000+20*b['displayedFrames'][0])
objects,_=layout(rom,OAM+o);size=sum(x['width']*x['height']//64 for x in objects)*32
check(size==b['allocation']*32==512,'Prior frame defines the entire allocation, no guessed tail')
block=vram[0x10000+a['tile']*32:0x10000+(a['tile']+a['allocation'])*32]
old=dict(direct=True,block=rom[TILES+t:TILES+t+size],identity=(b['resource'],b['tile'],b['allocation']),first=b['first'],index=b['index'])
pairs={frozenset((256+2*i,257+2*i)) for i in range(10)}
proof=retained(a,block,old,pairs)
check(proof=='queued land/water swap retains verified upload','Exact prior water image held for one queued land replacement')
following=observations[keys[keys.index(name)+1]]
check(any(x['address']==a['address'] and x['resource']==260 and x['displayProof']=='current' for x in following['actors']),'Following sample directly displays land body')
bad=bytearray(block);bad[0]^=1
check(retained(a,bytes(bad),old,pairs) is None,'Reject corrupted visible pixels')
for field,value in (('resource',258),('tile',a['tile']+1),('allocation',a['allocation']+1),('flags',0)):
    corrupt=dict(a);corrupt[field]=value
    check(retained(corrupt,block,old,pairs) is None,'Reject mismatched '+field)
corrupt=copy.deepcopy(old);corrupt['direct']=False
check(retained(a,block,corrupt,pairs) is None,'Reject chaining an unverified preceding upload')
check('Source world checkpoint unchanged' in prior['checks'],'Reused source preservation assertion')
out=ROOT/'build/art/generated-actions/water-retained'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
report=dict(status='passed',romSha1=meta['romSha1'],baseRomSha1=meta['baseRomSha1'],source=str(source),sourceSha256=sha(payload),
    checks=checks,reusedChecks=len(prior['checks']),observations={k:len(v) for k,v in prior['observations'].items()},outcomes=prior['outcomes'],
    correctedDisplay=dict(snapshot=name,previous=previous,proof=proof),
    scope='Completed paired Viking water-flag terrain fixture and native cancel to land, using unchanged retained captures with one exact pending land/water upload correction and six rejection controls. Background remains Giza. Not natural water-map, all-class/action/effect, custom-palette or finished-art acceptance.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status='passed',checks=len(checks),reusedChecks=len(prior['checks']),report=str(out/'report.json'))))
