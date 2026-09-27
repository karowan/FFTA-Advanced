"""Native roster, Change Job and equipment screens for both new generic jobs.

Reuses the cold fixture's declared party before deployment. All subsequent
screen transitions use recorded native inputs; no menu results are injected.
"""
import ctypes as C,hashlib,json,runpy,struct
from pathlib import Path
from actor_render_evidence import actors
ROOT=Path(__file__).resolve().parents[1]
from chemist_candidate import candidate
meta=candidate()
ROM=Path(meta['path']);rom=ROM.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
OUT=ROM.parent/'ui';OUT.mkdir(exist_ok=True);FIX=ROM.parent/'fixture'
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
inputs=[];checks=[];observations=[];e=None;stage='start'
def check(ok,name):
 assert ok,(stage,name)
 checks.append(name)
def tap(key,wait=180):inputs.append([stage,key,8,wait]);e.run(8,key);e.run(wait)
def capture(label):
 stem=f'{job}-{label}';e.screenshot(OUT/(stem+'.png'));e.save(OUT/(stem+'.state'))
 r=e.memory();iw=C.string_at(*e.maps[0x03000000]);v=C.string_at(*e.maps[0x06000000])
 for ext,data in [('ram',r),('iwram',iw),('vram',v),('palette',C.string_at(*e.maps[0x05000000]))]:
  (OUT/(stem+'.'+ext)).write_bytes(data)
 return r,iw,v
try:
 for slot,job,resource in ((2,126,276),(3,127,278)):
  stage=f'{job} roster';e=E(ROM);e.load(FIX/'party-profile.state');e.run(1)
  e.set_memory(0x3f410+27*slot+22,bytes((18,18,0,0xD4,0)))
  tap(8);tap(256)
  for _ in range(slot):tap(128)
  capture('roster');tap(256)
  r,iw,v=capture('unit');p=struct.unpack_from('<I',iw,0x2818)[0]-0x02000000
  check(struct.unpack_from('<I',r,p+0x1d0c)[0]==0x02000080+264*slot,'native selected roster unit')
  check(struct.unpack_from('<I',r,p+0x2d50)[0]==0x02000000+p+0x7290,'party list beyond complete copy tail')
  tap(32);tap(32);tap(256,600);stage=f'{job} wheel'
  r,iw,v=capture('wheel');p=struct.unpack_from('<I',iw,0x2818)[0]-0x02000000
  check(r[p+0x1287+28*r[p+0x1275]]==job,'selected new job')
  figures=actors(rom,r,v);check(len(figures)==1,'one header actor')
  a=figures[0];check(a['resource']==resource,'approved class resource')
  check(a['declaredSequence'] and bool(a['displayedFrames']),'actual native body upload')
  observations.append(dict(job=job,header=a))
  tap(1);tap(16);tap(16);tap(256,600);stage=f'{job} equipment';r,iw,v=capture('equipment')
  p=struct.unpack_from('<I',iw,0x2818)[0]-0x02000000
  check(r[p+0x7240+38:p+0x7240+65]==r[0x3f410+27*slot:0x3f410+27*(slot+1)],'equipment copy retains complete status record')
  check(r[p+0x7240+65]==slot+1,'equipment copy retains exact origin')
  e.close();e=None
 stage='battle Status roundtrip';job=0;e=E(ROM);e.load(FIX/'battle-ready.state');e.run(1)
 menus=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'));menus['wait_for_menu'](e)
 before=e.memory()
 for key in (32,32,32,256):tap(key)
 r,iw,v=capture('battle-status');p=struct.unpack_from('<I',iw,0x2818)[0]-0x02000000
 # The accepted native-palette parent retired compact Status; both screens
 # use the full constructor. Validate that contract, including its new tail.
 check(0x10000<p<0x3f000-0x9990,'full Status allocation fits')
 check(struct.unpack_from('<I',r,0x3f200)[0]==0x50485231,'native full Status lifetime')
 check(struct.unpack_from('<I',r,p+0x2d50)[0]==0x02000000+p+0x7290,'Status list beyond complete copy tail')
 for _ in range(4):tap(128)
 tap(1)
 # The pixel anchor expects Move selected; native return keeps Status orange.
 for _ in range(3):tap(16)
 menus['wait_for_menu'](e);after=e.memory();capture('battle-status-return')
 check(before[0x80:0x1e70]==after[0x80:0x1e70],'Status preserves all player records')
 check(before[0x3f410:0x3f7dc]==after[0x3f410:0x3f7dc],'Status preserves full job bank')
 check(after[0x3ff70:0x3ff74]==bytes(4),'Status retires copy owner')
 e.close();e=None
 report=dict(passed=True,romSha1=meta['romSha1'],checks=checks,inputs=inputs,observations=observations)
except BaseException as error:
 if e:capture('failure')
 report=dict(passed=False,romSha1=meta['romSha1'],stage=stage,error=repr(error),checks=checks,inputs=inputs,observations=observations);raise
finally:
 if e:e.close()
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(passed=True,checks=len(checks),report=str(OUT/'report.json'))))
