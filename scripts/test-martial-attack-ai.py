"""Grouped ordinary attack/status AI audit on the current captured candidate.

Native admission, recipient rows and area scores, not strategic turn playback.
Checks each racial owner, weapon gates, Silence, payment and shared supports.
"""
import collections,itertools,json,struct
from ai_review_fixture import *
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
ROW,NODE=0x0202f000,0x02015488
checks=collections.Counter();cases=[];failures=[]

def check(name,actual,expected=True):
 checks[name]+=1
 if actual!=expected:failures.append(dict(case=case,check=name,actual=actual,expected=expected))

def support(u,ident):
 lesson=next(l for l in registry['lessons'] if l['id']==ident)
 owner=next((o for o in lesson['owners'] if o['race']==m.read(u+6,1)[0]),None)
 if not owner:return False
 index=owner['abilityIndex'];m.put(u+0x3b,bytes((index,)))
 m.put(0x02001b40+index-144 if owner['race']==1 and index>=144 else u+0x40+index,b'\xff')
 return True

omitted={'SAM-A4','SAM-A5','DRK-A4','DRK-A9','VIK-A4'}
lessons=[l for l in registry['lessons'] if l['type']=='Action' and l['id'].startswith(('SAM-','DRK-','VIK-','SLD-AX-','GLD-AX-')) and l['id'] not in omitted]
conditions=('useful','silenced','no-MP','KO','petrify','unarmed','wrong-weapon','healer','ally',
 'target-Protect','target-Slow','target-Stop','target-no-MP','last-resort','bloodcasting','composure','opportunist','follow-through',
 'same-challenger','other-challenger')
for lesson in lessons:
 action=lesson['globalAbilityId'];ident=lesson['id']
 for owner,condition,sp in itertools.product(lesson['owners'],conditions,(STACK,STACK+4)):
  case=(ident,owner['race'],condition,sp);reset();job,race=owner['jobId'],owner['race']
  if condition in ('same-challenger','other-challenger') and action!=373:continue
  m.put(A+5,bytes((job,race,job)));m.put(A+0x35,bytes((job,)));m.put(T+0x29,b'\x80')
  weapon=376 if ident.startswith('SAM') else 1 if ident.startswith('DRK') else 399
  m.put(A+0x2a,struct.pack('<H',weapon));m.put(T+0x2a,struct.pack('<5H',288,302,0,0,0))
  for u,x in ((A,4),(T,5)):
   m.put(u+0xf6,bytes((x,14)));m.put(wrappers[u]+8,struct.pack('<3H',x*32+16,256,14*32+16))
   m.call(0x080ca2e8,u,stack=sp)
  if condition=='silenced':m.put(A+0xeb,b'\x08')
  if condition=='no-MP':m.put(A+0x1c,bytes(2))
  if condition=='KO':m.put(T+0x18,bytes(2))
  if condition=='petrify':m.put(T+0xe8,b'\x40')
  if condition in ('unarmed','wrong-weapon','healer'):
   m.put(A+0x2a,struct.pack('<H',{'unarmed':0,'wrong-weapon':2 if weapon!=1 else 376,'healer':124}[condition]))
  if condition=='ally':m.put(T+0x29,b'\0')
  if condition=='target-Protect':m.put(T+0xeb,b'\x02')
  if condition=='target-Slow':m.put(T+0xea,b'\x40')
  if condition=='target-Stop':m.put(T+0xe9,b'\x20')
  if condition=='target-no-MP':m.put(T+0x1c,bytes(2))
  if condition=='same-challenger':call('ffta_viking_grant_challenge',T,A)
  if condition=='other-challenger':call('ffta_viking_grant_challenge',T,0x02000398)
  if condition=='last-resort':call('ffta_drk_grant_last_resort',A,1)
  support_id={'bloodcasting':'DRK-S2','composure':'SAM-S1','opportunist':'VIK-S2','follow-through':'GLD-AX-S1'}.get(condition)
  if support_id and not support(A,support_id):continue
  if condition=='bloodcasting':m.put(A+0x1c,bytes(2))
  if condition=='composure':call('ffta_turn_event',A,1)
  if condition=='opportunist':m.put(T+0xe9,b'\x04')
  if condition=='follow-through':
   call('ffta_turn_event',A,1);m.put(wrappers[A]+8,struct.pack('<H',6*32+16))
   m.put(0x0200f4ec,struct.pack('<I',wrappers[A]));call('ffta_turn_flag',4,1,0x080968d3)
   check('completed-movement-ready',bool(call('ffta_turn_extra_flags',A)))
  before=protected();m.put(sp,bytes(8))
  admitted=m.call(0x08133e18,A,action,128,stack=sp)
  record=rom[0x11e8000+action*28:0x11e8000+(action+1)*28]
  check('AI-record-enabled',record[25]!=0)
  magic=action in (365,369,371,372)
  expected=not(condition=='silenced' and magic or condition=='no-MP' and record[4]>0)
  check('ordinary-admission',bool(admitted),expected)
  check('admission-pure',protected()==before)
  m.put(ROW-16,b'\xa5'*52);m.put(ROW,bytes(20));m.put(sp,bytes(8))
  m.call(0x080c2618,ROW,wrappers[A],wrappers[T],action,stack=sp)
  row=m.read(ROW,20);check('row-pure',protected()==before)
  check('row-guards',m.read(ROW-16,16)+m.read(ROW+20,16)==b'\xa5'*32)
  m.put(NODE,struct.pack('<I',wrappers[A]));m.put(NODE+8,struct.pack('<HH',action,0))
  score=m.call(0x080bdecc,wrappers[A],wrappers[T],action,0,stack=sp)
  score=score if score<0x80000000 else score-0x100000000
  check('score-pure',protected()==before);check('choice-scope-retired',m.read(0x0203f728,4)==bytes(4))
  value=struct.unpack_from('<h',row,12)[0]
  if condition=='useful':check('useful-hostile-row',value>0);check('useful-hostile-score',score>0)
  if condition=='KO':check('KO-recipient-empty',value,0);check('KO-recipient-score',score,0)
  recipient=m.call(0x080c48a4,A,T,action,stack=sp)
  check('recipient-admission-pure',protected()==before)
  if condition=='KO':check('KO-recipient-admission',recipient,0)
  if condition=='petrify':
   # Native physical/magic recipient admission itself allows this target;
   # status/theft gates differ. Do not impose the medicine-only restriction
   # on original attack policy or infer final selection from an early row.
   expected_recipient=0 if action in (360,366,373) else m.call(0x080c48a4,A,T,26 if magic else 0,stack=sp)
   check('native-Petrify-recipient-policy',recipient,expected_recipient)
  weapon_gated=ident.startswith(('SAM','DRK','SLD','GLD')) or action in (367,370)
  if weapon_gated and condition in ('unarmed','healer'):
   check('invalid-strike-row',value,0);check('invalid-strike-score',score,0)
  if action==373 and condition=='same-challenger':
   check('redundant-challenge-row',row[4:],bytes(16));check('redundant-challenge-score',score,0)
  if action==373 and condition=='other-challenger':
   check('replacement-challenge-retained',value>0 and score>0)
  # Preserve exact original forecasts for commands not deliberately reweighted.
  # This control does not assert their numeric formula is independently proven.
  if action!=360 and not(action==373 and condition=='same-challenger'):
   control=ROW+64;m.put(control,bytes(20));m.put(sp,bytes(8))
   m.call(S['ffta_ai_original_row'],control,wrappers[A],wrappers[T],action,stack=sp)
   check('native-recipient-policy',row,m.read(control,20))
   raw=m.call(S['ffta_ai_original_score'],wrappers[A],wrappers[T],action,0,stack=sp)
   check('native-area-policy',score,raw if raw<0x80000000 else raw-0x100000000)
  cases.append(dict(lesson=ident,race=race,condition=condition,stack=sp,admitted=admitted,recipient=recipient,row=list(struct.unpack('<10h',row)),score=score))
