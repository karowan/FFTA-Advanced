"""Native confirmation, gear cleanup and cold-load tests for all ten new jobs.

Only disposable emulator RAM receives AP mastery. The user's seed is read-only.
No new combat effects or natural prerequisite progression are claimed.
"""
import ctypes as C,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
arm=runpy.run_path(str(ROOT/'scripts/test-battle-inventory.py'))
from unicorn.arm_const import *
OUT=ROOT/'build/expansion/probes/all-new-jobs-in-game';OUT.mkdir(exist_ok=True)
probe='command-label'
frozen='--frozen' in sys.argv
manifest=json.loads((OUT/'manifest.json' if frozen else OUT.parent/(probe+'.json')).read_text())
data=(OUT/'frozen.gba' if frozen else OUT.parent/(probe+'.gba')).read_bytes()
engine=(OUT/'engine.bin' if frozen else ROOT/'build/expansion/engine.bin').read_bytes()
symbols=(OUT/'engine.symbols' if frozen else ROOT/'build/expansion/engine.symbols').read_text()
assert hashlib.sha1(data).hexdigest()==manifest['romSha1'],'Stale job-ui manifest'
assert hashlib.sha1(engine).hexdigest()==manifest['engineSha1'],'Stale job-ui engine'
assert data[0x1100000:0x1100000+len(engine)]==engine,'Embedded engine mismatch'
FAMILY=OUT
# Another parent build may run this test concurrently. Each ROM hash owns its
# emulator input, state files and screenshots, so shared rebuilds cannot swap
# the ROM or save state between individual cases in a running test.
OUT=FAMILY/hashlib.sha1(data).hexdigest();OUT.mkdir(exist_ok=True)
ROM=OUT/'frozen.gba';ROM.write_bytes(data);(OUT/'engine.bin').write_bytes(engine);(OUT/'engine.symbols').write_text(symbols)
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
for name,payload in [('frozen.gba',data),('engine.bin',engine),('engine.symbols',symbols.encode()),('manifest.json',json.dumps(manifest,indent=2).encode())]:
 (FAMILY/name).write_bytes(payload)
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
jobs=[j for j in registry['jobs'] if 116<=j['id']<=125]
if '--job' in sys.argv:jobs=[j for j in jobs if j['id']==int(sys.argv[sys.argv.index('--job')+1])]
counts={1:178,2:111,3:124,4:118,5:116};donors=[6,3,13,15,25,27,41,36,29,30]
seed_path=ROOT/'build/test-lab/early-town.sav';seed=seed_path.read_bytes();guard=bytes([0xd7])*0xbc
checks=[];seed_units=[]

def tap(e,key,wait=120):e.run(8,key);e.run(wait)
def cold(sram):
 e=h['Emulator'](ROM);e.set_memory(0,sram,0);e.run(3600)
 for key,wait in [(8,180),(256,60),(256,60),(256,180)]:tap(e,key,wait)
 e.set_memory(0x3ff44,guard);return e
def ctx(e):return struct.unpack_from('<I',C.string_at(*e.maps[0x03000000]),0x2818)[0]-0x02000000
def wheel(e):
 r=e.memory();p=ctx(e);n=struct.unpack_from('<I',r,p+0x1270)[0];assert 0<n<=12,n
 ids=[x&127 for x in r[p+0x1278:p+0x1278+n]]
 selected=r[p+0x1287+28*r[p+0x1275]]
 return p,ids,selected
def gear(unit):return list(struct.unpack_from('<5H',unit,0x2a))
def ap(r,offset,race,roster):
 inline=bytes(x&127 for x in r[offset+0x40:offset+0x40+min(counts[race],142 if race==1 else counts[race])])
 extra=bytes(x&127 for x in r[0x1b40+34*roster:0x1b40+34*(roster+1)]) if race==1 else b''
 return inline+extra
def capture(e,name,offset,race,roster,expected_ap):
 r=e.memory();assert r[0x3ff44:]==guard,('Guard',name)
 assert ap(r,offset,race,roster)==expected_ap,('AP preservation',name)
 e.screenshot(OUT/(name+'.png'))
def open_wheel(e,roster):
 # Verify the seed's visible No1..No6 selection against its canonical pointer.
 position={0:0,1:1,2:2,3:3,4:4,5:5}[roster]
 tap(e,8);tap(e,256)
 if position>=4:tap(e,32)
 for _ in range(position%4):tap(e,128)
 e.screenshot(OUT/f'roster-{roster}-selected.png')
 tap(e,256)
 p=ctx(e);actual=struct.unpack_from('<I',e.memory(),p+0x1d0c)[0]
 assert actual==0x02000080+264*roster,('Selected native roster unit',roster,hex(actual))
 tap(e,32);tap(e,32);tap(e,256,600)

