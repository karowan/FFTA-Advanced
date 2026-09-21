"""Actual Fight/Combo completion for every new job's permitted weapon family.
Requires the matching successful full combo in-game fixture report. Uses only
private RAM/savestates; original user games and saves are never opened.
"""
import ctypes as C,datetime,hashlib,json,pathlib,runpy,struct,sys
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1]
integrated='--integrated' in sys.argv;resume='--resume' in sys.argv;sha=lambda b:hashlib.sha1(b).hexdigest()
if integrated:
 meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text());candidate=pathlib.Path(meta['path']).parent
 pointer=json.loads((candidate/'combo-ui/latest.json').read_text());reportpath=pathlib.Path(pointer['report']);payload=reportpath.read_bytes();assert sha(payload)==pointer['reportSha1']
 report=json.loads(payload);assert report['romSha1']==meta['romSha1']
 source=pathlib.Path(pointer['directory'])
 for entry in report['completed'].values():
  for file,digest in entry.items():assert sha((source/file).read_bytes())==digest,('Changed Combo artifact',file)
 FAMILY=candidate/'combo-weapon-visuals';FAMILY.mkdir(exist_ok=True)
 previous=json.loads((FAMILY/'latest.json').read_text()) if resume else None
 OUT=pathlib.Path(previous['directory']) if previous else FAMILY/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
else:
 assert not resume,'Resume requires integrated mode'
 reportpath=ROOT/'build/expansion/probes/combos-in-game-tests.json';report=json.loads(reportpath.read_text());previous=None
 source=ROOT/'build/expansion/probes/combos-in-game'/report['romSha1']
 OUT=ROOT/'build/expansion/probes/combo-weapon-visuals'/report['romSha1']
assert report['passed'] and len(report['owners'])==10
if not integrated and '--frozen' not in sys.argv:assert report['romSha1']==json.loads((ROOT/'build/expansion/probes/combat.json').read_text())['romSha1'], 'Stale combo report'
rom=(source/'frozen.gba').read_bytes();assert hashlib.sha1(rom).hexdigest()==report['romSha1']
OUT.mkdir(parents=True,exist_ok=True);ROM=OUT/'frozen.gba';ROM.write_bytes(rom)
Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
TYPES={'SAM-C1':[9],'DRK-C1':[1,5,6],'VIK-C1':[31],'GEO-C1':[11,12],'CHM-C1':[7,12],'BRD-C1':[7,16],'DNC-C1':[7,8],'MYK-C1':[3,8]}
KEYS={1:32,2:128,3:16,4:128,5:64}
profiles=json.loads((ROOT/'build/expansion/probes/job-data.json').read_text())['profiles']
for job in profiles:
 allowed=[t for t in range(1,32) if (t<20 or t==31) and job['permissionMask']&(1<<(t-1))]
 assert sorted(TYPES[job['group']+'-C1'])==allowed, ('Incomplete approved weapon coverage',job['id'],allowed)
table=struct.unpack_from('<I',rom,0x79aec)[0]-0x08000000
items={t:next(i for i in range(1,461) if rom[table+i*32+8]==t) for t in set(sum(TYPES.values(),[]))}
checks=0;rows=[];completed={};provenance=[]
positive='--positive-control' in sys.argv
assert not positive or resume, 'Positive-control continuation requires authenticated resume'
if previous:
 prior_path=pathlib.Path(previous['report']);prior_bytes=prior_path.read_bytes();assert sha(prior_bytes)==previous['reportSha1'];prior=json.loads(prior_bytes)
 assert prior['romSha1']==report['romSha1'] and prior['sourceReportSha1']==sha(reportpath.read_bytes())
 for entry in prior['completed'].values():
  for file,digest in entry.items():assert sha((OUT/file).read_bytes())==digest,('Changed accepted artifact',file)
 checks=prior['checks'];rows=prior['cases'][:];completed.update(prior['completed']);provenance=prior.get('provenance',[])+[dict(report=str(prior_path),sha1=sha(prior_bytes))]

