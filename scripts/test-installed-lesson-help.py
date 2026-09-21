"""Current native help routing/decoding and bounded completion-patch writes.

No battle fixture, save or game playback is required for this text-only change.
All129 lesson descriptions pass through native readers, including shared races.
"""
import ast,collections,hashlib,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
def u16(b,p):return struct.unpack_from('<H',b,p)[0]
def u32(b,p):return struct.unpack_from('<I',b,p)[0]
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text(encoding='utf-8'))
rom=pathlib.Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
registry=json.loads((ROOT/'build/expansion/registry.json').read_text(encoding='utf-8'))
content=json.loads((ROOT/'build/expansion/probes/content-data.json').read_text(encoding='utf-8'))
audit=json.loads((ROOT/'build/reports/installed-design.json').read_text(encoding='utf-8'))
assert audit['passed'] and audit['candidateSha1']==meta['romSha1']
tree=ast.parse((ROOT/'scripts/test-content-data.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native text consumer>','exec'))
m=ARM(rom);counts=collections.Counter();observations=[]
def check(label,value):
 counts[label]+=1
 assert value,label
patch=meta['help']['completion']
# The last build stage changes only new text/table allocations, bank pointer,
# range endpoint and the explicitly listed racial help IDs. Executable code,
# combat data, saves and every other description remain byte-identical.
source=pathlib.Path(meta['path']).parent.parent/'completion-help-input.gba'
before=source.read_bytes();check('patch-input-hash',hashlib.sha1(before).hexdigest()==patch['inputSha1'])
expected=bytearray(before)
for allocation in patch['allocations']:
 p=allocation['offset'];n=allocation['bytes']
 check('new-help-free-space',before[p:p+n]==b'\xff'*n)
 check('allocated-text-digest',hashlib.sha1(rom[p:p+n]).hexdigest()==allocation['sha1'])
 expected[p:p+n]=rom[p:p+n]
expected[0x36d6c4:0x36d6c8]=rom[0x36d6c4:0x36d6c8]
ranges=content['addresses']['helpBanks']-0x08000000
expected[ranges+84:ranges+86]=rom[ranges+84:ranges+86]
banks=u32(rom,0x257e8)-0x08000000
for lesson in patch['lessons']:
 declared=next(l for l in registry['lessons'] if l['id']==lesson['id'])
 for owner in declared['owners']:
  p=u32(rom,banks+owner['race']*4)-0x08000000+owner['abilityIndex']*8+2
  expected[p:p+2]=rom[p:p+2]
check('only-declared-help-bytes-changed',bytes(expected)==rom)
old=patch['previous']-0x08000000;new=patch['address']-0x08000000;n=(patch['first']-0x1de)*4
check('every-prior-help-pointer-preserved',before[old:old+n]==rom[new:new+n])
mapping={(0x40,0x73):' ',(0x81,0x0b):'-',(0x80,0xf4):"'",(0x80,0xe4):'.',
 (0x80,0xec):',',(0x80,0xee):':',(0x80,0xf1):'/'}
texts={l['id']:l['text'] for l in patch['lessons']}
for lesson in audit['lessons']:
 helpids=set();description=None
 for owner in lesson['owners']:
  address=m.call(0x080cd480,owner['race'],owner['abilityIndex'])
  helpid=u16(rom,address-0x08000000+2);helpids.add(helpid)
  check('native-racial-help-id',helpid==owner['helpId'])
  route=m.map_help(helpid);check('native-expansion-help-route',route==(0x13,helpid-0x1de))
  _,body,flags=m.decode_help(*route);check('native-help-header',flags==b'\x00\x02')
  letters=[];line=0;lines=[]
  for i in range(0,len(body),2):
   a,b=body[i:i+2]
   if not a:break
   if (a,b)==(0x40,0x6e):letters.append(' ');lines.append(line);line=0;continue
   if (a,b) in ((0x40,0x61),(0x40,0x63)):continue
   if a==0x80 and 0xb0<=b<=0xc9:ch=chr(65+b-0xb0)
   elif a==0x80 and 0xca<=b<=0xe3:ch=chr(97+b-0xca)
   elif a==0x80 and 0xa6<=b<=0xaf:ch=chr(48+b-0xa6)
   else:ch=mapping[a,b]
   letters.append(ch);line+=1
  else:raise AssertionError('Unterminated help '+lesson['id'])
  lines.append(line);text=''.join(letters)
  check('nonempty-bounded-description',bool(text.strip()) and len(lines)<=3 and max(lines)<=27)
  if description is not None:check('shared-race-description-identical',text==description)
  description=text
 check('shared-race-help-id-identical',len(helpids)==1)
 if lesson['id'] in texts:check('completed-description-matches-source',description==texts[lesson['id']])
 observations.append(dict(id=lesson['id'],name=lesson['name'],helpId=next(iter(helpids)),text=description))
report=dict(passed=True,romSha1=meta['romSha1'],checks=sum(counts.values()),counts=dict(counts),lessons=observations,scope=__doc__)
output=pathlib.Path(meta['path']).parent/'installed-lesson-help.json'
output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
