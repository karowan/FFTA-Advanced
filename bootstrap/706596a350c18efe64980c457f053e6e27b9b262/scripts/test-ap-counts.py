"""Native AP import/count publication and validated load migration council tests."""
import ast,ctypes as C,hashlib,importlib.util,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
source=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')],type_ignores=[]),'<harness>','exec'))
out=ROOT/'build/expansion/probes';rom=(out/'ability-core.gba').read_bytes();meta=json.loads((out/'ability-core.json').read_text());base=(out/'content-inventory.gba').read_bytes();engine=(ROOT/'build/expansion/engine.bin').read_bytes();symbol_bytes=(ROOT/'build/expansion/engine.symbols').read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1'];assert hashlib.sha1(base).hexdigest()==meta['baseSha1'];assert hashlib.sha1(engine).hexdigest()==meta['engineSha1'];assert rom[0x1100000:0x1100000+len(engine)]==engine
frozen=out/'ap-count-council'/meta['romSha1'];frozen.mkdir(parents=True,exist_ok=True)
for name,data in [('ability-core.gba',rom),('ability-core.json',json.dumps(meta).encode()),('engine.symbols',symbol_bytes)]: (frozen/name).write_bytes(data)
symbols={p[2]:int(p[0],16) for line in symbol_bytes.decode().splitlines() if len(p:=line.split())==3}
iwram=iwram_from_boot();native=ARM(base,iwram);m=ARM(rom,iwram)
old=[0,142,77,95,85,88];new=[0,178,111,124,118,116];jobs=[0,2,15,22,30,37]
checks={};alignment=[]
def check(group,ok,message):
 assert ok,f'{group}: {message}'
 checks[group]=checks.get(group,0)+1

def reset(machine):
 machine.put(0x02000000,bytes(0x40000));machine.put(0x02001e70,b'FFTAEXP1\x01')

def call(name,*values,stack=STACK):return m.call(symbols[name],*values,stack=stack)

for name in ['ffta_import_with_abilities','ffta_give_with_abilities','ffta_publish_unit_count','ffta_load_migrate_abilities','ffta_quin_prepare']:
 m.u.hook_add(UC_HOOK_CODE,lambda u,a,s,d:alignment.append((a,u.reg_read(UC_ARM_REG_SP))),begin=symbols[name],end=symbols[name])
# Native template importer remains bounded for all native race IDs.
for race in range(256):check('native_bounds',m.call(0x080c9ed8,race)==native.call(0x080c9ed8,race),'C9ED8 changed')
for stack in (STACK,STACK-4):
 for race in range(1,6):
  for owned in (False,True):
   for fmt in (0,1):
    pointer=UNIT if owned else 0x02010000
    for bitmap in (0,0x55,0xff):
     unit=bytearray(264);unit[4]=1;unit[5]=unit[7]=jobs[race];unit[6]=race;unit[9]=10
     unit[0x40:0xd0]=bytes([0x21])*144
     template=bytearray([bitmap]*0x40);template[0x28]=3;template[0x29]=4
     for machine in (m,native):
      reset(machine)
      if not fmt:machine.put(0x02001e70,bytes(9))
      machine.put(pointer-16,b'\xDA'*16);machine.put(pointer,unit);machine.put(pointer+264,b'\xDB'*16)
      machine.put(0x02020000,template)
      machine.call(0x080c9f88,pointer,0x02020000,stack=stack)
     expected=bytearray(native.read(pointer,264))
     if fmt and (race!=1 or owned):expected[0x34]=new[race]
     check('import',m.read(pointer,264)==expected,f'race{race} owned{owned} format{fmt} bitmap{bitmap}')
     check('import',m.read(pointer-16,16)==b'\xDA'*16 and m.read(pointer+264,16)==b'\xDB'*16,'unit guards')
     check('import',m.read(0x02020000,0x40)==template,'template changed')
