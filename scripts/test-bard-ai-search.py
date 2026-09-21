"""Native Bard placement consumes real rows; no chosen scores or results.

Fixed flat geometry and legal origins are input scenarios. This tests the
downstream native search, not the scheduler, animation or a campaign turn.
"""
import collections,itertools,json,struct
from ai_review_fixture import *
NODE,GROUP,MOVE,BUFFER,GRID=0x02015488,0x02028000,0x0202d400,0x0202d600,0x02026000
OPPONENTS,CENTERS=0x0202aa00,0x0202ec00
checks=collections.Counter();cases=[];failures=[]
def check(label,actual,expected=True):
 checks[label]+=1
 if actual!=expected:failures.append(dict(case=case,check=label,actual=actual,expected=expected))
# The MP song/dance use Ether's formula but must not inherit the native
# no-AI-item byte25. Test the actual admission function, not just that byte.
for action,cost,race,job in ((399,0,5,123),(402,8,4,124)):
 for mp in (0,7,8,50):
  case=('non-item-MP-command',action,mp);reset()
  m.put(A+5,bytes((job,race,job)));m.put(A+0x35,bytes((job,)));m.put(A+0x1c,struct.pack('<H',mp))
  check('MP-command-native-AI-admission',bool(m.call(0x08133e18,A,action,128,stack=STACK)),mp>=cost)
def position(u,x,y):
 m.put(u+0xf6,bytes((x,y)));m.put(wrappers[u]+8,struct.pack('<3H',32*x+16,256,32*y+16))
for action,condition in itertools.product((393,394,395,397,398,399,400),('useful','complete','no-MP','blocked','silenced','distant')):
 case=(action,condition);reset()
 m.put(GRID,bytes((16,0))*256);info=bytearray(16)
 struct.pack_into('<I',info,4,GRID);info[8]=info[13]=info[15]=16;m.put(0x02007f10,info)
 for u in wrappers:position(u,0,0)
 position(A,4,14);position(T,12 if condition=='distant' else 5,14)
 for u in (A,T):
  m.call(0x080ca2e8,u,stack=STACK)
  if condition=='complete':
   m.put(u+0x18,struct.pack('<4H',300,300,100,100));m.put(u+0xe8,bytes((8,16,0,3,0,0,0,0)));m.put(state(u)+10,b'\x12')
 if condition=='no-MP':m.put(A+0x1c,bytes(2))
 if condition=='silenced':m.put(A+0xeb,b'\x08')
 # Native action discovery checks affordability/statuses before constructing
 # recipient rows. The later placement callback is not that admission gate.
 usable=m.call(0x08133e18,A,action,128,stack=STACK)
 check('native-admission',bool(usable),not(condition=='no-MP' and action not in (398,399)) and not(condition=='silenced' and action!=398))
 target=A if action==398 else T
 node=bytearray(0x21c);struct.pack_into('<IIHHII',node,0,wrappers[A],wrappers[target],action,0,GROUP,OPPONENTS)
 node[0x28]=1;struct.pack_into('<I',node,0x200,CENTERS);struct.pack_into('<I',node,0x204,BUFFER);struct.pack_into('<I',node,0x214,MOVE);m.put(NODE,node)
 m.put(OPPONENTS,bytes(0x290c));m.put(CENTERS-16,b'\xa5'*288)
 m.put(GROUP,bytes(0x290c));m.put(GROUP+0x2908,struct.pack('<H',2))
 for i,u in enumerate((A,T)):
  p=GROUP+i*808;m.put(p,struct.pack('<I',wrappers[u]));m.put(STACK,bytes(8))
  if usable:m.call(0x080c2618,p+4,wrappers[A],wrappers[u],action,stack=STACK)
  count=bool(int.from_bytes(m.read(p+14,2),'little'));m.put(p+804,struct.pack('<H',int(count)))
 movement=bytearray(b'\x80'*256)
 if condition!='blocked':movement[14*16+4]=2
 m.put(MOVE,movement);m.put(BUFFER-16,b'\xa5'*4128);before=protected();arithmetic=m.read(0x03005e80,384)
 for tick in range(257):
  try:more=m.call(0x080beac8 if target==A else 0x080bef28,NODE,0,stack=STACK)
  except Exception:
   print(json.dumps(dict(case=case,tick=tick,registers={name:hex(m.u.reg_read(reg)) for name,reg in
    (('pc',UC_ARM_REG_PC),('sp',UC_ARM_REG_SP),('lr',UC_ARM_REG_LR))}),indent=2),flush=True)
   raise
  if not more:break
 else:raise AssertionError(('unbounded native search',case))
 check('search-preserves-units-stock-state-RNG',protected()==before)
 check('search-preserves-native-IWRAM-arithmetic',m.read(0x03005e80,384)==arithmetic)
 check('search-preserves-buffer-guards',m.read(BUFFER-16,16)+m.read(BUFFER+4096,16)==b'\xa5'*32)
 check('native-center-list-guards',m.read(CENTERS-16,16)+m.read(CENTERS+256,16)==b'\xa5'*32)
 success=m.read(NODE+0x1b1,1)[0];score=m.word(NODE+0x1c);coords=list(m.read(NODE+0x1ac,4))
 expected=condition not in ('complete','blocked') and not(condition=='distant' and action!=398) and not(condition=='silenced' and action!=398) and not(condition=='no-MP' and action not in (398,399))
 check('native-useful-song-placement',success,int(expected))
 if success:
  check('benefit-positive',score>0);check('only-legal-origin',coords[:2],[4,14])
  check('center-covers-beneficiary',abs(coords[2]-(4 if action==398 else 5))+abs(coords[3]-14)<=int(action in (394,395,397,400)))
 cases.append(dict(action=action,condition=condition,success=success,score=score,coords=coords,callbacks=tick+1))
report=dict(passed=not failures,romSha1=meta['romSha1'],capture=capture,scope=__doc__,total=sum(checks.values()),checks=dict(checks),cases=cases,failures=failures)
(OUT/'bard-ai-search.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not failures,failures
