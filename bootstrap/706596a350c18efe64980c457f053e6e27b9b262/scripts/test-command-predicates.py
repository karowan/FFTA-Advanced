"""Council differential tests of command membership and four native predicates.
External battle restriction/status/selector callbacks are controlled fixtures;
range resolution, AP availability, native predicate bodies and replacements run.
"""
import ast,ctypes as C,hashlib,importlib.util,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
source=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')],type_ignores=[]),'<harness>','exec'))
out=ROOT/'build/expansion/probes';rom=(out/'command-core.gba').read_bytes();meta=json.loads((out/'command-core.json').read_text());base=(out/'command-data.gba').read_bytes();engine=(ROOT/'build/expansion/engine.bin').read_bytes();symbol_bytes=(ROOT/'build/expansion/engine.symbols').read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1'];assert hashlib.sha1(base).hexdigest()==meta['baseSha1'];assert hashlib.sha1(engine).hexdigest()==meta['engineSha1'];assert rom[0x1100000:0x1100000+len(engine)]==engine
symbols={p[2]:int(p[0],16) for line in symbol_bytes.decode().splitlines() if len(p:=line.split())==3}
frozen=out/'command-predicate-council'/meta['romSha1'];frozen.mkdir(parents=True,exist_ok=True)
for name,data in [('command-core.gba',rom),('command-core.json',json.dumps(meta).encode()),('engine.symbols',symbol_bytes)]: (frozen/name).write_bytes(data)
iwram=iwram_from_boot();native=ARM(base,iwram);m=ARM(rom,iwram);checks={};aligned=[]
for name in ('ffta_battle_command','ffta_special_action','ffta_action_command','ffta_action21'):
 m.u.hook_add(UC_HOOK_CODE,lambda u,a,s,d:aligned.append(u.reg_read(UC_ARM_REG_SP)),begin=symbols[name],end=symbols[name])
old=[0,142,77,95,85,88];new=[0,178,111,124,118,116];starters=[0,2,16,22,30,37]

def check(group,condition,label):
 assert condition,f'{group}: {label}'
 checks[group]=checks.get(group,0)+1

def callback(machine):
 def intercept(u,address,size,data):
  if address==0x080970e8:result=machine.restricted
  elif address==0x08096d7c:result=0x02018000
  elif address==0x080c8298:result=machine.blocked
  elif address==0x080ccd50:
   action=u.reg_read(UC_ARM_REG_R0)&65535;selector=u.reg_read(UC_ARM_REG_R1)&255
   assert selector in (0x13,0x15),(hex(address),selector)
   result=(action%3==0) if selector==0x13 else (action&1)
  else:raise AssertionError(hex(address))
  u.reg_write(UC_ARM_REG_R0,int(result));u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 for address in (0x080970e8,0x08096d7c,0x080c8298,0x080ccd50):machine.u.hook_add(UC_HOOK_CODE,intercept,begin=address,end=address)
for machine in (native,m):callback(machine)
jobtable=m.word(0x080c8598)

def fixture(machine,job,pattern,primary_command=None,secondary_command=None,secondary=None):
 machine.put(0x02000000,bytes(0x40000));machine.put(0x02001e70,b'FFTAEXP1\x01')
 machine.put(0x0200f438,struct.pack('<I',0x02018000));machine.put(0x02018018,struct.pack('<I',UNIT))
 race=machine.read(jobtable+job*52+4,1)[0];fallback=starters[race] if 0<race<6 else job
 data=bytearray(264);data[4]=1;data[5]=job;data[6]=race;data[7]=fallback;data[8]=secondary if secondary is not None else fallback
 command=machine.call(0x080c8570,job,fallback,0x0c)
 data[0x35]=command if primary_command is None else primary_command
 data[0x36]=0 if secondary_command is None else secondary_command;data[0x37]=1
 count=new[race] if 0<race<6 else machine.call(0x080c9ed8,race);data[0x34]=count
 native_count=old[race] if 0<race<6 else count
 for i in range(1,native_count):data[0x40+i]=(0 if pattern==0 else 37 if pattern==1 else 0x80 if pattern==2 else (0xe4 if i%2 else 0x33))
 machine.put(UNIT,data);machine.restricted=0;machine.blocked=0
 return race,fallback

# All original jobs, both branches, no added AP: selective wrappers retain native results.
for job in range(116):
 race=m.read(jobtable+job*52+4,1)[0]
 if not 0<race<6:continue # Non-playable aliases are tested below only with valid fallbacks.
 for pattern in range(4):
  for machine in (native,m):fixture(machine,job,pattern)
  for restricted in (0,1):
   m.restricted=native.restricted=restricted
   for selection in (6,7):check('original',m.call(0x08025fdc,selection)==native.call(0x08025fdc,selection),f'job{job} pattern{pattern} restricted{restricted} selection{selection}')
  check('original',m.call(0x08026ab8)==native.call(0x08026ab8),f'special job{job} pattern{pattern}')
  for blocked in (0,1):
   m.blocked=native.blocked=blocked
   check('original',m.call(0x081341ec,UNIT)==native.call(0x081341ec,UNIT),f'action21 job{job} blocked{blocked}')
  for action in (0,1,0x21,0x32,0xffff):check('original',m.call(0x08133d78,UNIT,action)==native.call(0x08133d78,UNIT,action),f'reverse job{job} action{action}')
