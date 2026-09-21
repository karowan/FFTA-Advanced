"""Fixed clean-ROM medicine catalog and native disassembly evidence."""
import hashlib,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
assert hashlib.sha1(rom).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
OUT=ROOT/'build/expansion/probes/chemist/native';OUT.mkdir(parents=True,exist_ok=True)
chars=json.loads((ROOT/'tools/ffta-randomizer-source/src/main/ffta/utils/charLookup.json').read_text())
def name(table,index):
 p=struct.unpack_from('<I',rom,table+4*index)[0]&0x1ffffff;s=''
 while rom[p]:
  a=f'{rom[p]:X}';b=f'{rom[p+1]:X}'
  if a+b in chars:s+=chars[a+b];p+=2
  else:s+=chars.get(a,'?');p+=1
 return s
actions=[]
for i in range(347):
 r=rom[0x55187c+i*28:0x55187c+(i+1)*28];title=name(0x5567f0,struct.unpack_from('<H',r)[0])
 if 250<=i<=275 or any(s.lower() in title.lower() for s in ('potion','ether','cureall','antidote','phoenix','soft','eye drops','echo screen')):
  ds=[list(rom[0x553e70+s*4:0x553e74+s*4]) for s in r[12:16]]
  actions.append(dict(id=i,name=title,record=r.hex(),descriptors=ds))
items=[]
for i in range(362,376):
 r=rom[0x51d1a0+(i-1)*32:0x51d1a0+i*32]
 items.append(dict(id=i,name=name(0x526680,struct.unpack_from('<H',r)[0]),record=r.hex()))
catalog=dict(actions=actions,items=items)
(OUT/'catalog.json').write_text(json.dumps(catalog,indent=2));print(json.dumps(catalog,indent=2))
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB);md.skipdata=True
ranges=[(0xa4be0,0xa5350),(0xa2030,0xa2210),(0xa39f8,0xa433c),(0xa4614,0xa4780),(0xa4990,0xa4be0),(0x12e6a4,0x12ee00),(0xa2210,0xa2380),(0x7b928,0x7bd00),(0x7c28c,0x7c500),(0xa433c,0xa4500),(0xa4500,0xa4614),(0xa4780,0xa4990),(0x131800,0x131b20),(0x130900,0x130bc0),(0x1323b0,0x132500),(0x133500,0x133800),(0x133e18,0x133f70)]
ranges += [(0x131ba8,0x131f70),(0x132000,0x1326ac),(0x1326ac,0x1329b8),(0x133180,0x1331f8),(0x133800,0x133bc4)]
ranges += [(0x130150,0x1302a0),(0x12f230,0x12f404),(0x131b20,0x131ba8)]
ranges += [(0xa2e70,0xa2ef0),(0x133bc4,0x133cd0)]
ranges += [(0x1339a8,0x133adc),(0xc8280,0xc82d8),(0x26b90,0x270cc),(0x272c6,0x273c0)]
ranges += [(0xa0014,0xa0210),(0x131da4,0x131dd4)]
ranges += [(0x271c0,0x27918),(0x26700,0x26b90),(0xccd50,0xcce60),(0x942ba,0x94500),(0x23560,0x23988),(0x253b0,0x26000),(0x26000,0x26700),(0x27918,0x29000)]
for start in range(0,len(rom)-4,2):
 a,b=struct.unpack_from('<HH',rom,start)
 if a&0xf800==0xf000 and b&0xf800==0xf800:
  displacement=((a&0x7ff)<<12)|((b&0x7ff)<<1)
  if displacement&0x400000:displacement-=0x800000
  if start+4+displacement in (0xca9e8,0x254a0):ranges.append((max(0,start-64),start+128))
for table,ids in [(0x3a86f8,(20,22,34,35,41)),(0x3a8604,(5,8,19)),(0x3a87b0,(9,38,68,79))]:
 for index in ids:
  addr=struct.unpack_from('<I',rom,table+index*(12 if table==0x3a87b0 else 4))[0]&0x1fffffe
  ranges.append((addr,addr+180))
lines=[]
for start,end in ranges:
 lines.append(f'\nNative {start:06X}..{end:06X}')
 lines.extend(f'{i.address:08X} {i.bytes.hex():<10} {i.mnemonic} {i.op_str}' for i in md.disasm(rom[start:end],0x08000000+start))
(OUT/'disassembly.txt').write_text('\n'.join(lines))

# Exact native battle-manager literal consumers, kept as audit evidence.
manager=[]
for off in range(0,0x150000,2):
 op=struct.unpack_from('<H',rom,off)[0]
 if op&0xf800!=0x4800:continue
 lit=((off+4)&~3)+(op&255)*4
 if struct.unpack_from('<I',rom,lit)[0]!=0x0200f438:continue
 manager.append(f'\nManager reader {off:06X}')
 manager.extend(f'{i.address:08X} {i.bytes.hex():<10} {i.mnemonic} {i.op_str}' for i in md.disasm(rom[off:off+128],0x08000000+off))
(OUT/'manager-readers.txt').write_text('\n'.join(manager))






application_users=[]
for offset in range(0,len(rom)-3,4):
 if int.from_bytes(rom[offset:offset+4],"little")==0x083a87b0:application_users.append(hex(offset))
(OUT/"application-table-users.json").write_text(json.dumps(application_users))

callbacks=[]
functions=sorted(set(struct.unpack_from('<I',rom,0x3a87b0+i*12)[0]&0x1fffffe for i in range(93)))
for effect in range(93):
 start=struct.unpack_from('<I',rom,0x3a87b0+effect*12)[0]&0x1fffffe
 end=next((x for x in functions if x>start),start+160)
 instructions=list(md.disasm(rom[start:min(end,start+600)],0x08000000+start))
 status_calls=[]
 for i,x in enumerate(instructions):
  if x.mnemonic=='bl' and x.op_str=='#0x8131dd4':
   status_calls.append([f'{y.address:08X} {y.mnemonic} {y.op_str}' for y in instructions[max(0,i-3):i+1]])
 callbacks.append(dict(effect=effect,pointer=hex(0x08000000+start),metadata=rom[0x3a87b0+effect*12:0x3a87b0+(effect+1)*12].hex(),statusCalls=status_calls))
(OUT/'application-callbacks.json').write_text(json.dumps(callbacks,indent=2))

ailment_names=[]
for action in range(347):
 row=rom[0x55187c+action*28:0x55187c+(action+1)*28]
 effects=[rom[0x553e70+d*4+1] for d in row[12:16]]
 if any(e in (12,35,41,45,46,56,60,61) for e in effects):
  ailment_names.append(dict(action=action,name=name(0x5567f0,struct.unpack_from('<H',row)[0]),effects=effects))
(OUT/'ailment-names.json').write_text(json.dumps(ailment_names,indent=2))
reaction_blockers={}
for reaction in range(1,16):
 reaction_blockers[reaction]=[status for status in range(44) if not rom[0x527d5c+12*reaction+(status*2)//8]&(1<<((status*2)%8))]
(OUT/'reaction-blockers.json').write_text(json.dumps(reaction_blockers,indent=2))
