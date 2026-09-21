"""Create a separate early-Cyril player showcase through native save/cold load.

Synthetic AP, equipment stock, gil and HP/MP are deliberate user-requested seed
inputs. This is save preparation, not proof of naturally earned progression.
"""
import ast,ctypes as C,datetime,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROM=ROOT/'roms/play/expansion-v0.7/FFTA_Expansion_v0.7.gba'
sha=lambda data:hashlib.sha1(data).hexdigest()
data=ROM.read_bytes();assert sha(data)=='1b070824a8dad4995434eee3ab40fa08187a6120'
seed_path=ROOT/'build/test-lab/early-town.sav';seed=seed_path.read_bytes()
OUT=ROOT/'build/showcase'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
OUT.mkdir(parents=True)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
counts={r['id']:r['totalCount'] for r in registry['races']}
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native equipment>','exec'))
checks=[];inputs=[];party=[];e=None;failure=None
def check(ok,name):
 assert ok,name
 checks.append(name)
def tap(key,wait=180):
 inputs.append([8,key,wait]);e.run(8,key);e.run(wait)
def cold(saved):
 global e
 e=E(ROM);e.set_memory(0,saved,0);e.run(3600)
 for key in (8,256,256,256):tap(key,300)
def context():return struct.unpack_from('<I',C.string_at(*e.maps[0x03000000]),0x2818)[0]-0x02000000
def wheel():
 r=e.memory();p=context();n=struct.unpack_from('<I',r,p+0x1270)[0]
 assert 0<n<=12
 return list(r[p+0x1278:p+0x1278+n]),r[p+0x1287+28*r[p+0x1275]]
def owned(r):return [r[0x80:0x1940],r[0x1940:0x1b40],r[0x1b40:0x1e70],r[0x1e80:0x1e98],r[0x1f64:0x1f68]]
try:
 cold(seed)
 original=e.memory();check({original[0x86+i*264] for i in range(6)}==set(range(1,6)),'Original six members cover all five races')
 for slot in range(6):
  offset=0x80+slot*264;race=original[offset+6]
  e.set_memory(offset+0x40,bytes([100])*min(counts[race],142 if race==1 else counts[race]))
  if race==1:e.set_memory(0x1b40+slot*34,bytes([100])*34)
 # All ordinary/equipment IDs, including recipe ingredients and all85 teachers.
 e.set_memory(0x1941,bytes([99])*460)
 e.set_memory(0x1f64,struct.pack('<I',999999))
 human=0
 for slot in range(6):
  offset=0x80+slot*264;race=original[offset+6]
  job={2:118,3:121,4:125,5:123}.get(race)
  if race==1:job=116+human;human+=1
  secondary=job+1 if job%2==0 else job-1
  tap(8);tap(256)
  if slot>=4:tap(32)
  for _ in range(slot%4):tap(128)
  tap(256);p=context()
  check(struct.unpack_from('<I',e.memory(),p+0x1d0c)[0]==0x02000000+offset,f'Native selected roster slot{slot}')
  tap(32);tap(32);tap(256,600)
  for _ in range(3):
   ids,selected=wheel()
   if job in [x&127 for x in ids]:break
   tap(2048,600)
  else:raise AssertionError(('Job missing',job))
  check(next(x for x in ids if x&127==job)&128,f'Native job{job} unlocked')
  check(secondary in [x&127 for x in ids] and next(x for x in ids if x&127==secondary)&128,f'Native alternate{secondary} unlocked')
  for _ in range(13):
   ids,selected=wheel()
   if selected==job:break
   tap(64)
  check(selected==job,f'Native selected job{job}')
  tap(256,300)
  if e.memory()[offset+7]!=job:tap(64);tap(256,1000)
  check(e.memory()[offset+7]==job,f'Native job change{job}')
  for _ in range(3):tap(1,240)
  # Both command identities are the native secondary-selection fields.
  e.set_memory(offset+8,bytes([secondary]));e.set_memory(offset+0x36,bytes([secondary]))
  m=ARM(data,C.string_at(*e.maps[0x03000000]));m.put(0x02000000,e.memory())
  for gear_slot in range(5):m.call(0x080caf78,0x02000000+offset,0,gear_slot)
  choices=[i for i in registry['items'] if any(t['jobId']==job for t in i['teaching'])]
  item=max(choices,key=lambda i:(i['weaponAttack'],i['magicPowerBonus']))
  check(m.call(0x080cb48c,0x02000000+offset,item['romItemId'],0)&1==0,f'Legal showcase weapon for{job}')
  m.call(0x080caf78,0x02000000+offset,item['romItemId'],0)
  e.set_memory(0,m.read(0x02000000,0x40000))
  e.set_memory(offset+0x18,struct.pack('<4H',500,500,200,200))
  e.set_memory(offset+0xd6,struct.pack('<H',10))
  combos=[o['abilityIndex'] for lesson in registry['lessons'] if lesson['type']=='Combo'
          for o in lesson['owners'] if o['jobId']==job]
  check(len(combos)==1,f'One showcase Combo for{job}')
  e.set_memory(offset+0x3c,bytes(combos))
  party.append(dict(slot=slot,race=race,job=job,secondary=secondary,weapon=item['name'],item=item['romItemId']))
  print('Prepared',party[-1],flush=True)
 expected=owned(e.memory())
 for lesson in registry['lessons']:
  for owner in lesson['owners']:
   matches=[p for p in party if p['race']==owner['race']]
   for p in matches:
    index=owner['abilityIndex'];address=0x80+p['slot']*264+0x40+index
    if owner['race']==1 and index>=144:address=0x1b40+p['slot']*34+index-144
    check((e.memory()[address]&127)>=lesson['ap']//10,'Mastered '+lesson['id']+' slot'+str(p['slot']))
 check(all(e.memory()[0x1940+i['romItemId']]==99 for i in registry['items']),'All85 teaching weapons stocked')
 e.screenshot(OUT/'prepared-world.png')
 for key,wait in ((8,180),(16,180),(256,180),(256,180),(256,180),(64,60),(256,300)):tap(key,wait)
 saved=e.memory(0);check(saved!=seed,'Native showcase save written')
 (OUT/'showcase.sav').write_bytes(saved)
 e.close();e=None;cold(saved)
 check(owned(e.memory())==expected,'Native cold Continue preserves entire showcase profile')
 check(e.memory()[0x2190:0x2192]==original[0x2190:0x2192],'Original early campaign stage preserved')
 check(seed_path.read_bytes()==seed,'Read-only seed preserved')
 e.save(OUT/'ready.state');e.screenshot(OUT/'ready.png')
 for key in (8,256):tap(key)
 e.screenshot(OUT/'party.png')
except BaseException as error:
 failure=repr(error)
 if e is not None:e.screenshot(OUT/'failure.png')
finally:
 if e is not None:e.close()
 report=dict(passed=failure is None,romSha1=sha(data),seedSha1=sha(seed),checks=checks,
  party=party,inputs=inputs,failure=failure,scope=__doc__,directory=str(OUT))
 if (OUT/'showcase.sav').exists():report['saveSha1']=sha((OUT/'showcase.sav').read_bytes())
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 (OUT.parent/'latest.json').write_text(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json')})+'\n',encoding='utf-8')
 print(json.dumps({'passed':report['passed'],'checks':len(checks),'failure':failure,'report':str(OUT/'report.json')}))
assert failure is None,failure
