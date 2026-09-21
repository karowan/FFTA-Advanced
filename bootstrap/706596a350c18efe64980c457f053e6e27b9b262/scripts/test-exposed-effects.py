"""Isolated native lifecycle hooks; Fell Cleave remains disabled."""
import argparse,ast,hashlib,json,pathlib,struct,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
sha=lambda b:hashlib.sha1(b).hexdigest()
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--snapshot',type=pathlib.Path);p.add_argument('--incoming',action='store_true');args=p.parse_args()
if args.snapshot:
 base=(args.snapshot/'frozen.gba').read_bytes();meta=json.loads((args.snapshot/'manifest.json').read_text())
 engine=(args.snapshot/'engine.bin').read_bytes();symbol_text=(args.snapshot/'engine.symbols').read_bytes()
else:
 base=(ROOT/'build/expansion/probes/combat.gba').read_bytes();meta=json.loads((ROOT/'build/expansion/probes/combat.json').read_text())
 engine=(ROOT/'build/expansion/engine.bin').read_bytes();symbol_text=(ROOT/'build/expansion/engine.symbols').read_bytes()
assert sha(base)==meta['romSha1'] and sha(engine)==meta['engineSha1']
assert base[0x1100000:0x1100000+len(engine)]==engine
OUT=ROOT/'build/expansion/probes/exposed-effects'/sha(base);OUT.mkdir(parents=True,exist_ok=True)
for name,data in [('frozen.gba',base),('engine.bin',engine),('engine.symbols',symbol_text)]: (OUT/name).write_bytes(data)
(OUT/'manifest.json').write_text(json.dumps(meta,indent=2))
oldsymbols={p[2]:int(p[0],16) for l in symbol_text.decode().splitlines() if len(p:=l.split())==3}
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
(OUT/'owner-import.s').write_text('.syntax unified\n.cpu arm7tdmi\n.thumb\n.global ffta_owned_exposed\n.thumb_func\nffta_owned_exposed:\n ldr r3,='+str(oldsymbols['ffta_owned_exposed']|1)+'\n bx r3\n.ltorg\n')
subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-Wl,-Ttext=0x091d0000','-Wl,-e,ffta_exposed_clear',str(OUT/'owner-import.s'),str(ROOT/'src/engine/exposed-effects.c'),str(ROOT/'src/engine/exposed-effects.s'),'-lgcc','-o',str(OUT/'isolated.elf')],check=True)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(OUT/'isolated.elf'),str(OUT/'isolated.bin')],check=True)
symbols={p[2]:int(p[0],16) for l in subprocess.check_output([prefix+'nm.exe','-n',str(OUT/'isolated.elf')],text=True).splitlines() if len(p:=l.split())==3}
image=bytearray(base);binary=(OUT/'isolated.bin').read_bytes()
assert image[0x11d0000:0x11d0000+len(binary)]==b'\xff'*len(binary),'Private code allocation overlaps existing ROM'
image[0x11d0000:0x11d0000+len(binary)]=binary
(OUT/'input.gba').write_bytes(image);(OUT/'symbols.json').write_text(json.dumps(symbols))
js="import fs from 'node:fs';import{patchExposedEffects}from'./scripts/patch-exposed-effects.mjs';const p=process.argv[1],b=fs.readFileSync(p+'/input.gba'),s=JSON.parse(fs.readFileSync(p+'/symbols.json'));patchExposedEffects(b,s,{application:true,incoming:"+str(args.incoming).lower()+"});fs.writeFileSync(p+'/isolated.gba',b);"
subprocess.run(['node','--input-type=module','-e',js,str(OUT)],cwd=ROOT,check=True)
image=(OUT/'isolated.gba').read_bytes()
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
fix=ROOT/'build/expansion/probes/exposed-storage/current'/sha(base)/'battle'
assert sha((fix/'frozen.gba').read_bytes())==sha(base)
ram=(fix/'battle-ready.ram').read_bytes();iw=(fix/'battle-ready.iwram').read_bytes()
native,expanded=ARM(base,iw),ARM(image,iw);checks=0
def same(fn,args,unit,clears,stack):
 global checks
 offset=(unit-0x02000080)//264 if 0x02000080<=unit<0x02001940 else 24+(unit-0x02002fc4)//264
 for m in (native,expanded):m.put(0x02000000,ram);m.put(0x02001e98,bytes([1])*36)
 result=[m.call(fn,*args,stack=stack) for m in (native,expanded)]
 expected=bytearray(native.read(0x02000000,0x40000))
 if clears:expected[0x1e98+offset]=0
 assert expanded.read(0x02000000,0x40000)==expected,(hex(fn),args,clears)
 assert result[0]==result[1],('result',hex(fn),result)
 checks+=2