reset(m);before=m.read(0x02000000,0x40000);call('ffta_publish_unit_count',0)
check('publication',m.read(0x02000000,0x40000)==before,'null publication modified state')
# Count publication eligibility and preservation on arbitrary exact live units.
for race in range(8):
 for active in (0,1,2):
  for count in ({0,1,141,142,178,255}|({old[race],new[race]} if race<6 else set())):
   reset(m);unit=bytearray([0x71]*264);unit[4]=active;unit[6]=race;unit[0x34]=count;m.put(UNIT,unit)
   call('ffta_publish_unit_count',UNIT)
   expected=bytearray(unit)
   if active and 1<=race<=5 and count in (old[race],new[race]):expected[0x34]=new[race]
   check('publication',m.read(UNIT,264)==expected,f'race{race} active{active} count{count}')
# Staging migration: each slot/race with native padding deliberately nonzero.
for state in (0x02000000,0x02005000):
 for fmt in (0,1,2):
  for invalid in (False,True):
   reset(m);data=bytearray(0x3ca8)
   for slot in range(24):
    race=slot%5+1;p=0x80+264*slot
    data[p:p+264]=bytes([0x30+slot])*264;data[p+4]=0 if slot==23 else 1;data[p+6]=race
    data[p+0x34]=0 if slot==22 else (old[race] if slot%2 else new[race])
   if fmt:data[0x1e70:0x1e79]=b'FFTAEXP1'+bytes([fmt]);data[0x1b40:0x1e70]=b'\x61'*816
   if invalid:struct.pack_into('<HBB',data,0x1940,376,1,0)
   if state!=0x02000000:m.put(state-16,b'\xDA'*16)
   m.put(state,data);m.put(state+len(data),b'\xDB'*16)
   # Keep an independent live sentinel when staging is used.
   if state!=0x02000000:m.put(0x02000000,b'\xCA'*0x3ca8)
   before=m.read(state,len(data));result=call('ffta_load_migrate_abilities',state)
   reject=fmt==2 or (fmt==0 and invalid)
   if reject:
    check('load',result&0x80000000 and m.read(state,len(data))==before,'invalid load not atomic')
   else:
    check('load',result==(1 if fmt==0 else 0),'migration result')
    for slot in range(24):
     race=slot%5+1;p=0x80+264*slot;expected=bytearray(before[p:p+264])
     if slot not in (22,23):
      expected[0x34]=new[race]
      if not fmt and race!=1:expected[0x40+old[race]:0x40+new[race]]=bytes(new[race]-old[race])
     check('load',m.read(state+p,264)==expected,f'slot{slot} race{race} format{fmt}')
    check('load',m.read(state+0x1b40,816)==(bytes(816) if not fmt else b'\x61'*816),'Human sidecar migration')
    check('quin_load',m.read(state+0x1e79,1)==b'\x02','valid pre-offer load initializes tracked Quin history')
   check('load',m.read(state+len(data),16)==b'\xDB'*16,'staging upper guard')
   if state!=0x02000000:check('load',m.read(0x02000000,0x3ca8)==b'\xCA'*0x3ca8,'staging mutated live state')
# Lazy give first converts valid legacy roster; alreadyformat1 keeps new AP.
for fmt in (0,1,2):
 for amount in (0,1,255):
  reset(m);data=bytearray(0x3ca8)
  for slot in range(5):
   race=slot+1;p=0x80+slot*264;data[p+4]=1;data[p+6]=race;data[p+0x34]=old[race];data[p+0x40:p+0xd0]=b'\x37'*144
  if fmt:data[0x1e70:0x1e79]=b'FFTAEXP1'+bytes([fmt])
  m.put(0x02000000,data)
  result=m.call(0x080ca900,1,amount)
  for slot in range(5):
   race=slot+1;p=0x80+slot*264
   check('give',m.read(0x02000000+p+0x34,1)[0]==(old[race] if fmt==2 else new[race]),'lazy count')
   if race!=1:check('give',m.read(0x02000000+p+0x40+old[race],new[race]-old[race])==(bytes(new[race]-old[race]) if fmt==0 else b'\x37'*(new[race]-old[race])),'lazy AP bytes')
  if fmt==2:check('give',m.read(0x02000000,len(data))==data,'unsupported format modified')
  else:
   check('give',m.read(0x02001941,1)[0]==min(amount,99),'give amount')
   check('quin_give',m.read(0x02001e79,1)==b'\x02','lazy newgame give initializes Quin history')
