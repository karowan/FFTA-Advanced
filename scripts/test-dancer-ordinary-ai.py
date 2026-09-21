"""Ordinary Dance native AI rows: legal targets, resource usefulness and purity.

Forbidden Dance choice and Passing Step route handling retain their dedicated
tests. This matrix includes their ordinary damage neighbor, not their UI.
"""
import collections,itertools,json,struct
from ai_review_fixture import *
checks=collections.Counter();cases=[];failures=[];ROW=0x0202f000;NODE=0x02015488
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())

def check(name,actual,expected=True):
 checks[name]+=1
 if actual!=expected:failures.append(dict(case=case,check=name,actual=actual,expected=expected))

def signed(n):return n if n<0x80000000 else n-0x100000000

conditions=('normal','ally','self','KO','petrify','empty-MP','small-MP','already-Slow',
 'both-debuffs','no-weapon','wrong-weapon','silenced','confused','unaffordable','Astra','Fury')
for action,condition in itertools.product((401,402,403,404,405,407,408,409),conditions):
 case=(action,condition);reset();target=A if condition=='self' else T
 m.put(A+5,bytes((124,4,124)));m.put(A+0x35,b'\x7c');m.put(A+9,b'\x19')
 m.put(A+0x2a,struct.pack('<H',416));m.put(T+0x29,b'\x80')
 m.put(A+0x20,struct.pack('<4H',90,40,50,40));m.put(T+0x20,struct.pack('<4H',40,25,40,25))
 if condition=='ally':m.put(T+0x29,b'\0')
 if condition=='KO':m.put(T+0x18,bytes(2))
 if condition=='petrify':m.put(T+0xe8,b'\x40')
 if condition=='empty-MP':m.put(T+0x1c,bytes(2))
 if condition=='small-MP':m.put(T+0x1c,b'\x03\0')
 if condition=='already-Slow':m.put(T+0xea,b'\x40')
 if condition=='both-debuffs':m.put(state(T)+3,b'\x12')
 if condition=='no-weapon':m.put(A+0x2a,bytes(2))
 if condition=='wrong-weapon':m.put(A+0x2a,struct.pack('<H',1))
 if condition=='silenced':m.put(A+0xeb,b'\x08')
 if condition=='confused':m.put(A+0xeb,b'\x10')
 if condition=='unaffordable':m.put(A+0x1c,bytes(2))
 if condition=='Astra':m.put(T+0xea,b'\x80')
 if condition=='Fury':
  lesson=next(l for l in registry['lessons'] if l['id']=='DNC-R1');index=lesson['owners'][0]['abilityIndex']
  m.put(A+0x3a,bytes((index,)));m.put(A+0x40+index,b'\xff');m.put(state(A)+3,b'\x40')
 before=protected();admitted=m.call(0x08133e18,A,action,128,stack=STACK)
 check('admission-pure',protected()==before)
 check('MP-cost-admission',bool(admitted),condition!='unaffordable')
 m.put(ROW-16,b'\xa5'*52);m.put(ROW,bytes(20));m.put(STACK,bytes(8));before=protected()
 m.call(0x080c2618,ROW,wrappers[A],wrappers[target],action,stack=STACK)
 row=m.read(ROW,20);check('row-pure',protected()==before)
 check('row-guards',m.read(ROW-16,16)+m.read(ROW+20,16)==b'\xa5'*32)
 m.put(NODE,struct.pack('<I',wrappers[A]));m.put(NODE+8,struct.pack('<HH',action,0));before=protected()
 score=signed(m.call(0x080bdecc,wrappers[A],wrappers[target],action,0,stack=STACK))
 check('area-score-pure',protected()==before);check('scope-retired',m.read(0x0203f728,4)==bytes(4))
 value=struct.unpack_from('<h',row,12)[0]
 denied=condition in ('ally','self','KO','petrify','confused') or action==408 and condition in ('no-weapon','wrong-weapon')
 if denied:check('illegal-target-has-no-benefit',value==score==0)
 if action==402 and condition=='empty-MP':check('empty-MP-has-no-benefit',value==score==0)
 if action==403 and condition=='already-Slow':check('existing-Slow-has-no-benefit',value==score==0)
 cases.append(dict(action=action,condition=condition,admitted=admitted,row=list(struct.unpack('<10h',row)),score=score))
