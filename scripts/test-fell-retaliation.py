"""Native Counter immediately after Fell, compared to a no-Exposed control."""
import ast,ctypes as C,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
from fell_test_context import load_context
meta=load_context('--current' in sys.argv);ROM=pathlib.Path(meta['path']);LAB=ROM.parent
OUT=LAB/'retaliation';OUT.mkdir(exist_ok=True);rom=ROM.read_bytes();sha=lambda b:hashlib.sha1(b).hexdigest();assert sha(rom)==meta['romSha1']
control=bytearray(rom);offset=meta['symbols']['ffta_exposed_paid_commit']-0x08000000
# Diagnostic oracle only: return success without storing the drawback. Both
# variants retain the same Fell coefficient, payment, RNG and Counter code.
control[offset:offset+4]=bytes.fromhex('01207047');CONTROL=OUT/'no-exposed-control.gba';CONTROL.write_bytes(control)
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'));checks=0;outcomes=[]
def check(ok,msg):
 global checks
 checks+=1
 assert ok,msg
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
half=lambda r,p:struct.unpack_from('<H',r,p)[0]
ACTOR,TARGET=0x398,0x33e4
setup=bytearray((LAB/'actual/confirmation.ram').read_bytes())
for off in (5,7):setup[TARGET+off]=16
setup[TARGET+6]=2;setup[TARGET+0x3a]=53;setup[TARGET+0x40+53]=0xff
struct.pack_into('<5H',setup,TARGET+0x2a,460,0,0,0,0)
struct.pack_into('<HH',setup,ACTOR+0x18,500,500)
m=ARM(rom,(LAB/'actual/confirmation.iwram').read_bytes());m.put(0x02000000,setup)
check(m.call(0x080cd4d4,0x02000000+TARGET)==8,'Native assignment is not Counter8')
check(m.call(0x0812e6a4,0x02000000+TARGET)==8,'Native Counter is not eligible')
for seed in range(16):
 pair=[]
 for kind,path in [('control',CONTROL),('exposed',ROM)]:
  e=h['Emulator'](path)
  try:
   e.load(LAB/'actual/confirmation.state');e.set_memory(0,bytes(setup))
   C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4)
   e.run(8,256);e.run(2100);r=e.memory()
   e.save(OUT/f'{kind}-{seed}.state');e.screenshot(OUT/f'{kind}-{seed}.png');(OUT/f'{kind}-{seed}.ram').write_bytes(r)
   check(half(r,ACTOR+0x1c)==34,(kind,seed,'MP cost'))
   check(r[0x1e9b]==(1 if kind=='exposed' else 0),(kind,seed,'Incorrect drawback control'))
   check(r[0x3ff44:]==bytes([0xd7])*0xbc,'Guard changed')
   pair.append(dict(fellDamage=250-half(r,TARGET+0x18),counterDamage=500-half(r,ACTOR+0x18)))
  finally:e.close()
 check(pair[0]['fellDamage']==pair[1]['fellDamage'],('Retaliation changed Fell',seed,pair))
 check(pair[1]['counterDamage']==pair[0]['counterDamage']*6//5,('Counter was not amplified once',seed,pair))
 outcomes.append(dict(seed=seed,control=pair[0],exposed=pair[1]))
 # Require immediate retaliation for both a landed and missed Fell.
 if {row['control']['fellDamage']>0 for row in outcomes if row['control']['counterDamage']>0}=={False,True}:break
check(any(row['control']['counterDamage']>0 for row in outcomes),'No native Counter executed in bounded seeds')
check({row['control']['fellDamage']>0 for row in outcomes if row['control']['counterDamage']>0}=={False,True},'Missing hit/miss Counter coverage')
report=dict(passed=True,romSha1=sha(rom),controlSha1=sha(control),checks=checks,outcomes=outcomes,
 scope='Native Counter8 after actual Fell431, with identical damage/cost/seed and only paid Exposed grant suppressed in the control. Enemy race/job/gear/reaction are disposable fixture assignments. A positive counter is required.')
(LAB/'retaliation-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