machine=arm['ARM'](arm['native_iwram']());machine.put(0x08000000,data)
def labels():
 original=bytes.fromhex('8000401902683fe0');installed=data[0x74c34:0x74c3c]
 assert installed!=original,'Command label hook absent'
 command_table=machine.r32(0x08074c0c);other_table=machine.r32(0x08074c20)
 regs=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
 count=0
 for command in range(256):
  for slot in [0,1]:
   name=machine.r16(command_table+command*4) if command<126 else 73
   machine.put(0x02000080+0x35+slot,bytes([command]))
   for stack in [0x03007000,0x03006ffc]:
    results=[]
    for code in [original,installed]:
     machine.put(0x08074c34,code)
     machine.u.ctl_remove_cache(0x08074c34,0x08074c3c)
     values=[name&255,0x44111111,0x44222222,0x44333333,slot,other_table,0x03002818,0x02000080,0x44888888,0x44999999,0x44aaaaaa,0x44bbbbbb]
     for reg,val in zip(regs,values):machine.u.reg_write(reg,val)
     machine.u.reg_write(UC_ARM_REG_SP,stack);before=machine.get(0x02000000,0x40000)
     machine.u.emu_start(0x08074c35,0x08074cbc,count=5000)
     assert machine.u.reg_read(UC_ARM_REG_PC)==0x08074cbc
     assert machine.u.reg_read(UC_ARM_REG_SP)==stack,'Label stack changed'
     assert machine.get(0x02000000,0x40000)==before,'Label mutated unit/global RAM'
     results.append([machine.u.reg_read(reg) for reg in regs])
    old,new=results
    for i in [1,4,5,6,7,8,9,10,11]:assert new[i]==old[i],('Label live register',command,slot,i)
    expected=other_table+4*(name if 116<=command<=125 else name&255)
    assert new[0]==expected and new[2]==machine.r32(expected),('Full command text pointer',command,slot,new[:3],hex(expected))
    if not 116<=command<=125:assert new[:3]==old[:3],('Vanilla label changed',command,slot)
    count+=1
 machine.put(0x08074c34,installed)
 return count
label_checks=labels()
appearance={}
for job in jobs:
 jid=job['id'];donor=donors[jid-116];values={}
 for selector in [4,5,6,7,9,10,11]:
  actual=machine.call(0x080c8570,jid,jid,selector)
  expected=machine.call(0x080c8570,donor,donor,selector)
  assert actual==expected,('Donor appearance selector',jid,donor,selector,actual,expected)
  values[hex(selector)]=actual
 appearance[jid]=values
