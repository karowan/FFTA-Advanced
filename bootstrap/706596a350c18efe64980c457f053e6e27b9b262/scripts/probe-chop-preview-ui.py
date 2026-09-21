"""Read-only Chop evidence analysis and complete racial-bank regression.

Preserves every frozen chop-game-lab file. A separate diagnostic ROM repairs
only the table allocation, allowing the original saved state/engine to replay.
"""
import ctypes as C,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn.arm_const import *
from PIL import Image
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'));arm=runpy.run_path(str(ROOT/'scripts/test-battle-inventory.py'))
LAB=ROOT/'build/expansion/probes/chop-game-lab';OUT=LAB.parent/'chop-preview-ui';OUT.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha1(b).hexdigest()
original_files={p.name:sha(p.read_bytes()) for p in LAB.iterdir() if p.is_file()}
broken=(LAB/'frozen.gba').read_bytes();clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
assert sha(broken)=='dc02c7b68c950a503441735b1a0d168c847784cd','Different failing fixture'
word=lambda data,offset:struct.unpack_from('<I',data,offset)[0]
native_table=word(clean,0xcd538)-0x08000000;broken_table=word(broken,0xcd538)-0x08000000
assert native_table==0x51ba84 and word(clean,native_table)==0x08000000+native_table+24*4
native_pointers=[word(clean,native_table+4*i) for i in range(24)]
assert word(broken,0x2c088)==0x08000000+broken_table

# Repair in a private ROM allocation, keeping the complete failing engine and
# all saved-state instruction addresses unchanged. Use only literal sites
# that reference this same table in the original ROM.
repair=bytearray(broken);destination=0x09f00000
table=bytearray(clean[native_table:native_table+96]);table[:24]=broken[broken_table:broken_table+24]
repair[destination-0x08000000:destination-0x08000000+96]=table
sites=[i for i in range(0,len(clean),4) if word(clean,i)==0x08000000+native_table and word(broken,i)==0x08000000+broken_table]
assert 0xcd538 in sites and 0x2c088 in sites
for offset in sites:struct.pack_into('<I',repair,offset,destination)
(OUT/'table-only-repair.gba').write_bytes(repair)
# A separate text marker determines whether nameID0 produces the top banner.
# Do not interpret a zero-filled ability record as an empty rendered string.
marker=bytearray(repair);marker_address=0x09f00100
marker_bytes=bytes(v for ch in 'NAMEZERO' for v in [0x80,0xb0+ord(ch)-65])+b'\0'
marker[marker_address-0x08000000:marker_address-0x08000000+len(marker_bytes)]=marker_bytes
struct.pack_into('<I',marker,word(marker,0x2c08c)-0x08000000,marker_address)
(OUT/'name-zero-marker.gba').write_bytes(marker)

def reaction_name(image,race,index=0):
 m=arm['ARM']((LAB/'preview-frame-020.iwram').read_bytes());m.put(0x08000000,image)
 m.put(0x02000000,bytes(0x40000));unit=0x02000080;obj=0x02008000
 m.put(unit+6,bytes([race]));m.put(unit+0x3a,bytes([index]));m.w32(obj+0xc,unit)
 for reg,value in [(UC_ARM_REG_R5,obj),(UC_ARM_REG_SP,0x03007000),(UC_ARM_REG_R6,0x02020000)]:m.u.reg_write(reg,value)
 m.u.emu_start(0x0802c05f,0x0802c09a,count=2000)
 assert m.u.reg_read(UC_ARM_REG_PC)==0x0802c09a
 return m,m.u.reg_read(UC_ARM_REG_R2)

old_machine,old_name=reaction_name(clean,18);bad_machine,bad_name=reaction_name(broken,18)
_,repaired_name=reaction_name(repair,18)
assert bad_name==0xffffffff and repaired_name==old_name
evidence={'race':18,'reactionIndex':0,'originalBank':hex(native_pointers[18]),
          'brokenBank':hex(word(broken,broken_table+18*4)),
          'originalNamePointer':hex(old_name),'brokenNamePointer':hex(bad_name),'repairedNamePointer':hex(repaired_name),
          'originalReactionRecord':clean[native_pointers[18]-0x08000000:native_pointers[18]-0x08000000+8].hex(),
          'diagnosticRepointSites':[hex(x) for x in sites]}

