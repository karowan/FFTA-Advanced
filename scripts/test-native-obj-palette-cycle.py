"""Identify retained OBJ418..424 phases through the original getter/callback.

Isolated native component plus existing-trace audit; no gameplay replay or
phase-normalization acceptance. The callback's linked draw list is empty in
the isolated input, so only its native palette/counter branch is exercised.
"""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=500000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
source=ROOT/'build/art/live-palette/battle/20260918T070700.550270Z'
raw=(source/'failed.json').read_bytes()
assert sha(raw)=='85c7cb3fff9cbf67e9f84c6e452e6023fd3fbdaf3d1d18bb90a363bc2df389ca'
retained=json.loads(raw)
meta=json.loads((ROOT/'build/art/live-palette/21052ed615a6463251cba9b98952b4cc07ba4546/manifest.json').read_text())
expected={
 'parent':('b866b0e2a65bd48e4d805a52eb452609bfde5f586ecc19adec9ec8cd1008b003','45d61181cd95764255d38f798e7f0a9fefef9520f960c61076425b26ed40d11e'),
 'candidate':('44dcb5a357f9c6ec5705abe5c1e2f64ffcdc382db8177d1e72d511ba6e84073d','5750a1677a3832488b04855f8776e4c3702a62495976c4fe89be159d19e76581')}
out=ROOT/'build/art/native-obj-cycle'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];records={}
def check(ok,label):
 assert ok,label
 checks.append(label)
try:
 for case,path,digest in [('parent',meta['source'],meta['baseRomSha1']),('candidate',meta['path'],meta['romSha1'])]:
  rom=Path(path).read_bytes();check(hashlib.sha1(rom).hexdigest()==digest,case+' ROM authenticated')
  ram=(source/(case+'-ready.ram')).read_bytes();iw=(source/(case+'-ready.iwram')).read_bytes()
  check((sha(ram),sha(iw))==expected[case],case+' retained state authenticated')
  check(rom[0xba794:0xba7ac].hex()=='0e4c0f4d042011f08ff9011c04312368281c0e2287f052fd' and struct.unpack_from('<I',rom,0xba7d4)[0]==0x03003ba4,case+' native initializer copies14 bytes from getter4 plus4 to OBJ418')
  check(rom[0xba66c:0xba69a].hex()=='f0b5071c3e1ca0363078013030700006001605280bdd114c25881148a11c0368201c0c2287f0defda58100203070' and struct.unpack_from('<I',rom,0xba6c8)[0]==0x03003ba4,case+' native callback cadence and rotation site authenticated')
  a=ARM(rom,iw);a.put(0x02000000,ram)
  palette=a.call(0x080cbabc,4);initial=a.read(palette+4,14)
  ring=struct.unpack('<7H',initial)
  rotations=[struct.pack('<7H',*(ring[n:]+ring[:n])) for n in range(7)]
  check(len(set(rotations))==7,case+' seven distinct source phases')
  observed=[]
  for label,row in retained['paletteTraces'][case].items():
   value=bytes.fromhex(row['nativeShadow'])[836:850]
   check(value in rotations,case+'/'+label+' retained OBJ colors are an exact native source rotation')
   observed.append(rotations.index(value))
  # Component input, not a game fixture: no linked actors, counter starts at0.
  context=0x02030000;a.put(context,bytes(0xa4));a.put(0x03003ba4,initial)
  baseline=a.read(0x03003860,1024);steps=[]
  for tick in range(1,43):
   a.call(0x080ba66c,context);shadow=a.read(0x03003860,1024)
   wanted=rotations[(tick//6)%7]
   check(shadow[836:850]==wanted and a.read(context+0xa0,1)==bytes([tick%6]),case+' exact six-call cadence and phase '+str(tick))
   check(shadow[:836]==baseline[:836] and shadow[850:]==baseline[850:],case+' native rotation preserves all other shadow colors '+str(tick))
   check(a.read(context,0xa0)==bytes(0xa0) and a.read(context+0xa1,3)==bytes(3),case+' empty linked-list component preserves other context bytes '+str(tick))
   steps.append(shadow[836:850].hex())
  records[case]=dict(sourceAddress=palette+4,sourceColors=initial.hex(),readyPhase=observed[0],retainedPhases=sorted(set(observed)),retainedSamples=len(observed),callbackPhases=steps)
 check(records['parent']['sourceColors']==records['candidate']['sourceColors'],'Both ROMs use identical native OBJ cycle source')
 report=dict(status='passed',checks=checks,romSha1=meta['romSha1'],source=str(source),sourceSha256=sha(raw),inputs=expected,records=records,
  scope='Authenticated original initializer instructions, native getter4 and six-call OBJ418..424 callback on isolated empty-list input, plus all existing battle shadow phases. No complete scheduler/input timing, linked actor draw, candidate acceptance or phase-normalization waiver.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),records={k:{x:v for x,v in r.items() if x!='callbackPhases'} for k,r in records.items()},report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,records=records),indent=2)+'\n');print(out);raise
