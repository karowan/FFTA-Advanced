"""Native suspend and cold Resume, with new jobs, lessons and packed effects.

Uses only the isolated cold-deployed candidate's emulator SRAM. Approved body
resources are checked against actual VRAM uploads before and after Resume.
"""
import collections,ctypes as C,hashlib,json,runpy,struct
from pathlib import Path
from actor_render_evidence import actors
ROOT=Path(__file__).resolve().parents[1]
from chemist_candidate import candidate
meta=candidate()
ROM=Path(meta['path']);image=ROM.read_bytes();assert hashlib.sha1(image).hexdigest()==meta['romSha1']
FIX=ROM.parent/'fixture';OUT=ROM.parent/'save';OUT.mkdir(exist_ok=True)
assert json.loads((FIX/'report.json').read_text())['romSha1']==meta['romSha1']
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
menus=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
checks=collections.Counter();inputs=[];e=None;stage='prepare';observed=[]
def check(n,a,b=True):checks[n]+=1;assert a==b,(stage,n,a,b)
def tap(k,wait=180):inputs.append((stage,k,8,wait));e.run(8,k);e.run(wait)
def capture(name):
 e.save(OUT/(name+'.state'));e.screenshot(OUT/(name+'.png'));r=e.memory()
 for label,data in [('ram',r),('iwram',C.string_at(*e.maps[0x03000000])),('vram',C.string_at(*e.maps[0x06000000]))]:
  (OUT/(name+'.'+label)).write_bytes(data)
 return r
def body_check():
 found=actors(image,e.memory(),C.string_at(*e.maps[0x06000000]))
 new=[a for a in found if a['resource'] in (276,278)]
 # Montblanc retains his original story appearance in every native job.
 # The other three are generic class bodies: two Physicians and one Sapper.
 check('three-generic-new-class-actors',len(new),3)
 check('both-new-body-resources',sorted(a['resource'] for a in new),[276,276,278])
 for a in new:
  check('body-native-descriptor',a['declaredSequence'])
  check('body-native-upload',bool(a['displayedFrames']))
  check('body-20-tile-OAM',a['expectedTiles'],20)
  check('body-allocation-fits',a['tileCount']<=a['allocation'])
 observed.append(dict(stage=stage,actors=new))
try:
 e=E(ROM);e.load(FIX/'battle-ready.state');e.run(1);menus['wait_for_menu'](e)
 # Legal scenario state: pending recovery/ward, smoke, a visible trap, and a
 # fuse on the current Viera. No turn is ended before native Suspend.
 for slot,data in ((1,bytes((0,48,0,0xD4,0))),(2,bytes((18,2,0,0,0))),(5,bytes((0,64,2,0,0xE0)))):
  e.set_memory(0x3f410+27*slot+22,data)
 e.run(30);before=capture('before');body_check()
 stage='native-suspend'
 for k in (1,8,16,256,256):tap(k)
 old=e.memory(0);tap(256,300);saved=e.memory(0)
 check('native-suspend-writes-flash',saved!=old)
 (OUT/'suspended.sav').write_bytes(saved);capture('suspended')
 e.close();e=None
 stage='cold-resume';e=E(ROM);e.set_memory(0,saved,0);e.run(3600)
 for k,wait in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):tap(k,wait)
 menus['wait_for_menu'](e);after=capture('resumed');body_check()
 check('all-live-job-effects-roundtrip',after[0x3f410:0x3f7dc],before[0x3f410:0x3f7dc])
 for slot,job in ((1,127),(2,126),(3,127),(4,126)):
  u=0x80+264*slot
  check('cold-new-job',after[u+5],job)
  check('cold-lessons',after[u+0x40:u+0xd0],before[u+0x40:u+0xd0])
  check('cold-HP-MP',after[u+0x18:u+0x20],before[u+0x18:u+0x20])
  check('cold-equipped-teaching-items',after[u+0x2a:u+0x34],before[u+0x2a:u+0x34])
 check('cold-inventory',after[0x1940:0x1e70],before[0x1940:0x1e70])
 check('cold-transient-route-empty',after[0x3f000:0x3f008],bytes(8))
 check('cold-action-roots-empty',after[0x3ff74:0x3ff8c],bytes(24))
 report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),inputs=inputs,actors=observed,
  saveSha1=hashlib.sha1(saved).hexdigest())
except BaseException as error:
 if e:capture('failure')
 report=dict(passed=False,romSha1=meta['romSha1'],stage=stage,error=repr(error),checks=dict(checks),inputs=inputs,actors=observed);raise
finally:
 if e:e.close()
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='actors'}))