# Custom jobs: original-only AP with inactive/Item/other secondary combinations.
for job in (2,16):
 for commands in ((0,0),(0,2),(1,2),(2,1),(2,0),(2,2)):
  for machine in (native,m):fixture(machine,job,3,commands[0],commands[1],job)
  for selection in (6,7):check('zero_item',m.call(0x08025fdc,selection)==native.call(0x08025fdc,selection),str((job,commands,selection)))
  check('zero_item',m.call(0x08026ab8)==native.call(0x08026ab8),str((job,commands)))
  check('zero_item',m.call(0x081341ec,UNIT)==native.call(0x081341ec,UNIT),str((job,commands)))
  for action in range(0,256):check('zero_item',m.call(0x08133d78,UNIT,action)==native.call(0x08133d78,UNIT,action),str((job,commands,action)))
# Explicit added-only lessons: control record type/action and AP flags independently.
for job,first,last in ((2,172,177),(16,105,110)):
 for slot in (1,2):
  for lesson in range(first,last+1):
   for typ in (0,1,2,3,4):
    for ap in (0,37,0x80,0xe4):
     fixture(m,job,0,2 if slot==1 else 0,2 if slot==2 else 0,job)
     race=m.read(UNIT+6,1)[0];bank=m.word(m.word(0x080ccf40)+4*race);address=bank+8*lesson;saved=m.read(address,8)
     # Action33 has both the synthetic special/restricted properties and is exact21hex.
     record=bytearray(saved);struct.pack_into('<H',record,4,0x21);record[6]=typ;m.put(address,record)
     ap_address=0x02001b40+lesson-144 if race==1 else UNIT+0x40+lesson;m.put(ap_address,[ap])
     eligible=typ in (1,4);available=bool(ap&128)
     for restricted in (0,1):
      m.restricted=restricted
      check('added',m.call(0x08025fdc,slot+5)==int(eligible and available),'battle added-only')
     check('added',m.call(0x08026ab8)==int(eligible and available),'special added-only')
     check('added',m.call(0x08133d78,UNIT,0x21)==(2 if eligible else 0),'reverse must ignore AP')
     for blocked in (0,1):
      m.blocked=blocked
      check('added',m.call(0x081341ec,UNIT)==int(eligible and available and not blocked),'action21 status')
     for action in (0x20,0x22,0x24):
      struct.pack_into('<H',record,4,action);m.put(address,record)
      m.restricted=1;m.blocked=0
      check('selector',m.call(0x08025fdc,slot+5)==int(eligible and available and bool(action&1)),'restricted selector denial')
      check('selector',m.call(0x08026ab8)==int(eligible and available and action%3==0),'special selector decision')
      check('selector',m.call(0x081341ec,UNIT)==0,'other action is not21')
     m.put(address,saved)
# Stateless successor interleaving: two unit/job contexts and three slots.
fixture(m,2,0,2,2,2);other=UNIT+264;unit=bytearray(m.read(UNIT,264));unit[5]=unit[7]=unit[8]=16;unit[6]=2;m.put(other,unit)
for pointer,expected in ((UNIT,list(range(1,12))+list(range(172,178))),(other,list(range(33,44))+list(range(105,111)))):
 for slot in (1,2):
  current=0;seen=[]
  for _ in range(18):
   value=m.call(symbols['ffta_command_successor'],pointer,slot,current)
   # Intervening scan for another unit must not change this one's cursor.
   m.call(symbols['ffta_command_successor'],other if pointer==UNIT else UNIT,1,40)
   if value==0x1ffff:break
   check('successor',value&0x10000 and (value&65535)>current,'successor marker/order')
   current=value&65535;seen.append(current)
  check('successor',seen==expected,'exact disjoint membership')
check('successor',m.call(symbols['ffta_command_successor'],UNIT,3,0)==0,'Item successor stays native')
for stack in (STACK,STACK-4):
 for job in (2,3,16,80):
  for machine in (native,m):fixture(machine,job,3)
  for address,arguments in ((0x08025fdc,(6,)),(0x08026ab8,()),(0x08133d78,(UNIT,0x21)),(0x081341ec,(UNIT,))):
   check('abi',m.call(address,*arguments,stack=stack)==native.call(address,*arguments,stack=stack),'both stack residues/fallback')
check('abi',bool(aligned) and all(sp%8==0 for sp in aligned),'C predicate boundary alignment')
report={'passed':True,'romSha1':meta['romSha1'],'checks':checks,'total':sum(checks.values()),'scope':'Native four-predicate differential and added-only type/AP/status cases. Restriction/status/selector providers are controlled callbacks; nested successor interleaving tests no shared state. No full battle menu or AI list rendering claim.'}
(frozen/'tests.json').write_text(json.dumps(report,indent=2)+'\n');(out/'command-predicate-tests.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