def checkpoint(passed,error=None):
 result={'passed':passed,'romSha1':report['romSha1'],'checks':checks,'cases':rows,'completed':completed,'provenance':provenance,'sourceReport':str(reportpath),'sourceReportSha1':sha(reportpath.read_bytes()),'error':error,'scope':'Actual native Fight and Combo UI through animation completion for every permitted weapon family on all10 new jobs; Bard knife Fight only because its Combo requires instruments. Disposable legal equipment/mastery fixtures, no user saves.'}
 path=OUT/('report-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')+'.json');path.write_text(json.dumps(result,indent=2))
 if integrated:(FAMILY/'latest.json').write_text(json.dumps(dict(directory=str(OUT),report=str(path),reportSha1=sha(path.read_bytes()),passed=passed,romSha1=report['romSha1']),indent=2))
 return result
def check(condition,detail):
 global checks
 assert condition,detail
 checks+=1

def tap(e,key):e.run(8,key);e.run(180)
for owner in report['owners']:
 unit=int(owner['unit'],16);target=int(owner['target'],16);race=owner['race'];name=owner['id']+'-race'+str(race);src=source/name
 for category in TYPES[owner['id']]:
  for command in ('Fight','Combo'):
   if command=='Combo' and owner['id']=='BRD-C1' and category==7:continue
   basekey=name+'-type'+str(category)+'-'+command
   if positive and basekey!='BRD-C1-race5-type7-Fight':continue
   # Seed6 is the observed Bard-knife positive; retain seed0 elsewhere.
   for seed in ((6,) if positive or basekey=='BRD-C1-race5-type7-Fight' else (0,)):
    if positive and any(r['job']==name and r['category']==category and r['targetHP']<999 for r in rows):break
    key=basekey+('-seed'+str(seed) if positive else '')
    if key in completed:continue
    case=OUT/key;case.mkdir(exist_ok=True);beforechecks=checks
    e=Emulator(ROM)
    try:
     e.load(src/'turn-ready.state');e.set_memory(unit+0x2a,struct.pack('<5H',items[category],0,0,0,0));e.set_memory(unit+0xd6,struct.pack('<H',3));e.set_memory(target+0x18,struct.pack('<HH',999,999));ready=e.memory();gear=ready[unit+0x2a:unit+0x34]
     tap(e,32);tap(e,256)
     if command=='Combo':tap(e,16)
     tap(e,256);tap(e,KEYS[race]);e.screenshot(case/'selected.png')
     # Deterministic native RNG; record hit/miss outcomes without replacing RNG.
     C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4)
     for _ in range(3):tap(e,256)
     e.run(1800)
     try:observe['wait_for_menu'](e,limit=6300)
     except AssertionError:
      e.save(case/'animation-stalled.state');(case/'animation-stalled.ram').write_bytes(e.memory())
      raise AssertionError(('weapon animation did not return control',name,category,command))
     e.screenshot(case/'completed.png')
     after=e.memory();check(after[unit+0x2a:unit+0x34]==gear,(name,category,command,'equipment'));check(after[unit:unit+4]==ready[unit:unit+4],(name,'identity'));check(struct.unpack_from('<H',after,unit+0xd6)[0]==(0 if command=='Combo' else 3),(name,category,command,'JP'));check(struct.unpack_from('<H',after,target+0x18)[0]>0,(name,'target survives'))
     e.save(case/'completed.state');rows.append({'job':name,'category':category,'item':items[category],'command':command,'seed':seed,'returnedControl':True,'targetHP':struct.unpack_from('<H',after,target+0x18)[0]});print(name,category,command,'finished',flush=True)
     completed[key]={str(p.relative_to(OUT)):sha(p.read_bytes()) for p in case.glob('*') if p.is_file()};checkpoint(False)
    except Exception as exc:
     checks=beforechecks;checkpoint(False,repr(exc));raise
    finally:e.close()
try:
 expected=sum(2*len(TYPES[o['id']])-(o['id']=='BRD-C1') for o in report['owners'])
 assert expected==39 and len([k for k in completed if '-seed' not in k])==expected,('Incomplete weapon-family coverage',len(completed))
 for job,category in {(r['job'],r['category']) for r in rows}:
  assert any(r['job']==job and r['category']==category and r['targetHP']<999 for r in rows), ('No successful hit for weapon family',job,category)
except Exception as exc:
 checkpoint(False,repr(exc));raise
result=checkpoint(True)
(OUT/'results.json').write_text(json.dumps(result,indent=2))
if not integrated:(ROOT/'build/expansion/probes/combo-weapon-visuals-tests.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ('completed','provenance')},indent=2))
