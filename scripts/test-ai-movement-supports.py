"""Native planning policy plus completed-movement support/preview boundaries.

No strategic AI optimizer: preserve the original command-before-move policy.
Candidate positions cannot mutate the real movement ledger. Actual movement,
including a loop/undo, changes the bonus consumed by the next native preview.
"""
import collections,itertools,json,struct
from ai_review_fixture import *
from unicorn import UC_HOOK_CODE
NODE,GROUP,OTHER,MOVE,BUFFER,GRID,CENTERS=0x02015488,0x02028000,0x0202aa00,0x0202d400,0x0202d600,0x02026000,0x0202ec00
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
traces=[];cases=[];current=None;checks=collections.Counter();failures=[];values=[]
def check(name,actual,expected=True):
 checks[name]+=1
 if actual!=expected:failures.append(dict(case=current,check=name,actual=actual,expected=expected))

def trace(u,pc,size,data):
 args=[u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
 aw=wrappers[A];p=A
 if pc==S['ffta_ai_choice_score']:aw=args[0];p=m.word(aw)
 else:p=args[0]
 traces.append(dict(case=current,pc=hex(pc),args=list(map(hex,args)),unit=hex(p),
  unitXY=list(m.read(p+0xf6,2)),wrapperXYZ=list(struct.unpack('<3H',m.read(aw+8,6))),
  nodeXY=list(m.read(NODE+0x1ac,4)),turn=m.read(0x0203f410+12,3).hex()))

for pc in (S['ffta_ai_choice_score'],S['ffta_turn_snapshot_flags'],S['ffta_turn_extra_flags']):
 m.u.hook_add(UC_HOOK_CODE,trace,begin=pc,end=pc)

for lesson,action in (('SAM-S1',0),('SAM-S1',23),('SAM-S1',348),('GLD-AX-S1',0),('GLD-AX-S1',361),('GLD-AX-S1',429)):
 current=(lesson,action);reset();race=1 if lesson=='SAM-S1' else 2
 job=(116 if action==348 else 8 if action==23 else 2) if race==1 else (16 if action==429 else 119)
 m.put(A+5,bytes((job,race,job)));m.put(A+0x35,bytes((job,)));m.put(T+0x29,b'\x80')
 m.put(A+0x2a,struct.pack('<H',376 if action==348 else 399 if action==429 else 1))
 entry=next(l for l in registry['lessons'] if l['id']==lesson);index=next(o['abilityIndex'] for o in entry['owners'] if o['race']==race)
 m.put(A+0x3b,bytes((index,)));m.put(0x02001b40+index-144 if race==1 and index>=144 else A+0x40+index,b'\xff')
 m.put(GRID,bytes((16,0))*256);info=bytearray(16);struct.pack_into('<I',info,4,GRID);info[8]=info[13]=info[15]=16;m.put(0x02007f10,info)
 for unit in wrappers:
  x,y=(4,14) if unit==A else (7,14) if unit==T else (0,0)
  m.put(unit+0xf6,bytes((x,y)));m.put(wrappers[unit]+8,struct.pack('<3H',x*32+16,256,y*32+16))
 for unit in (A,T):m.call(0x080ca2e8,unit,stack=STACK)
 call('ffta_turn_event',A,1)
 m.put(OTHER,bytes(0x290c));m.put(GROUP,bytes(0x290c));m.put(GROUP+0x2908,b'\x01\0');m.put(OTHER+0x2908,b'\x01\0')
 for p,unit in ((GROUP,T),(OTHER,A)):
  m.put(p,struct.pack('<I',wrappers[unit]));m.put(STACK,bytes(8))
  m.call(0x080c2618,p+4,wrappers[A],wrappers[unit],action,stack=STACK)
  m.put(p+804,struct.pack('<H',int(bool(int.from_bytes(m.read(p+14,2),'little')))))
 movement=bytearray(b'\x80'*256)
 for x in (4,5,6):movement[14*16+x]=2
 m.put(NODE,bytes(0x21c));m.put(STACK,struct.pack('<5I',OTHER,GROUP+4,0,MOVE,0))
 callback=m.call(0x080c01d0,NODE,wrappers[A],wrappers[T],GROUP,stack=STACK)
 m.put(NODE+0x200,struct.pack('<I',CENTERS));m.put(NODE+0x204,struct.pack('<I',BUFFER));m.put(MOVE,movement)
 before=protected();start=len(traces)
 for tick in range(257):
  if not m.call(callback,NODE,0,stack=STACK):break
 else:raise AssertionError(('unbounded placement',current))
 check('candidate-search-preserves-units-ledger-RNG',protected()==before)
 success=m.read(NODE+0x1b1,1)[0];xy=list(m.read(NODE+0x1ac,4))
 check('native-planning-produces-legal-target',bool(success) and xy[:2] in ([4,14],[5,14],[6,14]) and xy[2:]==[7,14])
 observed=traces[start:]
 score_traces=[t for t in observed if t['pc']==hex(S['ffta_ai_choice_score'])]
 check('native-score-path-observed',bool(score_traces))
 check('native-scores-use-unmoved-inputs',all(t['unitXY']==[4,14] and t['wrapperXYZ'][0]==144 for t in score_traces))
 cases.append(dict(case=current,callback=hex(callback),success=success,nodeXY=xy,scoreCalls=len(score_traces)))
 initial=m.read(0x02000000,0x40000);initial_iw=m.read(0x03000000,0x8000)
 for movement in ('stationary','one-tile','two-tiles','loop','undo'):
  current=(lesson,action,movement);m.put(0x02000000,initial);m.put(0x03000000,initial_iw)
  x=5 if movement=='one-tile' else 6 if movement in ('two-tiles','undo') else 4
  m.put(0x0200f4ec,struct.pack('<I',wrappers[A]));m.put(wrappers[A]+8,struct.pack('<H',x*32+16))
  if movement!='stationary':call('ffta_turn_flag',4,1,0x080968d3)
  if movement=='undo':
   m.put(wrappers[A]+8,struct.pack('<H',4*32+16));call('ffta_turn_flag',4,0,0x08096343)
  factor=25 if lesson=='SAM-S1' and movement in ('stationary','undo') else 27 if lesson=='GLD-AX-S1' and movement=='two-tiles' else 20
  before=protected();check('completed-movement-exact-factor',call('ffta_turn_damage_numerator',A,T,action,int(action!=23)),factor)
  check('factor-query-pure',protected()==before)
  # The public UI query consumes the moved wrapper before native execution
  # synchronizes the unit coordinates. Observe that the real formula reaches
  # the support provider, and require it to retire all temporary ownership.
  start=len(traces);m.put(STACK,struct.pack('<5I',0,255,0,0,0))
  result=m.call(0x080b55cc,wrappers[A],wrappers[T],action,struct.unpack('<H',m.read(A+0x2a,2))[0],stack=STACK)
  check('public-preview-keeps-live-state',protected()==before)
  check('public-preview-retires-snapshots',m.read(0x0203ff44,8)==bytes(8))
  check('public-preview-consumes-support-provider',len(traces)>start)
  values.append(dict(lesson=lesson,action=action,movement=movement,factor=factor,previewResult=result,providerCalls=len(traces)-start))
report=dict(passed=not failures,romSha1=meta['romSha1'],capture=capture,total=sum(checks.values()),checks=dict(checks),cases=cases,values=values,traces=traces,failures=failures,scope=__doc__)
(OUT/'ai-movement-supports.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ('capture','traces')},indent=2));assert not failures,failures
