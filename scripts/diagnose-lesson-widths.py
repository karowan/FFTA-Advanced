"""Measure original and new lesson labels with the native font consumer."""
import pathlib,json,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-synergies.py';ns={'__file__':str(source)}
exec(compile(source.read_text().split('reset()\nkatana=')[0],str(source),'exec'),ns)
m=ns['m'];m.put(0x02000000,ns['ram'])
content=json.loads((ROOT/'build/expansion/probes/content-data.json').read_text());clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
table=m.word(0x0802c08c);original={}
for race in content['races']:
 for i in range(race['nativeCount']):
  at=race['base']+8*i
  if clean[at+6]!=2:continue
  name,_,ident=struct.unpack_from('<3H',clean,at)
  original[ident]=m.call(0x080161bc,m.word(table+name*4),stack=ns['STACK'])
labels=[]
for lesson in ns['registry']['lessons']:
 if lesson['type'] in ('Reaction','Support'):
  labels.append(dict(id=lesson['id'],name=lesson['name'],width=m.call(0x080161bc,m.word(table+lesson['nameId']*4),stack=ns['STACK'])))
variants={}
for label in ('Counter Rhy.','Counter R.','C. Rhythm','Rhythm'):
 data=bytes(x for c in label for x in ((0x40,0x73) if c==' ' else (0x80,0xe4) if c=='.' else (0x80,0xb0+ord(c)-65 if c.isupper() else 0xca+ord(c)-97)))+b'\0'
 m.put(0x02028000,data);variants[label]=m.call(0x080161bc,0x02028000,stack=ns['STACK'])
report=dict(original=original,labels=labels,variants=variants)
(ns['OUT']/'lesson-width-diagnostic.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
