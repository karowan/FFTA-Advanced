"""Native presentation hook ABI versus original instructions; no game inputs."""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-mystic-knight-commands.py';ns={'__file__':str(source),'__name__':'visual_fixture'}
exec(compile(source.read_text().split('# Native casts cover')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,STACK,fixture,call=(ns[k] for k in ('m','S','meta','OUT','A','STACK','fixture','call'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
checks=collections.Counter();case=None
def check(k,a,b):checks[k]+=1;assert a==b,(k,case,a,b)
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
image=pathlib.Path(meta['path']).read_bytes()
sites=[(0xa6238,0xa624c,'category'),(0xa6412,0xa6420,'direction'),
       (0xa6424,0xa6434,'projectile'),(0xa662c,0xa6638,'actor'),
       (0xa5730,0xa573c,'impact'),(0xa588c,0xa58a0,'sound'),(0xddfce,0xddfe0,'magic_actor')]
registers=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,
 UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,
 UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
result,wrapper=0x02028000,0x02028400
for action,item in itertools.product((0,23,148,180,265,401,410,421,422,423),(0,7,8,21,88)):
 fixture(410);m.put(A+0x2a,struct.pack('<5H',88,0,0,0,0))
 m.put(wrapper,struct.pack('<I',A));m.put(result,struct.pack('<I',wrapper)+bytes(0x2c0))
 m.put(result+0x10,struct.pack('<HH',action,item))
 before=m.read(result,0x2c4)
 check('item-accessor',call('ffta_myk_visual_item',result),88 if action==421 else item)
 check('choice-accessor-read-only',m.read(result,0x2c4),before)
for start,end,name in sites:
 for action,operand,alignment,style in itertools.product((180,410,421),(0,7,8,21,88),(0,4),(0,3)):
  case=(name,action,operand,alignment,style);fixture(410)
  m.put(A+0x2a,struct.pack('<5H',88,0,0,0,0));m.put(wrapper,struct.pack('<I',A))
  data=bytearray(0x2c4);struct.pack_into('<I',data,0,wrapper)
  data[8]=255;data[9]=style;struct.pack_into('<HH',data,0x10,action,operand)
  outputs=[]
  for patched in (False,True):
   m.put(0x08000000+start,image[start:end] if patched else clean[start:end])
   m.u.ctl_remove_cache(0x08000000+start,0x08000000+end)
   control=bytearray(data)
   if not patched and action==421:struct.pack_into('<H',control,0x12,88)
   m.put(result,control);m.put(STACK-512,b'\xd7'*1024)
   m.u.reg_write(UC_ARM_REG_CPSR,0x2000003f)
   for i,r in enumerate(registers):m.u.reg_write(r,0x33000000+i)
   m.u.reg_write(UC_ARM_REG_R5,result if name in ('impact','sound') else wrapper)
   m.u.reg_write(UC_ARM_REG_R7,result)
   if name=='magic_actor':
    m.u.reg_write(UC_ARM_REG_R4,result);m.u.reg_write(UC_ARM_REG_R5,5);m.u.reg_write(UC_ARM_REG_R7,STACK+alignment+8)
   m.u.reg_write(UC_ARM_REG_SP,STACK+alignment)
   m.u.reg_write(UC_ARM_REG_LR,0x08000101)
   calls=[];align=[];helper_return=[None]
   def observer(u,p,size,user):
    if p==0x08000000+end:u.emu_stop();return
    if p==helper_return[0]:helper_return[0]=None
    if p==S['ffta_myk_visual_item']&~1:
     align.append(u.reg_read(UC_ARM_REG_SP)%8);helper_return[0]=u.reg_read(UC_ARM_REG_LR)&~1
    if p in (0x080ca7a4,0x0812eed0,0x0812ee98,0x0809836c):
     args=[u.reg_read(r) for r in registers[:4]]
     # Item-table reads inside primary-weapon lookup must execute normally.
     if helper_return[0] is not None:return
     calls.append((p,args[:4 if p==0x0809836c else 2]))
     for r,v in zip(registers[:4],(7,0x123,0x456,0x789)):u.reg_write(r,v)
     u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   handle=m.u.hook_add(UC_HOOK_CODE,observer)
   # Unicorn caches translated blocks before a later tracing hook is added.
   m.u.ctl_flush_tb()
   try:m.u.emu_start((0x08000000+start)|1,0,count=100000)
   finally:m.u.hook_del(handle)
   check('reaches-continuation',m.u.reg_read(UC_ARM_REG_PC),0x08000000+end)
   check('header-not-written',m.read(result,0x2c4),bytes(control))
   check('caller-stack-balanced',m.u.reg_read(UC_ARM_REG_SP),STACK+alignment)
   if patched:
    check('C-helper-aligned',align,[0,0] if name=='magic_actor' else [0])
   outputs.append((calls,[m.u.reg_read(r) for r in registers],m.read(STACK+alignment,32)))
  check('original-ABI-and-native-inputs',outputs[1],outputs[0])
  m.put(0x08000000+start,image[start:end]);m.u.ctl_remove_cache(0x08000000+start,0x08000000+end)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),
 limits=['Native graphic calls are observed ABI boundaries; actual rendering is tested by fixed mGBA playback.'])
(OUT/'mystic-knight-visual.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
