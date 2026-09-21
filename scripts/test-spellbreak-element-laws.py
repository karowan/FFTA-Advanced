"""Spellbreak keeps its primary element independently of selected buff/fuel."""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-carrier-element-laws.py'
exec(compile(source.read_text().split('\nfor action,self_target,seed in ')[0],str(source),'exec'))
observations=[]
for weapon,choice,seed,affinity in itertools.product((88,91),(7,8),(0,3,18),(0,1,2)):
 case=('Spellbreak-element',weapon,choice,seed,affinity);fixture(421,seed)
 m.put(A+0x2a,struct.pack('<5H',weapon,0,0,0,0));m.put(T+0xeb,b'\x03')
 call('ffta_myk_grant',A,2) # Blizzard enchantment must not replace the item.
 element=m.call(0x080ca7a4,weapon,4,stack=STACK)
 m.put(T+0x0c,bytes([1]*9))
 if element:m.put(T+0x0c+element,bytes((affinity,)))
 for banned,residue in itertools.product(range(1,9),(0,4)):
  check('Spellbreak-primary-prediction',query(421,banned,T,residue=residue),int(bool(element) and banned==element))
 check('Spellbreak-runtime-element',m.call(0x0812f8a4,A,421,weapon,stack=STACK),element)
 before_mp=half(A+0x1c);execute(421,choice=choice)
 check('Spellbreak-single-payment',before_mp-half(A+0x1c),10)
 check('Spellbreak-enchantment-kept',call('ffta_myk_enchantment',A),2)
 loss=500-half(T+0x18)
 check('unselected-native-buff-kept',bool(m.read(T+0xeb,1)[0]&(2 if choice==7 else 1)),True)
 removed=not bool(m.read(T+0xeb,1)[0]&(1 if choice==7 else 2))
 receipt=call('ffta_battle_workspace',0x2620);native_rows=rows(421,T)
 for i,o,row in native_rows:
  check('Spellbreak-original-choice',half(o+18),choice)
  check('Spellbreak-original-element',m.read(receipt+16+i,1)[0],0x80|element)
  m.put(A+0x2a,struct.pack('<5H',88 if weapon==91 else 91,0,0,0,0))
  call('ffta_myk_grant',A,3)
  for banned in range(1,9):check('Spellbreak-late-immutable-element',query(421,banned,T,row+0x14),int(bool(element) and banned==element))
  check('Spellbreak-copied-mask-rejected',query(421,element or 1,T,0x0203e100),0)
  check('Spellbreak-wrong-recipient-rejected',query(421,element or 1,A,row+0x14),0)
  m.put(0x08529348,bytes((2,element or 1)));m.put(STACK,struct.pack('<II',0,row+0x14))
  check('Spellbreak-native-late-element',m.call(0x08135750,A,T,421,0,stack=STACK),int(bool(element)))
 observations.append(dict(weapon=weapon,choice=choice,seed=seed,affinity=affinity,loss=loss,removed=removed))
 m.put(regs[0],bytes(0x26c4))
 check('Spellbreak-retired-result-rejected',query(421,element or 1,T,native_rows[0][2]+0x14),0)
for choice in (7,8):
 samples=[o for o in observations if o['weapon']==91 and o['choice']==choice]
 check('Spellbreak-positive-removal-'+str(choice),any(o['removed'] and o['loss']>0 for o in samples),True)
 check('Spellbreak-immune-removal-'+str(choice),any(o['removed'] and o['loss']==0 and o['affinity']==2 for o in samples),True)
 check('Spellbreak-immunity-'+str(choice),all(o['loss']==0 for o in samples if o['affinity']==2),True)
 check('Spellbreak-weakness-'+str(choice),any(o['loss']>next(p['loss'] for p in samples if p['seed']==o['seed'] and p['affinity']==1) for o in samples if o['affinity']==0),True)
for weapon,choice,banned in itertools.product((88,91),(7,8),(1,5)):
 case=('Spellbreak-native-AI',weapon,choice,banned);fixture(421)
 m.put(A+0x2a,struct.pack('<5H',weapon,0,0,0,0));m.put(T+0xeb,bytes((1 if choice==7 else 2,)))
 call('ffta_myk_grant',A,2)
 m.put(m.word(0x0200f438)+4,b'\0');m.put(0x0203f728,bytes(4))
 judge=0x020005a8;m.put(judge+0x28,struct.pack('<H',0x1000));m.put(judge+0x18,struct.pack('<HH',500,500));m.put(judge+0xe8,bytes(8))
 m.put(0x08529348,bytes((2,banned)));m.put(ROW,bytes(20));m.put(STACK,bytes(8))
 protected=[(A,264),(T,264),(record(A),22),(record(T),22),(0x030034b0,4),(0x03005e80,384)]
 before=[m.read(p,n) for p,n in protected]
 m.call(0x080c2618,ROW,wrappers[A],wrappers[T],421,stack=STACK)
 row=m.read(ROW,20)
 for (p,n),b in zip(protected,before):check('Spellbreak-AI-query-pure-'+hex(p),m.read(p,n),b)
 check('Spellbreak-AI-positive',int.from_bytes(row[10:12],'little')>0,True)
 check('Spellbreak-AI-chosen-buff',int.from_bytes(row[2:4],'little'),choice)
 check('Spellbreak-AI-actual-weapon-law',bool(row[17]&2),weapon==91 and banned==1)
report=dict(passed=True,romSha1=meta['romSha1'],total=sum(checks.values()),checks=dict(checks),observations=observations)
(OUT/'spellbreak-element-laws.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
