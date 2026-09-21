"""Native combo domain, named donors, weapon gates, status/RNG and trampoline ABI."""
import ast,ctypes as C,hashlib,importlib.util,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_INSN_INVALID
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02020000,0x02024000,0x08000100,0x03007000
OUT=ROOT/'build/expansion/probes';sha=lambda b:hashlib.sha1(b).hexdigest()
word=lambda b,p:struct.unpack_from('<I',b,p)[0]
meta=json.loads((OUT/'combo.json').read_text());image=(OUT/'combo.gba').read_bytes()
base=(OUT/'combo-input.gba').read_bytes();clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
engine=(ROOT/'build/expansion/engine.bin').read_bytes();symbol_bytes=(ROOT/'build/expansion/engine.symbols').read_bytes()
symbols={line.split()[2]:int(line.split()[0],16) for line in symbol_bytes.decode().splitlines() if len(line.split())==3}
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
assert sha(image)==meta['romSha1'] and sha(base)==meta['baseSha1']
assert sha(engine)==meta['engineSha1'] and image[0x1100000:0x1100000+len(engine)]==engine
FROZEN=OUT/'combos-native'/sha(image);FROZEN.mkdir(parents=True,exist_ok=True)
for name,data in [('frozen.gba',image),('input.gba',base),('engine.bin',engine),('engine.symbols',symbol_bytes)]: (FROZEN/name).write_bytes(data)
(FROZEN/'manifest.json').write_text(json.dumps(meta,indent=2))
# Independently identified by original racial type5 records and their native
# Other-text name IDs. Do not trust the builder's descriptive profile labels.
DONORS={'SAM-C1':(15,568),'DRK-C1':(2,546),'VIK-C1':(7,571),'GEO-C1':(17,549),
        'CHM-C1':(23,551),'BRD-C1':(32,553),'DNC-C1':(6,566),'MYK-C1':(11,544)}
ALLOWED={'SAM-C1':{9},'DRK-C1':{1,5,6},'VIK-C1':{31},'GEO-C1':{11,12},
         'CHM-C1':{7,12},'BRD-C1':{16},'DNC-C1':{7,8},'MYK-C1':{8,3}}
