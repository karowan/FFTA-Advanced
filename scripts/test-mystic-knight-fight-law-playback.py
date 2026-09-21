"""Fixed native Fight inputs reach the real post-action Judge law caller.

Only the first declared law and a return breakpoint differ in the private ROM.
Result masks, law arguments and law decisions are produced by the game.
"""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/test-mystic-knight-playback.py').read_text().split('cases=[(a,0,own)')[0]
source=source.replace("support=support.replace(\"OUT=LAB/'reaction-playback'\",\"OUT=LAB/'mystic-knight-playback'\")",
 "support=support.replace(\"OUT=LAB/'reaction-playback'\",\"OUT=LAB/'mystic-knight-fight-law-playback'\")")
exec(compile(source,'<fixed Mystic Fight formation>','exec'))
elements={1:1,2:5,3:6,11:7};statuses={4:9,5:26,6:27,9:22}
e=E(TEST_ROM)
try:
 e.load(OUT/'start.state');e.run(1)
 for key in (256,16,256):tap(e,key)
 menu(e)
 for key in (256,256,128,256,256):tap(e,key)
 check('native-Fight-confirmation',mode(e)==11 and half(e.memory(),0xf3fc)==0)
 checkpoint(e,'fight-confirmation',OUT)
finally:e.close()
cases=[(k,2,v,3) for k,v in elements.items()]
cases += [(k,typ,bit if typ==15 else 0,seed) for k,bit in statuses.items() for typ in (15,16) for seed in (0,3,18)]
cases += [(1,2,5,3),(7,2,1,3),(4,15,25,3),(0,2,1,3)]
for kind,typ,value,seed in cases:
 case=(kind,typ,value,seed);folder=OUT/('-'.join(map(str,case)));folder.mkdir(exist_ok=True)
 trial=bytearray(instrumented)
 check('known-first-native-law',trial[0x529348:0x52934a]==bytes((15,28)))
 trial[0x529348:0x52934a]=bytes((typ,value))
 for pc in (0x134e68,0x135076):
  check('native-Judge-return-instruction',trial[pc:pc+2]==bytes.fromhex('0006'))
  trial[pc:pc+2]=bytes.fromhex('fee7')
 path=folder/'law.gba';path.write_bytes(trial);e=E(path)
 try:
  e.load(OUT/'fight-confirmation.state')
  e.set_memory(STATE+20,struct.pack('<H',(88<<4)|kind if kind else 0))
  e.set_memory(LOG+148,struct.pack('<II',1,seed));e.run(8,256)
  for frame in range(301):
   if word(e.memory(),LOG)==0x504c4159:break
   e.run(1)
  r=checkpoint(e,'native-transaction',folder);e.run(1800)
  final=checkpoint(e,'Judge-result',folder);cpu=struct.unpack_from('<17I',(folder/'Judge-result.state').read_bytes(),0x20)
  check('one-native-Fight',word(r,LOG)==0x504c4159 and word(r,LOG+4)==1 and word(r,LOG+8)==0)
  count=word(r,LOG+16);objects=[]
  container=word(r,LOG+136)-0x02000000
  for i in range(count):
   o=container+i*0x2c4
   if half(r,o+16) or word(r,o)!=word(r,0xf4ec):continue
   for j in range(r[o+0x2c0]):
    row=o+0x20+j*0x2c;w=word(r,row)-0x02000000
    if 0<=w<len(r)-4 and word(r,w)==0x02000000+TARGET:objects.append(row)
  check('native-target-result-present',bool(objects))
  hit=any(half(r,row+12)&0x80 and not half(r,row+12)&0x40 for row in objects)
  bit=statuses.get(kind,255)
  applied=bit<44 and any(r[row+0x14+bit//8]&(1<<(bit%8)) for row in objects)
  expected=int(hit and elements.get(kind)==value) if typ==2 else int(hit and applied and (typ==16 or bit==value))
  trapped=cpu[15] in (0x08134e6a,0x08135078)
  check('successful-Fight-reaches-native-Judge',not hit or trapped)
  if trapped:check('actual-post-action-law-result',cpu[0]==expected)
  else:check('miss-without-law-result',not expected and half(final,0xf4e8+0xdc)==47)
  outcomes.append(dict(kind=kind,law=typ,value=value,seed=seed,hit=hit,applied=bool(applied),trapped=trapped,result=cpu[0] if trapped else None,
   pc=hex(cpu[15]),testSha1=hashlib.sha1(trial).hexdigest()))
 except Exception:checkpoint(e,'failure',folder);raise
 finally:e.close()
for kind in (*elements,*statuses):check('nonvacuous-successful-law-'+str(kind),any(o['kind']==kind and o['result']==1 for o in outcomes))
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),outcomes=outcomes,
 limits=['Stops after the actual Judge query; card animation and persistent penalties remain final campaign verification.'])
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
