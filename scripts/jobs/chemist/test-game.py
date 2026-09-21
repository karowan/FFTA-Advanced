"""Fixed native Chemist menu/preview/cancel/commit path; no interactive driver."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import hashlib,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[3];P=ROOT/'build/expansion/probes';meta=_load_job_candidate(P/'chemist/current.json');ROM=pathlib.Path(meta['path']);LAB=ROM.parent;FIX=LAB/'fixture';OUT=LAB/'game';OUT.mkdir(exist_ok=True)
assert hashlib.sha1(ROM.read_bytes()).hexdigest()==meta['romSha1']==json.loads((FIX/'report.json').read_text())['romSha1']
registry=json.loads((ROOT/'build/expansion/registry.json').read_text());Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'));checks={}
def check(g,a,b):checks[g]=checks.get(g,0)+1;assert a==b,(g,a,b)
def tap(e,k,wait=120):e.run(8,k);e.run(wait)
def active(e):
 r=e.memory();p=struct.unpack_from('<I',r,0xf438)[0]-0x02000000
 return struct.unpack_from('<I',r,p+24)[0] if 0<=p<0x3f7e0 else 0
def menu(e,previous=None):
 for _ in range(901):
  if observe['menu_visible'](e) and (previous is None or active(e)!=previous):return
  e.run(10)
 raise AssertionError('Native turn menu did not appear')
def capture(e,label):
 e.screenshot(OUT/(label+'.png'));e.save(OUT/(label+'.state'));r=e.memory();(OUT/(label+'.ram')).write_bytes(r);return r
for race,unit,job,turns in ((3,0x4a0,120,2),(5,0x188,122,5)):
 e=Emulator(ROM)
 try:
  e.load(FIX/'battle-ready.state');e.run(1);check('native-race',e.memory()[unit+6],race)
  for offset in (5,7,0x35):e.set_memory(unit+offset,bytes([job]))
  e.set_memory(unit+0x2a,bytes(10));e.set_memory(unit+0x3a,bytes(3))
  for l in registry['lessons']:
   if l['id'].startswith('CHM-'):
    owner=next(o for o in l['owners'] if o['race']==race);e.set_memory(unit+0x40+owner['abilityIndex'],b'\xff')
  for i in range(turns):
   menu(e);previous=active(e)
   for k in (32,32,256,256):tap(e,k)
   menu(e,previous)
  check('native-active-owner',active(e),0x02000000+unit)
  e.set_memory(unit+0x18,struct.pack('<4H',1,300,50,50));e.set_memory(0x1940+362,b'\x05');ready=capture(e,f'{race}-ready')
  for k in (32,256,32,256):tap(e,k)
  capture(e,f'{race}-ability-menu');tap(e,256);capture(e,f'{race}-target');tap(e,256);preview=capture(e,f'{race}-preview')
  check('native-selected-Potion',struct.unpack_from('<H',preview,0xf3fc)[0],383)
  check('preview-no-payment',preview[0x1940:0x1e70],ready[0x1940:0x1e70]);check('preview-no-heal',struct.unpack_from('<H',preview,unit+24)[0],1)
  tap(e,1);cancel=capture(e,f'{race}-cancel');check('cancel-no-payment',cancel[0x1940:0x1e70],ready[0x1940:0x1e70])
  for k in (256,256,256):tap(e,k,180)
  e.run(1800);result=capture(e,f'{race}-result')
  check('native-committed-heal',struct.unpack_from('<H',result,unit+24)[0],26);check('native-one-Potion',result[0x1940+362],4);check('native-no-MP-payment',struct.unpack_from('<H',result,unit+28)[0],50)
  menu(e)
 finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],checks=checks,total=sum(checks.values()));(LAB/'game-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