units=[0x02000080+264*i for i in range(24)]+[0x02002fc4+264*i for i in range(12)]
for stack in (STACK,STACK+4):
 for unit in units:
  same(0x08097298,(unit,),unit,True,stack)
  for value in (0,1,0x100,0x101,0xffffffff):same(0x080cddd0,(unit,value),unit,bool(value&255),stack)
  for status in range(44):
   for value in (0,1):same(0x080cd884,(unit,status,value),unit,status==6 and value,stack)
 # Complete native wrapper death cleanup, including its linked-status scans.
 for wrapper,unit in ((0x02022634,0x020033e4),(0x020226c4,UNIT),(0x02022874,0x02000398)):
  assert struct.unpack_from('<I',ram,wrapper-0x02000000)[0]==unit
  same(0x08099bac,(wrapper,),unit,True,stack)
 # Native complete job change, valid Human canonical input, original/new/same.
 for unit in (UNIT,0x02000398):
  for job in (ram[unit-0x02000000+7],2,3,10,116):
   same(0x080c8c24,(unit,job),unit,job!=ram[unit-0x02000000+7],stack)
 for query in (0,0x10,0x80,0x90):
  for m in (native,expanded):
   m.put(0x02000000,ram);m.put(0x02001e98,bytes([1])*36);m.put(0x0200f3f0+8,struct.pack('<I',UNIT));m.put(0x0200f3f0+0x26,struct.pack('<H',query))
  a=native.call(0x0813353c,0x0200f3f0,stack=stack);b=expanded.call(symbols['ffta_exposed_cureall_entry'],0x0200f3f0,stack=stack)
  wanted=bytearray(native.read(0x02000000,0x40000));wanted[0x1e98]=1 if query&0x10 else 0
  assert a==b and expanded.read(0x02000000,0x40000)==wanted;checks+=2
# Full native Cureall effect dispatcher: its original native cure masks remain
# the oracle, including no-native-ailment and all44 individual status bits.
for stack in (STACK,STACK+4):
 for status in range(-1,44):
  for query in (0,0x10):
   for m in (native,expanded):
    m.put(0x02000000,ram);m.put(0x02001e98,bytes([1])*36)
    m.put(UNIT+0xe8,struct.pack('<Q',0 if status<0 else 1<<status))
    context=bytearray(0x34)
    struct.pack_into('<IIIHH',context,0,0x02000398,0,UNIT,264,0)
    struct.pack_into('<H',context,0x26,query)
    struct.pack_into('<I',context,0x30,0x08553e70+0x8b*4)
    m.put(0x0200f3f0,context)
   allowed=native.call(0x08133a58,UNIT,79)
   # This readonly native query restores the original status words.
   results=[m.call(0x0813388c,stack=stack) for m in (native,expanded)]
   expected=bytearray(native.read(0x02000000,0x40000))
   if allowed and not query:expected[0x1e98]=0
   assert expanded.read(0x02000000,0x40000)==expected,('Cureall dispatcher',status,query)
   assert results[0]==results[1];checks+=2
