"""Read captured failing menu input through native command predicates.

Declared blocker diagnostic; no synthesized game results or interactive input.
"""
import ast,pathlib,json,hashlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text());ROM=pathlib.Path(meta['path']);LAB=ROM.parent
rom=ROM.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
RETURN,STACK=0x08000100,0x03007400
source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000')
exec(compile(ast.Module(body=[n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
iw=(LAB/'executor/execute-trap.iwram').read_bytes();samples=[]
S={p[2]:int(p[0],16) for line in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=line.split())==3}
S.update(meta['symbols']);unit=0x020005a8
for filename in ('start.ram','1/0/native-movement.ram','1/0/choices.ram'):
 path=LAB/'dancer-choice-playback'/filename;ram=path.read_bytes();m=ARM(rom,iw);m.put(0x02000000,ram)
 def call(name,*args):return m.call(S[name],*args,stack=STACK)
 p=0x0203a000
 bank=m.call(0x080cce60,unit,1,p,p+1,stack=STACK)
 sample=dict(file=filename,sha1=hashlib.sha1(ram).hexdigest(),range=list(m.read(p,2)),bank=hex(bank),
  commandJob=call('ffta_command_job',unit,1),available=call('ffta_ability_available',unit,90),
  ap=call('ffta_ap_value',unit,90),battleCommand=m.call(0x08025fdc,6,stack=STACK),
  usable=m.call(0x08133e18,unit,406,255,stack=STACK),lesson=m.read(bank+90*8,8).hex(),
  action=m.read(m.word(0x080ccd84)+406*28,28).hex())
 samples.append(sample)
report=dict(romSha1=meta['romSha1'],samples=samples)
import runpy
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
playback=[]
for delay in (180,600):
 e=E(LAB/'dancer-choice-playback/playback.gba')
 try:
  e.load(LAB/'dancer-choice-playback/start.state');e.run(1)
  rows=[]
  for index,key in enumerate((256,16,256,256,32,256)):
   e.run(8,key);e.run(delay);r=e.memory();p=struct.unpack_from('<I',r,0xf438)[0]-0x02000000
   rows.append(dict(index=index,key=key,mode=r[p+4],battlePhase=struct.unpack_from('<H',r,0xf5c4)[0]))
  playback.append(dict(delay=delay,steps=rows))
 finally:e.close()
report['timingControls']=playback
(LAB/'mystic-menu-diagnostic.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
