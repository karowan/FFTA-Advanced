"""Native placement for martial healing, protection and self preparation.

Fixed flat/height geometry, native recipient rows and declared legal origins.
No fabricated forecast values, scheduler claims or campaign playback.
"""
import collections,itertools,json,struct,sys
from ai_review_fixture import *
NODE,GROUP,OTHER,MOVE,BUFFER,GRID,CENTERS=0x02015488,0x02028000,0x0202aa00,0x0202d400,0x0202d600,0x02026000,0x0202ec00
checks=collections.Counter();cases=[];failures=[]

def check(name,actual,expected=True):
 checks[name]+=1
 if actual!=expected:failures.append(dict(case=case,check=name,actual=actual,expected=expected))

def complete(u):
 m.put(u+0x18,struct.pack('<H',300));m.put(u+0xeb,b'\x03')
 m.put(state(u),bytes((2,call('ffta_job_origin',A),1)));m.put(state(u)+4,b'\x02')

for action,condition in itertools.product((350,351,359,360,364,368),
 ('useful','complete','self-only','ally-only','blocked','silenced','unaffordable','distant','move-to-ally','height','cure-only')):
 case=(action,condition);reset()
 job,race=(116,1) if action<359 else (118,2) if action==368 else (117,1)
 m.put(A+5,bytes((job,race,job)));m.put(A+0x35,bytes((job,)));m.put(A+0x2a,struct.pack('<H',376 if job==116 else 1))
 m.put(GRID,bytes((16,0))*256);info=bytearray(16);struct.pack_into('<I',info,4,GRID);info[8]=info[13]=info[15]=16;m.put(0x02007f10,info)
 tx=12 if condition=='distant' else 7 if condition=='move-to-ally' else 5
 if condition=='height':m.put(GRID+2*(14*16+tx),b'\x40')
 for u in wrappers:
  x,y=(4,14) if u==A else (tx,14) if u==T else (0,0)
  m.put(u+0xf6,bytes((x,y)));m.put(wrappers[u]+8,struct.pack('<3H',x*32+16,1024 if u==T and condition=='height' else 256,y*32+16))
 for u in (A,T):m.call(0x080ca2e8,u,stack=STACK)
 if condition in ('complete','ally-only','distant','move-to-ally','height','cure-only'):complete(A)
 if condition in ('complete','self-only','cure-only'):complete(T)
 if condition=='cure-only':m.put(T+0xe9,b'\x04');m.put(T+0xeb,b'\x1b')
 if condition=='silenced':m.put(A+0xeb,b'\x08')
 if condition=='unaffordable':m.put(A+0x1c,bytes(2))
 usable=m.call(0x08133e18,A,action,128,stack=STACK)
 check('native-admission',bool(usable),condition!='unaffordable')
 target=A if action in (359,360) or condition=='self-only' else T
 node=bytearray(0x21c);struct.pack_into('<IIHHII',node,0,wrappers[A],wrappers[target],action,0,GROUP,OTHER)
 node[0x28]=1;struct.pack_into('<I',node,0x200,CENTERS);struct.pack_into('<I',node,0x204,BUFFER);struct.pack_into('<I',node,0x214,MOVE);m.put(NODE,node)
 m.put(OTHER,bytes(0x290c));m.put(GROUP,bytes(0x290c));m.put(GROUP+0x2908,b'\x02\0')
 for i,u in enumerate((A,T)):
  p=GROUP+808*i;m.put(p,struct.pack('<I',wrappers[u]));m.put(STACK,bytes(8))
  if usable:m.call(0x080c2618,p+4,wrappers[A],wrappers[u],action,stack=STACK)
  m.put(p+804,struct.pack('<H',int(bool(int.from_bytes(m.read(p+14,2),'little')))))
 movement=bytearray(b'\x80'*256)
 if condition!='blocked':movement[14*16+4]=2
 if condition=='move-to-ally':movement[14*16+6]=2
 # Let the actual native constructor choose its callback and initialize row
 # ownership. The two allocated scratch pointers are replaced with guarded
 # test arenas; no allocation/campaign-capacity claim is made here.
 selected=GROUP+4+(808 if target==T else 0)
 m.put(STACK,struct.pack('<5I',OTHER,selected,1,MOVE,0))
 callback=m.call(0x080c01d0,NODE,wrappers[A],wrappers[target],GROUP,stack=STACK)
 if '--native-search-control' in sys.argv and callback==0x080beac9:
  callback=S['ffta_myk_ai_original_self_search']
 m.put(NODE+0x200,struct.pack('<I',CENTERS));m.put(NODE+0x204,struct.pack('<I',BUFFER))
 m.put(MOVE,movement);m.put(BUFFER-16,b'\xa5'*4128);m.put(CENTERS-16,b'\xa6'*288)
 before=protected();arithmetic=m.read(0x03005e80,384)
 for tick in range(257):
  if not m.call(callback,NODE,0,stack=STACK):break
 else:raise AssertionError(('unbounded placement',case))
 check('placement-pure',protected()==before);check('low-stack-arithmetic-intact',m.read(0x03005e80,384)==arithmetic)
 check('buffer-guards',m.read(BUFFER-16,16)+m.read(BUFFER+4096,16)==b'\xa5'*32 and m.read(CENTERS-16,16)+m.read(CENTERS+256,16)==b'\xa6'*32)
 success=m.read(NODE+0x1b1,1)[0];score=m.word(NODE+0x1c);coords=list(m.read(NODE+0x1ac,4))
 expected=condition not in ('complete','blocked','unaffordable','distant','height','cure-only')
 if condition in ('ally-only','move-to-ally') and action in (359,360):expected=False
 if condition=='cure-only':expected=action==368
 check('useful-legal-command-selected',bool(success),expected)
 if success:
  check('positive-benefit',score>0);check('legal-origin',coords[:2] in ([[4,14],[6,14]] if condition=='move-to-ally' else [[4,14]]))
  # Native publication names the selected beneficiary. The executor resolves
  # self-centered areas separately; this alone is not a rendered-area test.
  if condition=='self-only' or action in (359,360):check('self-beneficiary',coords[2:],coords[:2])
  else:check('selected-beneficiary',coords[2:],[tx,14])
 cases.append(dict(action=action,condition=condition,success=success,score=score,coords=coords,callback=hex(callback),callbacks=tick+1))
report=dict(passed=not failures,romSha1=meta['romSha1'],capture=capture,total=sum(checks.values()),checks=dict(checks),cases=cases,failures=failures)
(OUT/('martial-utility-search-native-control.json' if '--native-search-control' in sys.argv else 'martial-utility-search.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not failures,failures
