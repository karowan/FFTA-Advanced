"""Native area placement for useful, redundant and silenced MP/Slow dances."""
import collections,itertools,json,struct
from ai_review_fixture import *
NODE,FRIENDS,ENEMIES,MOVE,BUFFER,GRID,CENTERS=0x02015488,0x02028000,0x0202aa00,0x0202d400,0x0202d600,0x02026000,0x0202ec00
checks=collections.Counter();cases=[];failures=[]
def check(name,actual,expected=True):
 checks[name]+=1
 if actual!=expected:failures.append(dict(case=case,check=name,actual=actual,expected=expected))
for action,condition in itertools.product((402,403),('useful','redundant','silenced','unaffordable','blocked','distant')):
 case=(action,condition);reset();m.put(A+5,bytes((124,4,124)));m.put(A+0x35,b'\x7c');m.put(T+0x29,b'\x80')
 m.put(GRID,bytes((16,0))*256);info=bytearray(16);struct.pack_into('<I',info,4,GRID);info[8]=info[13]=info[15]=16;m.put(0x02007f10,info)
 for u in wrappers:
  x,y=(4,14) if u==A else (12 if condition=='distant' else 5,14) if u==T else (0,0)
  m.put(u+0xf6,bytes((x,y)));m.put(wrappers[u]+8,struct.pack('<3H',x*32+16,256,y*32+16))
 for u in (A,T):m.call(0x080ca2e8,u,stack=STACK)
 if condition=='redundant':m.put(T+0x1c,bytes(2)) if action==402 else m.put(T+0xea,b'\x40')
 if condition=='silenced':m.put(A+0xeb,b'\x08')
 if condition=='unaffordable':m.put(A+0x1c,bytes(2))
 usable=m.call(0x08133e18,A,action,128,stack=STACK);check('native-admission',bool(usable),condition!='unaffordable')
 # BE5F4 treats the first group as intended recipients, second as collateral.
 # Harmful rows therefore put enemies first; beneficial songs put allies first.
 node=bytearray(0x21c);struct.pack_into('<IIHHII',node,0,wrappers[A],wrappers[T],action,0,ENEMIES,FRIENDS)
 struct.pack_into('<I',node,0x200,CENTERS);struct.pack_into('<I',node,0x204,BUFFER);struct.pack_into('<I',node,0x214,MOVE);m.put(NODE,node)
 for group,u in ((FRIENDS,A),(ENEMIES,T)):
  m.put(group,bytes(0x290c));m.put(group+0x2908,b'\x01\0');m.put(group,struct.pack('<I',wrappers[u]));m.put(STACK,bytes(8))
  if usable:m.call(0x080c2618,group+4,wrappers[A],wrappers[u],action,stack=STACK)
  m.put(group+804,struct.pack('<H',int(bool(int.from_bytes(m.read(group+14,2),'little')))))
 movement=bytearray(b'\x80'*256)
 if condition!='blocked':movement[14*16+4]=2
 m.put(MOVE,movement);m.put(BUFFER-16,b'\xa5'*4128);m.put(CENTERS-16,b'\xa6'*288)
 before=protected();arithmetic=m.read(0x03005e80,384)
 for tick in range(257):
  if not m.call(0x080bef28,NODE,0,stack=STACK):break
 else:raise AssertionError(('unbounded placement',case))
 check('placement-pure',protected()==before);check('resident-arithmetic-intact',m.read(0x03005e80,384)==arithmetic)
 check('native-buffer-guards',m.read(BUFFER-16,16)+m.read(BUFFER+4096,16)==b'\xa5'*32 and m.read(CENTERS-16,16)+m.read(CENTERS+256,16)==b'\xa6'*32)
 success=m.read(NODE+0x1b1,1)[0];score=m.word(NODE+0x1c);coords=list(m.read(NODE+0x1ac,4))
 check('only-useful-legal-dance-selected',bool(success),condition in ('useful','silenced'))
 if success:
  check('positive-placement-value',score>0);check('legal-origin',coords[:2],[4,14])
  check('covers-enemy',abs(coords[2]-5)+abs(coords[3]-14)<=1)
 cases.append(dict(action=action,condition=condition,success=success,score=score,coords=coords,callbacks=tick+1))
report=dict(passed=not failures,romSha1=meta['romSha1'],capture=capture,total=sum(checks.values()),checks=dict(checks),cases=cases,failures=failures)
(OUT/'dancer-ordinary-search.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not failures,failures
