"""All ten medicine commands: native discovery, recipe rows and inventory ownership."""
import collections,itertools,json,struct
from ai_review_fixture import *
REG=json.loads((ROOT/'build/expansion/registry.json').read_text())['lessons']
ROW=0x0202f000;NODE=0x02015488;checks=collections.Counter();cases=[];failures=[]

def check(name,actual,expected=True):
 checks[name]+=1
 if actual!=expected:failures.append(dict(case=case,check=name,actual=actual,expected=expected))

for action,race,condition in itertools.product(range(383,393),(3,5),
 ('useful','empty-stock','self','redundant','silenced','foreign-owner','actor-KO','actor-Petrify','Confuse','undead','hostile','one-HP-missing','pharmacology','recuperation','both-supports')):
 case=(action,race,condition);reset();actor=A;target=A if condition=='self' else T
 if condition=='foreign-owner':actor=T;target=T
 job=120 if race==3 else 122
 m.put(actor+5,bytes((job,race,job)));m.put(actor+0x35,bytes((job,)))
 m.put(0x02001940+362,bytes((0 if condition=='empty-stock' else 5,))*14)
 if action in (385,390):m.put(target+0x18,bytes(2))
 if action in (384,389):m.put(target+0xe9,b'\x06');m.put(target+0xeb,b'\x08')
 if condition=='silenced':m.put(actor+0xeb,b'\x08')
 if condition=='redundant':
  m.put(target+0x18,struct.pack('<4H',300,300,100,100));m.put(target+0xe8,bytes(8));m.put(target+0xeb,b'\x03');m.put(state(target)+8,b'\x02')
 if condition=='actor-KO':m.put(actor+0x18,bytes(2))
 if condition=='actor-Petrify':m.put(actor+0xe8,b'\x40')
 if condition=='Confuse':m.put(actor+0xeb,b'\x10')
 if condition=='undead':m.put(target+0xe9,b'\x08')
 if condition=='hostile':m.put(target+0x29,b'\x80')
 if condition=='one-HP-missing' and action not in (385,390):m.put(target+0x18,struct.pack('<H',299))
 if condition in ('pharmacology','both-supports'):m.put(actor+0x3b,bytes((next(o['abilityIndex'] for l in REG if l['id']=='CHM-S1' for o in l['owners'] if o['race']==race),)))
 if condition in ('recuperation','both-supports'):m.put(target+0x3b,bytes((next(o['abilityIndex'] for l in REG if l['id']=='SLD-AX-S1' for o in l['owners'] if o['race']==1),)))
 if condition in ('pharmacology','recuperation','both-supports'):m.put(target+0x18,struct.pack('<4H',0 if action in (385,390) else 100,501,1,201))
 before=protected();admitted=m.call(0x08133e18,actor,action,128,stack=STACK)
 check('admission-pure',protected()==before)
 check('native-stock-owner-admission',bool(admitted),condition not in ('empty-stock','foreign-owner','actor-KO','actor-Petrify','Confuse') and not(condition=='self' and action in (385,390)))
 m.put(ROW-16,b'\xa5'*52);m.put(ROW,bytes(20));m.put(STACK,bytes(8))
 m.call(0x080c2618,ROW,wrappers[actor],wrappers[target],action,stack=STACK)
 row=m.read(ROW,20);check('row-pure',protected()==before)
 check('row-bounds',m.read(ROW-16,16)+m.read(ROW+20,16)==b'\xa5'*32)
 value=struct.unpack_from('<h',row,12)[0]
 useful=condition not in ('empty-stock','foreign-owner','redundant','actor-KO','actor-Petrify','Confuse','undead','hostile') and not(condition=='self' and action in (385,390))
 check('useful-medicine-row',value<0 if useful else value==0)
 if useful and action==384:check('selects-stocked-needed-remedy',struct.unpack_from('<H',row,2)[0] in (367,368,369))
 if useful and action==386:check('selects-stocked-tonic',struct.unpack_from('<H',row,2)[0] in (363,364))
 m.put(NODE,struct.pack('<IIHH',wrappers[actor],wrappers[target],action,struct.unpack_from('<H',row,2)[0]))
 score=m.call(0x080bdecc,wrappers[actor],wrappers[target],action,0,stack=STACK);score=score if score<0x80000000 else score-0x100000000
 check('native-placement-score-matches-row',score,value)
 check('score-pure',protected()==before)
 if useful and condition=='one-HP-missing' and action in (383,386,387):check('actual-capped-healing-score',value,-2)
 if useful and condition in ('pharmacology','recuperation','both-supports') and action in (383,385,386,387,388,390):
  numerator=9 if condition=='both-supports' else 6
  expected=(25 if action==383 else 150 if action==386 else 100)*numerator//4
  if action==388:expected=120 if condition!='recuperation' else 80
  if action in (385,390):expected=250
  check('independent-support-and-revival-formula',value,-2*expected)
 cases.append(dict(action=action,race=race,condition=condition,admitted=admitted,row=list(struct.unpack('<10h',row))))