# Native event-script KO writes HP/MP zero directly and bypasses97298.
# Its status0 opcode clears Exposed regardless of the already-handled value.
for stack in (STACK,STACK+4):
 for status in range(44):
  outputs=[]
  for rom in (base,image):
   m=ARM(rom,iw);m.put(0x02000000,ram);m.put(0x02001e98,bytes([1])*36)
   m.put(0x02008000,bytes([0,0,status,1]));m.put(0x02008010,struct.pack('<I',UNIT))
   for i,reg in enumerate(range(UC_ARM_REG_R0,UC_ARM_REG_R12+1)):m.u.reg_write(reg,0x55000000+i)
   m.u.reg_write(UC_ARM_REG_R4,0x02008000);m.u.reg_write(UC_ARM_REG_R5,0x02008010)
   m.u.reg_write(UC_ARM_REG_SP,stack);m.u.reg_write(UC_ARM_REG_LR,RETURN|1)
   m.u.emu_start(0x081230f3,0x08123104,count=50000)
   assert m.u.reg_read(UC_ARM_REG_PC)==0x08123104
   outputs.append((m.read(0x02000000,0x40000),[m.u.reg_read(reg) for reg in range(UC_ARM_REG_R0,UC_ARM_REG_R12+1)]+[m.u.reg_read(UC_ARM_REG_SP),m.u.reg_read(UC_ARM_REG_CPSR)]))
  expected=bytearray(outputs[0][0])
  if status==0:expected[0x1e98]=0
  assert outputs[1][0]==expected and outputs[0][1]==outputs[1][1],('event KO',status,stack);checks+=2
# Battle-end block through its next native call, including status-flag read.
# All36 owned state bytes clear; native party refresh remains byte-identical.
for stack in (STACK,STACK+4):
 outputs=[]
 for rom in (base,image):
  m=ARM(rom,iw);m.put(0x02000000,ram);m.put(0x02001e98,bytes([1])*36)
  for i,reg in enumerate(range(UC_ARM_REG_R0,UC_ARM_REG_R12+1)):m.u.reg_write(reg,0x55000000+i)
  m.u.reg_write(UC_ARM_REG_SP,stack);m.u.reg_write(UC_ARM_REG_LR,RETURN|1)
  m.u.emu_start(0x08095215,0x0809522a,count=50000)
  assert m.u.reg_read(UC_ARM_REG_PC)==0x0809522a
  outputs.append((m.read(0x02000000,0x40000),[m.u.reg_read(reg) for reg in range(UC_ARM_REG_R0,UC_ARM_REG_R12+1)]+[m.u.reg_read(UC_ARM_REG_SP),m.u.reg_read(UC_ARM_REG_CPSR)]))
 expected=bytearray(outputs[0][0]);expected[0x1e98:0x1ebc]=bytes(36)
 assert outputs[1][0]==expected and outputs[0][1]==outputs[1][1],('battle end',stack);checks+=2
# Exact captured next-turn scheduler frame; native block stops before its next BL.
capture=ROOT/'build/expansion/probes/exposed-events'/sha(base)
regs=struct.unpack_from('<17I',(capture/'own-turn.state').read_bytes(),0x20)
turnram=(capture/'own-turn.ram').read_bytes();turniw=(capture/'own-turn.iwram').read_bytes()
for residue in (0,4):
 results=[]
 for rom in (base,image):
  m=ARM(rom,turniw);m.put(0x02000000,turnram);m.put(0x02001e98,bytes([1])*36)
  m.u.reg_write(UC_ARM_REG_CPSR,regs[16])
  for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12,UC_ARM_REG_SP,UC_ARM_REG_LR],regs[:15]):m.u.reg_write(reg,value)
  m.u.reg_write(UC_ARM_REG_SP,regs[13]+residue);m.u.reg_write(UC_ARM_REG_CPSR,regs[16])
  m.u.emu_start(0x08093023,0x0809302e,count=50000)
  assert m.u.reg_read(UC_ARM_REG_PC)==0x0809302e
  results.append((m.read(0x02000000,0x40000),[m.u.reg_read(reg) for reg in range(UC_ARM_REG_R0,UC_ARM_REG_R12+1)]+[m.u.reg_read(UC_ARM_REG_SP),m.u.reg_read(UC_ARM_REG_CPSR)]))
 expected=bytearray(results[0][0]);expected[0x1e98+5]=0
 assert results[1][0]==expected and results[0][1]==results[1][1],('turn',residue);checks+=2
