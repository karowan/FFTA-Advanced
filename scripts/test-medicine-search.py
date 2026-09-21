"""All ten medicines through actual native row/placement constructors.

Fixed range, height, stock, KO, ailment and missing-benefit cases. The native
constructor chooses its own search callback; no fabricated completed nodes.
"""
import collections,itertools,json,struct
from ai_review_fixture import *
NODE,GROUP,OTHER,MOVE,BUFFER,GRID,CENTERS=0x02015488,0x02028000,0x0202aa00,0x0202d400,0x0202d600,0x02026000,0x0202ec00
checks=collections.Counter();cases=[];failures=[]
def check(name,actual,expected=True):
 checks[name]+=1
 if actual!=expected:failures.append(dict(case=case,check=name,actual=actual,expected=expected))
def complete(u):
 m.put(u+0x18,struct.pack('<4H',300,300,100,100));m.put(u+0xe8,bytes(8));m.put(u+0xeb,b'\x03');m.put(state(u)+8,b'\x02')
def useful(u,action):
 m.put(u+0x18,struct.pack('<4H',0 if action in (385,390) else 200,300,50,100));m.put(u+0xe8,bytes(8));m.put(state(u)+8,b'\0')
 if action in (384,389):m.put(u+0xe9,b'\x02')

for action,condition in itertools.product(range(383,393),('useful','complete','self-only','blocked','empty-stock','distant','move-to-ally','height','missing-ingredient','long-throw')):
 case=(action,condition);reset();m.put(A+5,bytes((120,3,120)));m.put(A+0x35,b'\x78')
 if condition=='long-throw':m.put(A+0x3b,bytes((next(o['abilityIndex'] for l in json.loads((ROOT/'build/expansion/registry.json').read_text())['lessons'] if l['id']=='CHM-S2' for o in l['owners'] if o['race']==3),)))
 m.put(0x02001940+362,bytes((0 if condition=='empty-stock' else 5,))*14)
 if condition=='missing-ingredient' and action in (387,390,391,392):m.put(0x02001940+(363 if action==387 else 375 if action==390 else 374 if action==391 else 371 if action==392 else 0),b'\0')
 m.put(GRID,bytes((16,0))*256);info=bytearray(16);struct.pack_into('<I',info,4,GRID);info[8]=info[13]=info[15]=16;m.put(0x02007f10,info)
 tx=12 if condition=='distant' else 9 if condition in ('move-to-ally','long-throw') else 5
 if condition=='height':m.put(GRID+2*(14*16+tx),b'\x40')
 for u in wrappers:
  x,y=(4,14) if u==A else (tx,14) if u==T else (0,0)
  m.put(u+0xf6,bytes((x,y)));m.put(wrappers[u]+8,struct.pack('<3H',x*32+16,1024 if u==T and condition=='height' else 256,y*32+16))
 complete(A);useful(T,action)
 if condition=='complete':complete(T)
 if condition=='self-only':
  complete(T)
  if action not in (385,390):useful(A,action)
 for u in (A,T):m.call(0x080ca2e8,u,stack=STACK)
 usable=m.call(0x08133e18,A,action,128,stack=STACK)
 missing=condition=='missing-ingredient' and action in (387,390,391,392)
 check('native-stock-admission',bool(usable),condition!='empty-stock' and not missing)
 target=A if condition=='self-only' else T
 m.put(OTHER,bytes(0x290c));m.put(GROUP,bytes(0x290c));m.put(GROUP+0x2908,b'\x02\0')
 for i,u in enumerate((A,T)):
  p=GROUP+808*i;m.put(p,struct.pack('<I',wrappers[u]));m.put(STACK,bytes(8))
  if usable:m.call(0x080c2618,p+4,wrappers[A],wrappers[u],action,stack=STACK)
  m.put(p+804,struct.pack('<H',int(bool(int.from_bytes(m.read(p+14,2),'little')))))
 movement=bytearray(b'\x80'*256)
 if condition!='blocked':movement[14*16+4]=2
 if condition=='move-to-ally':movement[14*16+6]=2
 selected=GROUP+4+(808 if target==T else 0)
 m.put(STACK,struct.pack('<5I',OTHER,selected,1,MOVE,0))
 callback=m.call(0x080c01d0,NODE,wrappers[A],wrappers[target],GROUP,stack=STACK)
 m.put(NODE+0x200,struct.pack('<I',CENTERS));m.put(NODE+0x204,struct.pack('<I',BUFFER))
 m.put(MOVE,movement);m.put(BUFFER-16,b'\xa5'*4128);m.put(CENTERS-16,b'\xa6'*288)
 before=protected();arithmetic=m.read(0x03005e80,384)
 for tick in range(257):
  if not m.call(callback,NODE,0,stack=STACK):break
 else:raise AssertionError(('unbounded placement',case))
 check('placement-pure',protected()==before);check('low-stack-arithmetic-intact',m.read(0x03005e80,384)==arithmetic)
 check('buffer-guards',m.read(BUFFER-16,16)+m.read(BUFFER+4096,16)==b'\xa5'*32 and m.read(CENTERS-16,16)+m.read(CENTERS+256,16)==b'\xa6'*32)
 success=m.read(NODE+0x1b1,1)[0];score=m.word(NODE+0x1c);coords=list(m.read(NODE+0x1ac,4))
 expected=condition not in ('complete','blocked','empty-stock','distant','height') and not missing and not(condition=='self-only' and action in (385,390))
 if condition=='long-throw' and action==387:expected=False
 check('useful-legal-medicine-selected',bool(success),expected)
 if success:
  check('positive-benefit',score>0);check('legal-origin',coords[:2] in ([[4,14],[6,14]] if condition=='move-to-ally' else [[4,14]]))
  check('beneficiary',coords[2:],coords[:2] if condition=='self-only' else [tx,14])
 cases.append(dict(action=action,condition=condition,success=success,score=score,coords=coords,callback=hex(callback),callbacks=tick+1,selected=list(m.read(selected,20))))
report=dict(passed=not failures,romSha1=meta['romSha1'],capture=capture,total=sum(checks.values()),checks=dict(checks),cases=cases,failures=failures)
(OUT/'medicine-search.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not failures,failures
