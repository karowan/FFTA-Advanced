"""Guarding Draw's Protect must precede the same action's native Counter."""
import ast,ctypes as C,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
meta=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text());ROM=pathlib.Path(meta['path']);LAB=ROM.parent
proof=json.loads((LAB/'game-report.json').read_text());assert proof['passed'] and proof['romSha1']==meta['romSha1']
OUT=LAB/'retaliation';OUT.mkdir(exist_ok=True);rom=ROM.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
control=bytearray(rom);offset=meta['symbols']['ffta_samurai_after_attempt']-0x08000000
control[offset:offset+2]=bytes.fromhex('7047');CONTROL=OUT/'no-protect-grant.gba';CONTROL.write_bytes(control)
Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];checks=0;outcomes=[]
def check(ok,detail):
 global checks
 checks+=1;assert ok,detail
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
half=lambda r,p:struct.unpack_from('<H',r,p)[0]
ACTOR,TARGET=0x80,0x33e4;setup=bytearray((LAB/'game-352/confirmation.ram').read_bytes())
for off in (5,7):setup[TARGET+off]=16
setup[TARGET+6]=2;setup[TARGET+0x3a]=53;setup[TARGET+0x40+53]=0xff
struct.pack_into('<5H',setup,TARGET+0x2a,460,0,0,0,0);struct.pack_into('<HH',setup,ACTOR+0x18,500,500)
m=ARM(rom,(LAB/'fixture/battle-ready.iwram').read_bytes());m.put(0x02000000,setup)
check(m.call(0x080cd4d4,0x02000000+TARGET)==8,'Counter8 assignment');check(m.call(0x0812e6a4,0x02000000+TARGET)==8,'Counter8 eligibility')
for seed in range(16):
 pair=[]
 for kind,path in [('unprotected',CONTROL),('preprotected',CONTROL),('guarding',ROM)]:
  e=Emulator(path)
  try:
   e.load(LAB/'game-352/confirmation.state');e.set_memory(0,bytes(setup))
   if kind=='preprotected':e.set_memory(ACTOR+0xeb,bytes([setup[ACTOR+0xeb]|2]));e.set_memory(ACTOR+0xde,b'\x03')
   C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4);e.run(8,256);e.run(2100);r=e.memory()
   e.save(OUT/f'{kind}-{seed}.state');e.screenshot(OUT/f'{kind}-{seed}.png');(OUT/f'{kind}-{seed}.ram').write_bytes(r)
   check(half(r,ACTOR+0x1c)==44,(kind,seed,'MP cost'));check(r[0x1e98]==1,(kind,seed,'Centered consumed once/Exposed retained'))
   check(bool(r[ACTOR+0xeb]&2)==(kind!='unprotected'),(kind,seed,'Protect state'))
   check(r[0x3ff44:]==bytes(4)+b'\xd7'*0xb8,'Guard changed')
   pair.append(dict(strike=250-half(r,TARGET+0x18),counter=500-half(r,ACTOR+0x18)))
  finally:e.close()
 check(len({p['strike'] for p in pair})==1,('Protect changed outgoing strike',seed,pair))
 check(pair[1]['counter']==pair[2]['counter'],('Protect was not applied before Counter',seed,pair))
 check(pair[2]['counter']<=pair[0]['counter'],('Protect increased damage',seed,pair))
 outcomes.append(dict(seed=seed,unprotected=pair[0],preprotected=pair[1],guarding=pair[2]))
 if {r['guarding']['strike']>0 for r in outcomes if 0<r['guarding']['counter']<r['unprotected']['counter']}=={False,True}:break
check({r['guarding']['strike']>0 for r in outcomes if 0<r['guarding']['counter']<r['unprotected']['counter']}=={False,True},'Missing hit/miss reduced native Counter')
report=dict(passed=True,romSha1=meta['romSha1'],controlSha1=hashlib.sha1(control).hexdigest(),checks=checks,outcomes=outcomes,scope='Actual Counter after hit and missed Guarding Draw, paired no-grant and pre-Protect native controls')
(LAB/'retaliation-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