for job in jobs:
 jid,race=job['id'],job['race'];e=cold(seed)
 try:
  r=e.memory();units=[r[0x80+264*i:0x80+264*(i+1)] for i in range(6)]
  roster=next(i for i,u in enumerate(units) if u[6]==race);offset=0x80+264*roster;original=units[roster]
  if not seed_units:seed_units=[{'slot':i,'character':u[4],'jobRecord':u[5],'race':u[6],'job':u[7],'gear':gear(u)} for i,u in enumerate(units)]
  # Master both old and new lessons without altering gear, job or identity.
  e.set_memory(offset+0x40,bytes([100])*min(counts[race],142 if race==1 else counts[race]))
  if race==1:e.set_memory(0x1b40+34*roster,bytes([100])*34)
  expected_ap=ap(e.memory(),offset,race,roster);inventory=e.memory()[0x1940:0x1b40]
  open_wheel(e,roster);pages=[]
  for _ in range(3):
   p,ids,selected=wheel(e);pages.append(ids)
   if jid in ids:break
   tap(e,2048,600)
  else:raise AssertionError(('New job absent',jid,pages))
  for _ in range(13):
   p,ids,selected=wheel(e)
   if selected==jid:break
   tap(e,64)
  else:raise AssertionError(('Cannot select job',jid,selected,ids))
  capture(e,f'{jid}-selected',offset,race,roster,expected_ap)
  e.save(OUT/f'{jid}-selected.state')
  before_cancel=e.memory()[offset:offset+264]
  tap(e,1,300)
  cancelled=e.memory()[offset:offset+264]
  assert cancelled==before_cancel,('Cancel changed unit',jid,[(hex(i),a,b) for i,(a,b) in enumerate(zip(before_cancel,cancelled)) if a!=b])
  e.load(OUT/f'{jid}-selected.state');e.run(1);tap(e,256,300)
  confirmation='immediate'
  if e.memory()[offset+7]!=jid:
   confirmation='dialog'
   tap(e,1,300);assert e.memory()[offset:offset+264]==before_cancel,('Dialog cancel changed unit',jid)
   tap(e,256,300);tap(e,64);tap(e,256,1000)
  else:e.run(700)
  after=e.memory();unit=after[offset:offset+264]
  assert unit[7]==jid and unit[0x35]==jid,('Native job/command publication',jid,unit[7],unit[0x35])
  assert unit[0x34]==counts[race],('Published AP count',jid,unit[0x34])
  assert unit[4]==original[4] and unit[6]==race,'Identity/race changed'
  assert unit[5]==(original[5] if original[5]>=0x50 else jid),('Named alias preservation',jid,unit[5])
  assert after[0x1940:0x1b40]==inventory,'Job change changed owned inventory'
  machine.put(0x02000000,after);machine.put(0x03000000,C.string_at(*e.maps[0x03000000]))
  layout=machine.call(0x080caba8,0x02000000+offset,0x02000000+offset+0x2a,255,0)
  assert layout&1==0,('Illegal final equipment layout',jid,gear(unit),layout)
  for slot,item in enumerate(gear(unit)):
   if item:assert machine.call(0x080cb48c,0x02000000+offset,item,slot)&1==0,('Illegal retained gear',jid,item,slot)
  assert all(item==0 or item==old for item,old in zip(gear(unit),gear(original))),('Unexpected equipment replacement',jid)
  capture(e,f'{jid}-changed',offset,race,roster,expected_ap)
  for key in [1,1,1]:tap(e,key,240)
  # Reopen through native navigation; the current job must stay selected.
  open_wheel(e,roster);_,reopened,reselected=wheel(e);assert reselected==jid and jid in reopened
  capture(e,f'{jid}-reopened',offset,race,roster,expected_ap)
  for key in [1,1,1]:tap(e,key,240)
  for key,wait in [(8,180),(16,180),(256,180),(256,60),(256,60),(64,20),(256,300)]:tap(e,key,wait)
  saved=e.memory(0);assert saved!=seed;(OUT/f'{jid}-save.sav').write_bytes(saved)
  expected_unit=e.memory()[offset:offset+264]
 finally:e.close()
 e=cold(saved)
 try:
  actual=e.memory()[offset:offset+264]
  assert actual==expected_unit,('Cold-load complete unit',jid)
  assert e.memory()[0x1940:0x1b40]==inventory,'Cold-load inventory'
  capture(e,f'{jid}-cold-loaded',offset,race,roster,expected_ap)
  # A fresh menu rechecks the job label, donor presentation and command text.
  position={0:0,1:1,2:2,3:3,4:4,5:5}[roster]
  tap(e,8);tap(e,256)
  if position>=4:tap(e,32)
  for _ in range(position%4):tap(e,128)
  tap(e,256);tap(e,32);tap(e,256)
  capture(e,f'{jid}-command',offset,race,roster,expected_ap)
  tap(e,256);r=e.memory();p=ctx(e)
  commands=list(r[p+0x1134:p+0x1134+r[p+0x1132]])
  secondary=jid+1 if jid%2==0 else jid-1
  assert secondary in commands,('New secondary command unavailable',jid,secondary,commands)
  for _ in range(commands.index(secondary)):tap(e,32,40)
  e.screenshot(OUT/f'{jid}-secondary-selected.png')
  tap(e,256,300)
  e.screenshot(OUT/f'{jid}-secondary-after-A.png')
  r=e.memory();assert r[offset+0x36]==secondary and r[offset+8]==secondary,('Native secondary selection',jid,secondary,r[offset+0x36],r[offset+8])
  capture(e,f'{jid}-both-command-labels',offset,race,roster,expected_ap)
 finally:e.close()
 checks.append({'job':jid,'name':job['name'],'race':race,'roster':roster,'donorJob':donors[jid-116],
                'originalGear':gear(original),'finalGear':gear(unit),'layoutResult':layout,'pages':pages,
                'reopenedPage':reopened,'command':unit[0x35],'publishedCount':unit[0x34],
                'completeUnitColdLoad':True,'cancelPreservedUnit':True,'low7APPreserved':True,
                'appearanceSelectors':appearance[jid]})
 checks[-1]['confirmation']=confirmation
 checks[-1]['secondaryCommandSelected']=secondary
 (OUT/'progress.json').write_text(json.dumps(checks,indent=2));print('Passed',jid,job['raceName'],job['name'],flush=True)
assert seed_path.read_bytes()==seed,'Seed changed'
report={'passed':True,'romSha1':hashlib.sha1(data).hexdigest(),'engineSha1':manifest['engineSha1'],
        'artifactDirectory':str(OUT),'nativeLabelChecks':label_checks,'seedUnits':seed_units,'checks':checks,'scope':'All ten jobs through native selection, cancel/confirm, equipment cleanup, reopen, save and cold load; synthetic mastery only; no new battle effect claim'}
(OUT/'report.json').write_text(json.dumps(report,indent=2));(FAMILY/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps({'passed':True,'jobs':len(checks),'romSha1':report['romSha1']}))


