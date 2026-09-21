"""Native elemental arts, frozen law identity and original command mappings."""
import pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-carrier-element-laws.py'
exec(compile(source.read_text().split('\nfor action,self_target,seed in ')[0],str(source),'exec'))
audit='--audit' in sys.argv
observations=[]
last_only='--last-resort-only' in sys.argv
arts=(360,) if last_only else (360,361,362,367,370,408,*range(424,432))
if not audit:
 for action,weapon in itertools.product(arts,(0,13,68,91,399)):
  case=('primary-element-prediction',action,weapon);fixture(action)
  m.put(A+0x2a,struct.pack('<5H',weapon,0,0,0,0));element=m.call(0x080ca7a4,weapon,4,stack=STACK) if weapon else 0
  for banned in range(1,9):check('primary-element-prediction',query(action,banned,T),int(bool(element) and element==banned))
 for action,seed in itertools.product(arts,(0,3,18)):
  case=('actual-primary-carrier',action,seed);fixture(action,seed)
  race,jid,weapon=(1,117,1) if action in (360,361,362) else (4,124,88) if action==408 else (1,2,399) if 424<=action<=427 else (2,16,399) if action>=428 else (2,118,399)
  ns['job'](A,race,jid);m.put(A+0x2a,struct.pack('<5H',weapon,0,0,0,0));execute(action)
  receipt=call('ffta_battle_workspace',0x2620)
  for i,o,row in rows(action,T):
   check('actual-non-elemental-carrier-bound',m.read(receipt+16+i,1)[0],128)
   m.put(A+0x2a,struct.pack('<5H',13,0,0,0,0))
   check('late-unrelated-equipped-element-not-borrowed',query(action,5,T,row+0x14),0)
 for race,weapon,old_buff in itertools.product((1,2),(0,13,68,91),(False,True)):
  case=('Last-Resort-modes',race,weapon,old_buff);fixture(360,3);ns['job'](A,race,117 if race==1 else 119)
  m.put(A+0x2a,struct.pack('<5H',weapon,0,0,0,0))
  if old_buff:call('ffta_drk_grant_last_resort',A,1)
  for banned in range(1,9):check('self-Last-Resort-no-element',query(360,banned,A),0)
  if weapon:
   m.put(STACK,struct.pack('<III',0,2,0))
   expected=m.call(0x0812fe38,A,T,0,weapon,stack=STACK)
   m.put(STACK,struct.pack('<III',0,2,0))
   actual=m.call(0x0812fe38,A,T,360,weapon,stack=STACK)
   # Bare native Fight is the unmodified P reference here; the new art's
   # existing Last Resort is an additional final x1.25 action modifier.
   check('Last-Resort-ordinary-primary-reference',actual,expected*5//4 if old_buff else expected)
  before=m.read(A+0x18,8);execute(360,True)
  check('self-Last-Resort-weapon-free',m.read(record(A),1),b'\x06')
  check('self-Last-Resort-exact-cost',half(A+0x1c),int.from_bytes(before[4:6],'little')-8)
  check('self-Last-Resort-no-injury',m.read(A+0x18,4),before[:4])
  for _,_,row in rows(360,A):check('late-self-no-element',query(360,5,A,row+0x14),0)
for action,weapon,race,jid in ((360,13,1,117),(361,13,1,117),(362,60,1,117),(408,91,4,124)):
 if last_only and action!=360:continue
 for seed,affinity in itertools.product((0,3,18),(0,1,2)):
  case=('actual-elemental-damage',action,weapon,seed,affinity);fixture(action,seed)
  ns['job'](A,race,jid);m.put(A+0x2a,struct.pack('<5H',weapon,0,0,0,0));m.put(T+0x2a,bytes(10))
  element=m.call(0x080ca7a4,weapon,4,stack=STACK)
  m.put(T+0x0c,bytes([1]*9));m.put(T+0x0c+element,bytes((affinity,)))
  runtime=m.call(0x0812f8a4,A,action,weapon,stack=STACK)
  if not audit:check('runtime-element-matches-primary',runtime,element)
  execute(action)
  observations.append(dict(action=action,weapon=weapon,seed=seed,affinity=affinity,runtimeElement=runtime,weaponElement=element,loss=500-half(T+0x18)))
  if not audit:
   native_rows=rows(action,T)
   for i,o,row in native_rows:
    # A late query must keep the executed element after removal/replacement.
    m.put(A+0x2a,bytes(10))
    for banned in range(1,9):check('late-weapon-element',query(action,banned,T,row+0x14),int(banned==element))
    check('foreign-mask-rejected',query(action,element,T,0x0203e100),0)
    check('wrong-recipient-rejected',query(action,element,A,row+0x14),0)
    m.put(0x08529348,bytes((2,element)));m.put(STACK,struct.pack('<II',0,row+0x14))
    check('late-wrapper-weapon-element',m.call(0x08135750,A,T,action,0,stack=STACK),1)
   m.put(regs[0],bytes(0x26c4))
   check('retired-element-rejected',query(action,element,T,native_rows[0][2]+0x14),0)
if not audit:
 for action in ((360,) if last_only else (360,361,362,408)):
  o=[v for v in observations if v['action']==action]
  check('actual-positive-elemental-hit-'+str(action),any(v['loss']>0 and v['affinity']==1 for v in o),True)
  check('actual-immunity-'+str(action),all(v['loss']==0 for v in o if v['affinity']==2),True)
  check('actual-weakness-'+str(action),any(v['loss']>next(w['loss'] for w in o if w['seed']==v['seed'] and w['affinity']==1) for v in o if v['affinity']==0),True)
report=dict(audit=audit,passed=True,romSha1=meta['romSha1'],total=sum(checks.values()),checks=dict(checks),observations=observations)
(OUT/('carrier-weapon-element-audit.json' if audit else 'carrier-weapon-elements.json')).write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
