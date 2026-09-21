"""Native Fight results feed native elemental/status law queries after cleanup.

No supplied success masks: every committed mask comes from A433C execution.
Prediction, result ownership and cleanup controls are separate assertions.
"""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-mystic-knight-commands.py';ns={'__file__':str(source),'__name__':'fight_law_fixture'}
exec(compile(source.read_text().split('# Native casts cover')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,STACK,regs,fixture,execute,call,record=(ns[x] for x in
 ('m','S','meta','OUT','A','T','STACK','regs','fixture','execute','call','record'))
checks=collections.Counter();samples=[];case=None
LAW=0x0203e000
elements={1:1,2:5,3:6,11:7};statuses={4:9,5:26,6:27,9:22}
def check(k,a,b):checks[k]+=1;assert a==b,(k,case,a,b)
def h(p):return int.from_bytes(m.read(p,2),'little')
def protected():return m.read(A,264)+m.read(T,264)+m.read(0x0203f400,0x334)+m.read(0x030034b0,4)
def query(kind,values,mask=0,damage=0,move=0,residue=0,action=0):
 m.put(LAW,bytes(4)+bytes((kind,))+bytes(values).ljust(7,b'\0')+bytes(4))
 m.put(STACK+residue,struct.pack('<4I',move,damage&65535,mask,LAW));before=protected()
 result=m.call(0x081343c8,A,T,action,0,stack=STACK+residue)
 check('query-preserves-live-state-and-RNG',protected(),before)
 return result
for kind,seed,pair in itertools.product(range(1,12),range(8),((88,0),(88,89),(89,88))):
 case=(kind,seed,pair);fixture(0,seed);ns['ns']['job'](A,1,7)
 m.put(A+0x2a,struct.pack('<5H',*pair,0,0,0));call('ffta_myk_grant',A,kind)
 for element in range(1,9):check('element-prediction',query(2,[element]),int(elements.get(kind)==element))
 execute(0);container=regs[0];receipt=call('ffta_battle_workspace',0x2620)
 check('receipt-bound-to-native-container',m.word(receipt+4),container)
 seen=m.read(receipt+16,14);check('exactly-one-primary-component',list(seen).count(kind),1)
 # Deliberately remove the current enchantment AFTER execution. Laws must
 # still use the recorded action when a reaction consumed or cleared it.
 call('ffta_myk_clear',A)
 candidates=[];primary=[]
 for i in range(14):
  o=container+i*0x2c4
  if m.word(o)!=ns['wrappers'][A] or h(o+16):continue
  for j in range(m.read(o+0x2c0,1)[0]):
   row=o+0x20+j*0x2c;w=m.word(row)
   if w and m.word(w)==T:
    candidates.append(row)
    if seen[i]==kind:primary.append(row)
 check('actual-primary-recipient',bool(primary),True)
 hit=any(h(r+12)&0x80 and not h(r+12)&0x40 for r in primary)
 bit=statuses.get(kind,255)
 applied=bit<44 and any(hit and m.read(r+0x14+bit//8,1)[0]&(1<<(bit%8)) for r in primary)
 for row in candidates:
  for typ,value in [(2,v) for v in range(1,9)]+[(15,v) for v in (9,22,26,27,25)]+[(16,0)]:
   expected=int(hit and elements.get(kind)==value) if typ==2 else int(applied and (typ==16 or value==bit))
   for residue in (0,4):
    check('native-law-matches-committed-primary-event',query(typ,[value],row+0x14,h(row+0x1e),residue=residue),expected)
  check('native-movement-gate',query(2,[elements.get(kind,1)],row+0x14,move=1),0)
 samples.append(dict(kind=kind,seed=seed,pair=pair,hit=hit,status=bool(applied),receipt=list(seen)))
 # Pure copies of a successful mask cannot authenticate a retired result.
 copied=0x0203e100;m.put(copied,m.read(primary[0]+0x14,8))
 check('foreign-mask-no-event',query(2,[elements.get(kind,1)],copied),0)
 m.put(container,bytes(0x26c4))
 check('cleared-result-no-event',query(2,[elements.get(kind,1)],primary[0]+0x14),0)
for kind in statuses:check('nonvacuous-native-status-'+str(kind),any(x['kind']==kind and x['status'] for x in samples),True)
check('nonvacuous-misses',any(not x['hit'] for x in samples),True)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),samples=samples,
 limits=['Status/recovery prediction and actual Judge playback remain separate obligations.'])
(OUT/'mystic-knight-fight-laws.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
