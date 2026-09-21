"""Native Geo choice search on fixed boards, plus exact unmodified AI forwarding.

Movement-map inputs and material masks are declared. Native range, heights,
target eligibility, hit chance, damage and displacement are never stubbed.
Full autonomous turns are a separate plan step.
"""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-geomancer-arts.py';ns={'__file__':str(source),'__name__':'geo_ai_fixture'}
exec(compile(source.read_text().split('\nfor action,seed in itertools.product')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,STACK,wrappers,reset=(ns[k] for k in ('m','S','meta','OUT','A','T','STACK','wrappers','reset'))
NODE,GROUP,MOVE,BUFFER,TOKEN,POS=0x02015488,0x02028000,0x0202d400,0x0202d600,0x03007d00,0x0202f000
checks=collections.Counter();cases=[];case=None;failures=[];trace=[]
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3

def trace_move(u,address,size,data):
 if case==('moved-affinity',STACK,0,2) and len(trace)<520:
  args=[u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
  trace.append(dict(pc=hex(address),args=args,node=m.read(NODE+0x1ac,16).hex(),map=m.read(MOVE+14*16,16).hex()))
m.u.hook_add(UC_HOOK_CODE,trace_move,begin=0x080be074,end=0x080be074)
m.u.hook_add(UC_HOOK_CODE,trace_move,begin=0x080be1de,end=0x080be1de)
def check(k,ok):
 checks[k]+=1
 if not ok:failures.append((k,case))
def word(p):return int.from_bytes(m.read(p,4),'little')
def half(p):return int.from_bytes(m.read(p,2),'little')
def position(u,x,y):
 m.put(u+0xf6,bytes((x,y)));m.put(wrappers[u]+8,struct.pack('<3H',x*32+16,256,y*32+16))
def prepare(action,origins=((4,14),),members=None):
 reset(action);m.put(0x0203f728,bytes(4));m.put(m.word(0x0200f438)+4,b'\x00')
 members=members or (A,T)
 node=bytearray(0x21c);struct.pack_into('<IIHHII',node,0,wrappers[A],wrappers[T],action,0,GROUP,GROUP)
 struct.pack_into('<I',node,0x204,BUFFER);struct.pack_into('<I',node,0x214,MOVE);m.put(NODE,node)
 m.put(GROUP,bytes(0x290c));m.put(GROUP+0x2908,struct.pack('<H',len(members)))
 for i,u in enumerate(members):m.put(GROUP+i*808,struct.pack('<I',wrappers[u]))
 grid=bytearray(b'\x80'*256)
 for x,y in origins:grid[y*16+x]=2
 m.put(MOVE,grid);m.put(BUFFER-16,b'\xa5'*4128)
def search(sp):
 before=m.read(A,264)+m.read(T,264);rng=m.read(0x030034b0,4)
 for tick in range(257):
  result=m.call(0x080bef28,NODE,0,stack=sp)
  check('scope-retired-every-callback',word(0x0203f728)==0)
  if not result:break
 else:raise AssertionError('Unbounded search')
 check('readonly-live-units',before==m.read(A,264)+m.read(T,264))
 check('readonly-RNG',rng==m.read(0x030034b0,4))
 check('native-buffer-guards',m.read(BUFFER-16,16)+m.read(BUFFER+4096,16)==b'\xa5'*32)
 return dict(choice=half(NODE+10),position=list(m.read(NODE+0x1ac,2)),center=list(m.read(NODE+0x1ae,2)),success=m.read(NODE+0x1b1,1)[0],score=word(NODE+0x1c),callbacks=tick+1)

# Wind at the old tile is neutral. The only origin in reach grants a stronger
# available element. Forced elemental weaknesses independently identify which
# of the five real native forecasts should win; neither score nor choice is set.
for sp,(material,element) in itertools.product((STACK,STACK+4),((0,2),(1,3),(4,4),(8,1),(16,5))):
 case=('moved-affinity',sp,material,element);prepare(381,((4,14),(6,14)))
 position(T,10,14);m.put(0x091f0000+14*16+6,bytes((material,)))
 m.put(T+0x0c+element,b'\x00');result=search(sp)
 check('positive-native-candidate',result['success']==1 and result['score']>0)
 check('must-move-into-range',result['position']==[6,14])
 check('evaluated-tile-element',result['choice']==element)
 check('center-covers-target',abs(result['center'][0]-10)+abs(result['center'][1]-14)<=1)
 cases.append(dict(case=case,result=result))

# Prefer a center that hits the enemy without also damaging the adjacent ally.
case=('mixed-cross',);ally=next(u for u in wrappers if u not in (A,T))
prepare(381,members=(A,T,ally));position(ally,5,13)
m.put(ally+0x29,b'\x00');m.put(ally+0x18,struct.pack('<4H',500,500,100,100))
m.put(ally+0x0c,bytes([1]*9));m.put(ally+0xe8,bytes(8))
result=search(STACK);cx,cy=result['center']
check('mixed-cross-hits-enemy',result['success']==1 and abs(cx-5)+abs(cy-14)<=1)
check('mixed-cross-avoids-friendly-damage',abs(cx-5)+abs(cy-13)>1)
cases.append(dict(case=case,result=result))

# Action discovery must not discard Gaia just because Wind is absorbed at the
# departure tile. Its optimistic Fire row is only a possibility: an unreachable
# Fire origin must still fail the detailed movement-map gate.
for reachable in (False,True):
 case=('potential-element-row',reachable);prepare(381,((4,14),(6,14)) if reachable else ((4,14),))
 m.put(0x091f0000+14*16+6,b'\x08');m.put(T+0x0e,b'\x03');m.put(T+0x18,struct.pack('<H',100))
 m.put(STACK,bytes(8));m.call(0x080c2618,POS,wrappers[A],wrappers[T],381,stack=STACK)
 check('potential-Fire-enters-native-ranking',half(POS+2)==1 and half(POS+10)>0)
 result=search(STACK);check('potential-does-not-bypass-movement',bool(result['success'])==reachable)
 cases.append(dict(case=case,result=result))

# The native completed decision exists before the wrapper finishes moving.
# Its forecast must retain Fire at the committed endpoint throughout that gap.
case=('published-endpoint',);prepare(381)
m.put(0x091f0000+14*16+6,b'\x08');m.put(A+0x29,b'\x80')
m.put(0x0200f4ec,struct.pack('<I',wrappers[A]));m.put(NODE+10,struct.pack('<H',1))
m.put(NODE+0x1ac,bytes((6,14,5,14,0,1)));m.put(0x020101f8+0x54f4,struct.pack('<H',8))
m.put(0x020101f8+0x54be,struct.pack('<HH',381,1))
check('published-affinity-uses-committed-endpoint',m.call(S['ffta_geo_affinity'],A,stack=STACK)==8)
check('published-forecast-leaves-departure-unit',m.read(A+0xf6,2)==bytes((4,14)))

# Current-coordinate, no-range and allied-target controls must not borrow the
# attractive terrain at an unreachable origin or publish harmful casts.
for condition in ('no-range','allied','absorbed','height'):
 case=('rejection',condition);prepare(381)
 if condition=='no-range':position(T,12,14)
 if condition=='allied':m.put(T+0x29,b'\x00')
 if condition=='absorbed':m.put(T+0x0c+2,b'\x03');m.put(T+0x18,struct.pack('<H',100))
 if condition=='height':m.put(ns['GRID']+2*(14*16+5),b'\x1f')
 result=search(STACK);check('no-harmful-or-illegal-candidate',result['success']==0);cases.append(dict(case=case,result=result))

# Water-backed displacement shares the exact native collision helper with the
# executor. A one-tile corridor leaves one legal push and tests all cardinals.
directions=((0,-1),(1,0),(0,1),(-1,0))
for choice,(dx,dy) in enumerate(directions,1):
 case=('Torrent-direction',choice);prepare(376);position(T,5,14)
 m.put(0x091f0000+14*16+4,b'\x04')
 # Move the caster to the opposite side so that the sole legal push increases
 # spacing. Height31 on the three other landing cells blocks those pushes.
 position(A,5-dx,14-dy);grid=bytearray(b'\x80'*256);grid[(14-dy)*16+5-dx]=2;m.put(MOVE,grid)
 for other,(ox,oy) in enumerate(directions,1):
  if other!=choice:m.put(ns['GRID']+2*((14+oy)*16+5+ox),b'\x1f')
 m.put(ns['GRID']+2*((14-dy)*16+5-dx),b'\x10')
 m.put(0x091f0000+14*16+5,b'\x04')
 result=search(STACK);check('Torrent-publishes-cardinal',result['success']==1 and result['choice']==choice)
 cases.append(dict(case=case,result=result))

# An ordinary native action must use the exact original search with the same
# return, memory effects, registers and stack contract. Terminal phase avoids
# needing a fabricated native path allocator.
for action,sp in itertools.product((0,23,41,265,374,406),(STACK,STACK+4)):
 case=('native-forwarding',action,sp);prepare(action);m.put(NODE+0x1b8,struct.pack('<H',4))
 ram=m.read(0x02000000,0x40000);iw=m.read(0x03000000,0x8000)
 expected=m.call(S['ffta_geo_original_search'],NODE,0,stack=sp);after=m.read(0x02000000,0x40000)
 m.put(0x02000000,ram);m.put(0x03000000,iw)
 actual=m.call(0x080bef28,NODE,0,stack=sp)
 check('exact-original-return',actual==expected);check('exact-original-memory',m.read(0x02000000,0x40000)==after)
report=dict(passed=not failures,failures=failures,romSha1=meta['romSha1'],total=sum(checks.values()),checks=dict(checks),cases=cases,trace=trace,scope=__doc__)
(OUT/'geomancer-ai.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
assert not failures,failures