# The native field is a positive allowance, independent of MP and magic
# damage category. Check the entire approved action family partition once.
for lesson in registry['lessons']:
 if lesson['type'][0]!='A':continue
 ident=lesson['id'];action=lesson['globalAbilityId'];case=('silence-contract',ident)
 blocked=ident.startswith(('GEO-','MYK-')) or ident.startswith('BRD-') and ident!='BRD-A6' or ident in ('VIK-A1','VIK-A5','VIK-A7','VIK-A8')
 check('all-approved-action-Silence-fields',bool(m.call(0x080ccd50,action,20,stack=STACK)),not blocked)
# Real native menu generation, including all four Forbidden Dance options.
MENU,DESC,IDS,FLAGS=0x02028000,0x02028200,0x02028400,0x02028500
menus=[]
for secondary,silenced,mp in itertools.product((False,True),(False,True),(0,50)):
 case=('Dance-menu',secondary,silenced,mp);reset()
 original=ram[0x5a8+5];job=original if secondary else 124
 m.put(A+5,bytes((job,4,job,124 if secondary else 0)));m.put(A+0x35,bytes((job,124 if secondary else 0,0)))
 m.put(A+0x2a,struct.pack('<H',416));m.put(A+0x1c,struct.pack('<H',mp));m.put(A+0xeb,bytes((8 if silenced else 0,)))
 for lesson in registry['lessons']:
  if lesson['id'].startswith('DNC-A'):
   index=next(o['abilityIndex'] for o in lesson['owners'] if o['race']==4);m.put(A+0x40+index,b'\xff')
 manager=m.word(0x0200f438);m.put(manager+4,b'\x06');m.put(manager+24,struct.pack('<I',A))
 m.put(MENU,bytes(0xa4));m.put(MENU+10,b'\x04');m.put(MENU+0x94,struct.pack('<II',IDS,FLAGS))
 m.put(IDS-16,b'\xa5'*120);m.put(FLAGS-16,b'\xa6'*54);m.put(FLAGS,b'\x01'*22)
 bank=m.call(0x080cce60,A,2 if secondary else 1,DESC+4,DESC+5,stack=STACK)
 m.put(DESC,struct.pack('<I',bank));m.put(DESC+6,bytes((124,0,0,0,0,0)));before=protected()
 m.call(0x08026d44,MENU,DESC,stack=STACK);count=m.read(DESC+9,1)[0];check('menu-capacity',count<=22)
 check('menu-query-pure',protected()==before)
 rows=struct.unpack('<'+'I'*count,m.read(IDS,4*count));actions=[int.from_bytes(m.read(bank+i*8+4,2),'little') for i in rows]
 check('all-nine-Dance-actions',set(actions)==set(range(401,410)))
 check('four-Forbidden-choices',actions.count(406)==4)
 for i,action in enumerate(actions):check('Silence-never-greys-Dance',m.read(FLAGS+i,1)[0],int(mp>=rom[0x11e8000+action*28+4]))
 check('menu-output-guards',m.read(IDS-16,16)+m.read(IDS+88,16)==b'\xa5'*32 and m.read(FLAGS-16,16)+m.read(FLAGS+22,16)==b'\xa6'*32)
 menus.append(dict(secondary=secondary,silenced=silenced,mp=mp,actions=actions,enabled=list(m.read(FLAGS,count))))
report=dict(passed=not failures,romSha1=meta['romSha1'],capture=capture,scope=__doc__,
 total=sum(checks.values()),checks=dict(checks),cases=cases,menus=menus,failures=failures)
(OUT/'dancer-ordinary-ai.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
assert not failures,failures
