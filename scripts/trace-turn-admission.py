"""Deterministic observation of native movement/turn admission; no bonus injection."""
import ast,ctypes as C,hashlib,json,pathlib,runpy,struct,subprocess
from native_battle_wrappers import fixed_giza_formation
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
ROOT=pathlib.Path(__file__).resolve().parents[1]
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<read-only native allowance>','exec'))
allowance_machine=None
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
rom=pathlib.Path(meta['path']);image=rom.read_bytes();out=rom.parent/'turn-admission';out.mkdir(exist_ok=True)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
LOG=0x3f220;events=[];case=None;sequence=0;state_checks=[];cold=[]
original=struct.unpack_from('<I',image,0xa4344)[0]
code=r'''
#include <stdint.h>
static unsigned h(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static void note(unsigned type,unsigned caller,const uint8_t *actor){
 volatile unsigned *log=(volatile unsigned *)0x0203f220u;
 const uint8_t *battle=(const uint8_t *)0x0200f4e8u;
 const uint8_t *w=*(const uint8_t *const *)(battle+4);
 if(!log[1] || !w)return;
 if(!actor)actor=*(const uint8_t *const *)w;
 unsigned n=log[0]++,i=4+(n%16)*7;
 log[i]=type;log[i+1]=caller;log[i+2]=(unsigned)actor;
 log[i+3]=*(const uint8_t *)0x02001f70u|((unsigned)actor[0xeb]<<8)|((unsigned)h(battle+0xdc)<<16);
 const uint8_t *state=((const uint8_t *(*)(const uint8_t *))__STATE__u)(actor);
 log[i+4]=state?(state[12]|((unsigned)state[13]<<8)|((unsigned)state[14]<<16)|((unsigned)state[19]<<24)):0;
 log[i+5]=(h(w+8)>>5)|((h(w+12)>>5)<<16);
 log[i+6]=actor[0xf6]|((unsigned)actor[0xf7]<<16);
}
extern unsigned turn_original_flag(unsigned,unsigned);
unsigned turn_flag(unsigned flag,unsigned value,unsigned caller){
 if(flag==4)note(1|(value<<8),caller,0);
 return turn_original_flag(flag,value);
}
extern unsigned turn_original_execute(uint8_t *,uint8_t *,unsigned,unsigned,unsigned,unsigned,unsigned,unsigned);
unsigned turn_execute(uint8_t *out,uint8_t *wrapper,unsigned x,unsigned y,unsigned action,unsigned item,unsigned mode,unsigned last){
 note(2|(action<<8),0,*(const uint8_t *const *)wrapper);
 return turn_original_execute(out,wrapper,x,y,action,item,mode,last);
}
'''
code=code.replace('__STATE__',str(meta['symbols']['ffta_job_state']|1))
if 'ffta_turn_flag' in meta['symbols']:
 code=code.replace('return turn_original_flag(flag,value);',f"return ((unsigned (*)(unsigned,unsigned,unsigned)){meta['symbols']['ffta_turn_flag']|1}u)(flag,value,caller);")
(out/'trace.c').write_text(code)
(out/'trace.s').write_text(f'''.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global turn_flag_entry
.thumb_func
turn_flag_entry:
 pop {{r3}}
 mov r2,lr
 b turn_flag
.global turn_original_flag
.thumb_func
turn_original_flag:
 push {{lr}}
 lsls r0,r0,#16
 lsls r1,r1,#16
 lsrs r3,r0,#19
 ldr r2,=0x02001f70
 adds r3,r3,r2
 ldr r2,=0x080c9581
 bx r2
.align 2
.global turn_execute_entry
.thumb_func
turn_execute_entry:
 pop {{r3}}
 b turn_execute
.global turn_original_execute
.thumb_func
turn_original_execute:
 push {{r3}}
 ldr r3,={original}
 bx r3
.ltorg
''')
(out/'trace.ld').write_text('SECTIONS { . = 0x093f0000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.comment) *(.ARM.attributes) } }')
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-ffreestanding','-fno-builtin','-nostdlib','-Wall','-Wextra','-Werror',
 '-Wl,-T,'+str(out/'trace.ld'),str(out/'trace.s'),str(out/'trace.c'),'-o',str(out/'trace.elf')],check=True)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(out/'trace.elf'),str(out/'trace.bin')],check=True)