# Exact stocked choice, real cure and one-support-slot restoration policies.
for action,choice,bit in ((384,367,9),(384,368,10),(384,369,27),(384,371,6),(386,363,None),(386,364,None)):
 for stocked in (False,True):
  case=('choice',action,choice,stocked);reset();m.put(A+5,bytes((120,3,120)));m.put(A+0x35,b'\x78')
  m.put(0x02001940+362,bytes(14));m.put(0x02001940+choice,bytes((int(stocked),)))
  if bit is not None:m.put(T+0xe8+bit//8,bytes((1<<(bit%8),)))
  m.put(STACK,bytes(8));before=protected();m.call(0x080c2618,ROW,wrappers[A],wrappers[T],action,stack=STACK)
  row=m.read(ROW,20);value=struct.unpack_from('<h',row,12)[0]
  check('only-stocked-choice-is-useful',value<0,stocked)
  if stocked:check('exact-item-operand',struct.unpack_from('<H',row,2)[0],choice)
  check('choice-forecast-pure',protected()==before)
  cases.append(dict(action=action,choice=choice,stocked=stocked,row=list(struct.unpack('<10h',row))))
for tag in ('wound','challenge','wisp','polka','frolic','conceal-only','last-resort'):
 case=('custom-cure',tag);reset();m.put(A+5,bytes((120,3,120)));m.put(A+0x35,b'\x78');m.put(0x02001940+374,b'\x05')
 if tag=='wound':call('ffta_wound_record_replace',call('ffta_owned_wound',T),100)
 if tag=='challenge':m.put(state(T)+5,b'\x01')
 if tag=='wisp':m.put(state(T)+17,b'\x40')
 if tag=='polka':m.put(state(T)+3,b'\x02')
 if tag=='frolic':m.put(state(T)+3,b'\x10')
 if tag=='conceal-only':m.put(T+0xe9,b'\x10')
 if tag=='last-resort':m.put(state(T),b'\x02')
 before=protected();m.put(STACK,bytes(8));m.call(0x080c2618,ROW,wrappers[A],wrappers[T],389,stack=STACK)
 row=m.read(ROW,20);value=struct.unpack_from('<h',row,12)[0]
 check('actual-broad-cure-domain',value,-40 if tag not in ('conceal-only','last-resort') else 0)
 check('broad-remedy-pure',protected()==before)
 cases.append(dict(tag=tag,row=list(struct.unpack('<10h',row))))
for action,condition in itertools.product((0,1,12,251,264,350,351,359,360,364,368,393,400,406,409,421),('ordinary','self','KO','Petrify')):
 case=('original-recipient-control',action,condition);reset();target=A if condition=='self' else T
 if condition=='KO':m.put(target+0x18,bytes(2))
 if condition=='Petrify':m.put(target+0xe8,b'\x40')
 before=protected();actual=m.call(0x080c48a4,A,target,action,stack=STACK)
 check('recipient-hook-keeps-other-actions',actual,call('ffta_medicine_original_recipient',A,target,action))
 check('recipient-hook-pure',protected()==before)
 check('choice-scope-retired',m.read(0x0203f728,4),bytes(4))
report=dict(passed=not failures,romSha1=meta['romSha1'],capture=capture,total=sum(checks.values()),checks=dict(checks),cases=cases,failures=failures)
(OUT/'medicine-ai.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not failures,failures
