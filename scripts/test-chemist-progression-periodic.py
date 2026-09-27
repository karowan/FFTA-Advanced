"""Native Wait -> Fuse playback -> next menu on the cold-deployed candidate.

The Fuse, owner, initial HP and formation are declared scenario inputs.
Damage, periodic controller states, KO and turn transitions are native output.
Read-only ARM clones calculate the exact elemental forecast for comparison.
"""
import ast,collections,ctypes as C,hashlib,json,runpy,struct,sys
from pathlib import Path
from native_battle_wrappers import from_emulator
ROOT=Path(__file__).resolve().parents[1]
from chemist_candidate import candidate
meta=candidate()
ROM=Path(meta['path']);image=ROM.read_bytes();assert hashlib.sha1(image).hexdigest()==meta['romSha1']
FIX=ROM.parent/'fixture';OUT=ROM.parent/'periodic';OUT.mkdir(exist_ok=True)
assert json.loads((FIX/'report.json').read_text())['romSha1']==meta['romSha1']
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
menu=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
STACK,RETURN=0x03006800,0x08000100
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<read-only ARM>','exec'))
half=lambda b,p:struct.unpack_from('<H',b,p)[0]
word=lambda b,p:struct.unpack_from('<I',b,p)[0]
checks=collections.Counter();results=[];case=None
def check(n,a,b):checks[n]+=1;assert a==b,(case,n,a,b)
def clone(e):
 m=ARM(image,C.string_at(*e.maps[0x03000000]));m.put(0x02000000,e.memory());return m
def call(m,n,*args):return m.call(meta['symbols'][n],*args,stack=0x03006800)
def active(e):
 r=e.memory();return word(r,word(r,0xf438)-0x02000000+24)
def capture(e,d,n):
 e.save(d/(n+'.state'));e.screenshot(d/(n+'.png'))
 (d/(n+'.ram')).write_bytes(e.memory());(d/(n+'.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
try:
 for hp,condition in ((500,'plain'),(1,'lethal'),(500,'immune'),(500,'trap'),(1,'trap-lethal'),(500,'trap-immune')):
  case=condition;d=OUT/condition;d.mkdir(exist_ok=True);e=E(ROM)
  try:
   e.load(FIX/'battle-ready.state');e.run(1);menu['wait_for_menu'](e)
   actor=active(e)-0x02000000;caster=0x188
   check('different-live-owner',actor!=caster,True)
   wrappers=from_emulator(image,e);w=wrappers[actor]
   r=e.memory();x,y=half(r,w+8)//32,half(r,w+12)//32
   # Keep actual placement. All occupied tiles in the cross, including allies,
   # must resolve in the same delayed burst. Prevent unrelated native Regen.
   for unit in wrappers:
    e.set_memory(unit+0xe8,bytes(8));e.set_memory(unit+0x18,struct.pack('<4H',500,500,100,100))
   e.set_memory(actor+0x18,struct.pack('<H',hp))
   e.set_memory(caster+0x20,struct.pack('<4H',70,40,80,40))
   trap=condition.startswith('trap')
   if condition=='immune':e.set_memory(actor+0x0d,b'\x02')
   if condition=='trap-immune':e.set_memory(actor+0x12,b'\x02')
   m=clone(e);owner=call(m,'ffta_job_origin',0x02000000+caster)
   p=call(m,'ffta_job_state',0x02000000+actor)-0x02000000
   check('valid-Fuse-owner',1<=owner<=36,True)
   if trap:
    check('fixed-Move-origin',(x,y),(0,14))
    e.set_memory(caster+0x29,bytes((e.memory()[actor+0x29]^128,)))
    trap_record=call(m,'ffta_job_state',0x02000000+caster)-0x02000000
    e.set_memory(trap_record+23,bytes((16,0,0|(13<<4))))
   else:e.set_memory(p+23,bytes((64,owner,0,x|(y<<4))))
   m=clone(e);expected={}
   for unit,wrapper in wrappers.items():
    r=e.memory();tx,ty=half(r,wrapper+8)//32,half(r,wrapper+12)//32
    same_height=abs(half(r,w+10)-half(r,wrapper+10))<=32
    if (trap and unit==actor) or (not trap and abs(x-tx)+abs(y-ty)<=1 and same_height):
     if trap:
      m.put(STACK,struct.pack('<II',0,2))
      damage=m.call(meta['symbols']['ffta_integrated_original_exposed_preview'],0x02000000+caster,0x02000000+unit,464,0,stack=STACK)
     else:damage=call(m,'ffta_cp_fuse_damage',0x02000000+caster,0x02000000+unit)
     if damage&0x80000000:damage-=0x100000000
     expected[unit]=max(0,min(500,half(r,unit+0x18)-damage))
   check('carrier-covered',actor in expected,True)
   # Scenario edits above change HP and the trap owner's side after the menu
   # exists. Let native refresh work finish before supplying player input;
   # otherwise its first key sample can occur after a short press is released.
   e.run(60)
   r=e.memory()
   check('setup-refresh-preserves-HP',half(r,actor+0x18),hp)
   if trap:
    check('setup-refresh-preserves-origin',(half(r,w+8)//32,half(r,w+12)//32),(0,14))
    check('setup-refresh-preserves-trap',(r[trap_record+23]>>3)&7,2)
   capture(e,d,'before');previous=active(e)
   for key in ((256,16,256) if trap else (32,32,256,256)):
    e.run(8,key);e.run(180)
   frames=0
   for frames in range(0,9000,10):
    if trap:
     if frames>=1200:break
    elif menu['menu_visible'](e) and active(e)!=previous:break
    e.run(10)
   else:raise AssertionError('Fuse playback did not return to next menu')
   capture(e,d,'after');r=e.memory()
   for unit,want in expected.items():check('native-cross-HP',half(r,unit+0x18),want)
   if trap:
    check('Trap-consumed',(r[trap_record+23]>>3)&7,0)
    check('Move-reached-trap',(half(r,w+8)//32,half(r,w+12)//32),(0,13))
   else:check('Fuse-consumed',r[p+23]>>6,0)
   check('no-additional-MP',half(r,caster+0x1c),100)
   results.append(dict(case=case,actor=actor,expected=expected,frames=frames))
  except BaseException:
   capture(e,d,'failure');raise
  finally:e.close()
 result=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),cases=results)
except BaseException as error:
 result=dict(passed=False,romSha1=meta['romSha1'],checks=dict(checks),case=case,error=repr(error));raise
finally:(OUT/'report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