symbols={p[2]:int(p[0],16) for l in subprocess.check_output([prefix+'nm.exe','-n',str(out/'trace.elf')],text=True).splitlines() if len(p:=l.split())==3}
code=(out/'trace.bin').read_bytes();assert image[0x13f0000:0x13f0000+len(code)]==b'\xff'*len(code)
patched=bytearray(image);patched[0x13f0000:0x13f0000+len(code)]=code
# Diagnostic observes calls and delegates every flag operation to the exact
# production consumer. The logger does not write any owned movement state.
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
assert clean[0xc9574:0xc9580]==bytes.fromhex('00b500040904c30c094a9b18')
assert struct.unpack_from('<I',image,0xc957c)[0]==meta['symbols']['ffta_turn_flag_entry']|1
patched[0xc9574:0xc9580]=bytes.fromhex('08b4c046004b1847')+struct.pack('<I',symbols['turn_flag_entry']|1)
struct.pack_into('<I',patched,0xa4344,symbols['turn_execute_entry']|1)
test=out/'trace.gba';test.write_bytes(patched)
word=lambda r,p:struct.unpack_from('<I',r,p)[0]
def active(e):
 r=e.memory();p=word(r,0xf438)-0x02000000
 return word(r,p+24) if 0<=p<len(r)-28 else 0
def collect(e):
 global sequence
 r=e.memory();n=word(r,LOG)
 assert sequence<=n<=sequence+16,('trace ring overflow',case,sequence,n)
 for i in range(sequence,n):events.append(dict(case=case,sequence=i,record=list(struct.unpack_from('<7I',r,LOG+16+(i%16)*28))))
 sequence=n
 assert r[0x3f3f0:0x3f400]==b'\xd7'*16
def run(e,frames,key=0):
 for n in range(0,frames,10):e.run(min(10,frames-n),key);collect(e)
def tap(e,key,wait=180):run(e,8,key);run(e,wait)
def menu(e,previous=None):
 for n in range(900):
  if observe['menu_visible'](e) and (previous is None or active(e)!=previous):return
  run(e,10)
 raise AssertionError(('menu timeout',case,hex(active(e))))
def state_check(e,unit,expected,label):
 global allowance_machine
 r=e.memory();p=0x3f410+(unit-0x80)//264*22;s=r[p:p+22]
 actual=[s[12],s[13],s[14]&7]
 # Read the ordinary native getter on a clone, never write the live turn.
 # This oracle is independent of the new packed allowance getters.
 if allowance_machine is None:allowance_machine=ARM(image,C.string_at(*e.maps[0x03000000]))
 allowance_machine.put(0x02000000,r);allowance_machine.put(0x03000000,C.string_at(*e.maps[0x03000000]))
 native=allowance_machine.call(0x080ca394,0x02000000+unit)
 original=(s[14]>>3)|(((s[19]>>3)&3)<<5);remaining=(s[19]>>5)&3
 used=2 if case[0]=='move-two' else 1
 budget=min(2,max(0,native-used)) if label=='native-movement-completed' else min(2,native)
 if expected==[0,0,0]:assert s[19]&248==0,(case,label,'ledger not cleared',s.hex())
 else:
  assert s[19]&128 and original==native,(case,label,'original allowance',original,native,s.hex())
  assert remaining==budget,(case,label,'remaining budget',remaining,budget,s.hex())
 state_checks.append(dict(case=case,label=label,actual=actual,expected=expected,original=original,native=native,remaining=remaining));assert actual==expected,(case,label,actual,expected)