pointers=[word(clean,0x51ba84+4*r)-0x08000000 for r in range(24)]+[0x51d17c]
native_lessons=[]
for race in range(24):
 for index in range((pointers[race+1]-pointers[race])//8):
  record=clean[pointers[race]+8*index:pointers[race]+8*index+8]
  if record[6]==5:native_lessons.append((race,index,struct.unpack_from('<H',record,4)[0],struct.unpack_from('<H',record)[0]))
assert len(native_lessons)==42 and {r[2] for r in native_lessons}==set(range(1,34))
assert {r[0] for r in native_lessons}=={1,2,3,4,5},'New native race/combo domain'
new_table=meta['address']-0x08000000
assert image[new_table:new_table+34*4]==clean[0x52736c:0x52736c+34*4]
assert image[new_table+34*4:new_table+128*4]==bytes(94*4)
refs=[p for p in range(0,len(clean),4) if word(clean,p)==0x0852736c]
assert refs==[0x12e19c,0x12e3e4,0x130514]
assert all(word(image,p)==meta['address'] for p in refs)
donor_units={}
for key,(donor,nameid) in DONORS.items():
 candidates=[r for r in native_lessons if r[2:]==(donor,nameid)];assert candidates,(key,donor,nameid)
 donor_units[key]=candidates[0]
 row=next(r for r in meta['added'] if r['id']==key)
 assert row['donor']==donor,('Wrong named donor',key,row['donor'],donor)
 assert image[new_table+row['globalAbilityId']*4:new_table+(row['globalAbilityId']+1)*4]==clean[0x52736c+donor*4:0x527370+donor*4]

tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')],type_ignores=[]),'<native-harness>','exec'))
iwram=iwram_from_boot();native=ARM(clean,iwram);expanded=ARM(image,iwram)
RNG=word(clean,0x2818);c_entries={symbols[n] for n in ('ffta_combo_assigned','ffta_combo_chance','ffta_combo_range','ffta_combo_power','ffta_primary_weapon')}
alignments=[]
def c_entry(u,pc,size,data):
 if pc in c_entries:
  sp=u.reg_read(UC_ARM_REG_SP);assert sp%8==0,('Unaligned C entry',hex(pc),hex(sp));alignments.append(pc)
expanded.u.hook_add(UC_HOOK_CODE,c_entry)
def arm7_bl_suffix(u,data):
 # ARM7TDMI supports this documented two-halfword BL idiom. Unicorn's newer
 # CPU rejects a standalone suffix; emulate that instruction, not the call.
 pc=u.reg_read(UC_ARM_REG_PC)
 if not 0x09100000<=pc<0x09100000+len(engine) or bytes(u.mem_read(pc,2))!=b'\x00\xf8':return False
 target=u.reg_read(UC_ARM_REG_LR);u.reg_write(UC_ARM_REG_LR,(pc+2)|1);u.reg_write(UC_ARM_REG_PC,target|1)
 return True
expanded.u.hook_add(UC_HOOK_INSN_INVALID,arm7_bl_suffix)
FUNCTIONS=(0x080cd4c0,0x0812e130,0x0812e3b0,0x081304e0)
counts={'original':0,'weapon':0,'status_rng':0,'null_menu':0,'offhand':0}

def fixture(m,race,index,equipment=(),status=-1,locked=False,seed=0):
 unit=bytearray(264);unit[4]=2;unit[5]=unit[7]=2;unit[6]=race;unit[0x3c]=index
 for off in (0x18,0x1a,0x1c,0x1e):struct.pack_into('<H',unit,off,100)
 for slot,item in enumerate(equipment):struct.pack_into('<H',unit,0x2a+2*slot,item)
 if status>=0:unit[0xe8+status//8]|=1<<(status%8)
 if locked:struct.pack_into('<H',unit,0x28,0x1000)
 m.put(UNIT-16,b'\xa5'*16+unit+b'\xb6'*16)
 m.put(0x02001940,b'\xd7'*0x5dc);m.put(RNG,struct.pack('<I',seed))
 return bytes(unit)

def call(m,fn,stack,unit,mode=0,null=False):
 before=m.read(UNIT-16,296)
 args=(0,) if null else ((UNIT,0,mode) if fn==0x0812e130 else (UNIT,))
 try:value=m.call(fn,*args,stack=stack)
 except Exception as error:raise AssertionError((hex(fn),hex(m.u.reg_read(UC_ARM_REG_PC)),hex(m.u.reg_read(UC_ARM_REG_LR)),str(error))) from error
 assert m.read(UNIT-16,296)==before and m.read(0x02001940,0x5dc)==b'\xd7'*0x5dc,'Read-only combo function mutated state'
 return value,m.word(RNG)

# Every original racial combo lesson (covers all33 nonzero profiles), and
# no-assigned across all24 native race banks. Both legal incoming SP offsets.
for race,index,global_id,name in native_lessons+[(r,0,0,0) for r in range(24)]:
 for stack in (STACK,STACK+4):
  for fn in FUNCTIONS:
   a=fixture(native,race,index);b=fixture(expanded,race,index)
   assert call(native,fn,stack,a)==call(expanded,fn,stack,b),(race,index,hex(fn))
   counts['original']+=1
for stack in (STACK,STACK+4):
 a=fixture(native,1,0);b=fixture(expanded,1,0)
 assert call(native,FUNCTIONS[0],stack,a,null=True)==call(expanded,FUNCTIONS[0],stack,b,null=True)==(0,0)
 counts['null_menu']+=1

# Real item records cover every native equipment category and the new Axe.
items=word(image,0xca7c4)-0x08000000;by_category={0:0};weapons={}
for ident in range(1,461):
 row=image[items+ident*32:items+(ident+1)*32];category=row[8]
 by_category.setdefault(category,ident)
 if 1<=row[11]<=2 and category!=20:weapons.setdefault(category,[]).append((row[16],ident))
assert set(by_category)==set(range(32)),('Equipment category coverage',sorted(by_category))
lessons=[r for r in registry['lessons'] if r['type']=='Combo'];owners=sum(len(r['owners']) for r in lessons)
assert len(lessons)==8 and owners==10
for lesson in lessons:
 key=lesson['id'];dr,di,_,_=donor_units[key]
 legal=min(item for category in ALLOWED[key] for _,item in weapons[category])
 for owner in lesson['owners']:
  race,index=owner['race'],owner['abilityIndex']
  for category,primary in by_category.items():
   permitted=category in ALLOWED[key] and category in weapons
   for stack in (STACK,STACK+4):
    for fn in FUNCTIONS:
     a=fixture(native,dr,di,(primary,));b=fixture(expanded,race,index,(primary,))
     expected=call(native,fn,stack,a)[0] if permitted else 0
     if fn==FUNCTIONS[0] and permitted:expected=index
     actual=call(expanded,fn,stack,b)[0]
     assert actual==expected,('Weapon gate',key,race,category,hex(fn),actual,expected)
     counts['weapon']+=1
  # A stronger legal offhand cannot rescue a disallowed primary weapon.
  strongest=max((power,item) for c in ALLOWED[key] for power,item in weapons[c])
  wrong=min((power,item) for c in weapons if c not in ALLOWED[key] for power,item in weapons[c])
  assert strongest[0]>wrong[0],('Offhand fixture not stronger',key)
  for equipment,allowed in [((wrong[1],strongest[1]),False),((legal,wrong[1]),True)]:
   for stack in (STACK,STACK+4):
    for fn in FUNCTIONS:
     a=fixture(native,dr,di,equipment);b=fixture(expanded,race,index,equipment)
     expected=call(native,fn,stack,a)[0] if allowed else 0
     if fn==FUNCTIONS[0] and allowed:expected=index
     assert call(expanded,fn,stack,b)[0]==expected,('Primary order',key,equipment,hex(fn))
     counts['offhand']+=1
  # Entire native chance path: all44 status bits, none, KO/disabled bit,
  # deterministic/RNG modes, two seeds and both incoming stack alignments.
  for status in range(-1,44):
   for mode in (0,4):
    for seed in (0,0x12345678):
     for stack in (STACK,STACK+4):
      a=fixture(native,dr,di,(legal,),status,seed=seed);b=fixture(expanded,race,index,(legal,),status,seed=seed)
      assert call(native,FUNCTIONS[1],stack,a,mode)==call(expanded,FUNCTIONS[1],stack,b,mode),('Chance/status/RNG',key,status,mode,seed)
      counts['status_rng']+=1
  for stack in (STACK,STACK+4):
   a=fixture(native,dr,di,(legal,),locked=True);b=fixture(expanded,race,index,(legal,),locked=True)
   assert call(native,FUNCTIONS[1],stack,a)==call(expanded,FUNCTIONS[1],stack,b)==(0,0)
   counts['status_rng']+=1
assert alignments and set(alignments)==c_entries
report={'passed':True,'romSha1':sha(image),'engineSha1':sha(engine),'symbolsSha1':sha(symbol_bytes),
 'nativeRacialComboLessons':len(native_lessons),'nativeGlobalDomain':'0..33','newProfiles':8,'raceOwnerCases':owners,
 'donors':{k:v[0] for k,v in DONORS.items()},'cases':counts,'alignedCEntries':len(alignments),
 'scope':'Installed four boundaries, native original/domain differential, all32 equipment categories, ordered dual weapons, all44 status bits, RNG state and both stack alignments. No combo battle execution claim.'}
(FROZEN/'report.json').write_text(json.dumps(report,indent=2));(OUT/'combos-native/report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))

