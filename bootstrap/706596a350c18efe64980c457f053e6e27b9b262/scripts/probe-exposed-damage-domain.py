"""Read-only native stage/magnitude domain for Exposed classification review."""
import json,pathlib,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
chars=json.loads((ROOT/'tools/ffta-randomizer-source/src/main/ffta/utils/charLookup.json').read_text())
word=lambda p:struct.unpack_from('<I',rom,p)[0]
half=lambda p:struct.unpack_from('<H',rom,p)[0]
def name(action):
 p=word(0x5567f0+half(0x55187c+action*28)*4)-0x08000000;out='';compact=rom[p]==1
 if compact:p+=1
 while rom[p]:
  if compact:out+=chars.get(f'{rom[p]:X}','?');p+=1;continue
  else:a,b=rom[p:p+2];p+=2
  if a==0x80 and 0xb0<=b<=0xc9:out+=chr(65+b-0xb0)
  elif a==0x80 and 0xca<=b<=0xe3:out+=chr(97+b-0xca)
  elif a==0x80 and 0xa6<=b<=0xaf:out+=chr(48+b-0xa6)
  elif (a,b)==(0x40,0x73):out+=' '
  elif (a,b)==(0x80,0xf4):out+="'"
  elif (a,b)==(0x80,0xe4):out+='.'
  else:out+='?'
 return out
rows=[]
for selector in range((0x3a87b0-0x3a86f8)//4):
 records=[]
 for action in range(347):
  r=0x55187c+28*action
  for stage in rom[r+12:r+15]:
   if not stage:continue
   descriptor=rom[0x553e70+4*stage:0x553e74+4*stage]
   if descriptor[3]!=selector:continue
   effect=descriptor[1];kind=rom[0x3a87b0+effect*12+4]
   records.append({'action':action,'name':name(action),'stage':stage,'effect':effect,'kind':kind,'supportClassBit':bool(word(r+16)&(1<<18))})
 rows.append({'selector':selector,'callback':hex(word(0x3a86f8+4*selector)),'users':records})
out=ROOT/'build/expansion/probes/exposed-damage-domain.json';out.write_text(json.dumps(rows,indent=2))
for row in rows:
 if row['selector']:print(row['selector'],row['callback'],', '.join(f"{r['action']}:{r['name']}[k{r['kind']}/b{int(r['supportClassBit'])}]" for r in row['users']))