# Freeze the current production repair, independent of subsequent parent builds.
meta=json.loads((LAB.parent/'combat.json').read_text());current=(LAB.parent/'combat.gba').read_bytes()
assert sha(current)==meta['romSha1'],'Stale current combat manifest'
engine=(ROOT/'build/expansion/engine.bin').read_bytes()
assert sha(engine)==meta['engineSha1'] and current[0x1100000:0x1100000+len(engine)]==engine
STAGE=OUT/sha(current);STAGE.mkdir(exist_ok=True);(STAGE/'frozen.gba').write_bytes(current)
current_table=word(current,0xcd538)-0x08000000
assert word(current,0x2c088)==0x08000000+current_table
checks=[]
for race in range(24):
 bank=word(current,current_table+4*race)
 if race==0 or race>=6:assert bank==native_pointers[race],('Original racial bank pointer lost',race,hex(bank),hex(native_pointers[race]))
 for index in range(8):
  native,native_name=reaction_name(clean,race,index)
  expanded,expanded_name=reaction_name(current,race,index)
  record=expanded.call(0x080cd480,race,index)
  assert record==bank+index*8,('Native CD480 record address',race,index,hex(record),hex(bank))
  name=expanded.r16(record);others=word(current,0x2c08c)
  expected=expanded.r32(others+name*4)
  assert expanded_name==expected,('Native reaction name resolution',race,index)
  assert 0x08000000<=expanded_name<0x0a000000,('Invalid reaction name pointer',race,index,hex(expanded_name))
  if race==0 or race>=6:
   assert expanded.get(record,8)==native.get(native.call(0x080cd480,race,index),8),('Original reaction record changed',race,index)
   assert expanded_name==native_name,('Original reaction text changed',race,index)
  checks.append([race,index])

def replay(rom,label):
 e=h['Emulator'](rom)
 try:
  e.load(LAB/'prepreview.state');samples=[]
  for frame in range(121):
   e.run(1,256 if frame<8 else 0)
   if frame in [0,20,21,30,60,120]:
    r=e.memory();samples.append({'frame':frame,'uiFlags':struct.unpack_from('<H',r,0x31650)[0],
                                'contextPrefix':r[0x2d900:0x2d920].hex(),'guard':r[0x3ff44:0x3ff50].hex()})
  e.screenshot(OUT/(label+'.png'));e.save(OUT/(label+'.state'))
  state=(OUT/(label+'.state')).read_bytes();samples[-1]['registers']=[hex(v) for v in struct.unpack_from('<17I',state,0x20)]
  assert e.memory()[0x3ff44:]==bytes([0xd7])*0xbc,'Upper guard damaged'
  return samples
 finally:e.close()
replays={'broken':replay(LAB/'frozen.gba','broken'),'tableOnlyRepair':replay(OUT/'table-only-repair.gba','table-only-repair'),
         'nameZeroMarker':replay(OUT/'name-zero-marker.gba','name-zero-marker')}
# Change only the native action-record description halfword. Keep the engine,
# formula, eligibility, animations, flags, and saved battle identical.
action_table=word(repair,0x23320)-0x08000000
description=action_table+423*28+22
assert struct.unpack_from('<H',repair,description)[0]==0xa5
for value in (0,0xa8):
 variant=bytearray(repair);struct.pack_into('<H',variant,description,value)
 label=f'banner-{value:x}';path=OUT/(label+'.gba');path.write_bytes(variant)
 replays[label]=replay(path,label)
 assert replays[label][-1]['uiFlags']==replays['tableOnlyRepair'][-1]['uiFlags']==0xe3
images={label:Image.open(OUT/(label+'.png')).convert('RGB') for label in
        ('broken','table-only-repair','name-zero-marker','banner-0','banner-a8')}
reference=images['table-only-repair'];width,height=reference.size
top=(0,0,width,height*3//16);lower=(0,height*3//16,width,height)
assert len(images['broken'].getcolors(width*height))==1,'Failure no longer reproduces as a white screen'
assert len(reference.getcolors(width*height))>16,'Table repair did not restore rendered battle'
assert reference.crop(top).tobytes()==images['name-zero-marker'].crop(top).tobytes()
assert reference.crop(lower).tobytes()!=images['name-zero-marker'].crop(lower).tobytes()
for label in ('banner-0','banner-a8'):
 assert reference.crop(top).tobytes()!=images[label].crop(top).tobytes()
 # Suppressing the task also changes sprite-animation timing in the map.
 # Compare the numerical/name UI below the map, not animated unit poses.
 ui=(0,height*9//16,width,height)
 assert reference.crop(ui).tobytes()==images[label].crop(ui).tobytes(),'Description changed preview UI'
evidence['banner']={'descriptionOffset':hex(description),'originalDescriptionId':0xa5,
 'zero':'No banner','0xa8':'Aimed attack!','original':'Knock back!',
 'nativeRead': '080B5CF2 ldrh r0,[r1,#0x16]; nonzero calls08029528 at080B5CFC',
 'nameZeroMarkerChangesLowerRowOnly':True,'numericalPreviewPixelsUnchanged':True}
assert {p.name:sha(p.read_bytes()) for p in LAB.iterdir() if p.is_file()}==original_files,'Original evidence changed'
report={'passed':True,'failingRomSha1':sha(broken),'currentRomSha1':sha(current),'currentEngineSha1':meta['engineSha1'],
        'nativeBankCount':24,'nativeNameAndGetterCases':len(checks),'evidence':evidence,'replays':replays,
        'scope':'All24bank pointers and192 native record/name cases; same failing state/engine with only allocation repaired; no Morph/name-parser bypass'}
(STAGE/'report.json').write_text(json.dumps(report,indent=2));(OUT/'report.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='replays'},indent=2))