# Native assigned-support getter independently establishes Immunity11.
for stack in (STACK,STACK+4):
 for support in (0,115):
  for active in (0,1,0x0a,0x0b,0xfe,0xff):
   expanded.put(0x02000000,ram);expanded.put(UNIT+0x3b,bytes([support]));expanded.put(0x02001e98,bytes([active]))
   assert expanded.call(0x080cd50c,UNIT)==(11 if support else 0)
   before=expanded.read(0x02000000,0x40000)
   assert expanded.call(symbols['ffta_exposed_can_apply'],UNIT,stack=stack)==(0 if support else 1)
   assert before==expanded.read(0x02000000,0x40000);checks+=2
   for action in (0,1,347,423,430,431,65535):
    expanded.put(0x02000000,before)
    assert expanded.call(symbols['ffta_exposed_paid_commit'],UNIT,action,stack=stack)==(0 if action==431 and support else 1)
    wanted=bytearray(before)
    if action==431 and not support:wanted[0x1e98]=active|1
    assert expanded.read(0x02000000,0x40000)==wanted;checks+=2
# Full captured MP-payment block, including native insufficient-policy branch.
pregs=struct.unpack_from('<17I',(capture/'payment.state').read_bytes(),0x20)
pram=(capture/'payment.ram').read_bytes();piw=(capture/'payment.iwram').read_bytes()
for residue in (0,4):
 for action in list(range(347))+[430,431]:
  for immunity in (0,1):
   outputs=[]
   for rom in (base,image):
    m=ARM(rom,piw);m.put(0x02000000,pram);m.put(0x0200039e,b'\x01');m.put(0x020003d3,bytes([115 if immunity else 0]));m.put(0x02001e98,bytes(36))
    # Move the complete captured caller frame for the alternate ABI residue.
    sp=pregs[13]+residue;m.put(sp,piw[pregs[13]-0x03000000:pregs[13]-0x03000000+0x100]);m.put(sp+0x4c,struct.pack('<I',action))
    m.u.reg_write(UC_ARM_REG_CPSR,pregs[16])
    for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12,UC_ARM_REG_SP,UC_ARM_REG_LR],pregs[:15]):m.u.reg_write(reg,value)
    m.u.reg_write(UC_ARM_REG_SP,sp)
    # Captured frame begins after subtraction. Reconstruct its verified
    # pre-subtraction operands for the relocated hook, preserving Fight bypass.
    mp=struct.unpack_from('<H',pram,0x398+0x1c)[0]
    m.u.reg_write(UC_ARM_REG_R0,mp)
    m.u.reg_write(UC_ARM_REG_R4,mp-pregs[4])
    def stop(u,pc,size,_):
     if pc in (0x080a45da,0x080a4968):u.emu_stop()
    m.u.hook_add(UC_HOOK_CODE,stop)
    m.u.emu_start(0x080a45c7,RETURN,count=50000)
    outputs.append((m.u.reg_read(UC_ARM_REG_PC),m.read(0x02000000,0x40000),[m.u.reg_read(reg) for reg in range(UC_ARM_REG_R0,UC_ARM_REG_R12+1)]+[m.u.reg_read(UC_ARM_REG_SP)]))
   blocked=action==431 and immunity
   expected=bytearray(outputs[0][1])
   if blocked:expected[0x398+0x1c:0x398+0x1e]=pram[0x398+0x1c:0x398+0x1e]
   elif action==431:expected[0x1e98+3]=1
   assert outputs[1][0]==(0x080a4968 if blocked else 0x080a45da),(action,immunity,residue,hex(outputs[1][0]))
   assert outputs[1][1]==expected,(action,immunity,residue)
   if not blocked:assert outputs[0][2]==outputs[1][2],('paid registers',action,immunity)
   checks+=3
report={'passed':True,'checks':checks,'baseSha1':sha(base),'romSha1':sha(image),'engineSha1':sha(engine),'incomingHooks':args.incoming,'scope':'Isolated lifecycle plus paid-commit gate. Production431 remains disabled; incoming acceptance is separate.'}
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