# Last Resort's actor buff must never masquerade as an enemy benefit. Compare
# against an otherwise identical native forecast with only that descriptor
# omitted, across primary weapon families and legal racial supports.
for race,weapon,condition,sp in itertools.product((1,2),(0,1,124,376,399),('normal','active','bloodcasting','composure','Protect'),(STACK,STACK+4)):
 case=('Last Resort first-stage oracle',race,weapon,condition,sp);reset()
 m.put(A+5,bytes((117 if race==1 else 119,race,117 if race==1 else 119)));m.put(T+0x29,b'\x80')
 m.put(A+0x2a,struct.pack('<H',weapon));m.put(A+0xf6,bytes((4,14)));m.put(T+0xf6,bytes((5,14)))
 if condition=='active':call('ffta_drk_grant_last_resort',A,1)
 if condition=='bloodcasting':support(A,'DRK-S2');m.put(A+0x1c,bytes(2))
 if condition=='composure':
  if not support(A,'SAM-S1'):continue
  call('ffta_turn_event',A,1)
 if condition=='Protect':m.put(T+0xeb,b'\x02')
 m.put(ROW,bytes(20));m.put(sp,bytes(8));before=protected()
 m.call(0x080c2618,ROW,wrappers[A],wrappers[T],360,stack=sp)
 value=struct.unpack('<h',m.read(ROW+12,2))[0]
 m.put(NODE,struct.pack('<I',wrappers[A]));m.put(NODE+8,struct.pack('<HH',360,0))
 score=m.call(0x080bdecc,wrappers[A],wrappers[T],360,0,stack=sp)
 ptr=0x091e8000+360*28+13;saved=m.read(ptr,1);check('actor-buff-descriptor',saved,b'\xd8')
 m.put(ptr,b'\x01');control=ROW+64;m.put(control,bytes(20));m.put(sp,bytes(8))
 try:
  m.call(S['ffta_ai_original_row'],control,wrappers[A],wrappers[T],360,stack=sp)
  rawscore=m.call(S['ffta_ai_original_score'],wrappers[A],wrappers[T],360,0,stack=sp)
 finally:m.put(ptr,saved)
 rawvalue=struct.unpack('<h',m.read(control+12,2))[0]
 legal=weapon not in (0,124);preparation=20 if legal and condition!='active' else 0
 check('hostile-row-exact-strike-plus-new-buff',value,rawvalue+preparation if legal else 0)
 check('hostile-score-exact-strike-plus-new-buff',score,rawscore+preparation if legal else 0)
 check('hostile-oracle-pure',protected()==before)
 # Illegal weapons cannot attack, but self preparation remains useful/legal.
 if not legal:
  m.put(ROW,bytes(20));m.put(sp,bytes(8));m.call(0x080c2618,ROW,wrappers[A],wrappers[A],360,stack=sp)
  check('self-preparation-remains-weapon-free',struct.unpack('<h',m.read(ROW+12,2))[0],0 if condition=='active' else -20)
 cases.append(dict(lesson='DRK-A5',race=race,weapon=weapon,condition=condition,stack=sp,oracle=True,value=value,score=score,rawvalue=rawvalue,rawscore=rawscore))
report=dict(passed=not failures,romSha1=meta['romSha1'],capture=capture,total=sum(checks.values()),checks=dict(checks),cases=cases,failures=failures,scope=__doc__)
(OUT/'martial-attack-ai.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ('cases','capture')},indent=2));assert not failures,failures[:20]
