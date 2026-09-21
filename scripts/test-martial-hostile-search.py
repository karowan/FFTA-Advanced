"""Native Last Resort/Provoke placement with legal weapons and exact challenge owner.

The actual constructor chooses its search callback; fixed movement and native
rows are inputs. This is placement/admission coverage, not autonomous playback.
"""
import collections,itertools,json,struct
from ai_review_fixture import *
NODE,GROUP,OTHER,MOVE,BUFFER,GRID,CENTERS=0x02015488,0x02028000,0x0202aa00,0x0202d400,0x0202d600,0x02026000,0x0202ec00
checks=collections.Counter();cases=[];failures=[]
def check(name,actual,expected=True):
 checks[name]+=1
 if actual!=expected:failures.append(dict(case=case,check=name,actual=actual,expected=expected))

for action,race,condition in itertools.product((360,373),(1,2),
 ('useful','unarmed','Healer','katana','axe','blocked','silenced','no-MP','distant','move-to-target','height','same-challenger','other-challenger','last-resort')):
 if action==373 and race!=2:continue
 case=(action,race,condition);reset();job=118 if action==373 else 117 if race==1 else 119
 m.put(A+5,bytes((job,race,job)));m.put(A+0x35,bytes((job,)));m.put(T+0x29,b'\x80')
 m.put(A+0x2a,struct.pack('<H',{'unarmed':0,'Healer':124,'katana':376,'axe':399}.get(condition,1)))
 m.put(GRID,bytes((16,0))*256);info=bytearray(16);struct.pack_into('<I',info,4,GRID);info[8]=info[13]=info[15]=16;m.put(0x02007f10,info)
 tx=12 if condition=='distant' else 8 if condition=='move-to-target' else 5
 if condition=='height':m.put(GRID+2*(14*16+tx),b'\x40')
 for u in wrappers:
  x,y=(4,14) if u==A else (tx,14) if u==T else (0,0)
  m.put(u+0xf6,bytes((x,y)));m.put(wrappers[u]+8,struct.pack('<3H',x*32+16,1024 if u==T and condition=='height' else 256,y*32+16))
 for u in (A,T):m.call(0x080ca2e8,u,stack=STACK)
 if condition=='silenced':m.put(A+0xeb,b'\x08')
 if condition=='no-MP':m.put(A+0x1c,bytes(2))
 if condition=='same-challenger':call('ffta_viking_grant_challenge',T,A)
 if condition=='other-challenger':call('ffta_viking_grant_challenge',T,0x02000398)
 if condition=='last-resort':call('ffta_drk_grant_last_resort',A,1)
 usable=m.call(0x08133e18,A,action,128,stack=STACK)
 check('native-admission',bool(usable),condition!='no-MP')
 m.put(OTHER,bytes(0x290c));m.put(GROUP,bytes(0x290c));m.put(GROUP+0x2908,b'\x01\0');m.put(OTHER+0x2908,b'\x01\0')
 for p,u in ((GROUP,T),(OTHER,A)):
  m.put(p,struct.pack('<I',wrappers[u]));m.put(STACK,bytes(8))
  if usable:m.call(0x080c2618,p+4,wrappers[A],wrappers[u],action,stack=STACK)
  m.put(p+804,struct.pack('<H',int(bool(int.from_bytes(m.read(p+14,2),'little')))))
 movement=bytearray(b'\x80'*256)
 if condition!='blocked':movement[14*16+4]=2
 if condition=='move-to-target':movement[14*16+7]=2
 m.put(NODE,bytes(0x21c));m.put(STACK,struct.pack('<5I',OTHER,GROUP+4,0,MOVE,0))
 callback=m.call(0x080c01d0,NODE,wrappers[A],wrappers[T],GROUP,stack=STACK)
 m.put(NODE+0x200,struct.pack('<I',CENTERS));m.put(NODE+0x204,struct.pack('<I',BUFFER))
 m.put(MOVE,movement);m.put(BUFFER-16,b'\xa5'*4128);m.put(CENTERS-16,b'\xa6'*288)
 before=protected();arithmetic=m.read(0x03005e80,384)
 for tick in range(257):
  if not m.call(callback,NODE,0,stack=STACK):break
 else:raise AssertionError(('unbounded placement',case))
 check('placement-pure',protected()==before);check('low-stack-arithmetic-intact',m.read(0x03005e80,384)==arithmetic)
 check('buffer-guards',m.read(BUFFER-16,16)+m.read(BUFFER+4096,16)==b'\xa5'*32 and m.read(CENTERS-16,16)+m.read(CENTERS+256,16)==b'\xa6'*32)
 success=m.read(NODE+0x1b1,1)[0];score=m.word(NODE+0x1c);coords=list(m.read(NODE+0x1ac,4))
 expected=condition not in ('blocked','no-MP','distant','height')
 if action==360 and condition in ('unarmed','Healer'):expected=False
 if action==373 and condition=='same-challenger':expected=False
 check('legal-useful-hostile-placement',bool(success),expected)
 if success:
  check('positive-value',score>0);check('actual-target',coords[2:],[tx,14])
  check('legal-origin',coords[:2] in ([[4,14],[7,14]] if condition=='move-to-target' else [[4,14]]))
 cases.append(dict(action=action,race=race,condition=condition,success=success,score=score,coords=coords,callback=hex(callback),ticks=tick+1))
report=dict(passed=not failures,romSha1=meta['romSha1'],capture=capture,total=sum(checks.values()),checks=dict(checks),cases=cases,failures=failures,scope=__doc__)
(OUT/'martial-hostile-search.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ('cases','capture')},indent=2));assert not failures,failures