check('abi',all(sp%8==0 for _,sp in alignment),'C entry misaligned')
load_alignment=[]
for offset,success,failure in [(0x13aa48,0x0813aa50,0x0813aa30),(0x13aad8,0x0813aae0,0x0813aaca)]:
 for stack in (STACK,STACK-4):
  for bad in (False,True):
   reset(m);staging=bytearray(0x3ca8);staging[0x84]=1;staging[0x86]=1;staging[0xb4]=142
   if bad:struct.pack_into('<HBB',staging,0x1940,376,1,0)
   m.put(0x02003cb0,staging);before=m.read(0x02000000,0x3ca8)
   for reg,value in [(UC_ARM_REG_SP,stack),(UC_ARM_REG_LR,0x08001235),(UC_ARM_REG_R4,0x44112233),(UC_ARM_REG_R8,0x88112233),(UC_ARM_REG_R9,0x99112233),(UC_ARM_REG_R10,0xAA112233),(UC_ARM_REG_R11,0xBB112233),(UC_ARM_REG_R5,0x02003cb0),(UC_ARM_REG_R6,0x66112233),(UC_ARM_REG_R7,0x77112233)]:m.u.reg_write(reg,value)
   mark=len(alignment);end=failure if bad else success
   m.u.emu_start((0x08000000+offset)|1,end,count=50000)
   check('load_entry',m.u.reg_read(UC_ARM_REG_PC)==end,'native branch target')
   check('load_entry',m.u.reg_read(UC_ARM_REG_SP)==stack,'native stack')
   check('load_entry',m.u.reg_read(UC_ARM_REG_LR)==0x08001235,'native LR')
   check('load_entry',m.u.reg_read(UC_ARM_REG_R6)==0x66112233 and m.u.reg_read(UC_ARM_REG_R7)==0x77112233,'native callee registers')
   check('load_entry',m.u.reg_read(UC_ARM_REG_R4)==(0x44112233 if bad else 0x02000000),'native r4 contract')
   check('load_entry',all(m.u.reg_read(reg)==value for reg,value in [(UC_ARM_REG_R8,0x88112233),(UC_ARM_REG_R9,0x99112233),(UC_ARM_REG_R10,0xAA112233),(UC_ARM_REG_R11,0xBB112233)]),'native high registers')
   check('load_entry',m.read(0x02000000,0x3ca8)==before,'uncommitted live state changed')
   check('load_entry',m.read(0x02003d64,1)[0]==(142 if bad else 178),'staging Human count')
   check('quin_load_entry',m.read(0x02005b29,1)==(b'\0' if bad else b'\x02'),'normal/suspend staged Quin initialization')
   load_alignment.extend(alignment[mark:])

check('abi',bool(load_alignment) and all(sp%8==0 for _,sp in load_alignment),'Load C entry misaligned')

report={'romSha1':meta['romSha1'],'passed':True,'checks':checks,'total':sum(checks.values()),'loadEntryCStackResidues':sorted(set(sp%8 for _,sp in load_alignment)),'scope':'Native C9F88 import differential across five races, ownership, formats, bitmap patterns and stack residues; C9ED8 all byte inputs; publication eligibility; staging load atomic rejection, first conversion and current-format AP retention; installed CA900 and normal/suspend load entry dispatch. No complete save menu or full constructor simulation.'}
(frozen/'ap-count-tests.json').write_text(json.dumps(report,indent=2)+'\n');(out/'ap-count-tests.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

