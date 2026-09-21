"""Elemental command laws: fixed records, selected Gaia and consumed Release.

Native commands create all result rows. Pure native law queries and actual
AI rows consume them; no injected success flags or receipt-writer calls.
"""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-mystic-knight-commands.py';ns={'__file__':str(source),'__name__':'carrier_law_fixture'}
exec(compile(source.read_text().split('# Native casts cover')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,STACK,regs,fixture,execute,call,record,wrappers=(ns[k] for k in
 ('m','S','meta','OUT','A','T','STACK','regs','fixture','execute','call','record','wrappers'))
checks=collections.Counter();samples=[];case=None;LAW=0x0203e000;ROW=0x02028000
elements={1:1,2:5,3:6,11:7}
half=lambda p:int.from_bytes(m.read(p,2),'little')
def check(k,a,b):checks[k]+=1;assert a==b,(k,case,a,b)
def query(action,element,target,mask=0,move=0,residue=0,actor=None):
 actor=actor or A
 m.put(LAW,bytes(4)+bytes((2,0,element))+bytes(9))
 m.put(STACK+residue,struct.pack('<4I',move,0,mask,LAW))
 receipt=call('ffta_battle_workspace',0x2620)
 protected=[(A,264),(T,264),(record(A),22),(record(T),22),(0x030034b0,4),(0x0203ff44,8),(0x03005e80,384)]
 if receipt:protected.append((receipt,64))
 before=[m.read(p,n) for p,n in protected]
 value=m.call(0x081343c8,actor,target,action,0,stack=STACK+residue)
 for (p,n),b in zip(protected,before):check('query-preserves-'+hex(p),m.read(p,n),b)
 return value
def setup(action,seed=0):
 fixture(action,seed)
 if action==381:
  ns['job'](A,3,121);m.put(A+0x2a,bytes(10))
  grid=0x02026000;m.put(grid,bytes((16,0))*256);info=bytearray(16)
  struct.pack_into('<I',info,4,grid);info[8]=info[13]=info[15]=16;m.put(0x02007f10,info)
  for w in wrappers.values():m.put(w+10,struct.pack('<H',256))
  m.put(0x091f0000,bytes(163*256));m.put(0x091f0000+14*16+4,b'\x1f')
def rows(action,target):
 result=[]
 for i in range(14):
  o=regs[0]+i*0x2c4
  if m.word(o)!=wrappers[A] or half(o+16)!=action:continue
  for j in range(m.read(o+0x2c0,1)[0]):
   row=o+0x20+j*0x2c;w=m.word(row)
   if w and m.word(w)==target:result.append((i,o,row))
 check('native-recipient-row',bool(result),True);return result

for action,self_target,seed in itertools.product(range(410,421),(False,True),(0,3,18)):
 case=('fixed-command',action,self_target,seed);setup(action,seed)
 target=A if self_target else T;expected=elements.get(action-409,0)
 check('record-matches-runtime-element',m.call(0x080ccd50,action,1,stack=STACK),expected)
 for value,residue in itertools.product(range(1,9),(0,4)):
  check('fixed-command-prediction',query(action,value,target,residue=residue),int(value==expected))
 execute(action,self_target)
 for _,_,row in rows(action,target):
  for value in range(1,9):check('fixed-command-committed',query(action,value,target,row+0x14),int(value==expected))
 samples.append(dict(action=action,self=self_target,seed=seed,element=expected))

for action,choice,seed in [(a,c,s) for a,choices in ((381,range(1,6)),(422,(1,2,3,8,11))) for c,s in itertools.product(choices,(0,1,3,18))]:
 case=('dynamic-command',action,choice,seed);setup(action,seed)
 if action==422:call('ffta_myk_grant',A,choice)
 expected=choice if action==381 else elements.get(choice,0)
 if action==381:
  # The actual native player targeter owns this prediction choice.
  manager=m.word(0x0200f438);m.put(manager+4,b'\x0b');m.put(manager+16,struct.pack('<H',choice))
  m.put(manager+20,struct.pack('<II',action,A))
 for value,residue in itertools.product(range(1,9),(0,4)):
  check('selected-command-prediction',query(action,value,T,residue=residue),int(value==expected))
 execute(action,False,choice if action==381 else 0)
 if action==422:check('fuel-actually-consumed',call('ffta_myk_enchantment',A),0)
 receipt=call('ffta_battle_workspace',0x2620);native_rows=rows(action,T)
 for i,o,row in native_rows:
  check('recorded-original-element',m.read(receipt+16+i,1)[0],0x80|expected)
  if action==381:check('native-executed-choice-operand',half(o+18),choice)
 # Alter current state after execution. Late reporting must keep its own
 # authenticated original component identity, including a non-elemental one.
 if action==422:call('ffta_myk_grant',A,2 if choice!=2 else 1)
 else:
  m.put(0x091f0000+14*16+4,b'\0');m.put(m.word(0x0200f438)+16,struct.pack('<H',2 if choice!=2 else 1))
 for i,o,row in native_rows:
  for value,residue in itertools.product(range(1,9),(0,4)):
   check('late-law-keeps-original-element',query(action,value,T,row+0x14,residue=residue),int(value==expected))
  check('movement-stays-exempt',query(action,expected or 1,T,row+0x14,move=1),0)
  copied=0x0203e100;m.put(copied,m.read(row+0x14,8))
  check('copied-mask-has-no-authority',query(action,expected or 1,T,copied),0)
  check('wrong-recipient-has-no-authority',query(action,expected or 1,A,row+0x14),0)
  # Native late wrapper iterates the actual rule list, with item-used=false.
  m.put(0x08529348,bytes((2,expected or 8)))
  m.put(STACK,struct.pack('<II',0,row+0x14))
  check('native-late-wrapper-element',m.call(0x08135750,A,T,action,0,stack=STACK),int(bool(expected)))
 samples.append(dict(action=action,choice=choice,seed=seed,element=expected,rows=len(native_rows)))
 m.put(regs[0],bytes(0x26c4))
 check('retired-container-has-no-authority',query(action,expected or 1,T,native_rows[0][2]+0x14),0)

for action,choice,banned in [(a,c,b) for a,choices in ((381,range(1,6)),(422,(1,2,3,8,11))) for c,b in itertools.product(choices,(True,False))]:
 case=('native-AI',action,choice,banned);setup(action)
 expected=choice if action==381 else elements.get(choice,0)
 m.put(m.word(0x0200f438)+4,b'\0');m.put(0x0203f728,bytes(4))
 judge=0x020005a8;m.put(judge+0x28,struct.pack('<H',0x1000));m.put(judge+0x18,struct.pack('<HH',500,500));m.put(judge+0xe8,bytes(8))
 if action==422:call('ffta_myk_grant',A,choice)
 else:m.put(T+0x0c+choice,b'\0')
 law_element=expected if banned and expected else 8
 m.put(0x08529348,bytes((2,law_element)))
 m.put(ROW,bytes(20));m.put(STACK,bytes(8));before=m.read(0x03005e80,384)
 m.call(0x080c2618,ROW,wrappers[A],wrappers[T],action,stack=STACK)
 row=m.read(ROW,20)
 check('AI-query-code-intact',m.read(0x03005e80,384),before)
 check('native-AI-row-positive',int.from_bytes(row[10:12],'little')>0,True)
 if action==381:check('native-AI-selected-element',int.from_bytes(row[2:4],'little'),choice)
 check('native-AI-law-flag',bool(row[17]&2),bool(expected and banned))
 samples.append(dict(ai=True,action=action,choice=choice,banned=banned,row=row.hex()))
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),samples=samples)
(OUT/'carrier-element-laws.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
