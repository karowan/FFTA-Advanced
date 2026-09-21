"""Native font widths, padding arithmetic and bounded equipment help decoding.
No rebuilds or user files; tests a frozen content-data ROM image in memory.
"""
import ast,ctypes as C,hashlib,importlib.util,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
source=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')],type_ignores=[]),'<harness>','exec'))
NativeARM=ARM
source=ast.parse((ROOT/'scripts/test-content-data.py').read_text())
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','u16','u32')],type_ignores=[]),'<text-harness>','exec'))
TextARM=ARM
out=ROOT/'build/expansion/probes';rom=(out/'content-data.gba').read_bytes();meta=json.loads((out/'content-data.json').read_text())
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
m=NativeARM(rom,iwram_from_boot());t=TextARM(rom)
checks=0

def check(value,label):
 global checks
 checks+=1
 assert value,label

names=m.word(0x0806e770);items=meta['addresses']['items']
rows=[]
for item in range(461):
 name_id=struct.unpack('<H',m.read(items+item*32,2))[0]
 pointer=m.word(names+name_id*4)
 width=m.call(0x080161bc,pointer)
 check(width<=11,f'Item{item} name width {width} exceeds11')
 # Execute the actual native monster-feed clear calculation up to13A88.
 m.u.reg_write(UC_ARM_REG_R0,width);m.u.reg_write(UC_ARM_REG_R5,0x02024000)
 m.u.emu_start(0x0805c2c7,0x08013a88,count=25)
 check(m.u.reg_read(UC_ARM_REG_PC)==0x08013a88,'Native padding did not reach clear')
 count=m.u.reg_read(UC_ARM_REG_R1);destination=m.u.reg_read(UC_ARM_REG_R0)
 check(count==2*(12-width),f'Item{item} wrong native feed padding')
 check(destination+count*32==0x02024380,f'Item{item} feed clear exceeds row')
 # Exact party detail centering uses12 tiles, shop info13 incl2 icon tiles.
 check(0<=(12-width)//2+8<=14,f'Item{item} party icon coordinate')
 check(0<=(13-width-2)//2+9<=16,f'Item{item} shop icon coordinate')
 rows.append({'id':item,'widthTiles':width})
# Prove the test catches the old monster-feeding underflow.
m.u.reg_write(UC_ARM_REG_R0,13);m.u.reg_write(UC_ARM_REG_R5,0x02024000)
m.u.emu_start(0x0805c2c7,0x08013a88,count=25)
check(m.u.reg_read(UC_ARM_REG_R1)==65534,'Underflow negative control')
# Measure the actual reward popup prefix and suffix. The current popup's item/
# quest namespace branch requires its own integration audit; do not bypass it.
prefix=m.word(0x085668b0+0x144);suffix=m.word(0x085668b0+0x148)
prefix_width=m.call(0x080161bc,prefix)
suffix_raw=m.read(suffix,128);suffix_end=next(i for i in range(0,128,2) if suffix_raw[i]==0)
reward_widths=[]
for row in rows:
 pointer=m.word(names+struct.unpack('<H',m.read(items+row['id']*32,2))[0]*4)
 raw=m.read(pointer,128);end=next(i for i in range(0,128,2) if raw[i]==0)
 m.put(0x02023000,raw[:end]+suffix_raw[:suffix_end]+b'\0')
 total=prefix_width+2+m.call(0x080161bc,0x02023000)
 check(total<=20,f"Item{row['id']} reward popup needs{total} tiles")
 reward_widths.append(total)
help_rows=[]
for profile in meta['itemProfiles']:
 bank,index=t.map_help(profile['helpId']);bp=u32(rom,0x36d678+bank*4)
 pointer=u32(rom,meta['addresses']['help']-0x08000000+index*4)
 raw=rom[pointer-0x08000000:pointer-0x08000000+512];end=raw.index(0,2)
 expected=raw[2:end+1]
 # Reproduce native11B80 output/scratch gap: context30E to50C=510 bytes.
 dest=0x02020000;scratch=dest+510
 t.u.mem_write(dest-32,b'\xa5'*(32+510+512+32))
 t.call(0x08013e9c,dest,bp,scratch,index,0x02022000,0x02022001)
 check(len(expected)<=510,f"Item{profile['id']} help exceeds main output buffer")
 check(bytes(t.u.mem_read(dest,len(expected)))==expected,'Help text mismatch')
 check(bytes(t.u.mem_read(dest-32,32))==b'\xa5'*32,'Help underflow')
 check(bytes(t.u.mem_read(dest+len(expected),510-len(expected)))==b'\xa5'*(510-len(expected)),'Help output tail overwritten')
 check(bytes(t.u.mem_read(scratch,512+32))==b'\xa5'*(512+32),'Uncompressed help unexpectedly touches scratch/tail')
 widths=[]
 for line in expected[:-5].split(b'\x40\x6e'):
  m.put(0x02023000,line+b'\0');widths.append(m.call(0x080161bc,0x02023000))
 check(max(widths)<=24,f"Item{profile['id']} help line too wide {widths}")
 help_rows.append({'id':profile['id'],'decodedBytes':len(expected),'lines':len(widths),'maxWidthTiles':max(widths)})
report={'romSha1':meta['romSha1'],'checks':checks,'passed':True,'originalMaxWidthTiles':max(r['widthTiles'] for r in rows[:376]),'newMaxWidthTiles':max(r['widthTiles'] for r in rows[376:]),'rewardPrefixWidthTiles':prefix_width,'rewardMaxWidthTiles':max(reward_widths),'maxDecodedHelpBytes':max(r['decodedBytes'] for r in help_rows),'maxHelpLines':max(r['lines'] for r in help_rows),'maxHelpLineWidthTiles':max(r['maxWidthTiles'] for r in help_rows),'newItems':rows[376:],'help':help_rows,'scope':'Native font measurement, native feed clear arithmetic, fixed-layout coordinates, reward string width and native decoder510-byte guards. No full-menu or help paging claim.'}
(out/'equipment-name-width-tests.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('newItems','help')},indent=2))