for route,race in [('wait-AI',1)]+[(route,race) for race in (1,2) for route in ('move-one','move-two','cancel')]:
 e=E(test);sequence=0
 try:
  e.load(rom.parent/'fixture/battle-ready.state');e.set_memory(LOG,bytes(464)+b'\xd7'*16);e.set_memory(LOG+4,struct.pack('<I',1));fixed_giza_formation(image,e)
  if race==2:
   from native_battle_wrappers import from_emulator
   w=from_emulator(image,e);e.set_memory(0x290+0xf6,bytes((0,13)));e.set_memory(w[0x290]+8,struct.pack('<3H',16,32,13*32+16))
  for turn in range(16 if route=='wait-AI' else 4 if race==1 else 0):
   case=(route,race,'wait',turn);menu(e);previous=active(e)
   for key in (32,32,256,256):tap(e,key)
   menu(e,previous)
  if route!='wait-AI':
   unit=0x80 if race==1 else 0x398;origin=[2,13] if race==1 else [1,14]
   assert active(e)==0x02000000+unit
   state_check(e,unit,origin+[1],'native-turn-start')
   case=(route,race,'move');tap(e,256);tap(e,16)
   if route=='move-two':tap(e,16)
   tap(e,256,900);menu(e)
   state_check(e,unit,origin+[7 if route=='move-two' else 3],'native-movement-completed')
   if route=='cancel':
    case=(route,race,'cancel');tap(e,1);tap(e,1);menu(e);state_check(e,unit,origin+[1],'native-undo')
   e.screenshot(out/(route+str(race)+'.png'));(out/(route+str(race)+'.ram')).write_bytes(e.memory())
   if route=='cancel':e.save(out/('cancel'+str(race)+'.state'))
   case=(route,race,'end');previous=active(e)
   for key in (32,256,256):tap(e,key)
   menu(e,previous)
   state_check(e,unit,[0,0,0],'native-turn-end')
 finally:
  (out/'partial.json').write_text(json.dumps(dict(events=events,stateChecks=state_checks),indent=2));e.close()
assert any(e['record'][0]&255==2 and e['record'][2]>=0x02002fc4 for e in events),'no actual AI action observed'
ai=[e['record'] for e in events if e['record'][0]&255==2 and e['record'][2]>=0x02002fc4]
assert all(r[4]>>16&1 for r in ai),('AI action lacks active turn',ai)
assert any((r[4]>>16)&7==7 for r in ai),('No native AI moved action',ai)
assert any((r[4]>>16)&7==1 for r in ai),('No native AI stationary action',ai)
# A native suspend is available after returning to the free cursor, which
# cancels an uncommitted Move. Save the actual undo result and cold-load it in
# the uninstrumented ROM; never repair flash or the resumed record.
def plain_tap(e,key,wait=180):e.run(8,key);e.run(wait)
for race,unit,origin in ((1,0x80,[2,13]),(2,0x398,[1,14])):
 case=('cold',race);e=E(rom)
 try:
  e.load(out/('cancel'+str(race)+'.state'));expected=e.memory()
  for key in (1,8,16,256,256):plain_tap(e,key)
  old=e.memory(0);plain_tap(e,256,300);saved=e.memory(0)
  assert saved!=old,('native suspend unchanged',case)
  (out/('cancel'+str(race)+'.sav')).write_bytes(saved)
 finally:e.close()
 e=E(rom)
 try:
  e.set_memory(0,saved,0);e.run(3600)
  for key,wait in ((8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)):plain_tap(e,key,wait)
  observe['wait_for_menu'](e);actual=e.memory()
  state_check(e,unit,origin+[1],'cold-native-undo-state')
  assert actual[unit+0x18:unit+0x20]==expected[unit+0x18:unit+0x20]
  assert actual[0x1940:0x1e70]==expected[0x1940:0x1e70]
  assert actual[0x3ff44:0x3ff4c]==bytes(8)
  e.screenshot(out/('cold'+str(race)+'.png'))
  cold.append(dict(race=race,saveSha1=hashlib.sha1(saved).hexdigest(),state=origin+[1]))
 finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],events=events,stateChecks=state_checks,cold=cold,fields=['type+value/action','caller','actor','native flags+statusEB+interpreter','owned originX+originY+packedMovement14+packedMovement19','wrapperXY','unitXY'],scope=__doc__)
(out/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
