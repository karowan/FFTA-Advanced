"""Conservative static references for remaining native palette effect lifetimes.

Scans every halfword for Thumb BL encodings and all bytes for exact 32-bit
function addresses. Data may look like code. Absence does not prove that an
address cannot be constructed dynamically; runtime consumers remain separate.
"""
import datetime, hashlib, json, struct
from pathlib import Path
from native_art import ROOT

meta=json.loads((ROOT/'build/art/live-palette/poc.json').read_text())
rom=Path(meta['source']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['baseRomSha1']
targets={0x081479dc:'palette init',0x08147a2c:'palette heap destroy',
 0x08146fb8:'type2 constructor',0x08147068:'type4 constructor',
 0x08147124:'type8 constructor',0x081471e0:'type16 constructor',
 0x08147fd8:'rotation wrapper',0x08148034:'cycling wrapper',
 0x08148084:'stream wrapper',0x081480c4:'frame table wrapper'}
refs={address:dict(name=name,address=hex(address),thumbBL=[],literalPointers=[]) for address,name in targets.items()}
for offset in range(0,len(rom)-4,2):
 first,second=struct.unpack_from('<HH',rom,offset)
 if first&0xf800==0xf000 and second&0xf800==0xf800:
  displacement=((first&2047)<<12)|((second&2047)<<1)
  if displacement&0x400000:displacement-=0x800000
  target=0x08000000+offset+4+displacement
  if target in refs:refs[target]['thumbBL'].append(hex(0x08000000+offset))
for address,result in refs.items():
 for value in (address,address|1):
  pattern=struct.pack('<I',value);start=0
  while True:
   offset=rom.find(pattern,start)
   if offset<0:break
   result['literalPointers'].append(dict(at=hex(0x08000000+offset),value=hex(value)))
   start=offset+1
expected={0x081479dc:[0x0800029e],0x08147a2c:[],0x08146fb8:[0x08148024],
 0x08147068:[0x08148072],0x08147124:[0x081480b4],0x081471e0:[0x081480f2],
 0x08147fd8:[0x0801d458,0x0801d468,0x080d41f2],0x08148034:[0x080d4214],
 0x08148084:[],0x081480c4:[]}
for address,calls in expected.items():
 assert refs[address]['thumbBL']==[hex(v) for v in calls],refs[address]
 assert not refs[address]['literalPointers'],refs[address]
table=struct.unpack_from('<I',rom,0x1472c0)[0]
callbacks={kind:struct.unpack_from('<I',rom,table-0x08000000+kind*4)[0] for kind in (1,2,4,8,16)}
assert callbacks=={1:0x08148741,2:0x08146865,4:0x08146bb1,8:0x08146c8d,16:0x08146d39}
out=ROOT/'build/art/effect-reachability'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True)
report=dict(status='passed',sourceRomSha1=meta['baseRomSha1'],source=meta['source'],references=list(refs.values()),
 callbackTable=hex(table),callbacks={str(k):hex(v) for k,v in callbacks.items()},
 scope='Static full-file Thumb BL and exact pointer audit. Call sites inspected separately in disassembly. No dynamic reachability proof or runtime coverage claim.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status='passed',report=str(out/'report.json'))))
