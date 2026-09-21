"""Actual native results offer/Yes/No and SRAM lifecycle of the retry safeguard.

The immutable mission-lab fixture uses the native results flow with a native
generated Mythril Rush accepted record. Its preceding battle is Herb Picking;
this does not claim a campaign unlock or a Mythril Rush battle playthrough.
"""
import ast,ctypes as C,hashlib,importlib.util,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'build/expansion/probes';D=P/'quin-history';F=P/'mission-lab/mission111'
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'));ROM=D/'quin-history.gba';OUT=D/'in-game';OUT.mkdir(exist_ok=True)
checks=[]
CURRENT='--current' in sys.argv
if CURRENT:
 meta=json.loads((P/'combat.json').read_text());D=D/meta['romSha1'];D.mkdir(exist_ok=True)
 ROM=D/'current.gba';ROM.write_bytes((P/'combat.gba').read_bytes());assert hashlib.sha1(ROM.read_bytes()).hexdigest()==meta['romSha1']
 OUT=D/'in-game';OUT.mkdir(exist_ok=True);F=OUT/'fresh-results';F.mkdir(exist_ok=True)
 fixture=P/'quin-current-fixture';fm=json.loads((fixture/'report.json').read_text());assert fm['romSha1']==meta['romSha1'],'Recreate quin-current-fixture for current ROM'
def tap(e,k,wait=300):e.run(8,k);e.run(wait)
def quin(r):return [i for i in range(24) if r[0x84+264*i] and r[0x80+264*i:0x84+264*i]==bytes.fromhex('5f165508')]
def check(value,label):assert value,label;checks.append(label)
if CURRENT:
 # Recreate the results fixture through this build's native victory and ending.
 e=h['Emulator'](ROM)
 try:
  e.load(fixture/'battle-ready.state');check(e.memory()[0x1e79]==2,'ordinary native pre-offer import initializes tracking')
  for p in fm['otherUnitPointers']:e.set_memory(p-0x02000000+0x18,b'\0\0')
  for key in (32,32,256,256):tap(e,key,180)
  e.run(6000)
  for _ in range(13):tap(e,256)
  e.screenshot(F/'native-herb-ending.png')
  # Native accepted-record generator resolves the untouched first reward.
  sys.path.insert(0,str(ROOT/'tools/arm-python'))
  from unicorn import *
  from unicorn.arm_const import *
  UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
  tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
  exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native generator>','exec'))
  m=ARM(ROM.read_bytes(),C.string_at(*e.maps[0x03000000]));m.put(0x02000000,e.memory())
  for reg,value in ((UC_ARM_REG_R5,0x0855ae4c+70*111),(UC_ARM_REG_R8,111<<16),(UC_ARM_REG_R10,3),(UC_ARM_REG_SP,STACK)):m.u.reg_write(reg,value)
  m.u.hook_add(UC_HOOK_CODE,lambda u,a,s,d:u.emu_stop() if a==0x080d0162 else None);m.u.emu_start(0x080cff41,0,count=100000)
  check(m.u.reg_read(UC_ARM_REG_PC)==0x080d0162,'native accepted record generator returns')
  record=bytearray(m.read(0x03002850,16));record[2]&=~0x1c;record[4:6]=b'\0\0'
  check(struct.unpack_from('<HH',record,8)==(400,0),'Mythril original Silvril reward')
  e.set_memory(0x21c8,bytes(record));e.set_memory(0x2c30,struct.pack('<H',111));e.set_memory(0x2b08,bytes(256))
  # The session was initialized before the original offer; completing its flag
  # now models the approved prerequisite without creating legacy ambiguity.
  e.set_memory(0x1fd8,bytes((e.memory()[0x1fd8]|2,)))
  tap(e,256);tap(e,256);e.save(F/'01.state');e.screenshot(F/'results.png')
 finally:e.close()
 # Brand-new native boot: no supplied save or modified starting script.
 e=h['Emulator'](ROM)
 try:
  e.run(3600)
  for key in (8,256,256,256):tap(e,key,600)
  check(e.memory()[0x1e70:0x1e7a]==b'FFTAEXP1\x01\x02','actual native newgame initializes tracking before snowball battle')
  e.screenshot(OUT/'native-newgame.png')
 finally:e.close()
for label,seed,accept in [('failed',0,None),('declined',2,False),('accepted',2,True)]:
 e=h['Emulator'](ROM)
 try:
  e.load(F/'01.state')
  if not CURRENT:e.set_memory(0x1e79,b'\x02') # private diagnostic lacks load composition
  check(e.memory()[0x1e79]==2,label+' tracked history before offer')
  pointer,_=e.maps[0x03000000];C.memmove(pointer+0x34b0,struct.pack('<I',seed),4)
  tap(e,256);e.screenshot(OUT/(label+'-offer.png'))
  candidate=e.memory()[0x2fc4:0x2fc8]==bytes.fromhex('5f165508')
  check(candidate==(accept is not None),label+' native chance result')
  if accept is not None:
   tap(e,256) # default Yes
   if not accept:tap(e,64) # select No
   tap(e,256)
  for _ in range(4):tap(e,256)
  r=e.memory();check(bool(quin(r))==bool(accept),label+' roster ownership');check(r[0x1e79]==(3 if accept else 2),label+' history only on acceptance')
  check(any(r[0x2b08+4*i]==25 for i in range(64)),label+' original Silvril reward retained')
  e.screenshot(OUT/(label+'-world.png'));e.save(OUT/(label+'.state'));(OUT/(label+'.ram')).write_bytes(r)
  if accept:
   expected=r[0x80:0x1940]
   for k,w in [(8,40),(16,40),(256,40),(256,60),(256,60),(64,20),(256,300)]:tap(e,k,w)
   e.screenshot(OUT/'accepted-saved.png');saved=e.memory(0);(OUT/'accepted.sav').write_bytes(saved)
 finally:e.close()
e=h['Emulator'](ROM)
try:
 e.set_memory(0,saved,0);e.run(3600)
 for k,w in [(8,180),(256,60),(256,60),(256,180)]:tap(e,k,w)
 r=e.memory();check(r[0x80:0x1940]==expected,'native cold load restores all24 roster records');check(r[0x1e79]==3,'accepted history survives native SRAM cold load');check(quin(r)==[6],'Quin identity survives native cold load');e.screenshot(OUT/'cold-loaded.png')
finally:e.close()
report={'romSha1':hashlib.sha1(ROM.read_bytes()).hexdigest(),'checks':checks,'nativeSaveSha1':hashlib.sha1(saved).hexdigest(),'fixtureScope':__doc__}
(OUT/'results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'checks':len(checks),'romSha1':report['romSha1']}))
