"""Native existing help preservation and private Samurai action/support descriptions."""
import ast,hashlib,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
def u16(b,p):return struct.unpack_from('<H',b,p)[0]
def u32(b,p):return struct.unpack_from('<I',b,p)[0]
tree=ast.parse((ROOT/'scripts/test-content-data.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native text harness>','exec'))
P=ROOT/'build/expansion/probes';meta=json.loads((P/'samurai/current.json').read_text());ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1'];help=meta['help'];base=(ROM.parent/'input.gba').read_bytes()
m,n=ARM(rom),ARM(base);checks={}
def check(k,a,b):
 assert a==b,(k,a,b)
 checks[k]=checks.get(k,0)+1
for ident in range(help['first']):
 a=n.map_help(ident);b=m.map_help(ident);check('original_and_equipment_routing',b,a)
 check('original_and_equipment_text',m.decode_help(*b),n.decode_help(*a))
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
for lesson in help['lessons']:
 ident=lesson['helpId'];route=m.map_help(ident);check('new_help_route',route,(0x13,ident-0x1de))
 _,body,flags=m.decode_help(*route);check('header',flags,b'\0\2')
 tokens=[];line=0;lines=[];mapping={(0x40,0x73):' ',(0x81,0x0b):'-',(0x80,0xf4):"'",(0x80,0xe4):'.',(0x80,0xec):',',(0x80,0xee):':',(0x80,0xf1):'/'}
 for i in range(0,4096,2):
  a,b=body[i:i+2]
  if a==0:break
  if (a,b)==(0x40,0x6e):tokens.append(' ');lines.append(line);line=0;continue
  if (a,b) in ((0x40,0x61),(0x40,0x63)):continue
  if a==0x80 and 0xb0<=b<=0xc9:letter=chr(65+b-0xb0)
  elif a==0x80 and 0xca<=b<=0xe3:letter=chr(97+b-0xca)
  elif a==0x80 and 0xa6<=b<=0xaf:letter=chr(48+b-0xa6)
  else:letter=mapping[a,b]
  tokens.append(letter);line+=1
 lines.append(line);check('native_decoded_description',''.join(tokens),lesson['text']);check('bounded_lines',len(lines)<=3 and max(lines)<=27,True)
 record=next(l for l in registry['lessons'] if l['id']==lesson['id'])
 for owner in record['owners']:
  address=m.call(0x080cd480,owner['race'],owner['abilityIndex'])
  check('native_assigned_help',u16(rom,address-0x08000000+2),ident)
result={'passed':True,'romSha1':meta['romSha1'],'checks':sum(checks.values()),'groups':checks,'lessons':len(help['lessons']),'scope':__doc__}
(ROM.parent/'help-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
