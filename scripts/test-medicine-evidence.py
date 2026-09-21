"""Verify all ten actual medicine results from retained current-ROM playback.

Reuses fixed, saved inputs instead of replaying passing turns. A failed sweep
does not become a passing report: only individually verified native results
are accepted, with hashes for the original evidence and instrumented image.
"""
import hashlib,json,pathlib,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
OUT=pathlib.Path(meta['path']).parent;rom=pathlib.Path(meta['path']).read_bytes()
sha=lambda b:hashlib.sha1(b).hexdigest()
assert sha(rom)==meta['romSha1']
h=lambda r,p:struct.unpack_from('<H',r,p)[0]
w=lambda r,p:struct.unpack_from('<I',r,p)[0]
LOG=0x3ff50;T=0x33e4;sources=[];checks=0
def check(value):
 global checks
 checks+=1;assert value,(action,folder)
for action in range(383,393):
 chosen=None
 for report in sorted(OUT.glob('medicine-turns-*/report.json')):
  data=json.loads(report.read_text())
  if data['romSha1']!=meta['romSha1']:continue
  for result in data['outcomes']:
   if result['action']==action and result['casts'] and result['casts'][0]['action']==action:
    chosen=(report,data,result);break
  if chosen:break
 assert chosen,('Missing current-ROM actual medicine',action)
 report,data,result=chosen;folder=report.parent/f"{action}-{result['condition']}-{result['seed']}"
 image=(report.parent/'playback.gba').read_bytes();check(sha(image)==data['instrumentedSha1'])
 # The recorder may change only its reserved code and executor entry pointer.
 restored=bytearray(image);restored[0xa4344:0xa4348]=rom[0xa4344:0xa4348];restored[0x13f0000:0x13f1000]=rom[0x13f0000:0x13f1000]
 check(bytes(restored)==rom)
 before=(folder/'AI-turn-start.ram').read_bytes();after=(folder/'native-result.ram').read_bytes();final=(folder/'native-handoff.ram').read_bytes()
 actor=w(after,LOG+24)-0x02000000
 check(0x80<=actor<0x80+24*264 and (actor-0x80)%264==0)
 check(before[actor+6] in (3,5) and before[actor+5] in (120,122))
 check(w(after,LOG)==0x504c4159 and w(after,LOG+8)==action and w(after,LOG+16)>0)
 check(w(after,LOG+28)==0x02000000+T)
 item=w(after,LOG+136)
 recipe={383:(362,),384:(367,),385:(375,),386:(364,),387:(362,363),388:(365,),389:(374,),390:(364,375),391:(362,374),392:(362,371)}[action]
 if action in (384,386):check(item==recipe[0])
 check(before[0x1940+362:0x1940+376]==bytes((5,))*14)
 check(after[0x1940+362:0x1940+376]==bytes(4 if i in recipe else 5 for i in range(362,376)))
 check(h(before,actor+0x1c)==h(after,actor+0x1c)==100)
 if action in (383,386,387):check(h(after,T+0x18)-h(before,T+0x18)=={383:25,386:150,387:100}[action])
 if action==388:check(h(after,T+0x1c)-h(before,T+0x1c)==80)
 if action in (385,390):check(h(before,T+0x18)==0 and h(after,T+0x18)==h(after,T+0x1a)//2)
 if action in (384,389):check(before[T+0xe9]&2 and not after[T+0xe9]&2)
 if action==391:check(after[0x3f410+(24+(T-0x2fc4)//264)*22+8]&3)
 if action==392:check(after[T+0xeb]&3==3)
 check(final[0x3f728:0x3f72c]==bytes(4))
 evidence={str(report.relative_to(ROOT)):sha(report.read_bytes())}
 for name in ('declared-input','AI-turn-start','native-result','native-handoff'):
  for suffix in ('state','ram'):
   path=folder/(name+'.'+suffix);evidence[str(path.relative_to(ROOT))]=sha(path.read_bytes())
  state=(folder/(name+'.state')).read_bytes()
  check(state[0x19000+0x6170:0x19000+0x6d68]==rom[0xa38d24:0xa3991c])
 sources.append(dict(action=action,seed=result['seed'],recipe=recipe,actor=hex(actor+0x02000000),files=evidence))
report=dict(passed=True,romSha1=meta['romSha1'],total=checks,commands=10,sources=sources,
 limits=['Ten exact native positive cases across retained reports; failed full reports remain failed.','Long Throw destination correction has separate native placement evidence.','This is not final campaign or assembled-release acceptance.'])
(OUT/'medicine-evidence.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
