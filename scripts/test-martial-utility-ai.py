"""Native martial utility rows, residual benefits and shared healing supports."""
import collections,itertools,json,struct
from ai_review_fixture import *
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
checks=collections.Counter();cases=[];failures=[];ROW=0x0202f000;NODE=0x02015488
def check(name,actual,expected=True):
 checks[name]+=1
 if actual!=expected:failures.append(dict(case=case,check=name,actual=actual,expected=expected))
def equipped(u,ident):
 lesson=next(l for l in registry['lessons'] if l['id']==ident);race=m.read(u+6,1)[0]
 index=next(o['abilityIndex'] for o in lesson['owners'] if o['race']==race)
 m.put(u+0x3b,bytes((index,)))
 m.put(0x02001b40+index-144 if race==1 and index>=144 else u+0x40+index,b'\xff')
idents=('SAM-A4','SAM-A5','DRK-A4','DRK-A5','DRK-A9','VIK-A4')
conditions=('useful','self','enemy','KO','petrify','no-weapon','complete','complete-hurt','complete-ailment',
 'recuperation','centered','centered-recuperation','composure','centered-composure-recuperation',
 'partial-protect','partial-shell','ward-only','cure-only','unaffordable','silenced','bloodcasting','bloodcasting-too-low')
for ident,condition,sp in itertools.product(idents,conditions,(STACK,STACK+4)):
 case=(ident,condition,sp);reset();lesson=next(l for l in registry['lessons'] if l['id']==ident)
 action=lesson['globalAbilityId'];owner=lesson['owners'][0];job,race=owner['jobId'],owner['race']
 m.put(A+5,bytes((job,race,job)));m.put(A+0x35,bytes((job,)))
 m.put(A+0x2a,struct.pack('<H',376 if ident.startswith('SAM') else 1))
 target=A if ident in ('DRK-A4','DRK-A5') or condition=='self' else T
 if condition=='enemy':target=T;m.put(T+0x29,b'\x80')
 if condition=='KO':m.put(target+0x18,bytes(2))
 if condition=='petrify':m.put(target+0xe8,b'\x40')
 if condition=='no-weapon':m.put(A+0x2a,bytes(2))
 if condition=='unaffordable':m.put(A+0x1c,bytes(2))
 if condition.startswith('complete'):
  token=call('ffta_job_origin',A)
  for u in (A,T):
   m.put(u+0x18,struct.pack('<H',200 if condition=='complete-hurt' else 300));m.put(u+0xeb,b'\x03')
   m.put(state(u),bytes((2,token,1)));m.put(state(u)+4,b'\x02')
   if condition=='complete-ailment':m.put(u+0xe9,b'\x04')
 healing=ident in ('SAM-A4','DRK-A4')
 if healing and any(s in condition for s in ('recuperation','centered','composure')):
  m.put(target+0x18,struct.pack('<H',1))
  if 'recuperation' in condition:equipped(target,'SLD-AX-S1')
  if 'centered' in condition:call('ffta_centered_grant',A,0)
  if 'composure' in condition:
   equipped(A,'SAM-S1');call('ffta_turn_event',A,1)
 if condition=='partial-protect':m.put(target+0xeb,b'\x02')
 if condition=='partial-shell':m.put(target+0xeb,b'\x01')
 if condition=='ward-only':m.put(target+0x18,struct.pack('<H',300))
 if condition=='cure-only':
  m.put(state(target)+4,b'\x02');m.put(target+0xe9,b'\x04');m.put(target+0xeb,b'\x18')
 if condition=='silenced':m.put(A+0xeb,b'\x08')
 if condition.startswith('bloodcasting'):
  equipped(A,'DRK-S2');m.put(A+0x1c,bytes(2))
  if condition=='bloodcasting-too-low':m.put(A+0x18,b'\x01\0')
 m.put(ROW-16,b'\xa5'*52);m.put(ROW,bytes(20));m.put(sp,bytes(8));before=protected()
 admitted=m.call(0x08133e18,A,action,128,stack=sp);check('admission-pure',protected()==before)
 check('affordability-and-Silence-admission',bool(admitted),condition not in ('unaffordable','bloodcasting-too-low','KO') or condition=='KO' and target!=A)
 m.call(0x080c2618,ROW,wrappers[A],wrappers[target],action,stack=sp)
 row=m.read(ROW,20);check('row-pure',protected()==before);check('row-guards',m.read(ROW-16,16)+m.read(ROW+20,16)==b'\xa5'*32)
 m.put(NODE,struct.pack('<I',wrappers[A]));m.put(NODE+8,struct.pack('<HH',action,0));before=protected()
 score=m.call(0x080bdecc,wrappers[A],wrappers[target],action,0,stack=sp);score=score if score<0x80000000 else score-0x100000000
 check('area-score-pure',protected()==before);check('scope-retired',m.read(0x0203f728,4)==bytes(4))
 value=struct.unpack_from('<h',row,12)[0]
 if condition=='enemy' and ident=='DRK-A5':
  # An independent native damage/hit control removes only the actor-buff
  # descriptor in private emulator memory. Restore exact shipping bytes.
  ptr=0x091e8000+action*28+13;saved=m.read(ptr,1);m.put(ptr,b'\x01')
  control=ROW+64;m.put(control,bytes(20));m.put(sp,bytes(8))
  m.call(S['ffta_ai_original_row'],control,wrappers[A],wrappers[target],action,stack=sp)
  rawscore=m.call(S['ffta_ai_original_score'],wrappers[A],wrappers[target],action,0,stack=sp)
  m.put(ptr,saved)
  check('hostile-Last-Resort-retains-native-strike',value,struct.unpack_from('<h',m.read(control,20),12)[0]+20)
  check('hostile-area-keeps-strike-plus-preparation',score,rawscore+20)
 else:
  h=lambda p:struct.unpack('<H',m.read(p,2))[0]
  status=lambda bit:bool(m.read(target+0xe8+bit//8,1)[0]&(1<<(bit%8)))
  hp=h(target+0x18);maximum=h(target+0x1a);expected=0
  if healing:
   base=min(35*maximum,14000) if ident=='SAM-A4' else min(20*maximum,10000)
   cent=5 if ident=='SAM-A4' and 'centered' in condition else 4
   comp=25 if 'composure' in condition else 20
   recup=3 if 'recuperation' in condition and not(ident=='DRK-A4' and 'composure' in condition) else 2
   expected+=2*min(max(0,maximum-hp),base*cent*comp*recup//16000)
  if ident=='SAM-A5':expected+=20*(not status(25))
  if ident in ('SAM-A5','DRK-A4'):expected+=20*(not status(24))
  if ident in ('DRK-A5','DRK-A9'):expected+=0 if condition.startswith('complete') else 20
  if ident=='VIK-A4':expected+=20*(not(condition.startswith('complete') or condition=='cure-only'))+20*sum(status(bit) for bit in (10,27,28))
  denied=condition in ('KO','petrify','enemy') or condition=='no-weapon' and ident.startswith('SAM') or condition=='cure-only' and target==A
  if denied:expected=0
  check('exact-marginal-row-value',value,-expected);check('exact-marginal-area-value',score,-expected)
  if not expected:check('empty-benefit-clears-row',row[4:]==bytes(16))
  else:
   check('native-sort-value',struct.unpack_from('<h',row,14)[0],-expected)
   if ident in ('DRK-A5','DRK-A9','VIK-A4'):
    check('pure-custom-buff-native-classification',list(struct.unpack_from('<4H',row,4)),[82,0,0,1])
 cases.append(dict(lesson=ident,condition=condition,stack=sp,admitted=admitted,row=list(struct.unpack('<10h',row)),score=score))
report=dict(passed=not failures,romSha1=meta['romSha1'],capture=capture,total=sum(checks.values()),checks=dict(checks),cases=cases,failures=failures)
(OUT/'martial-utility-ai.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not failures,failures
