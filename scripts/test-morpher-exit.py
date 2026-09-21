"""Native battle exit for all forms plus actual Blowup KO and one cold save.

Enemy HP zero is a declared exit precondition; this does not claim a won battle
or campaign progression. Native Wait/results/dialogue/cleanup/save all run.
"""
import pathlib
EXIT_SCOPE=__doc__;ROOT=pathlib.Path(__file__).resolve().parents[1]
helper=ROOT/'scripts/test-morpher-lifecycle.py'
head=helper.read_text().split("latest=LAB/'morpher-lifecycle-latest.json'")[0]
head=head.replace("'morpher-lifecycle-'+stamp","'morpher-exit-'+stamp")
exec(compile(head,str(helper),'exec'));SCOPE=EXIT_SCOPE;__doc__=SCOPE
life_pointer=json.loads((LAB/'morpher-lifecycle-latest.json').read_text());lp=pathlib.Path(life_pointer['report'])
assert sha(lp.read_bytes())==life_pointer['sha1'];life=json.loads(lp.read_bytes())
assert life['passed'] and life['romSha1']==meta['romSha1'] and life['producer']==pointer
sources=[dict(name=r['name'],directory=r['directory'],label='morphed',files=r['files']) for r in accepted['cases']]
ko=next(r for r in life['cases'] if r['phase']=='defeated')
sources.append(dict(name='Bomb-KO',directory=ko['directory'],label='defeated',files=ko['files']))
latest=LAB/'morpher-exit-latest.json';rows=[];retained=[];failure=None;e=None

def checkpoint(label):
 e.save(folder/(label+'.state'));e.screenshot(folder/(label+'.png'));(folder/(label+'.ram')).write_bytes(e.memory())
 (folder/(label+'.sav')).write_bytes(e.memory(0))
 return {p.name:sha(p.read_bytes()) for p in folder.glob(label+'.*')}

def report(passed=False):
 result=dict(passed=passed,romSha1=meta['romSha1'],instrumentedSha1=sha(instrumented),producer=pointer,lifecycle=life_pointer,
             scope=SCOPE,cases=rows,checks=dict(checks),retained=retained,failure=failure)
 p=OUT/'report.json';p.write_text(json.dumps(result,indent=2)+'\n');latest.write_text(json.dumps(dict(report=str(p),sha1=sha(p.read_bytes()),passed=passed)))
 return result

if '--resume' in sys.argv:
 prev=json.loads(latest.read_text());p=pathlib.Path(prev['report']);assert sha(p.read_bytes())==prev['sha1'];old=json.loads(p.read_bytes())
 assert old['producer']==pointer and old['lifecycle']==life_pointer
 for row in old['cases']:
  for file,digest in row['files'].items():assert sha((pathlib.Path(row['directory'])/file).read_bytes())==digest
 rows.extend(old['cases']);checks.update(old['checks']);retained.append(prev)
try:
 for entry in sources:
  name=entry['name'];case=name
  if any(r['name']==name for r in rows):continue
  source=pathlib.Path(entry['directory'])
  for file,digest in entry['files'].items():assert sha((source/file).read_bytes())==digest
  folder=OUT/name;folder.mkdir();e=E(TEST_ROM);e.load(source/(entry['label']+'.state'));e.run(1)
  before=e.memory();check('native-form-or-KO-input',bool(before[ACTOR+0xea]&4) if name!='Bomb-KO' else half(before,ACTOR+0x18)==0)
  for u in (0x32dc,0x33e4,0x2fc4,0x34ec,0x30cc,0x31d4):e.set_memory(u+0x18,bytes(2))
  checkpoint('exit-input')
  for key in (32,32,256,256):tap(e,key)
  e.run(6000)
  for page in range(20):
   tap(e,256,300)
   if page in (12,16,19):checkpoint('result-'+str(page))
  for _ in range(4):tap(e,1)
  after=e.memory();check('native-exit-clears-morph',not after[ACTOR+0xea]&4)
  check('native-exit-preserves-identity',after[ACTOR:ACTOR+8]==before[ACTOR:ACTOR+8])
  check('native-exit-preserves-Soul',after[ACTOR+0x2a:ACTOR+0x34]==before[ACTOR+0x2a:ACTOR+0x34])
  check('native-exit-preserves-captured-bank',after[0x2e78:0x2fb8]==before[0x2e78:0x2fb8])
  xy=after[0x2c16:0x2c1a];e.run(12,128 if half(after,0x2c16)<40 else 64);e.run(30)
  check('native-world-cursor-responds',e.memory()[0x2c16:0x2c1a]!=xy)
  files=checkpoint('world')
  if name=='Bomb-KO':
   # Herb Picking awards Lutia Pass. This is the native mandatory placement
   # screen, where Start is intentionally unavailable until placing the tile.
   m=ARM(image,C.string_at(*e.maps[0x03000000]));m.put(0x02000000,e.memory())
   giza=m.call(0x08036330,8)
   gx,gy=m.call(0x08035a20,giza-1)+6,m.call(0x08035a44,giza-1)+4
   options=[]
   for tile in range(1,31):
    if m.call(0x08036350,tile):continue
    x,y=m.call(0x08035a20,tile-1)+6,m.call(0x08035a44,tile-1)+4
    options.append(((x-gx)**2+(y-gy)**2,tile,x,y))
   _,tile,x,y=min(options)
   for _ in range(600):
    cx,cy=struct.unpack_from('<HH',e.memory(),0x2c16)
    if abs(cx-x)<=2 and abs(cy-y)<=2:break
    key=(128 if cx<x else 64) if abs(cx-x)>2 else (32 if cy<y else 16)
    e.run(1,key)
   else:raise AssertionError('Native territory cursor exceeded route bound')
   e.run(30);tap(e,256,300);checkpoint('territory-selected');tap(e,256,600)
   m=ARM(image,C.string_at(*e.maps[0x03000000]));m.put(0x02000000,e.memory())
   check('native-new-territory-placed',m.call(0x08036350,tile)!=0)
   for _ in range(4):tap(e,1)
   saved=e.memory();old_sram=e.memory(0)
   for step,(key,wait) in enumerate(((8,180),(16,180),(256,180),(256,180),(256,180),(64,60),(256,300))):
    tap(e,key,wait);checkpoint('save-step-'+str(step))
   sram=e.memory(0);check('normal-save-writes-native-SRAM',sram!=old_sram);(folder/'normal.sav').write_bytes(sram)
   e.close();e=E(ROM);e.set_memory(0,sram,0);e.run(3600)
   for key,wait in ((8,180),(256,60),(256,60),(256,180)):tap(e,key,wait)
   actual=e.memory()
   for lo,hi in ((0x80,0x1940),(0x1940,0x1f40),(0x2e78,0x2fb8)):
    check('cold-full-roster-inventory-bank',actual[lo:hi]==saved[lo:hi])
   check('cold-no-stale-morph',not actual[ACTOR+0xea]&4)
   files.update(checkpoint('cold'));files['normal.sav']=sha(sram)
  rows.append(dict(name=name,directory=str(folder),files=files));report();e.close();e=None;print(name,'native exit passed',flush=True)
except Exception as exc:
 import traceback;traceback.print_exc();failure=repr(exc)
 if e is not None:
  e.save(OUT/'failure.state');e.screenshot(OUT/'failure.png');(OUT/'failure.ram').write_bytes(e.memory())
finally:
 if e is not None:e.close()
result=report(failure is None and len(rows)==10)
print(json.dumps(dict(passed=result['passed'],cases=len(rows),checks=sum(checks.values()),failure=failure,report=str(OUT/'report.json'))))
assert result['passed'],failure
