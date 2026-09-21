"""Native item/weapon classification and actual medicine HP/MP law domains."""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-carrier-element-laws.py'
exec(compile(source.read_text().split('\nfor action,self_target,seed in ')[0],str(source),'exec'))
cases=[]
def law(action,kind,value=0,target=None,item_used=0,mask=0,damage=0,move=0,residue=0):
 target=target or T
 m.put(LAW,bytes(4)+bytes((kind,0,value))+bytes(9))
 m.put(STACK+residue,struct.pack('<4I',move,damage&65535,mask,LAW))
 protected=[(A,264),(T,264),(record(A),22),(record(T),22),(0x02001940,512),(0x030034b0,4),(0x03005e80,384)]
 before=[m.read(p,n) for p,n in protected]
 n=m.call(0x081343c8,A,target,action,item_used,stack=STACK+residue)
 for (p,size),b in zip(protected,before):check('law-query-pure-'+hex(p),m.read(p,size),b)
 return n
# Approved weapon delivery, distinct from a prerequisite merely to know a
# spell: all Iaido, damaging Dark Arts, Viking weapon strikes, Sword Dance,
# blade-delivered Mystic commands and axe techniques. Release is a burst.
weapon_actions=set(range(347,359))|set(range(360,364))|{367,370,408,423}|set(range(410,422))|set(range(424,432))
for action,own,pair,residue in itertools.product(range(347,432),(False,True),((88,383),(383,88),(0,0)),(0,4)):
 case=('all-new-classifications',action,own,pair,residue);fixture(action)
 m.put(A+0x2a,struct.pack('<5H',*pair,0,0,0));target=A if own else T
 uses=action in weapon_actions and not (action==360 and own)
 primary_type=m.call(0x080ca7a4,pair[0],3,stack=STACK) if pair[0] else 0
 for value in (7,9):check('approved-weapon-law',law(action,10,value,target,residue=residue),int(uses and value==primary_type))
 check('recipe-is-item-use',law(action,4,target=target,residue=residue),int(383<=action<=392))
 check('movement-not-item-use',law(action,4,target=target,move=1,residue=residue),0)
for action,item_used,residue in itertools.product(range(347),(0,1),(0,4)):
 case=('ordinary-item-control',action,item_used,residue);fixture(action)
 check('ordinary-item-boolean-unchanged',law(action,4,item_used=item_used,residue=residue),item_used)

recipes=[(383,0,(362,)),(384,367,(367,)),(384,368,(368,)),(384,369,(369,)),(384,371,(371,)),
 (385,0,(375,)),(386,363,(363,)),(386,364,(364,)),(387,0,(362,363)),(388,0,(365,)),
 (389,0,(374,)),(390,0,(364,375)),(391,0,(362,374)),(392,0,(362,371))]
for race,(action,choice,ingredients),full in itertools.product((3,5),recipes,(False,True)):
 case=('actual-medicine',race,action,choice,full);fixture(action)
 ns['job'](A,race,120 if race==3 else 122);m.put(A+0x2a,bytes(10))
 m.put(T+0x29,b'\0');m.put(T+0xe8,bytes(8));m.put(T+0x18,struct.pack('<4H',500 if full else 100,500,100 if full else 1,100))
 if action in (385,390):m.put(T+0x18,bytes(2))
 if action in (384,389):
  bit={367:9,368:10,369:27,371:6}.get(choice,9)
  m.put(T+0xe8+bit//8,bytes((1<<(bit%8),)))
 m.put(0x02001940+362,bytes([5])*14)
 beforeHP=half(T+0x18);beforeMP=half(T+0x1c)
 execute(action,False,choice)
 check('actual-atomic-recipe-debit',m.read(0x02001940+362,14),bytes(4 if i in ingredients else 5 for i in range(362,376)))
 native_rows=rows(action,T)
 for _,_,row in native_rows:
  flags=half(row+12);damage=struct.unpack('<h',m.read(row+0x1e,2))[0] if flags&1 else 0
  check('medicine-native-success-gate',bool(flags&128) and not bool(flags&64),True)
  check('committed-medicine-item-law',law(action,4,mask=row+0x14),1)
  if action in (383,386,387):check('HP-law-receives-actual-restoration',damage,beforeHP-half(T+0x18))
  if action==388:
   check('MP-only-not-HP-law',damage,0);check('actual-MP-restoration',half(T+0x1c)>beforeMP,not full)
  for kind,threshold in itertools.product((11,12,13,14),(1,25,50,100,255)):
   want=(0<damage<threshold if kind==11 else damage>threshold if kind==12 else 0>damage>-threshold if kind==13 else damage<-threshold)
   m.put(0x08529348,bytes((kind,threshold)));m.put(STACK,struct.pack('<II',damage&65535,row+0x14))
   check('native-late-HP-domain',m.call(0x08135750,A,T,action,0,stack=STACK),int(want))
  m.put(0x08529348,b'\x04\0');m.put(STACK,struct.pack('<II',damage&65535,row+0x14))
  check('native-late-recipe-item-law',m.call(0x08135750,A,T,action,0,stack=STACK),1)
 cases.append(dict(race=race,action=action,choice=choice,full=full,HP=half(T+0x18)-beforeHP,MP=half(T+0x1c)-beforeMP))
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),cases=cases)
(OUT/'carrier-category-laws.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='cases'},indent=2))
