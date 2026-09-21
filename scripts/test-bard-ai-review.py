"""Native song rows/scores: useful components, shared supports and pure queries.

This certifies recipient decisions, not full-turn movement/rendering.
"""
import collections,itertools,json,struct
from ai_review_fixture import *
checks=collections.Counter();rows=[];ROW=0x0202f000;NODE=0x02015488
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
def equip(u,ident):
 lesson=next(l for l in registry['lessons'] if l['id']==ident)
 race=m.read(u+6,1)[0];index=next(o['abilityIndex'] for o in lesson['owners'] if o['race']==race)
 m.put(u+(0x3b if lesson['type'][0]=='S' else 0x3a),bytes((index,)))
 m.put(0x02001b40+index-144 if race==1 and index>=144 else u+0x40+index,b'\xff')
def setup(action,condition):
 reset();target=A if condition.startswith('self') else T
 if condition=='enemy':m.put(T+0x29,b'\x80')
 if condition in ('full','cure-only','full-buffed'):m.put(T+0x18,struct.pack('<4H',300,300,100,100))
 if condition in ('native-buffs','all-buffs','full-buffed'):m.put(T+0xe8,bytes((8,16,0,3,0,0,0,0)))
 if condition in ('song-buffs','all-buffs','full-buffed'):m.put(state(T)+10,b'\x12')
 if condition in ('silence','self-silence'):m.put(A+0xeb,b'\x08')
 if condition=='confused':m.put(A+0xeb,b'\x10')
 if condition=='KO':m.put(T+0x18,bytes(2))
 if condition=='petrify':m.put(T+0xe8,b'\x40')
 if condition=='undead':m.put(T+0xe9,b'\x08');m.put(T+0x29,b'\x80')
 if condition=='self-hidden':m.put(A+0xe9,b'\x10')
 if condition=='cure-only':m.put(T+0xe9,b'\x06');m.put(T+0xeb,b'\x18')
 if condition in ('recuperation','boost','both'):
  m.put(T+0x18,struct.pack('<H',1))
  if condition in ('recuperation','both'):equip(T,'SLD-AX-S1')
  if condition in ('boost','both'):equip(A,'BRD-R1');m.put(state(A)+11,b'\x01')
 if condition=='small-MP-gap':m.put(T+0x1c,struct.pack('<H',97))
 return target
def check(name,value):
 checks[name]+=1
 assert value,(name,case)
conditions=('ally','self','enemy','full','native-buffs','song-buffs','all-buffs','silence','confused','KO','petrify','undead',
 'full-buffed','self-hidden','self-silence','cure-only','recuperation','boost','both','small-MP-gap')
for action,condition,sp in itertools.product(range(393,401),conditions,(STACK,STACK+4)):
 case=(action,condition,sp);target=setup(action,condition)
 m.put(ROW-16,b'\xa5'*52);m.put(ROW,bytes(20));m.put(sp,bytes(8));before=protected()
 m.call(0x080c2618,ROW,wrappers[A],wrappers[target],action,stack=sp)
 row=m.read(ROW,20);check('row-query-pure',protected()==before)
 check('row-memory-guards',m.read(ROW-16,16)+m.read(ROW+20,16)==b'\xa5'*32)
 m.put(NODE,struct.pack('<I',wrappers[A]));m.put(NODE+8,struct.pack('<HH',action,0));before=protected()
 score=m.call(0x080bdecc,wrappers[A],wrappers[target],action,0,stack=sp)
 score=score if score<0x80000000 else score-0x100000000
 check('score-query-pure',protected()==before);check('scope-retired',m.read(0x0203f728,4)==bytes(4))
 value=struct.unpack_from('<h',row,12)[0]
 if action!=396:
  denied=condition in ('enemy','confused','KO','petrify','undead') or condition in ('silence','self-silence') and action!=398
  expected=0
  if not denied:
   hp=0 if condition in ('full','cure-only','full-buffed') else 100 if action==393 else 60
   if condition in ('recuperation','boost','both'):
    hp=({ 'recuperation':180,'boost':156,'both':234} if action==393 else {'recuperation':90,'boost':78,'both':117})[condition]
   hasnative=condition in ('native-buffs','all-buffs','full-buffed')
   hassong=condition in ('song-buffs','all-buffs','full-buffed')
   if action==393:expected=-2*hp-(80 if condition=='cure-only' else 0)
   if action in (394,395):expected=-20*(not hasnative)-20*(not hassong)
   if action==397:expected=-2*hp-20*(not hasnative)
   if action==398:expected=-20 if condition in ('self','self-silence') else 0
   if action==399:expected=0 if condition.startswith('self') or condition in ('full','cure-only','full-buffed') else -3 if condition=='small-MP-gap' else -20
   if action==400:expected=0 if hasnative else -60
  check('exact-useful-song-row',value==expected)
  check('row-and-area-agree',score==expected)
  if not expected:check('no-empty-benefit-candidate',row[4:]==bytes(16))
  else:check('native-sort-value',struct.unpack_from('<h',row,14)[0]==expected)
 else:
  check('native-Requiem-domain',(value>0 and score>0) if condition=='undead' else value==score==0)
 rows.append(dict(action=action,condition=condition,stack=sp,row=list(struct.unpack('<10h',row)),score=score))
report=dict(passed=True,scope=__doc__,
 romSha1=meta['romSha1'],capture=capture,total=sum(checks.values()),checks=dict(checks),rows=rows)
(OUT/'bard-ai-review.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
